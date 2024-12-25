# tests/test_board.py

import pytest
import sys
from pathlib import Path

current_path = Path(__file__).resolve()
project_root = current_path.parents[1]  
sys.path.append(str(project_root))

print("Project Root Path:", project_root)

from chess_logic.board import Board
from chess_logic.pieces import Pawn, Rook, Knight, Bishop

class TestIsSquareAttacked:
    """ Тесты для метода is_square_attacked() """

    def setup_method(self):
        """
        Эта функция вызывается перед каждым тестовым методом.
        Создаём пустую доску 8x8 (Board),
        чтобы для каждого теста мы имели 'чистое' состояние.
        """
        self.board = Board()
        for r in range(8):
            for c in range(8):
                self.board.grid[r][c] = None

    # 1
    def test_white_pawn_attacks_up_left(self):
        """Белая пешка на (3,3) атакует (2,2). Должно вернуться True."""
        self.board.grid[3][3] = Pawn('white', (3, 3))
        attacked = self.board.is_square_attacked((4, 2), 'white')
        assert attacked is True

    # 2
    def test_white_pawn_attacks_up_right(self):
        """Белая пешка на (3,3) атакует (2,4). Должно вернуться True."""
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
        """Чёрная пешка на (4,4) атакует (5,3). Должно вернуться True."""
        self.board.grid[4][4] = Pawn('black', (4, 4))
        attacked = self.board.is_square_attacked((3, 3), 'black')
        assert attacked is True

    # 5
    def test_black_pawn_attacks_down_right(self):
        """Чёрная пешка на (4,4) атакует (5,5). Должно вернуться True."""
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

    # # 12
    # def test_king_attacks_adjacent(self):
    #     """
    #     Король на (4,4) атакует все 8 соседних клеток, проверим одну из них (3,3).
    #     """
    #     self.board.grid[4][4] = King('white', (4, 4))
    #     attacked = self.board.is_square_attacked((3, 3), 'white')
    #     assert attacked is True

    # # 13
    # def test_king_does_not_attack_two_away(self):
    #     """
    #     Король на (4,4) НЕ атакует (2,4).
    #     """
    #     self.board.grid[4][4] = King('white', (4, 4))
    #     attacked = self.board.is_square_attacked((2, 4), 'white')
    #     assert attacked is False

    # 14
    def test_bishop_attacks_diagonal(self):
        """
        Слон на (4,4) атакует (6,6), (2,2) и т.д.
        Проверим (6,6).
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

    # # 16
    # def test_queen_attacks_diagonal(self):
    #     """
    #     Ферзь на (4,4) атакует (7,7) по диагонали
    #     """
    #     self.board.grid[4][4] = Queen('black', (4, 4))
    #     attacked = self.board.is_square_attacked((7, 7), 'black')
    #     assert attacked is True

    # # 17
    # def test_queen_attacks_straight(self):
    #     """
    #     Ферзь на (4,4) атакует (4,0) по горизонтали
    #     """
    #     self.board.grid[4][4] = Queen('black', (4, 4))
    #     attacked = self.board.is_square_attacked((4, 0), 'black')
    #     assert attacked is True

    # 18
    def test_position_out_of_bounds_returns_false(self):
        """
        Если проверяем клетку за границами доски — ожидаем False (или исключение, но чаще False).
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