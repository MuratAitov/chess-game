# chess_logic/board.py

from typing import Optional, Tuple
from pieces import Piece, Pawn, Rook
# , Knight, Bishop, Queen, King

class Board:
    def __init__(self):
        self.grid = [[None for i in range(8)] for j in range(8)]
    
    def setup_initial_position(self):
        # Пешки
        for col in range(8):
            self.grid[6][col] = Pawn('white', (6, col))
            self.grid[1][col] = Pawn('black', (1, col))
        
        # Ладьи
        self.grid[7][0] = Rook('white', (7, 0))
        self.grid[7][7] = Rook('white', (7, 7))
        self.grid[0][0] = Rook('black', (0, 0))
        self.grid[0][7] = Rook('black', (0, 7))
        
        # # Кони
        # self.grid[7][1] = Knight('white', (7, 1))
        # self.grid[7][6] = Knight('white', (7, 6))
        # self.grid[0][1] = Knight('black', (0, 1))
        # self.grid[0][6] = Knight('black', (0, 6))
        
        # # Слоны
        # self.grid[7][2] = Bishop('white', (7, 2))
        # self.grid[7][5] = Bishop('white', (7, 5))
        # self.grid[0][2] = Bishop('black', (0, 2))
        # self.grid[0][5] = Bishop('black', (0, 5))
        
        # # Ферзи
        # self.grid[7][3] = Queen('white', (7, 3))
        # self.grid[0][3] = Queen('black', (0, 3))
        
        # # Короли
        # self.grid[7][4] = King('white', (7, 4))
        # self.grid[0][4] = King('black', (0, 4))
    
    def place_test_pieces(self):
        """
        ставим несколько фигур в произвольных позициях.
        """
        for r in range(8):
            for c in range(8):
                self.grid[r][c] = None
        
        self.grid[0][0] = Rook('white', (0, 0))
        self.grid[3][0] = Pawn('black', (3, 0))
        # self.grid[4][4] = King('white', (4, 4))
        # self.grid[2][2] = Bishop('black', (2, 2))
    
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
        for row in range(8):
            for col in range(8):
                p = self.grid[row][col]
                if p is not None and p.color == by_color:
                    if position in p.get_legal_moves(self):
                        return True
        return False
    
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
    
    
board = Board()
board.place_test_pieces()
print(board.highlight_moves(Rook('white', (0, 0))))