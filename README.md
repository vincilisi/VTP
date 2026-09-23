# VTP WebApp - primo prototipo

## Avvio

```bash
python -m venv .venv
```

Windows PowerShell:
```powershell
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

macOS/Linux:
```bash
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Apri http://127.0.0.1:8000

## Funzioni presenti
- registrazione locale di nome, cognome, targa e modello
- firma tracciata con mouse o dito
- caricamento statino PDF
- estrazione preliminare dei servizi Venezia Terminal Passeggeri
- conteggi separati Aviaria e Indennita radiogeno

## Regole provvisorie
- SALONI o USCITA SALONI: 15 euro Aviaria
- RXM o RXP: 2 euro Indennita radiogeno
