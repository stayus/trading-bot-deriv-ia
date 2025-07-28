# bot/deriv_api.py
import websocket
import json
import threading
import time
from dotenv import load_dotenv
import os

load_dotenv()

class DerivAPI:
    def __init__(self, demo=True):
        self.demo = demo
        self.ws_url = "wss://ws.deriv.com/websockets/v3"  # ✅ URL correta
        self.connection = None
        self.data = {}
        self.token = os.getenv("DERIV_TOKEN")
        if not self.token:
            raise Exception("❌ DERIV_TOKEN não encontrado no .env")

        self.req_id = 1

    def connect(self):
        print("🔴 Conectando à Deriv.com...")
        try:
            self.connection = websocket.WebSocketApp(
                self.ws_url,
                on_open=self.on_open,
                on_message=self.on_message,
                on_error=self.on_error,
                on_close=self.on_close
            )
            thread = threading.Thread(target=self.connection.run_forever)
            thread.daemon = True
            thread.start()
        except Exception as e:
            print(f"❌ Falha ao iniciar WebSocket: {e}")

    def on_open(self, ws):
        print("🟢 Conexão aberta. Autenticando...")
        self.authenticate()

    def authenticate(self):
        msg = {"authorize": self.token}
        self.connection.send(json.dumps(msg))

    def on_message(self, ws, message):
        try:
            response = json.loads(message)
            msg_type = response.get("msg_type")

            if "error" in response:
                error = response["error"]
                print(f"❌ Erro API: {error['message']}")
            else:
                if msg_type == "authorize":
                    print("✅ AUTENTICADO NA DERIV!")
                    self.data["authorized"] = True
                    self.get_balance()

                elif msg_type == "balance":
                    bal = response["balance"]["balance"]
                    curr = response["balance"]["currency"]
                    self.data["balance"] = bal
                    print(f"💰 Saldo: {bal} {curr}")

                elif msg_type == "candles":
                    prices = [float(c["close"]) for c in response["candles"]]
                    self.data["candles"] = prices
                    print(f"📊 {len(prices)} velas recebidas")

                elif msg_type == "proposal":
                    prop = response["proposal"]
                    contract_id = response["echo_req"]["proposal"]
                    self.data["last_proposal"] = {
                        "contract_id": contract_id,
                        "payout": float(prop["payout"]),
                        "stake": float(prop["spot"])
                    }
                    print(f"📋 Cotação: {prop['display_value']}")

                elif msg_type == "buy":
                    buy = response["buy"]
                    print(f"✅ OPERAÇÃO REALIZADA! Contrato ID: {buy['contract_id']} | Valor: ${buy['price']}")
        except Exception as e:
            print(f"❌ Erro ao processar mensagem: {e}")

    def on_error(self, ws, error):
        print(f"🔴 Erro de conexão: {error}")

    def on_close(self, ws, close_status, close_msg):
        print("🔌 Conexão fechada. Tentando reconectar...")
        time.sleep(3)
        self.connect()

    def get_balance(self):
        self.send({"balance": 1})

    def get_candles(self, symbol="R_50", count=100, granularity=60):
        msg = {
            "ticks_history": symbol,
            "adjust_start_time": 1,
            "count": count,
            "end": "latest",
            "start": 1,
            "style": "candles",
            "granularity": granularity,
            "req_id": self.req_id
        }
        self.req_id += 1
        self.send(msg)

    def get_price(self, symbol="R_50", contract_type="CALL", duration=5, amount=2):
        msg = {
            "proposal": self.req_id,
            "symbol": symbol,
            "contract_type": contract_type,
            "currency": "USD",
            "amount": amount,
            "duration": duration,
            "duration_unit": "t",
            "basis": "stake",
            "req_id": self.req_id
        }
        self.req_id += 1
        self.send(msg)

    def buy_contract(self, contract_id, price):
        """Envia a ordem de compra REAL"""
        msg = {
            "buy": contract_id,
            "price": price,
            "req_id": self.req_id
        }
        self.req_id += 1
        self.send(msg)
        print(f"✅✅ ENVIOU COMPRA: Contrato {contract_id} por ${price}")

    def send(self, message):
        if self.connection and self.connection.sock and self.connection.sock.connected:
            self.connection.send(json.dumps(message))
        else:
            print("⚠️ Não pode enviar: WebSocket não conectado")

    def start(self):
        self.connect()