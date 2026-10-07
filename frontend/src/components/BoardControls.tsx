import React from 'react';
import { Rewind, SkipBack, SkipForward, FastForward, ChevronDown, Lightbulb } from 'lucide-react';
import type { PositionNode } from '../types';

interface BoardControlsProps {
  currentPly: number;
  totalPlys: number;
  activeNode?: PositionNode;
  onJumpToPly: (ply: number) => void;
}

export const BoardControls: React.FC<BoardControlsProps> = ({
  currentPly,
  totalPlys,
  activeNode,
  onJumpToPly,
}) => {
  const isWhite = activeNode ? activeNode.is_white === 1 : currentPly % 2 === 0;
  const turnLabel = isWhite ? 'White' : 'Black';

  const moveText =
    activeNode?.san && activeNode.san !== 'Initial' && activeNode.san !== 'Live'
      ? `${activeNode.san} (${turnLabel})`
      : `Start Position (${turnLabel})`;

  const label = activeNode?.label || 'Best Move';
  const maxPly = Math.max(0, totalPlys - 1);
  const isStart = currentPly === 0;
  const isEnd = currentPly >= maxPly;

  return (
    <div className="flex flex-col gap-3.5 select-none w-full max-w-[500px] mx-auto">
      {/* Current Position Status Banner */}
      <div className="h-11 bg-gray-100 rounded-full shadow-clay-in px-3.5 flex items-center justify-between text-xs">
        <div className="flex items-center gap-2.5 truncate">
          <div className="flex items-center gap-1 bg-[#151619] text-white px-2.5 py-1 rounded-full font-mono text-[11px] font-bold shrink-0 shadow-sm">
            <span>PLY {currentPly}</span>
            <ChevronDown size={12} className="text-gray-400" />
          </div>

          <span className="font-medium text-gray-700 truncate text-xs">
            {moveText}
          </span>
        </div>

        <div className="bg-gray-100 shadow-clay-sm px-3 py-1 rounded-full flex items-center gap-1.5 shrink-0 text-[11px] font-semibold text-gray-800">
          <Lightbulb size={13} strokeWidth={1.75} className="text-gray-800" />
          <span>{label}</span>
        </div>
      </div>

      {/* Timeline Range Slider */}
      <div className="w-full h-7 bg-gray-100 rounded-full shadow-clay-in flex items-center px-3">
        <input
          type="range"
          min="0"
          max={maxPly}
          value={currentPly}
          onChange={(e) => onJumpToPly(parseInt(e.target.value, 10))}
          disabled={totalPlys <= 1}
          className="w-full appearance-none bg-transparent cursor-pointer [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:w-3.5 [&::-webkit-slider-thumb]:h-3.5 [&::-webkit-slider-thumb]:bg-gray-800 [&::-webkit-slider-thumb]:rounded-full [&::-webkit-slider-thumb]:shadow-md focus:outline-none"
        />
      </div>

      {/* Navigation Buttons */}
      <div className="flex items-center justify-between gap-3">
        <button
          onClick={() => onJumpToPly(0)}
          disabled={isStart}
          className="w-10 h-10 bg-gray-100 rounded-full shadow-clay-sm flex items-center justify-center hover:bg-gray-50 active:shadow-clay-in-sm text-gray-700 transition-all disabled:opacity-40"
          title="Start"
        >
          <Rewind size={15} strokeWidth={1.5} />
        </button>

        <button
          onClick={() => onJumpToPly(currentPly - 1)}
          disabled={isStart}
          className="flex-1 h-10 bg-gray-100 rounded-full shadow-clay-sm flex items-center justify-center gap-2 font-bold hover:bg-gray-50 active:shadow-clay-in-sm text-gray-700 transition-all text-xs disabled:opacity-40"
        >
          <SkipBack size={14} strokeWidth={1.5} /> Prev
        </button>

        <button
          onClick={() => onJumpToPly(currentPly + 1)}
          disabled={isEnd}
          className="flex-1 h-10 bg-[#16171a] hover:bg-black text-white rounded-full shadow-md flex items-center justify-center gap-2 font-bold transition-all text-xs active:scale-[0.99] disabled:opacity-40"
        >
          Next <SkipForward size={14} strokeWidth={1.5} />
        </button>

        <button
          onClick={() => onJumpToPly(maxPly)}
          disabled={isEnd}
          className="w-10 h-10 bg-gray-100 rounded-full shadow-clay-sm flex items-center justify-center hover:bg-gray-50 active:shadow-clay-in-sm text-gray-700 transition-all disabled:opacity-40"
          title="End"
        >
          <FastForward size={15} strokeWidth={1.5} />
        </button>
      </div>
    </div>
  );
};

export default BoardControls;

