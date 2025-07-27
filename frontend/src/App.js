import { useEffect, useState } from 'react';

function App() {
  const [password, setPassword] = useState('');
  const [authenticated, setAuthenticated] = useState(false);
  const [status, setStatus] = useState({
    ligado: false,
    lucro: 0,
    operacoes: 0,
    modo: 'demo'
  });

  const API = 'https://meu-bot-backend.onrender.com'; // 🔥 Mude para seu backend

  const login = () => {
    if (password === 'secreta123') {
      setAuthenticated(true);
    } else {
      alert('Senha errada!');
    }
  };

  const ligar = () => fetch(`${API}/ligar`, { method: 'POST' });
  const parar = () => fetch(`${API}/parar`, { method: 'POST' });
  const mudarModo = (modo) => fetch(`${API}/modo/${modo}`, { method: 'POST' });

  useEffect(() => {
    const interval = setInterval(() => {
      fetch(`${API}/status`)
        .then(r => r.json())
        .then(data => setStatus(data))
        .catch(console.error);
    }, 3000);
    return () => clearInterval(interval);
  }, [API]);

  if (!authenticated) {
    return (
      <div style={{ padding: 20, textAlign: 'center' }}>
        <h2>🔐 Login</h2>
        <input
          type="password"
          value={password}
          onChange={e => setPassword(e.target.value)}
          placeholder="Senha"
          style={{ padding: 10, margin: 10 }}
        />
        <button onClick={login} style={{ padding: 10 }}>Entrar</button>
      </div>
    );
  }

  return (
    <div style={{ padding: 20 }}>
      <h2>🤖 Bot Trader</h2>
      <p><b>Modo:</b> {status.modo.toUpperCase()}</p>
      <p><b>Status:</b> {status.ligado ? '🟢 Ativo' : '🔴 Parado'}</p>
      <p><b>Lucro:</b> R$ {status.lucro.toFixed(2)}</p>
      <p><b>Operações:</b> {status.operacoes}</p>

      <div style={{ marginTop: 20 }}>
        <button onClick={() => mudarModo('demo')} style={{ margin: 5 }}>Modo Demo</button>
        <button onClick={() => mudarModo('real')} style={{ margin: 5 }}>Modo Real</button>
        <button onClick={ligar} style={{ margin: 5, backgroundColor: 'green', color: 'white' }}>Ligar</button>
        <button onClick={parar} style={{ margin: 5, backgroundColor: 'red', color: 'white' }}>Parar</button>
      </div>
    </div>
  );
}

export default App;