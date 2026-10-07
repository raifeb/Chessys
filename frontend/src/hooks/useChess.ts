import { useState, useCallback } from 'react';
import { Chess } from 'chess.js';

export const useChess = () => {
  const [game, setGame] = useState(new Chess());
  const [fen, setFen] = useState(game.fen());

  const makeMove = useCallback((sourceSquare: string, targetSquare: string) => {
    const gameCopy = new Chess(game.fen());
    try {
      const move = gameCopy.move({
        from: sourceSquare,
        to: targetSquare,
        promotion: 'q', // Always promote to queen for simplicity
      });

      if (move === null) return false;
      
      setGame(gameCopy);
      setFen(gameCopy.fen());
      return true;
    } catch (e) {
      return false;
    }
  }, [game]);

  const resetGame = useCallback(() => {
    const newGame = new Chess();
    setGame(newGame);
    setFen(newGame.fen());
  }, []);

  const loadPgn = useCallback((pgn: string) => {
    const newGame = new Chess();
    try {
      newGame.loadPgn(pgn);
      setGame(newGame);
      setFen(newGame.fen());
      return true;
    } catch {
      return false;
    }
  }, []);

  const setPosition = useCallback((newFen: string) => {
    const newGame = new Chess(newFen);
    setGame(newGame);
    setFen(newFen);
  }, []);

  return {
    game,
    fen,
    makeMove,
    resetGame,
    loadPgn,
    setPosition
  };
};
