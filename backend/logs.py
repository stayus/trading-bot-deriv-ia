# backend/logs.py
import csv
from datetime import datetime
import os

LOG_FILE = "trades.csv"

# Cabeçalho do CSV
if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Data", "Hora", "Ativo", "Sinal", "Valor", "Resultado", "Lucro", "Saldo", "Modo"])

def registrar_operacao(sinal, valor, resultado, lucro, estado, ativo="BTC/USD"):
    data = datetime.now()
    with open(LOG_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            data.strftime("%d/%m/%Y"),
            data.strftime("%H:%M:%S"),
            ativo,
            sinal,
            f"{valor:.2f}",
            "✅ Win" if resultado else "❌ Loss",
            f"{lucro:.2f}",
            f"{estado['lucro']:.2f}",
            estado['modo'].upper()
        ])