import { useState, useEffect } from "react";
import { widgetDataApi } from "../../../api";

const INITIAL_ORDERS = {
  orders: [],
};

export default function OrdersWidget({ widget, onUpdate }) {
  const [data, setData] = useState(INITIAL_ORDERS);
  const [loading, setLoading] = useState(true);
  const [newOrder, setNewOrder] = useState("");
  const [newClient, setNewClient] = useState("");
  const [filter, setFilter] = useState("todos");

  useEffect(() => {
    loadData();
  }, [widget]);

  async function loadData() {
    try {
      const res = await widgetDataApi.get(widget.id);
      if (res.payload && res.payload.orders) {
        setData(res.payload);
      }
    } catch (e) {
      console.error("Erro ao carregar ordens:", e);
    } finally {
      setLoading(false);
    }
  }

  async function saveData() {
    try {
      await widgetDataApi.set(widget.id, data);
      if (onUpdate) onUpdate(widget.id, data);
    } catch (e) {
      alert("Erro ao salvar: " + e.message);
    }
  }

  function addOrder() {
    const title = newOrder.trim();
    const client = newClient.trim();
    if (!title || !client) return;
    const now = new Date().toISOString();
    setData((d) => ({
      ...d,
      orders: [
        ...d.orders,
        {
          id: Date.now(),
          title,
          client,
          status: "pendente",
          createdAt: now,
        },
      ],
    }));
    setNewOrder("");
    setNewClient("");
    saveData();
  }

  function updateStatus(orderId, status) {
    setData((d) => ({
      ...d,
      orders: d.orders.map((o) =>
        o.id === orderId ? { ...o, status } : o
      ),
    }));
    saveData();
  }

  function deleteOrder(orderId) {
    if (!window.confirm("Remover esta ordem?")) return;
    setData((d) => ({
      ...d,
      orders: d.orders.filter((o) => o.id !== orderId),
    }));
    saveData();
  }

  const filtered = filter === "todos"
    ? data.orders
    : data.orders.filter((o) => o.status === filter);

  const statusCounts = {
    todos: data.orders.length,
    pendente: data.orders.filter((o) => o.status === "pendente").length,
    em_andamento: data.orders.filter((o) => o.status === "em_andamento").length,
    concluido: data.orders.filter((o) => o.status === "concluido").length,
  };

  return (
    <div className="flex flex-col h-full bg-pixelSurface border border-gray-700 rounded pixel-border overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between px-3 py-2 border-b border-gray-700 bg-pixelCard/50">
        <div className="flex items-center gap-2">
          <span className="text-lg">🖨</span>
          <h3 className="text-xs uppercase tracking-widest text-orange-400 font-bold">
            Ordens de Serviço
          </h3>
        </div>
        <div className="text-[9px] text-gray-500">Mundo 3D</div>
      </div>

      {/* Body */}
      <div className="flex-1 overflow-y-auto p-3 flex flex-col gap-3">
        {/* Filtro + Stats */}
        <div className="flex items-center gap-2 flex-wrap">
          {["todos", "pendente", "em_andamento", "concluido"].map((f) => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              className={`px-2 py-1 text-[9px] uppercase tracking-wider rounded border ${
                filter === f
                  ? "bg-orange-900/40 border-orange-600 text-orange-300"
                  : "bg-gray-800 border-gray-700 text-gray-400 hover:text-gray-200"
              }`}
            >
              {f === "todos" ? "Todas" : f === "pendente" ? "Pendentes" : f === "em_andamento" ? "Em Andamento" : "Concluídas"}
              {statusCounts[f] > 0 && (
                <span className="ml-1">({statusCounts[f]})</span>
              )}
            </button>
          ))}
        </div>

        {/* Lista de ordens */}
        {filtered.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-8 text-gray-500 gap-1">
            <div className="w-10 h-10 border border-dashed border-gray-600 rounded flex items-center justify-center">
              <span className="text-lg">📋</span>
            </div>
            <p className="text-xs">Nenhuma ordem nesta filtro</p>
          </div>
        ) : (
          <div className="flex flex-col gap-2">
            {filtered.map((order) => (
              <OrderCard
                key={order.id}
                order={order}
                onStatusChange={(status) => updateStatus(order.id, status)}
                onDelete={() => deleteOrder(order.id)}
              />
            ))}
          </div>
        )}

        {/* Formulário de nova ordem */}
        <div className="border-t border-gray-700 pt-2 mt-2">
          <div className="text-[9px] uppercase tracking-wider text-gray-500 mb-1">
            Nova Ordem
          </div>
          <div className="grid grid-cols-2 gap-2 mb-2">
            <input
              type="text"
              value={newOrder}
              onChange={(e) => setNewOrder(e.target.value)}
              placeholder="Título da ordem"
              className="bg-gray-800 border border-gray-600 rounded px-2 py-1 text-xs text-white placeholder-gray-500 focus:outline-none focus:border-orange-500"
            />
            <input
              type="text"
              value={newClient}
              onChange={(e) => setNewClient(e.target.value)}
              placeholder="Cliente"
              className="bg-gray-800 border border-gray-600 rounded px-2 py-1 text-xs text-white placeholder-gray-500 focus:outline-none focus:border-orange-500"
            />
          </div>
          <button
            onClick={addOrder}
            className="pixel-btn px-3 py-1 text-[9px] w-full"
          >
            + Criar Ordem
          </button>
        </div>
      </div>
    </div>
  );
}

function OrderCard({ order, onStatusChange, onDelete }) {
  const statusColors = {
    pendente: { bg: "bg-yellow-900/30", border: "border-yellow-700/30", text: "text-yellow-400" },
    em_andamento: { bg: "bg-blue-900/30", border: "border-blue-700/30", text: "text-blue-400" },
    concluido: { bg: "bg-green-900/30", border: "border-green-700/30", text: "text-green-400" },
  };

  const sc = statusColors[order.status] || statusColors.pendente;

  return (
    <div className={`rounded p-2 border ${sc.bg} ${sc.border}`}>
      <div className="flex items-start justify-between gap-2">
        <div className="flex-1 min-w-0">
          <div className="text-xs font-bold text-gray-200 truncate">{order.title}</div>
          <div className="text-[9px] text-gray-500 mt-0.5">
            Cliente: {order.client}
          </div>
          <div className="text-[9px] text-gray-600 mt-0.5">
            {new Date(order.createdAt).toLocaleDateString("pt-BR")}
          </div>
        </div>
        <div className="flex flex-col gap-1 items-end">
          <select
            value={order.status}
            onChange={(e) => onStatusChange(e.target.value)}
            className={`text-[9px] px-1 py-0.5 rounded border capitalize ${sc.border} ${sc.text} bg-gray-800/80`}
          >
            <option value="pendente">Pendente</option>
            <option value="em_andamento">Em Andamento</option>
            <option value="concluido">Concluído</option>
          </select>
          <button
            onClick={onDelete}
            className="text-[9px] text-red-400 hover:text-red-300 opacity-60 hover:opacity-100"
          >
            ✕
          </button>
        </div>
      </div>
      {/* Barra de progresso visual */}
      <div className="mt-1.5 h-1 bg-gray-800 rounded-full overflow-hidden">
        <div
          className="h-full transition-all"
          style={{
            width: order.status === "concluido" ? "100%" : order.status === "em_andamento" ? "50%" : "0%",
            backgroundColor: order.status === "concluido" ? "#4ade80" : order.status === "em_andamento" ? "#60a5fa" : "transparent",
          }}
        ></div>
      </div>
    </div>
  );
}
