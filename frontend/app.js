const { useState, useEffect, useRef } = React;

function ChatApp() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [convs, setConvs] = useState([]);
  const [search, setSearch] = useState("");
  const [active, setActive] = useState(null);
  const [recording, setRecording] = useState(false);
  const [showSidebar, setShowSidebar] = useState(true);

  const wsRef = useRef(null);
  const recRef = useRef(null);

  useEffect(() => {
    fetchConversations("");
  }, []);

  const fetchConversations = (q) => {
    const url = q ? `/api/conversations?search=${encodeURIComponent(q)}` : '/api/conversations';
    fetch(url)
      .then(res => res.json())
      .then(setConvs);
  };

  useEffect(() => {
    const ws = new WebSocket(`${location.protocol === 'https:' ? 'wss' : 'ws'}://${location.host}/ws`);
    ws.onmessage = ev => {
      const data = JSON.parse(ev.data);
      if (data.type === 'chunk') {
        setMessages(prev => {
          const last = prev[prev.length - 1];
          if (last && last.role === 'assistant' && !last.done) {
            last.content += data.content;
            return [...prev.slice(0, -1), last];
          }
          return [...prev, { role: 'assistant', content: data.content, done: false }];
        });
      } else if (data.type === 'end') {
        setMessages(prev => {
          const last = prev[prev.length - 1];
          if (last) last.done = true;
          return [...prev];
        });
        fetchConversations(search);
      } else if (data.type === 'history') {
        setMessages(data.messages || []);
      }
    };
    wsRef.current = ws;
    return () => ws.close();
  }, []);

  const send = (content) => {
    const text = content ?? input;
    if (!text.trim()) return;
    setMessages(prev => [...prev, { role: 'user', content: text }]);
    wsRef.current && wsRef.current.send(JSON.stringify({ action: 'chat', content: text }));
    setInput("");
  };

  const loadConversation = (tid) => {
    setActive(tid);
    wsRef.current && wsRef.current.send(JSON.stringify({ action: 'load', thread_id: tid }));
  };

  const newConversation = () => {
    setActive(null);
    setMessages([]);
    wsRef.current && wsRef.current.send(JSON.stringify({ action: 'reset' }));
  };

  const doRename = (tid) => {
    const title = prompt('Novo título:');
    if (title) {
      fetch(`/api/conversations/${tid}/rename`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title })
      }).then(() => fetchConversations(search));
    }
  };

  const doDelete = (tid) => {
    if (confirm('Excluir conversa?')) {
      fetch(`/api/conversations/${tid}`, { method: 'DELETE' }).then(() => {
        if (active === tid) newConversation();
        fetchConversations(search);
      });
    }
  };

  const startVoice = () => {
    const Rec = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!Rec) return;
    const rec = new Rec();
    rec.lang = 'pt-BR';
    rec.onresult = e => {
      const txt = e.results[0][0].transcript;
      setRecording(false);
      rec.stop();
      send(txt);
    };
    rec.onend = () => setRecording(false);
    recRef.current = rec;
    setRecording(true);
    rec.start();
  };

  return (
    React.createElement('div', { className: 'sidebar-chat' },
      showSidebar && React.createElement('div', { className: 'sidebar' },
        React.createElement('button', {
          className: 'toggle-sidebar',
          onClick: () => setShowSidebar(false)
        }, '⮜'),
        React.createElement('input', {
          placeholder: 'Buscar...',
          value: search,
          onChange: e => { setSearch(e.target.value); fetchConversations(e.target.value); }
        }),
        React.createElement('div', { className: 'conv-list' },
          convs.map(c =>
            React.createElement('div', {
              key: c.thread_id,
              className: `conv-item ${active === c.thread_id ? 'active' : ''}`,
              onClick: () => loadConversation(c.thread_id)
            },
              React.createElement('span', null, c.title || c.thread_id.slice(0,8)),
              React.createElement('button', { onClick: e => { e.stopPropagation(); doRename(c.thread_id); } }, '✏️'),
              React.createElement('button', { onClick: e => { e.stopPropagation(); doDelete(c.thread_id); } }, '🗑️')
            )
          )
        ),
        React.createElement('div', { className: 'conv-item', onClick: newConversation }, '+ Nova conversa')
      ),
      React.createElement('div', { className: 'chat-main' },
        !showSidebar && React.createElement('button', {
          className: 'toggle-sidebar show-sidebar',
          onClick: () => setShowSidebar(true)
        }, '☰'),
        React.createElement('div', { className: 'messages' },
          messages.map((m,i) =>
            React.createElement('div', { key: i, className: `msg ${m.role}` }, m.content)
          )
        ),
        React.createElement('div', { className: 'input-area' },
          React.createElement('div', { className: 'input-wrapper' },
            React.createElement('button', {
              className: 'icon-mic',
              onClick: startVoice
            }, recording ? '◼' : React.createElement('i', { className: 'fas fa-microphone' })),
            React.createElement('input', {
              value: input,
              onChange: e => setInput(e.target.value),
              placeholder: 'Digite sua mensagem...',
              onKeyDown: e => { if (e.key === 'Enter') send(); }
            }),
            React.createElement('button', { className: 'icon-send', onClick: () => send() },
              React.createElement('i', { className: 'fas fa-paper-plane' }))
          )
        )
      )
    )
  );
}

ReactDOM.createRoot(document.getElementById('root')).render(React.createElement(ChatApp));
