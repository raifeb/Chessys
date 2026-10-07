import React from 'react';
import type { MatchSummary, GameHeaders } from '../types';

interface MatchSummaryViewProps {
  summary: MatchSummary | null;
  headers: GameHeaders | null;
}

const PHASES = ['Opening', 'Middlegame', 'Endgame'] as const;

export const MatchSummaryView: React.FC<MatchSummaryViewProps> = ({ summary, headers }) => {
  if (!summary) {
    return (
      <div className="h-full flex flex-col items-center justify-center p-6 text-gray-400 font-mono text-xs border border-dashed border-gray-300 rounded-2xl select-none">
        <span>No post-match summary available.</span>
        <span className="text-[10px] text-gray-400 mt-1">Analyze a PGN game to view full post-mortem analytics.</span>
      </div>
    );
  }

  const whitePlayer = headers?.white || 'White';
  const blackPlayer = headers?.black || 'Black';
  const whiteElo = headers?.white_elo || '-';
  const blackElo = headers?.black_elo || '-';

  return (
    <div className="space-y-5 select-none">
      {/* Opening Banner */}
      <div className="bg-gray-100 rounded-2xl shadow-clay-in p-4 flex justify-between items-center">
        <div>
          <span className="text-[10px] font-bold text-gray-500 uppercase tracking-widest block">Opening</span>
          <span className="text-xs font-bold text-gray-900">{summary.opening}</span>
        </div>
        <span className="text-xs font-mono font-bold bg-gray-200 px-3 py-1 rounded-full text-gray-700">
          {headers?.eco || 'ECO'}
        </span>
      </div>

      {/* Accuracy & ACPL Grid */}
      <div className="grid grid-cols-2 gap-4">
        {/* White */}
        <div className="bg-gray-100 rounded-2xl shadow-clay-out p-4 flex flex-col gap-2">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-gray-900">{whitePlayer}</span>
            <span className="text-[10px] font-mono text-gray-500">({whiteElo})</span>
          </div>
          <div className="grid grid-cols-2 gap-2 mt-1">
            <div className="bg-gray-100 rounded-xl shadow-clay-in p-2 text-center">
              <span className="text-[9px] font-bold text-gray-400 uppercase tracking-wider block">Accuracy</span>
              <span className="text-base font-black font-mono text-gray-900">{summary.white_stats.accuracy}%</span>
            </div>
            <div className="bg-gray-100 rounded-xl shadow-clay-in p-2 text-center">
              <span className="text-[9px] font-bold text-gray-400 uppercase tracking-wider block">ACPL</span>
              <span className="text-base font-black font-mono text-gray-900">{summary.white_stats.acpl}</span>
            </div>
          </div>
        </div>

        {/* Black */}
        <div className="bg-gray-100 rounded-2xl shadow-clay-out p-4 flex flex-col gap-2">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-gray-900">{blackPlayer}</span>
            <span className="text-[10px] font-mono text-gray-500">({blackElo})</span>
          </div>
          <div className="grid grid-cols-2 gap-2 mt-1">
            <div className="bg-gray-100 rounded-xl shadow-clay-in p-2 text-center">
              <span className="text-[9px] font-bold text-gray-400 uppercase tracking-wider block">Accuracy</span>
              <span className="text-base font-black font-mono text-gray-900">{summary.black_stats.accuracy}%</span>
            </div>
            <div className="bg-gray-100 rounded-xl shadow-clay-in p-2 text-center">
              <span className="text-[9px] font-bold text-gray-400 uppercase tracking-wider block">ACPL</span>
              <span className="text-base font-black font-mono text-gray-900">{summary.black_stats.acpl}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Phase Error Distribution */}
      <div className="bg-gray-100 rounded-2xl shadow-clay-in p-4">
        <span className="text-[10px] font-bold text-gray-500 uppercase tracking-widest block mb-3">
          Error Distribution by Phase
        </span>
        <div className="space-y-2.5">
          {PHASES.map((phase) => {
            const wErr = summary.white_phase_errors[phase] || 0;
            const bErr = summary.black_phase_errors[phase] || 0;
            const total = Math.max(1, wErr + bErr);

            return (
              <div key={phase} className="text-xs">
                <div className="flex justify-between items-center mb-1 text-[10px] font-medium text-gray-600">
                  <span>{phase}</span>
                  <span className="font-mono text-[10px] text-gray-400">
                    W: {wErr} | B: {bErr}
                  </span>
                </div>
                <div className="h-2.5 w-full bg-gray-200 rounded-full overflow-hidden flex shadow-inner">
                  <div
                    className="bg-gray-400 h-full transition-all duration-500"
                    style={{ width: `${(wErr / total) * 100}%` }}
                    title={`White: ${wErr}`}
                  />
                  <div
                    className="bg-gray-900 h-full transition-all duration-500"
                    style={{ width: `${(bErr / total) * 100}%` }}
                    title={`Black: ${bErr}`}
                  />
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Tactical Narrative */}
      <div className="bg-gray-100 rounded-2xl shadow-clay-out p-4">
        <span className="text-[10px] font-bold text-gray-500 uppercase tracking-widest block mb-2">
          Post-Mortem Tactical Narrative
        </span>
        <div className="text-xs text-gray-700 leading-relaxed space-y-2 whitespace-pre-line font-medium">
          {summary.narrative}
        </div>
      </div>
    </div>
  );
};

export default MatchSummaryView;

