# docs/ZEBRA_Commands.md
# ZEBRA ZPL Commands Reference

## Podstawowe komendy

### Host Commands
- `~HI` - Host Identification
- `~HS` - Host Status
- `^WD` - Download Configuration

### Label Commands
- `^XA` - Start Format
- `^XZ` - End Format
- `^FO` - Field Origin
- `^A0` - Scalable Font
- `^FD` - Field Data
- `^FS` - Field Separator

### Barcode Commands
- `^BY` - Bar Code Field Default
- `^BCN` - Code 128 Bar Code

## Przykłady etykiet

### Etykieta produktu
```zpl
^XA
^FO50,50^A0N,50,50^FDNazwa Produktu^FS
^FO50,120^A0N,30,30^FDKod: PRD001^FS
^FO50,170^BY3
^BCN,100,Y,N,N
^FD1234567890123^FS
^XZ
```

### Etykieta magazynowa
```zpl
^XA
^FO20,20^A0N,40,40^FDMAGAZYN^FS
^FO20,70^A0N,30,30^FDStan: 150 szt^FS
^FO20,120^A0N,25,25^FDLokalizacja: A1-B2^FS
^XZ
```
