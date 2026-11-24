; Bank $09 horizontal Title / BRAM menu cursor replacement ($D28E..$D39A, 269 B max).
.MEMORYMAP
  SLOTSIZE $2000
  DEFAULTSLOT 0
  SLOT 0 $C000
.ENDME

.ROMBANKMAP
  BANKSTOTAL 1
  BANKSIZE $2000
  BANKS 1
.ENDRO

.EMPTYFILL $EA

.BANK 0 SLOT 0

.ORG $128E
.SECTION "Menu2" FORCE
Menu2_Run:
  lda #$01
  ldx #$03
  bra MenuCommon
.ENDS

.ORG $12BD
.SECTION "Menu4" FORCE
Menu4_Run:
  lda #$03
  ldx #$07
MenuCommon:
  sta $3F0D
  stx $3F0E
  lda #$01
  sta $3F09
  sty $3F0A
  stz $BA
@loop:
  bsr MenuInput
  lda $3F0E
  jsr ClearCursorH
  lda $BA
  asl
  clc
  adc $3F0A
  bsr DrawPearl
  stz $3F12
  jsr $EE7E
  .dw $D28A
  jsr $EE8A
  .dw $D28A
  dec $3F12
  jsr $EEF7
  .dw @loop
  jmp $D28A

MenuInput:
  jsr $EF03         ; Up not pressed?
  .dw @chk_right
  bra @prev
@chk_right:
  jsr $EF07         ; Right not pressed?
  .dw @chk_down
@prev:
  lda $BA
  beq @done
  dec $BA
  jmp $EC39
@chk_down:
  jsr $EF0B         ; Down not pressed?
  .dw @chk_left
  bra @next
@chk_left:
  jsr $EF0F         ; Left not pressed?
  .dw @chk_sel
@next:
  lda $BA
  cmp $3F0D
  bcs @done
  inc $BA
  jmp $EC39
@chk_sel:
  jsr $EEFB         ; Select not pressed?
  .dw @done
  lda $BA
  ina
  cmp $3F0D
  beq @store
  bcc @store
  cla
@store:
  sta $BA
  jmp $EC39
@done:
  rts

DrawPearl:
  pha
  tay
  ldx $3F09
  lda #$66
  jsr $D39B
  ldx $3F09
  ply
  iny
  lda #$76
  jsr $D39B
  jmp $E2C0
.ENDS

.ORG $135D
.SECTION "Clear4" FORCE
ClearCursor4:
  lda #$07
ClearCursorH:
  sta $3F2A
  ldx $3F09
  ldy $3F0A
  jsr $CA9C
  lda #$01
  sta $3F29
  jmp $C7E5
.ENDS
