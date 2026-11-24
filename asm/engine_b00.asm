; Bank $00 free tail ($FF90..$FFDF, 80 B max) safe wait wrappers preserving MPR2/MPR3 across $EF70.
.MEMORYMAP
  SLOTSIZE $2000
  DEFAULTSLOT 0
  SLOT 0 $E000
.ENDME

.ROMBANKMAP
  BANKSTOTAL 1
  BANKSIZE $2000
  BANKS 1
.ENDRO

.EMPTYFILL $FF

.BANK 0 SLOT 0
.ORG $1F90
.SECTION "EngineB00" FORCE

SafeWait_E2C0:
  tma #$04
  pha
  tma #$08
  pha
  jsr $E2C0
  bra _SafeWait_Restore

SafeWait_EF33:
  tma #$04
  pha
  tma #$08
  pha
  jsr $EF33

_SafeWait_Restore:
  pla
  tam #$08
  pla
  tam #$04
  rts

; Direct far-string copier called from B$00:$F915 with MPR6 untouched.
Hook_F915:
  cly
  lda ($D8),Y
  cmp #$FC
  bne @copy
  iny
  lda ($D8),Y       ; bank ($61..$7E)
  pha               ; save before remapping MPR2/MPR3
  iny
  lda ($D8),Y       ; ptr lo
  tax
  iny
  lda ($D8),Y       ; ptr hi
  stx $D8
  sta $D9
  pla
  tam #$04          ; MPR2 ($4000..$5FFF) = bank
  ina
  tam #$08          ; MPR3 ($6000..$7FFF) = bank + 1
@copy:
  ldx $DC
  cly
@loop:
  lda ($D8),Y
  sta $2E00,X
  inx
  iny
  cmp #$FF
  bne @loop
  stx $DC
  rts

Inc11By3:
  inc $11
  inc $11
  inc $11
  rts

.ENDS
