from typing import List, Tuple


class Piece:
    """
    Базовый класс для всех фигур.
    """
    WHITE_SYMBOLS = {
        'King': '♔',  # U+2654
        'Queen': '♕',  # U+2655
        'Rook': '♖',  # U+2656
        'Bishop': '♗',  # U+2657
        'Knight': '♘',  # U+2658
        'Pawn': '♙'  # U+2659
    }

    BLACK_SYMBOLS = {
        'King': '♚',  # U+265A
        'Queen': '♛',  # U+265B
        'Rook': '♜',  # U+265C
        'Bishop': '♝',  # U+265D
        'Knight': '♞',  # U+265E
        'Pawn': '♟'  # U+265F
    }

    def __init__(self, color: str, position: Tuple[int, int]):
        """
        :param color: 'white' или 'black'
        :param position: (row, col), где 0 <= row, col <= 7
        """
        self.color = color
        self.position = position

    def get_legal_moves(self, board) -> List[Tuple[int, int]]:
        """Шахи не учитывбатся"""
        return []

    def get_unicode_symbol(self) -> str:
        """
        Возвращает юникод-символ шахматной фигуры 
        в зависимости от класса и цвета.
        """
        # self.__class__.__name__ вернёт строку 'King', 'Queen' и т. д.
        piece_name = self.__class__.__name__

        if self.color == 'white':
            return self.WHITE_SYMBOLS.get(piece_name, '?')
        else:
            return self.BLACK_SYMBOLS.get(piece_name, '?')

    def __str__(self):
        """
        При выводе print(piece) в консоли будем видеть юникод-символ,
        например, ♔ или ♟ (если хотим).
        """
        return self.get_unicode_symbol()
    def __repr__(self):
        """
        Репрезентация в отладочном выводе. Возвращает строку вида 'wP' или 'bK',
        которая используется как ключ для доступа к изображениям фигур.
        """
        color_prefix = 'w' if self.color == 'white' else 'b'
        piece_type = 'N' if self.__class__.__name__ == 'Knight' else self.__class__.__name__[0]
        return f"{color_prefix}{piece_type}"


class Pawn(Piece):
    """
    Пешка. без взятия на проходе и без превращения.
    """

    def get_legal_moves(self, board):
        moves = []
        row, col = self.position
        direction = -1 if self.color == 'white' else 1

        forward_row = row + direction
        if board.in_bounds((forward_row, col)) and board.get_piece((forward_row, col)) is None:
            moves.append((forward_row, col))

            if self.color == 'white' and row == 6:
                two_step_row = row + 2 * direction
                if (board.get_piece((two_step_row, col)) is None and
                        board.in_bounds((two_step_row, col))):
                    moves.append((two_step_row, col))
            elif self.color == 'black' and row == 1:
                two_step_row = row + 2 * direction
                if (board.get_piece((two_step_row, col)) is None and
                        board.in_bounds((two_step_row, col))):
                    moves.append((two_step_row, col))

        for attack_col in [col - 1, col + 1]:
            attack_pos = (row + direction, attack_col)
            if board.in_bounds(attack_pos):
                target_piece = board.get_piece(attack_pos)
                if target_piece is not None and target_piece.color != self.color:
                    moves.append(attack_pos)

        return moves


class Rook(Piece):
    '''Ладья'''

    def get_legal_moves(self, board):
        moves = []
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        row, col = self.position
        for drow, dcol in directions:
            r, c = row, col
            while True:
                r += drow
                c += dcol
                if not board.in_bounds((r, c)):
                    break
                target_piece = board.get_piece((r, c))
                if target_piece is None:
                    moves.append((r, c))
                else:
                    if target_piece.color != self.color:
                        moves.append((r, c))
                    break
        return moves


class Knight(Piece):
    """Конь"""

    def get_legal_moves(self, board):
        moves = []
        row, col = self.position
        knight_moves = [
            (row + 2, col + 1),
            (row + 2, col - 1),
            (row - 2, col + 1),
            (row - 2, col - 1),
            (row + 1, col + 2),
            (row + 1, col - 2),
            (row - 1, col + 2),
            (row - 1, col - 2),
        ]
        for (r, c) in knight_moves:
            if board.in_bounds((r, c)):
                target_piece = board.get_piece((r, c))
                if target_piece is None or target_piece.color != self.color:
                    moves.append((r, c))

        return moves


class Bishop(Piece):
    """Слон"""

    def get_legal_moves(self, board):
        moves = []
        row, col = self.position
        directions_diagonal = [(1, 1), (1, -1), (-1, 1), (-1, -1)]

        for drow, dcol in directions_diagonal:
            r, c = row, col
            while True:
                r += drow
                c += dcol
                if not board.in_bounds((r, c)):
                    break
                target_piece = board.get_piece((r, c))
                if target_piece is None:
                    moves.append((r, c))
                else:
                    if target_piece.color != self.color:
                        moves.append((r, c))
                    break

        return moves


class Queen(Piece):
    """Ферзь"""

    def get_legal_moves(self, board):
        moves = []
        row, col = self.position
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
        for drow, dcol in directions:
            r, c = row, col
            while True:
                r += drow
                c += dcol
                if not board.in_bounds((r, c)):
                    break
                target_piece = board.get_piece((r, c))
                if target_piece is None:
                    moves.append((r, c))
                else:
                    if target_piece.color != self.color:
                        moves.append((r, c))
                    break
        return moves


class King(Piece):
    """Король"""

    def get_legal_moves(self, board):
        moves = []
        row, col = self.position

        king_steps = [
            (row - 1, col - 1),
            (row - 1, col),
            (row - 1, col + 1),
            (row, col - 1),
            (row, col + 1),
            (row + 1, col - 1),
            (row + 1, col),
            (row + 1, col + 1),
        ]

        for (r, c) in king_steps:
            if board.in_bounds((r, c)):
                target_piece = board.get_piece((r, c))
                if target_piece is None or target_piece.color != self.color:
                    moves.append((r, c))

        return moves


if __name__ == '__main__':
    pawn = Pawn('white', (1, 1))
