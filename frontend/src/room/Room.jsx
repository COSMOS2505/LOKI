import { useState, useEffect } from "react";
import { widgetsApi } from "../../api";
import Agent from "./Agent";
import ChatPanel from "./ChatPanel";
import WidgetContent from "./widgets/WidgetContent";

export default function Room({ floor, onBack, onWidgetClick }) {
  const [widgets, setWidgets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [chatOpen, setChatOpen] = useState(false);
  const [selectedWidget, setSelectedWidget] = useState(null);

  useEffect(() => {
    loadWidgets();
  }, [floor]);

  async function loadWidgets() {
    if (!floor) return;
    try {
      const data = await widgetsApi.list(floor.id);
      setWidgets(data);
    } catch (e) {
      console.error("Erro ao carregar widgets:", e);
      setWidgets([]);
    } finally {
      setLoading(false);
    }
  }

  async function addWidget(widgetType) {
    try {
      const newWidget = await widgetsApi.create(floor.id, widgetType, {});
      setWidgets((prev) => [...prev, newWidget]);
    } catch (e) {
      alert("Erro ao adicionar widget: " + e.message);
    }
  }

  function handleWidgetClick(widget) {
    setSelectedWidget(widget);
  }

  const floorColor = floor?.color || "#4ade80";

  return (
    <div className="relative w-[90%] max-w-4xl bg-pixelSurface overflow-hidden pixel-border">
      {/* Janelas decorativas laterais */}
      <div className="absolute -left-6 top-4 w-5 h-20 bg-purple-800/30 border border-gray-600"></div>
      <div className="absolute -right-6 top-4 w-5 h-20 bg-purple-800/30 border border-gray-600"></div>
      <div className="absolute -left-6 bottom-4 w-5 h-20 bg-purple-800/30 border border-gray-600"></div>
      <div className="absolute -right-6 bottom-4 w-5 h-20 bg-purple-800/30 border border-gray-600"></div>

      {/* Teto decorativo */}
      <div className="h-8 bg-gradient-to-b from-purple-900/40 to-transparent border-b border-gray-700/50">
        <div className="flex items-center justify-between px-6">
          <div className="flex items-center gap-2">
            <div
              className="w-2 h-6 rounded-sm"
              style={{ backgroundColor: floorColor, boxShadow: `0 0 8px ${floorColor}` }}
            />
            <h2 className="text-lg font-bold uppercase tracking-widest text-pixelGold">
              {floor?.name}
            </h2>
          </div>
          <button
            onClick={onBack}
            className="pixel-btn px-2 py-1 text-[10px] leading-none"
          >
            ← Sair
          </button>
        </div>
      </div>

      {/* Chão (decorativo) */}
      <div className="h-6 bg-gradient-to-t from-gray-900/40 to-transparent border-t border-gray-700/30"></div>

      {/* Corpo da sala 2D */}
      <div className="flex flex-col items-center justify-center p-6 relative min-h-[400px]">
        {/* Fundo do quarto - papel parede pixel */}
        <div className="absolute inset-0 opacity-30 pointer-events-none">
          <svg width="100%" height="100%" viewBox="0 0 400 300" preserveAspectRatio="xMidYMid slice">
            <defs>
              <pattern id="wallpaper" width="24" height="24" patternUnits="userSpaceOnUse">
                <rect width="24" height="24" fill="#16213e" />
                <rect x="0" y="0" width="12" height="12" fill="#1a1a2e" />
                <rect x="12" y="12" width="12" height="12" fill="#1a1a2e" />
                <rect width="24" height="1" fill="#0f3460" opacity="0.3" />
                <rect y="12" width="24" height="1" fill="#0f3460" opacity="0.3" />
              </pattern>
            </defs>
            <rect width="100%" height="100%" fill="url(#wallpaper)" />
          </svg>
        </div>

        {/* Mesa principal */}
        <div className="relative z-10 w-full max-w-md mb-8">
          <div className="relative mx-auto">
            {/* Superfície da mesa */}
            <div className="w-full h-16 bg-gradient-to-b from-amber-900/30 to-amber-950/50 border-2 border-amber-700/50 rounded-t-lg">
              <div className="absolute inset-0 flex items-center justify-center gap-3">
                {/* Papel / caderno na mesa */}
                <div className="w-20 h-14 bg-white/10 border border-amber-600/30 rounded">
                  <div className="h-full w-full bg-[linear-gradient(to_right,#e2e8f0_1px,transparent_1px)] bg-[length:12px_12px]"></div>
                </div>
                {/* Caneta */}
                <div className="w-1 h-8 bg-gray-600 rounded"></div>
                {/* Tinteiro */}
                <div className="w-6 h-4 bg-blue-900/40 border border-blue-700/30 rounded"></div>
              </div>
            </div>
            {/* Pernas da mesa */}
            <div className="flex justify-between px-4 pb-2">
              <div className="w-4 h-4 bg-amber-900/40 border border-amber-700/30"></div>
              <div className="w-4 h-4 bg-amber-900/40 border border-amber-700/30"></div>
            </div>
          </div>
        </div>

        {/* Agente NPC (clicável) */}
        <div className="relative z-20 mb-6">
          <Agent onClick={() => setChatOpen(true)} floorName={floor?.name} />
          <p className="text-[10px] text-gray-500 text-center mt-1 uppercase tracking-widest">
            Agente — clique para conversar
          </p>
        </div>

        {/* Área de widgets */}
        <div className="relative z-10 w-full">
          {/* Grid de widgets existentes */}
          {widgets.length > 0 ? (
            <div className="grid grid-cols-2 gap-3">
              {widgets.map((widget) => (
                <WidgetCard
                  key={widget.id}
                  widget={widget}
                  onClick={() => handleWidgetClick(widget)}
                />
              ))}
            </div>
          ) : (
            <div className="flex flex-col items-center gap-2 py-6">
              <div className="w-12 h-12 border border-dashed border-gray-600 rounded flex items-center justify-center">
                <span className="text-xl">+</span>
              </div>
              <p className="text-xs text-gray-500">Nenhum widget nesta sala</p>
            </div>
          )}

          {/* Botões de adicionar widget */}
          <div className="mt-4 flex flex-wrap gap-2">
            <AddWidgetButton
              onClick={() => addWidget("financeiro")}
              icon="💰"
              label="Finanças"
            />
            <AddWidgetButton
              onClick={() => addWidget("ordens")}
              icon="🖨"
              label="Ordens"
            />
            <AddWidgetButton
              onClick={() => addWidget("posts_instagram")}
              icon="📸"
              label="Posts"
            />
            <AddWidgetButton
              onClick={() => addWidget("docs")}
              icon="📁"
              label="Docs"
            />
          </div>
        </div>
      </div>

      {/* Modal de widget aberto */}
      {selectedWidget && (
        <div className="absolute inset-0 z-30 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm">
          <div
            className="relative w-full max-w-lg max-h-[80vh] overflow-hidden pixel-border"
            onClick={(e) => e.stopPropagation()}
          >
            <WidgetContent
              widget={selectedWidget}
              onClose={() => setSelectedWidget(null)}
              onUpdate={(widgetId, data) => {
                setWidgets((prev) => prev.map((w) => w.id === widgetId ? { ...w } : w));
              }}
            />
          </div>
        </div>
      )}

      {/* Painel de chat */}
      {chatOpen && (
        <div className="absolute inset-0 z-30 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm">
          <div
            className="relative w-full max-w-lg max-h-[80vh] overflow-hidden pixel-border"
            onClick={(e) => e.stopPropagation()}
          >
            <ChatPanel
              floorId={floor?.id}
              systemPrompt={floor?.agent_system_prompt}
              agentMemory={floor?.agent_memory}
              onClose={() => setChatOpen(false)}
            />
          </div>
        </div>
      )}
    </div>
  );
}

function WidgetCard({ widget, onClick }) {
  const typeConfig = {
    financeiro: { icon: "💰", label: "Finanças", color: "#34d399" },
    ordens: { icon: "🖨", label: "Ordens", color: "#fb923c" },
    posts_instagram: { icon: "📸", label: "Posts", color: "#c084fc" },
    docs: { icon: "📁", label: "Docs", color: "#818cf8" },
  };

  const config = typeConfig[widget.widget_type] || {
    icon: "📋",
    label: widget.widget_type,
    color: "#e2e8f0",
  };

  return (
    <button
      onClick={onClick}
      className="group relative pixel-border rounded bg-pixelCard border border-gray-600 hover:border-gray-500 transition-all text-left"
      style={{ borderColor: config.color + "60" }}
    >
      <div className="h-1 w-full" style={{ backgroundColor: config.color }}></div>
      <div className="p-3">
        <div className="text-2xl mb-1">{config.icon}</div>
        <div className="text-xs font-bold uppercase tracking-widest" style={{ color: config.color }}>
          {config.label}
        </div>
        <div className="text-[9px] text-gray-500 mt-1">{widget.widget_type}</div>
      </div>
      <div className="absolute inset-0 rounded opacity-0 group-hover:opacity-100 transition-opacity bg-white/5 pointer-events-none"></div>
    </button>
  );
}

function AddWidgetButton({ icon, label, onClick }) {
  return (
    <button
      onClick={onClick}
      className="pixel-btn px-2 py-1 text-[10px] leading-none border-dashed hover:bg-gray-700"
    >
      {icon} {label}
    </button>
  );
}
