import type { 
  EvaluationRequest, 
  EvaluationResponse, 
  BatchEvaluationRequest, 
  PgnAnalysisResponse 
} from '../types';

const API_BASE_URL = 'http://localhost:8000/api';

export const evaluatePosition = async (req: EvaluationRequest): Promise<EvaluationResponse> => {
  const response = await fetch(`${API_BASE_URL}/evaluate`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(req),
  });

  if (!response.ok) {
    throw new Error('Network response was not ok');
  }

  return response.json();
};

export const evaluateBatch = async (req: BatchEvaluationRequest): Promise<EvaluationResponse[]> => {
  const response = await fetch(`${API_BASE_URL}/evaluate/batch`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(req),
  });
  if (!response.ok) throw new Error('Network response was not ok');
  return response.json();
};

export const analyzePgn = async (pgn: string): Promise<PgnAnalysisResponse> => {
  const response = await fetch(`${API_BASE_URL}/analyze-pgn`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ pgn }),
  });
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || 'Failed to analyze PGN');
  }
  return response.json();
};
