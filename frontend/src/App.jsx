import axios from 'axios';
import {
  AlertCircle,
  Bot,
  BrainCircuit,
  CheckCircle2,
  Database,
  MessageSquare,
  Plus,
  Send,
  Trash2,
  Upload,
  User
} from 'lucide-react';
import { useEffect, useRef, useState } from 'react';

function App() {
  const [file, setFile] = useState(null);
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [isDragging, setIsDragging] = useState(false);
  const [toast, setToast] = useState({ show: false, message: "", type: "success" });

  // Update this to your Hugging Face URL
  const API_BASE = "https://divya930-documind-ai.hf.space";

  const [sessions, setSessions] = useState(() => {
    const saved = localStorage.getItem('documind_sessions_v3');
    return saved ? JSON.parse(saved) : [];
  });

  const [activeSessionId, setActiveSessionId] = useState(() => {
    return localStorage.getItem('documind_active_id_v3') || null;
  });

  const chatContainerRef = useRef(null);

  useEffect(() => {
    localStorage.setItem('documind_sessions_v3', JSON.stringify(sessions));
    localStorage.setItem('documind_active_id_v3', activeSessionId || "");
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
    }
  }, [sessions, activeSessionId]);

  const showToast = (msg, type = "success") => {
    setToast({ show: true, message: msg, type });
    setTimeout(() => setToast({ show: false, message: "", type: "success" }), 4000);
  };

  const handleUpload = async () => {
    if (!file) return;
    setUploading(true);
    const formData = new FormData();
    formData.append('file', file);
    try {
      await axios.post(`${API_BASE}/upload`, formData);
      showToast("Brain Trained Successfully!", "success");
    } catch (e) { 
      showToast("Backend connection failed.", "error"); 
    } finally { setUploading(false); }
  };

  const createNewChat = () => {
    const newId = Date.now().toString();
    const newSession = { id: newId, title: "New Analysis", messages: [] };
    setSessions([newSession, ...sessions]);
    setActiveSessionId(newId);
  };

  const handleChat = async () => {
    if (!query) return;
    let currentId = activeSessionId;
    if (!currentId) {
        currentId = Date.now().toString();
        const newSession = { id: currentId, title: query.slice(0, 25), messages: [] };
        setSessions([newSession, ...sessions]);
        setActiveSessionId(currentId);
    }
    const userMsg = { role: 'user', text: query };
    setSessions(prev => prev.map(s => 
      s.id === currentId ? { ...s, title: s.messages.length === 0 ? query.slice(0, 25) : s.title, messages: [...s.messages, userMsg] } : s
    ));
    setQuery("");
    setLoading(true);
    try {
      const res = await axios.get(`${API_BASE}/ask?q=${query}`);
      const botMsg = { role: 'bot', text: res.data.answer };
      setSessions(prev => prev.map(s => s.id === currentId ? { ...s, messages: [...s.messages, botMsg] } : s));
    } catch (e) {
      showToast("AI response failed.", "error");
    } finally { setLoading(false); }
  };

  const deleteSession = (id, e) => {
    e.stopPropagation();
    setSessions(sessions.filter(s => s.id !== id));
    if (activeSessionId === id) setActiveSessionId(null);
  };

  return (
    <div className="flex h-screen bg-[#09090b] text-zinc-300 font-sans overflow-hidden relative">
      {toast.show && (
        <div className="fixed top-6 right-6 z-[100] animate-in fade-in slide-in-from-top-4 duration-300">
          <div className={`px-5 py-3 rounded-2xl shadow-2xl flex items-center gap-3 border backdrop-blur-md ${toast.type === 'success' ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400' : 'bg-red-500/10 border-red-500/30 text-red-400'}`}>
            {toast.type === 'success' ? <CheckCircle2 size={18} /> : <AlertCircle size={18} />}
            <span className="text-sm font-bold tracking-tight">{toast.message}</span>
          </div>
        </div>
      )}
      <aside className="w-80 bg-[#121214] flex flex-col border-r border-zinc-800 shadow-2xl relative z-10">
        <div className="p-6 border-b border-zinc-800/60 flex items-center gap-3">
          <div className="p-2 bg-indigo-600 rounded-lg shadow-lg shadow-indigo-900/30"><BrainCircuit size={22} className="text-white" /></div>
          <div>
            <h1 className="text-lg font-extrabold text-white tracking-tight">DocuMind AI</h1>
            <span className="text-[9px] text-green-500 font-bold uppercase tracking-widest animate-pulse">Live on Cloud</span>
          </div>
        </div>
        <div className="p-4 flex flex-col gap-4">
          <button onClick={createNewChat} className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-zinc-800 hover:bg-zinc-700 border border-zinc-700 rounded-xl font-bold text-sm text-white"><Plus size={18} /> New Analysis</button>
          <div onDragOver={(e)=>{e.preventDefault(); setIsDragging(true)}} onDragLeave={()=>setIsDragging(false)} onDrop={(e)=>{e.preventDefault(); setIsDragging(false); setFile(e.dataTransfer.files[0])}} className={`border-2 border-dashed rounded-2xl p-6 text-center transition-all ${isDragging ? 'border-indigo-500 bg-indigo-600/10' : 'border-zinc-800 bg-zinc-900/40'}`}>
            <input type="file" id="pdf-input" className="hidden" onChange={(e) => setFile(e.target.files[0])} />
            <label htmlFor="pdf-input" className="cursor-pointer block"><Upload size={28} className="mx-auto mb-2 text-zinc-600" /><p className="text-[11px] font-semibold text-zinc-500">{file ? file.name : "Drop PDF here"}</p></label>
            {file && <button onClick={handleUpload} className="mt-4 w-full text-[11px] bg-indigo-600 py-2.5 rounded-xl font-black uppercase hover:bg-indigo-500 shadow-xl">{uploading ? "Analyzing..." : "Index File"}</button>}
          </div>
        </div>
        <div className="flex-1 overflow-y-auto px-3 space-y-1 py-2">
          <div className="flex items-center gap-2 px-3 mb-4 mt-2 opacity-40"><Database size={12} /><span className="text-[10px] font-black uppercase tracking-widest text-zinc-400">History</span></div>
          {sessions.map(s => (
            <div key={s.id} onClick={() => setActiveSessionId(s.id)} className={`group flex items-center justify-between px-3 py-3.5 rounded-xl cursor-pointer ${activeSessionId === s.id ? 'bg-zinc-800 text-white' : 'text-zinc-500 hover:bg-zinc-800/40'}`}>
              <div className="flex items-center gap-3 overflow-hidden"><MessageSquare size={14} /><span className="text-xs truncate font-medium">{s.title}</span></div>
              <Trash2 size={14} className="opacity-0 group-hover:opacity-100 hover:text-red-500" onClick={(e) => deleteSession(s.id, e)} />
            </div>
          ))}
        </div>
      </aside>
      <main className="flex-1 flex flex-col bg-[#09090b] relative">
        {activeSessionId ? (
          <>
            <div ref={chatContainerRef} className="flex-1 overflow-y-auto p-6 lg:p-12 space-y-10 scrollbar-hide">
              {sessions.find(s => s.id === activeSessionId)?.messages.map((msg, i) => (
                <div key={i} className={`w-full flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                  <div className={`flex gap-5 max-w-[70%] ${msg.role === 'user' ? 'flex-row-reverse' : 'flex-row'}`}>
                    <div className={`w-9 h-9 rounded-xl flex items-center justify-center shrink-0 shadow-lg border ${msg.role === 'user' ? 'bg-indigo-600' : 'bg-zinc-800'}`}>
                      {msg.role === 'user' ? <User size={18} className="text-white" /> : <Bot size={18} className="text-indigo-400" />}
                    </div>
                    <div className={`p-5 rounded-3xl shadow-xl text-[15px] ${msg.role === 'user' ? 'bg-indigo-700 text-white rounded-tr-none' : 'bg-[#121214] text-zinc-200 border border-zinc-800 rounded-tl-none'}`}>{msg.text}</div>
                  </div>
                </div>
              ))}
              {loading && <div className="text-zinc-500 text-xs font-medium italic animate-pulse ml-14">DocuMind is reading chunks...</div>}
            </div>
            <div className="p-8 bg-linear-to-t from-[#09090b] to-transparent">
              <div className="max-w-4xl mx-auto relative flex items-center">
                <input value={query} onChange={(e) => setQuery(e.target.value)} onKeyDown={(e) => e.key === 'Enter' && handleChat()} placeholder="Ask DocuMind anything..." className="w-full bg-[#121214] border border-zinc-800 rounded-2xl pl-6 pr-16 py-5 focus:outline-none focus:ring-2 focus:ring-indigo-600/50 text-white shadow-2xl" />
                <button onClick={handleChat} className="absolute right-3 bg-indigo-600 p-3.5 rounded-xl hover:bg-indigo-500 active:scale-90 shadow-lg shadow-indigo-900/40"><Send size={20} className="text-white" /></button>
              </div>
            </div>
          </>
        ) : (
          <div className="h-full flex flex-col items-center justify-center p-10">
            <BrainCircuit size={100} className="text-zinc-800 animate-pulse mb-8" />
            <h2 className="text-3xl font-black text-white">DocuMind Intelligence</h2>
            <p className="text-zinc-500 mt-3 text-center max-w-sm">Backend is Live on Hugging Face. Ready to process your documents.</p>
            <button onClick={createNewChat} className="mt-10 bg-indigo-600 hover:bg-indigo-500 text-white px-10 py-4 rounded-2xl font-black uppercase tracking-widest shadow-2xl active:scale-95 flex items-center gap-3"><Plus size={20} /> New Analysis</button>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;