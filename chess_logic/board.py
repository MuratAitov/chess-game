# chess_logic/board.py

from typing import Optional, Tuple, List
try:
    from pieces import Piece, Pawn, Rook, Knight, Bishop, Queen, King
except ImportError:
    from chess_logic.pieces import Piece, Pawn, Rook, Knight, Bishop, Queen, King


class Board:
    def __init__(self):
        self.grid = [[None for i in range(8)] for j in range(8)]
        self.castling_rights = {
            'white': {'K': True, 'Q': True},
            'black': {'K': True, 'Q': True},
        }
        self.en_passant_target = None
        self.halfmove_clock = 0
        self.repetition_counts = {}
        self.halfmove_clock = 0
        self.repetition_counts = {}
    
    def setup_initial_position(self):
        self.castling_rights = {
            'white': {'K': True, 'Q': True},
            'black': {'K': True, 'Q': True},
        }
        self.en_passant_target = None
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
        self.record_position('white')

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
    
    def move_piece(self, start_pos: Tuple[int, int], end_pos: Tuple[int, int], promotion: Optional[str] = None, next_color: Optional[str] = None) -> bool:
        """
        Move a piece from start_pos to end_pos if the move is legal.
        A move is legal if:
        1. There's a piece at start_pos
        2. The move is in the piece's legal moves
        3. The move doesn't leave the player's king in check
        """
        piece = self.get_piece(start_pos)
        if piece is None:
            return False
        
        # Check if move is in piece's basic legal moves
        if end_pos not in piece.get_legal_moves(self):
            return False
        
        # Snapshot state for undo if move is illegal
        captured_piece = self.get_piece(end_pos)
        old_pos = piece.position
        prev_en_passant = self.en_passant_target
        prev_castling = (
            self.castling_rights['white']['K'],
            self.castling_rights['white']['Q'],
            self.castling_rights['black']['K'],
            self.castling_rights['black']['Q'],
        )
        rook_move = None
        en_passant_capture_pos = None
        promoted_piece = None

        # Handle en passant capture
        if (piece.__class__.__name__ == 'Pawn' and
            self.en_passant_target == end_pos and
            captured_piece is None):
            en_passant_capture_pos = (old_pos[0], end_pos[1])
            captured_piece = self.get_piece(en_passant_capture_pos)
            if captured_piece:
                self.grid[en_passant_capture_pos[0]][en_passant_capture_pos[1]] = None

        # Move piece
        self.grid[start_pos[0]][start_pos[1]] = None

        # Handle promotion
        if piece.__class__.__name__ == 'Pawn' and end_pos[0] in (0, 7):
            promoted_piece = self._create_promotion_piece(piece.color, end_pos, promotion)
            self.grid[end_pos[0]][end_pos[1]] = promoted_piece
        else:
            self.grid[end_pos[0]][end_pos[1]] = piece
            piece.position = end_pos

        # Handle castling (king moves two squares)
        if piece.__class__.__name__ == 'King' and abs(end_pos[1] - old_pos[1]) == 2:
            row = old_pos[0]
            if end_pos[1] == 6:
                rook_start = (row, 7)
                rook_end = (row, 5)
            else:
                rook_start = (row, 0)
                rook_end = (row, 3)
            rook_piece = self.get_piece(rook_start)
            if rook_piece:
                self.grid[rook_start[0]][rook_start[1]] = None
                self.grid[rook_end[0]][rook_end[1]] = rook_piece
                rook_piece.position = rook_end
                rook_move = (rook_piece, rook_start, rook_end)

        # Update castling rights
        if piece.__class__.__name__ == 'King':
            self.castling_rights[piece.color]['K'] = False
            self.castling_rights[piece.color]['Q'] = False
        elif piece.__class__.__name__ == 'Rook':
            if piece.color == 'white':
                if old_pos == (0, 0):
                    self.castling_rights['white']['Q'] = False
                elif old_pos == (0, 7):
                    self.castling_rights['white']['K'] = False
            else:
                if old_pos == (7, 0):
                    self.castling_rights['black']['Q'] = False
                elif old_pos == (7, 7):
                    self.castling_rights['black']['K'] = False

        if captured_piece and captured_piece.__class__.__name__ == 'Rook':
            if captured_piece.color == 'white':
                if end_pos == (0, 0):
                    self.castling_rights['white']['Q'] = False
                elif end_pos == (0, 7):
                    self.castling_rights['white']['K'] = False
            else:
                if end_pos == (7, 0):
                    self.castling_rights['black']['Q'] = False
                elif end_pos == (7, 7):
                    self.castling_rights['black']['K'] = False

        # Update en passant target
        self.en_passant_target = None
        if piece.__class__.__name__ == 'Pawn' and abs(end_pos[0] - old_pos[0]) == 2:
            mid_row = (end_pos[0] + old_pos[0]) // 2
            self.en_passant_target = (mid_row, end_pos[1])

        # Check if our king is in check after this move
        in_check = self.is_in_check(piece.color)

        # Undo if illegal
        if in_check:
            if rook_move:
                rook_piece, rook_start, rook_end = rook_move
                self.grid[rook_end[0]][rook_end[1]] = None
                self.grid[rook_start[0]][rook_start[1]] = rook_piece
                rook_piece.position = rook_start

            if promoted_piece:
                self.grid[end_pos[0]][end_pos[1]] = None
                self.grid[old_pos[0]][old_pos[1]] = piece
                piece.position = old_pos
            else:
                self.grid[end_pos[0]][end_pos[1]] = None
                self.grid[old_pos[0]][old_pos[1]] = piece
                piece.position = old_pos

            if en_passant_capture_pos and captured_piece:
                self.grid[en_passant_capture_pos[0]][en_passant_capture_pos[1]] = captured_piece
            else:
                self.grid[end_pos[0]][end_pos[1]] = captured_piece

            self.en_passant_target = prev_en_passant
            self.castling_rights['white']['K'] = prev_castling[0]
            self.castling_rights['white']['Q'] = prev_castling[1]
            self.castling_rights['black']['K'] = prev_castling[2]
            self.castling_rights['black']['Q'] = prev_castling[3]
            return False

        is_capture = captured_piece is not None
        is_pawn_move = piece.__class__.__name__ == 'Pawn'
        if is_capture or is_pawn_move:
            self.halfmove_clock = 0
        else:
            self.halfmove_clock += 1

        if next_color:
            self.record_position(next_color)

        return True

    def _create_promotion_piece(self, color: str, position: Tuple[int, int], promotion: Optional[str]):
        promo = (promotion or 'q').lower()
        if promo == 'r':
            return Rook(color, position)
        if promo == 'b':
            return Bishop(color, position)
        if promo == 'n':
            return Knight(color, position)
        return Queen(color, position)

    def get_position_key(self, side_to_move: str) -> str:
        rows = []
        for row in range(7, -1, -1):
            empty = 0
            row_parts = []
            for col in range(8):
                piece = self.get_piece((row, col))
                if not piece:
                    empty += 1
                else:
                    if empty:
                        row_parts.append(str(empty))
                        empty = 0
                    name = piece.__class__.__name__
                    letter = {
                        'Pawn': 'p',
                        'Knight': 'n',
                        'Bishop': 'b',
                        'Rook': 'r',
                        'Queen': 'q',
                        'King': 'k',
                    }[name]
                    if piece.color == 'white':
                        letter = letter.upper()
                    row_parts.append(letter)
            if empty:
                row_parts.append(str(empty))
            rows.append(''.join(row_parts))

        castling = ''
        if self.castling_rights['white']['K']:
            castling += 'K'
        if self.castling_rights['white']['Q']:
            castling += 'Q'
        if self.castling_rights['black']['K']:
            castling += 'k'
        if self.castling_rights['black']['Q']:
            castling += 'q'
        if not castling:
            castling = '-'

        if self.en_passant_target:
            ep_file = chr(ord('a') + self.en_passant_target[1])
            ep_rank = str(self.en_passant_target[0] + 1)
            ep = ep_file + ep_rank
        else:
            ep = '-'

        side = 'w' if side_to_move == 'white' else 'b'
        return f\"{'/'.join(rows)} {side} {castling} {ep}\"

    def record_position(self, side_to_move: str):
        key = self.get_position_key(side_to_move)
        self.repetition_counts[key] = self.repetition_counts.get(key, 0) + 1

    def is_threefold_repetition(self, side_to_move: str) -> bool:
        key = self.get_position_key(side_to_move)
        return self.repetition_counts.get(key, 0) >= 3

    def is_insufficient_material(self) -> bool:
        pieces = []
        bishops = []
        for row in range(8):
            for col in range(8):
                piece = self.get_piece((row, col))
                if piece:
                    pieces.append(piece)
                    if piece.__class__.__name__ == 'Bishop':
                        bishops.append((piece.color, (row + col) % 2))

        non_kings = [p for p in pieces if p.__class__.__name__ != 'King']
        if not non_kings:
            return True
        if len(non_kings) == 1:
            return non_kings[0].__class__.__name__ in ('Bishop', 'Knight')
        if len(non_kings) == 2:
            if all(p.__class__.__name__ == 'Knight' for p in non_kings):
                return True
            if all(p.__class__.__name__ == 'Bishop' for p in non_kings):
                same_color = bishops[0][1] == bishops[1][1] and bishops[0][0] != bishops[1][0]
                return same_color
        return False

    def _apply_temporary_move(self, piece: Piece, start_pos: Tuple[int, int], end_pos: Tuple[int, int], promotion: Optional[str] = None):
        captured_piece = self.get_piece(end_pos)
        old_pos = piece.position
        rook_move = None
        en_passant_capture_pos = None
        promoted_piece = None

        if (piece.__class__.__name__ == 'Pawn' and
            self.en_passant_target == end_pos and
            captured_piece is None):
            en_passant_capture_pos = (old_pos[0], end_pos[1])
            captured_piece = self.get_piece(en_passant_capture_pos)
            if captured_piece:
                self.grid[en_passant_capture_pos[0]][en_passant_capture_pos[1]] = None

        self.grid[start_pos[0]][start_pos[1]] = None

        if piece.__class__.__name__ == 'Pawn' and end_pos[0] in (0, 7):
            promoted_piece = self._create_promotion_piece(piece.color, end_pos, promotion)
            self.grid[end_pos[0]][end_pos[1]] = promoted_piece
        else:
            self.grid[end_pos[0]][end_pos[1]] = piece
            piece.position = end_pos

        if piece.__class__.__name__ == 'King' and abs(end_pos[1] - old_pos[1]) == 2:
            row = old_pos[0]
            if end_pos[1] == 6:
                rook_start = (row, 7)
                rook_end = (row, 5)
            else:
                rook_start = (row, 0)
                rook_end = (row, 3)
            rook_piece = self.get_piece(rook_start)
            if rook_piece:
                self.grid[rook_start[0]][rook_start[1]] = None
                self.grid[rook_end[0]][rook_end[1]] = rook_piece
                rook_piece.position = rook_end
                rook_move = (rook_piece, rook_start, rook_end)

        return (piece, captured_piece, old_pos, en_passant_capture_pos, rook_move, promoted_piece)

    def _undo_temporary_move(self, end_pos: Tuple[int, int], state):
        piece, captured_piece, old_pos, en_passant_capture_pos, rook_move, promoted_piece = state

        if rook_move:
            rook_piece, rook_start, rook_end = rook_move
            self.grid[rook_end[0]][rook_end[1]] = None
            self.grid[rook_start[0]][rook_start[1]] = rook_piece
            rook_piece.position = rook_start

        if promoted_piece:
            self.grid[end_pos[0]][end_pos[1]] = None
            self.grid[old_pos[0]][old_pos[1]] = piece
            piece.position = old_pos
        else:
            self.grid[end_pos[0]][end_pos[1]] = None
            self.grid[old_pos[0]][old_pos[1]] = piece
            piece.position = old_pos

        if en_passant_capture_pos and captured_piece:
            self.grid[en_passant_capture_pos[0]][en_passant_capture_pos[1]] = captured_piece
        else:
            self.grid[end_pos[0]][end_pos[1]] = captured_piece
    
    def is_square_attacked(self, position: Tuple[int, int], by_color: str) -> bool:
        """
        Check if a square is attacked by pieces of the given color.
        
        Args:
            position: The square to check (row, col)
            by_color: The color of attacking pieces to check for
            
        Returns:
            True if the square is attacked, False otherwise
        """
        if not self.in_bounds(position):
            return False
            
        row, col = position 
        
        # Check for pawn attacks
        if by_color == 'white':
            # White pawns attack diagonally upward (from lower row numbers)
            for attack_col in (col - 1, col + 1):
                pawn_row = row - 1
                if self.in_bounds((pawn_row, attack_col)):
                    piece = self.grid[pawn_row][attack_col]
                    if piece is not None and piece.color == 'white' and piece.__class__.__name__ == 'Pawn':
                        return True
        else:
            # Black pawns attack diagonally downward (from higher row numbers)
            for attack_col in (col - 1, col + 1):
                pawn_row = row + 1
                if self.in_bounds((pawn_row, attack_col)):
                    piece = self.grid[pawn_row][attack_col]
                    if piece is not None and piece.color == 'black' and piece.__class__.__name__ == 'Pawn':
                        return True
    
        # Check for knight attacks
        knight_moves = [
            (row + 2, col + 1), (row + 2, col - 1),
            (row - 2, col + 1), (row - 2, col - 1),
            (row + 1, col + 2), (row + 1, col - 2),
            (row - 1, col + 2), (row - 1, col - 2),
        ]
        
        for r, c in knight_moves:
            if self.in_bounds((r, c)):
                piece = self.grid[r][c]
                if piece is not None and piece.color == by_color and piece.__class__.__name__ == 'Knight':
                    return True

        # Check for king attacks
        for drow in [-1, 0, 1]:
            for dcol in [-1, 0, 1]:
                if drow == 0 and dcol == 0:
                    continue
                r, c = row + drow, col + dcol
                if self.in_bounds((r, c)):
                    piece = self.grid[r][c]
                    if piece is not None and piece.color == by_color and piece.__class__.__name__ == 'King':
                        return True
                    
        # Check for bishop/queen diagonal attacks
        directions_diagonal = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
        for drow, dcol in directions_diagonal:
            r, c = row, col
            while True:
                r += drow
                c += dcol
                if not self.in_bounds((r, c)):
                    break
                piece = self.grid[r][c]
                if piece is not None:
                    if piece.color == by_color and piece.__class__.__name__ in ('Bishop', 'Queen'):
                        return True
                    break  # Piece blocks further attacks in this direction

        # Check for rook/queen straight line attacks
        directions_line = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        for drow, dcol in directions_line:
            r, c = row, col
            while True:
                r += drow
                c += dcol
                if not self.in_bounds((r, c)):
                    break
                piece = self.grid[r][c]
                if piece is not None:
                    if piece.color == by_color and piece.__class__.__name__ in ('Rook', 'Queen'):
                        return True
                    break  # Piece blocks further attacks in this direction

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
        return self.is_square_attacked(king_pos, opponent_color)
    def is_checkmate(self, color: str) -> bool:
        """
        DY??D_D?D?????D??,, D?D??.D_D'D,?,???? D?D, ??D?D?D?D?D?D??<D1 ?+D?D??, D? D?D_D?D_DD?D?D,D, D?D??,D?.
        
        Args:
            color (str): ?+D?D??, D,D3??D_D?D? ('white' D,D?D, 'black')
            
        Returns:
            bool: True D???D?D, ???,D_ D?D??,, False D? D???D_?,D,D?D?D_D? ??D?????D?D?
        """
        if not self.is_in_check(color):
            return False
        return len(self.get_legal_moves_for_color_with_promotions(color)) == 0
    def is_stalemate(self, color: str) -> bool:
        """
        DY??D_D?D?????D??,, D?D??.D_D'D,?,???? D?D, ??D?D?D?D?D?D??<D1 ?+D?D??, D? D?D_D?D_DD?D?D,D, D?D??,D?.
        
        Args:
            color (str): ?+D?D??, D,D3??D_D?D? ('white' D,D?D, 'black')
            
        Returns:
            bool: True D???D?D, ???,D_ D?D??,, False D? D???D_?,D,D?D?D_D? ??D?????D?D?
        """
        if self.is_in_check(color):
            return False
        return len(self.get_legal_moves_for_color_with_promotions(color)) == 0

    def get_legal_moves_for_color(self, color: str) -> List[Tuple[Tuple[int, int], Tuple[int, int]]]:
        """
        Get all legal moves for a given color (moves that don't put own king in check).
        Returns list of (start_pos, end_pos) tuples.
        """
        legal_moves = []
        
        for row in range(8):
            for col in range(8):
                piece = self.get_piece((row, col))
                if piece and piece.color == color:
                    piece_moves = piece.get_legal_moves(self)
                    
                    for move in piece_moves:
                        # Test if this move is actually legal (doesn't put king in check)
                        old_pos = piece.position
                        state = self._apply_temporary_move(piece, old_pos, move)
                        
                        # Check if king is in check
                        legal = not self.is_in_check(color)
                        
                        # Restore board
                        self._undo_temporary_move(move, state)
                        
                        if legal:
                            legal_moves.append((old_pos, move))
        
        return legal_moves

    def get_legal_moves_for_color_with_promotions(self, color: str) -> List[Tuple[Tuple[int, int], Tuple[int, int], Optional[str]]]:
        """
        Get all legal moves for a given color, including promotion choices.
        Returns list of (start_pos, end_pos, promotion) where promotion is one of q/r/b/n or None.
        """
        legal_moves = []
        promotion_choices = ['q', 'r', 'b', 'n']

        for row in range(8):
            for col in range(8):
                piece = self.get_piece((row, col))
                if piece and piece.color == color:
                    piece_moves = piece.get_legal_moves(self)

                    for move in piece_moves:
                        promos = [None]
                        if piece.__class__.__name__ == 'Pawn' and move[0] in (0, 7):
                            promos = promotion_choices

                        for promo in promos:
                            old_pos = piece.position
                            state = self._apply_temporary_move(piece, old_pos, move, promo)
                            legal = not self.is_in_check(color)
                            self._undo_temporary_move(move, state)

                            if legal:
                                legal_moves.append((old_pos, move, promo))

        return legal_moves
    
    def is_game_over(self, color: str) -> Tuple[bool, str]:
        """
        Check if the game is over for the given color.
        Returns (is_over, reason) where reason is 'checkmate', 'stalemate', or ''
        """
        if self.is_insufficient_material():
            return True, 'draw'

        legal_moves = self.get_legal_moves_for_color_with_promotions(color)
        
        if not legal_moves:  # No legal moves
            if self.is_in_check(color):
                return True, 'checkmate'
            else:
                return True, 'stalemate'

        if self.halfmove_clock >= 100:
            return True, 'draw'
        if self.is_threefold_repetition(color):
            return True, 'draw'
        
        return False, ''
    
            
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
    board.setup_initial_position()
    print(board)
