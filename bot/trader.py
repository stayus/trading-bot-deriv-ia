# bot/trader.py
import time
import random
import numpy as np
from sklearn.linear_model import LinearRegression

# Simulação de análise com IA
def predict_trend(prices):
    X = np.array(range(len(prices))).reshape(-1, 1)
    y = np.array(prices)
    model = LinearRegression().fit(X, y)
    next_pred = model.predict([[len(prices)]])[0]
    return "call" if next_pred > prices[-1] else "put"

def calculate_rsi(prices, window=14):
    delta = np.diff(prices)
    gain = delta.copy()
    loss = delta.copy()
    gain[gain < 0] = 0
    loss[loss > 0] = 0
    avg_gain = np.mean(gain[-window:])
    avg_loss = -np.mean(loss[-window:])
    if avg_loss == 0:
        return 100
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

def trading_loop():
    from backend.main import state
    print("🟢 Bot de trading com IA iniciado...")

    while state["running"]:
        try:
            # Simular preços
            price = 100 + random.uniform(-5, 5)
            historical = [price + random.uniform(-2, 2) for _ in range(50)]

            rsi = calculate_rsi(historical)
            trend = predict_trend(historical)

            # Estratégia: só opera se RSI em zona neutra e tendência clara
            if 40 < rsi < 60:
                amount = 2.0  # Valor da operação
                duration = 5  # 5 ticks

                # Simular resultado
                win = random.choice([True, False])  # 50% de chance
                profit = amount * 0.9 if win else -amount

                # Atualiza estado
                state["trades"] += 1
                state["profit"] += profit
                state["last_signal"] = f"{trend.upper()} - RSI: {rsi:.1f} - {'✅ Win' if win else '❌ Loss'}"

                print(f"Operação: {trend} | RSI: {rsi:.1f} | Resultado: {profit:+.2f} | Saldo: {state['profit']:.2f}")

                # Verifica metas
                if state["profit"] >= state["target"]:
                    print("🎯 Meta de ganho atingida!")
                    state["running"] = False

                if state["profit"] <= -state["stop_loss"]:
                    print("🛑 Limite de perda atingido!")
                    state["running"] = False

            time.sleep(3)  # Nova análise a cada 3 segundos

        except Exception as e:
            print("Erro no bot:", e)
            time.sleep(5)