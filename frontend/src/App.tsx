import { useState, useEffect, useRef } from 'react';
import { useChess } from './hooks/useChess';
import { evaluatePosition, analyzePgn } from './services/api';
const DEMO_PGN = `[Event "Immortal Game"]
[Site "London"]
[Date "1851.06.21"]
[White "Adolf Anderssen"]
[Black "Lionel Kieseritzky"]
[Result "1-0"]

1. e4 e5 2. f4 exf4 3. Bc4 Qh4+ 4. Kf1 b5 5. Bxb5 Nf6 6. Nf3 Qh6 7. d3 Nh5 8. Nh4 Qg5 9. Nf5 c6 10. g4 Nf6 11. Rg1 cxb5 12. h4 Qg6 13. h5 Qg5 14. Qf3 Ng8 15. Bxf4 Qf6 16. Nc3 Bc5 17. Nd5 Qxb2 18. Bd6 Bxg1 19. e5 Qxa1+ 20. Ke2 Na6 21. Nxg7+ Kd8 22. Qf6+ Nxf6 23. Be7# 1-0`;
import type { PositionNode, GameHeaders, MatchSummary } from './types';

import { Sidebar } from './components/Sidebar';
import { MatchHeader } from './components/MatchHeader';
import { ChessBoard } from './components/ChessBoard';
import { BoardControls } from './components/BoardControls';
import { TelemetryPanel } from './components/TelemetryPanel';

export function App() {
  const { fen, makeMove, resetGame, setPosition } = useChess();

  const [headers, setHeaders] = useState<GameHeaders | null>(null);
  const [positions, setPositions] = useState<PositionNode[]>([]);
  const [summary, setSummary] = useState<MatchSummary | null>(null);
  const [currentPly, setCurrentPly] = useState(0);
  const [isBatchMode, setIsBatchMode] = useState(false);
  const [boardOrientation, setBoardOrientation] = useState<'white' | 'black'>('white');
  const [isLoading, setIsLoading] = useState(false);
  const [activeTab, setActiveTab] = useState<'telemetry' | 'summary'>('telemetry');

  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (isBatchMode) return;

    const fetchLiveEval = async () => {
      try {
        const res = await evaluatePosition({ fen, player_elo: 1750, ply: 20 });
        const liveNode: PositionNode = {
          ply: 0,
          move_number: 1,
          color: 'white',
          is_white: 1,
          san: 'Live',
          uci: '',
          from_sq: null,
          to_sq: null,
          fen,
          eval_cp: 0,
          cp_eval_white: (res.features.material_balance || 0) * 100,
          cp_loss: 0,
          label: 'Live Position',
          risk_prob: res.blunder_probability,
          blunder_risk_pct: res.blunder_probability * 100,
          best_move: '-',
          tactical_tension: res.features.tactical_tension,
          hanging_pieces: res.features.hanging_pieces,
          material_balance: res.features.material_balance,
          features: res.features,
        };
        setPositions([liveNode]);
        setCurrentPly(0);
      } catch (err) {
        console.error('Live evaluation failed:', err);
      }
    };
    fetchLiveEval();
  }, [fen, isBatchMode]);

  const onDrop = ({ sourceSquare, targetSquare }: { sourceSquare: string; targetSquare: string | null }) => {
    if (isBatchMode) {
      setIsBatchMode(false);
      setHeaders(null);
      setSummary(null);
    }
    return targetSquare ? makeMove(sourceSquare, targetSquare) : false;
  };

  const handleReset = () => {
    setIsBatchMode(false);
    setPositions([]);
    setHeaders(null);
    setSummary(null);
    setCurrentPly(0);
    resetGame();
  };

  const processPgnText = async (pgnText: string) => {
    setIsLoading(true);
    try {
      const data = await analyzePgn(pgnText);
      setHeaders(data.headers);
      setPositions(data.positions);
      setSummary(data.summary);
      setIsBatchMode(true);
      setCurrentPly(0);
      if (data.positions.length > 0) {
        setPosition(data.positions[0].fen);
      }
    } catch (err: unknown) {
      console.error(err);
      const message = err instanceof Error ? err.message : 'Failed to analyze PGN. Make sure backend is running.';
      alert(message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    const text = await file.text();
    await processPgnText(text);
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  const jumpToPly = (ply: number) => {
    if (!positions || positions.length === 0) return;
    const targetPly = Math.max(0, Math.min(positions.length - 1, ply));
    setCurrentPly(targetPly);
    setPosition(positions[targetPly].fen);
  };

  const activeNode: PositionNode | undefined = positions[currentPly];

  const chartData = positions.map((p) => ({
    ply: p.ply,
    risk: p.blunder_risk_pct,
    evalPawns: p.cp_eval_white / 100.0,
    label: p.label,
    san: p.san,
  }));

  const totalPlys = positions.length > 1 ? positions.length - 1 : 0;

  return (
    <div className="min-h-screen bg-[#eaedf0] text-gray-900 flex font-sans selection:bg-gray-300">
      <input
        type="file"
        accept=".pgn"
        className="hidden"
        ref={fileInputRef}
        onChange={handleFileUpload}
      />

      {/* 1. Left Sidebar */}
      <Sidebar
        isLoading={isLoading}
        isBatchMode={isBatchMode}
        positions={positions}
        currentPly={currentPly}
        onUploadClick={() => fileInputRef.current?.click()}
        onLoadDemo={() => processPgnText(DEMO_PGN)}
        onFlipBoard={() => setBoardOrientation((prev) => (prev === 'white' ? 'black' : 'white'))}
        onResetSession={handleReset}
        onSelectPly={jumpToPly}
      />

      {/* 2. Main Analytics Canvas */}
      <main className="flex-1 p-6 lg:p-7 h-screen overflow-y-auto">
        <div className="max-w-[1400px] mx-auto h-full grid grid-cols-1 xl:grid-cols-12 gap-6 lg:gap-7 items-start">
          {/* Center Column: Chessboard & Controls */}
          <div className="xl:col-span-5 flex flex-col gap-4 sm:gap-5 h-full justify-between max-w-[500px] mx-auto w-full">
            <MatchHeader headers={headers} />
            <ChessBoard
              fen={fen}
              orientation={boardOrientation}
              onPieceDrop={onDrop}
              isWhiteTurn={activeNode ? activeNode.is_white === 1 : currentPly % 2 === 0}
              onFlipBoard={() => setBoardOrientation((prev) => (prev === 'white' ? 'black' : 'white'))}
            />
            <BoardControls
              currentPly={currentPly}
              totalPlys={positions.length}
              activeNode={activeNode}
              onJumpToPly={jumpToPly}
            />
          </div>

          {/* Right Column: Telemetry Bento Box */}
          <div className="xl:col-span-7 flex flex-col h-full w-full">
            <TelemetryPanel
              activeTab={activeTab}
              setActiveTab={setActiveTab}
              activeNode={activeNode}
              chartData={chartData}
              currentPly={currentPly}
              totalPlys={totalPlys}
              onSelectPly={jumpToPly}
              summary={summary}
              headers={headers}
            />
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;
