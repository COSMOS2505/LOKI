import { useState, useEffect } from "react";
import { widgetDataApi } from "../../../api";

const INITIAL_POSTS = {
  posts: [],
  templates: ["foto_cotidiana", "tutorial", "behind_the_scenes", "produto_em_destaque", "comunidade"],
};

export default function PostsWidget({ widget, onUpdate }) {
  const [data, setData] = useState(INITIAL_POSTS);
  const [loading, setLoading] = useState(true);
  const [newPost, setNewPost] = useState("");
  const [newCaption, setNewCaption] = useState("");
  const [newHashtags, setNewHashtags] = useState("#loki #lifeos");
  const [newSchedule, setNewSchedule] = useState("");
  const [filter, setFilter] = useState("todos");
  const [scheduledOnly, setScheduledOnly] = useState(false);

  useEffect(() => {
    loadData();
  }, [widget]);

  async function loadData() {
    try {
      const res = await widgetDataApi.get(widget.id);
      if (res.payload && res.payload.posts) {
        setData({ ...INITIAL_POSTS, posts: res.payload.posts });
      }
    } catch (e) {
      console.error("Erro ao carregar posts:", e);
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

  function addPost() {
    const content = newPost.trim();
    const caption = newCaption.trim();
    const hashtags = newHashtags.trim();
    const schedule = newSchedule.trim();
    if (!content) return;
    const now = new Date().toISOString();
    setData((d) => ({
      ...d,
      posts: [
        ...d.posts,
        {
          id: Date.now(),
          content,
          caption,
          hashtags,
          schedule,
          status: schedule ? "agendado" : "rascunho",
          createdAt: now,
          scheduledAt: schedule ? new Date(schedule).toISOString() : null,
        },
      ],
    }));
    setNewPost("");
    setNewCaption("");
    setNewHashtags("#loki #lifeos");
    setNewSchedule("");
    saveData();
  }

  function updateStatus(postId, status) {
    setData((d) => ({
      ...d,
      posts: d.posts.map((p) =>
        p.id === postId ? { ...p, status } : p
      ),
    }));
    saveData();
  }

  function deletePost(postId) {
    if (!window.confirm("Remover este post?")) return;
    setData((d) => ({
      ...d,
      posts: d.posts.filter((p) => p.id !== postId),
    }));
    saveData();
  }

  function scheduleDate() {
    const now = new Date();
    now.setHours(now.getHours() + 24);
    setNewSchedule(now.toISOString().slice(0, 16));
  }

  const filtered = data.posts.filter((p) => {
    if (scheduledOnly && !p.schedule) return false;
    if (filter === "todos") return true;
    if (filter === "rascunho") return p.status === "rascunho";
    if (filter === "agendado") return p.status === "agendado";
    if (filter === "publicado") return p.status === "publicado";
    return true;
  });

  const statusCounts = {
    todos: data.posts.length,
    rascunho: data.posts.filter((p) => p.status === "rascunho").length,
    agendado: data.posts.filter((p) => p.status === "agendado").length,
    publicado: data.posts.filter((p) => p.status === "publicado").length,
  };

  return (
    <div className="flex flex-col h-full bg-pixelSurface border border-gray-700 rounded pixel-border overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between px-3 py-2 border-b border-gray-700 bg-pixelCard/50">
        <div className="flex items-center gap-2">
          <span className="text-lg">📸</span>
          <h3 className="text-xs uppercase tracking-widest text-purple-400 font-bold">
            Posts Instagram
          </h3>
        </div>
        <div className="text-[9px] text-gray-500">Planejador</div>
      </div>

      {/* Body */}
      <div className="flex-1 overflow-y-auto p-3 flex flex-col gap-3">
        {/* Stats */}
        <div className="flex items-center gap-3 text-[9px] text-gray-500">
          <span className="px-2 py-0.5 bg-gray-800 rounded border border-gray-700">
            Total: {statusCounts.todos}
          </span>
          <span className="px-2 py-0.5 bg-gray-800 rounded border border-gray-700">
            Rascunhos: {statusCounts.rascunho}
          </span>
          <span className="px-2 py-0.5 bg-gray-800 rounded border border-gray-700">
            Agendados: {statusCounts.agendado}
          </span>
          <span className="px-2 py-0.5 bg-gray-800 rounded border border-gray-700">
            Publicados: {statusCounts.publicado}
          </span>
        </div>

        {/* Filtros */}
        <div className="flex items-center gap-2 flex-wrap">
          {["todos", "rascunho", "agendado", "publicado"].map((f) => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              className={`px-2 py-1 text-[9px] uppercase tracking-wider rounded border ${
                filter === f
                  ? "bg-purple-900/40 border-purple-600 text-purple-300"
                  : "bg-gray-800 border-gray-700 text-gray-400 hover:text-gray-200"
              }`}
            >
              {f === "todos" ? "Todos" : f === "rascunho" ? "Rascunhos" : f === "agendado" ? "Agendados" : "Publicados"}
              {statusCounts[f] > 0 && (
                <span className="ml-1">({statusCounts[f]})</span>
              )}
            </button>
          ))}
          <label className="flex items-center gap-1 text-[9px] text-gray-500 cursor-pointer ml-2">
            <input
              type="checkbox"
              checked={scheduledOnly}
              onChange={(e) => setScheduledOnly(e.target.checked)}
              className="accent-purple-500"
            />
            Só agendados
          </label>
        </div>

        {/* Lista de posts */}
        {filtered.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-8 text-gray-500 gap-1">
            <div className="w-10 h-10 border border-dashed border-gray-600 rounded flex items-center justify-center">
              <span className="text-lg">📷</span>
            </div>
            <p className="text-xs">Nenhum post nesta filtro</p>
          </div>
        ) : (
          <div className="flex flex-col gap-2">
            {filtered.map((post) => (
              <PostCard
                key={post.id}
                post={post}
                onStatusChange={(status) => updateStatus(post.id, status)}
                onDelete={() => deletePost(post.id)}
              />
            ))}
          </div>
        )}

        {/* Formulário de novo post */}
        <div className="border-t border-gray-700 pt-2 mt-2">
          <div className="text-[9px] uppercase tracking-wider text-gray-500 mb-1">
            Novo Post
          </div>
          <div className="flex flex-col gap-2">
            <textarea
              value={newPost}
              onChange={(e) => setNewPost(e.target.value)}
              placeholder="Conteúdo / roteiro do post"
              rows={2}
              className="bg-gray-800 border border-gray-600 rounded px-2 py-1 text-xs text-white placeholder-gray-500 focus:outline-none focus:border-purple-500 resize-none"
            />
            <textarea
              value={newCaption}
              onChange={(e) => setNewCaption(e.target.value)}
              placeholder="Legenda"
              rows={1}
              className="bg-gray-800 border border-gray-600 rounded px-2 py-1 text-xs text-white placeholder-gray-500 focus:outline-none focus:border-purple-500 resize-none"
            />
            <div className="grid grid-cols-2 gap-2">
              <input
                type="text"
                value={newHashtags}
                onChange={(e) => setNewHashtags(e.target.value)}
                placeholder="#hashtags"
                className="bg-gray-800 border border-gray-600 rounded px-2 py-1 text-xs text-white placeholder-gray-500 focus:outline-none focus:border-purple-500"
              />
              <div className="flex gap-1">
                <input
                  type="datetime-local"
                  value={newSchedule}
                  onChange={(e) => setNewSchedule(e.target.value)}
                  className="flex-1 bg-gray-800 border border-gray-600 rounded px-2 py-1 text-xs text-white focus:outline-none focus:border-purple-500"
                />
                <button
                  onClick={scheduleDate}
                  className="pixel-btn px-2 py-1 text-[9px] self-end"
                >
                  +1d
                </button>
              </div>
            </div>
            <button
              onClick={addPost}
              className="pixel-btn px-3 py-1 text-xs w-full"
            >
              + Criar Post
            </button>
          </div>
        </div>

        {/* Templates rápidos */}
        <div className="border-t border-gray-700 pt-2">
          <div className="text-[9px] uppercase tracking-wider text-gray-500 mb-1">
            Templates rápidos
          </div>
          <div className="flex flex-wrap gap-1">
            {data.templates.map((t) => (
              <button
                key={t}
                onClick={() => {
                  const templates = {
                    foto_cotidiana: "Foto do dia ☀️\n\numa nova perspectiva",
                    tutorial: "Tutorial rápido:\n\npasso a passo",
                    behind_the_scenes: "Behind the scenes 🎬\n\no processo",
                    produto_em_destaque: "Produto em destaque 🔥\n\ndestaques",
                    comunidade: "Comunidade 👥\n\nnossa turma",
                  };
                  setNewPost(templates[t] || t);
                }}
                className="px-2 py-0.5 bg-gray-800 border border-gray-700 rounded text-[9px] text-gray-400 hover:text-purple-300 hover:border-purple-700/50"
              >
                {t.replace("_", " ")}
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

function PostCard({ post, onStatusChange, onDelete }) {
  const statusColors = {
    rascunho: { bg: "bg-gray-800/40", border: "border-gray-700/30", text: "text-gray-400" },
    agendado: { bg: "bg-purple-900/30", border: "border-purple-700/30", text: "text-purple-400" },
    publicado: { bg: "bg-green-900/30", border: "border-green-700/30", text: "text-green-400" },
  };

  const sc = statusColors[post.status] || statusColors.rascunho;

  return (
    <div className={`rounded p-2 border ${sc.bg} ${sc.border}`}>
      <div className="flex items-start justify-between gap-2">
        <div className="flex-1 min-w-0">
          <div className="text-xs text-gray-300 leading-relaxed">{post.content}</div>
          {post.caption && (
            <div className="text-[9px] text-gray-500 mt-1 italic">
              {post.caption}
            </div>
          )}
          {post.hashtags && (
            <div className="text-[9px] text-purple-400/70 mt-1">
              {post.hashtags}
            </div>
          )}
          {post.schedule && (
            <div className="text-[9px] text-purple-300 mt-1">
              🕐 Agendado: {new Date(post.schedule).toLocaleString("pt-BR")}
            </div>
          )}
          <div className="text-[9px] text-gray-600 mt-1">
            Criado: {new Date(post.createdAt).toLocaleDateString("pt-BR")}
          </div>
        </div>
        <div className="flex flex-col gap-1 items-end">
          <select
            value={post.status}
            onChange={(e) => onStatusChange(e.target.value)}
            className={`text-[9px] px-1 py-0.5 rounded border capitalize ${sc.border} ${sc.text} bg-gray-800/80`}
          >
            <option value="rascunho">Rascunho</option>
            <option value="agendado">Agendado</option>
            <option value="publicado">Publicado</option>
          </select>
          <button
            onClick={onDelete}
            className="text-[9px] text-red-400 hover:text-red-300 opacity-60 hover:opacity-100"
          >
            ✕
          </button>
        </div>
      </div>
    </div>
  );
}
