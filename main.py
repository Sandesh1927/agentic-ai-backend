from fastapi import FastAPI
from datetime import datetime
import time

app = FastAPI(title="Agentic AI Misuse Detection")

# -----------------------------
# Scam keywords
# -----------------------------
SCAM_KEYWORDS = [
    "otp", "password", "bank", "account",
    "blocked", "urgent", "verify", "send", "money"
]

# -----------------------------
# Agent memory
# -----------------------------
agents = {
    "agent_001": {
        "risk_score": 10,
        "status": "SAFE",
        "last_message": "",
        "last_time": 0,
        "repeat_count": 0
    },
    "agent_002": {
        "risk_score": 10,
        "status": "SAFE",
        "last_message": "",
        "last_time": 0,
        "repeat_count": 0
    }
}

# -----------------------------
# Incident logs (history)
# -----------------------------
incident_logs = []

# -----------------------------
# Keyword risk
# -----------------------------
def keyword_risk(message: str):
    score = 0
    msg = message.lower()
    for word in SCAM_KEYWORDS:
        if word in msg:
            score += 20
    return score

# -----------------------------
# Behavior risk
# -----------------------------
def behavior_risk(agent_id: str, message: str):
    agent = agents[agent_id]
    now = time.time()
    score = 0

    if now - agent["last_time"] < 5:
        score += 10

    if message.lower() == agent["last_message"].lower():
        agent["repeat_count"] += 1
        score += 10 * agent["repeat_count"]
    else:
        agent["repeat_count"] = 0

    agent["last_time"] = now
    agent["last_message"] = message

    return score

# -----------------------------
# Risk decay
# -----------------------------
def decay_risk(agent_id):
    if agents[agent_id]["risk_score"] > 10:
        agents[agent_id]["risk_score"] -= 5

# -----------------------------
# Status update
# -----------------------------
def update_status(agent_id):
    score = agents[agent_id]["risk_score"]

    if score >= 80:
        agents[agent_id]["status"] = "BLOCKED"
    elif score >= 40:
        agents[agent_id]["status"] = "SUSPICIOUS"
    else:
        agents[agent_id]["status"] = "SAFE"

# -----------------------------
# Log incidents automatically
# -----------------------------
def log_incident(agent_id, message):
    incident_logs.append({
        "time": datetime.now().isoformat(),
        "agent_id": agent_id,
        "message": message,
        "risk_score": agents[agent_id]["risk_score"],
        "status": agents[agent_id]["status"]
    })

# -----------------------------
# APIs
# -----------------------------
@app.get("/")
def home():
    return {
        "message": "Agentic AI Misuse Detection Backend Running",
        "time": datetime.now()
    }

@app.get("/agents")
def get_agents():
    return agents

@app.get("/incidents")
def get_incidents():
    return incident_logs

@app.post("/agent_message/{agent_id}")
def receive_message(agent_id: str, message: str):

    if agent_id not in agents:
        return {"error": "Agent not found"}

    k_risk = keyword_risk(message)
    b_risk = behavior_risk(agent_id, message)

    if k_risk == 0 and b_risk == 0:
        decay_risk(agent_id)
    else:
        agents[agent_id]["risk_score"] += k_risk + b_risk

    update_status(agent_id)

    # Auto log if risky
    if agents[agent_id]["status"] in ["SUSPICIOUS", "BLOCKED"]:
        log_incident(agent_id, message)

    return {
        "agent_id": agent_id,
        "message": message,
        "keyword_risk": k_risk,
        "behavior_risk": b_risk,
        "total_risk": agents[agent_id]["risk_score"],
        "status": agents[agent_id]["status"]
    }
