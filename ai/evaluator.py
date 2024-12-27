# Пример: Piece-Square Table для белой пешки (упрощённый)
# Индексы [row][col]
PAWN_PST = [
    [0,  0,  0,  0,  0,  0,  0,  0],
    [50, 50, 50, 50, 50, 50, 50, 50],
    [10, 10, 20, 30, 30, 20, 10, 10],
    [5,  5, 10, 25, 25, 10,  5,  5],
    [0,  0,  0, 20, 20,  0,  0,  0],
    [5, -5,-10,  0,  0,-10, -5,  5],
    [5, 10, 10,-20,-20, 10, 10,  5],
    [0,  0,  0,  0,  0,  0,  0,  0]
]

KNIGHT_PST = [
    [-50,-40,-30,-30,-30,-30,-40,-50],
    [-40,-20,  0,  0,  0,  0,-20,-40],
    [-30,  0, 10, 15, 15, 10,  0,-30],
    [-30,  5, 15, 20, 20, 15,  5,-30],
    [-30,  0, 15, 20, 20, 15,  0,-30],
    [-30,  5, 10, 15, 15, 10,  5,-30],
    [-40,-20,  0,  5,  5,  0,-20,-40],
    [-50,-40,-30,-30,-30,-30,-40,-50]
]

class ChessEvaluator:
    def __init__(self):
        self.PIECE_VALUES = {
            'Pawn': 100,
            'Knight': 320,
            'Bishop': 330,
            'Rook': 500,
            'Queen': 900,
            'King': 20000
        }
        
        # Веса для разных компонентов оценки
        self.MATERIAL_WEIGHT = 1.0
        self.POSITION_WEIGHT = 0.5
        self.PAWN_STRUCTURE_WEIGHT = 0.3
        self.CHECK_WEIGHT = 1.0

    def evaluate_material(self, board):
        """Оценка материального преимущества"""
        score = 0
        for row in range(8):
            for col in range(8):
                piece = board.get_piece((row, col))
                if piece:
                    value = self.PIECE_VALUES[piece.__class__.__name__]
                    if piece.color == 'black':
                        score += value
                    else:
                        score -= value
        return score * self.MATERIAL_WEIGHT

    def evaluate_piece_moves(self, board):
        """Оценка контроля важных клеток"""
        score = 0
        square_values = {
            (3, 3): 1.0, (3, 4): 1.0, (4, 3): 1.0, (4, 4): 1.0,  # центр
            (2, 2): 0.5, (2, 3): 0.5, (2, 4): 0.5, (2, 5): 0.5,  # расширенный центр
            (3, 2): 0.5, (3, 5): 0.5,
            (4, 2): 0.5, (4, 5): 0.5,
            (5, 2): 0.5, (5, 3): 0.5, (5, 4): 0.5, (5, 5): 0.5
        }

        for row in range(8):
            for col in range(8):
                piece = board.get_piece((row, col))
                if piece:
                    if (row, col) in square_values:
                        value = square_values[(row, col)]
                        if piece.color == 'black':
                            score += value
                        else:
                            score -= value
        return score * self.POSITION_WEIGHT

    def evaluate_pawn_structure(self, board):
        """Оценка пешечной структуры"""
        score = 0
        
        for row in range(1, 7):  # пропускаем крайние ряды
            for col in range(8):
                piece = board.get_piece((row, col))
                if piece and piece.__class__.__name__ == 'Pawn':
                    # Проверяем соседние пешки по диагонали
                    for d_col in [-1, 1]:
                        if 0 <= col + d_col <= 7:
                            if piece.color == 'black':
                                neighbor = board.get_piece((row - 1, col + d_col))
                            else:
                                neighbor = board.get_piece((row + 1, col + d_col))
                            
                            if (neighbor and 
                                neighbor.__class__.__name__ == 'Pawn' and 
                                neighbor.color == piece.color):
                                if piece.color == 'black':
                                    score += 1
                                else:
                                    score -= 1
                                    
        return score * self.PAWN_STRUCTURE_WEIGHT

    def is_in_check(self, board, color):
        """Проверка шаха"""
        # Предполагая, что в вашем классе Board есть метод is_in_check
        if hasattr(board, 'is_in_check'):
            if board.is_in_check(color):
                return 1 if color == 'white' else -1
        return 0
    def evaluate_position(self, board):
        """Общая оценка позиции"""
        # Разделим оценку на компоненты для лучшей читаемости
        material_score = self.evaluate_material(board) / 100
        piece_moves_score = self.evaluate_piece_moves(board) / 100
        pawn_structure_score = self.evaluate_pawn_structure(board) / 100
        piece_square_score = self.evaluate_piece_square_tables(board) / 100
        
        # Оценка шахов
        white_check = self.is_in_check(board, 'white') * self.CHECK_WEIGHT / 100
        black_check = self.is_in_check(board, 'black') * self.CHECK_WEIGHT / 100
        check_score = white_check + black_check

        # Суммируем все компоненты
        total_score = (
            material_score +
            piece_moves_score + 
            pawn_structure_score +
            piece_square_score +
            check_score
        )

        return total_score

    def evaluate_piece_square_tables(self, board):
        score = 0
        piece_square_tables = {
            'Pawn': PAWN_PST,
            'Knight': KNIGHT_PST,
            # Add other piece tables as needed
        }
        
        for row in range(8):
            for col in range(8):
                piece = board.get_piece((row, col))
                if piece:
                    piece_type = piece.__class__.__name__
                    if piece_type in piece_square_tables:
                        pst = piece_square_tables[piece_type]
                        
                        # White pieces read the table normally
                        if piece.color == 'white':
                            score += pst[7 - row][col]  # Flip row for white's perspective
                        # Black pieces read the table from their perspective
                        else:
                            score -= pst[row][col]
        
        return score * 0.1  # Weight factor to balance with other evaluation components


if __name__ == "__main__":
    
    import sys
    from pathlib import Path

    current_path = Path(__file__).resolve()
    project_root = current_path.parents[1]
    if str(project_root) not in sys.path:
        sys.path.append(str(project_root))

    print("Project Root Path:", project_root)
        
    from chess_logic.board import Board  
    from chess_logic.pieces import Pawn, Rook, Knight, Bishop, Queen, King
    
    # Create test boards with different positions
    def create_test_board(fen_string):
        board = Board()
        board.load_from_fen(fen_string)  # Assuming your Board class has this method
        return board
    
    # Test different board layouts
    test_positions = {
        "Starting Position": lambda b: b.setup_initial_position(),
        "Material Advantage": lambda b: [
            b.place_test_pieces(Rook('white', (0,0)), (0,0)),
            b.place_test_pieces(Knight('white', (0,1)), (0,1)),
            b.place_test_pieces(Bishop('white', (0,2)), (0,2)), 
            b.place_test_pieces(King('white', (0,4)), (0,4)),
            b.place_test_pieces(Bishop('white', (0,5)), (0,5)),
            b.place_test_pieces(Knight('white', (0,6)), (0,6)),
            b.place_test_pieces(Rook('white', (0,7)), (0,7)),
            b.place_test_pieces(King('black', (7,4)), (7,4)),
            b.place_test_pieces(Queen('black', (7,3)), (7,3))
        ],
        "Center Control": lambda b: [
            b.place_test_pieces(Pawn('white', (3,3)), (3,3)),
            b.place_test_pieces(Pawn('white', (3,4)), (3,4)),
            b.place_test_pieces(Knight('white', (2,3)), (2,3)),
            b.place_test_pieces(King('white', (0,4)), (0,4)),
            b.place_test_pieces(Pawn('black', (4,3)), (4,3)),
            b.place_test_pieces(Pawn('black', (4,4)), (4,4)), 
            b.place_test_pieces(King('black', (7,4)), (7,4))
        ],
        "Pawn Structure": lambda b: [
            b.place_test_pieces(Pawn('white', (1,3)), (1,3)),
            b.place_test_pieces(Pawn('white', (1,4)), (1,4)),
            b.place_test_pieces(Pawn('white', (2,3)), (2,3)),
            b.place_test_pieces(King('white', (0,4)), (0,4)),
            b.place_test_pieces(Pawn('black', (6,3)), (6,3)),
            b.place_test_pieces(Pawn('black', (6,4)), (6,4)),
            b.place_test_pieces(Pawn('black', (5,3)), (5,3)),
            b.place_test_pieces(King('black', (7,4)), (7,4))
        ],
        "Development": lambda b: [
            b.place_test_pieces(Knight('white', (2,2)), (2,2)),
            b.place_test_pieces(Bishop('white', (2,5)), (2,5)),
            b.place_test_pieces(Pawn('white', (1,4)), (1,4)),
            b.place_test_pieces(King('white', (0,4)), (0,4)),
            b.place_test_pieces(Knight('black', (7,1)), (7,1)),
            b.place_test_pieces(Bishop('black', (7,2)), (7,2)),
            b.place_test_pieces(King('black', (7,4)), (7,4))
        ]
    }

    evaluator = ChessEvaluator()

    # Evaluate each position
    for position_name, setup_fn in test_positions.items():
        board = Board()
        setup_fn(board)
        score = evaluator.evaluate_position(board)
        
        print(f"\nPosition: {position_name}")
        print("Board:")
        print(board)
        print(f"Evaluation score: {score}")
        print("Component breakdown:")
        print(f"- Material: {evaluator.evaluate_material(board)}")
        print(f"- Position: {evaluator.evaluate_piece_moves(board)}")
        print(f"- Pawn Structure: {evaluator.evaluate_pawn_structure(board)}")
        print("-" * 50)
