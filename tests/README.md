# Unit Tests für Kritische Funktionen

Dieser Ordner enthält Unit-Tests für die **kritischsten Funktionen** des Discord Bots - Funktionen, bei denen wirklich etwas schiefgehen kann.

## Getestete Kritische Operationen

### 1. **test_dbms.py** - Datenbank-Operationen (KRITISCH!)
Tests für Funktionen, die bei Fehlern zu Datenverlust oder Inkonsistenzen führen können:
- `connect()` - Datenbankverbindung mit Retry-Logik
- `insert_data()` - Daten einfügen (Duplicate Keys, unbestätigte Writes)
- `update_data()` - Daten aktualisieren (mehrere Dokumente)
- `delete_data()` - Daten löschen (gefährlich bei leeren Queries!)
- `upload_table()` - Komplette Tabelle hochladen/ersetzen

### 2. **test_db_loader.py** - CSV Import & Initialisierung (KRITISCH!)
Tests für Funktionen, die beim App-Start oder Datenimport schieflaufen können:
- `import_tables()` - CSV-Dateien in DB laden (Encoding, fehlende Dateien)
- `initialize_discord_tables()` - Discord-Tabellen initialisieren
- UTF-8 Sonderzeichen-Handling
- Ungültige ID-Konvertierung
- Force-Reload Logik

### 3. **test_dish_selector.py** - Datenbank-Abfragen
Tests für zufällige Datenbankabfragen:
- Umgang mit leeren Tabellen
- Fehlende Keys in Dokumenten

### 4. **test_fun_fact_selector.py** - Datenbank-Abfragen
Tests für Fun-Fact Auswahl:
- Umgang mit leeren Ergebnissen
- Mehrfache Abfragen

### 5. **test_translator.py** - API-Aufrufe (KRITISCH!)
Tests für externe API-Calls die fehlschlagen können:
- Übersetzung mit Retry-Logik (10 Versuche)
- Fallback auf Originaltext bei Fehler
- User-spezifische Sprachen aus DB

## Warum diese Tests wichtig sind

Diese Tests konzentrieren sich auf **kritische Fehlerszenarien**:

1. **Datenverlust verhindern**: DB-Operationen werden getestet, die Daten löschen/überschreiben
2. **Connection-Failures**: Netzwerkprobleme beim DB-Connect oder API-Calls
3. **Encoding-Issues**: UTF-8 Sonderzeichen in CSV-Imports
4. **Race Conditions**: Mehrfache gleichzeitige Updates
5. **Empty/Invalid Data**: Umgang mit leeren Tabellen oder ungültigen Werten

## Tests ausführen

### Alle Tests:
```powershell
python -m unittest discover -s tests -p "test_*.py" -v
```

### Nur kritische DB-Tests:
```powershell
python -m unittest tests.test_dbms tests.test_db_loader -v
```

### Einzelne Testdateien:
```powershell
python tests/test_dbms.py
python tests/test_db_loader.py
python tests/test_translator.py
```

### Mit Coverage (optional):
```powershell
pip install pytest pytest-cov
pytest --cov=discord_bot --cov-report=html tests/
```

## Test-Struktur

Jeder Test folgt dem **AAA-Pattern**:
- **Arrange**: Mocks und Test-Daten vorbereiten
- **Act**: Die kritische Funktion ausführen
- **Assert**: Prüfen, ob Fehler korrekt behandelt werden

Alle externen Abhängigkeiten (MongoDB, Discord API, Google Translate) werden gemockt.

## Was getestet wird

✅ **Fehlerbehandlung** - Was passiert bei Exceptions?  
✅ **Retry-Logik** - Werden Verbindungen wiederholt?  
✅ **Datenintegrität** - Werden Daten korrekt gespeichert/geladen?  
✅ **Edge Cases** - Leere Daten, ungültige IDs, fehlende Dateien  
✅ **Rollback-Verhalten** - Was passiert wenn etwas schiefgeht?

## Wichtige Szenarien

### Datenbank-Connection schlägt fehl
```python
# Test prüft: Wird nach 3 Versuchen eine Exception geworfen?
test_connect_fails_after_max_retries
```

### CSV-Import mit ungültigen Daten
```python
# Test prüft: Werden ungültige IDs korrekt behandelt?
test_import_tables_handles_invalid_id_conversion
```

### Leere Query löscht alle Daten
```python
# Test prüft: delete_data({}) ist gefährlich!
test_delete_data_with_empty_query_deletes_all
```

### API-Call schlägt 10x fehl
```python
# Test prüft: Wird Originaltext zurückgegeben?
test_execute_function_returns_original_text_on_failure
```
