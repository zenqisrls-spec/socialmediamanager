# Manuale Utente (prima versione) — ZenQi Social Media Manager

> Guida semplice per installare, configurare e usare l’app anche senza competenze tecniche.

---

## 1) A cosa serve questa applicazione

L’app aiuta a:

- generare strategie marketing,
- creare idee post social,
- creare bozze campagne ADS,
- organizzare un calendario editoriale,
- gestire un flusso di approvazione e pubblicazione automatica.

---

## 2) Cosa ti serve prima di iniziare

### Requisiti minimi

- Python 3.11 / 3.12 / 3.13
- pip
- Connessione internet (per installare pacchetti)
- Browser web (Chrome/Edge/Firefox)

### Dipendenze usate dal progetto

Installate automaticamente da `requirements.txt`:

- fastapi
- uvicorn
- pydantic
- python-dotenv

Opzionale:

- openai (solo se vuoi risposte AI reali via chiave API)

---

## 3) Installazione passo passo (Windows)

### Metodo consigliato (one-click)

1. Apri `Prompt dei comandi` nella cartella del progetto.
2. Esegui:

```cmd
start_windows.bat
```

Questo script:
- crea `.venv`,
- installa dipendenze,
- crea `.env` se manca,
- avvia il server.

### Metodo manuale (PowerShell)

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload
```

Se `Activate.ps1` è bloccato:

```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned -Force
.\.venv\Scripts\Activate.ps1
```

---

## 4) Installazione passo passo (Linux/macOS)

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

---

## 5) Primo avvio: cosa aprire nel browser

Con server avviato:

- Interfaccia utente: `http://127.0.0.1:8000/`
- Documentazione tecnica API: `http://127.0.0.1:8000/docs`
- Health check: `http://127.0.0.1:8000/health`

---

## 6) Database: dove sono salvati i dati

L’app usa un database SQLite locale:

- file DB: `data/app.db`

Dentro il DB trovi:

- configurazioni applicazione,
- utenti/ruoli demo,
- bozze automazione,
- storico pubblicazioni,
- audit logs.

Non serve installare MySQL/PostgreSQL per partire.

---

## 7) Login e ruoli (per iniziare subito)

Nella UI trovi la sezione **Login utenti / ruoli**.

Utenti demo:

- `admin / admin123`
- `approver / approver123`
- `editor / editor123`

Ruoli:

- **admin**: configura sistema, avvia automazione, vede audit
- **approver**: approva/rifiuta bozze
- **editor**: crea bozze

---

## 8) Configurazione (senza codice)

Nella UI, sezione **Configurazioni (no-code)**:

1. Clicca **Carica config**.
2. Compila i campi necessari.
3. Clicca **Salva config**.

Prima di generare contenuti, compila anche il blocco **Profilo Centro (personalizzazione)**:

- nome centro,
- sito,
- settore,
- città/zona,
- valore distintivo.

In questo modo post e campagne risultano personalizzati (es. Toscana invece di Roma).

Campi importanti:

- `OpenAI API Key` (facoltativa)
- `Model Name`
- `Richiedi approvazione umana`
- `Abilita autopubblicazione`
- `Abilita WhatsApp`
- credenziali Meta/WhatsApp (se vuoi pubblicazione reale)

---

## 9) Come usare l’app (flusso consigliato)

> Interfaccia aggiornata: non è più necessario scrivere JSON manualmente.  
> Usi campi guidati, menu a tendina e pulsanti.

### Fase A — Generazione contenuti

Nelle card dedicate:

- **Strategia**
- **Contenuti social**
- **Campagne ADS**
- **Scheduler**

compila i campi richiesti e clicca i pulsanti “Genera…”.

Per **post** e **campagne ADS** puoi indicare direttamente gli **argomenti** desiderati
(es. “meditazione, gestione stress, sonno”) nel campo dedicato:
non serve intervenire su JSON.

### Fase B — Workflow pubblicazione

1. Vai in **Automazione completa**.
2. Crea una bozza (`Crea bozza`).
3. Se serve, approva (`Approva bozza`) con ruolo approver/admin.
4. Esegui `Esegui automazione ora` (oppure attendi loop automatico).
5. Controlla risultati in bozze/storico e nel **Dashboard operativo**.

---

## 10) Integrazioni esterne: cosa è già attivo

### Attivo

- Meta Graph API (Facebook/Instagram feed)
- WhatsApp Business API (messaggio testo)

### Predisposto ma da completare

- TikTok API
- Google Ads API

---

## 11) Errori comuni e soluzioni rapide

### `TypeError: Failed to fetch`

- Assicurati che il server sia avviato.
- Apri UI da `http://127.0.0.1:8000/` (non da file locale).
- Verifica il campo `URL API Base`.

### `Token mancante` / `Permessi insufficienti`

- Esegui login nella UI.
- Usa l’utente con ruolo corretto.

### Nessuna pubblicazione reale

- Controlla credenziali Meta/WhatsApp nella config.
- Verifica che `autopublish` sia attivo e che la bozza sia approvata (se richiesto).

---

## 12) Backup e manutenzione base

### Backup veloce

Basta copiare:

- `data/app.db`
- `.env` (se presente)

### Aggiornamento dipendenze

```bash
pip install -r requirements.txt --upgrade
```

---

## 13) Checklist finale (go-live locale)

- [ ] Server attivo
- [ ] Login riuscito
- [ ] Config salvata
- [ ] Bozza creata
- [ ] Bozza approvata (se policy attiva)
- [ ] Automazione eseguita
- [ ] Dashboard operativo con KPI visibili

---

## 14) Prossimi miglioramenti consigliati

- hash password + MFA
- token OAuth refresh automatico
- migrazione PostgreSQL
- monitoraggio errori/alert (Sentry/Prometheus)
- test end-to-end su integrazioni esterne
