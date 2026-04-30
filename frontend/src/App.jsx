import axios from 'axios';
import {
  AlertCircle,
  Bot,
  BrainCircuit,
  CheckCircle2,
  Database,
  Menu,
  MessageSquare,
  Plus,
  Send,
  Trash2,
  Upload,
  User,
  X
} from 'lucide-react';
import { useEffect, useRef, useState } from 'react';

function App() {
  const [file, setFile] = useState(null);
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [isDragging, setIsDragging] = useState(false);
  const [toast, setToast] = useState({ show: false, message: "", type: "success" });
  const [isSidebarOpen, setIsSidebarOpen] = useState(false); // Mobile Menu State

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
    setIsSidebarOpen(false); // Close sidebar on mobile after selection
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

  const currentSession = sessions.find(s => s.id === activeSessionId);

  return (
    <div className="flex h-screen bg-[#09090b] text-zinc-300 font-sans overflow-hidden relative">
      
      {/* --- MOBILE TOAST --- */}
      {toast.show && (
        <div className="fixed top-4 right-4 left-4 md:left-auto md:w-auto z-[200] animate-in fade-in slide-in-from-top-4">
          <div className={`px-5 py-3 rounded-2xl shadow-2xl flex items-center justify-center gap-3 border backdrop-blur-md ${toast.type === 'success' ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400' : 'bg-red-500/10 border-red-500/30 text-red-400'}`}>
            {toast.type === 'success' ? <CheckCircle2 size={18} /> : <AlertCircle size={18} />}
            <span className="text-sm font-bold">{toast.message}</span>
          </div>
        </div>
      )}

      {/* --- MOBILE MENU OVERLAY --- */}
      {isSidebarOpen && (
        <div 
          className="fixed inset-0 bg-black/60 backdrop-blur-sm z-[140] md:hidden"
          onClick={() => setIsSidebarOpen(false)}
        />
      )}

      {/* --- SIDEBAR --- */}
      <aside className={`
        fixed inset-y-0 left-0 z-[150] w-72 bg-[#121214] flex flex-col border-r border-zinc-800 shadow-2xl transition-transform duration-300
        ${isSidebarOpen ? 'translate-x-0' : '-translate-x-full'}
        md:relative md:translate-x-0 md:w-80
      `}>
        <div className="p-6 border-b border-zinc-800/60 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-indigo-600 rounded-lg shadow-lg shadow-indigo-900/30"><BrainCircuit size={22} className="text-white" /></div>
            <div>
              <h1 className="text-lg font-extrabold text-white tracking-tight">DocuMind AI</h1>
              <span className="text-[9px] text-green-500 font-bold uppercase tracking-widest animate-pulse">Live on Cloud</span>
            </div>
          </div>
          <button className="md:hidden text-zinc-500" onClick={() => setIsSidebarOpen(false)}><X /></button>
        </div>

        <div className="p-4 flex flex-col gap-4">
          <button onClick={createNewChat} className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-zinc-800 hover:bg-zinc-700 border border-zinc-700 rounded-xl font-bold text-sm text-white"><Plus size={18} /> New Analysis</button>
          
          {/* Responsive Drag & Drop Box */}
          <div onDragOver={(e)=>{e.preventDefault(); setIsDragging(true)}} onDragLeave={()=>setIsDragging(false)} onDrop={(e)=>{e.preventDefault(); setIsDragging(false); setFile(e.dataTransfer.files[0])}} className={`border-2 border-dashed rounded-2xl p-4 md:p-6 text-center transition-all ${isDragging ? 'border-indigo-500 bg-indigo-600/10' : 'border-zinc-800 bg-zinc-900/40'}`}>
            <input type="file" id="pdf-input" className="hidden" onChange={(e) => setFile(e.target.files[0])} />
            <label htmlFor="pdf-input" className="cursor-pointer block">
              <Upload size={24} className="mx-auto mb-2 text-zinc-600" />
              <p className="text-[10px] font-semibold text-zinc-500 truncate">{file ? file.name : "Select PDF"}</p>
            </label>
            {file && <button onClick={handleUpload} className="mt-3 w-full text-[10px] bg-indigo-600 py-2 rounded-lg font-black uppercase hover:bg-indigo-500">{uploading ? "Analyzing..." : "Index"}</button>}
          </div>
        </div>

        <div className="flex-1 overflow-y-auto px-3 space-y-1 py-2 scrollbar-hide">
          <div className="flex items-center gap-2 px-3 mb-4 mt-2 opacity-40 md:opacity-50"><Database size={12} /><span className="text-[10px] font-black uppercase tracking-widest text-zinc-400">History</span></div>
          {sessions.map(s => (
            <div key={s.id} onClick={() => {setActiveSessionId(s.id); setIsSidebarOpen(false);}} className={`group flex items-center justify-between px-3 py-3.5 rounded-xl cursor-pointer ${activeSessionId === s.id ? 'bg-zinc-800 text-white' : 'text-zinc-500 hover:bg-zinc-800/40'}`}>
              <div className="flex items-center gap-3 overflow-hidden"><MessageSquare size={14} /><span className="text-xs truncate font-medium">{s.title}</span></div>
              <Trash2 size={14} className="opacity-100 md:opacity-0 md:group-hover:opacity-100 hover:text-red-500" onClick={(e) => deleteSession(s.id, e)} />
            </div>
          ))}
        </div>
      </aside>

      {/* --- MAIN CONTENT AREA --- */}
      <main className="flex-1 flex flex-col bg-[#09090b] relative w-full">
        
        {/* Mobile Header Bar */}
        <div className="flex items-center justify-between p-4 md:hidden border-b border-zinc-800 bg-[#121214]">
          <button onClick={() => setIsSidebarOpen(true)}><Menu size={24} /></button>
          <h2 className="text-sm font-bold tracking-tight">DocuMind AI</h2>
          <div className="w-6"></div> {/* Spacer */}
        </div>

        {activeSessionId ? (
          <>
            <div ref={chatContainerRef} className="flex-1 overflow-y-auto p-4 md:p-12 lg:px-48 space-y-8 scrollbar-hide">
              {currentSession?.messages.map((msg, i) => (
                <div key={i} className={`w-full flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                  <div className={`flex gap-3 md:gap-5 max-w-[90%] md:max-w-[75%] ${msg.role === 'user' ? 'flex-row-reverse' : 'flex-row'}`}>
                    <div className={`w-8 h-8 md:w-9 md:h-9 rounded-lg flex items-center justify-center shrink-0 shadow-lg border ${msg.role === 'user' ? 'bg-indigo-600 border-indigo-500' : 'bg-zinc-800 border-zinc-700'}`}>
                      {msg.role === 'user' ? <User size={16} className="text-white" /> : <Bot size={16} className="text-indigo-400" />}
                    </div>
                    <div className={`p-4 md:p-5 rounded-2xl md:rounded-3xl shadow-xl text-[14px] md:text-[15px] leading-relaxed ${
                      msg.role === 'user' 
                      ? 'bg-indigo-700 text-white rounded-tr-none' 
                      : 'bg-[#121214] text-zinc-200 border border-zinc-800 rounded-tl-none'
                    }`}>
                      {msg.text}
                    </div>
                  </div>
                </div>
              ))}
              {loading && (
                <div className="flex justify-start animate-pulse">
                   <div className="flex gap-4 items-center">
                    <div className="w-8 h-8 rounded-lg bg-zinc-800 flex items-center justify-center"><Bot size={16} className="text-indigo-500" /></div>
                    <div className="text-zinc-500 text-[10px] uppercase font-bold tracking-widest">Scanning...</div>
                  </div>
                </div>
              )}
            </div>

            {/* Responsive Input Area */}
            <div className="p-4 md:p-8 bg-linear-to-t from-[#09090b] via-[#09090b] to-transparent">
              <div className="max-w-4xl mx-auto relative group">
                <div className="absolute -inset-1 bg-indigo-500/10 rounded-2xl blur opacity-100 md:opacity-0 md:group-focus-within:opacity-100 transition duration-500"></div>
                <div className="relative flex items-center">
                  <input 
                    value={query} 
                    onChange={(e) => setQuery(e.target.value)} 
                    onKeyDown={(e) => e.key === 'Enter' && handleChat()} 
                    placeholder="Ask anything..." 
                    className="w-full bg-[#121214] border border-zinc-800 rounded-xl md:rounded-2xl pl-4 pr-12 md:pl-6 md:pr-16 py-4 md:py-5 focus:outline-none focus:ring-2 focus:ring-indigo-600/50 text-white text-sm md:text-base shadow-2xl" 
                  />
                  <button onClick={handleChat} className="absolute right-2 md:right-3 bg-indigo-600 p-2.5 md:p-3.5 rounded-lg md:rounded-xl hover:bg-indigo-500 active:scale-90 shadow-lg">
                    <Send size={18} className="text-white" />
                  </button>
                </div>
              </div>
              <p className="hidden md:block text-center text-[10px] text-zinc-600 mt-6 font-bold uppercase tracking-[0.2em]">Enterprise AI Intelligence System</p>
            </div>
          </>
        ) : (
          <div className="h-full flex flex-col items-center justify-center p-6 text-center">
            <BrainCircuit size={80} className="text-zinc-800 animate-pulse mb-8" />
            <h2 className="text-2xl md:text-3xl font-black text-white tracking-tighter">DocuMind Intelligence</h2>
            <p className="text-zinc-500 mt-3 text-sm max-w-xs md:max-w-sm">Backend is Live on Cloud. Securely process your private data.</p>
            <button onClick={createNewChat} className="mt-8 bg-indigo-600 hover:bg-indigo-500 text-white px-8 md:px-10 py-3 md:py-4 rounded-xl md:rounded-2xl font-black uppercase tracking-widest shadow-2xl active:scale-95 transition-all flex items-center gap-3">
              <Plus size={20} /> New Analysis
            </button>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;