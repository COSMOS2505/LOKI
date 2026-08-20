export default function Agent({ onClick, floorName }) {
  return (
    <button
      onClick={onClick}
      className="group relative cursor-pointer"
      title="Clique para conversar com o agente da sala"
    >
      {/* Sprite do agente — monolito pixel 8-bit inline */}
      <svg
        width="80"
        height="96"
        viewBox="0 0 80 96"
        className="drop-shadow-[3px_3px_0_#000] hover:drop-shadow-[4px_4px_0_#000] transition-all"
        role="img"
        aria-label={`Agente da sala ${floorName}`}
      >
        {/* Mesa */}
        <rect x="8" y="68" width="64" height="12" fill="#5c4033" stroke="#3b2416" strokeWidth="2" />
        <rect x="12" y="80" width="6" height="14" fill="#4a2c1a" stroke="#2a1608" strokeWidth="2" />
        <rect x="62" y="80" width="6" height="14" fill="#4a2c1a" stroke="#2a1608" strokeWidth="2" />

        {/* Corpo (casaco) */}
        <rect x="18" y="40" width="44" height="32" fill="#3b82f6" stroke="#1e3a8a" strokeWidth="2" />
        {/* Chapéu / moletom */}
        <rect x="22" y="30" width="36" height="14" fill="#f8fafc" stroke="#64748b" strokeWidth="2" />
        <rect x="26" y="26" width="28" height="6" fill="#e2e8f0" stroke="#94a3b8" strokeWidth="2" />

        {/* Cabeça */}
        <rect x="28" y="10" width="24" height="20" fill="#fcd34d" stroke="#92400e" strokeWidth="2" />
        {/* Olhos */}
        <rect x="32" y="16" width="4" height="4" fill="#1e293b" />
        <rect x="44" y="16" width="4" height="4" fill="#1e293b" />
        {/* Boca */}
        <rect x="34" y="22" width="12" height="2" fill="#78350f" />

        {/* Braço esquerdo + caneta */}
        <rect x="12" y="44" width="8" height="20" fill="#3b82f6" stroke="#1e3a8a" strokeWidth="2" />
        <rect x="8" y="54" width="6" height="2" fill="#1e293b" />

        {/* Braço direito */}
        <rect x="60" y="44" width="8" height="20" fill="#3b82f6" stroke="#1e3a8a" strokeWidth="2" />
        <rect x="62" y="55" width="4" height="2" fill="#1e293b" />

        {/* Perspectiva da mesa (destaque) */}
        <polygon points="8,68 72,68 66,60 14,60" fill="#2a1608" stroke="#5c4033" strokeWidth="1" />

        {/* Indicador hover glow */}
        <circle cx="40" cy="30" r="24" fill="none" stroke="#4ade80" strokeWidth="1" strokeDasharray="4 4" opacity="0.4" />
      </svg>

      {/* Tooltip */}
      <div className="absolute -bottom-6 left-1/2 -translate-x-1/2 whitespace-nowrap opacity-0 group-hover:opacity-100 transition-opacity text-[10px] uppercase tracking-widest text-green-400 bg-black/60 px-2 py-1 rounded border border-green-800/50">
        Clique para falar
      </div>
    </button>
  );
}
