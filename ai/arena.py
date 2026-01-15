import argparse
import math
import random
import subprocess
import time
from typing import List, Tuple, Optional

from chess_logic.board import Board
from ai.engine import ChessEngine


def pos_to_uci(pos: Tuple[int, int]) -> str:
    row, col = pos
    return f"{chr(ord('a') + col)}{row + 1}"


def uci_to_pos(uci: str) -> Tuple[int, int]:
    file_char = uci[0]
    rank_char = uci[1]
    col = ord(file_char) - ord('a')
    row = int(rank_char) - 1
    return (row, col)


def move_to_uci(move: Tuple[Tuple[int, int], Tuple[int, int]], board: Board) -> str:
    start_pos, end_pos = move
    piece = board.get_piece(start_pos)
    uci = pos_to_uci(start_pos) + pos_to_uci(end_pos)
    if piece and piece.__class__.__name__ == 'Pawn' and end_pos[0] in (0, 7):
        uci += 'q'
    return uci


def uci_to_move(uci: str) -> Tuple[Tuple[int, int], Tuple[int, int], Optional[str]]:
    start = uci_to_pos(uci[0:2])
    end = uci_to_pos(uci[2:4])
    promo = uci[4] if len(uci) > 4 else None
    return start, end, promo


class UciEngine:
    def __init__(self, path: str):
        self.proc = subprocess.Popen(
            [path],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )
        self._send('uci')
        self._read_until('uciok')
        self._send('isready')
        self._read_until('readyok')

    def _send(self, cmd: str):
        self.proc.stdin.write(cmd + '
')
        self.proc.stdin.flush()

    def _read_until(self, token: str):
        while True:
            line = self.proc.stdout.readline()
            if not line:
                raise RuntimeError('UCI engine exited unexpectedly')
            if line.strip() == token:
                return

    def set_option(self, name: str, value):
        self._send(f"setoption name {name} value {value}")

    def set_position(self, moves: List[str]):
        if moves:
            self._send('position startpos moves ' + ' '.join(moves))
        else:
            self._send('position startpos')

    def go(self, movetime_ms: int) -> str:
        self._send(f"go movetime {movetime_ms}")
        while True:
            line = self.proc.stdout.readline()
            if not line:
                raise RuntimeError('UCI engine exited unexpectedly')
            line = line.strip()
            if line.startswith('bestmove'):
                return line.split()[1]

    def quit(self):
        try:
            self._send('quit')
        finally:
            self.proc.kill()


def play_game(engine: ChessEngine, stockfish: UciEngine, engine_color: str, movetime_ms: int, max_plies: int) -> float:
    board = Board()
    board.setup_initial_position()
    moves_uci: List[str] = []
    cur_color = 'white'

    for _ in range(max_plies):
        if cur_color == engine_color:
            move = engine.get_best_move(board, cur_color, time_limit=movetime_ms / 1000.0)
            if not move:
                if board.is_in_check(cur_color):
                    return 0.0
                return 0.5
            uci = move_to_uci(move, board)
            if not board.move_piece(move[0], move[1]):
                return 0.0
            moves_uci.append(uci)
        else:
            stockfish.set_position(moves_uci)
            best = stockfish.go(movetime_ms)
            if best == '(none)':
                if board.is_in_check(cur_color):
                    return 1.0
                return 0.5
            start, end, _promo = uci_to_move(best)
            if not board.move_piece(start, end):
                return 1.0
            moves_uci.append(best)

        cur_color = 'black' if cur_color == 'white' else 'white'
        game_over, reason = board.is_game_over(cur_color)
        if game_over:
            if reason == 'checkmate':
                return 1.0 if cur_color != engine_color else 0.0
            return 0.5

    return 0.5


def estimate_elo(score: float, games: int, opponent_elo: int) -> float:
    s = score / games if games > 0 else 0.5
    s = max(0.01, min(0.99, s))
    return opponent_elo + 400.0 * math.log10(s / (1.0 - s))


def run_match(stockfish_path: str, engine_depth: int, movetime_ms: int, games_per_elo: int, elos: List[int], max_plies: int):
    engine = ChessEngine(depth=engine_depth)
    results = []

    for elo in elos:
        stockfish = UciEngine(stockfish_path)
        stockfish.set_option('Threads', 1)
        stockfish.set_option('Hash', 64)
        stockfish.set_option('UCI_LimitStrength', 'true')
        stockfish.set_option('UCI_Elo', elo)
        stockfish._send('isready')
        stockfish._read_until('readyok')

        score = 0.0
        for game in range(games_per_elo):
            engine_color = 'white' if game % 2 == 0 else 'black'
            score += play_game(engine, stockfish, engine_color, movetime_ms, max_plies)
        stockfish.quit()

        results.append((elo, score, games_per_elo))

    return results


def main():
    parser = argparse.ArgumentParser(description='Run external Elo estimate vs Stockfish.')
    parser.add_argument('--stockfish-path', required=True, help='Path to Stockfish binary')
    parser.add_argument('--depth', type=int, default=5, help='Engine search depth')
    parser.add_argument('--movetime-ms', type=int, default=200, help='Time per move in ms')
    parser.add_argument('--games-per-elo', type=int, default=20, help='Games per opponent Elo')
    parser.add_argument('--elos', type=int, nargs='+', default=[1200, 1600, 2000], help='Stockfish Elo settings')
    parser.add_argument('--max-plies', type=int, default=200, help='Max plies per game before draw')
    args = parser.parse_args()

    results = run_match(
        stockfish_path=args.stockfish_path,
        engine_depth=args.depth,
        movetime_ms=args.movetime_ms,
        games_per_elo=args.games_per_elo,
        elos=args.elos,
        max_plies=args.max_plies,
    )

    total_score = 0.0
    total_games = 0
    estimates = []

    for elo, score, games in results:
        est = estimate_elo(score, games, elo)
        estimates.append((elo, est, score, games))
        total_score += score
        total_games += games

    for elo, est, score, games in estimates:
        print(f"Stockfish Elo {elo}: score {score}/{games} -> estimate {est:.0f}")

    if total_games > 0:
        overall = sum(est * games for _, est, _, games in estimates) / total_games
        print(f"Overall estimate: {overall:.0f}")


if __name__ == '__main__':
    main()
