import { useState } from "react";
import FloorModal from "./FloorModal";

export default function FloorCard({ floor, onClick, onEdit }) {
  const [menuOpen, setMenuOpen] = useState(false);

  const colors = {
    label: floor.color || "#4ade80",
    bg: floor.color + "20",
  };

  return (
    <div
      className="relative group pixel-border rounded bg-pixelSurface cursor-pointer hover:bg-pixelCard transition-all"
      onClick={onClick}
      style={{ borderColor: floor.color }}
    >
      {/* Some decorative pixel elements */}
      <div className="absolute -left-1 -top-1 w-2 h-2 bg-gray-700"></div>
      <div className="absolute -right-1 -top-1 w-2 h-2 bg-gray-700"></div>
      <div className="absolute -left-1 -bottom-1 w-2 h-2 bg-gray-700"></div>

      <div className="flex items-center gap-4 p-4">
        {/* Floor number */}
        <div
          className="w-12 h-12 rounded bg-gray-800 border border-gray-600 flex items-center justify-center text-lg font-bold"
          style={{ color: floor.color }}
        >
          {floor.order_index ?? "?"}
        </div>

        {/* Floor info */}
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <h3 className="font-bold uppercase tracking-widest text-sm text-gray-100 truncate">
              {floor.name}
            </h3>
            <div
              className="w-2 h-4 rounded-sm"
              style={{ backgroundColor: floor.color, boxShadow: `0 0 6px ${floor.color}` }}
            ></div>
          </div>
          {floor.purpose && (
            <p className="text-xs text-gray-400 truncate mt-0.5">
              {floor.purpose}
            </p>
          )}
          {floor.status_summary && (
            <p className="text-[10px] text-gray-500 mt-1 truncate">
              {floor.status_summary}
            </p>
          )}
        </div>

        {/* Status indicator */}
        {floor.is_archived ? (
          <span className="text-[10px] uppercase tracking-wider text-gray-600">
            Arquivado
          </span>
        ) : (
          <span className="text-[10px] uppercase tracking-wider text-green-400">
            Online
          </span>
        )}
      </div>

      {/* Quick menu on hover */}
      {!floor.is_archived && (
        <div
          className="absolute right-2 top-1/2 -translate-y-1/2 opacity-0 group-hover:opacity-100 transition-opacity flex gap-1"
          onClick={(e) => e.stopPropagation()}
        >
          <button
            onClick={(e) => {
              e.stopPropagation();
              setMenuOpen(!menuOpen);
            }}
            className="pixel-btn px-2 py-1 text-xs"
          >
            ⋯
          </button>
          {menuOpen && (
            <div className="absolute right-0 top-full mt-1 bg-pixelSurface border border-gray-700 rounded pixel-border p-1 z-10">
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  setMenuOpen(false);
                }}
                className="w-full text-left text-xs text-gray-400 hover:text-gray-200 px-2 py-1"
              >
                ➕ Novo widget
              </button>
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  setMenuOpen(false);
                  onEdit();
                }}
                className="w-full text-left text-xs text-gray-400 hover:text-gray-200 px-2 py-1"
              >
                ✏️ Editar
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
