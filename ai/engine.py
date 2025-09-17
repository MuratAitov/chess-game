"""
Simple chess AI engine using minimax with alpha-beta pruning
"""
import sys
from pathlib import Path
import random
from typing import Tuple, Optional, List

current_path = Path(__file__).resolve()
project_root = current_path.parents[1]
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

from chess_logic.board import Board
from ai.evaluator import ChessEvaluator


class ChessEngine:
    def __init__(self, depth: int = 3):
        self.depth = depth
        self.evaluator = ChessEvaluator()
        self.nodes_searched = 0

        # Добавляем некоторую случайность для более низких уровней сложности
        self.randomness = max(0, 4 - depth) * 0.2  # Больше случайности для меньшей глубины

    def get_best_move(self, board: Board, color: str) -> Optional[Tuple[Tuple[int, int], Tuple[int, int]]]:
        """
        Find the best move for the given color using minimax with alpha-beta pruning.
        Returns (start_pos, end_pos) or None if no moves available.
        """
        self.nodes_searched = 0
        legal_moves = board.get_legal_moves_for_color(color)

        if not legal_moves:
            return None

        best_move = None
        best_score = float('-inf') if color == 'black' else float('inf')

        # Shuffle moves to add some randomness when scores are equal
        random.shuffle(legal_moves)

        for start_pos, end_pos in legal_moves:
            # Make the move
            captured_piece = board.get_piece(end_pos)
            piece = board.get_piece(start_pos)
            old_pos = piece.position

            board.grid[start_pos[0]][start_pos[1]] = None
            board.grid[end_pos[0]][end_pos[1]] = piece
            piece.position = end_pos

            # Evaluate the position
            if color == 'black':
                score = self.minimax(board, self.depth - 1, False, float('-inf'), float('inf'))
                if score > best_score:
                    best_score = score
                    best_move = (start_pos, end_pos)
            else:
                score = self.minimax(board, self.depth - 1, True, float('-inf'), float('inf'))
                if score < best_score:
                    best_score = score
                    best_move = (start_pos, end_pos)

            # Undo the move
            board.grid[old_pos[0]][old_pos[1]] = piece
            piece.position = old_pos
            board.grid[end_pos[0]][end_pos[1]] = captured_piece

        print(f"AI searched {self.nodes_searched} nodes, best score: {best_score:.2f}")
        return best_move

    def minimax(self, board: Board, depth: int, maximizing: bool, alpha: float, beta: float) -> float:
        """
        Minimax algorithm with alpha-beta pruning.
        maximizing=True means we're maximizing for black, False means minimizing for white.
        """
        self.nodes_searched += 1

        if depth == 0:
            base_eval = self.evaluator.evaluate_position(board)
            # Добавляем случайность для более слабых уровней
            if self.randomness > 0:
                noise = random.uniform(-self.randomness, self.randomness)
                return base_eval + noise
            return base_eval

        color = 'black' if maximizing else 'white'
        legal_moves = board.get_legal_moves_for_color(color)

        # Check for terminal positions
        if not legal_moves:
            if board.is_in_check(color):
                # Checkmate - very bad for the side to move
                return -10000 if maximizing else 10000
            else:
                # Stalemate - neutral
                return 0

        if maximizing:
            max_eval = float('-inf')
            for start_pos, end_pos in legal_moves:
                # Make the move
                captured_piece = board.get_piece(end_pos)
                piece = board.get_piece(start_pos)
                old_pos = piece.position

                board.grid[start_pos[0]][start_pos[1]] = None
                board.grid[end_pos[0]][end_pos[1]] = piece
                piece.position = end_pos

                eval_score = self.minimax(board, depth - 1, False, alpha, beta)
                max_eval = max(max_eval, eval_score)

                # Undo the move
                board.grid[old_pos[0]][old_pos[1]] = piece
                piece.position = old_pos
                board.grid[end_pos[0]][end_pos[1]] = captured_piece

                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    break  # Alpha-beta pruning

            return max_eval
        else:
            min_eval = float('inf')
            for start_pos, end_pos in legal_moves:
                # Make the move
                captured_piece = board.get_piece(end_pos)
                piece = board.get_piece(start_pos)
                old_pos = piece.position

                board.grid[start_pos[0]][start_pos[1]] = None
                board.grid[end_pos[0]][end_pos[1]] = piece
                piece.position = end_pos

                eval_score = self.minimax(board, depth - 1, True, alpha, beta)
                min_eval = min(min_eval, eval_score)

                # Undo the move
                board.grid[old_pos[0]][old_pos[1]] = piece
                piece.position = old_pos
                board.grid[end_pos[0]][end_pos[1]] = captured_piece

                beta = min(beta, eval_score)
                if beta <= alpha:
                    break  # Alpha-beta pruning

            return min_eval


if __name__ == "__main__":
    # Test the AI
    board = Board()
    board.setup_initial_position()
    engine = ChessEngine(depth=3)

    print("Initial position:")
    print(board)

    # Get AI move for black
    move = engine.get_best_move(board, 'black')
    if move:
        start, end = move
        print(f"AI suggests: {start} -> {end}")

        # Make the move
        if board.move_piece(start, end):
            print("Move made successfully!")
            print(board)
        else:
            print("Move failed!")
    else:
        print("No legal moves found!")