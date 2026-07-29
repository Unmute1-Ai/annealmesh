# Hermes-Nemotron mesh

Web, text, and voice interfaces for a multi-model candidate-ranking pipeline.

## Setup

```powershell
cd C:\Users\cindy\builds\hermes-nemotron-mesh
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .
Copy-Item .env.example .env
```

Set model and Speech NIM endpoints in `.env`.

## Web app

```powershell
hermes-web
```

Open `http://127.0.0.1:8080`. Microphone access requires HTTPS when the app is
served from a non-local address.

Production deployments should place the service behind an HTTPS reverse proxy,
keep `.env` outside the image, and expose `/health` to the platform.

## CLI

```powershell
hermes-mesh "Design a fault-tolerant event ingestion service"
hermes-voice .\question.wav -o .\answer.wav
```
