import React from 'react';
import {
  Activity,
  FileText,
  Moon,
  User,
  Star,
  Shield,
  BarChart2,
  Crosshair,
  Layers,
} from 'lucide-react';
import type { PositionNode, MatchSummary, GameHeaders } from '../types';
import MetricCard from './MetricCard';
import TelemetryChart, { type TelemetryPoint } from './TelemetryChart';
import MatchSummaryView from './MatchSummaryView';

interface TelemetryPanelProps {
  activeTab: 'telemetry' | 'summary';
  setActiveTab: (tab: 'telemetry' | 'summary') => void;
  activeNode?: PositionNode;
  chartData: TelemetryPoint[];
  currentPly: number;
  totalPlys: number;
  onSelectPly: (ply: number) => void;
  summary: MatchSummary | null;
  headers: GameHeaders | null;
}

const KnightIcon: React.FC<{ className?: string }> = ({ className }) => (
  <svg
    className={className}
    viewBox="0 0 24 24"
    xmlns="http://www.w3.org/2000/svg"
  >
    <path d="M19 22H5c-.55 0-1-.45-1-1v-1c0-.55.45-1 1-1h14c.55 0 1 .45 1 1v1c0 .55-.45 1-1 1zm-4.5-5h-5c-.4 0-.75-.24-.9-.6l-1.3-3.26c-.3-.76-.08-1.63.53-2.16L9.6 9.5C9.25 9.04 9 8.35 9 7.5c0-.81.33-1.6 1.05-2.22C11.16 4.33 13.06 4 15 4c.55 0 1 .45 1 1 0 1.25-.43 2.37-1.12 3.16l1.37 1.37c.48.48.75 1.13.75 1.82v4.15c0 .83-.67 1.5-1.5 1.5z" />
  </svg>
);

export const TelemetryPanel: React.FC<TelemetryPanelProps> = ({
  activeTab,
  setActiveTab,
  activeNode,
  chartData,
  currentPly,
  totalPlys,
  onSelectPly,
  summary,
  headers,
}) => {
  const qualityValue = activeNode?.label || 'Best Move';
  const cpLossText =
    activeNode?.cp_loss !== undefined ? `${activeNode.cp_loss} CP LOSS` : '0 CP LOSS';

  const riskValue = activeNode ? `${activeNode.blunder_risk_pct.toFixed(1)}%` : '0.0%';
  const riskSubValue =
    activeNode && activeNode.blunder_risk_pct >= 20 ? 'High Risk' : 'Stable';

  const evalValue = activeNode
    ? `${activeNode.cp_eval_white > 0 ? '+' : ''}${(activeNode.cp_eval_white / 100).toFixed(2)}`
    : '+0.20';

  const balance = activeNode?.material_balance ?? 0;
  const formattedBalance = balance > 0 ? `+${balance}` : `${balance}`;

  return (
    <div className="flex flex-col gap-4 sm:gap-5 h-full select-none">
      {/* Top Bar: Tabs on Left + Utility Buttons on Right */}
      <div className="flex items-center justify-between gap-3 shrink-0">
        {/* Tab Switcher */}
        <div className="flex items-center gap-1.5 p-1 bg-gray-100 rounded-full shadow-clay-in">
          <button
            onClick={() => setActiveTab('telemetry')}
            className={`px-4 sm:px-5 py-2 rounded-full font-bold text-xs flex items-center gap-2 transition-all ${
              activeTab === 'telemetry'
                ? 'bg-[#151619] text-white shadow-md'
                : 'text-gray-600 hover:text-gray-900 font-semibold'
            }`}
          >
            <Activity size={14} strokeWidth={2} />
            Live Telemetry
          </button>

          <button
            onClick={() => setActiveTab('summary')}
            className={`px-4 py-2 rounded-full text-xs flex items-center gap-2 transition-all ${
              activeTab === 'summary'
                ? 'bg-[#151619] text-white shadow-md font-bold'
                : 'text-gray-600 hover:text-gray-900 font-semibold'
            }`}
          >
            <FileText size={14} strokeWidth={1.5} />
            Match Post-Mortem Summary
          </button>
        </div>

        {/* Right Utility Buttons (Moon & User) */}
        <div className="flex items-center gap-2.5">
          <button
            className="w-9 h-9 rounded-full bg-gray-100 shadow-clay-sm flex items-center justify-center text-gray-700 hover:text-gray-950 active:shadow-clay-in-sm transition-all"
            title="Toggle theme"
          >
            <Moon size={15} strokeWidth={1.75} />
          </button>

          <button
            className="w-9 h-9 rounded-full bg-gray-100 shadow-clay-sm flex items-center justify-center text-gray-700 hover:text-gray-950 active:shadow-clay-in-sm transition-all"
            title="User Profile"
          >
            <User size={15} strokeWidth={1.75} />
          </button>
        </div>
      </div>

      {/* Tab 1: Live Telemetry */}
      {activeTab === 'telemetry' ? (
        <div className="flex-1 flex flex-col gap-4 sm:gap-5 overflow-hidden">
          {/* Top 3 Metric Cards */}
          <div className="grid grid-cols-3 gap-4 sm:gap-5 shrink-0">
            <MetricCard
              icon={<Star size={14} strokeWidth={2} className="text-gray-800" />}
              label="QUALITY"
              value={qualityValue}
              subValue={cpLossText}
            />
            <MetricCard
              icon={<Shield size={14} strokeWidth={2} className="text-gray-800" />}
              label="ML RISK"
              value={riskValue}
              subValue={riskSubValue}
            />
            <MetricCard
              icon={<BarChart2 size={14} strokeWidth={2} className="text-gray-800" />}
              label="EVAL ADV."
              value={evalValue}
              subValue="Pawns"
            />
          </div>

          {/* Middle Timeline Container */}
          <div className="bg-gray-100 rounded-[2rem] shadow-clay-out p-5 flex-1 flex flex-col min-h-[300px] overflow-hidden">
            <div className="flex justify-between items-center mb-3 shrink-0">
              <div className="flex items-center gap-2">
                <div className="w-6 h-6 rounded-lg bg-gray-200/80 flex items-center justify-center text-gray-900 shrink-0">
                  <KnightIcon className="w-4 h-4 fill-current text-gray-900" />
                </div>
                <div>
                  <h3 className="text-xs font-black tracking-tight text-gray-950">
                    Cognitive Telemetry Timeline
                  </h3>
                  <p className="text-[10px] font-medium text-gray-400">
                    Click any chart node to jump to ply
                  </p>
                </div>
              </div>

              <div className="font-mono text-[10px] font-bold bg-gray-100 shadow-clay-in px-3 py-1 rounded-full text-gray-700">
                PLY {currentPly} / {totalPlys}
              </div>
            </div>

            <div className="bg-gray-100 rounded-2xl shadow-clay-in flex-1 p-3.5 relative overflow-hidden">
              <TelemetryChart
                data={chartData}
                currentPly={currentPly}
                onSelectPly={onSelectPly}
              />
            </div>
          </div>

          {/* Bottom Tactical Complexity Row */}
          <div className="grid grid-cols-3 gap-4 sm:gap-5 shrink-0">
            <MetricCard
              icon={<Crosshair size={13} className="text-gray-700" strokeWidth={1.75} />}
              label="Center Tension"
              value={activeNode?.tactical_tension ?? 0}
            />
            <MetricCard
              icon={<KnightIcon className="w-3.5 h-3.5 fill-current text-gray-700" />}
              label="Hanging Pieces"
              value={activeNode?.hanging_pieces ?? 0}
            />
            <MetricCard
              icon={<Layers size={13} className="text-gray-700" strokeWidth={1.75} />}
              label="Material Balance"
              value={formattedBalance}
            />
          </div>
        </div>
      ) : (
        /* Tab 2: Match Post-Mortem Summary */
        <div className="flex-1 bg-gray-100 rounded-[2rem] shadow-clay-out p-6 overflow-y-auto">
          <MatchSummaryView summary={summary} headers={headers} />
        </div>
      )}
    </div>
  );
};

export default TelemetryPanel;

