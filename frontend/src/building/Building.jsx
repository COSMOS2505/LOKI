import { useState, useEffect } from "react";
import { floorsApi } from "../api";
import FloorCard from "./FloorCard";
import FloorModal from "./FloorModal";
import Room from "../room/Room";

export default function Building() {
  const [floors, setFloors] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedFloor, setSelectedFloor] = useState(null);
  const [modalOpen, setModalOpen] = useState(false);
  const [editingFloor, setEditingFloor] = useState(null);
  const [showRoom, setShowRoom] = useState(false);

  useEffect(() => {
    loadFloors();
  }, []);

  async function loadFloors() {
    try {
      const data = await floorsApi.list();
      setFloors(data);
    } catch (e) {
      console.error("Erro ao carregar andares:", e);
      setFloors([]);
    } finally {
      setLoading(false);
    }
  }

  function handleFloorClick(floor) {
    setSelectedFloor(floor);
    setShowRoom(true);
  }

  function handleFloorClose() {
    setSelectedFloor(null);
    setShowRoom(false);
  }

  function handleAddFloor() {
    setEditingFloor(null);
    setModalOpen(true);
  }

  function handleEditFloor(floor) {
    setEditingFloor(floor);
    setModalOpen(true);
  }

  async function handleCreateFloor(formData) {
    try {
      await floorsApi.create(formData);
      await loadFloors();
      setModalOpen(false);
    } catch (e) {
      alert("Erro ao criar andar: " + e.message);
    }
  }

  async function handleUpdateFloor(id, data) {
    try {
      await floorsApi.update(id, data);
      await loadFloors();
      if (selectedFloor && selectedFloor.id === id) {
        const updated = await floorsApi.list().then((f) => f.find((f) => f.id === id));
        if (updated) setSelectedFloor(updated);
      }
    } catch (e) {
      alert("Erro ao atualizar andar: " + e.message);
    }
  }

  async function handleDeleteFloor(id) {
    if (!confirm("Arquivar este andar?")) return;
    try {
      await floorsApi.delete(id);
      await loadFloors();
      if (selectedFloor && selectedFloor.id === id) {
        handleFloorClose();
      }
    } catch (e) {
      alert("Erro ao arquivar: " + e.message);
    }
  }

  function handleWidgetClick(widget) {
    alert(`Abrir widget: ${widget.widget_type}\n\nEm breve: interface do widget.`);
  }

  if (showRoom && selectedFloor) {
    return (
      <div className="relative w-full h-screen overflow-hidden bg-black/60">
        <Room
          floor={selectedFloor}
          onBack={handleFloorClose}
          onWidgetClick={handleWidgetClick}
        />
      </div>
    );
  }

  return (
    <div className="relative w-full h-screen overflow-hidden">
      {/* Fundo do prédio */}
      <div className="absolute inset-0 bg-[url('data:image/svg+xml;charset=utf-8,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20width%3D%2264%22%20height%3D%2264%22%3E%3Crect%20width%3D%2264%22%20height%3D%2264%22%20fill%3D%22%231a1a2e%22%2F%3E%3Crect%20x%3D%220%22%20y%3D%220%22%20width%3D%2232%22%20height%3D%2232%22%20fill%3D%22%2316213e%22%2F%3E%3Crect%20x%3D%2232%22%20y%3D%2232%22%20width%3D%2232%22%20height%3D%2232%22%20fill%3D%22%2316213e%22%2F%3E%3C%2Fsvg%3E')] bg-repeat"></div>

      {/* Typography do prédio */}
      <div className="relative z-10 flex flex-col items-center pt-6 pb-4">
        <div className="text-[10px] tracking-[0.3em] uppercase text-gray-500 mb-1">
          Loki Life OS
        </div>
        <h1 className="text-3xl font-bold tracking-wider text-pixelGold drop-shadow-[3px_3px_0_#000]">
          PRÉDIO DOS ANDARES
        </h1>
      </div>

      {/* Corpo do prédio */}
      <div className="relative z-10 flex flex-1 flex-col items-center px-4 pt-10 pb-6 overflow-y-auto">
        {loading ? (
          <div className="flex flex-col items-center gap-2">
            <div className="w-6 h-6 border-2 border-pixelGold border-t-transparent animate-spin rounded"></div>
            <div className="text-xs text-gray-500">Carregando andares...</div>
          </div>
        ) : floors.length === 0 ? (
          <div className="flex flex-col items-center gap-3 py-12">
            <div className="w-16 h-16 border-2 border-dashed border-gray-600 rounded pixel-border flex items-center justify-center">
              <span className="text-2xl">?</span>
            </div>
            <p className="text-sm text-gray-500">
              Nenhum andar criado. Adicione o primeiro andar!
            </p>
          </div>
        ) : (
          <div className="flex flex-col w-full max-w-2xl gap-3">
            {floors.map((floor) => (
              <FloorCard
                key={floor.id}
                floor={floor}
                onClick={() => handleFloorClick(floor)}
                onEdit={() => handleEditFloor(floor)}
              />
            ))}
            <button
              onClick={handleAddFloor}
              className="pixel-btn px-6 py-3 mt-2 w-full text-sm"
            >
              + NOVO ANDAR
            </button>
          </div>
        )}
      </div>

      {/* Modal de criação/edição */}
      {modalOpen && (
        <FloorModal
          onClose={() => setModalOpen(false)}
          onSubmit={editingFloor ? handleUpdateFloor : handleCreateFloor}
          onDeleteFloor={handleDeleteFloor}
          existingFloor={editingFloor}
        />
      )}
    </div>
  );
}
