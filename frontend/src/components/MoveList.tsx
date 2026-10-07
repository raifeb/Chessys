import React, { useRef, useEffect } from 'react';
import type { PositionNode } from '../types';

interface MoveListProps {
  positions: PositionNode[];
  currentPly: number;
  onSelectPly: (ply: number) => void;
}

const getMoveAnnotation = (label: string) => {
  switch (label) {
    case 'Blunder':
      return '??';
    case 'Mistake':
      return '?';
    case 'Inaccuracy':
      return '?!';
    default:
      return '';
  }
};

export const MoveList: React.FC<MoveListProps> = ({
  positions,
  currentPly,
  onSelectPly,
}) => {
  const activeRef = useRef<HTMLButtonElement>(null);

  useEffect(() => {
    if (activeRef.current) {
      activeRef.current.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
  }, [currentPly]);

  if (!positions || positions.length <= 1) {
    return (
      <div className="h-full flex flex-col items-center justify-center text-xs text-gray-500 font-mono py-8 select-none">
        <span>No moves recorded</span>
        <span className="text-[10px] text-gray-600 mt-1">Load demo or upload PGN</span>
      </div>
    );
  }

  // Pair moves into turns: [ { moveNumber: 1, white?: node, black?: node }, ... ]
  const turns: { moveNumber: number; white?: PositionNode; black?: PositionNode }[] = [];

  for (let i = 1; i < positions.length; i++) {
    const node = positions[i];
    const turnIndex = Math.floor((i - 1) / 2);
    if (!turns[turnIndex]) {
      turns[turnIndex] = { moveNumber: Math.floor((i + 1) / 2) };
    }
    if (node.is_white === 1) {
      turns[turnIndex].white = node;
    } else {
      turns[turnIndex].black = node;
    }
  }

  return (
    <div className="h-full overflow-y-auto pr-1 space-y-0.5 font-mono text-xs select-none scrollbar-thin scrollbar-thumb-gray-800">
      {turns.map((turn) => {
        const isWhiteActive = turn.white && turn.white.ply === currentPly;
        const isBlackActive = turn.black && turn.black.ply === currentPly;

        const whiteAnnotation = turn.white ? getMoveAnnotation(turn.white.label) : '';
        const blackAnnotation = turn.black ? getMoveAnnotation(turn.black.label) : '';

        return (
          <div
            key={turn.moveNumber}
            className="flex items-center text-[11px] py-1 px-1.5 rounded hover:bg-white/5 transition-colors"
          >
            <span className="w-6 text-gray-500 font-medium">{turn.moveNumber}.</span>

            {/* White Move */}
            <div className="flex-1 flex items-center">
              {turn.white ? (
                <button
                  ref={isWhiteActive ? activeRef : null}
                  onClick={() => onSelectPly(turn.white!.ply)}
                  className={`px-1.5 py-0.5 rounded text-left flex items-center gap-1 transition-all ${
                    isWhiteActive
                      ? 'bg-white/20 text-white font-bold shadow-sm'
                      : 'text-gray-300 hover:text-white font-medium'
                  }`}
                >
                  <span>{turn.white.san}</span>
                  {whiteAnnotation && (
                    <span className="text-[9px] font-bold text-gray-400">
                      {whiteAnnotation}
                    </span>
                  )}
                </button>
              ) : (
                <span className="text-gray-700">-</span>
              )}
            </div>

            {/* Black Move */}
            <div className="flex-1 flex items-center">
              {turn.black ? (
                <button
                  ref={isBlackActive ? activeRef : null}
                  onClick={() => onSelectPly(turn.black!.ply)}
                  className={`px-1.5 py-0.5 rounded text-left flex items-center gap-1 transition-all ${
                    isBlackActive
                      ? 'bg-white/20 text-white font-bold shadow-sm'
                      : 'text-gray-300 hover:text-white font-medium'
                  }`}
                >
                  <span>{turn.black.san}</span>
                  {blackAnnotation && (
                    <span className="text-[9px] font-bold text-gray-400">
                      {blackAnnotation}
                    </span>
                  )}
                </button>
              ) : (
                <span className="text-gray-700">-</span>
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
};

export default MoveList;

