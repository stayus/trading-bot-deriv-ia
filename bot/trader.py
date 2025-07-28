# bot/trader.py
import time
import random
import numpy as np
from sklearn.linear_model import LinearRegression
import os
import csv
from datetime import datetime

# Tentar importar a API da Deriv
try:
    from .deriv_api import DerivAPI
    api = DerivAPI(demo=True)  # False para conta real
    api.start()
except Exception as e:
    print(f"⚠️ Erro ao carregar DerivAPI: {e}")
    api = None

# -------------------------------
# Funções de Análise Técnica
# -------------------------------

def calcular_rsi(precos, periodo=14):
    if len(precos) < periodo + 1:
        return 50
    deltas = np.diff(precos)
    ganho = np.where(deltas > 0, deltas, 0)
    perda = np.where(deltas < 0, -deltas, 0)
    media_ganho = np.mean(ganho[-periodo:])
    media_perda = np.mean(perda[-periodo:])
    if media_perda == 0:
        return 100
    rs = media_ganho / media_perda
    return 100 - (100 / (1 + rs))

def media_movel_simples(precos, periodo=9):
    return np.mean(precos[-periodo:])

def prever_tendencia(precos):
    X = np.array(range(len(precos))).reshape(-1, 1)
    y = np.array(precos)
    modelo = LinearRegression().fit(X, y)
    proximo = modelo.predict([[len(precos)]])[0]
    return "CALL" if proximo > precos[-1] else "PUT"

# -------------------------------
# Registro de Operações (CSV)
# -------------------------------

LOG_FILE = "trades.csv"
HEADERS = ["Data", "Hora", "Ativo", "Sinal", "Valor", "Resultado", "Lucro", "Saldo", "Modo"]

if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(HEADERS)

def registrar_operacao(ativo, sinal, valor, resultado, lucro, estado):
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
            f"{estado['profit']:.2f}",
            estado['mode'].upper()
        ])

# -------------------------------
# Loop Principal do Bot
# -------------------------------

def loop_do_bot(estado):
    print("🟢 Bot iniciado... Aguardando conexão com Deriv")
    ativos = ["R_50", "R_75", "R_100"]  # Pode adicionar EUR/USD depois
    duracao_ticks = 5  # Duração do contrato (5 ticks)

    while estado["running"]:
        try:
            # Atualiza saldo
            if api:
                api.get_balance()
                time.sleep(0.5)

            # Verifica metas
            if estado["profit"] >= estado["target"]:
                print("🎯 Meta de ganho atingida! Parando...")
                estado["running"] = False
                break
            if estado["profit"] <= -estado["stop_loss"]:
                print("🛑 Stop loss atingido! Parando...")
                estado["running"] = False
                break

            # Limite de pares simultâneos
            if len(estado["active_pairs"]) >= estado["max_concurrent"]:
                estado["last_signal"] = f"Limite atingido: {len(estado['active_pairs'])}/2"
                time.sleep(3)
                continue

            # Analisa cada ativo
            oportunidades = []
            for ativo in ativos:
                # Pede velas
                if api:
                    api.get_candles(symbol=ativo, count=100, granularity=60)
                    time.sleep(0.3)  # Evita flood

                # Usa velas reais ou fallback
                if api and api.data.get("candles") and len(api.data["candles"]) >= 50:
                    historico = api.data["candles"]
                else:
                    preco_atual = random.uniform(90, 110)
                    historico = [preco_atual + random.uniform(-3, 3) for _ in range(50)]

                if len(historico) < 50:
                    continue

                rsi = calcular_rsi(historico)
                mm9 = media_movel_simples(historico)
                preco_atual = historico[-1]
                tendencia = prever_tendencia(historico)
                direcao = "CALL" if preco_atual > mm9 else "PUT"

                # Filtros
                if not (30 < rsi < 70):
                    continue
                if tendencia != direcao:
                    continue
                variacao = abs(historico[-1] - historico[-6])
                if variacao < 0.5:
                    continue

                score = abs(rsi - 50) + variacao
                oportunidades.append({
                    "ativo": ativo,
                    "direcao": direcao,
                    "score": score
                })

            # Escolhe a melhor oportunidade
            if oportunidades:
                melhor = max(oportunidades, key=lambda x: x["score"])
                ativo = melhor["ativo"]
                direcao = melhor["direcao"]
                valor = estado["investment"]

                # Atualiza estado
                estado["current_pair"] = ativo
                estado["last_signal"] = f"Analisando {ativo}..."

                # Pede cotação
                if api and api.data.get("authorized"):
                    api.get_price(
                        symbol=ativo,
                        contract_type=direcao,
                        duration=duracao_ticks,
                        amount=valor
                    )
                    estado["last_signal"] = f"📊 Cotação pedida para {ativo}"

                    # Espera resposta (simulado)
                    time.sleep(1.5)

                    # ✅ ENVIA A ORDEM DE COMPRA REAL
                    if api.data.get("last_proposal"):
                        proposal = api.data["last_proposal"]
                        api.buy_contract(contract_id=proposal["contract_id"], price=valor)
                        estado["active_pairs"].append(ativo)
                        estado["last_signal"] = f"✅ Enviado {direcao} em {ativo}"
                        print(f"🚀 OPERAÇÃO ENVIADA: {direcao} em {ativo} | Valor: ${valor}")

                else:
                    # Modo simulação (seguro)
                    resultado = random.random() > 0.48
                    lucro = valor * 0.9 if resultado else -valor
                    estado["profit"] += lucro
                    estado["trades"] += 1
                    estado["last_signal"] = f"{ativo}:{direcao} {'✅' if resultado else '❌'}"
                    registrar_operacao(ativo, direcao, valor, resultado, lucro, estado)
                    print(f"📉 SIMULADO: {ativo} | {direcao} | Lucro: {lucro:+.2f}")

                # Simula tempo do contrato
                time.sleep(15)
                if ativo in estado["active_pairs"]:
                    estado["active_pairs"].remove(ativo)

            time.sleep(5)

        except Exception as e:
            print(f"❌ Erro no bot: {e}")
            time.sleep(5)