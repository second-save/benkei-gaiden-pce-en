-- Cold-boot debug warp & QA cheat driver for Benkei Gaiden (PCE).
-- Expects globals passed via --var:
--   DEBUG_DIR (abs path to tools/debug)
--   SCENE     (scene name in scenes.lua; optional if only using GOD/NOENC/NOCLIP/FAST)
-- Optional cheat globals:
--   GOD=1     pin active party HP/MP to MaxHP/MaxMP every frame
--   NOENC=1   disable random encounters ($C4 |= $01)
--   NOCLIP=1  disable map & NPC collision ($C4 |= $06)
--   FAST=1    fast step/text speed ($38)

local dbg = dofile(DEBUG_DIR .. "/scenes.lua")
local S = SCENE and dbg.SCENES[SCENE] or nil
if SCENE and not S then
  error("unknown debug scene: " .. tostring(SCENE))
end

local function wread(off) return emu.read(off, emu.memType.pceWorkRam) end
local function wwrite(off, val) emu.write(off, val, emu.memType.pceWorkRam) end

local function init_party(profile)
  for i = 0, 0x3F do wwrite(0x0200 + i, 0xFF) end
  for i = 0, 0x1F do wwrite(0x0300 + i, 0xFF) end
  for i = 0, 0x09 do wwrite(0x0320 + i, 0x00) end
  wwrite(0x0320, 0x80)
  wwrite(0x0323, 0x80)
  wwrite(0x0324, 0x04)

  if profile == "midgame" then
    -- 4-member party: Kijaku (0), Sayaka (1), Saburo (2), Benkei (3) Lv15
    local members = {
      { id = 0x00, hp = 95, mp = 40, lv = 15, eq = { 0x03, 0x22, 0x40 }, atk = 32, def = 20, agi = 18 },
      { id = 0x01, hp = 78, mp = 65, lv = 15, eq = { 0x04, 0x23, 0x41 }, atk = 22, def = 18, agi = 24 },
      { id = 0x02, hp = 88, mp = 30, lv = 15, eq = { 0x05, 0x24, 0xFF }, atk = 28, def = 19, agi = 22 },
      { id = 0x03, hp = 120, mp = 20, lv = 15, eq = { 0x06, 0x25, 0xFF }, atk = 40, def = 25, agi = 14 },
    }
    for slot, m in ipairs(members) do
      local base = 0x0200 + (slot - 1) * 16
      wwrite(base + 0x00, m.id)
      wwrite(base + 0x01, m.hp)
      wwrite(base + 0x02, m.mp)
      wwrite(base + 0x03, 0x00)
      wwrite(base + 0x04, 0x12)
      wwrite(base + 0x05, 0x34)
      wwrite(base + 0x06, m.lv)
      wwrite(base + 0x07, m.eq[1])
      wwrite(base + 0x08, m.eq[2])
      wwrite(base + 0x09, m.eq[3])
      wwrite(base + 0x0A, m.atk)
      wwrite(base + 0x0B, m.def)
      wwrite(base + 0x0C, m.agi)
    end
    -- Populate consumable bag $2300..$230F (B$01:$CD39)
    local bag = { 0x60, 0x60, 0x62, 0x66, 0x61, 0x63, 0x64, 0x65 }
    for idx, item in ipairs(bag) do
      wwrite(0x0300 + idx - 1, item)
      wwrite(0x0308 + idx - 1, item)
    end
    -- Populate equipment bag $2310..$231F (B$01:$CD69)
    local eq_bag = { 0x03, 0x04, 0x05, 0x06, 0x22, 0x23, 0x40, 0x41 }
    for idx, eq in ipairs(eq_bag) do
      wwrite(0x0310 + idx - 1, eq)
    end
    -- 2,500 sen (0x09C4)
    wwrite(0x00B7, 0xC4)
    wwrite(0x00B8, 0x09)
  else
    -- Starting Lv1 solo Kijaku (22 HP, 0 MP, 50 sen)
    wwrite(0x0200, 0x00)
    wwrite(0x0201, 22)
    wwrite(0x0202, 0)
    wwrite(0x0203, 0); wwrite(0x0204, 0); wwrite(0x0205, 0)
    wwrite(0x0206, 1)
    wwrite(0x020A, 5); wwrite(0x020B, 1); wwrite(0x020C, 2)
    wwrite(0x0300, 0x60); wwrite(0x0301, 0x62)
    wwrite(0x00B7, 50); wwrite(0x00B8, 0)
  end
end

local boot_queued = false
local warp_stage = 0
local steps_queued = false
local special_state = 0
local title_ready = false
local title_steps_queued = false

if S and S.skip_splash then
  L.on_exec(0xE08C, 0xE08C, function()
    emu.setState({ ["cpu.pc"] = 0xE08F })
  end)
end

if S and S.skip_title then
  L.on_exec(0xE0A7, 0xE0A7, function()
    init_party(S.party or "solo")
    wwrite(0x00D0, S.loc or 0)
    emu.setState({ ["cpu.pc"] = 0xE11A })
  end)
end

if S and S.skip_logo then
  L.on_exec(0xE2DE, 0xE2DE, function()
    if L.mpr(6) == 0x02 then
      emu.setState({ ["cpu.x"] = 0x01 })
    end
  end)
  L.on_exec(0xC82D, 0xC82D, function()
    if L.mpr(6) == 0x02 then
      emu.setState({ ["cpu.pc"] = 0xC842 })
    end
  end)
end

if S and S.title_steps then
  L.on_exec(0xCFCB, 0xCFCB, function()
    if L.mpr(6) == 0x09 then
      title_ready = true
    end
  end)
end

if S and S.force_bram then
  L.on_exec(0xCFDF, 0xCFDF, function()
    if L.mpr(6) == 0x09 then
      emu.setState({ ["cpu.a"] = 0x00 })
    end
  end)
end

if S and S.warp_idx ~= nil then
  L.on_exec(0xDCFF, 0xDCFF, function()
    if L.mpr(6) == 0x1F and warp_stage == 0 then
      warp_stage = 1
      emu.setState({ ["cpu.pc"] = 0xDD00 })
    end
  end)

  L.on_exec(0xDD0B, 0xDD0B, function()
    if L.mpr(6) == 0x1F and warp_stage == 1 then
      warp_stage = 2
      local ptr = 0x4A74 + S.warp_idx * 9
      wwrite(0x000D, ptr & 0xFF)
      wwrite(0x000E, ptr >> 8)
      emu.setState({ ["cpu.x"] = S.warp_idx, ["cpu.pc"] = 0xDD88 })
    end
  end)

  if S.pos then
    L.on_exec(0xDDCF, 0xDDCF, function()
      if L.mpr(6) == 0x1F and warp_stage == 2 then
        warp_stage = 3
        wwrite(0x00A7, S.pos[1])
        wwrite(0x00A8, S.pos[2])
        wwrite(0x00A9, S.pos[3] or 0x03)
        wwrite(0x1401, S.pos[1])
        wwrite(0x1403, S.pos[2])
      end
    end)
  end
end

if S and S.special == "battle" then
  L.on_exec(0xEAE0, 0xEAE0, function()
    if special_state == 1 and wread(0x00E0) == 0x03 then
      wwrite(0x00C4, wread(0x00C4) & 0xFE)
      emu.setState({ ["cpu.pc"] = 0xEAF9 })
    end
  end)
  L.on_exec(0xEAFC, 0xEAFC, function()
    if special_state == 1 then
      special_state = 2
      wwrite(0x00E3, S.enemy_grp or 0x00)
      wwrite(0x00CB, 0x00)
    end
  end)
end

if S and S.special == "ending" then
  -- Trim the 160-frame black pause at start of Ending Slideshow ($D521)
  L.on_exec(0xD523, 0xD523, function()
    if L.mpr(6) == 0x09 then
      emu.setState({ ["cpu.x"] = 4 })
    end
  end)
end

L.on_exec(0xFF39, 0xFF39, function()
  if S and S.special == "credits" and special_state == 2 then
    special_state = 3
    emu.setState({ ["memoryManager.mpr[6]"] = 0x1B, ["cpu.pc"] = 0xD9C1 })
  end
end)

L.on_frame(function(f)
  if S and S.boot_steps and not boot_queued then
    boot_queued = true
    for _, st in ipairs(S.boot_steps) do
      L.press(st[2], st[1])
    end
  end
  if S and S.title_steps and title_ready and not title_steps_queued then
    title_steps_queued = true
    for _, st in ipairs(S.title_steps) do
      L.press(st[2], st[1])
    end
  end

  if (GOD or 0) ~= 0 then
    for slot = 0, 3 do
      local id = wread(0x0200 + slot * 16)
      if id ~= 0xFF and (id & 0x80) == 0 then
        local mhp = wread(0x02C3 + slot * 16)
        local mmp = wread(0x02C4 + slot * 16)
        if mhp > 0 then wwrite(0x0201 + slot * 16, mhp) end
        wwrite(0x0202 + slot * 16, mmp)
      end
    end
  end

  if (NOENC or 0) ~= 0 then
    wwrite(0x00C4, wread(0x00C4) | 0x01)
  end
  if (NOCLIP or 0) ~= 0 then
    wwrite(0x00C4, wread(0x00C4) | 0x06)
  end
  if (FAST or 0) ~= 0 then
    wwrite(0x0038, 0x20)
  end

  if not S then return end

  local ready = true
  if S.warp_idx ~= nil then
    ready = (warp_stage >= 2)
  end
  if ready and S.wait_e0 then
    ready = (wread(0x00E0) == S.wait_e0)
  end
  if ready and S.steps and not steps_queued then
    steps_queued = true
    for _, st in ipairs(S.steps) do
      L.press(st[2], st[1])
    end
  end

  if ready and S.special and special_state == 0 then
    special_state = 1
    if S.special == "gameover" then
      wwrite(0x0200, wread(0x0200) | 0x80)
      L.on_exec(0xE229, 0xE229, function()
        if special_state == 1 then
          special_state = 2
          emu.setState({ ["cpu.pc"] = 0xE219 })
        end
      end)
    elseif S.special == "ending" then
      wwrite(0x00E5, 0x55)
    elseif S.special == "testmode" or S.special == "credits" then
      L.on_exec(0xE229, 0xE229, function()
        if special_state == 1 then
          special_state = 2
          if S.special == "testmode" then
            emu.setState({ ["memoryManager.mpr[6]"] = 0x1B, ["cpu.pc"] = 0xC386 })
          else
            emu.setState({ ["cpu.pc"] = 0xFF34 })
          end
        end
      end)
    end
  end

  if f == FRAMES - 1 then
    L.log(string.format(
      "FINAL f=%d a2=%02X a4=%02X e0=%02X fa=%02X",
      f, wread(0x00A2), wread(0x00A4), wread(0x00E0), wread(0x00FA)
    ))
    if S.expect then
      for addr, want in pairs(S.expect) do
        local got = wread(addr)
        if want == "nonzero" then
          assert(got ~= 0, string.format("scene %s: WRAM $%04X expected nonzero, got $00", SCENE, 0x2000 + addr))
        else
          assert(got == want, string.format("scene %s: WRAM $%04X expected $%02X, got $%02X", SCENE, 0x2000 + addr, want, got))
        end
      end
    end
  end
end)
