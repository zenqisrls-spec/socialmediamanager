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

Se ricevi esattamente l'errore **"L'esecuzione di script è disabilitata nel sistema in uso"**:

```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned -Force
.\.venv\Scripts\Activate.ps1
```

Se non vuoi modificare la policy utente, puoi usare il bypass solo per la sessione corrente:

```powershell
powershell -ExecutionPolicy Bypass -NoProfile -Command ". .\.venv\Scripts\Activate.ps1; python --version"
```

Alternativa senza script PowerShell (Prompt dei comandi/CMD):

```cmd
.venv\Scripts\activate.bat
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

### 5.b) Avvio rapido Windows con script `.bat` (one-click)

Se preferisci evitare PowerShell e problemi di Execution Policy, puoi usare:

```cmd
start_windows.bat
```

Lo script:
- crea `.venv` se manca,
- attiva venv con `activate.bat`,
- aggiorna `pip/setuptools/wheel`,
- installa dipendenze,
- crea `.env` da `.env.example` se non esiste,
- avvia `uvicorn app.main:app --reload`.

### 6) Se `pip install` fallisce per proxy/rete

Se ricevi errori simili a `Tunnel connection failed: 403 Forbidden`, devi configurare pip con il proxy aziendale o usare una rete senza restrizioni.

### 7) Errore `pydantic-core` / Rust su Windows

Con Python 3.14 devi usare **Pydantic v2** (questo progetto richiede `pydantic>=2.12.4,<3`).
Se vedi errori `pydantic-core` / `maturin` / `PyO3`, stai quasi certamente installando da:

- un vecchio `.venv`,
- cache pip,
- un `requirements.txt` non aggiornato.

Procedura rapida (PowerShell):

```powershell
if (Get-Command deactivate -ErrorAction SilentlyContinue) { deactivate }
Remove-Item -Recurse -Force .venv
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip setuptools wheel
pip cache purge
pip install --index-url https://pypi.org/simple --upgrade "pydantic>=2.12.4,<3"
pip install --index-url https://pypi.org/simple -r requirements.txt
```

Verifica finale:

```powershell
pip show pydantic
```

Deve risultare una versione `2.x` (consigliato `>=2.12.4`).

## Avvio rapido

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

API disponibile su: `http://127.0.0.1:8000/docs`
Interfaccia grafica web: `http://127.0.0.1:8000/`

## Come usarla (anche se non conosci le API)

1. Avvia il server (`uvicorn app.main:app --reload`).
2. Apri il browser su `http://127.0.0.1:8000/` (non aprire `index.html` direttamente da file).
3. Nell'interfaccia:
   - clicca **Verifica API** per controllare connessione;
   - usa i pulsanti **Genera strategia / Genera post / Genera campagne / Genera calendario**.

### Che risultati ottieni

- **Strategia**: posizionamento, pillar mensili, KPI, funnel offerta.
- **Contenuti social**: elenco idee post con canale, hook, caption e call to action.
- **Campagne ADS**: proposte campagne Meta/Google con target, copy, budget e KPI.
- **Scheduler**: calendario editoriale con data, canale, orario e tema.

### Errore `TypeError: Failed to fetch` nella UI

Di solito significa che la pagina non riesce a raggiungere il backend:

- verifica che il server sia attivo su `http://127.0.0.1:8000`;
- usa la pagina da `http://127.0.0.1:8000/` (non da `file://...`);
- controlla il campo **URL API Base** nella UI (deve essere `http://127.0.0.1:8000` in locale).

## Variabili ambiente

- `OPENAI_API_KEY`: chiave API OpenAI (opzionale ma consigliata)
- `MODEL_NAME`: modello da usare (default: `gpt-4.1-mini`)

Puoi impostarle in due modi:

1. **File `.env`** (metodo classico): nella root del progetto, copiando `.env.example` in `.env`.
2. **Interfaccia grafica** su `http://127.0.0.1:8000/` nella sezione **Configurazioni (no-code)**, che salva su `data/app_config.json`.

## Autorizzazione umana e autopubblicazione

Nella UI trovi un workflow base:

- `Richiedi approvazione umana` ✅: ogni pubblicazione va in stato `pending_approval`.
- `Abilita autopubblicazione` ✅: se l'approvazione è disattivata, la pubblicazione passa in stato `simulated_published`.
- `Abilita WhatsApp`: impostazione pronta lato configurazione (attualmente simulata).

> Nota: in questa versione l'invio verso social/WhatsApp è **simulato**.  
> Per pubblicazione reale servono integrazioni API dedicate (Meta Graph API, WhatsApp Business API, TikTok API, Google Ads API) e gestione token/permessi.

## Versione con automazione completa (operativa)

Flusso disponibile nella UI:

1. Crea bozza contenuto con canale e data/ora (`Automazione completa`).
2. Approva/Rifiuta bozza (human approval).
3. Esegui automazione ora oppure lascia il job automatico (ogni 30 secondi).
4. Controlla storico pubblicazioni.

Endpoint automazione:

- `POST /api/v1/automation/drafts`
- `GET /api/v1/automation/drafts`
- `POST /api/v1/automation/drafts/{draft_id}/approve`
- `POST /api/v1/automation/drafts/{draft_id}/reject`
- `POST /api/v1/automation/run`
- `GET /api/v1/automation/published`

Il sistema salva stato in `data/automation_state.json`.

### Dashboard di controllo

Endpoint:

- `GET /api/v1/dashboard/summary`

Mostra KPI operativi in tempo reale:
- bozze totali,
- pubblicazioni totali,
- pubblicazioni riuscite/fallite,
- distribuzione bozze per stato e canale.

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
