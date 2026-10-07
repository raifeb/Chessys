import React from 'react';
import { ChevronRight } from 'lucide-react';

interface MetricCardProps {
  icon: React.ReactNode;
  label: string;
  value: string | number;
  subValue?: string | number;
}

export const MetricCard: React.FC<MetricCardProps> = ({
  icon,
  label,
  value,
  subValue,
}) => {
  const isBottomCard = subValue === undefined;

  return (
    <div
      className={`bg-gray-100 rounded-3xl shadow-clay-in p-4 sm:p-5 flex flex-col justify-between select-none ${
        isBottomCard ? 'h-24' : 'h-28'
      }`}
    >
      <div className="flex items-center gap-2 text-gray-500">
        <span className="text-gray-700">{icon}</span>
        <span className="text-[9px] sm:text-[10px] font-bold uppercase tracking-widest text-gray-500">
          {label}
        </span>
      </div>

      <div className="flex items-center justify-between">
        <span
          className={`font-black font-mono text-gray-900 tracking-tight truncate ${
            isBottomCard ? 'text-2xl leading-none' : 'text-2xl sm:text-[26px]'
          }`}
        >
          {value}
        </span>
        <ChevronRight size={14} className="text-gray-400 shrink-0" strokeWidth={1.5} />
      </div>

      {subValue !== undefined && (
        <div className="text-[10px] font-mono text-gray-500 font-medium">
          {subValue}
        </div>
      )}
    </div>
  );
};

export default MetricCard;

