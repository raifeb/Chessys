import React from 'react';
import { Chessboard } from 'react-chessboard';
import { RefreshCw, Maximize2, MoreVertical } from 'lucide-react';

interface ChessBoardProps {
  fen: string;
  orientation: 'white' | 'black';
  onPieceDrop: ({ sourceSquare, targetSquare }: { sourceSquare: string; targetSquare: string | null }) => boolean;
  isWhiteTurn?: boolean;
  onFlipBoard?: () => void;
}

export const ChessBoard: React.FC<ChessBoardProps> = ({
  fen,
  orientation,
  onPieceDrop,
  isWhiteTurn = true,
  onFlipBoard,
}) => {
  return (
    <div className="bg-gray-100 rounded-[2rem] shadow-clay-out p-5 sm:p-6 w-full max-w-[500px] mx-auto select-none flex flex-col gap-3.5">
      {/* Top Board Toolbar */}
      <div className="flex items-center justify-between">
        <div className="h-8 bg-gray-100 rounded-full shadow-clay-in px-3.5 flex items-center gap-2 text-xs font-semibold text-gray-800">
          <div
            className={`w-3 h-3 rounded-full border shadow-sm ${
              isWhiteTurn ? 'bg-white border-gray-300' : 'bg-gray-900 border-gray-900'
            }`}
          />
          <span>{isWhiteTurn ? 'White to move' : 'Black to move'}</span>
        </div>

        <div className="flex items-center gap-2">
          {onFlipBoard && (
            <button
              onClick={onFlipBoard}
              className="w-8 h-8 rounded-full bg-gray-100 shadow-clay-sm flex items-center justify-center text-gray-700 hover:text-gray-950 active:shadow-clay-in-sm transition-all"
              title="Flip board"
            >
              <RefreshCw size={14} strokeWidth={1.5} />
            </button>
          )}

          <button
            className="w-8 h-8 rounded-full bg-gray-100 shadow-clay-sm flex items-center justify-center text-gray-700 hover:text-gray-950 active:shadow-clay-in-sm transition-all"
            title="Full screen"
          >
            <Maximize2 size={14} strokeWidth={1.5} />
          </button>

          <button
            className="w-8 h-8 rounded-full bg-gray-100 shadow-clay-sm flex items-center justify-center text-gray-700 hover:text-gray-950 active:shadow-clay-in-sm transition-all"
            title="More options"
          >
            <MoreVertical size={14} strokeWidth={1.5} />
          </button>
        </div>
      </div>

      {/* Chessboard */}
      <div className="rounded-xl overflow-hidden shadow-clay-in">
        <Chessboard
          options={{
            position: fen,
            boardOrientation: orientation,
            darkSquareStyle: { backgroundColor: '#a4a8ad' },
            lightSquareStyle: { backgroundColor: '#f0f2f5' },
            onPieceDrop: onPieceDrop,
            animationDurationInMs: 200,
          }}
        />
      </div>
    </div>
  );
};

export default ChessBoard;

