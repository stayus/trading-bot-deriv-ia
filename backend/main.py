# backend/main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
import threading
import time

app = FastAPI()

# Estado global
state = {
    "running": False,
    "mode": "demo",
    "profit": 0.0,
    "trades": 0,
    "target": 50.0,
    "stop_loss": 30.0,
    "last_signal": "Nenhum"
}

PASSWORD = "bot2025"  # 🔐 Mude depois!

class LoginModel(BaseModel):
    password: str

@app.post("/login")
def login(data: LoginModel):
    if data.password == PASSWORD:
        return {"success": True, "mode": state["mode"]}
    raise HTTPException(status_code=401, detail="Senha incorreta")

@app.get("/status")
def get_status():
    return state

@app.post("/start")
def start_bot():
    if not state["running"]:
        state["running"] = True
        threading.Thread(target=run_trading_bot, daemon=True).start()
    return {"status": "Bot iniciado"}

@app.post("/stop")
def stop_bot():
    state["running"] = False
    return {"status": "Bot parado"}

@app.post("/set-mode/{mode}")
def set_mode(mode: str):
    if mode in ["demo", "real"]:
        state["mode"] = mode
        return {"mode": mode}
    raise HTTPException(status_code=400, detail="Modo inválido")

def run_trading_bot():
    from bot.trader import trading_loop
    trading_loop()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=10000)