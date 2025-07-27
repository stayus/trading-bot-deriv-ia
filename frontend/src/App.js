import { useEffect, useState } from 'react';

function App() {
  const [password, setPassword] = useState('');
  const [authenticated, setAuthenticated] = useState(false);
  const [status, setStatus] = useState({
    running: false,
    profit: 0,
    trades: 0,
    mode: 'demo',
    last_signal: 'Nenhum'
  });

  const API_URL = 'https://bottrading-qmzb.onrender.com'; // ⚠️ Mude depois!

  const login = () => {
    fetch(`${API_URL}/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ password })
    })
    .then(res => res.json())
    .then(() => setAuthenticated(true))
    .catch(() => alert('Erro ao conectar'));
  };

  const updateStatus = () => {
    fetch(`${API_URL}/status`)
      .then(res => res.json())
      .then(setStatus)
      .catch(console.error);
  };

  useEffect(() => {
    const interval = setInterval(updateStatus, 3000);
    return () => clearInterval(interval);
  }, []);

  if (!authenticated) {
    return (
      <div className="p-6 bg-gray-50 min-h-screen flex items-center justify-center">
        <div className="bg-white p-6 rounded-lg shadow-md w-80">
          <h1 className="text-xl font-bold mb-4">Login</h1>
          <input
            type="password"
            value={password}
            onChange={e => setPassword(e.target.value)}
            placeholder="Senha"
            className="border p-2 w-full mb-4"
          />
          <button onClick={login} className="bg-blue-500 text-white p-2 w-full rounded">
            Entrar
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 bg-gray-50 min-h-screen">
      <div className="max-w-sm mx-auto bg-white rounded-lg shadow-md p-6">
        <h1 className="text-2xl font-bold text-center mb-4">🤖 Bot Trader IA</h1>

        <div className="mb-4">
          <p><strong>Modo:</strong> 
            <button onClick={() => fetch(`${API_URL}/set-mode/demo`, {method:'POST'})} className={`px-2 py-1 mx-1 ${status.mode==='demo'?'bg-blue-500 text-white':'bg-gray-200'}`}>Demo</button>
            <button onClick={() => fetch(`${API_URL}/set-mode/real`, {method:'POST'})} className={`px-2 py-1 mx-1 ${status.mode==='real'?'bg-red-500 text-white':'bg-gray-200'}`}>Real</button>
          </p>
          <p><strong>Status:</strong> <span className={status.running ? 'text-green-500' : 'text-red-500'}>{status.running ? '✅ Ativo' : '🛑 Parado'}</span></p>
          <p><strong>Lucro:</strong> R$ {status.profit.toFixed(2)}</p>
          <p><strong>Operações:</strong> {status.trades}</p>
          <p><strong>Último sinal:</strong> {status.last_signal}</p>
        </div>

        <div className="flex gap-2 mt-6">
          <button
            onClick={() => fetch(`${API_URL}/start`, { method: 'POST' })}
            className="flex-1 bg-green-500 text-white p-3 rounded font-bold"
          >
            ▶️ LIGAR
          </button>
          <button
            onClick={() => fetch(`${API_URL}/stop`, { method: 'POST' })}
            className="flex-1 bg-red-500 text-white p-3 rounded font-bold"
          >
            ⏹️ PARAR
          </button>
        </div>
      </div>
    </div>
  );
}

export default App;