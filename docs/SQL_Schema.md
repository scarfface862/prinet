
# docs/SQL_Schema.md
# WAPROMAG Database Schema

## Tabele główne

### Kontrahenci
```sql
CREATE TABLE Kontrahenci (
    ID int IDENTITY(1,1) PRIMARY KEY,
    Kod nvarchar(20) NOT NULL UNIQUE,
    Nazwa nvarchar(200) NOT NULL,
    NIP nvarchar(15),
    REGON nvarchar(14),
    Adres nvarchar(300),
    KodPocztowy nvarchar(10),
    Miasto nvarchar(100),
    Telefon nvarchar(50),
    Email nvarchar(100),
    DataUtworzenia datetime DEFAULT GETDATE(),
    DataModyfikacji datetime DEFAULT GETDATE(),
    CzyAktywny bit DEFAULT 1
);
```

### Produkty
```sql
CREATE TABLE Produkty (
    ID int IDENTITY(1,1) PRIMARY KEY,
    Kod nvarchar(30) NOT NULL UNIQUE,
    KodKreskowy nvarchar(50),
    Nazwa nvarchar(200) NOT NULL,
    Opis nvarchar(500),
    Kategoria nvarchar(50),
    JednostkaMiary nvarchar(10) DEFAULT 'szt',
    CenaZakupu decimal(10,2) DEFAULT 0,
    CenaSprzedazy decimal(10,2) DEFAULT 0,
    StanMagazynowy decimal(10,3) DEFAULT 0,
    StanMinimalny decimal(10,3) DEFAULT 0,
    StawkaVAT decimal(5,2) DEFAULT 23.00,
    DataUtworzenia datetime DEFAULT GETDATE(),
    CzyAktywny bit DEFAULT 1
);
```

### DokumentyMagazynowe
```sql
CREATE TABLE DokumentyMagazynowe (
    ID int IDENTITY(1,1) PRIMARY KEY,
    Numer nvarchar(50) NOT NULL UNIQUE,
    TypDokumentu nvarchar(10) NOT NULL, -- PZ, WZ, MM, PW, RW
    KontrahentID int FOREIGN KEY REFERENCES Kontrahenci(ID),
    DataWystawienia datetime DEFAULT GETDATE(),
    DataOperacji datetime DEFAULT GETDATE(),
    Magazyn nvarchar(50) DEFAULT 'GŁÓWNY',
    WartoscNetto decimal(12,2) DEFAULT 0,
    WartoscVAT decimal(12,2) DEFAULT 0,
    WartoscBrutto decimal(12,2) DEFAULT 0,
    Status nvarchar(20) DEFAULT 'ROBOCZA',
    CzyZatwierdzona bit DEFAULT 0
);
```

### KonfiguracjaDrukarek
```sql
CREATE TABLE KonfiguracjaDrukarek (
    ID int IDENTITY(1,1) PRIMARY KEY,
    NazwaDrukarki nvarchar(50) NOT NULL,
    AdresIP nvarchar(15) NOT NULL,
    Port int DEFAULT 9100,
    ModelDrukarki nvarchar(50),
    TypDrukarki nvarchar(20) DEFAULT 'ZEBRA',
    Lokalizacja nvarchar(100),
    CzyAktywna bit DEFAULT 1,
    FormatEtyket nvarchar(50) DEFAULT 'STANDARD'
);
```

## Przykładowe zapytania

### Produkty z niskim stanem
```sql
SELECT p.Kod, p.Nazwa, sm.Stan, p.StanMinimalny
FROM Produkty p
LEFT JOIN StanyMagazynowe sm ON p.ID = sm.ProduktID
WHERE sm.Stan < p.StanMinimalny
  AND p.CzyAktywny = 1;
```

### Dokumenty z pozycjami
```sql
SELECT d.Numer, d.TypDokumentu, k.Nazwa as Kontrahent,
       p.Kod as KodProduktu, pdm.Ilosc, pdm.CenaJednostkowa
FROM DokumentyMagazynowe d
LEFT JOIN Kontrahenci k ON d.KontrahentID = k.ID
LEFT JOIN PozycjeDokumentowMagazynowych pdm ON d.ID = pdm.DokumentID
LEFT JOIN Produkty p ON pdm.ProduktID = p.ID
WHERE d.DataWystawienia >= '2025-06-01'
ORDER BY d.DataWystawienia DESC;
```

