import { useState, useRef, useEffect } from "react";
import { chatApi } from "../api";

export default function ChatPanel({ floorId, systemPrompt, agentMemory, onClose }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);
  const scrollRef = useRef(null);

  async function loadHistory() {
    try {
      const data = await chatApi.list(floorId);
      setMessages(data);
    } catch (e) {
      console.error("Erro ao carregar histórico:", e);
    }
  }

  useEffect(() => {
    loadHistory();
  }, [floorId]);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  async function handleSend(e) {
    e.preventDefault();
    if (!input.trim() || sending) return;

    const userMsg = input.trim();
    setInput("");
    setSending(true);

    try {
      // Adiciona mensagem do usuário localmente
      const userEntry = {
        id: Date.now(),
        floor_id: floorId,
        role: "user",
        content: userMsg,
        created_at: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, userEntry]);

      // Envia para API
      const result = await chatApi.send({
        floor_id: floorId,
        message: userMsg,
        system_prompt: systemPrompt,
        agent_memory: agentMemory,
      });

      setMessages((prev) => [...prev, {
        id: result.agent_reply.id || Date.now() + 1,
        floor_id: floorId,
        role: "agent",
        content: result.agent_reply.content || result.agent_reply,
        created_at: new Date().toISOString(),
      }]);
    } catch (err) {
      console.error("Erro no chat:", err);
      setMessages((prev) => [...prev, {
        id: Date.now(),
        floor_id: floorId,
        role: "agent",
        content: "⚠️ Erro ao comunicar com o agente. Tente novamente.",
        created_at: new Date().toISOString(),
      }]);
    } finally {
      setSending(false);
    }
  }

  function formatTime(iso) {
    try {
      const d = new Date(iso);
      return d.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
    } catch {
      return "";
    }
  }

  return (
    <div className="flex flex-col h-full bg-black/40 border border-gray-700 rounded pixel-border overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between px-3 py-2 bg-pixelSurface border-b border-gray-700">
        <h3 className="text-xs uppercase tracking-widest text-pixelAgent font-bold">
          Terminal do Agente
        </h3>
        <button
          onClick={onClose}
          className="pixel-btn px-2 py-1 text-[10px] leading-none"
        >
          ✕
        </button>
      </div>

      {/* Messages */}
      <div
        ref={scrollRef}
        className="flex-1 overflow-y-auto p-3 flex flex-col gap-2 max-h-[320px] min-h-[200px]"
      >
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-gray-500 text-xs">
            <div className="w-8 h-8 border border-gray-700 rounded flex items-center justify-center mb-2">
              <span className="text-lg">?</span>
            </div>
            <p>Histórico vazio. Comece a conversar!</p>
          </div>
        ) : (
          messages.map((msg) => (
            <div
              key={msg.id}
              className={`flex flex-col ${
                msg.role === "user"
                  ? "items-end gap-1"
                  : "items-start gap-1"
              }`}
            >
              <div
                className={`max-w-[85%] px-3 py-2 text-xs leading-relaxed ${
                  msg.role === "user"
                    ? "bg-purple-800/60 text-gray-100 rounded-pulse border border-purple-700/30 rtl:mr-3"
                    : "bg-green-900/30 text-gray-200 rounded-pulse border border-green-700/30 rtl:mr-3"
                }`}
                style={{
                  backgroundColor: msg.role === "user"
                    ? "#312e81"
                    : "#052e16",
                }}
              >
                {msg.content}
              </div>
              <span className="text-[9px] text-gray-600">
                {formatTime(msg.created_at)}
              </span>
            </div>
          ))
        )}

        {sending && (
          <div className="items-start gap-1">
            <div className="bg-green-900/30 border border-green-700/30 rounded-pulse px-3 py-2 text-xs text-gray-400">
              <span className="inline-block w-3 h-3 border-2 border-purple-400 border-t-transparent animate-spin mr-2"></span>
              Agente pensando...
            </div>
          </div>
        )}
      </div>

      {/* Input */}
      <form
        onSubmit={handleSend}
        className="flex items-center gap-2 px-3 py-2 border-t border-gray-700 bg-black/20"
      >
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Digite sua mensagem..."
          className="flex-1 bg-gray-800 border border-gray-600 rounded px-3 py-2 text-xs text-white placeholder-gray-500 focus:outline-none focus:border-pixelAgent"
          disabled={sending}
        />
        <button
          type="submit"
          disabled={!input.trim() || sending}
          className="pixel-btn px-3 py-2 text-xs disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Enviar
        </button>
      </form>
    </div>
  );
}
