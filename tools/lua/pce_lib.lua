-- Mesen2 / MesenCE (PC Engine) driver library.
-- run_emu.py prepends globals: OUT, ERRFILE, ROUTE, FRAMES, SHOT_EVERY, SHOTS,
-- STATE_IN, STATE_OUT, STATE_EVERY, MASH, MASH_KEY, SYSTEM.
L = { frame = 0 }
local pce, cpuMem = emu.cpuType.pce, emu.memType.pceMemory
local ALL = 0xFFFF

local logf = assert(io.open(OUT .. "log.txt", "w"))
function L.log(s) logf:write(tostring(s) .. "\n"); logf:flush() end
local function outpath(p) return (p:match("^%a:") or p:match("^/")) and p or OUT .. p end
function L.write_file(path, data) local f = assert(io.open(outpath(path), "wb")); f:write(data); f:close() end
function L.read_file(path) local f = assert(io.open(path, "rb")); local d = f:read("a"); f:close(); return d end
function L.shot(name) L.write_file(OUT .. name, emu.takeScreenshot()) end
function L.finish(code) logf:flush(); emu.stop(code or 0) end
function L.fail(msg)
  local f = io.open(ERRFILE, "a"); f:write(tostring(msg) .. "\n"); f:close()
  emu.stop(2)
end
function L.safe(fn) return function(...) local ok, e = pcall(fn, ...); if not ok then L.fail(e) end end end

function L.pc() return emu.getState()["cpu.pc"] end
function L.mpr(slot) return emu.getState()["memoryManager.mpr[" .. tostring(slot) .. "]"] end
function L.rom_off(cpu_addr)
  local slot = (cpu_addr >> 13) & 7
  local bank = L.mpr(slot)
  local off13 = cpu_addr & 0x1FFF
  local rom_sz = emu.getMemorySize(emu.memType.pcePrgRom)
  -- On 384 KiB (48-bank) HuCards, bit 6 selects the upper 128 KiB chip ($40..$4F mirrored -> $20..$2F).
  local eff_bank = bank
  if rom_sz == 0x60000 and bank >= 0x40 and bank < 0x80 then
    eff_bank = 0x20 + (bank & 0x0F)
  end
  return eff_bank * 0x2000 + off13, bank
end

function L.on_exec(lo, hi, fn)
  local cb = L.safe(fn)
  return emu.addMemoryCallback(cb, emu.callbackType.exec, lo, hi, pce, cpuMem)
end
function L.on_read(lo, hi, fn, mt)
  local cb = L.safe(fn)
  return emu.addMemoryCallback(cb, emu.callbackType.read, lo, hi, pce, mt or cpuMem)
end
function L.on_write(lo, hi, fn, mt)
  local cb = L.safe(fn)
  return emu.addMemoryCallback(cb, emu.callbackType.write, lo, hi, pce, mt or cpuMem)
end

local function grab(mt, n)
  local t = {}
  for a = 0, n - 1 do t[#t + 1] = string.char(emu.read(a, mt)) end
  return table.concat(t)
end

function L.dump_vdc(prefix)
  prefix = prefix or "vdc"
  local vram_sz = emu.getMemorySize(emu.memType.pceVideoRam)
  local pal_sz = emu.getMemorySize(emu.memType.pcePaletteRam)
  local satb_sz = emu.getMemorySize(emu.memType.pceSpriteRam)
  L.write_file(prefix .. ".vram.bin", grab(emu.memType.pceVideoRam, vram_sz > 0 and vram_sz or 0x10000))
  L.write_file(prefix .. ".pal.bin", grab(emu.memType.pcePaletteRam, pal_sz > 0 and pal_sz or 0x400))
  L.write_file(prefix .. ".satb.bin", grab(emu.memType.pceSpriteRam, satb_sz > 0 and satb_sz or 0x200))
  local s, keys = emu.getState(), {}
  for k, v in pairs(s) do
    if k:find("^vdc%.") or k:find("^vce%.") or k:find("^memoryManager%.mpr") then
      keys[#keys + 1] = k .. "=" .. tostring(v)
    end
  end
  table.sort(keys)
  L.write_file(prefix .. ".vdc.txt", table.concat(keys, "\n") .. "\n")
end

function L.dump_ram(path)
  local sz = emu.getMemorySize(emu.memType.pceWorkRam)
  L.write_file(path, grab(emu.memType.pceWorkRam, sz > 0 and sz or 0x2000))
end

local jobs, execId = {}, nil
local function service()
  local job = table.remove(jobs, 1)
  if not job then return end
  if job.op == "save" then L.write_file(job.path, emu.createSavestate())
  else emu.loadSavestate(L.read_file(job.path)) end
  if #jobs == 0 then
    emu.removeMemoryCallback(execId, emu.callbackType.exec, 0, ALL, pce, cpuMem)
    execId = nil
  end
  if job.done then job.done() end
end
local function schedule(job)
  jobs[#jobs + 1] = job
  if not execId then execId = L.on_exec(0, ALL, service) end
end
function L.save_state(path, done) schedule({ op = "save", path = path, done = done }) end
function L.load_state(path, done) schedule({ op = "load", path = path, done = done }) end

local BTN_ALIAS = { a = "i", b = "ii", start = "run", i = "i", ii = "ii", run = "run",
                    select = "select", up = "up", down = "down", left = "left", right = "right" }
local queue = {}
function L.press(spec, frames)
  local b = {}
  if spec ~= "-" then
    for name in spec:gmatch("[^+]+") do
      local mapped = BTN_ALIAS[name:lower()] or error("unknown PCE button: " .. name)
      b[mapped] = true
    end
  end
  queue[#queue + 1] = { buttons = b, frames = frames }
end
function L.load_route(path)
  for line in io.lines(path) do
    local l = line:gsub("#.*", ""):match("^%s*(.-)%s*$")
    if l ~= "" then
      local n, spec = l:match("^(%d+)%s+(%S+)$")
      if not n then error("bad route line: " .. line) end
      L.press(spec, tonumber(n))
    end
  end
end
function L.route_done() return #queue == 0 end

emu.addEventCallback(L.safe(function()
  local q = queue[1]
  if q then
    emu.setInput(q.buttons, 0)
  elseif (MASH or 0) > 0 and L.frame % MASH < 6 then
    local mk = BTN_ALIAS[(MASH_KEY or "i"):lower()] or "i"
    emu.setInput({ [mk] = true }, 0)
  end
end), emu.eventType.inputPolled)

local frameFns = {}
function L.on_frame(fn) frameFns[#frameFns + 1] = fn end
emu.addEventCallback(L.safe(function()
  L.frame = L.frame + 1
  local q = queue[1]
  if q then q.frames = q.frames - 1; if q.frames <= 0 then table.remove(queue, 1) end end
  for _, fn in ipairs(frameFns) do fn(L.frame) end
end), emu.eventType.endFrame)

local shotset = {}
for _, f in ipairs(SHOTS or {}) do shotset[f] = true end
local function begin()
  if ROUTE then L.load_route(ROUTE) end
  local start, ending = L.frame, false
  L.on_frame(function(f)
    local n = f - start
    if ((SHOT_EVERY or 0) > 0 and n % SHOT_EVERY == 0) or shotset[n] then
      L.shot(string.format("f%06d.png", n))
    end
    if (STATE_EVERY or 0) > 0 and n > 0 and n % STATE_EVERY == 0 then
      L.save_state(string.format("%ss%06d.mss", OUT, n))
    end
    local stop = FRAMES and n >= FRAMES or (not FRAMES and L.route_done())
    if stop and not ending then
      ending = true
      L.shot("final.png")
      L.log("final frame " .. n)
      if STATE_OUT then L.save_state(STATE_OUT, function() L.finish(0) end) else L.finish(0) end
    end
  end)
end
if STATE_IN then L.load_state(STATE_IN, begin) else begin() end
