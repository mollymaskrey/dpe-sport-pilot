"""
main.py

DPE Sport Pilot Oral Examiner
Socratic oral exam simulator grounded in KFNL, RV-12/Rotax 912, northern Colorado.
Deploys to Render with persistent disk at /var/data for session logging.
"""

import os
import json
import random
from datetime import datetime, date

import anthropic
from dash import Dash, dcc, html, Input, Output, State, ctx, no_update
import dash_bootstrap_components as dbc

# ---------------------------------------------------------------------------
# TRON splash CSS
# ---------------------------------------------------------------------------

TRON_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&display=swap');

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
    position: fixed;
    top: 0; left: 0;
    width: 100%; height: 2px;
    background: linear-gradient(90deg, transparent, #00eeff, transparent);
    animation: scan 4s linear infinite;
    opacity: 0.4;
    pointer-events: none;
    z-index: 10;
}
@keyframes scan {
    0%   { top: 0%; }
    100% { top: 100%; }
}

.tron-logo {
    font-size: 11px;
    letter-spacing: 6px;
    color: #555;
    text-transform: uppercase;
    margin-bottom: 8px;
    animation: fadeIn 1s ease 0.5s both;
}
.tron-title {
    font-size: 52px;
    font-weight: bold;
    letter-spacing: 14px;
    color: #00eeff;
    text-transform: uppercase;
    text-shadow: 0 0 20px #00eeff, 0 0 60px #00eeff88, 0 0 100px #00eeff44;
    margin-bottom: 4px;
    animation: fadeIn 1s ease 0.8s both;
    font-family: 'Share Tech Mono', monospace;
}
.tron-sub {
    font-size: 10px;
    letter-spacing: 6px;
    color: #006677;
    text-transform: uppercase;
    margin-bottom: 48px;
    animation: fadeIn 1s ease 1.1s both;
}

.loader-wrap {
    width: 380px;
    margin-bottom: 40px;
    animation: fadeIn 1s ease 1.4s both;
}
.loader-label {
    font-size: 9px;
    letter-spacing: 4px;
    color: #006677;
    text-transform: uppercase;
    margin-bottom: 8px;
    display: flex;
    justify-content: space-between;
}
.loader-bar-bg {
    width: 100%;
    height: 3px;
    background: #001a1f;
    border: 1px solid #003344;
    position: relative;
    overflow: hidden;
}
.loader-bar {
    height: 100%;
    width: 0%;
    background: #00eeff;
    box-shadow: 0 0 10px #00eeff, 0 0 20px #00eeff88;
    animation: load 3s ease 1.8s forwards;
}
@keyframes load {
    0%   { width: 0%; }
    20%  { width: 15%; }
    45%  { width: 42%; }
    70%  { width: 71%; }
    88%  { width: 88%; }
    100% { width: 100%; }
}

.auth-panel {
    width: 400px;
    border: 1px solid #004455;
    background: #000d10;
    padding: 28px 32px;
    animation: fadeIn 1.2s ease 4.8s both;
    position: relative;
}
.auth-panel::before {
    content: '';
    position: absolute;
    top: -1px; left: 24px; right: 24px; height: 1px;
    background: #00eeff;
    box-shadow: 0 0 10px #00eeff;
}
.auth-label {
    font-size: 9px;
    letter-spacing: 4px;
    color: #006677;
    text-transform: uppercase;
    margin-bottom: 14px;
    font-family: 'Share Tech Mono', monospace;
}
.auth-input-wrap {
    display: flex;
    align-items: center;
    border: 1px solid #004455;
    background: #000a0d;
    padding: 10px 14px;
    margin-bottom: 16px;
    transition: border-color 0.3s;
}
.auth-input-wrap:focus-within {
    border-color: #00eeff;
    box-shadow: 0 0 12px #00eeff22;
}
.auth-prompt {
    color: #00eeff;
    font-size: 14px;
    margin-right: 10px;
    opacity: 0.7;
    user-select: none;
    font-family: 'Share Tech Mono', monospace;
}
#pilot-name-input {
    background: transparent !important;
    border: none !important;
    outline: none !important;
    color: #00eeff !important;
    font-family: 'Share Tech Mono', 'Courier New', monospace !important;
    font-size: 14px !important;
    letter-spacing: 3px !important;
    flex: 1;
    caret-color: #00eeff;
    box-shadow: none !important;
    width: 100%;
}
#pilot-name-input::placeholder {
    color: #003344;
    letter-spacing: 2px;
}
.auth-btn {
    width: 100%;
    background: transparent;
    border: 1px solid #00eeff;
    color: #00eeff;
    font-family: 'Share Tech Mono', 'Courier New', monospace;
    font-size: 10px;
    letter-spacing: 5px;
    text-transform: uppercase;
    padding: 11px;
    cursor: pointer;
    transition: background 0.2s, box-shadow 0.2s;
    box-shadow: 0 0 10px #00eeff22;
}
.auth-btn:hover {
    background: #00eeff15;
    box-shadow: 0 0 20px #00eeff44;
}
#splash-message {
    font-size: 10px;
    letter-spacing: 3px;
    text-transform: uppercase;
    margin-top: 14px;
    min-height: 18px;
    text-align: center;
    font-family: 'Share Tech Mono', monospace;
}
.msg-granted { color: #00ff88; text-shadow: 0 0 10px #00ff8888; }
.msg-denied  { color: #ff3333; text-shadow: 0 0 10px #ff333388; }
.msg-waiting { color: #006677; }

.corner {
    position: fixed;
    width: 16px; height: 16px;
    border-color: #00eeff;
    border-style: solid;
    opacity: 0.5;
}
.corner.tl { top: 12px; left: 12px; border-width: 1px 0 0 1px; }
.corner.tr { top: 12px; right: 12px; border-width: 1px 1px 0 0; }
.corner.bl { bottom: 12px; left: 12px; border-width: 0 0 1px 1px; }
.corner.br { bottom: 12px; right: 12px; border-width: 0 1px 1px 0; }

.hex-badge {
    position: fixed;
    top: 18px; right: 24px;
    font-size: 8px;
    letter-spacing: 2px;
    color: #003344;
    text-transform: uppercase;
    font-family: 'Share Tech Mono', monospace;
}
.status-row {
    display: flex;
    justify-content: space-between;
    width: 400px;
    margin-top: 20px;
    animation: fadeIn 1s ease 5.2s both;
}
.status-dot {
    font-size: 8px;
    letter-spacing: 2px;
    color: #004455;
    text-transform: uppercase;
    display: flex;
    align-items: center;
    gap: 6px;
    font-family: 'Share Tech Mono', monospace;
}
.dot-live {
    width: 6px; height: 6px;
    border-radius: 50%;
    background: #00eeff;
    box-shadow: 0 0 8px #00eeff;
    animation: pulse 2s ease-in-out infinite;
    flex-shrink: 0;
}
@keyframes pulse {
    0%, 100% { opacity: 1; }
    50%       { opacity: 0.2; }
}
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(8px); }
    to   { opacity: 1; transform: translateY(0); }
}
"""

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

SESSION_LOG_PATH = "/var/data/session_log.json"
PORT = int(os.environ.get("PORT", 8050))

# ---------------------------------------------------------------------------
# ACS Knowledge Areas with base weights (higher = more likely to be picked)
# Areas you said feel shakier get higher base weight
# ---------------------------------------------------------------------------

KNOWLEDGE_AREAS = {
    "weather": {
        "label": "Weather & Meteorology",
        "weight": 10,
        "description": "Front range convective activity, mountain wave, density altitude, METAR/TAF, wind shear, AIRMETS/SIGMETS, go/no-go decisions at KFNL"
    },
    "systems": {
        "label": "Aircraft Systems — RV-12 / Rotax 912",
        "weight": 10,
        "description": "Carbureted Rotax 912 specifics: carb ice susceptibility and prevention, dual carb sync, oil temp warmup gate, gearbox oil, fuel system, electrical, what differs from a Lycoming"
    },
    "airspace": {
        "label": "Airspace",
        "weight": 9,
        "description": "KFNL Class D ops, Denver Class B proximity, Class C/D/E transitions, special use airspace, VFR cruising altitudes, northern Colorado airspace structure"
    },
    "performance": {
        "label": "Performance & Limitations",
        "weight": 9,
        "description": "Sport Pilot weight limits, 1320 lb MTOW, density altitude effects at KFNL (5016 MSL), RV-12 performance charts, best glide, climb performance on hot afternoons"
    },
    "sport_pilot_regs": {
        "label": "Sport Pilot Privileges & Limitations",
        "weight": 9,
        "description": "As-a-Sport-Pilot-can-you questions: night flight, Class B, passenger requirements, medical/driver's license, MOSAIC changes, logging requirements, currency"
    },
    "aeromedical": {
        "label": "Aeromedical Factors",
        "weight": 7,
        "description": "Hypoxia, spatial disorientation, illusions, fatigue, medication, alcohol rules, density altitude physiological effects at Colorado elevations"
    },
    "aerodynamics": {
        "label": "Aerodynamics & Flight Principles",
        "weight": 7,
        "description": "Lift/drag, stall characteristics, RV-12 stall speed and the 59-knot VS1 criterion, load factors, wake turbulence, ground effect"
    },
    "cross_country": {
        "label": "Cross-Country Planning",
        "weight": 7,
        "description": "VFR flight planning from KFNL, pilotage, dead reckoning, GPS use, fuel planning, alternates, weight and balance for the RV-12, TFRs"
    },
    "emergency": {
        "label": "Emergency Procedures",
        "weight": 8,
        "description": "Engine failure in the RV-12/Rotax, best glide, off-airport landing, partial power scenarios, fire, electrical failure, lost comms at KFNL Class D"
    },
    "airport_ops": {
        "label": "Airport & Traffic Pattern Operations",
        "weight": 6,
        "description": "KFNL traffic pattern, runway 15/33, Class D comms, light signals, runway incursion avoidance, wake turbulence procedures, taxiing at towered airports"
    },
    "navigation": {
        "label": "Navigation & Charts",
        "weight": 6,
        "description": "Sectional chart reading around northern Colorado, VORs, GPS, lost procedures, airspace depiction, identifying landmarks near KFNL"
    },
    "documents": {
        "label": "Required Documents & Inspections",
        "weight": 4,
        "description": "ARROW, airworthiness, registration, operating handbook, weight and balance, required inspections, logbook endorsements for Sport Pilot"
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
    """
    Pick n topics weighted by base weight, recency penalty, and struggle bonus.
    Areas not seen recently and historically difficult get higher priority.
    """
    log = load_session_log()
    today = date.today().isoformat()
    scores = {}

    for key, info in KNOWLEDGE_AREAS.items():
        score = info["weight"]
        entry = log.get(key, {})

        # Recency penalty: reduce score if covered recently
        last_seen = entry.get("last_seen")
        if last_seen:
            days_ago = (date.today() - date.fromisoformat(last_seen)).days
            if days_ago == 0:
                score *= 0.1   # covered today, strongly deprioritize
            elif days_ago <= 2:
                score *= 0.4
            elif days_ago <= 5:
                score *= 0.7

        # Struggle bonus: areas with lower confidence get boosted
        confidence = entry.get("confidence", 1.0)
        score *= (2.0 - confidence)  # confidence 0.5 -> 1.5x, confidence 1.0 -> 1.0x

        scores[key] = max(score, 0.1)

    keys = list(scores.keys())
    weights = [scores[k] for k in keys]
    total = sum(weights)
    probs = [w / total for w in weights]

    chosen = []
    remaining_keys = keys[:]
    remaining_probs = probs[:]
    for _ in range(min(n, len(remaining_keys))):
        r = random.random()
        cumulative = 0
        for i, p in enumerate(remaining_probs):
            cumulative += p
            if r <= cumulative:
                chosen.append(remaining_keys[i])
                remaining_keys.pop(i)
                remaining_probs.pop(i)
                total_p = sum(remaining_probs)
                remaining_probs = [p / total_p for p in remaining_probs]
                break

    return chosen


def update_session_log(topic_key: str, hint_count: int, turns: int):
    """Update the session log after a topic is completed."""
    log = load_session_log()
    entry = log.get(topic_key, {})
    times_seen = entry.get("times_seen", 0) + 1

    # Rough confidence: fewer hints and fewer turns = higher confidence
    # hint_count 0 -> 1.0, hint_count 3+ -> 0.4
    raw_confidence = max(0.4, 1.0 - (hint_count * 0.2))
    # Smooth with history
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
# System prompt builder
# ---------------------------------------------------------------------------

def build_system_prompt(topics: list, pilot_name: str = "Molly") -> str:
    topic_details = "\n".join(
        f"- {KNOWLEDGE_AREAS[t]['label']}: {KNOWLEDGE_AREAS[t]['description']}"
        for t in topics
    )

    return f"""You are Dave, a Designated Pilot Examiner (DPE) conducting a Sport Pilot oral exam at Fort Collins-Loveland Municipal Airport (KFNL) in northern Colorado. You have 30 years of flying experience in the Rocky Mountain region and genuinely love aviation. You want every applicant to pass — you are encouraging, friendly, and collegial. You call the applicant {pilot_name}.

AIRCRAFT: The applicant is flying a carbureted Van's RV-12 with a Rotax 912 ULS engine. All questions should be grounded in this specific aircraft.

AIRPORT & REGION: KFNL sits at 5,016 feet MSL near Fort Collins. The Rocky Mountain front range means density altitude, afternoon convective buildups, mountain wave, chinook winds, and rapid weather changes are all real operational factors. Denver Class B is nearby, as is complex airspace.

YOUR EXAMINATION STYLE — THE SOCRATIC METHOD:
- Never just ask a question and accept a yes/no or one-line answer. Probe deeper.
- When Molly gives a correct answer, follow up: "Good — now what if the wind shifted to 270 at 15?" or "Why does that matter specifically for the Rotax?"
- When Molly gives a partial answer, ask a targeted follow-up that leads her toward the missing piece. Do NOT give the answer — guide her to find it.
- When Molly is stuck, give a hint. Not the answer, but a nudge: "Think about what happens to air density as temperature rises..." or "Remember what makes the Rotax carb system different from a Lycoming?"
- Only move to a new topic when you are genuinely satisfied that Molly understands the concept, not just recited the correct answer.
- Occasionally push back even on correct answers to test confidence: "Are you sure about that? What regulation covers that specifically?"
- Use real scenarios: "It's 2pm on a July afternoon, 95°F on the ramp at KFNL. Walk me through your go/no-go thinking..."

SPORT PILOT SPECIFIC:
- Ask "As a Sport Pilot, can you..." questions frequently. These are prime DPE territory.
- Know the MOSAIC rule changes and probe whether {pilot_name} understands what has changed vs. old rules.
- The 59-knot VS1 stall speed criterion is central to Sport Pilot / MOSAIC eligibility.

TODAY'S TOPIC AREAS (work through these, spending real time on each):
{topic_details}

SESSION FLOW:
- Start with a warm welcome and a scenario-based opening question from the first topic.
- Spend 4-6 exchanges on each topic area before transitioning naturally.
- Transition by saying something like "Alright, let's shift gears..." 
- End the session when all topics are covered with a brief, honest summary of how {pilot_name} did and any areas to review.

TONE: Friendly, experienced mountain pilot. Never adversarial. Think of it as a conversation between two pilots, one of whom happens to be evaluating the other. Use aviation shorthand naturally (DA, MSL, AGL, METAR, etc.) — {pilot_name} knows the language.

Do not break character. Do not explain that you are an AI. You are Dave."""


# ---------------------------------------------------------------------------
# Anthropic client
# ---------------------------------------------------------------------------

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
# Splash screen layout
# ---------------------------------------------------------------------------

def build_splash():
    grid_bg = html.Div(style={
        "position": "absolute",
        "top": 0, "left": 0, "right": 0, "bottom": 0,
        "backgroundImage": (
            "linear-gradient(rgba(0,238,255,0.07) 1px, transparent 1px),"
            "linear-gradient(90deg, rgba(0,238,255,0.07) 1px, transparent 1px)"
        ),
        "backgroundSize": "50px 50px",
        "pointerEvents": "none",
    })

    return html.Div([
        html.Div(className="corner tl"),
        html.Div(className="corner tr"),
        html.Div(className="corner bl"),
        html.Div(className="corner br"),
        html.Div(className="scan-line"),
        html.Div("SYS:DPE.AX // v1.0.0", className="hex-badge"),

        html.Div(className="tron-wrap", children=[
            grid_bg,
            html.Div("KFNL · RV-12 · ROTAX 912", className="tron-logo"),
            html.Div("DPE", className="tron-title"),
            html.Div("Sport Pilot Oral Examiner", className="tron-sub"),

            html.Div(className="loader-wrap", children=[
                html.Div(className="loader-label", children=[
                    html.Span("Initializing knowledge grid"),
                    html.Span(""),
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
                        id="pilot-name-input",
                        type="text",
                        placeholder="enter your name",
                        debounce=False,
                        autoFocus=True,
                        n_submit=0,
                        maxLength=30,
                        style={"flex": 1},
                    ),
                ]),
                html.Button(
                    "Begin Oral Exam →",
                    id="splash-btn",
                    className="auth-btn",
                    n_clicks=0,
                ),
                html.Div("", id="splash-message", className="msg-waiting"),
            ]),

            html.Div(className="status-row", children=[
                html.Div(className="status-dot", children=[
                    html.Div(className="dot-live"),
                    html.Span("System online"),
                ]),
                html.Div("Northern Colorado // KFNL", className="status-dot"),
            ]),
        ]),
    ], style={"minHeight": "100vh", "background": "#000", "position": "relative"})


# ---------------------------------------------------------------------------
# Main exam layout
# ---------------------------------------------------------------------------

def build_layout():
    log = load_session_log()

    # Build stats for sidebar
    area_stats = []
    for key, info in KNOWLEDGE_AREAS.items():
        entry = log.get(key, {})
        last_seen = entry.get("last_seen", "Never")
        confidence = entry.get("confidence", None)
        conf_color = "#3FB950" if confidence and confidence >= 0.8 else \
                     "#F0883E" if confidence and confidence >= 0.6 else \
                     "#EF5350" if confidence else "#555"
        conf_label = f"{confidence:.0%}" if confidence else "—"
        area_stats.append(
            html.Div([
                html.Span(info["label"],
                          style={"fontSize": "10px", "color": "#C9D1D9",
                                 "display": "block", "marginBottom": "2px"}),
                html.Div([
                    html.Span(f"Last: {last_seen}",
                              style={"fontSize": "9px", "color": "#8B949E",
                                     "marginRight": "8px"}),
                    html.Span(conf_label,
                              style={"fontSize": "9px", "color": conf_color,
                                     "fontWeight": "600"}),
                ]),
            ], style={"marginBottom": "10px", "paddingBottom": "8px",
                      "borderBottom": "1px solid #21262D"})
        )

    return html.Div(
        style={
            "backgroundColor": "#0D1117",
            "minHeight": "100vh",
            "fontFamily": "'IBM Plex Mono', monospace",
            "color": "#C9D1D9",
            "display": "flex",
            "flexDirection": "column",
        },
        children=[
            # Header
            html.Div(
                style={
                    "backgroundColor": "#161B22",
                    "borderBottom": "1px solid #30363D",
                    "padding": "14px 24px",
                    "display": "flex",
                    "alignItems": "center",
                    "justifyContent": "space-between",
                },
                children=[
                    html.Div([
                        html.Span("✈ ", style={"color": "#58A6FF", "fontSize": "18px"}),
                        html.Span("DPE SPORT PILOT ORAL EXAMINER",
                                  style={"color": "#58A6FF", "fontSize": "15px",
                                         "letterSpacing": "0.15em", "fontWeight": "600"}),
                    ]),
                    html.Div([
                        html.Span("KFNL · RV-12 · ROTAX 912",
                                  style={"color": "#8B949E", "fontSize": "10px",
                                         "letterSpacing": "0.1em"}),
                    ]),
                ]
            ),

            # Body
            html.Div(
                style={"display": "flex", "flex": "1", "overflow": "hidden"},
                children=[

                    # Sidebar
                    html.Div(
                        style={
                            "width": "220px",
                            "flexShrink": "0",
                            "backgroundColor": "#161B22",
                            "borderRight": "1px solid #30363D",
                            "padding": "16px",
                            "overflowY": "auto",
                        },
                        children=[
                            html.P("KNOWLEDGE AREAS",
                                   style={"fontSize": "9px", "color": "#58A6FF",
                                          "letterSpacing": "0.12em",
                                          "marginBottom": "12px",
                                          "borderBottom": "1px solid #21262D",
                                          "paddingBottom": "6px"}),
                            html.Div(area_stats, id="area-stats"),
                            html.P("CONFIDENCE",
                                   style={"fontSize": "9px", "color": "#8B949E",
                                          "letterSpacing": "0.1em",
                                          "marginTop": "12px", "marginBottom": "6px"}),
                            html.Div([
                                html.Span("● ", style={"color": "#3FB950", "fontSize": "10px"}),
                                html.Span("≥ 80%  Strong",
                                          style={"fontSize": "9px", "color": "#8B949E"}),
                            ]),
                            html.Div([
                                html.Span("● ", style={"color": "#F0883E", "fontSize": "10px"}),
                                html.Span("60–79%  Review",
                                          style={"fontSize": "9px", "color": "#8B949E"}),
                            ]),
                            html.Div([
                                html.Span("● ", style={"color": "#EF5350", "fontSize": "10px"}),
                                html.Span("< 60%  Focus here",
                                          style={"fontSize": "9px", "color": "#8B949E"}),
                            ]),
                        ]
                    ),

                    # Main chat area
                    html.Div(
                        style={"flex": "1", "display": "flex",
                               "flexDirection": "column", "overflow": "hidden"},
                        children=[

                            # Topic banner (populated on session start)
                            html.Div(id="topic-banner",
                                     style={"padding": "8px 20px",
                                            "backgroundColor": "#0D1117",
                                            "borderBottom": "1px solid #21262D",
                                            "fontSize": "10px", "color": "#8B949E",
                                            "letterSpacing": "0.08em",
                                            "minHeight": "30px"}),

                            # Chat messages
                            html.Div(
                                id="chat-display",
                                style={
                                    "flex": "1",
                                    "overflowY": "auto",
                                    "padding": "20px",
                                    "display": "flex",
                                    "flexDirection": "column",
                                    "gap": "12px",
                                },
                                children=[
                                    html.Div(
                                        style={
                                            "textAlign": "center",
                                            "color": "#8B949E",
                                            "fontSize": "12px",
                                            "marginTop": "60px",
                                        },
                                        children=[
                                            html.Div("✈", style={"fontSize": "40px",
                                                                   "marginBottom": "16px",
                                                                   "color": "#30363D"}),
                                            html.P("Ready when you are.",
                                                   style={"marginBottom": "8px"}),
                                            html.P("Hit Start Session to begin your oral exam.",
                                                   style={"fontSize": "10px",
                                                          "color": "#555"}),
                                        ]
                                    )
                                ]
                            ),

                            # Input area
                            html.Div(
                                style={
                                    "padding": "14px 20px",
                                    "borderTop": "1px solid #30363D",
                                    "backgroundColor": "#161B22",
                                    "display": "flex",
                                    "gap": "10px",
                                    "alignItems": "flex-end",
                                },
                                children=[
                                    dcc.Textarea(
                                        id="user-input",
                                        placeholder="Your answer...",
                                        disabled=True,
                                        style={
                                            "flex": "1",
                                            "backgroundColor": "#0D1117",
                                            "color": "#C9D1D9",
                                            "border": "1px solid #30363D",
                                            "borderRadius": "6px",
                                            "padding": "10px 12px",
                                            "fontSize": "13px",
                                            "fontFamily": "'IBM Plex Mono', monospace",
                                            "resize": "none",
                                            "minHeight": "60px",
                                            "maxHeight": "120px",
                                            "outline": "none",
                                        }
                                    ),
                                    html.Div([
                                        html.Button(
                                            "Start Session",
                                            id="start-btn",
                                            n_clicks=0,
                                            style={
                                                "backgroundColor": "#1F6FEB",
                                                "color": "#fff",
                                                "border": "none",
                                                "borderRadius": "6px",
                                                "padding": "10px 16px",
                                                "cursor": "pointer",
                                                "fontSize": "11px",
                                                "fontFamily": "'IBM Plex Mono', monospace",
                                                "fontWeight": "600",
                                                "letterSpacing": "0.05em",
                                                "display": "block",
                                                "marginBottom": "6px",
                                                "width": "120px",
                                            }
                                        ),
                                        html.Button(
                                            "Send  ↵",
                                            id="send-btn",
                                            n_clicks=0,
                                            disabled=True,
                                            style={
                                                "backgroundColor": "#238636",
                                                "color": "#fff",
                                                "border": "none",
                                                "borderRadius": "6px",
                                                "padding": "10px 16px",
                                                "cursor": "pointer",
                                                "fontSize": "11px",
                                                "fontFamily": "'IBM Plex Mono', monospace",
                                                "fontWeight": "600",
                                                "display": "block",
                                                "width": "120px",
                                            }
                                        ),
                                    ]),
                                ]
                            ),
                        ]
                    ),
                ]
            ),

            # Hidden state stores
        ]
    )


# ---------------------------------------------------------------------------
# Message bubble builder
# ---------------------------------------------------------------------------

def make_bubble(role: str, text: str, pilot_name: str = "Pilot") -> html.Div:
    is_dave = role == "assistant"
    return html.Div(
        style={
            "display": "flex",
            "flexDirection": "column",
            "alignItems": "flex-start" if is_dave else "flex-end",
        },
        children=[
            html.Div(
                html.Span("Dave" if is_dave else pilot_name,
                          style={"fontSize": "9px",
                                 "color": "#58A6FF" if is_dave else "#3FB950",
                                 "letterSpacing": "0.08em"}),
                style={"marginBottom": "4px",
                       "paddingLeft": "4px" if is_dave else "0",
                       "paddingRight": "0" if is_dave else "4px"}
            ),
            html.Div(
                text,
                style={
                    "backgroundColor": "#161B22" if is_dave else "#1F3A1F",
                    "border": f"1px solid {'#30363D' if is_dave else '#2EA043'}",
                    "borderRadius": "8px",
                    "padding": "12px 16px",
                    "maxWidth": "75%",
                    "fontSize": "13px",
                    "lineHeight": "1.6",
                    "whiteSpace": "pre-wrap",
                    "color": "#C9D1D9",
                }
            ),
        ]
    )


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

app.index_string = f"""
<!DOCTYPE html>
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
</html>
"""

app.layout = html.Div([
    # All stores live here permanently — never inside swapped content
    dcc.Store(id="pilot-name-store", data=""),
    dcc.Store(id="conversation-store", data=[]),
    dcc.Store(id="session-meta-store", data={
        "active": False,
        "topics": [],
        "current_topic_idx": 0,
        "hint_counts": {},
        "turn_counts": {},
    }),
    dcc.Store(id="thinking-store", data=False),
    dcc.Location(id="url"),
    html.Div(id="page-content", children=build_splash()),
])


# ---------------------------------------------------------------------------
# Callbacks
# ---------------------------------------------------------------------------

@app.callback(
    Output("page-content",      "children"),
    Output("pilot-name-store",  "data"),
    Output("splash-message",    "children"),
    Output("splash-message",    "className"),
    Input("splash-btn",         "n_clicks"),
    Input("pilot-name-input",   "n_submit"),
    State("pilot-name-input",   "value"),
    prevent_initial_call=True,
)
def handle_splash(n_clicks, n_submit, name):
    if not name or not name.strip():
        return no_update, no_update, "// enter your name to begin", "msg-denied"
    pilot = name.strip().title()
    return build_layout(), pilot, no_update, no_update


@app.callback(
    Output("conversation-store",  "data"),
    Output("session-meta-store",  "data"),
    Output("chat-display",        "children"),
    Output("topic-banner",        "children"),
    Output("user-input",          "disabled"),
    Output("send-btn",            "disabled"),
    Output("start-btn",           "children"),
    Output("user-input",          "value"),
    Input("start-btn",            "n_clicks"),
    Input("send-btn",             "n_clicks"),
    State("user-input",           "value"),
    State("conversation-store",   "data"),
    State("session-meta-store",   "data"),
    State("chat-display",         "children"),
    State("pilot-name-store",     "data"),
    prevent_initial_call=True,
)
def handle_interaction(start_clicks, send_clicks, user_text,
                        conversation, meta, current_bubbles, pilot_name):

    pilot_name = pilot_name or "Pilot"
    trigger = ctx.triggered_id

    # ── START SESSION ──────────────────────────────────────────────────────
    if trigger == "start-btn":
        topics = pick_topics(3)
        system_prompt = build_system_prompt(topics, pilot_name)
        meta = {
            "active": True,
            "topics": topics,
            "system_prompt": system_prompt,
            "current_topic_idx": 0,
            "hint_counts": {t: 0 for t in topics},
            "turn_counts": {t: 0 for t in topics},
        }

        # Kick off with Dave's opening
        opening = get_ai_response([], system_prompt)
        conversation = [{"role": "assistant", "content": opening}]

        bubbles = [make_bubble("assistant", opening, pilot_name)]
        topic_labels = " → ".join(
            KNOWLEDGE_AREAS[t]["label"] for t in topics
        )
        banner = f"TODAY'S TOPICS: {topic_labels}"

        return (conversation, meta, bubbles, banner,
                False, False, "New Session", "")

    # ── SEND MESSAGE ───────────────────────────────────────────────────────
    if trigger == "send-btn" and user_text and user_text.strip():
        if not meta.get("active"):
            return (no_update,) * 8

        user_text = user_text.strip()
        conversation = conversation + [{"role": "user", "content": user_text}]

        system_prompt = meta.get("system_prompt", "")
        response = get_ai_response(conversation, system_prompt)
        conversation = conversation + [{"role": "assistant", "content": response}]

        # Heuristic: count hints from Dave's response
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

            # Detect topic transition ("let's shift", "moving on", "next area")
            transition_phrases = ["let's shift", "shift gears", "moving on",
                                   "next area", "next topic", "let's talk about"]
            if any(ph in lower_resp for ph in transition_phrases):
                # Log completed topic
                update_session_log(
                    current_topic,
                    meta["hint_counts"].get(current_topic, 0),
                    meta["turn_counts"].get(current_topic, 0),
                )
                meta["current_topic_idx"] = current_idx + 1

        # Rebuild bubble list
        bubbles = []
        for msg in conversation:
            bubbles.append(make_bubble(msg["role"], msg["content"], pilot_name))

        return (conversation, meta, bubbles, no_update,
                False, False, no_update, "")

    return (no_update,) * 8


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import threading, webbrowser
    def open_browser():
        webbrowser.open(f"http://localhost:{PORT}")
    threading.Timer(1.5, open_browser).start()
    app.run(debug=False, port=PORT)