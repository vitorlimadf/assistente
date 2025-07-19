const { useState, useEffect, useRef } = React;

function ChatApp() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const wsRef = useRef(null);

  useEffect(() => {
    const ws = new WebSocket(`${location.protocol === 'https:' ? 'wss' : 'ws'}://${location.host}/ws`);
    ws.onmessage = (ev) => {
      const data = JSON.parse(ev.data);
      if (data.type === 'chunk') {
        setMessages((prev) => {
          const last = prev[prev.length - 1];
          if (last && last.role === 'assistant' && !last.done) {
            last.content += data.content;
            return [...prev.slice(0, -1), last];
          }
          return [...prev, { role: 'assistant', content: data.content, done: false }];
        });
      } else if (data.type === 'end') {
        setMessages((prev) => {
          const last = prev[prev.length - 1];
          if (last) last.done = true;
          return [...prev];
        });
      } else if (data.type === 'history') {
        setMessages(data.messages);
      }
    };
    wsRef.current = ws;
    return () => ws.close();
  }, []);

  const send = () => {
    if (!input.trim()) return;
    const msg = { role: 'user', content: input };
    setMessages([...messages, msg]);
    wsRef.current && wsRef.current.send(JSON.stringify({ action: 'chat', content: input }));
    setInput("");
  };

  return (
    React.createElement('div', { className: 'chat-container' },
      messages.map((m, i) =>
        React.createElement('div', { key: i, className: `msg ${m.role}` }, m.content)
      ),
      React.createElement('div', { className: 'input-area' },
        React.createElement('input', {
          value: input,
          onChange: e => setInput(e.target.value),
          placeholder: 'Digite sua mensagem...',
          onKeyDown: e => { if (e.key === 'Enter') send(); }
        }),
        React.createElement('button', { onClick: send }, 'Enviar')
      )
    )
  );
}

ReactDOM.createRoot(document.getElementById('root')).render(React.createElement(ChatApp));
