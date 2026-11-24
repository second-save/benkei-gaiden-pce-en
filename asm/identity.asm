; Minimal HuC6280 bank-$30 assembly payload proving wla-huc6280 + wlalink pipeline.
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
.ORG $0000
.SECTION "IdentitySig" FORCE
IdentitySig:
  .DB "BENKEI-GAIDEN-EN", 0
  nop
  rts
.ENDS
