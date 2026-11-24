; Bank $02 free tail ($DFBC..$DFFF, 68 B max) far-string hooks for B$02:$CE45/$CF27/$D9CF/$DA01.
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

.EMPTYFILL $FF

.BANK 0 SLOT 0
.ORG $1FBC
.SECTION "EngineB02" FORCE

; Check if ($0D) starts with far-string sentinel $FC <bank> <lo> <hi>.
; Preserves nothing needed by $CE48/$CF32 except updating $0D/$0E and MPR2/MPR3.
ResolveFar0D:
  cly
  lda ($0D),Y
  cmp #$FC
  bne @ret
  iny
  lda ($0D),Y       ; bank ($61..$7E)
  pha               ; save bank on stack before remapping MPR2/MPR3
  iny
  lda ($0D),Y       ; ptr lo
  tax
  iny
  lda ($0D),Y       ; ptr hi
  stx $0D
  sta $0E
  pla
  tam #$04          ; MPR2 ($4000..$5FFF) = bank
  ina
  tam #$08          ; MPR3 ($6000..$7FFF) = bank + 1
@ret:
  rts

Hook_CE45:
  jsr ResolveFar0D
  ldx $00
  ldy $01
  rts

Hook_CF27:
  jsr ResolveFar0D
  ldx $87
  ldy $88
  rts

; Switch MPR5 ($A000..$BFFF) to Bank $60 for translated enemy names ($A000 pointer table).
Hook_EnemyBank:
  lda #$60
  tam #$20
  tya
  asl
  tay
  rts

.ENDS
