import React from 'react';
import {
  AreaChart,
  Area,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
} from 'recharts';
import { Target, Zap } from 'lucide-react';

export interface TelemetryPoint {
  ply: number;
  risk: number;
  evalPawns: number;
  label?: string;
  san?: string;
}

interface TelemetryChartProps {
  data: TelemetryPoint[];
  currentPly: number;
  onSelectPly?: (ply: number) => void;
}

export const TelemetryChart: React.FC<TelemetryChartProps> = ({
  data,
  currentPly,
  onSelectPly,
}) => {
  if (!data || data.length === 0) {
    return (
      <div className="h-full min-h-[220px] flex flex-col items-center justify-center text-gray-400 font-mono text-xs border border-dashed border-gray-300 rounded-2xl select-none">
        <span className="font-sans font-medium text-gray-500">Awaiting game telemetry data...</span>
        <span className="text-[10px] text-gray-400 mt-1">Upload a PGN or click "Load Demo Match"</span>
      </div>
    );
  }

  const currentPoint = data[currentPly] || data[0];

  return (
    <div className="w-full h-full flex flex-col gap-3 select-none">
      <div className="flex-1 min-h-[110px] flex flex-col">
        <div className="flex justify-between items-center mb-1">
          <div className="flex items-center gap-1.5 text-gray-600">
            <Target size={13} strokeWidth={1.75} className="text-gray-800" />
            <span className="text-[10px] font-bold tracking-wider text-gray-700 uppercase">
              Eval Advantage (Pawns)
            </span>
          </div>
          <span className="text-xs font-mono font-bold text-gray-900">
            {currentPoint?.evalPawns !== undefined
              ? `${currentPoint.evalPawns > 0 ? '+' : ''}${currentPoint.evalPawns.toFixed(2)}`
              : '+0.00'}
          </span>
        </div>

        <div className="flex-1 w-full min-h-[85px]">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart
              data={data}
              margin={{ top: 5, right: 10, left: -25, bottom: 0 }}
              onClick={(e) => {
                if (e && typeof e.activeTooltipIndex === 'number' && onSelectPly) {
                  onSelectPly(e.activeTooltipIndex);
                }
              }}
            >
              <defs>
                <linearGradient id="evalGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#111827" stopOpacity={0.12} />
                  <stop offset="95%" stopColor="#111827" stopOpacity={0.0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e6eb" />
              <XAxis dataKey="ply" hide />
              <YAxis
                domain={[-8, 8]}
                ticks={[-8, -4, 0, 4, 8]}
                stroke="#9ca3af"
                fontSize={9}
                axisLine={false}
                tickLine={false}
                tickFormatter={(v) => `${v > 0 ? '+' : ''}${v}`}
              />
              <ReferenceLine y={0} stroke="#9ca3af" strokeDasharray="2 2" />
              <ReferenceLine x={currentPly} stroke="#111827" strokeWidth={1.5} />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#111827',
                  color: '#fff',
                  borderRadius: '8px',
                  border: 'none',
                  fontSize: '11px',
                  fontFamily: 'monospace',
                }}
                itemStyle={{ color: '#fff' }}
                labelFormatter={(label) =>
                  `Ply ${label} ${data[Number(label)]?.san ? `(${data[Number(label)].san})` : ''}`
                }
                formatter={(value: unknown) => [
                  typeof value === 'number'
                    ? `${value > 0 ? '+' : ''}${value.toFixed(2)} pawns`
                    : '0.00 pawns',
                  'Eval',
                ]}
              />
              <Area
                type="monotone"
                dataKey="evalPawns"
                stroke="#111827"
                strokeWidth={1.75}
                fillOpacity={1}
                fill="url(#evalGradient)"
                animationDuration={200}
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="flex-1 min-h-[110px] flex flex-col border-t border-gray-200/80 pt-2.5">
        <div className="flex justify-between items-center mb-1">
          <div className="flex items-center gap-1.5 text-gray-600">
            <Zap size={13} strokeWidth={1.75} className="text-gray-800" />
            <span className="text-[10px] font-bold tracking-wider text-gray-700 uppercase">
              Cognitive Blunder Risk (%)
            </span>
          </div>
          <span className="text-xs font-mono font-bold text-gray-900">
            {currentPoint?.risk !== undefined
              ? `${currentPoint.risk.toFixed(1)}%`
              : '0.0%'}
          </span>
        </div>

        <div className="flex-1 w-full min-h-[85px]">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart
              data={data}
              margin={{ top: 5, right: 10, left: -25, bottom: 0 }}
              onClick={(e) => {
                if (e && typeof e.activeTooltipIndex === 'number' && onSelectPly) {
                  onSelectPly(e.activeTooltipIndex);
                }
              }}
            >
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e6eb" />
              <XAxis
                dataKey="ply"
                stroke="#9ca3af"
                fontSize={9}
                axisLine={false}
                tickLine={false}
                interval={Math.max(1, Math.floor(data.length / 10))}
              />
              <YAxis
                domain={[0, 100]}
                ticks={[0, 25, 50, 75, 100]}
                stroke="#9ca3af"
                fontSize={9}
                axisLine={false}
                tickLine={false}
                tickFormatter={(v) => `${v}%`}
              />
              <ReferenceLine y={20} stroke="#9ca3af" strokeDasharray="2 2" />
              <ReferenceLine x={currentPly} stroke="#111827" strokeWidth={1.5} />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#111827',
                  color: '#fff',
                  borderRadius: '8px',
                  border: 'none',
                  fontSize: '11px',
                  fontFamily: 'monospace',
                }}
                itemStyle={{ color: '#fff' }}
                labelFormatter={(label) =>
                  `Ply ${label} ${data[Number(label)]?.san ? `(${data[Number(label)].san})` : ''}`
                }
                formatter={(value: unknown) => [
                  typeof value === 'number' ? `${value.toFixed(1)}%` : '0.0%',
                  'Risk',
                ]}
              />
              <Line
                type="monotone"
                dataKey="risk"
                stroke="#2d3748"
                strokeWidth={1.75}
                dot={false}
                activeDot={{ r: 4, fill: '#111827', stroke: '#fff', strokeWidth: 1.5 }}
                animationDuration={200}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};

export default TelemetryChart;

