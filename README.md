# DPE Sport Pilot Oral Examiner

A Socratic oral exam simulator and aviation knowledge tool for Sport Pilot applicants, grounded in KFNL (Fort Collins-Loveland Municipal Airport), the Van's RV-12 with a carbureted Rotax 912 ULS, and northern Colorado airspace and weather. Built with Dash/Plotly, deployed on Render.

---

## Overview

Two modes, one persona — Dave, a friendly 30-year front range DPE who wants you to pass.

### ⚡ DPE Exam Mode
Dave picks 3 weighted knowledge areas per session and uses the Socratic method to probe understanding, not just correct answers. He gives hints when you're stuck, pushes back even when you're right, and only moves on when he's genuinely satisfied. Sessions are logged — areas you haven't seen recently or where confidence was low get prioritized next time.

### ◎ Oracle Mode
You drive. Bring something you flew today, a system you want to understand, a reg you're fuzzy on. Dave explains it thoroughly, calibrates to what you already know, and follows the conversation wherever it goes. Sessions are not logged — use Export Session to save the conversation as a `.txt` file for your notes.

---

## Knowledge Areas (DPE Mode)

| Area | Weight |
|---|---|
| Weather & Meteorology (front range specific) | 10 |
| Aircraft Systems — RV-12 / Rotax 912 | 10 |
| Emergency Procedures | 8 |
| Airspace (KFNL Class D, Denver Class B proximity) | 9 |
| Performance & Limitations (density altitude at 5016 MSL) | 9 |
| Sport Pilot Privileges & Limitations (MOSAIC current rules) | 9 |
| Aeromedical Factors | 7 |
| Aerodynamics & Flight Principles | 7 |
| Cross-Country Planning | 7 |
| Airport & Traffic Pattern Operations | 6 |
| Navigation & Charts | 6 |
| Required Documents & Inspections | 4 |

Topic selection is weighted by base difficulty, recency penalty (areas covered recently are deprioritized), and confidence score (areas where hints were needed get boosted).

---

## Tech Stack

| Layer | Technology |
|---|---|
| UI | Dash 2.17 + Dash Bootstrap Components |
| AI | Anthropic Claude (claude-sonnet-4) |
| Hosting | Render (Starter tier, $7/mo) |
| Persistence | Render persistent disk at `/var/data` |
| Repo | GitHub (auto-deploy on push to `main`) |

---

## Recreating from Scratch

### 1. Local project folder

```bash
mkdir dpe-sport-pilot
cd dpe-sport-pilot
```

### 2. Initialize Git and create GitHub repo

```bash
git init
```

Create an empty repo at github.com/new — name it `dpe-sport-pilot`, no README, no .gitignore.

```bash
git remote add origin https://github.com/mollymaskrey/dpe-sport-pilot.git
```

### 3. Create scaffolding files

**.gitignore**
```bash
cat > .gitignore << 'EOF'
__pycache__/
*.pyc
*.pyo
.env
.DS_Store
*.egg-info/
dist/
build/
.venv/
venv/
EOF
```

**Procfile**
```bash
cat > Procfile << 'EOF'
web: gunicorn main:server --workers 1 --threads 2 --timeout 120
EOF
```

**requirements.txt**
```bash
cat > requirements.txt << 'EOF'
dash==2.17.1
dash-bootstrap-components==1.6.0
anthropic>=0.40.0
gunicorn==22.0.0
EOF
```

### 4. First commit and push

```bash
git add .
git commit -m "initial scaffold"
git branch -M main
git push -u origin main
```

---

## Render Setup

### 5. Create Web Service

1. Go to **render.com** → your project → **New Web Service**
2. Connect repo: `mollymaskrey/dpe-sport-pilot`
   - If repo doesn't appear: Credentials → Configure in GitHub → grant access
3. Settings:
   - **Branch:** `main`
   - **Runtime:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn main:server --workers 1 --threads 2 --timeout 120`
   - **Instance Type:** Starter ($7/mo) — supports persistent disk

### 6. Environment variables

In Render → **Environment**:

| Key | Value |
|---|---|
| `ANTHROPIC_API_KEY` | your key |

### 7. Persistent disk

In Render → **Disk** → Add disk:

| Field | Value |
|---|---|
| Name | `session-data` |
| Mount Path | `/var/data` |
| Size | 1 GB |

The session log (`/var/data/session_log.json`) tracks topic recency and confidence scores across DPE sessions. Oracle sessions are never logged.

---

## Deploy

Render auto-deploys on every push to `main`:

```bash
git add .
git commit -m "your message"
git push
```

App is live at: **https://dpe-sport-pilot.onrender.com**

---

## Session Log Format (DPE Mode only)

```json
{
  "weather": {
    "last_seen": "2026-05-16",
    "times_seen": 3,
    "confidence": 0.833,
    "last_hint_count": 0
  },
  "emergency": {
    "last_seen": "2026-05-14",
    "times_seen": 1,
    "confidence": 0.600,
    "last_hint_count": 2
  }
}
```

Confidence is computed from hint count per topic. Areas with lower confidence and longer time since last seen are weighted higher in the next session's topic selection. Oracle mode sessions are excluded from this log.

---

## Exporting Oracle Sessions

Hit **⬇ Export Session** in the header at any time. Downloads a `.txt` file formatted as:

```
DPE Sport Pilot Oral Examiner — Oracle Mode
Pilot: Molly
Date: 2026-05-16
============================================================

[Dave]
Hey Molly! Good to see you...

[Molly]
I was working on the 912 the other day...
```

Ready to open in Word or paste into your notes.

---

## Local Development

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export ANTHROPIC_API_KEY=your_key
python main.py
```

App opens at `http://localhost:8050`. Session log writes to `/var/data/session_log.json` — create that directory locally if needed:

```bash
sudo mkdir -p /var/data && sudo chmod 777 /var/data
```
