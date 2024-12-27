# tests/test_board.py

import pytest
import sys
from pathlib import Path

current_path = Path(__file__).resolve()
project_root = current_path.parents[1]
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

print("Project Root Path:", project_root)

from chess_logic.board import Board
from chess_logic.pieces import Pawn, Rook, Knight, Bishop, Queen, King


class TestIsSquareAttacked:
    """
    Extensive test suite for Board.is_square_attacked().
    Includes 100 tests covering pawns, rooks, knights, bishops,
    queens, kings, and mixed scenarios.
    """

    def setup_method(self):
        """
        This function is called before each test method.
        Creates a fresh 8x8 board with no pieces.
        """
        self.board = Board()
        for r in range(8):
            for c in range(8):
                self.board.grid[r][c] = None

    # =========================================================================
    #                               ORIGINAL 20 TESTS
    # =========================================================================

    # 1
    def test_white_pawn_attacks_up_left(self):
        """Белая пешка на (3,3) атакует (4,2). Должно вернуться True."""
        self.board.grid[3][3] = Pawn('white', (3, 3))
        attacked = self.board.is_square_attacked((4, 2), 'white')
        assert attacked is True

    # 2
    def test_white_pawn_attacks_up_right(self):
        """Белая пешка на (3,3) атакует (4,4). Должно вернуться True."""
        self.board.grid[3][3] = Pawn('white', (3, 3))
        attacked = self.board.is_square_attacked((4, 4), 'white')
        assert attacked is True

    # 3
    def test_white_pawn_does_not_attack_forward(self):
        """Белая пешка на (3,3) НЕ атакует (2,3). Должно вернуться False."""
        self.board.grid[3][3] = Pawn('white', (3, 3))
        attacked = self.board.is_square_attacked((2, 3), 'white')
        assert attacked is False

    # 4
    def test_black_pawn_attacks_down_left(self):
        """Чёрная пешка на (4,4) атакует (3,3). Должно вернуться True."""
        self.board.grid[4][4] = Pawn('black', (4, 4))
        attacked = self.board.is_square_attacked((3, 3), 'black')
        assert attacked is True

    # 5
    def test_black_pawn_attacks_down_right(self):
        """Чёрная пешка на (4,4) атакует (3,5). Должно вернуться True."""
        self.board.grid[4][4] = Pawn('black', (4, 4))
        attacked = self.board.is_square_attacked((3, 5), 'black')
        assert attacked is True

    # 6
    def test_black_pawn_does_not_attack_forward(self):
        """Чёрная пешка на (4,4) НЕ атакует (5,4). Должно быть False."""
        self.board.grid[4][4] = Pawn('black', (4, 4))
        attacked = self.board.is_square_attacked((5, 4), 'black')
        assert attacked is False

    # 7
    def test_rook_attacks_horizontally(self):
        """
        Ладья на (3,3) должна атаковать (3,7).
        """
        self.board.grid[3][3] = Rook('white', (3, 3))
        attacked = self.board.is_square_attacked((3, 7), 'white')
        assert attacked is True

    # 8
    def test_rook_attacks_vertically(self):
        """
        Ладья на (3,3) должна атаковать (0,3).
        """
        self.board.grid[3][3] = Rook('white', (3, 3))
        attacked = self.board.is_square_attacked((0, 3), 'white')
        assert attacked is True

    # 9
    def test_rook_attack_blocked_by_piece(self):
        """
        Ладья на (3,3) НЕ атакует (3,7), если на (3,5) стоит своя же фигура.
        """
        self.board.grid[3][3] = Rook('white', (3, 3))
        self.board.grid[3][5] = Pawn('white', (3, 5))
        attacked = self.board.is_square_attacked((3, 7), 'white')
        assert attacked is False

    # 10
    def test_knight_attack_g_shape(self):
        """
        Конь на (3,3) атакует (5,4).
        """
        self.board.grid[3][3] = Knight('black', (3, 3))
        attacked = self.board.is_square_attacked((5, 4), 'black')
        assert attacked is True

    # 11
    def test_knight_attack_g_shape2(self):
        """
        Конь на (3,3) атакует (1,4).
        """
        self.board.grid[3][3] = Knight('black', (3, 3))
        attacked = self.board.is_square_attacked((1, 4), 'black')
        assert attacked is True

    # 12
    def test_king_attacks_adjacent(self):
        """
        Король на (4,4) атакует все 8 соседних клеток, проверим одну из них (3,3).
        """
        self.board.grid[4][4] = King('white', (4, 4))
        attacked = self.board.is_square_attacked((3, 3), 'white')
        assert attacked is True

    # 13
    def test_king_does_not_attack_two_away(self):
        """
        Король на (4,4) НЕ атакует (2,4).
        """
        self.board.grid[4][4] = King('white', (4, 4))
        attacked = self.board.is_square_attacked((2, 4), 'white')
        assert attacked is False

    # 14
    def test_bishop_attacks_diagonal(self):
        """
        Слон на (4,4) атакует (6,6), (2,2) и т.д. Проверим (6,6).
        """
        self.board.grid[4][4] = Bishop('white', (4, 4))
        attacked = self.board.is_square_attacked((6, 6), 'white')
        assert attacked is True

    # 15
    def test_bishop_blocked_by_own_piece(self):
        """
        Слон на (4,4) НЕ атакует (6,6), если на (5,5) своя фигура.
        """
        self.board.grid[4][4] = Bishop('white', (4, 4))
        self.board.grid[5][5] = Knight('white', (5, 5))
        attacked = self.board.is_square_attacked((6, 6), 'white')
        assert attacked is False

    # 16
    def test_queen_attacks_diagonal(self):
        """
        Ферзь на (4,4) атакует (7,7) по диагонали
        """
        self.board.grid[4][4] = Queen('black', (4, 4))
        attacked = self.board.is_square_attacked((7, 7), 'black')
        assert attacked is True

    # 17
    def test_queen_attacks_straight(self):
        """
        Ферзь на (4,4) атакует (4,0) по горизонтали
        """
        self.board.grid[4][4] = Queen('black', (4, 4))
        attacked = self.board.is_square_attacked((4, 0), 'black')
        assert attacked is True

    # 18
    def test_position_out_of_bounds_returns_false(self):
        """
        Если проверяем клетку за границами доски — ожидаем False.
        """
        attacked = self.board.is_square_attacked((8, 8), 'white')
        assert attacked is False

    # 19
    def test_empty_board_any_square_not_attacked(self):
        """
        На пустой доске никакая клетка не может быть атакована.
        """
        attacked = self.board.is_square_attacked((3, 3), 'white')
        assert attacked is False

    # 20
    def test_multiple_attackers_still_true(self):
        """
        Если клетку (3,3) атакуют сразу несколько фигур (две ладьи),
        is_square_attacked() всё равно должен вернуть True.
        """
        self.board.grid[3][0] = Rook('black', (3, 0))
        self.board.grid[3][7] = Rook('black', (3, 7))
        attacked = self.board.is_square_attacked((3, 3), 'black')
        assert attacked is True

    # =========================================================================
    #                           ADDITIONAL 80 TESTS
    # =========================================================================
    #
    # We'll add more scenarios covering corners, blocking, edges, multiple pieces,
    # advanced patterns, etc. Each test is enumerated from #21 to #100.

    # -------------------- 21-30: Additional Pawn Tests --------------------

    # 21
    def test_white_pawn_attacks_from_edge_left_side(self):
        """
        White pawn at (3,0). Checks if (4,-1) is attacked => out of bounds => False,
        but (4,1) => True if within board.
        We'll check (4,1).
        """
        self.board.grid[3][0] = Pawn('white', (3, 0))
        attacked = self.board.is_square_attacked((4, 1), 'white')
        assert attacked is True

    # 22
    def test_white_pawn_on_last_rank_does_not_attack_off_board(self):
        """
        White pawn at (7,3) can't go further up (no row 8).
        Checking (8,2) or (8,4) => out of bounds => False.
        We'll check (8,2).
        """
        self.board.grid[7][3] = Pawn('white', (7, 3))
        attacked = self.board.is_square_attacked((8, 2), 'white')
        assert attacked is False

    # 23
    def test_black_pawn_on_first_rank_does_not_attack_off_board(self):
        """
        Black pawn at (0,3). 
        The squares (negative row => out of bounds).
        Checking ( -1, 2 ) => out of bounds => False
        """
        self.board.grid[0][3] = Pawn('black', (0, 3))
        attacked = self.board.is_square_attacked((-1, 2), 'black')
        assert attacked is False

    # 24
    def test_white_pawn_in_corner_attacks_only_one_diagonal(self):
        """
        White pawn at (2,7), top-right corner from that perspective.
        Attacks (3,6) if within board => True, but (3,8) => out of bounds => check False
        We'll check (3,6).
        """
        self.board.grid[2][7] = Pawn('white', (2, 7))
        attacked = self.board.is_square_attacked((3, 6), 'white')
        assert attacked is True

    # 25
    def test_black_pawn_in_corner_attacks_only_one_diagonal(self):
        """
        Black pawn at (5,7).
        Attacks (4,6) => True if in range, (4,8) => out of bounds => check if False.
        We'll check (4,6).
        """
        self.board.grid[5][7] = Pawn('black', (5, 7))
        attacked = self.board.is_square_attacked((4, 6), 'black')
        assert attacked is True

    # 26
    def test_pawn_blocked_by_piece_does_not_change_attack_logic(self):
        """
        White pawn at (3,3) with own piece in front (2,3).
        Attack squares are still (4,2) and (4,4) in `is_square_attacked` sense.
        We'll check (4,2) => True, forward block doesn't affect diagonal attack.
        """
        self.board.grid[3][3] = Pawn('white', (3, 3))
        self.board.grid[2][3] = Rook('white', (2, 3))  # blocking forward
        attacked = self.board.is_square_attacked((4, 2), 'white')
        assert attacked is True

    # 27
    def test_white_pawn_diagonal_capture_opponent_piece_presence_or_not(self):
        """
        'is_square_attacked' doesn't require an actual piece to be there,
        just the potential attack path. So even if (4,4) is empty, 
        white pawn on (3,3) => (4,4) attacked = True.
        """
        self.board.grid[3][3] = Pawn('white', (3, 3))
        attacked = self.board.is_square_attacked((4, 4), 'white')
        assert attacked is True

    # 28
    def test_black_pawn_diagonal_capture_opponent_piece_presence_or_not(self):
        """
        Same logic for black pawn. 
        Black pawn at (4,4) => checks (3,3) and (3,5).
        We'll check (3,3) => True, even if empty.
        """
        self.board.grid[4][4] = Pawn('black', (4, 4))
        attacked = self.board.is_square_attacked((3, 3), 'black')
        assert attacked is True

    # 29
    def test_white_pawn_at_second_rank_does_not_attack_two_forward(self):
        """
        This is a movement rule scenario, but let's confirm the 'attack' squares
        are unaffected by the possibility of moving 2 squares forward. 
        White pawn at (6,3) => only diagonal squares attacked => (7,2) and (7,4).
        We'll check (7,2) => True, (8,3) => not relevant to attack.
        """
        self.board.grid[6][3] = Pawn('white', (6, 3))
        attacked = self.board.is_square_attacked((7, 2), 'white')
        assert attacked is True

    # 30
    def test_black_pawn_at_second_rank_attack_check(self):
        """
        Black pawn at (1,3). 
        Attack squares => (2,2) and (2,4).
        We'll check (2,4) => True.
        """
        self.board.grid[1][3] = Pawn('black', (1, 3))
        attacked = self.board.is_square_attacked((2, 4), 'black')
        assert attacked is True

    # -------------------- 31-40: Additional Rook Tests --------------------

    # 31
    def test_rook_on_edge_attacks_along_row_only(self):
        """
        Rook at (0,0). 
        Attacks (0,1), (0,2), ... (0,7) horizontally, 
        and (1,0), (2,0), ... (7,0) vertically.
        We'll check (0,7) => True, (7,0) => True.
        """
        self.board.grid[0][0] = Rook('white', (0, 0))
        assert self.board.is_square_attacked((0, 7), 'white') is True
        assert self.board.is_square_attacked((7, 0), 'white') is True

    # 32
    def test_rook_blocked_by_same_color_immediately(self):
        """
        Rook at (0,0), own Pawn at (0,1).
        Then (0,2) => not attacked, because the rook is blocked at (0,1).
        """
        self.board.grid[0][0] = Rook('white', (0, 0))
        self.board.grid[0][1] = Pawn('white', (0, 1))
        attacked = self.board.is_square_attacked((0, 2), 'white')
        assert attacked is False

    # 33
    def test_rook_blocked_by_opponent_color_immediately(self):
        """
        Rook at (0,0), opponent Pawn at (0,1).
        Then (0,2) => not attacked. 
        But (0,1) => attacked, because it's an opponent piece on that square.
        """
        self.board.grid[0][0] = Rook('white', (0, 0))
        self.board.grid[0][1] = Pawn('black', (0, 1))
        assert self.board.is_square_attacked((0, 1), 'white') is True
        assert self.board.is_square_attacked((0, 2), 'white') is False

    # 34
    def test_rook_vertical_attack_several_spaces(self):
        """
        Rook at (1,3). 
        Attacks up to (0,3), and down to (2,3), (3,3), (4,3), etc. 
        We'll check (7,3).
        """
        self.board.grid[1][3] = Rook('black', (1, 3))
        attacked = self.board.is_square_attacked((7, 3), 'black')
        assert attacked is True

    # 35
    def test_two_rooks_of_same_color_both_attack_same_square(self):
        """
        Rooks at (1,3) and (1,7). 
        Square (1,5) => attacked by both. Only need one => True.
        """
        self.board.grid[1][3] = Rook('white', (1, 3))
        self.board.grid[1][7] = Rook('white', (1, 7))
        attacked = self.board.is_square_attacked((1, 5), 'white')
        assert attacked is True

    # 36
    def test_rook_in_center_unblocked_attacks_many_squares(self):
        """
        Rook at (4,4). 
        Some random checks: (4,0), (4,7), (0,4), (7,4) => all True if no block.
        """
        self.board.grid[4][4] = Rook('white', (4, 4))
        assert self.board.is_square_attacked((4, 0), 'white') is True
        assert self.board.is_square_attacked((4, 7), 'white') is True
        assert self.board.is_square_attacked((0, 4), 'white') is True
        assert self.board.is_square_attacked((7, 4), 'white') is True

    # 37
    def test_rook_blocked_in_middle_line(self):
        """
        Rook at (4,4), same-color Pawn at (4,6).
        Then (4,7) => not attacked. (4,6) => attacked if it's an opponent; 
        but it's same color => still blocks. 
        """
        self.board.grid[4][4] = Rook('white', (4, 4))
        self.board.grid[4][6] = Pawn('white', (4, 6))
        assert self.board.is_square_attacked((4, 7), 'white') is False

    # 38
    def test_rook_opponent_piece_block(self):
        """
        Rook at (4,4), black Pawn at (4,6) but let's say the rook is also black => can't pass it.
        Actually if it's the same color (black) => it's a block. 
        We'll flip it: Rook=white, Pawn=black at (4,6).
        Then (4,7) => not attacked. (4,6) => attacked, yes.
        """
        self.board.grid[4][4] = Rook('white', (4, 4))
        self.board.grid[4][6] = Pawn('black', (4, 6))
        assert self.board.is_square_attacked((4, 7), 'white') is False
        assert self.board.is_square_attacked((4, 6), 'white') is True

    # 39
    def test_rook_attack_along_positive_diagonal_is_false(self):
        """
        Rook doesn't attack diagonals. Rook at (3,3).
        is_square_attacked((4,4), 'white') => False
        """
        self.board.grid[3][3] = Rook('white', (3, 3))
        attacked = self.board.is_square_attacked((4, 4), 'white')
        assert attacked is False

    # 40
    def test_rook_attack_along_knight_move_is_false(self):
        """
        Rook at (3,3), check if (5,4) is attacked => that would be a knight move => False.
        """
        self.board.grid[3][3] = Rook('black', (3, 3))
        attacked = self.board.is_square_attacked((5, 4), 'black')
        assert attacked is False

    # -------------------- 41-50: Additional Knight Tests --------------------

    # 41
    def test_knight_on_edge_misses_off_board_moves(self):
        """
        Knight at (0,0). Potential moves include negative indices => out of bounds => skip.
        Let's check (2,1) => True, (1,2) => True, (2,-1) => out => False, etc.
        """
        self.board.grid[0][0] = Knight('white', (0, 0))
        assert self.board.is_square_attacked((2, 1), 'white') is True
        assert self.board.is_square_attacked((1, 2), 'white') is True
        assert self.board.is_square_attacked((2, -1), 'white') is False

    # 42
    def test_knight_on_corner_attacks_two_squares(self):
        """
        Knight at (7,7). 
        Potential moves: (5,6), (6,5). Check those => True.
        (8,5), etc. => out of bounds => False.
        """
        self.board.grid[7][7] = Knight('black', (7, 7))
        assert self.board.is_square_attacked((5, 6), 'black') is True
        assert self.board.is_square_attacked((6, 5), 'black') is True
        assert self.board.is_square_attacked((8, 5), 'black') is False

    # 43
    def test_knight_jumps_over_pieces_unaffected(self):
        """
        Knight at (3,3), own or enemy piece at (4,3) or (3,4) doesn't matter. 
        Knight can still jump to (5,4), etc. We'll confirm (5,4).
        """
        self.board.grid[3][3] = Knight('white', (3, 3))
        self.board.grid[4][3] = Pawn('white', (4, 3))  # same color blocking in front
        attacked = self.board.is_square_attacked((5, 4), 'white')
        assert attacked is True

    # 44
    def test_knight_center_attacks_8_positions(self):
        """
        Knight at (4,4). Check each of 8 possible moves in-bounds => True.
        We'll test (6,5), (6,3), (5,6), (5,2) for instance.
        """
        self.board.grid[4][4] = Knight('black', (4, 4))
        assert self.board.is_square_attacked((6, 5), 'black') is True
        assert self.board.is_square_attacked((6, 3), 'black') is True
        assert self.board.is_square_attacked((5, 6), 'black') is True
        assert self.board.is_square_attacked((5, 2), 'black') is True

    # 45
    def test_knight_cannot_attack_diagonally_one_square(self):
        """
        Knight at (3,3). 
        Check if (4,4) is attacked => that's a bishop/king move => should be False.
        """
        self.board.grid[3][3] = Knight('white', (3, 3))
        attacked = self.board.is_square_attacked((4, 4), 'white')
        assert attacked is False

    # 46
    def test_knight_cannot_attack_straight_line(self):
        """
        Knight at (2,2). 
        Check if (2,3) is attacked => that would be a rook step => False.
        """
        self.board.grid[2][2] = Knight('black', (2, 2))
        attacked = self.board.is_square_attacked((2, 3), 'black')
        assert attacked is False

    # 47
    def test_knight_blocks_do_not_matter_example_2(self):
        """
        Knight at (2,2), own rook at (3,3). 
        Checking if (4,4) is attacked => yes, if it's a valid 'L' move. 
        Actually (4,4) is not an L from (2,2). So it's False.
        But let's check (4,3) => True if it's a valid L from (2,2)? (2->4 = +2, 2->3=+1 => yes).
        """
        self.board.grid[2][2] = Knight('white', (2, 2))
        self.board.grid[3][3] = Rook('white', (3, 3))
        attacked = self.board.is_square_attacked((4, 3), 'white')
        assert attacked is True

    # 48
    def test_knight_does_not_attack_off_knight_shape(self):
        """
        Knight at (2,2). 
        Checking random squares that aren't a knight's move: (4,2), (3,2), (0,2), etc. => False
        """
        self.board.grid[2][2] = Knight('black', (2, 2))
        assert self.board.is_square_attacked((4, 2), 'black') is False
        assert self.board.is_square_attacked((3, 2), 'black') is False

    # 49
    def test_knight_multiple_check_all_must_be_true(self):
        """
        Knight at (4,4). We'll test many squares: 
        (6,5), (6,3), (2,5), (2,3), (5,6), (5,2), (3,6), (3,2).
        All => True if in bounds.
        """
        self.board.grid[4][4] = Knight('white', (4, 4))
        squares = [(6,5), (6,3), (2,5), (2,3), (5,6), (5,2), (3,6), (3,2)]
        for sq in squares:
            assert self.board.is_square_attacked(sq, 'white') is True

    # 50
    def test_knight_in_corner_blocked_all_but_two_moves(self):
        """
        Knight at (0,7). 
        Potential L-moves => (2,6), (1,5) => in-bounds => True, others => out-of-bounds => False
        """
        self.board.grid[0][7] = Knight('black', (0, 7))
        assert self.board.is_square_attacked((2,6), 'black') is True
        assert self.board.is_square_attacked((1,5), 'black') is True
        # Let's confirm out-of-bounds like (2,8), (1,9) => obviously not tested by is_square_attacked
        # since that's outside board. No explicit check needed.

    # -------------------- 51-60: Additional Bishop Tests --------------------

    # 51
    def test_bishop_on_edge_attacks_diagonal_inwards(self):
        """
        Bishop at (0,0). 
        Attacks (1,1), (2,2), (3,3), etc., if unblocked.
        We'll check (3,3) => True.
        """
        self.board.grid[0][0] = Bishop('white', (0, 0))
        assert self.board.is_square_attacked((3,3), 'white') is True

    # 52
    def test_bishop_opposite_edge_blocked_by_opponent(self):
        """
        Bishop at (7,7). 
        Suppose there's an opponent piece at (5,5).
        Then squares beyond (5,5) on that diagonal => not attacked. For example (4,4) => not reached.
        Actually, the bishop "would" pass over (6,6). Let's set up carefully:
          - Opponent at (6,6) => that blocks further squares like (5,5).
        We'll test (5,5) => False, but (6,6) => True (since it's an opponent piece).
        """
        self.board.grid[7][7] = Bishop('white', (7, 7))
        self.board.grid[6][6] = Pawn('black', (6, 6))  # block
        assert self.board.is_square_attacked((6,6), 'white') is True
        assert self.board.is_square_attacked((5,5), 'white') is False

    # 53
    def test_bishop_center_attacks_all_four_diagonals(self):
        """
        Bishop at (4,4). We'll check random squares: (5,5), (6,6), (3,3), (2,2),
        (5,3), (3,5) => all True if unblocked.
        """
        self.board.grid[4][4] = Bishop('black', (4, 4))
        for sq in [(5,5), (6,6), (3,3), (2,2), (5,3), (3,5)]:
            assert self.board.is_square_attacked(sq, 'black') is True

    # 54
    def test_bishop_cannot_attack_straight_line(self):
        """
        Bishop at (4,4). Checking (4,5) => rook/queen line => should be False.
        """
        self.board.grid[4][4] = Bishop('white', (4, 4))
        attacked = self.board.is_square_attacked((4, 5), 'white')
        assert attacked is False

    # 55
    def test_bishop_blocked_after_opponent_piece_on_diagonal(self):
        """
        Bishop at (2,2), black Pawn at (3,3).
        Then (4,4) => not attacked, because the bishop can't pass the opponent at (3,3).
        But (3,3) => is attacked (since it's an opponent piece).
        """
        self.board.grid[2][2] = Bishop('white', (2, 2))
        self.board.grid[3][3] = Pawn('black', (3, 3))
        assert self.board.is_square_attacked((3,3), 'white') is True
        assert self.board.is_square_attacked((4,4), 'white') is False

    # 56
    def test_bishop_no_attack_with_slight_offset(self):
        """
        Bishop at (2,2). Checking (4,3) => not on perfect diagonal => False
        """
        self.board.grid[2][2] = Bishop('black', (2, 2))
        attacked = self.board.is_square_attacked((4, 3), 'black')
        assert attacked is False

    # 57
    def test_two_bishops_same_diagonal_different_colors(self):
        """
        White bishop at (2,2), black bishop at (4,4).
        Checking is_square_attacked((4,4), 'white') => True
        Checking is_square_attacked((2,2), 'black') => True
        They mutually attack each other if nothing else in between.
        """
        self.board.grid[2][2] = Bishop('white', (2, 2))
        self.board.grid[4][4] = Bishop('black', (4, 4))
        assert self.board.is_square_attacked((4,4), 'white') is True
        assert self.board.is_square_attacked((2,2), 'black') is True

    # 58
    def test_bishop_far_corner_block(self):
        """
        Bishop at (7,0). Opponent piece at (6,1). That blocks further squares e.g. (5,2).
        We'll check (5,2) => False, (6,1) => True (opponent).
        """
        self.board.grid[7][0] = Bishop('white', (7, 0))
        self.board.grid[6][1] = Pawn('black', (6, 1))
        assert self.board.is_square_attacked((6,1), 'white') is True
        assert self.board.is_square_attacked((5,2), 'white') is False

    # 59
    def test_bishop_on_same_color_squares_diagonal_logic(self):
        """
        A bishop on a light square can only stay on light squares, so it never attacks dark squares.
        Let's do a quick example: bishop at (0,0) => a dark square if we consider 0,0 = black. 
        Actually let's not assume color of squares, but logically it won't attack (1,2).
        We'll check (1,2) => false. (2,2) => true.
        """
        self.board.grid[0][0] = Bishop('black', (0, 0))
        assert self.board.is_square_attacked((2,2), 'black') is True
        assert self.board.is_square_attacked((1,2), 'black') is False

    # 60
    def test_bishop_multiple_capture_possibilities(self):
        """
        Bishop at (4,4). 
        Opponent pieces at (6,6) and (2,2).
        Both squares => True if no block.
        """
        self.board.grid[4][4] = Bishop('white', (4, 4))
        self.board.grid[6][6] = Rook('black', (6, 6))
        self.board.grid[2][2] = Knight('black', (2, 2))
        assert self.board.is_square_attacked((6,6), 'white') is True
        assert self.board.is_square_attacked((2,2), 'white') is True

    # -------------------- 61-70: Additional Queen Tests --------------------

    # 61
    def test_queen_center_combines_rook_bishop_attacks(self):
        """
        Queen at (4,4). 
        Check some squares: 
           diagonal => (6,6) => True
           straight => (4,7) => True
        """
        self.board.grid[4][4] = Queen('black', (4, 4))
        assert self.board.is_square_attacked((6,6), 'black') is True
        assert self.board.is_square_attacked((4,7), 'black') is True

    # 62
    def test_queen_blocked_in_diagonal_direction(self):
        """
        Queen at (4,4). Opponent piece at (6,6). 
        Then (7,7) => not attacked.
        But (6,6) => attacked => True
        """
        self.board.grid[4][4] = Queen('white', (4, 4))
        self.board.grid[6][6] = Pawn('black', (6, 6))
        assert self.board.is_square_attacked((6,6), 'white') is True
        assert self.board.is_square_attacked((7,7), 'white') is False

    # 63
    def test_queen_blocked_in_straight_direction(self):
        """
        Queen at (4,4). Same-color piece at (4,6).
        Then (4,7) => not attacked. (4,6) => not an enemy, so no 'capture', 
        but in is_square_attacked logic, it doesn't matter if it's same or enemy => it blocks further squares.
        """
        self.board.grid[4][4] = Queen('black', (4, 4))
        self.board.grid[4][6] = Knight('black', (4, 6))
        assert self.board.is_square_attacked((4, 7), 'black') is False

    # 64
    def test_queen_diagonal_vs_straight_precedence(self):
        """
        There's no real precedence, but let's confirm queen can do both. 
        Place queen at (2,2), check (2,7) => horizontal => True if unblocked,
        check (7,2) => vertical => True if unblocked,
        check (5,5) => diagonal => True if unblocked.
        We'll do them all.
        """
        self.board.grid[2][2] = Queen('white', (2, 2))
        assert self.board.is_square_attacked((2, 7), 'white') is True
        assert self.board.is_square_attacked((7, 2), 'white') is True
        assert self.board.is_square_attacked((5, 5), 'white') is True

    # 65
    def test_queen_cannot_jump_over_same_color_piece_in_line(self):
        """
        Queen at (2,2), own bishop at (2,4). Then (2,5) => not attacked.
        """
        self.board.grid[2][2] = Queen('black', (2, 2))
        self.board.grid[2][4] = Bishop('black', (2, 4))
        assert self.board.is_square_attacked((2, 5), 'black') is False

    # 66
    def test_queen_cannot_jump_over_opponent_in_line(self):
        """
        Queen at (2,2), opponent bishop at (2,4). Then (2,5) => not attacked,
        but (2,4) => attacked => True.
        """
        self.board.grid[2][2] = Queen('white', (2, 2))
        self.board.grid[2][4] = Bishop('black', (2, 4))
        assert self.board.is_square_attacked((2, 4), 'white') is True
        assert self.board.is_square_attacked((2, 5), 'white') is False

    # 67
    def test_queen_on_corner_attacks_entire_rank_file_diagonal(self):
        """
        Queen at (0,7). 
        - Rank: (0,0)...(0,6) => True
        - File: (1,7)...(7,7) => True
        - Diagonal: (1,6), (2,5), ...
        We'll just check (4,3) => diagonal => True if unblocked, 
        and (0,0) => horizontal => True, (7,7) => vertical => True
        """
        self.board.grid[0][7] = Queen('black', (0, 7))
        assert self.board.is_square_attacked((0, 0), 'black') is True
        assert self.board.is_square_attacked((7, 7), 'black') is True
        assert self.board.is_square_attacked((4, 3), 'black') is True

    # 68
    def test_queen_in_front_of_opponent_king(self):
        """
        Queen at (4,4), black King at (4,7).
        If unblocked, (4,7) is attacked by the queen => True
        """
        self.board.grid[4][4] = Queen('white', (4, 4))
        self.board.grid[4][7] = King('black', (4, 7))
        attacked = self.board.is_square_attacked((4, 7), 'white')
        assert attacked is True

    # 69
    def test_queen_with_multiple_possible_takes(self):
        """
        Queen at (4,4), black rooks at (4,2) and (6,6). 
        Both squares => True if no block in between.
        We'll place them so they don't block each other: (4,2) is horizontal, (6,6) diagonal.
        """
        self.board.grid[4][4] = Queen('white', (4, 4))
        self.board.grid[4][2] = Rook('black', (4, 2))
        self.board.grid[6][6] = Rook('black', (6, 6))
        assert self.board.is_square_attacked((4, 2), 'white') is True
        assert self.board.is_square_attacked((6, 6), 'white') is True

    # 70
    def test_queen_not_knight_move(self):
        """
        Queen at (3,3). Checking (5,4) => that would be a knight move => false for queen.
        """
        self.board.grid[3][3] = Queen('black', (3, 3))
        assert self.board.is_square_attacked((5, 4), 'black') is False

    # -------------------- 71-80: Additional King Tests --------------------

    # 71
    def test_king_on_edge_limited_moves(self):
        """
        King at (0,0). Attacks (1,0), (1,1), (0,1) => True if in bounds.
        Checking (1,1) => True
        """
        self.board.grid[0][0] = King('white', (0, 0))
        assert self.board.is_square_attacked((1,1), 'white') is True

    # 72
    def test_king_on_corner_ultra_limited(self):
        """
        King at (7,7). Attacks (6,7), (6,6), (7,6).
        Checking (6,7), (6,6), (7,6) => True. Off-board => false automatically.
        """
        self.board.grid[7][7] = King('black', (7, 7))
        for sq in [(6,7), (7,6), (6,6)]:
            assert self.board.is_square_attacked(sq, 'black') is True

    # 73
    def test_king_blocked_by_own_piece_doesnt_affect_attack_squares(self):
        """
        'is_square_attacked' doesn't care if the king can actually move or if it's blocked.
        If the square is adjacent, it's considered attacked. 
        E.g. King at (4,4), own Pawn at (3,3). (3,3) => still attacked, but in real chess you can't capture your own piece. 
        For is_square_attacked, it's considered.
        """
        self.board.grid[4][4] = King('white', (4, 4))
        self.board.grid[3][3] = Pawn('white', (3, 3))  # same color
        attacked = self.board.is_square_attacked((3, 3), 'white')
        assert attacked is True

    # 74
    def test_king_not_attacking_two_squares_diagonally(self):
        """
        King at (3,3). 
        Checking (5,5) => definitely more than 1 step away => False
        """
        self.board.grid[3][3] = King('black', (3, 3))
        attacked = self.board.is_square_attacked((5, 5), 'black')
        assert attacked is False

    # 75
    def test_king_attacks_8_positions_in_center(self):
        """
        King at (4,4). The 8 squares around it => True.
        We'll just spot-check (5,5), (3,3), (4,5), (5,3).
        """
        self.board.grid[4][4] = King('white', (4, 4))
        check_squares = [(5,5), (3,3), (4,5), (5,3)]
        for sq in check_squares:
            assert self.board.is_square_attacked(sq, 'white') is True

    # 76
    def test_king_adjacent_to_opponent_king_mutual_attack(self):
        """
        White king at (4,4), black king at (5,5). 
        White attacks (5,5)? Only 1 diagonal step => True.
        Black attacks (4,4)? Same logic => True.
        (In real chess, kings can't stand adjacent legally, but for is_square_attacked logic, it's possible.)
        """
        self.board.grid[4][4] = King('white', (4, 4))
        self.board.grid[5][5] = King('black', (5, 5))
        assert self.board.is_square_attacked((5,5), 'white') is True
        assert self.board.is_square_attacked((4,4), 'black') is True

    # 77
    def test_king_on_same_rank_checks_adjacent_files(self):
        """
        King at (4,4), checking (4,3) and (4,5) => True
        """
        self.board.grid[4][4] = King('black', (4, 4))
        assert self.board.is_square_attacked((4,3), 'black') is True
        assert self.board.is_square_attacked((4,5), 'black') is True

    # 78
    def test_king_on_same_file_checks_adjacent_ranks(self):
        """
        King at (2,2), checking (1,2) and (3,2) => True
        """
        self.board.grid[2][2] = King('white', (2, 2))
        assert self.board.is_square_attacked((1,2), 'white') is True
        assert self.board.is_square_attacked((3,2), 'white') is True

    # 79
    def test_king_does_not_attack_knightlike_moves(self):
        """
        King at (3,3). Checking (5,4) => knight shape => False
        """
        self.board.grid[3][3] = King('black', (3, 3))
        assert self.board.is_square_attacked((5,4), 'black') is False

    # 80
    def test_king_does_not_attack_two_steps_horizontal(self):
        """
        King at (3,3). Checking (3,5) => 2 squares horizontally => False
        """
        self.board.grid[3][3] = King('white', (3, 3))
        assert self.board.is_square_attacked((3,5), 'white') is False

    # -------------------- 81-90: Mixed / Complex Scenarios --------------------

    # 81
    def test_mixed_simple_case_white_rook_black_bishop_on_board(self):
        """
        White rook at (0,0), black bishop at (1,1).
        - (0,1) => attacked by rook? True
        - (1,1) => attacked by rook? True (same file or rank? Actually no -> it's diagonal. Wait:
            from (0,0) to (1,1) is diagonal => rook can't do that. So => False
        - black bishop at (1,1) => checks (0,0)? => diagonal => True
        So we test carefully.
        """
        self.board.grid[0][0] = Rook('white', (0, 0))
        self.board.grid[1][1] = Bishop('black', (1, 1))

        # (0,1) => same rank => True
        assert self.board.is_square_attacked((0,1), 'white') is True
        # (1,1) => diagonal => rook => False
        assert self.board.is_square_attacked((1,1), 'white') is False
        # black bishop => does (0,0) => diagonal => True
        assert self.board.is_square_attacked((0,0), 'black') is True

    # 82
    def test_mixed_knight_bishop_king_center(self):
        """
        White knight at (3,3), black bishop at (4,4), black king at (5,4).
        - White attacks (5,4)? Knight from (3,3)->(5,4) => True
        - black bishop at (4,4) attacks (3,3)? => yes diagonal => True
        - black king at (5,4) => attacks (4,3)? => True? It's diagonally adjacent => no, that's 1 row difference and 1 col difference => yes => True
        """
        self.board.grid[3][3] = Knight('white', (3, 3))
        self.board.grid[4][4] = Bishop('black', (4, 4))
        self.board.grid[5][4] = King('black', (5, 4))

        assert self.board.is_square_attacked((5,4), 'white') is True   # knight jump
        assert self.board.is_square_attacked((3,3), 'black') is True   # bishop diagonal
        assert self.board.is_square_attacked((4,3), 'black') is True   # king adjacency

    # 83
    def test_mixed_rook_and_queen_blocking_each_other(self):
        """
        White rook at (4,0), white queen at (4,2). black bishop at (4,4).
        - The queen blocks the rook from seeing (4,4).
        So is (4,4) attacked by white? Possibly from the queen if unblocked?
        Actually queen is at (4,2), it can see (4,3), (4,4) => yes, unless there's something at (4,3).
        We'll place an additional piece at (4,3).
        """
        self.board.grid[4][0] = Rook('white', (4, 0))
        self.board.grid[4][2] = Queen('white', (4, 2))
        self.board.grid[4][3] = Knight('white', (4, 3))  # block
        self.board.grid[4][4] = Bishop('black', (4, 4))

        # (4,4) => attacked by rook? No, blocked at (4,2) or (4,3).
        # (4,4) => attacked by queen? Also blocked at (4,3).
        assert self.board.is_square_attacked((4,4), 'white') is False

    # 84
    def test_mixed_several_white_pieces_black_king_in_check(self):
        """
        White rook at (0,3), white bishop at (2,1), black king at (1,3).
        Rook from (0,3) => attacks (1,3) => same file => True
        bishop at (2,1) => not relevant for that square maybe, but let's confirm diagonal => (1,3)? 
        That would be offset (1,3)->(2,1) => difference is (1,2), not same diagonal => false for bishop.
        """
        self.board.grid[0][3] = Rook('white', (0, 3))
        self.board.grid[2][1] = Bishop('white', (2, 1))
        self.board.grid[1][3] = King('black', (1, 3))

        assert self.board.is_square_attacked((1,3), 'white') is True

    # 85
    def test_mixed_multiple_pieces_on_board_no_attack_example(self):
        """
        White knight at (0,0), white bishop at (7,7), black rook at (7,0).
        Check if (3,3) is attacked by white => Knight from (0,0)? Possibly, but (3,3) is not an L from (0,0).
        Bishop at (7,7) => (3,3)? It's diagonal => yes if no block.
          Actually it is diagonal. Let's see if there's a block. We'll place a random piece in between, say (5,5).
        """
        self.board.grid[0][0] = Knight('white', (0, 0))
        self.board.grid[7][7] = Bishop('white', (7, 7))
        self.board.grid[7][0] = Rook('black', (7, 0))
        # add a block in bishop's path
        self.board.grid[5][5] = Pawn('white', (5, 5))

        assert self.board.is_square_attacked((3,3), 'white') is False
        # Because bishop is blocked by the pawn at (5,5).

    # 86
    def test_mixed_two_knights_one_bishop_various_attacks(self):
        """
        White knight at (2,5), black knight at (3,3), black bishop at (5,1).
        We'll test some squares for each color:
        - White attacks (4,6)? Knight from (2,5) => 2 up, 1 right => yes => True
        - Black attacks (1,2)? Knight from (3,3) => 2 down, 1 left => yes => True
        - Black bishop at (5,1) => let's see if (3,3) is attacked => diagonal => yes => True
        """
        self.board.grid[2][5] = Knight('white', (2, 5))
        self.board.grid[3][3] = Knight('black', (3, 3))
        self.board.grid[5][1] = Bishop('black', (5, 1))

        assert self.board.is_square_attacked((4,6), 'white') is True
        assert self.board.is_square_attacked((1,2), 'black') is True
        # bishop(5,1) => (3,3) is diagonal if difference is (2,2) => yes
        assert self.board.is_square_attacked((3,3), 'black') is True

    # 87
    def test_mixed_king_vs_queen_check_scenario(self):
        """
        White king at (0,0), black queen at (0,7).
        The queen on (0,7) attacks all squares on row 0 => (0,0) => True
        So white king is in check if no block. We'll confirm is_square_attacked((0,0),'black') => True
        """
        self.board.grid[0][0] = King('white', (0, 0))
        self.board.grid[0][7] = Queen('black', (0, 7))
        assert self.board.is_square_attacked((0,0), 'black') is True

    # 88
    def test_mixed_rook_and_pawn_arrangement_for_attacks(self):
        """
        White rook at (3,0), black pawn at (4,1).
        - White rook => does it attack (4,1)? Not horizontally or vertically => False
        - black pawn => from (4,1) => attacks (3,0) => True if diagonal => yes, row-1=3, col-1=0 => that works.
        """
        self.board.grid[3][0] = Rook('white', (3, 0))
        self.board.grid[4][1] = Pawn('black', (4, 1))

        assert self.board.is_square_attacked((4,1), 'white') is False
        assert self.board.is_square_attacked((3,0), 'black') is True

    # 89
    def test_mixed_opposing_bishops_different_diagonals_no_interaction(self):
        """
        White bishop at (0,2), black bishop at (7,5).
        If they are on different color squares or diagonals that never intersect => they can't attack each other.
        We'll check if (7,5) attacked by white => possibly no if no diagonal alignment.
        """
        self.board.grid[0][2] = Bishop('white', (0, 2))
        self.board.grid[7][5] = Bishop('black', (7, 5))
        assert self.board.is_square_attacked((7,5), 'white') is False
        assert self.board.is_square_attacked((0,2), 'black') is False

    # 90
    def test_mixed_queens_on_same_line_blocked_by_own_piece(self):
        """
        White queen at (2,2), black queen at (2,7), but there's a white rook at (2,4).
        Then white queen can't see (2,7), black queen can't see (2,2).
        is_square_attacked((2,7), 'white') => False
        is_square_attacked((2,2), 'black') => False
        """
        self.board.grid[2][2] = Queen('white', (2, 2))
        self.board.grid[2][4] = Rook('white', (2, 4))
        self.board.grid[2][7] = Queen('black', (2, 7))

        assert self.board.is_square_attacked((2,7), 'white') is False
        assert self.board.is_square_attacked((2,2), 'black') is False

    # -------------------- 91-100: More Edge & Random Tests --------------------

    # 91
    def test_edge_row_top_pieces_and_attacks(self):
        """
        White rook at (7,0), black bishop at (7,7).
        Rook => attacks along row 7 => (7,1),(7,2),..., (7,6), and file => (0,0)..(6,0).
        bishop at (7,7) => diagonal => might do (6,6), (5,5), etc.
        We'll confirm (7,7) attacked by rook => yes if no block in between? Actually, (7,7) is same row => True
        """
        self.board.grid[7][0] = Rook('white', (7, 0))
        self.board.grid[7][7] = Bishop('black', (7, 7))
        # No block in between horizontally
        assert self.board.is_square_attacked((7,7), 'white') is True

    # 92
    def test_edge_column_left_pieces_and_attacks(self):
        """
        White queen at (0,2), black rook at (0,7) => Wait, that's the same row. 
        Let's do something else: White queen at (0,2), black rook at (5,0).
        The black rook => attacks entire col=0 => so (0,0) => but our queen is at (0,2). Not relevant.
        We'll check is (5,2) attacked by black? => no, not same row or column, 
        or diagonal for a rook => false.
        """
        self.board.grid[0][2] = Queen('white', (0, 2))
        self.board.grid[5][0] = Rook('black', (5, 0))
        assert self.board.is_square_attacked((5,2), 'black') is False

    # 93
    def test_mutual_attack_same_rank_rooks_different_colors(self):
        """
        White rook at (4,4), black rook at (4,7), no block => they see each other.
        => is_square_attacked((4,7),'white') => True
        => is_square_attacked((4,4),'black') => True
        """
        self.board.grid[4][4] = Rook('white', (4, 4))
        self.board.grid[4][7] = Rook('black', (4, 7))
        assert self.board.is_square_attacked((4,7), 'white') is True
        assert self.board.is_square_attacked((4,4), 'black') is True

    # 94
    def test_mutual_attack_same_file_queens_different_colors(self):
        """
        White queen at (2,2), black queen at (6,2).
        No blocking => they see each other => both True
        """
        self.board.grid[2][2] = Queen('white', (2, 2))
        self.board.grid[6][2] = Queen('black', (6, 2))
        assert self.board.is_square_attacked((6,2), 'white') is True
        assert self.board.is_square_attacked((2,2), 'black') is True

    # 95
    def test_mutual_attack_diagonal_bishops_opposite_colors(self):
        """
        White bishop at (1,1), black bishop at (3,3), no block => mutual diagonal => both True
        """
        self.board.grid[1][1] = Bishop('white', (1, 1))
        self.board.grid[3][3] = Bishop('black', (3, 3))
        assert self.board.is_square_attacked((3,3), 'white') is True
        assert self.board.is_square_attacked((1,1), 'black') is True

    # 96
    def test_no_attack_if_different_lines_for_rooks(self):
        """
        White rook at (0,0), black rook at (1,7).
        Distinct row & column => rooks do not see each other => False
        """
        self.board.grid[0][0] = Rook('white', (0, 0))
        self.board.grid[1][7] = Rook('black', (1, 7))
        assert self.board.is_square_attacked((1,7), 'white') is False
        assert self.board.is_square_attacked((0,0), 'black') is False

    # 97
    def test_no_attack_if_different_diagonals_for_bishops(self):
        """
        White bishop at (2,0), black bishop at (4,3).
        Are they on the same diagonal? 
        Let's see: (2,0) -> (3,1) -> (4,2) -> (5,3). So (4,3) => 2 steps row, 3 steps col => not perfect diagonal => False
        """
        self.board.grid[2][0] = Bishop('white', (2, 0))
        self.board.grid[4][3] = Bishop('black', (4, 3))
        assert self.board.is_square_attacked((4,3), 'white') is False
        assert self.board.is_square_attacked((2,0), 'black') is False

    # 98
    def test_no_attack_if_knight_is_out_of_shape(self):
        """
        White knight at (5,5). Checking (7,5) => that's 2 up, 0 left => not a knight move => False
        """
        self.board.grid[5][5] = Knight('white', (5, 5))
        assert self.board.is_square_attacked((7,5), 'white') is False

    # 99
    def test_no_attack_if_king_is_2_squares_away_diagonally(self):
        """
        King at (2,2). Checking (4,4) => 2 diagonal => outside king's range => False
        """
        self.board.grid[2][2] = King('black', (2, 2))
        assert self.board.is_square_attacked((4,4), 'black') is False

    # 100
    def test_big_mixed_scenario_many_pieces_varied_positions(self):
        """
        Large scenario:
         - White: King(7,7), Rook(0,0), Knight(3,2), Bishop(2,5)
         - Black: King(0,7), Queen(4,4), Pawn(6,6), Rook(5,0)
        Check a variety of squares quickly.
        """
        self.board.grid[7][7] = King('white', (7, 7))
        self.board.grid[0][0] = Rook('white', (0, 0))
        self.board.grid[3][2] = Knight('white', (3, 2))
        self.board.grid[2][5] = Bishop('white', (2, 5))

        self.board.grid[0][7] = King('black', (0, 7))
        self.board.grid[4][4] = Queen('black', (4, 4))
        self.board.grid[6][6] = Pawn('black', (6, 6))
        self.board.grid[5][0] = Rook('black', (5, 0))

        # 1) (0,0) attacked by black? Possibly from black rook at (5,0) => same file => True if no block
        #    Actually check if there's a block? (1,0) to (4,0)? We have no pieces listed => so no block => True
        assert self.board.is_square_attacked((0,0), 'black') is True

        # 2) (4,4) attacked by white? Maybe from bishop(2,5)? That would require (3,4) or (4,3) diagonal => not correct.
        #    Maybe from rook(0,0)? It's not same row or col. Knight(3,2) => (4,4) => that's 1,2 => not a knight move. => False
        assert self.board.is_square_attacked((4,4), 'white') is False

        # 3) (7,7) attacked by black? Possibly queen(4,4) => diagonal up to (7,7)? That's +3 row, +3 col => yes => True
        assert self.board.is_square_attacked((7,7), 'black') is True

        # 4) (6,6) attacked by white? Possibly bishop(2,5) => that would be +4 row, +1 col => not diagonal => no.
        #    Rook(0,0) => different row/col => no. Knight(3,2)->(6,6)? That's +3 row, +4 col => not an L => no. => False
        assert self.board.is_square_attacked((6,6), 'white') is False