# ZenQi Social Media Manager (AI)

Applicazione MVP per automatizzare la gestione social e pubblicitaria del centro olistico **ZenQi SRLS** (`zenqi.it`).

## Funzionalità

- Definizione obiettivi marketing (awareness, acquisizione lead, fidelizzazione).
- Generazione piano editoriale multi-canale (Instagram, Facebook, TikTok, LinkedIn).
- Produzione copy e idee creative con AI.
- Bozza di campagne advertising (Meta/Google) con segmenti target, budget e KPI.
- Scheduler automatico con frequenza consigliata.

## Stack tecnico

- Python 3.11, 3.12 o 3.13 (consigliato: 3.11/3.12)
- FastAPI
- Pydantic
- Uvicorn
- Integrazione AI via OpenAI API (opzionale, con fallback locale)

## Cosa installare per farla funzionare

### 1) Prerequisiti di sistema

- **Python 3.11, 3.12 o 3.13** (consigliato 3.11/3.12)
- **pip** (normalmente incluso con Python)
- (Consigliato) **virtual environment** (`venv`)

### 2) Dipendenze Python del progetto

Installa i pacchetti presenti in `requirements.txt`:

- `fastapi`
- `uvicorn`
- `pydantic`
- `python-dotenv`

> `openai` è opzionale: l'app funziona comunque con fallback locale.  
> Se vuoi usare chiamate reali OpenAI:

```powershell
pip install openai
```

### 3) Installazione guidata (Linux/macOS)

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
cp .env.example .env
```

### 4) Avvio API

```bash
uvicorn app.main:app --reload
```

Poi apri: `http://127.0.0.1:8000/docs`

### 5) Guida passo passo per Windows (PowerShell)

1. Installa **Python 3.11 o 3.12** da `python.org` e durante l'installazione seleziona **Add python.exe to PATH**.
2. Apri **PowerShell** nella cartella del progetto.
3. Crea l'ambiente virtuale:

```powershell
py -m venv .venv
```

4. Attiva l'ambiente virtuale:

```powershell
.\.venv\Scripts\Activate.ps1
```

Se ricevi un errore tipo **"Termine '\.venv\Scripts\Activate.ps1' non riconosciuto"**, stai usando il comando senza `.\` iniziale corretto.  
In PowerShell il comando giusto è:

```powershell
.\.venv\Scripts\Activate.ps1
```

> `\.venv\Scripts\Activate.ps1` (senza il punto iniziale) **non** funziona.

Se invece compare un errore di Execution Policy (script bloccati), esegui:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

5. Aggiorna pip e installa dipendenze:

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

6. Crea il file `.env`:

```powershell
copy .env.example .env
```

7. (Opzionale ma consigliato) inserisci in `.env` la tua chiave:

```env
OPENAI_API_KEY=la_tua_chiave
MODEL_NAME=gpt-4.1-mini
```

8. Avvia il server:

```powershell
uvicorn app.main:app --reload
```

9. Apri il browser su:
`http://127.0.0.1:8000/docs`

### 6) Se `pip install` fallisce per proxy/rete

Se ricevi errori simili a `Tunnel connection failed: 403 Forbidden`, devi configurare pip con il proxy aziendale o usare una rete senza restrizioni.

### 7) Errore `pydantic-core` / Rust su Windows

Da questa versione del progetto usiamo `pydantic==1.10.24`, che **non richiede `pydantic-core`**.
Se vedi ancora errori `pydantic-core` / `maturin` / `PyO3`, stai quasi certamente installando da:

- un vecchio `.venv`,
- cache pip,
- un `requirements.txt` non aggiornato.

Procedura rapida (PowerShell):

```powershell
deactivate
Remove-Item -Recurse -Force .venv
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip setuptools wheel
pip cache purge
pip install --index-url https://pypi.org/simple -r requirements.txt
```

Verifica finale:

```powershell
pip show pydantic
```

Deve risultare `Version: 1.10.24`.

## Avvio rapido

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

API disponibile su: `http://127.0.0.1:8000/docs`

## Variabili ambiente

- `OPENAI_API_KEY`: chiave API OpenAI (opzionale ma consigliata)
- `MODEL_NAME`: modello da usare (default: `gpt-4.1-mini`)

## Endpoint principali

- `POST /api/v1/strategy/generate` → genera strategia marketing mensile.
- `POST /api/v1/content/generate-posts` → crea post social e CTA.
- `POST /api/v1/ads/generate-campaigns` → crea campagne advertising.
- `POST /api/v1/scheduler/build` → genera calendario editoriale automatico.

## Note

Questa è una base pronta per evolvere con:

- integrazioni reali a Meta Graph API, TikTok API, Google Ads API;
- approvazione umana prima della pubblicazione;
- tracciamento performance e ottimizzazione automatica delle campagne.
