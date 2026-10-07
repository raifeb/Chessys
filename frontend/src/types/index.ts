export interface TelemetryData {
  material_balance: number;
  tactical_tension: number;
  hanging_pieces: number;
  king_openness: number;
  legal_moves_count: number;
  mobility_ratio: number;
  is_check: number;
  absolute_pins: number;
}

export interface PositionNode {
  ply: number;
  move_number: number;
  color: 'white' | 'black' | string;
  is_white: number;
  san: string;
  uci: string;
  from_sq: string | null;
  to_sq: string | null;
  fen: string;
  eval_cp: number;
  cp_eval_white: number;
  cp_loss: number;
  label: string;
  risk_prob: number;
  blunder_risk_pct: number;
  best_move: string;
  best_move_uci?: string | null;
  tactical_tension: number;
  hanging_pieces: number;
  material_balance: number;
  features: TelemetryData;
}

export interface GameHeaders {
  white: string;
  black: string;
  white_elo: string;
  black_elo: string;
  opening: string;
  eco: string;
  white_avatar?: string;
  black_avatar?: string;
}

export interface PlayerStats {
  accuracy: number;
  acpl: number;
  total_moves: number;
}

export interface PhaseErrors {
  Opening: number;
  Middlegame: number;
  Endgame: number;
}

export interface MatchSummary {
  white_stats: PlayerStats;
  black_stats: PlayerStats;
  white_phase_errors: PhaseErrors;
  black_phase_errors: PhaseErrors;
  narrative: string;
  opening: string;
}

export interface PgnAnalysisResponse {
  headers: GameHeaders;
  positions: PositionNode[];
  summary: MatchSummary;
}

export interface EvaluationResponse {
  blunder_probability: number;
  is_blunder: boolean;
  features: TelemetryData;
}

export interface EvaluationRequest {
  fen: string;
  player_elo: number;
  ply: number;
}

export interface BatchEvaluationRequest {
  fens: string[];
  player_elo: number;
}
