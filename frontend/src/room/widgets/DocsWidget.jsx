import { useState, useEffect } from "react";
import { widgetDataApi } from "../../../api";

const INITIAL_DOCS = {
  documents: [],
  folders: [],
};

export default function DocsWidget({ widget, onUpdate }) {
  const [data, setData] = useState(INITIAL_DOCS);
  const [loading, setLoading] = useState(true);
  const [newDoc, setNewDoc] = useState("");
  const [newFolder, setNewFolder] = useState("");
  const [filter, setFilter] = useState("todos");

  useEffect(() => {
    loadData();
  }, [widget]);

  async function loadData() {
    try {
      const res = await widgetDataApi.get(widget.id);
      if (res.payload && (res.payload.documents || res.payload.folders)) {
        setData(res.payload);
      }
    } catch (e) {
      console.error("Erro ao carregar documentos:", e);
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

  function addDocument() {
    const name = newDoc.trim();
    if (!name) return;
    setData((d) => ({
      ...d,
      documents: [
        ...d.documents,
        {
          id: Date.now(),
          name,
          folder: null,
          description: "",
          status: "ativo",
          createdAt: new Date().toISOString(),
        },
      ],
    }));
    setNewDoc("");
    saveData();
  }

  function addFolder() {
    const name = newFolder.trim();
    if (!name) return;
    setData((d) => ({
      ...d,
      folders: [
        ...d.folders,
        {
          id: Date.now(),
          name,
          color: "#818cf8",
          documentCount: 0,
        },
      ],
    }));
    setNewFolder("");
    saveData();
  }

  function moveToFolder(docId, folderId) {
    setData((d) => ({
      ...d,
      documents: d.documents.map((doc) =>
        doc.id === docId ? { ...doc, folder: folderId } : doc
      ),
    }));
    saveData();
  }

  function deleteDoc(docId) {
    if (!window.confirm("Remover este documento?")) return;
    setData((d) => ({
      ...d,
      documents: d.documents.filter((doc) => doc.id !== docId),
    }));
    saveData();
  }

  function deleteFolder(folderId) {
    if (!window.confirm("Remover esta pasta?")) return;
    setData((d) => ({
      ...d,
      folders: d.folders.filter((f) => f.id !== folderId),
      documents: d.documents.map((doc) =>
        doc.folder === folderId ? { ...doc, folder: null } : doc
      ),
    }));
    saveData();
  }

  const filteredDocs = filter === "todos"
    ? data.documents
    : data.documents.filter((doc) => doc.folder === filter || doc.status === filter);

  const folderDocCount = {};
  data.folders.forEach((f) => {
    folderDocCount[f.id] = data.documents.filter((d) => d.folder === f.id).length;
  });

  return (
    <div className="flex flex-col h-full bg-pixelSurface border border-gray-700 rounded pixel-border overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between px-3 py-2 border-b border-gray-700 bg-pixelCard/50">
        <div className="flex items-center gap-2">
          <span className="text-lg">📁</span>
          <h3 className="text-xs uppercase tracking-widest text-indigo-400 font-bold">
            Documentos
          </h3>
        </div>
        <div className="text-[9px] text-gray-500">Viagem / Roteiro</div>
      </div>

      {/* Body */}
      <div className="flex-1 overflow-y-auto p-3 flex flex-col gap-3">
        {/* Folders (pastas) */}
        {data.folders.length > 0 && (
          <div className="flex items-center gap-2 mb-2">
            <div className="text-[9px] uppercase tracking-wider text-gray-500">Pastas:</div>
            {data.folders.map((folder) => (
              <button
                key={folder.id}
                onClick={() => setFilter(Number(filter) === folder.id ? "todos" : folder.id)}
                className={`px-2 py-0.5 text-[9px] uppercase tracking-wider rounded border ${
                  filter === folder.id
                    ? "bg-indigo-900/40 border-indigo-600 text-indigo-300"
                    : "bg-gray-800 border-gray-700 text-gray-400 hover:text-gray-200"
                }`}
                style={filter === folder.id ? { borderColor: folder.color } : {}}
              >
                {folder.name} ({folderDocCount[folder.id] || 0})
              </button>
            ))}
          </div>
        )}

        {/* Lista de documentos */}
        {filteredDocs.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-8 text-gray-500 gap-1">
            <div className="w-10 h-10 border border-dashed border-gray-600 rounded flex items-center justify-center">
              <span className="text-lg">📄</span>
            </div>
            <p className="text-xs">Nenhum documento nesta pasta</p>
          </div>
        ) : (
          <div className="flex flex-col gap-2">
            {filteredDocs.map((doc) => (
              <DocCard
                key={doc.id}
                doc={doc}
                folders={data.folders}
                onMoveToFolder={(folderId) => moveToFolder(doc.id, folderId)}
                onDelete={() => deleteDoc(doc.id)}
              />
            ))}
          </div>
        )}

        {/* Formulários */}
        <div className="border-t border-gray-700 pt-2 mt-2">
          <div className="grid grid-cols-2 gap-2">
            <div>
              <div className="text-[9px] uppercase tracking-wider text-gray-500 mb-1">
                Novo Documento
              </div>
              <div className="flex gap-1">
                <input
                  type="text"
                  value={newDoc}
                  onChange={(e) => setNewDoc(e.target.value)}
                  placeholder="Nome do doc"
                  className="flex-1 bg-gray-800 border border-gray-600 rounded px-2 py-1 text-xs text-white placeholder-gray-500 focus:outline-none focus:border-indigo-500"
                />
                <button
                  onClick={addDocument}
                  className="pixel-btn px-2 py-1 text-[9px]"
                >
                  + Add
                </button>
              </div>
            </div>
            <div>
              <div className="text-[9px] uppercase tracking-wider text-gray-500 mb-1">
                Nova Pasta
              </div>
              <div className="flex gap-1">
                <input
                  type="text"
                  value={newFolder}
                  onChange={(e) => setNewFolder(e.target.value)}
                  placeholder="Nome da pasta"
                  className="flex-1 bg-gray-800 border border-gray-600 rounded px-2 py-1 text-xs text-white placeholder-gray-500 focus:outline-none focus:border-indigo-500"
                />
                <button
                  onClick={addFolder}
                  className="pixel-btn px-2 py-1 text-[9px]"
                >
                  + Add
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function DocCard({ doc, folders, onMoveToFolder, onDelete }) {
  const folder = folders.find((f) => f.id === doc.folder);

  return (
    <div className="rounded p-2 bg-gray-800/40 border border-gray-700/50">
      <div className="flex items-start justify-between gap-2">
        <div className="flex-1 min-w-0">
          <div className="text-xs font-medium text-gray-200 truncate">{doc.name}</div>
          {folder && (
            <div className="text-[9px] text-indigo-400/70 mt-0.5">
              📂 {folder.name}
            </div>
          )}
          <div className="text-[9px] text-gray-600 mt-0.5">
            {new Date(doc.createdAt).toLocaleDateString("pt-BR")}
          </div>
        </div>
        <div className="flex flex-col gap-1 items-end">
          {folders.length > 0 && (
            <select
              value={doc.folder || ""}
              onChange={(e) => onMoveToFolder(e.target.value ? Number(e.target.value) : null)}
              className="text-[9px] px-1 py-0.5 rounded border border-gray-700 bg-gray-800/80 text-gray-400"
            >
              <option value="">Sem pasta</option>
              {folders.map((f) => (
                <option key={f.id} value={f.id}>{f.name}</option>
              ))}
            </select>
          )}
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
