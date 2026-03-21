# ZenQi Social Media Manager (AI)

Applicazione MVP per automatizzare la gestione social e pubblicitaria del centro olistico **ZenQi SRLS** (`zenqi.it`).

## Funzionalità

- Definizione obiettivi marketing (awareness, acquisizione lead, fidelizzazione).
- Generazione piano editoriale multi-canale (Instagram, Facebook, TikTok, LinkedIn).
- Produzione copy e idee creative con AI.
- Bozza di campagne advertising (Meta/Google) con segmenti target, budget e KPI.
- Scheduler automatico con frequenza consigliata.

## Stack tecnico

- Python 3.11+
- FastAPI
- Pydantic
- Uvicorn
- Integrazione AI via OpenAI API (opzionale, con fallback locale)

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
