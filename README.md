# Chall API

FastAPI boilerplate.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

## Run

```bash
uvicorn app.main:app --reload
```

- Health check: http://localhost:8000/api/v1/health
- Docs: http://localhost:8000/docs

## Test

```bash
pytest
```
# space-repetition-app
