import React, { useState } from 'react';
import type { GameHeaders } from '../types';

interface PlayerIdentityProps {
  name: string;
  rating?: string | number;
  avatarUrl?: string | null;
  side: 'white' | 'black';
  reverseLayout?: boolean;
}

const PlayerIdentity: React.FC<PlayerIdentityProps> = ({
  name,
  rating,
  avatarUrl,
  side,
  reverseLayout = false,
}) => {
  const [imgError, setImgError] = useState(false);
  const cleanUrl = avatarUrl?.trim() || null;

  const renderIndicator = () => {
    if (cleanUrl && !imgError) {
      return (
        <img
          src={cleanUrl}
          alt={name}
          onError={() => setImgError(true)}
          className="w-5 h-5 rounded-full object-cover shadow-clay-sm ring-1 ring-gray-300 shrink-0"
        />
      );
    }

    if (side === 'white') {
      return (
        <div
          className="w-3.5 h-3.5 rounded-full bg-white shadow-clay-sm border border-gray-200 shrink-0"
          title="White"
        />
      );
    }

    return (
      <div
        className="w-3.5 h-3.5 rounded-full bg-gray-900 shadow-clay-sm shrink-0"
        title="Black"
      />
    );
  };

  return (
    <div
      className={`flex items-center gap-2.5 truncate ${
        reverseLayout ? 'flex-row-reverse text-right' : 'flex-row text-left'
      }`}
    >
      {renderIndicator()}
      <div className="truncate text-xs font-bold font-mono">
        <span className="text-gray-900">{name}</span>
        {rating && <span className="text-gray-400 font-normal ml-1">({rating})</span>}
      </div>
    </div>
  );
};

interface MatchHeaderProps {
  headers: GameHeaders | null;
}

export const MatchHeader: React.FC<MatchHeaderProps> = ({ headers }) => {
  const whiteName = headers?.white || 'White';
  const blackName = headers?.black || 'Black';
  const whiteElo = headers?.white_elo || '1500';
  const blackElo = headers?.black_elo || '1500';

  return (
    <div className="h-12 bg-gray-100 rounded-full shadow-clay-pill px-6 flex items-center justify-between shrink-0 select-none">
      <div className="flex-1 min-w-0 pr-3">
        <PlayerIdentity
          name={whiteName}
          rating={whiteElo}
          avatarUrl={headers?.white_avatar}
          side="white"
        />
      </div>

      <div className="px-3 shrink-0 text-[11px] font-black text-gray-400 tracking-wider">
        VS
      </div>

      <div className="flex-1 min-w-0 pl-3 flex justify-end">
        <PlayerIdentity
          name={blackName}
          rating={blackElo}
          avatarUrl={headers?.black_avatar}
          side="black"
          reverseLayout
        />
      </div>
    </div>
  );
};

export default MatchHeader;

