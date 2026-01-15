"""
Simple chess AI engine using minimax with alpha-beta pruning
"""
import sys
import time
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Tuple, Optional, List

current_path = Path(__file__).resolve()
project_root = current_path.parents[1]
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

from chess_logic.board import Board
from chess_logic.pieces import Pawn, Queen, Rook, Bishop, Knight
from ai.evaluator import ChessEvaluator


TT_EXACT = 0
TT_LOWER = 1
TT_UPPER = 2


@dataclass
class TTEntry:
    depth: int
    score: float
    flag: int
    best_move: Optional[Tuple[Tuple[int, int], Tuple[int, int], Optional[str]]]


class ChessEngine:
    def __init__(self, depth: int = 3):
        self.depth = depth
        self.evaluator = ChessEvaluator()
        self.nodes_searched = 0
        self.q_nodes = 0
        self.tt = {}
        self.killer_moves = []
        self.history = {}
        self.time_up = False
        self.stop_time = None
        self.MATE_SCORE = 100000

        self.use_randomness = False
        self.randomness = 0.0
        self._zobrist = self._init_zobrist()

    def _init_zobrist(self):
        rng = random.Random(0)
        piece_types = ['Pawn', 'Knight', 'Bishop', 'Rook', 'Queen', 'King']
        pieces = {
            'white': [[rng.getrandbits(64) for _ in range(64)] for _ in piece_types],
            'black': [[rng.getrandbits(64) for _ in range(64)] for _ in piece_types],
        }
        castling = {
            'white': {'K': rng.getrandbits(64), 'Q': rng.getrandbits(64)},
            'black': {'K': rng.getrandbits(64), 'Q': rng.getrandbits(64)},
        }
        en_passant = [rng.getrandbits(64) for _ in range(8)]
        side = rng.getrandbits(64)
        return {
            'pieces': pieces,
            'piece_index': {name: idx for idx, name in enumerate(piece_types)},
            'castling': castling,
            'en_passant': en_passant,
            'side': side,
        }

    def _compute_hash(self, board: Board, color: str) -> int:
        h = 0
        pieces = self._zobrist['pieces']
        piece_index = self._zobrist['piece_index']
        for row in range(8):
            for col in range(8):
                piece = board.get_piece((row, col))
                if piece:
                    idx = piece_index[piece.__class__.__name__]
                    h ^= pieces[piece.color][idx][row * 8 + col]

        if getattr(board, 'castling_rights', None):
            if board.castling_rights['white']['K']:
                h ^= self._zobrist['castling']['white']['K']
            if board.castling_rights['white']['Q']:
                h ^= self._zobrist['castling']['white']['Q']
            if board.castling_rights['black']['K']:
                h ^= self._zobrist['castling']['black']['K']
            if board.castling_rights['black']['Q']:
                h ^= self._zobrist['castling']['black']['Q']

        if getattr(board, 'en_passant_target', None):
            file_idx = board.en_passant_target[1]
            h ^= self._zobrist['en_passant'][file_idx]

        if color == 'black':
            h ^= self._zobrist['side']

        return h

    def _time_check(self):
        if self.stop_time is None:
            return False
        if time.time() >= self.stop_time:
            self.time_up = True
            return True
        return False

    def _piece_value(self, piece) -> int:
        return self.evaluator.PIECE_VALUES.get(piece.__class__.__name__, 0)

    def _is_capture(self, board: Board, move) -> bool:
        start_pos, end_pos = move[0], move[1]
        captured_piece = board.get_piece(end_pos)
        if captured_piece is not None:
            return True
        piece = board.get_piece(start_pos)
        if piece and piece.__class__.__name__ == 'Pawn':
            if getattr(board, 'en_passant_target', None) == end_pos:
                return True
        return False

    def _order_moves(self, board: Board, moves, tt_best, ply: int):
        def score_move(move):
            if tt_best and move == tt_best:
                return 1000000
            start_pos, end_pos = move[0], move[1]
            piece = board.get_piece(start_pos)
            captured = board.get_piece(end_pos)
            score = 0
            if captured is not None:
                score += 10000 + self._piece_value(captured) - self._piece_value(piece)
            if piece and piece.__class__.__name__ == 'Pawn' and end_pos[0] in (0, 7):
                score += 8000
            if self.killer_moves and ply < len(self.killer_moves) and move in self.killer_moves[ply]:
                score += 7000
            score += self.history.get(move, 0)
            return score

        return sorted(moves, key=score_move, reverse=True)

    def _evaluate_for(self, board: Board, color: str) -> float:
        base_eval = self.evaluator.evaluate_position(board)
        if self.use_randomness and self.randomness > 0:
            base_eval += random.uniform(-self.randomness, self.randomness)
        return base_eval if color == 'black' else -base_eval

    def _make_move(self, board: Board, move, color: str):
        start_pos, end_pos = move[0], move[1]
        promotion = move[2] if len(move) > 2 else None
        piece = board.get_piece(start_pos)
        captured_piece = board.get_piece(end_pos)
        old_pos = piece.position

        prev_en_passant = board.en_passant_target
        prev_castling = (
            board.castling_rights['white']['K'],
            board.castling_rights['white']['Q'],
            board.castling_rights['black']['K'],
            board.castling_rights['black']['Q'],
        )

        rook_move = None
        en_passant_capture_pos = None
        promoted_piece = None

        if (piece.__class__.__name__ == 'Pawn' and
            board.en_passant_target == end_pos and
            captured_piece is None):
            en_passant_capture_pos = (old_pos[0], end_pos[1])
            captured_piece = board.get_piece(en_passant_capture_pos)
            if captured_piece:
                board.grid[en_passant_capture_pos[0]][en_passant_capture_pos[1]] = None

        board.grid[start_pos[0]][start_pos[1]] = None

        if piece.__class__.__name__ == 'Pawn' and end_pos[0] in (0, 7):
            promo = (promotion or 'q').lower()
            if promo == 'r':
                promoted_piece = Rook(piece.color, end_pos)
            elif promo == 'b':
                promoted_piece = Bishop(piece.color, end_pos)
            elif promo == 'n':
                promoted_piece = Knight(piece.color, end_pos)
            else:
                promoted_piece = Queen(piece.color, end_pos)
            board.grid[end_pos[0]][end_pos[1]] = promoted_piece
        else:
            board.grid[end_pos[0]][end_pos[1]] = piece
            piece.position = end_pos

        if piece.__class__.__name__ == 'King' and abs(end_pos[1] - old_pos[1]) == 2:
            row = old_pos[0]
            if end_pos[1] == 6:
                rook_start = (row, 7)
                rook_end = (row, 5)
            else:
                rook_start = (row, 0)
                rook_end = (row, 3)
            rook_piece = board.get_piece(rook_start)
            if rook_piece:
                board.grid[rook_start[0]][rook_start[1]] = None
                board.grid[rook_end[0]][rook_end[1]] = rook_piece
                rook_piece.position = rook_end
                rook_move = (rook_piece, rook_start, rook_end)

        if piece.__class__.__name__ == 'King':
            board.castling_rights[piece.color]['K'] = False
            board.castling_rights[piece.color]['Q'] = False
        elif piece.__class__.__name__ == 'Rook':
            if piece.color == 'white':
                if old_pos == (0, 0):
                    board.castling_rights['white']['Q'] = False
                elif old_pos == (0, 7):
                    board.castling_rights['white']['K'] = False
            else:
                if old_pos == (7, 0):
                    board.castling_rights['black']['Q'] = False
                elif old_pos == (7, 7):
                    board.castling_rights['black']['K'] = False

        if captured_piece and captured_piece.__class__.__name__ == 'Rook':
            if captured_piece.color == 'white':
                if end_pos == (0, 0):
                    board.castling_rights['white']['Q'] = False
                elif end_pos == (0, 7):
                    board.castling_rights['white']['K'] = False
            else:
                if end_pos == (7, 0):
                    board.castling_rights['black']['Q'] = False
                elif end_pos == (7, 7):
                    board.castling_rights['black']['K'] = False

        board.en_passant_target = None
        if piece.__class__.__name__ == 'Pawn' and abs(end_pos[0] - old_pos[0]) == 2:
            mid_row = (end_pos[0] + old_pos[0]) // 2
            board.en_passant_target = (mid_row, end_pos[1])

        return (
            piece,
            captured_piece,
            old_pos,
            en_passant_capture_pos,
            rook_move,
            promoted_piece,
            prev_en_passant,
            prev_castling,
        )

    def _undo_move(self, board: Board, move, state):
        start_pos, end_pos = move[0], move[1]
        (
            piece,
            captured_piece,
            old_pos,
            en_passant_capture_pos,
            rook_move,
            promoted_piece,
            prev_en_passant,
            prev_castling,
        ) = state

        if rook_move:
            rook_piece, rook_start, rook_end = rook_move
            board.grid[rook_end[0]][rook_end[1]] = None
            board.grid[rook_start[0]][rook_start[1]] = rook_piece
            rook_piece.position = rook_start

        if promoted_piece:
            board.grid[end_pos[0]][end_pos[1]] = None
            board.grid[old_pos[0]][old_pos[1]] = piece
            piece.position = old_pos
        else:
            board.grid[end_pos[0]][end_pos[1]] = None
            board.grid[old_pos[0]][old_pos[1]] = piece
            piece.position = old_pos

        if en_passant_capture_pos and captured_piece:
            board.grid[en_passant_capture_pos[0]][en_passant_capture_pos[1]] = captured_piece
        else:
            board.grid[end_pos[0]][end_pos[1]] = captured_piece

        board.en_passant_target = prev_en_passant
        board.castling_rights['white']['K'] = prev_castling[0]
        board.castling_rights['white']['Q'] = prev_castling[1]
        board.castling_rights['black']['K'] = prev_castling[2]
        board.castling_rights['black']['Q'] = prev_castling[3]

    def get_best_move(self, board: Board, color: str, time_limit: Optional[float] = None) -> Optional[Tuple[Tuple[int, int], Tuple[int, int]]]:
        self.nodes_searched = 0
        self.q_nodes = 0
        self.time_up = False
        self.stop_time = time.time() + time_limit if time_limit else None

        if hasattr(board, 'get_legal_moves_for_color_with_promotions'):
            legal_moves = board.get_legal_moves_for_color_with_promotions(color)
        else:
            legal_moves = board.get_legal_moves_for_color(color)
        if not legal_moves:
            return None

        best_move = legal_moves[0]

        for current_depth in range(1, self.depth + 1):
            self.killer_moves = [[None, None] for _ in range(current_depth + 2)]
            self.history = {}
            alpha = -self.MATE_SCORE
            beta = self.MATE_SCORE
            score = self._search(board, current_depth, alpha, beta, color, 0)
            if self.time_up:
                break
            root_hash = self._compute_hash(board, color)
            entry = self.tt.get(root_hash)
            if entry and entry.best_move:
                best_move = entry.best_move

        print(f"AI searched {self.nodes_searched} nodes ({self.q_nodes} qnodes), best score: {score:.2f}")
        return best_move

    def _search(self, board: Board, depth: int, alpha: float, beta: float, color: str, ply: int) -> float:
        if self._time_check():
            return self._evaluate_for(board, color)

        self.nodes_searched += 1
        position_hash = self._compute_hash(board, color)
        entry = self.tt.get(position_hash)
        if entry and entry.depth >= depth:
            if entry.flag == TT_EXACT:
                return entry.score
            if entry.flag == TT_LOWER and entry.score >= beta:
                return entry.score
            if entry.flag == TT_UPPER and entry.score <= alpha:
                return entry.score

        if depth == 0:
            return self._quiescence(board, alpha, beta, color, ply)

        if hasattr(board, 'get_legal_moves_for_color_with_promotions'):
            legal_moves = board.get_legal_moves_for_color_with_promotions(color)
        else:
            legal_moves = board.get_legal_moves_for_color(color)
        if not legal_moves:
            if board.is_in_check(color):
                return -self.MATE_SCORE + ply
            return 0

        tt_best = entry.best_move if entry else None
        ordered_moves = self._order_moves(board, legal_moves, tt_best, ply)

        best_move = None
        alpha_orig = alpha
        next_color = 'white' if color == 'black' else 'black'

        for move in ordered_moves:
            state = self._make_move(board, move, color)
            score = -self._search(board, depth - 1, -beta, -alpha, next_color, ply + 1)
            self._undo_move(board, move, state)

            if self.time_up:
                return self._evaluate_for(board, color)

            if score > alpha:
                alpha = score
                best_move = move
                if alpha >= beta:
                    if not self._is_capture(board, move):
                        if ply < len(self.killer_moves):
                            killers = self.killer_moves[ply]
                            if move != killers[0]:
                                killers[1] = killers[0]
                                killers[0] = move
                        self.history[move] = self.history.get(move, 0) + depth * depth
                    break

        flag = TT_EXACT
        if alpha <= alpha_orig:
            flag = TT_UPPER
        elif alpha >= beta:
            flag = TT_LOWER

        self.tt[position_hash] = TTEntry(depth, alpha, flag, best_move)
        return alpha

    def _quiescence(self, board: Board, alpha: float, beta: float, color: str, ply: int) -> float:
        if self._time_check():
            return self._evaluate_for(board, color)

        self.q_nodes += 1
        stand_pat = self._evaluate_for(board, color)
        if stand_pat >= beta:
            return beta
        if stand_pat > alpha:
            alpha = stand_pat

        if hasattr(board, 'get_legal_moves_for_color_with_promotions'):
            legal_moves = board.get_legal_moves_for_color_with_promotions(color)
        else:
            legal_moves = board.get_legal_moves_for_color(color)
        capture_moves = [m for m in legal_moves if self._is_capture(board, m)]
        if not capture_moves:
            return alpha

        ordered_moves = self._order_moves(board, capture_moves, None, ply)
        next_color = 'white' if color == 'black' else 'black'

        for move in ordered_moves:
            state = self._make_move(board, move, color)
            score = -self._quiescence(board, -beta, -alpha, next_color, ply + 1)
            self._undo_move(board, move, state)

            if self.time_up:
                return self._evaluate_for(board, color)

            if score >= beta:
                return beta
            if score > alpha:
                alpha = score

        return alpha


if __name__ == "__main__":
    # Test the AI
    board = Board()
    board.setup_initial_position()
    engine = ChessEngine(depth=3)

    print("Initial position:")
    print(board)

    move = engine.get_best_move(board, 'black')
    if move:
        start, end = move
        print(f"AI suggests: {start} -> {end}")

        if board.move_piece(start, end):
            print("Move made successfully!")
            print(board)
        else:
            print("Move failed!")
    else:
        print("No legal moves found!")
