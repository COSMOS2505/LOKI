import { useState, useEffect } from "react";
import { widgetDataApi } from "../../../api";

const INITIAL_BUDGET = {
  totalBudget: 0,
  entries: [],
  categories: ["Hospedagem", "Transporte", "Alimentação", "Tourist", "Outros"],
};

export default function FinanceWidget({ widget, onUpdate }) {
  const [data, setData] = useState(INITIAL_BUDGET);
  const [loading, setLoading] = useState(true);
  const [newCategory, setNewCategory] = useState("");
  const [newEntryName, setNewEntryName] = useState("");
  const [newEntryValue, setNewEntryValue] = useState("");

  useEffect(() => {
    loadData();
  }, [widget]);

  async function loadData() {
    try {
      const res = await widgetDataApi.get(widget.id);
      if (res.payload && Object.keys(res.payload).length > 0) {
        setData(res.payload);
      }
    } catch (e) {
      console.error("Erro ao carregar dados financeiros:", e);
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

  function addCategory() {
    const cat = newCategory.trim();
    if (!cat) return;
    setData((d) => ({
      ...d,
      categories: [...d.categories, cat],
    }));
    setNewCategory("");
    saveData();
  }

  function addEntry() {
    const name = newEntryName.trim();
    const value = parseFloat(newEntryValue) || 0;
    if (!name || value <= 0) return;
    setData((d) => ({
      ...d,
      entries: [...d.entries, { name, value, category: "Outros", done: false }],
    }));
    setNewEntryName("");
    setNewEntryValue("");
    saveData();
  }

  function toggleDone(entry) {
    setData((d) => ({
      ...d,
      entries: d.entries.map((e) =>
        e.name === entry.name ? { ...e, done: !e.done } : e
      ),
    }));
    saveData();
  }

  function totalSpent() {
    return data.entries
      .filter((e) => e.done)
      .reduce((sum, e) => sum + e.value, 0);
  }

  function pendingValue() {
    return data.entries
      .filter((e) => !e.done)
      .reduce((sum, e) => sum + e.value, 0);
  }

  const spent = totalSpent();
  const pending = pendingValue();
  const total = data.totalBudget || 0;
  const remaining = total > 0 ? total - spent : 0;
  const percent = total > 0 ? Math.min(100, Math.round((spent / total) * 100)) : 0;

  const barColor = percent > 90 ? "#e94560" : percent > 70 ? "#facc15" : "#4ade80";

  return (
    <div className="flex flex-col h-full bg-pixelSurface border border-gray-700 rounded pixel-border overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between px-3 py-2 border-b border-gray-700 bg-pixelCard/50">
        <div className="flex items-center gap-2">
          <span className="text-lg">💰</span>
          <h3 className="text-xs uppercase tracking-widest text-green-400 font-bold">
            Controle Financeiro
          </h3>
        </div>
        <div className="text-[9px] text-gray-500">Viagem do Brasil</div>
      </div>

      {/* Body */}
      <div className="flex-1 overflow-y-auto p-3 flex flex-col gap-3">
        {/* Resumo */}
        <div className="bg-gray-900/40 rounded p-3 border border-gray-700/50">
          <div className="grid grid-cols-3 gap-2 text-center">
            <div>
              <div className="text-[9px] text-gray-500 uppercase tracking-wider">Presupuesto</div>
              <div className="text-lg font-bold text-green-400">
                R$ {total.toLocaleString("pt-BR", { minimumFractionDigits: 2 })}
              </div>
            </div>
            <div>
              <div className="text-[9px] text-gray-500 uppercase tracking-wider">Gasto</div>
              <div className="text-lg font-bold text-yellow-400">
                R$ {spent.toLocaleString("pt-BR", { minimumFractionDigits: 2 })}
              </div>
            </div>
            <div>
              <div className="text-[9px] text-gray-500 uppercase tracking-wider">Restante</div>
              <div className="text-lg font-bold text-blue-400">
                R$ {remaining.toLocaleString("pt-BR", { minimumFractionDigits: 2 })}
              </div>
            </div>
          </div>
          {/* Barra de progresso */}
          <div className="mt-3 h-3 bg-gray-800 rounded-full overflow-hidden border border-gray-700">
            <div
              className="h-full transition-all duration-300"
              style={{ width: `${percent}%`, backgroundColor: barColor }}
            ></div>
          </div>
          <div className="flex justify-between text-[9px] text-gray-500 mt-1">
            <span>0%</span>
            <span>"{percent}%" de gasto</span>
            <span>100%</span>
          </div>
        </div>

        {/* Entradas Pendentes */}
        {data.entries.filter((e) => !e.done).length > 0 && (
          <div className="bg-gray-900/30 rounded p-2 border border-yellow-700/30">
            <div className="text-[9px] uppercase tracking-wider text-yellow-400 font-bold mb-1">
              Pendências ({data.entries.filter((e) => !e.done).length})
            </div>
            {data.entries
              .filter((e) => !e.done)
              .map((entry, i) => (
                <div
                  key={i}
                  className="flex items-center gap-2 py-1 border-b border-gray-800/50 last:border-0"
                >
                  <input
                    type="checkbox"
                    checked={entry.done}
                    onChange={() => toggleDone(entry)}
                    className="accent-green-500"
                  />
                  <span className="flex-1 text-xs text-gray-300">{entry.name}</span>
                  <span className="text-xs text-gray-500">R$ {entry.value.toFixed(2)}</span>
                </div>
              ))}
          </div>
        )}

        {/* Entradas Realizadas */}
        {data.entries.filter((e) => e.done).length > 0 && (
          <div className="bg-gray-900/30 rounded p-2 border border-green-700/30">
            <div className="text-[9px] uppercase tracking-wider text-green-400 font-bold mb-1">
              Realizado ({data.entries.filter((e) => e.done).length})
            </div>
            {data.entries
              .filter((e) => e.done)
              .map((entry, i) => (
                <div
                  key={i}
                  className="flex items-center gap-2 py-1 border-b border-gray-800/50 last:border-0 opacity-60"
                  style={{ textDecoration: "line-through" }}
                >
                  <span className="flex-1 text-xs text-gray-400">{entry.name}</span>
                  <span className="text-xs text-gray-500">R$ {entry.value.toFixed(2)}</span>
                </div>
              ))}
          </div>
        )}

        {/* Se não há entradas */}
        {data.entries.length === 0 && (
          <div className="flex flex-col items-center justify-center py-6 text-gray-500 gap-1">
            <div className="w-8 h-8 border border-dashed border-gray-600 rounded flex items-center justify-center">
              <span className="text-sm">+</span>
            </div>
            <p className="text-xs">Nenhuma despesa registrada</p>
          </div>
        )}

        {/* Formulário de nova entrada */}
        <div className="border-t border-gray-700 pt-2 mt-2">
          <div className="grid grid-cols-4 gap-2 mb-2">
            <input
              type="text"
              value={newEntryName}
              onChange={(e) => setNewEntryName(e.target.value)}
              placeholder="Despesa"
              className="bg-gray-800 border border-gray-600 rounded px-2 py-1 text-xs text-white placeholder-gray-500 focus:outline-none focus:border-green-500"
            />
            <input
              type="number"
              value={newEntryValue}
              onChange={(e) => setNewEntryValue(e.target.value)}
              placeholder="Valor R$"
              className="bg-gray-800 border border-gray-600 rounded px-2 py-1 text-xs text-white placeholder-gray-500 focus:outline-none focus:border-green-500"
            />
            <select
              className="bg-gray-800 border border-gray-600 rounded px-2 py-1 text-xs text-white focus:outline-none focus:border-green-500"
              value="Outros"
              onChange={(e) => {
                setData((d) => ({
                  ...d,
                  entries: [...d.entries.slice(-1), { name: newEntryName, value: parseFloat(newEntryValue) || 0, category: e.target.value, done: false }],
                }));
              }}
            >
              {data.categories.map((cat) => (
                <option key={cat} value={cat}>{cat}</option>
              ))}
            </select>
            <button
              onClick={addEntry}
              className="bg-green-900/40 border border-green-700/50 rounded px-2 py-1 text-xs text-green-300 hover:bg-green-900/60 font-bold tracking-wider uppercase"
            >
              Add
            </button>
          </div>
        </div>

        {/* Categorias */}
        <div className="border-t border-gray-700 pt-2 mt-2">
          <div className="text-[9px] uppercase tracking-wider text-gray-500 mb-1">
            Categorias
          </div>
          <div className="flex flex-wrap gap-1 mb-2">
            {data.categories.map((cat) => (
              <span
                key={cat}
                className="px-2 py-0.5 bg-gray-800 border border-gray-600 rounded text-[9px] text-gray-400 uppercase tracking-wider"
              >
                {cat}
              </span>
            ))}
          </div>
          <div className="flex gap-1">
            <input
              type="text"
              value={newCategory}
              onChange={(e) => setNewCategory(e.target.value)}
              placeholder="Nova categoria"
              className="flex-1 bg-gray-800 border border-gray-600 rounded px-2 py-1 text-[9px] text-white placeholder-gray-500 focus:outline-none focus:border-green-500"
            />
            <button
              onClick={addCategory}
              className="pixel-btn px-2 py-1 text-[9px]"
            >
              Add
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
