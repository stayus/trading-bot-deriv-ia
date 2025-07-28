# backend/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

# Estado do bot
estado = {
    "running": False,
    "mode": "demo",
    "profit": 0.0,
    "trades": 0,
    "investment": 2.0,
    "target": 50.0,
    "stop_loss": 30.0,
    "last_signal": "Parado",
    "current_pair": "Nenhum",
    "result": "N/A",
    "active_pairs": [],
    "max_concurrent": 2
}

# Permitir acesso do frontend (evita erro de CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class ConfigModel(BaseModel):
    investment: float = None
    target: float = None
    stop_loss: float = None

@app.get("/status")
def get_status():
    return estado

@app.post("/start")
def start_bot():
    if not estado["running"]:
        estado["running"] = True
        from threading import Thread
        Thread(target=run_bot, daemon=True).start()
    return {"status": "Bot iniciado"}

@app.post("/stop")
def stop_bot():
    estado["running"] = False
    return {"status": "Bot parado"}

@app.post("/set-mode/{mode}")
def set_mode(mode: str):
    if mode in ["demo", "real"]:
        estado["mode"] = mode
        return {"mode": mode}
    return {"error": "Modo inválido"}

@app.post("/config")
def set_config(config: ConfigModel):
    if config.investment is not None:
        estado["investment"] = config.investment
    if config.target is not None:
        estado["target"] = config.target
    if config.stop_loss is not None:
        estado["stop_loss"] = config.stop_loss
    return {"config": "Atualizado"}

def run_bot():
    from bot.trader import loop_do_bot
    loop_do_bot(estado)