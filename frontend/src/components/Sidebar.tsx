import React from 'react';
import { Upload, FolderOpen, RefreshCcw, RotateCcw, ChevronDown, Loader2 } from 'lucide-react';
import type { PositionNode } from '../types';
import MoveList from './MoveList';

interface SidebarProps {
  isLoading: boolean;
  isBatchMode: boolean;
  positions: PositionNode[];
  currentPly: number;
  onUploadClick: () => void;
  onLoadDemo: () => void;
  onFlipBoard: () => void;
  onResetSession: () => void;
  onSelectPly: (ply: number) => void;
}

export const Sidebar: React.FC<SidebarProps> = ({
  isLoading,
  isBatchMode,
  positions,
  currentPly,
  onUploadClick,
  onLoadDemo,
  onFlipBoard,
  onResetSession,
  onSelectPly,
}) => {
  const totalPlys = positions.length > 1 ? positions.length - 1 : 0;

  return (
    <aside className="w-72 sm:w-80 shrink-0 p-5 sm:p-6 flex flex-col gap-5 bg-[#151619] text-gray-200 z-10 h-screen overflow-y-auto select-none border-r border-white/5 shadow-2xl">
      {/* Brand Header with Chess Knight */}
      <div className="flex items-center gap-3">
        <div className="w-9 h-9 rounded-xl bg-white/10 flex items-center justify-center text-white shrink-0 shadow-inner">
          <svg
            className="w-5 h-5 fill-current"
            viewBox="0 0 24 24"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path d="M19 22H5c-.55 0-1-.45-1-1v-1c0-.55.45-1 1-1h14c.55 0 1 .45 1 1v1c0 .55-.45 1-1 1zm-4.5-5h-5c-.4 0-.75-.24-.9-.6l-1.3-3.26c-.3-.76-.08-1.63.53-2.16L9.6 9.5C9.25 9.04 9 8.35 9 7.5c0-.81.33-1.6 1.05-2.22C11.16 4.33 13.06 4 15 4c.55 0 1 .45 1 1 0 1.25-.43 2.37-1.12 3.16l1.37 1.37c.48.48.75 1.13.75 1.82v4.15c0 .83-.67 1.5-1.5 1.5z" />
          </svg>
        </div>
        <div>
          <h1 className="text-xl font-black tracking-tight text-white leading-none">
            CHESSYS
          </h1>
          <p className="text-[9px] font-bold text-gray-400 uppercase tracking-widest mt-1">
            Chess Analytics & Telemetry
          </p>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex flex-col gap-2">
        <button
          disabled={isLoading}
          onClick={onUploadClick}
          className="w-full h-12 bg-white text-gray-950 font-bold rounded-2xl shadow-lg flex items-center justify-center gap-2.5 hover:bg-gray-100 active:scale-[0.99] transition-all text-xs disabled:opacity-50"
        >
          {isLoading ? (
            <Loader2 size={16} className="animate-spin text-gray-900" />
          ) : (
            <Upload size={16} strokeWidth={2} className="text-gray-900" />
          )}
          Upload PGN
        </button>

        <button
          disabled={isLoading}
          onClick={onLoadDemo}
          className="w-full h-10 bg-transparent text-gray-300 hover:text-white hover:bg-white/5 rounded-xl flex items-center gap-3 px-3.5 transition-all text-xs font-medium disabled:opacity-50"
        >
          <FolderOpen size={16} strokeWidth={1.5} className="text-gray-400" />
          Load Demo Match
        </button>

        <button
          onClick={onFlipBoard}
          className="w-full h-10 bg-transparent text-gray-300 hover:text-white hover:bg-white/5 rounded-xl flex items-center gap-3 px-3.5 transition-all text-xs font-medium"
        >
          <RefreshCcw size={15} strokeWidth={1.5} className="text-gray-400" />
          Flip Board
        </button>
      </div>

      {/* Move Notation Box */}
      <div className="flex-1 min-h-[220px] bg-[#0d0e10] shadow-dark-in rounded-2xl p-3.5 flex flex-col overflow-hidden border border-white/5">
        <div className="flex justify-between items-center mb-2 px-1 shrink-0">
          <div className="flex items-center gap-1.5">
            <div className="w-1.5 h-1.5 rounded-full bg-gray-400"></div>
            <span className="text-[10px] font-bold text-gray-400 uppercase tracking-wider">
              Move Notation
            </span>
          </div>
          <span className="text-[10px] font-mono text-gray-500">
            {totalPlys > 0 ? `${totalPlys} ply` : 'Live'}
          </span>
        </div>
        <div className="flex-1 overflow-hidden">
          <MoveList
            positions={positions}
            currentPly={currentPly}
            onSelectPly={onSelectPly}
          />
        </div>
      </div>

      {/* Footer Controls */}
      <div className="flex flex-col gap-2 mt-auto shrink-0">
        <div className="h-10 rounded-xl bg-[#1b1c20] border border-white/5 flex items-center px-3.5 justify-between text-xs">
          <span className="font-bold uppercase text-gray-500 text-[10px] tracking-wider">
            Mode
          </span>
          <div className="flex items-center gap-1.5 text-gray-200 text-xs font-medium">
            <span>{isBatchMode ? 'PGN Telemetry' : 'Interactive'}</span>
            <ChevronDown size={14} className="text-gray-500" />
          </div>
        </div>

        <button
          onClick={onResetSession}
          className="w-full h-10 bg-[#1c1d22] hover:bg-[#24262c] border border-white/5 rounded-xl font-medium text-gray-400 hover:text-gray-200 active:scale-[0.99] transition-all text-xs flex items-center justify-center gap-2"
        >
          <RotateCcw size={14} strokeWidth={1.5} />
          Reset Session
        </button>
      </div>
    </aside>
  );
};

export default Sidebar;

