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
- `openai`

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

### 7) Errore `pydantic-core` / Rust su Windows (`metadata-generation-failed`)

Se durante `pip install -r requirements.txt` vedi messaggi come:

- `error: metadata-generation-failed`
- `This is an issue with the package mentioned above: pydantic-core`
- richieste di installare `Rust`/`Cargo`

di solito stai usando una versione Python non supportata dalle wheel precompilate del pacchetto, oppure `pip` è troppo vecchio e prova a compilare da sorgente.

Procedura consigliata (PowerShell):

1. Verifica versione Python:

```powershell
py --version
```

2. Usa esplicitamente Python **3.11** o **3.12** (consigliato per massima compatibilità):

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

3. Aggiorna gli strumenti di build/install:

```powershell
python -m pip install --upgrade pip setuptools wheel
```

4. Installa prima le dipendenze binarie principali:

```powershell
pip install --only-binary=:all: pydantic-core pydantic
```

5. Reinstalla tutte le dipendenze:

```powershell
pip install -r requirements.txt
```

Se il punto 4 fallisce ancora, quasi sempre significa che la tua versione di Python non ha wheel disponibili per `pydantic-core`: ricrea il venv con `py -3.11` e riprova.

> Nota importante: con **Python 3.14.x** puoi ricevere proprio questo errore (`pydantic-core` + Rust/Cargo) perché alcune dipendenze non pubblicano ancora wheel compatibili. In quel caso usa 3.11 o 3.12.

#### Posso risolvere **senza reinstallare Python**?

Sì, hai 2 strade:

1. **Restare su Python 3.14** e compilare da sorgente (più lenta/fragile):
   - installa **Rust** (`rustup`) + **Microsoft C++ Build Tools**;
   - poi esegui:

```powershell
python -m pip install --upgrade pip setuptools wheel maturin
pip install pydantic-core --no-binary pydantic-core
pip install -r requirements.txt
```

2. **Non toccare Python di sistema**, ma usare un Python 3.12 isolato nel progetto (consigliato):
   - installa `uv` una sola volta;
   - crea/usa un interpreter locale 3.12 solo per questo progetto:

```powershell
uv python install 3.12
uv venv --python 3.12 .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

La soluzione 2 evita di reinstallare/disinstallare il Python già presente sul PC ed è la più stabile.

#### Se `uv` non funziona

Nessun problema: puoi procedere senza `uv`.

Opzione A (se hai già Python 3.11/3.12 installato):

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

Opzione B (se hai solo Python 3.14 e non vuoi reinstallare Python):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip setuptools wheel
pip install --only-binary=:all: "pydantic>=2.12.4,<3" "pydantic-core>=2.35.0,<3"
pip install -r requirements.txt
```

Per Python 3.14 è **meglio evitare la build da sorgente** di `pydantic-core` (Rust/PyO3), perché può fallire con errori su `jiter`/`PyUnicode_*`.

Se ricevi l'errore:

- `Python interpreter version (3.14) is newer than PyO3's maximum supported version (3.13)`

stai compilando da sorgente. Interrompi e forza ruote binarie aggiornate:

```powershell
pip uninstall -y pydantic-core pydantic
pip cache purge
python -m pip install --upgrade pip setuptools wheel
pip install --only-binary=:all: "pydantic>=2.12.4,<3" "pydantic-core>=2.35.0,<3"
pip install -r requirements.txt
```

Se ancora prova a compilare, esegui:

```powershell
pip install --only-binary=:all: -r requirements.txt
```

Nota: se imposti variabili temporanee come `PYO3_USE_ABI3_FORWARD_COMPATIBILITY`, chiudi e riapri PowerShell prima di ritentare con le wheel binarie.

Se invece vedi errori Rust come `cannot find function ... PyUnicode_New` dentro `jiter`/`pyo3`,
stai quasi certamente compilando una versione non compatibile di `pydantic-core` per Python 3.14.
Aggiorna prima `pydantic` e poi reinstalla:

```powershell
python -m pip install --upgrade pip setuptools wheel
pip install "pydantic>=2.12.4,<3" "pydantic-core>=2.35.0,<3"
pip install -r requirements.txt
```

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
