"""
main.py — DPE Sport Pilot Oral Examiner
Socratic oral exam simulator grounded in KFNL, RV-12/Rotax 912, northern Colorado.
Deploys to Render with persistent disk at /var/data for session logging.

Architecture: single layout, splash/exam toggled via display style.
All dcc.Store components exist from page load — no dynamic component creation.
"""

import os
import json
import random
from datetime import date

import anthropic
from dash import Dash, dcc, html, Input, Output, State, ctx, no_update
import dash_bootstrap_components as dbc

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

SESSION_LOG_PATH = "/var/data/session_log.json"
PORT = int(os.environ.get("PORT", 8050))

SHOW  = {"display": "block"}
HIDE  = {"display": "none"}

# ---------------------------------------------------------------------------
# TRON CSS
# ---------------------------------------------------------------------------

TRON_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&display=swap');

body { margin: 0; padding: 0; background: #000; }

.tron-wrap {
    background: #000;
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    position: relative;
    overflow: hidden;
    padding: 2rem;
    font-family: 'Share Tech Mono', 'Courier New', monospace;
}
.scan-line {
    position: fixed; top: 0; left: 0;
    width: 100%; height: 2px;
    background: linear-gradient(90deg, transparent, #00eeff, transparent);
    animation: scan 4s linear infinite;
    opacity: 0.4; pointer-events: none; z-index: 10;
}
@keyframes scan { 0% { top: 0%; } 100% { top: 100%; } }
.tron-logo {
    font-size: 11px; letter-spacing: 6px; color: #555;
    text-transform: uppercase; margin-bottom: 8px;
    animation: fadeIn 1s ease 0.5s both;
}
.tron-title {
    font-size: 52px; font-weight: bold; letter-spacing: 14px;
    color: #00eeff; text-transform: uppercase;
    text-shadow: 0 0 20px #00eeff, 0 0 60px #00eeff88, 0 0 100px #00eeff44;
    margin-bottom: 4px; animation: fadeIn 1s ease 0.8s both;
    font-family: 'Share Tech Mono', monospace;
}
.tron-sub {
    font-size: 10px; letter-spacing: 6px; color: #006677;
    text-transform: uppercase; margin-bottom: 48px;
    animation: fadeIn 1s ease 1.1s both;
}
.loader-wrap { width: 380px; margin-bottom: 40px; animation: fadeIn 1s ease 1.4s both; }
.loader-label {
    font-size: 9px; letter-spacing: 4px; color: #006677;
    text-transform: uppercase; margin-bottom: 8px;
    display: flex; justify-content: space-between;
}
.loader-bar-bg {
    width: 100%; height: 3px; background: #001a1f;
    border: 1px solid #003344; overflow: hidden;
}
.loader-bar {
    height: 100%; width: 0%; background: #00eeff;
    box-shadow: 0 0 10px #00eeff, 0 0 20px #00eeff88;
    animation: load 3s ease 1.8s forwards;
}
@keyframes load {
    0% { width: 0%; } 20% { width: 15%; } 45% { width: 42%; }
    70% { width: 71%; } 88% { width: 88%; } 100% { width: 100%; }
}
.auth-panel {
    width: 400px; border: 1px solid #004455; background: #000d10;
    padding: 28px 32px; animation: fadeIn 1.2s ease 4.8s both; position: relative;
}
.auth-panel::before {
    content: ''; position: absolute;
    top: -1px; left: 24px; right: 24px; height: 1px;
    background: #00eeff; box-shadow: 0 0 10px #00eeff;
}
.auth-label {
    font-size: 9px; letter-spacing: 4px; color: #006677;
    text-transform: uppercase; margin-bottom: 14px;
    font-family: 'Share Tech Mono', monospace;
}
.auth-input-wrap {
    display: flex; align-items: center; border: 1px solid #004455;
    background: #000a0d; padding: 10px 14px; margin-bottom: 16px;
    transition: border-color 0.3s;
}
.auth-input-wrap:focus-within { border-color: #00eeff; box-shadow: 0 0 12px #00eeff22; }
.auth-prompt {
    color: #00eeff; font-size: 14px; margin-right: 10px;
    opacity: 0.7; user-select: none; font-family: 'Share Tech Mono', monospace;
}
#pilot-name-input {
    background: transparent !important; border: none !important;
    outline: none !important; color: #00eeff !important;
    font-family: 'Share Tech Mono', 'Courier New', monospace !important;
    font-size: 14px !important; letter-spacing: 3px !important;
    flex: 1; caret-color: #00eeff; box-shadow: none !important; width: 100%;
}
#pilot-name-input::placeholder { color: #003344; letter-spacing: 2px; }
.auth-btn {
    width: 100%; background: transparent; border: 1px solid #00eeff;
    color: #00eeff; font-family: 'Share Tech Mono', 'Courier New', monospace;
    font-size: 10px; letter-spacing: 5px; text-transform: uppercase;
    padding: 11px; cursor: pointer; transition: background 0.2s, box-shadow 0.2s;
    box-shadow: 0 0 10px #00eeff22;
}
.auth-btn:hover { background: #00eeff15; box-shadow: 0 0 20px #00eeff44; }
#splash-message {
    font-size: 10px; letter-spacing: 3px; text-transform: uppercase;
    margin-top: 14px; min-height: 18px; text-align: center;
    font-family: 'Share Tech Mono', monospace;
}
.msg-granted { color: #00ff88; text-shadow: 0 0 10px #00ff8888; }
.msg-denied  { color: #ff3333; text-shadow: 0 0 10px #ff333388; }
.msg-waiting { color: #006677; }
.mode-btn-wrap {
    display: flex; gap: 12px; margin-bottom: 0;
}
.mode-btn {
    flex: 1; background: transparent; border: 1px solid #004455;
    color: #006677; font-family: 'Share Tech Mono', 'Courier New', monospace;
    font-size: 10px; letter-spacing: 4px; text-transform: uppercase;
    padding: 11px 8px; cursor: pointer; transition: all 0.2s;
}
.mode-btn:hover { border-color: #00eeff; color: #00eeff; box-shadow: 0 0 16px #00eeff22; }
.mode-btn.selected {
    border-color: #00eeff; color: #00eeff;
    background: #00eeff12; box-shadow: 0 0 16px #00eeff33;
}
.export-btn {
    background: transparent; border: 1px solid #004455; color: #006677;
    font-family: 'Share Tech Mono', monospace; font-size: 9px;
    letter-spacing: 3px; text-transform: uppercase; padding: 6px 12px;
    cursor: pointer; transition: all 0.2s;
}
.export-btn:hover { border-color: #00eeff; color: #00eeff; }
.corner { position: fixed; width: 16px; height: 16px; border-color: #00eeff; border-style: solid; opacity: 0.5; }
.corner.tl { top: 12px; left: 12px; border-width: 1px 0 0 1px; }
.corner.tr { top: 12px; right: 12px; border-width: 1px 1px 0 0; }
.corner.bl { bottom: 12px; left: 12px; border-width: 0 0 1px 1px; }
.corner.br { bottom: 12px; right: 12px; border-width: 0 1px 1px 0; }
.status-row {
    display: flex; justify-content: space-between;
    width: 400px; margin-top: 20px; animation: fadeIn 1s ease 5.2s both;
}
.status-dot {
    font-size: 8px; letter-spacing: 2px; color: #004455;
    text-transform: uppercase; display: flex; align-items: center;
    gap: 6px; font-family: 'Share Tech Mono', monospace;
}
.dot-live {
    width: 6px; height: 6px; border-radius: 50%; background: #00eeff;
    box-shadow: 0 0 8px #00eeff; animation: pulse 2s ease-in-out infinite; flex-shrink: 0;
}
@keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.2; } }
@keyframes fadeIn { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: translateY(0); } }
"""

# ---------------------------------------------------------------------------
# ACS Knowledge Areas
# ---------------------------------------------------------------------------

KNOWLEDGE_AREAS = {
    "weather": {
        "label": "Weather & Meteorology", "weight": 10,
        "description": "Front range convective activity, mountain wave, density altitude, METAR/TAF, wind shear, AIRMETS/SIGMETS, go/no-go decisions at KFNL",
    },
    "systems": {
        "label": "Aircraft Systems — RV-12 / Rotax 912", "weight": 10,
        "description": "Carbureted Rotax 912 specifics: carb ice susceptibility and prevention, dual carb sync, oil temp warmup gate, gearbox oil, fuel system, electrical, what differs from a Lycoming",
    },
    "airspace": {
        "label": "Airspace", "weight": 9,
        "description": "KFNL Class D ops, Denver Class B proximity, Class C/D/E transitions, special use airspace, VFR cruising altitudes, northern Colorado airspace structure",
    },
    "performance": {
        "label": "Performance & Limitations", "weight": 9,
        "description": "Sport Pilot weight limits, 1320 lb MTOW, density altitude effects at KFNL (5016 MSL), RV-12 performance charts, best glide, climb performance on hot afternoons",
    },
    "sport_pilot_regs": {
        "label": "Sport Pilot Privileges & Limitations", "weight": 9,
        "description": "As-a-Sport-Pilot-can-you questions: night flight, Class B, passenger requirements, medical/driver's license, MOSAIC changes, logging requirements, currency",
    },
    "aeromedical": {
        "label": "Aeromedical Factors", "weight": 7,
        "description": "Hypoxia, spatial disorientation, illusions, fatigue, medication, alcohol rules, density altitude physiological effects at Colorado elevations",
    },
    "aerodynamics": {
        "label": "Aerodynamics & Flight Principles", "weight": 7,
        "description": "Lift/drag, stall characteristics, RV-12 stall speed and the 59-knot VS1 criterion, load factors, wake turbulence, ground effect",
    },
    "cross_country": {
        "label": "Cross-Country Planning", "weight": 7,
        "description": "VFR flight planning from KFNL, pilotage, dead reckoning, GPS use, fuel planning, alternates, weight and balance for the RV-12, TFRs",
    },
    "emergency": {
        "label": "Emergency Procedures", "weight": 8,
        "description": "Engine failure in the RV-12/Rotax, best glide, off-airport landing, partial power scenarios, fire, electrical failure, lost comms at KFNL Class D",
    },
    "airport_ops": {
        "label": "Airport & Traffic Pattern Operations", "weight": 6,
        "description": "KFNL traffic pattern, runway 15/33, Class D comms, light signals, runway incursion avoidance, wake turbulence procedures, taxiing at towered airports",
    },
    "navigation": {
        "label": "Navigation & Charts", "weight": 6,
        "description": "Sectional chart reading around northern Colorado, VORs, GPS, lost procedures, airspace depiction, identifying landmarks near KFNL",
    },
    "documents": {
        "label": "Required Documents & Inspections", "weight": 4,
        "description": "ARROW, airworthiness, registration, operating handbook, weight and balance, required inspections, logbook endorsements for Sport Pilot",
    },
}

# ---------------------------------------------------------------------------
# Session log helpers
# ---------------------------------------------------------------------------

def load_session_log() -> dict:
    if os.path.exists(SESSION_LOG_PATH):
        try:
            with open(SESSION_LOG_PATH, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def save_session_log(log: dict):
    os.makedirs(os.path.dirname(SESSION_LOG_PATH), exist_ok=True)
    with open(SESSION_LOG_PATH, "w") as f:
        json.dump(log, f, indent=2)


def pick_topics(n: int = 3) -> list:
    log = load_session_log()
    scores = {}
    for key, info in KNOWLEDGE_AREAS.items():
        score = info["weight"]
        entry = log.get(key, {})
        last_seen = entry.get("last_seen")
        if last_seen:
            days_ago = (date.today() - date.fromisoformat(last_seen)).days
            if days_ago == 0:
                score *= 0.1
            elif days_ago <= 2:
                score *= 0.4
            elif days_ago <= 5:
                score *= 0.7
        confidence = entry.get("confidence", 1.0)
        score *= (2.0 - confidence)
        scores[key] = max(score, 0.1)

    keys = list(scores.keys())
    weights = [scores[k] for k in keys]
    total = sum(weights)
    probs = [w / total for w in weights]

    chosen = []
    rk, rp = keys[:], probs[:]
    for _ in range(min(n, len(rk))):
        r = random.random()
        cum = 0
        for i, p in enumerate(rp):
            cum += p
            if r <= cum:
                chosen.append(rk[i])
                rk.pop(i); rp.pop(i)
                t = sum(rp)
                rp = [x / t for x in rp]
                break
    return chosen


def update_session_log(topic_key: str, hint_count: int, turns: int):
    log = load_session_log()
    entry = log.get(topic_key, {})
    times_seen = entry.get("times_seen", 0) + 1
    raw_confidence = max(0.4, 1.0 - (hint_count * 0.2))
    old_confidence = entry.get("confidence", 1.0)
    new_confidence = (old_confidence * (times_seen - 1) + raw_confidence) / times_seen
    log[topic_key] = {
        "last_seen": date.today().isoformat(),
        "times_seen": times_seen,
        "confidence": round(new_confidence, 3),
        "last_hint_count": hint_count,
    }
    save_session_log(log)


# ---------------------------------------------------------------------------
# System prompt
# ---------------------------------------------------------------------------

def build_system_prompt(topics: list, pilot_name: str = "Pilot") -> str:
    topic_details = "\n".join(
        f"- {KNOWLEDGE_AREAS[t]['label']}: {KNOWLEDGE_AREAS[t]['description']}"
        for t in topics
    )
    return f"""You are Dave, a Designated Pilot Examiner (DPE) conducting a Sport Pilot oral exam at Fort Collins-Loveland Municipal Airport (KFNL) in northern Colorado. You have 30 years of flying experience in the Rocky Mountain region and genuinely love aviation. You want every applicant to pass — you are encouraging, friendly, and collegial. You call the applicant {pilot_name}.

AIRCRAFT: The applicant is flying a carbureted Van's RV-12 with a Rotax 912 ULS engine. All questions should be grounded in this specific aircraft.

AIRPORT & REGION: KFNL sits at 5,016 feet MSL near Fort Collins. The Rocky Mountain front range means density altitude, afternoon convective buildups, mountain wave, chinook winds, and rapid weather changes are all real operational factors. Denver Class B is nearby.

YOUR EXAMINATION STYLE — THE SOCRATIC METHOD:
- Never just ask a question and accept a yes/no or one-line answer. Probe deeper.
- When {pilot_name} gives a correct answer, follow up with a harder edge case or "why does that matter specifically for the Rotax?"
- When {pilot_name} gives a partial answer, ask a targeted follow-up that leads toward the missing piece. Do NOT give the answer — guide them to find it.
- When {pilot_name} is stuck, give a hint. Not the answer, but a nudge: "Think about what happens to air density as temperature rises..."
- Only move to a new topic when you are genuinely satisfied that {pilot_name} understands the concept.
- Occasionally push back even on correct answers to test confidence.
- Use real scenarios: "It's 2pm on a July afternoon, 95°F on the ramp at KFNL. Walk me through your go/no-go thinking..."

SPORT PILOT SPECIFIC — CURRENT RULES (MOSAIC era, 2024+):
You must know and apply the CURRENT regulations, not pre-MOSAIC rules. Key points:

- Under 14 CFR 61.315 and 61.325, Sport Pilots MAY operate in Class B, C, and D airspace with the required training and endorsement. This is current law. Do NOT tell applicants they are prohibited from Class B — they are not, with proper endorsement.
- MOSAIC (Modernization of Special Airspace and Class E Airspace) has expanded Sport Pilot privileges. Know what changed.
- The 59-knot VS1 stall speed criterion remains central to LSA/MOSAIC eligibility for the RV-12.
- Night flight: Sport Pilots still may not fly at night under the basic Sport Pilot certificate, but MOSAIC has introduced pathways — know the distinction.
- Medical: Sport Pilot may exercise privileges with a valid US driver's license in lieu of a medical certificate, with specific conditions.
- If {pilot_name} corrects you on a regulation and cites the CFR, take it seriously — verify your knowledge before pushing back. You should not be confidently wrong about current rules.

Ask "As a Sport Pilot, can you..." questions frequently — these are prime DPE territory and the answers have changed under MOSAIC.

TODAY'S TOPIC AREAS (work through these, spending real time on each):
{topic_details}

SESSION FLOW:
- Start with a warm welcome and a scenario-based opening question from the first topic.
- Spend 4-6 exchanges on each topic area before transitioning naturally.
- Transition by saying something like "Alright, let's shift gears..."
- End the session with a brief honest summary of how {pilot_name} did and any areas to review.

TONE: Friendly, experienced mountain pilot. Never adversarial. Use aviation shorthand naturally (DA, MSL, AGL, METAR, etc.).

Do not break character. Do not explain that you are an AI. You are Dave."""


# ---------------------------------------------------------------------------
# Anthropic API
# ---------------------------------------------------------------------------

def build_oracle_prompt(pilot_name: str = "Pilot") -> str:
    return f"""You are Dave, an experienced pilot and flight instructor with 30 years flying in the Rocky Mountain region, based at Fort Collins-Loveland Municipal Airport (KFNL) in northern Colorado. You know the RV-12 with the carbureted Rotax 912 ULS inside and out, and you love talking aviation.

{pilot_name} is a Sport Pilot working toward their checkride and has come to you with a question or topic they want to explore — something they encountered flying, read about, or are curious about. This is NOT an exam. There's no evaluation, no pressure. Think of it as two pilots sitting in the FBO after a flight, digging into something interesting.

YOUR ROLE:
- Answer {pilot_name}'s questions thoroughly and accurately.
- Tailor explanations to the RV-12/Rotax 912 and KFNL/northern Colorado context whenever relevant.
- Ask a clarifying question early to understand what {pilot_name} already knows, so you can calibrate your explanation — but don't pepper them with questions.
- Go deep if they want to go deep. Follow tangents if they're interesting.
- Share your own experience: "I remember flying into mountain wave over the Divide once..." makes it real.
- If they ask about regs, use CURRENT rules — MOSAIC era, 2024+. Under 14 CFR 61.315 and 61.325, Sport Pilots MAY operate in Class B, C, and D airspace with proper training and endorsement. Do not cite pre-MOSAIC limitations as if they are current.
- If you're not certain about something, say so — a good instructor doesn't bluff.

TONE: Relaxed, collegial, enthusiastic about aviation. You love this stuff and it shows. No exam pressure, no judgment. Just a good conversation between pilots.

Do not break character. Do not explain that you are an AI. You are Dave."""


def get_ai_response(messages: list, system_prompt: str) -> str:
    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        system=system_prompt,
        messages=messages,
    )
    return response.content[0].text


# ---------------------------------------------------------------------------
# Message bubble
# ---------------------------------------------------------------------------

def make_bubble(role: str, text: str, pilot_name: str = "Pilot") -> html.Div:
    is_dave = role == "assistant"
    return html.Div(
        style={"display": "flex", "flexDirection": "column",
               "alignItems": "flex-start" if is_dave else "flex-end"},
        children=[
            html.Div(
                html.Span("Dave" if is_dave else pilot_name,
                          style={"fontSize": "9px", "letterSpacing": "0.08em",
                                 "color": "#58A6FF" if is_dave else "#3FB950"}),
                style={"marginBottom": "4px",
                       "paddingLeft": "4px" if is_dave else "0",
                       "paddingRight": "0" if is_dave else "4px"},
            ),
            html.Div(text, style={
                "backgroundColor": "#161B22" if is_dave else "#1F3A1F",
                "border": f"1px solid {'#30363D' if is_dave else '#2EA043'}",
                "borderRadius": "8px", "padding": "12px 16px",
                "maxWidth": "75%", "fontSize": "13px", "lineHeight": "1.6",
                "whiteSpace": "pre-wrap", "color": "#C9D1D9",
            }),
        ]
    )


# ---------------------------------------------------------------------------
# Sidebar stats
# ---------------------------------------------------------------------------

def build_area_stats() -> list:
    log = load_session_log()
    stats = []
    for key, info in KNOWLEDGE_AREAS.items():
        entry = log.get(key, {})
        last_seen = entry.get("last_seen", "Never")
        confidence = entry.get("confidence", None)
        conf_color = (
            "#3FB950" if confidence and confidence >= 0.8 else
            "#F0883E" if confidence and confidence >= 0.6 else
            "#EF5350" if confidence else "#555"
        )
        conf_label = f"{confidence:.0%}" if confidence else "—"
        stats.append(html.Div([
            html.Span(info["label"], style={"fontSize": "10px", "color": "#C9D1D9",
                                            "display": "block", "marginBottom": "2px"}),
            html.Div([
                html.Span(f"Last: {last_seen}", style={"fontSize": "9px", "color": "#8B949E",
                                                        "marginRight": "8px"}),
                html.Span(conf_label, style={"fontSize": "9px", "color": conf_color,
                                             "fontWeight": "600"}),
            ]),
        ], style={"marginBottom": "10px", "paddingBottom": "8px",
                  "borderBottom": "1px solid #21262D"}))
    return stats


# ---------------------------------------------------------------------------
# Layout — everything in DOM at load time, toggled by display style
# ---------------------------------------------------------------------------

def build_full_layout():
    grid_bg = html.Div(style={
        "position": "absolute", "top": 0, "left": 0, "right": 0, "bottom": 0,
        "backgroundImage": (
            "linear-gradient(rgba(0,238,255,0.07) 1px, transparent 1px),"
            "linear-gradient(90deg, rgba(0,238,255,0.07) 1px, transparent 1px)"
        ),
        "backgroundSize": "50px 50px", "pointerEvents": "none",
    })

    # ── SPLASH ──────────────────────────────────────────────────────────────
    splash = html.Div(id="splash-screen", style=SHOW, children=[
        html.Div(className="corner tl"),
        html.Div(className="corner tr"),
        html.Div(className="corner bl"),
        html.Div(className="corner br"),
        html.Div(className="scan-line"),
        html.Div(className="tron-wrap", children=[
            grid_bg,
            html.Div("KFNL · RV-12 · ROTAX 912", className="tron-logo"),
            html.Div("DPE", className="tron-title"),
            html.Div("Sport Pilot Oral Examiner", className="tron-sub"),
            html.Div(className="loader-wrap", children=[
                html.Div(className="loader-label", children=[
                    html.Span("Initializing knowledge grid"), html.Span(""),
                ]),
                html.Div(className="loader-bar-bg", children=[
                    html.Div(className="loader-bar"),
                ]),
            ]),
            html.Div(className="auth-panel", children=[
                html.Div("// Pilot Identity", className="auth-label"),
                html.Div(className="auth-input-wrap", children=[
                    html.Span(">_", className="auth-prompt"),
                    dcc.Input(
                        id="pilot-name-input", type="text",
                        placeholder="enter your name",
                        debounce=False, autoFocus=True,
                        n_submit=0, maxLength=30,
                        style={"flex": 1},
                    ),
                ]),
                html.Div("// Select Mode", className="auth-label",
                         style={"marginTop": "4px"}),
                html.Div(className="mode-btn-wrap", children=[
                    html.Button("⚡ DPE Exam", id="mode-dpe-btn", n_clicks=0,
                                className="mode-btn selected"),
                    html.Button("◎ Oracle", id="mode-oracle-btn", n_clicks=0,
                                className="mode-btn"),
                ]),
                html.Div(id="mode-hint", children="Dave picks topics · Socratic method · session tracked",
                         style={"fontSize": "9px", "color": "#004455", "letterSpacing": "2px",
                                "textAlign": "center", "margin": "10px 0 14px",
                                "fontFamily": "Share Tech Mono, monospace",
                                "textTransform": "uppercase"}),
                html.Button("Begin →", id="splash-btn",
                            className="auth-btn", n_clicks=0),
                html.Div("", id="splash-message", className="msg-waiting"),
            ]),
            html.Div(className="status-row", children=[
                html.Div(className="status-dot", children=[
                    html.Div(className="dot-live"), html.Span("System online"),
                ]),
                html.Div("Northern Colorado // KFNL", className="status-dot"),
            ]),
        ]),
    ])

    # ── EXAM ────────────────────────────────────────────────────────────────
    exam = html.Div(id="exam-screen", style=HIDE, children=[
        html.Div(style={
            "backgroundColor": "#0D1117", "height": "100vh",
            "fontFamily": "'IBM Plex Mono', monospace", "color": "#C9D1D9",
            "display": "flex", "flexDirection": "column", "overflow": "hidden",
        }, children=[
            # Header
            html.Div(style={
                "backgroundColor": "#161B22", "borderBottom": "1px solid #30363D",
                "padding": "14px 24px", "display": "flex",
                "alignItems": "center", "justifyContent": "space-between",
            }, children=[
                html.Div([
                    html.Span("✈ ", style={"color": "#58A6FF", "fontSize": "18px"}),
                    html.Span(id="header-title",
                              children="DPE SPORT PILOT ORAL EXAMINER",
                              style={"color": "#58A6FF", "fontSize": "15px",
                                     "letterSpacing": "0.15em", "fontWeight": "600"}),
                ]),
                html.Div(style={"display": "flex", "alignItems": "center", "gap": "16px"}, children=[
                    html.Button("⬇ Export Session", id="export-btn", n_clicks=0,
                                className="export-btn"),
                    html.Span("KFNL · RV-12 · ROTAX 912",
                              style={"color": "#8B949E", "fontSize": "10px",
                                     "letterSpacing": "0.1em"}),
                ]),
            ]),
            # Body
            html.Div(style={
                "display": "flex", "flex": "1", "overflow": "hidden",
                "height": "calc(100vh - 53px)", "minHeight": "0",
            }, children=[
                # Sidebar
                html.Div(id="sidebar-panel", style={
                    "width": "220px", "flexShrink": "0",
                    "backgroundColor": "#161B22", "borderRight": "1px solid #30363D",
                    "padding": "16px", "overflowY": "auto",
                }, children=[
                    # DPE sidebar
                    html.Div(id="dpe-sidebar", children=[
                        html.P("KNOWLEDGE AREAS", style={
                            "fontSize": "9px", "color": "#58A6FF", "letterSpacing": "0.12em",
                            "marginBottom": "12px", "borderBottom": "1px solid #21262D",
                            "paddingBottom": "6px",
                        }),
                        html.Div(build_area_stats(), id="area-stats"),
                        html.P("CONFIDENCE", style={
                            "fontSize": "9px", "color": "#8B949E",
                            "letterSpacing": "0.1em", "marginTop": "12px", "marginBottom": "6px",
                        }),
                        *[html.Div([
                            html.Span("● ", style={"color": c, "fontSize": "10px"}),
                            html.Span(label, style={"fontSize": "9px", "color": "#8B949E"}),
                        ]) for c, label in [
                            ("#3FB950", "≥ 80%  Strong"),
                            ("#F0883E", "60–79%  Review"),
                            ("#EF5350", "< 60%  Focus here"),
                        ]],
                    ]),
                    # Oracle sidebar
                    html.Div(id="oracle-sidebar", style={"display": "none"}, children=[
                        html.P("ORACLE MODE", style={
                            "fontSize": "9px", "color": "#00eeff", "letterSpacing": "0.12em",
                            "marginBottom": "12px", "borderBottom": "1px solid #21262D",
                            "paddingBottom": "6px",
                        }),
                        html.P("ASK DAVE ANYTHING", style={
                            "fontSize": "9px", "color": "#8B949E", "letterSpacing": "0.1em",
                            "marginBottom": "16px",
                        }),
                        *[html.Div([
                            html.Span("→ ", style={"color": "#00eeff", "fontSize": "10px"}),
                            html.Span(topic, style={"fontSize": "10px", "color": "#8B949E",
                                                    "lineHeight": "1.6"}),
                        ], style={"marginBottom": "10px"}) for topic in [
                            "Rotax 912 systems & quirks",
                            "Front range weather",
                            "Mountain wave & turbulence",
                            "Airspace & regs (MOSAIC)",
                            "Density altitude at KFNL",
                            "Emergency procedures",
                            "Cross-country planning",
                            "Sport Pilot privileges",
                            "Aerodynamics & stalls",
                            "Anything you flew today",
                        ]],
                        html.Div(style={
                            "marginTop": "20px", "paddingTop": "12px",
                            "borderTop": "1px solid #21262D",
                        }, children=[
                            html.P("SESSION NOT LOGGED", style={
                                "fontSize": "9px", "color": "#004455",
                                "letterSpacing": "0.1em",
                            }),
                            html.P("Use Export Session to save this conversation.",
                                   style={"fontSize": "9px", "color": "#555",
                                          "lineHeight": "1.5"}),
                        ]),
                    ]),
                ]),
                # Chat
                html.Div(style={
                    "flex": "1", "display": "flex",
                    "flexDirection": "column", "overflow": "hidden",
                    "minHeight": "0",
                }, children=[
                    html.Div(id="topic-banner", style={
                        "padding": "8px 20px", "backgroundColor": "#0D1117",
                        "borderBottom": "1px solid #21262D", "fontSize": "10px",
                        "color": "#8B949E", "letterSpacing": "0.08em", "minHeight": "30px",
                    }),
                    html.Div(id="chat-display", style={
                        "flex": "1", "overflowY": "auto", "padding": "20px",
                        "display": "flex", "flexDirection": "column", "gap": "12px",
                    }, children=[
                        html.Div(style={
                            "textAlign": "center", "color": "#8B949E",
                            "fontSize": "12px", "marginTop": "60px",
                        }, children=[
                            html.Div("✈", style={"fontSize": "40px",
                                                  "marginBottom": "16px", "color": "#30363D"}),
                            html.P("Ready when you are."),
                            html.P("Hit Start Session to begin.",
                                   style={"fontSize": "10px", "color": "#555"}),
                        ]),
                    ]),
                    html.Div(style={
                        "padding": "14px 20px", "borderTop": "1px solid #30363D",
                        "backgroundColor": "#161B22", "display": "flex",
                        "gap": "10px", "alignItems": "flex-end",
                    }, children=[
                        dcc.Textarea(
                            id="user-input", placeholder="Your answer...", disabled=True,
                            style={
                                "flex": "1", "backgroundColor": "#0D1117",
                                "color": "#C9D1D9", "border": "1px solid #30363D",
                                "borderRadius": "6px", "padding": "10px 12px",
                                "fontSize": "13px", "fontFamily": "'IBM Plex Mono', monospace",
                                "resize": "none", "minHeight": "60px",
                                "maxHeight": "120px", "outline": "none",
                            }
                        ),
                        html.Div([
                            html.Button("Start Session", id="start-btn", n_clicks=0,
                                        style={
                                            "backgroundColor": "#1F6FEB", "color": "#fff",
                                            "border": "none", "borderRadius": "6px",
                                            "padding": "10px 16px", "cursor": "pointer",
                                            "fontSize": "11px", "fontWeight": "600",
                                            "fontFamily": "'IBM Plex Mono', monospace",
                                            "letterSpacing": "0.05em", "display": "block",
                                            "marginBottom": "6px", "width": "120px",
                                        }),
                            html.Button("Send  ↵", id="send-btn", n_clicks=0, disabled=True,
                                        style={
                                            "backgroundColor": "#238636", "color": "#fff",
                                            "border": "none", "borderRadius": "6px",
                                            "padding": "10px 16px", "cursor": "pointer",
                                            "fontSize": "11px", "fontWeight": "600",
                                            "fontFamily": "'IBM Plex Mono', monospace",
                                            "display": "block", "width": "120px",
                                        }),
                        ]),
                    ]),
                ]),
            ]),
        ]),
    ])

    return html.Div([
        dcc.Store(id="pilot-name-store", data=""),
        dcc.Store(id="mode-store", data="dpe"),
        dcc.Store(id="conversation-store", data=[]),
        dcc.Store(id="session-meta-store", data={
            "active": False, "topics": [], "current_topic_idx": 0,
            "hint_counts": {}, "turn_counts": {},
        }),
        dcc.Download(id="export-download"),
        splash,
        exam,
    ])


# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------

app = Dash(
    __name__,
    title="DPE Sport Pilot Examiner",
    external_stylesheets=[
        dbc.themes.DARKLY,
        "https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&display=swap",
    ],
    suppress_callback_exceptions=True,
)
server = app.server

app.index_string = f"""<!DOCTYPE html>
<html>
<head>
    {{%metas%}}
    <title>DPE Sport Pilot Examiner</title>
    {{%favicon%}}
    {{%css%}}
    <style>{TRON_CSS}</style>
</head>
<body>
    {{%app_entry%}}
    {{%config%}}
    {{%scripts%}}
    {{%renderer%}}
</body>
</html>"""

app.layout = build_full_layout()


# ---------------------------------------------------------------------------
# Callback: mode button toggle
# ---------------------------------------------------------------------------

@app.callback(
    Output("mode-dpe-btn",  "className"),
    Output("mode-oracle-btn", "className"),
    Output("mode-store",    "data"),
    Output("mode-hint",     "children"),
    Input("mode-dpe-btn",   "n_clicks"),
    Input("mode-oracle-btn","n_clicks"),
    prevent_initial_call=True,
)
def toggle_mode(dpe_clicks, oracle_clicks):
    trigger = ctx.triggered_id
    if trigger == "mode-oracle-btn":
        return ("mode-btn", "mode-btn selected", "oracle",
                "You drive · Ask anything · Conversation not tracked")
    return ("mode-btn selected", "mode-btn", "dpe",
            "Dave picks topics · Socratic method · session tracked")


# ---------------------------------------------------------------------------
# Callback: splash → exam
# ---------------------------------------------------------------------------

@app.callback(
    Output("splash-screen",    "style"),
    Output("exam-screen",      "style"),
    Output("pilot-name-store", "data"),
    Output("header-title",     "children"),
    Output("dpe-sidebar",      "style"),
    Output("oracle-sidebar",   "style"),
    Output("splash-message",   "children"),
    Output("splash-message",   "className"),
    Input("splash-btn",        "n_clicks"),
    Input("pilot-name-input",  "n_submit"),
    State("pilot-name-input",  "value"),
    State("mode-store",        "data"),
    prevent_initial_call=True,
)
def handle_splash(n_clicks, n_submit, name, mode):
    if not name or not name.strip():
        return no_update, no_update, no_update, no_update, no_update, no_update, "// enter your name to begin", "msg-denied"
    pilot = name.strip().title()
    if mode == "oracle":
        title = f"ORACLE MODE  //  {pilot.upper()}"
        dpe_style = {"display": "none"}
        oracle_style = {"display": "block"}
    else:
        title = "DPE SPORT PILOT ORAL EXAMINER"
        dpe_style = {"display": "block"}
        oracle_style = {"display": "none"}
    return HIDE, SHOW, pilot, title, dpe_style, oracle_style, no_update, no_update


# ---------------------------------------------------------------------------
# Callback: Export session as .txt
# ---------------------------------------------------------------------------

@app.callback(
    Output("export-download",    "data"),
    Input("export-btn",          "n_clicks"),
    State("conversation-store",  "data"),
    State("pilot-name-store",    "data"),
    State("oracle-sidebar",      "style"),
    prevent_initial_call=True,
)
def export_session(n_clicks, conversation, pilot_name, oracle_style):
    if not conversation:
        return no_update
    pilot = pilot_name or "Pilot"
    is_oracle = oracle_style and oracle_style.get("display") == "block"
    mode_label = "Oracle Mode" if is_oracle else "DPE Exam Mode"
    mode_slug = "oracle" if is_oracle else "dpe"
    lines = [
        f"DPE Sport Pilot Oral Examiner — {mode_label}",
        f"Pilot: {pilot}",
        f"Date: {date.today().isoformat()}",
        "=" * 60,
        "",
    ]
    for msg in conversation:
        speaker = "Dave" if msg["role"] == "assistant" else pilot
        lines.append(f"[{speaker}]")
        lines.append(msg["content"])
        lines.append("")
    content = "\n".join(lines)
    filename = f"dpe_session_{date.today().isoformat()}_{mode_slug}.txt"
    return dcc.send_string(content, filename)


# ---------------------------------------------------------------------------
# Callback: Start Session / Send
# ---------------------------------------------------------------------------

@app.callback(
    Output("conversation-store", "data"),
    Output("session-meta-store", "data"),
    Output("chat-display",       "children"),
    Output("topic-banner",       "children"),
    Output("user-input",         "disabled"),
    Output("send-btn",           "disabled"),
    Output("start-btn",          "children"),
    Output("user-input",         "value"),
    Output("user-input",         "placeholder"),
    Input("start-btn",           "n_clicks"),
    Input("send-btn",            "n_clicks"),
    State("user-input",          "value"),
    State("conversation-store",  "data"),
    State("session-meta-store",  "data"),
    State("pilot-name-store",    "data"),
    State("mode-store",          "data"),
    State("oracle-sidebar",      "style"),
    prevent_initial_call=True,
)
def handle_interaction(start_clicks, send_clicks, user_text,
                       conversation, meta, pilot_name, mode, oracle_style):

    pilot_name = pilot_name or "Pilot"
    trigger = ctx.triggered_id
    # Use sidebar visibility as ground truth for mode — avoids store race condition
    is_oracle = oracle_style and oracle_style.get("display") == "block"

    if trigger == "start-btn":
        if is_oracle:
            system_prompt = build_oracle_prompt(pilot_name)
            meta = {
                "active": True, "topics": [], "system_prompt": system_prompt,
                "current_topic_idx": 0, "hint_counts": {}, "turn_counts": {},
            }
            opening = get_ai_response(
                [{"role": "user", "content": "Hi Dave, I have something I want to dig into."}],
                system_prompt
            )
            conversation = [{"role": "assistant", "content": opening}]
            bubbles = [make_bubble("assistant", opening, pilot_name)]
            banner = "ORACLE MODE — ask anything · KFNL · RV-12 · Rotax 912 · northern Colorado"
            placeholder = "Ask Dave anything..."
        else:
            topics = pick_topics(3)
            system_prompt = build_system_prompt(topics, pilot_name)
            meta = {
                "active": True, "topics": topics, "system_prompt": system_prompt,
                "current_topic_idx": 0,
                "hint_counts": {t: 0 for t in topics},
                "turn_counts": {t: 0 for t in topics},
            }
            opening = get_ai_response(
                [{"role": "user", "content": "Hello, I'm ready to begin my oral exam."}],
                system_prompt
            )
            conversation = [{"role": "assistant", "content": opening}]
            bubbles = [make_bubble("assistant", opening, pilot_name)]
            banner = "TODAY'S TOPICS: " + " → ".join(
                KNOWLEDGE_AREAS[t]["label"] for t in topics
            )
            placeholder = "Your answer..."
        return conversation, meta, bubbles, banner, False, False, "New Session", "", placeholder

    if trigger == "send-btn" and user_text and user_text.strip():
        if not meta.get("active"):
            return (no_update,) * 9
        user_text = user_text.strip()
        conversation = conversation + [{"role": "user", "content": user_text}]
        system_prompt = meta.get("system_prompt", "")
        response = get_ai_response(conversation, system_prompt)
        conversation = conversation + [{"role": "assistant", "content": response}]

        if not is_oracle:
            hint_keywords = ["think about", "remember", "hint", "consider",
                             "what about", "clue", "nudge"]
            topics = meta.get("topics", [])
            current_idx = meta.get("current_topic_idx", 0)
            if current_idx < len(topics):
                current_topic = topics[current_idx]
                lower_resp = response.lower()
                if any(kw in lower_resp for kw in hint_keywords):
                    meta["hint_counts"][current_topic] = \
                        meta["hint_counts"].get(current_topic, 0) + 1
                meta["turn_counts"][current_topic] = \
                    meta["turn_counts"].get(current_topic, 0) + 1
                transition_phrases = ["let's shift", "shift gears", "moving on",
                                       "next area", "next topic", "let's talk about"]
                if any(ph in lower_resp for ph in transition_phrases):
                    update_session_log(
                        current_topic,
                        meta["hint_counts"].get(current_topic, 0),
                        meta["turn_counts"].get(current_topic, 0),
                    )
                    meta["current_topic_idx"] = current_idx + 1

        bubbles = [make_bubble(m["role"], m["content"], pilot_name) for m in conversation]
        return conversation, meta, bubbles, no_update, False, False, no_update, "", no_update

    return (no_update,) * 9


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import threading, webbrowser
    def open_browser():
        webbrowser.open(f"http://localhost:{PORT}")
    threading.Timer(1.5, open_browser).start()
    app.run(debug=False, port=PORT)