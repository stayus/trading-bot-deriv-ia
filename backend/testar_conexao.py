# testar_conexao.py
import websocket

def on_open(ws):
    print("🟢 Conexão ABERTA com ws.deriv.com!")
    ws.send('{"ping":1}')

def on_message(ws, msg):
    print("📩 Resposta:", msg)

def on_error(ws, error):
    print("🔴 Erro de conexão:", error)

def on_close(ws, close_status, close_msg):
    print("🔌 Conexão fechada")

# Testa a conexão
ws = websocket.WebSocketApp(
    "wss://ws.deriv.com/websockets/v3",
    on_open=on_open,
    on_message=on_message,
    on_error=on_error,
    on_close=on_close
)

print("🔄 Tentando conectar...")
ws.run_forever()