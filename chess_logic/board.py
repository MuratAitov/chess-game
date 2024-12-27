# chess_logic/board.py

from typing import Optional, Tuple
try:
    from pieces import Piece, Pawn, Rook, Knight, Bishop, Queen, King
except ImportError:
    from chess_logic.pieces import Piece, Pawn, Rook, Knight, Bishop, Queen, King


class Board:
    def __init__(self):
        self.grid = [[None for i in range(8)] for j in range(8)]
    
    def setup_initial_position(self):
        # Пешки
        for col in range(8):
            self.grid[6][col] = Pawn('black', (6, col))
            self.grid[1][col] = Pawn('white', (1, col))
        
        # Ладьи
        self.grid[7][0] = Rook('black', (7, 0))
        self.grid[7][7] = Rook('black', (7, 7))
        self.grid[0][0] = Rook('white', (0, 0))
        self.grid[0][7] = Rook('white', (0, 7))
        
        # Кони
        self.grid[7][1] = Knight('black', (7, 1))
        self.grid[7][6] = Knight('black', (7, 6))
        self.grid[0][1] = Knight('white', (0, 1))
        self.grid[0][6] = Knight('white', (0, 6))
        
        # Слоны
        self.grid[7][2] = Bishop('black', (7, 2))
        self.grid[7][5] = Bishop('black', (7, 5))
        self.grid[0][2] = Bishop('white', (0, 2))
        self.grid[0][5] = Bishop('white', (0, 5))
        
        # Ферзи
        self.grid[7][3] = Queen('black', (7, 3))
        self.grid[0][3] = Queen('white', (0, 3))
        
        # Короли
        self.grid[7][4] = King('black', (7, 4))
        self.grid[0][4] = King('white', (0, 4))
    
    def place_test_pieces(self, piece: Piece, position: Tuple[int, int]):
        """
        Ставит указанную фигуру на заданные координаты.
        
        Args:
            piece (Piece): Фигура для размещения
            position (Tuple[int, int]): Координаты (строка, столбец)
        """
        row, col = position
        if self.in_bounds(position):
            self.grid[row][col] = piece
            piece.position = position
    
    def in_bounds(self, pos: Tuple[int, int]) -> bool:
        row, col = pos
        return 0 <= row < 8 and 0 <= col < 8
    
    def get_piece(self, pos: Tuple[int, int]) -> Optional[Piece]:
        row, col = pos
        return self.grid[row][col]
    
    def move_piece(self, start_pos: Tuple[int, int], end_pos: Tuple[int, int]) -> bool:
        piece = self.get_piece(start_pos)
        if piece is None:
            return False
        
        if end_pos not in piece.get_legal_moves(self):
            return False
        
        self.grid[start_pos[0]][start_pos[1]] = None
        self.grid[end_pos[0]][end_pos[1]] = piece
        piece.position = end_pos
        return True
    
    def is_square_attacked(self, position: Tuple[int, int], by_color: str) -> bool:
        row, col= position 
        
        # for pawn 
        if by_color == 'white':
            for attack_col in (col - 1, col + 1):
                if self.in_bounds((row - 1, attack_col)):
                    piece = self.grid[row - 1][attack_col]
                    if piece is not None and piece.color == 'white' and piece.__class__.__name__ == 'Pawn':
                        return True
        else:
            for attack_col in (col - 1, col + 1):
                if self.in_bounds((row + 1, attack_col)):
                    piece = self.grid[row + 1][attack_col]
                    if piece is not None and piece.color == 'black' and piece.__class__.__name__ == 'Pawn':
                        return True
    
        # for knight 
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
        
        for r, c in knight_moves:
            if self.in_bounds((r, c)):
                piece = self.grid[r][c]
                if piece is not None and piece.color == by_color and piece.__class__.__name__ == 'Knight':
                    return True

        # for king 
        for drow in [-1, 0, 1]:
            for dcol in [-1, 0, 1]:
                if drow == 0 and dcol == 0:
                    continue
                r = row + drow
                c = col + dcol
                if self.in_bounds((r, c)):
                    piece = self.grid[r][c]
                    if piece is not None and piece.color == by_color and piece.__class__.__name__ == 'King':
                        return True
                    
        # for bishop / queen 
        directions_diagonal = [(1,1), (1,-1), (-1,1), (-1,-1)]
        for drow, dcol in directions_diagonal:
            r, c = row, col
            while True:
                r += drow
                c += dcol
                if not self.in_bounds((r,c)):
                    break
                piece = self.grid[r][c]
                if piece is not None:
                    if piece.color == by_color and piece.__class__.__name__ in ('Bishop', 'Queen'):
                        return True
                    break

        # for rook / queen 
        directions_line = [(1,0), (-1,0), (0,1), (0,-1)]
        for drow, dcol in directions_line:
            r, c = row, col
            while True:
                r += drow
                c += dcol
                if not self.in_bounds((r,c)):
                    break
                piece = self.grid[r][c]
                if piece is not None:
                    if piece.color == by_color and piece.__class__.__name__ in ('Rook', 'Queen'):
                        return True
                    break

        return False
    
    
    def is_in_check(self, color: str) -> bool:
        """
        Проверяет, находится ли король указанного цвета под шахом.
        
        Args:
            color (str): цвет короля ('white' или 'black')
            
        Returns:
            bool: True если король под шахом, False в противном случае
        """
        # Найдем позицию короля указанного цвета
        king_pos = None
        for row in range(8):
            for col in range(8):
                piece = self.get_piece((row, col))
                if (piece and 
                    piece.__class__.__name__ == 'King' and 
                    piece.color == color):
                    king_pos = (row, col)
                    break
            if king_pos:
                break
        
        if not king_pos:
            return False  # Король не найден (не должно случиться в нормальной игре)
        
        # Проверим, может ли какая-либо фигура противника атаковать короля
        opponent_color = 'black' if color == 'white' else 'white'
        for row in range(8):
            for col in range(8):
                piece = self.get_piece((row, col))
                if piece and piece.color == opponent_color:
                    # Получаем все возможные ходы фигуры
                    legal_moves = piece.get_legal_moves(self)
                    # Если позиция короля в списке возможных ходов - это шах
                    if king_pos in legal_moves:
                        return True
                
        return False

    def is_checkmate(self, color: str) -> bool:
        """
        Проверяет, находится ли указанный цвет в положении мата.
        
        Args:
            color (str): цвет игрока ('white' или 'black')
            
        Returns:
            bool: True если это мат, False в противном случае
        """
        # Если нет шаха, то нет и мата
        if not self.is_in_check(color):
            return False
        
        # Проверяем все фигуры указанного цвета
        for row in range(8):
            for col in range(8):
                piece = self.get_piece((row, col))
                if piece and piece.color == color:
                    # Получаем все возможные ходы фигуры
                    legal_moves = piece.get_legal_moves(self)
                    
                    # Проверяем каждый возможный ход
                    for move in legal_moves:
                        # Сохраняем текущее состояние
                        captured_piece = self.get_piece(move)
                        old_pos = piece.position
                        
                        # Пробуем сделать ход
                        self._move_piece(piece, move)
                        
                        # Проверяем, остается ли король под шахом
                        still_in_check = self.is_in_check(color)
                        
                        # Возвращаем всё как было
                        self._move_piece(piece, old_pos)
                        if captured_piece:
                            self.pieces[move] = captured_piece
                        
                        # Если нашелся ход, спасающий от шаха - это не мат
                        if not still_in_check:
                            return False
                            
        # Если не нашлось ходов, спасающих от шаха - это мат
        return True

    def is_stalemate(self, color: str) -> bool:
        """
        Проверяет, находится ли указанный цвет в положении пата.
        
        Args:
            color (str): цвет игрока ('white' или 'black')
            
        Returns:
            bool: True если это пат, False в противном случае
        """
        # Если есть шах, то это не пат
        if self.is_in_check(color):
            return False
        
        # Проверяем, есть ли хоть один легальный ход
        for row in range(8):
            for col in range(8):
                piece = self.get_piece((row, col))
                if piece and piece.color == color:
                    legal_moves = piece.get_legal_moves(self)
                    
                    # Проверяем каждый возможный ход
                    for move in legal_moves:
                        # Сохраняем текущее состояние
                        captured_piece = self.get_piece(move)
                        old_pos = piece.position
                        
                        # Пробуем сделать ход
                        self._move_piece(piece, move)
                        
                        # Проверяем, не подставляет ли ход короля под шах
                        legal_move = not self.is_in_check(color)
                        
                        # Возвращаем всё как было
                        self._move_piece(piece, old_pos)
                        if captured_piece:
                            self.pieces[move] = captured_piece
                        
                        # Если нашелся хотя бы один легальный ход - это не пат
                        if legal_move:
                            return False
                            
        # Если не нашлось ни одного легального хода - это пат
        return True
    
            
    def highlight_moves(self, piece: Piece) -> str:
        moves = piece.get_legal_moves(self)
        moves_set = set(moves) 
        
        lines = []
        for row in range(7, -1, -1):
            row_str = []
            for col in range(8):
                cell_piece = self.grid[row][col]
                if cell_piece is None:
                    if (row, col) in moves_set:
                        row_str.append('*')
                    else:
                        row_str.append('.')
                else:
                    row_str.append(str(cell_piece))
            lines.append(f"{row+1} " + " ".join(row_str))
        lines.append("  a b c d e f g h")
        return "\n".join(lines)
    
    def __str__(self):
        lines = []
        for row in range(7, -1, -1):
            row_str = []
            for col in range(8):
                piece = self.grid[row][col]
                if piece is None:
                    row_str.append(".")
                else:
                    row_str.append(str(piece))
            lines.append(f"{row+1} " + " ".join(row_str))
        lines.append("  a b c d e f g h")
        return "\n".join(lines)
    
if __name__ == '__main__':
    board = Board()
    board.place_test_pieces()
    print(board.highlight_moves(Rook('white', (0, 0))))