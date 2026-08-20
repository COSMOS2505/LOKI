import { useState } from "react";

const PRESET_PROMPTS = {
  viagem: `Você é o agente de viagem do usuário. Ajude a planejar, orçar e organizar a viagem. Mantenha um tom prático e enfático nos custos.`,
  tese: `Você é o orientador virtual do autor da tese. Ajude a estruturar capítulos, revisar argumentos, sugerir referências e manter o cronograma.`,
  financeiro: `Você é o gestor financeiro pessoal. Ajude a planejar despesas, controlar orçamento, sugerir cortes e manter o registro de entradas/saídas.`,
  mundo3d: `Você é o coordenador do Mundo 3D (impressoras, pedidos, fila de fabricação). Ajude a gerenciar pedidos, status e planejar posts.`,
  posts: `Você é o planejador de conteúdo para Instagram. Ajude a criar ideias de posts, roteiros, hashtags e cronograma de publicação.`,
};

const PRESET_COLORS = {
  viagem: "#f472b6",
  tese: "#818cf8",
  financeiro: "#34d399",
  mundo3d: "#fb923c",
  posts: "#c084fc",
  default: "#4ade80",
};

export default function FloorModal({
  onClose, onSubmit, onDeleteFloor, existingFloor
}) {
  const [form, setForm] = useState({
    name: existingFloor?.name ?? "",
    purpose: existingFloor?.purpose ?? "",
    color: existingFloor?.color ?? PRESET_COLORS.default,
    status_summary: existingFloor?.status_summary ?? "",
    agent_system_prompt: existingFloor?.agent_system_prompt
      ?? (PRESET_PROMPTS.default ?? ""),
    agent_memory: existingFloor?.agent_memory ?? "{}",
  });

  const isEdit = !!existingFloor;

  function handleChange(e) {
    const { name, value } = e.target;
    setForm((f) => ({ ...f, [name]: value }));
  }

  async function handleSubmit(e) {
    e.preventDefault();
    try {
      await onSubmit(existingFloor?.id, form);
      onClose();
    } catch (err) {
      alert("Erro: " + err.message);
    }
  }

  function handleDelete(e) {
    e.preventDefault();
    e.stopPropagation();
    if (window.confirm("Arquivar este andar?")) {
      onDeleteFloor(existingFloor.id);
      onClose();
    }
  }

  const colorOptions = Object.entries(PRESET_COLORS).map(([key, hex]) => (
    <label key={key} className="cursor-pointer">
      <input
        type="radio"
        name="color"
        value={hex}
        checked={form.color === hex}
        onChange={handleChange}
        className="sr-only"
      />
      <div
        className="w-6 h-6 rounded-sm border-2 transition-all"
        style={{
          backgroundColor: hex,
          borderColor: form.color === hex ? "#f8fafc" : "#334155",
          boxShadow: form.color === hex ? `0 0 8px ${hex}` : "none",
        }}
      ></div>
    </label>
  ));

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm"
      onClick={onClose}
    >
      <div
        className="relative w-[90%] max-w-lg bg-pixelSurface border-2 border-gray-600 rounded pixel-border p-6"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Decoração pixel */}
        <div className="absolute -top-2 left-4 w-3 h-3 bg-gray-700"></div>
        <div className="absolute -top-2 right-4 w-3 h-3 bg-gray-700"></div>
        <div className="absolute -bottom-2 left-4 w-3 h-3 bg-gray-700"></div>
        <div className="absolute -bottom-2 right-4 w-3 h-3 bg-gray-700"></div>

        <h2 className="text-lg font-bold uppercase tracking-widest text-pixelGold mb-4">
          {isEdit ? "EDITAR ANDAR" : "NOVO ANDAR"}
        </h2>

        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          {/* Nome */}
          <div>
            <label className="block text-xs uppercase tracking-wider text-gray-400 mb-1">
              Nome do andar
            </label>
            <input
              name="name"
              value={form.name}
              onChange={handleChange}
              className="w-full bg-gray-800 border border-gray-600 rounded px-3 py-2 text-white placeholder-gray-500 focus:outline-none focus:border-pixelGold"
              placeholder="Ex: Viagem do Brasil"
              required
            />
          </div>

          {/* Propósito */}
          <div>
            <label className="block text-xs uppercase tracking-wider text-gray-400 mb-1">
              Propósito
            </label>
            <textarea
              name="purpose"
              value={form.purpose}
              onChange={handleChange}
              className="w-full bg-gray-800 border border-gray-600 rounded px-3 py-2 text-white placeholder-gray-500 focus:outline-none focus:border-pixelGold resize-none"
              rows={2}
              placeholder="O que esta sala gerencia?"
            />
          </div>

          {/* Cor temática */}
          <div>
            <label className="block text-xs uppercase tracking-wider text-gray-400 mb-2">
              Cor temática
            </label>
            <div className="flex gap-2 flex-wrap">
              {colorOptions}
            </div>
          </div>

          {/* Status summary */}
          <div>
            <label className="block text-xs uppercase tracking-wider text-gray-400 mb-1">
              Resumo de status
            </label>
            <input
              name="status_summary"
              value={form.status_summary}
              onChange={handleChange}
              className="w-full bg-gray-800 border border-gray-600 rounded px-3 py-2 text-white placeholder-gray-500 focus:outline-none focus:border-pixelGold"
              placeholder="Ex: 3 pendências, 1 em andamento"
            />
          </div>

          {/* System prompt */}
          <div>
            <label className="block text-xs uppercase tracking-wider text-gray-400 mb-1">
              System prompt do agente
            </label>
            <textarea
              name="agent_system_prompt"
              value={form.agent_system_prompt}
              onChange={handleChange}
              className="w-full bg-gray-800 border border-gray-600 rounded px-3 py-2 text-white placeholder-gray-500 focus:outline-none focus:border-pixelGold resize-none font-mono text-xs"
              rows={3}
              placeholder="Instruções para o agente desta sala"
            />
          </div>

          {/* Opcional: agent memory */}
          <div>
            <label className="block text-xs uppercase tracking-wider text-gray-400 mb-1">
              Memória do agente (JSON)
            </label>
            <textarea
              name="agent_memory"
              value={form.agent_memory}
              onChange={handleChange}
              className="w-full bg-gray-800 border border-gray-600 rounded px-3 py-2 text-white placeholder-gray-500 focus:outline-none focus:border-pixelGold resize-none font-mono text-xs"
              rows={2}
              placeholder='{"visits": 0, "notes": []}'
            />
          </div>

          {/* Botões */}
          <div className="flex gap-3 pt-2">
            <button
              type="submit"
              className="pixel-btn flex-1 py-2 text-sm"
            >
              {isEdit ? "Salvar" : "Criar Andar"}
            </button>
            {isEdit && (
              <button
                type="button"
                onClick={handleDelete}
                className="pixel-btn px-3 py-2 text-sm text-red-400 border-red-900/50 hover:bg-red-900/30"
              >
                Arquivar
              </button>
            )}
            <button
              type="button"
              onClick={onClose}
              className="pixel-btn px-3 py-2 text-sm"
            >
              Cancelar
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
