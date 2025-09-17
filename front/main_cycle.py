# импортируемые библиотеки
import sys
from pathlib import Path

import pygame

current_path = Path(__file__).resolve()
project_root = current_path.parents[1]
sys.path.append(str(project_root))
from InitRender import screen, board, rendering, draw_game_info
from ai.engine import ChessEngine
from chess_logic.board import Board

# Game state variables
cur_color = 'white'
running = True
points_pos = []
chosen_piece = None
clock = pygame.time.Clock()

# AI settings
ai_enabled = False
ai_color = 'black'  # AI plays as black by default
ai_difficulty = 2  # 1=Easy, 2=Medium, 3=Hard, 4=Expert
ai_engine = ChessEngine(depth=ai_difficulty + 1)  # depth 2-5
ai_thinking = False

# Difficulty settings
difficulty_names = {1: "Легкий", 2: "Средний", 3: "Тяжелый", 4: "Эксперт"}
difficulty_depths = {1: 2, 2: 3, 3: 4, 4: 5}

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:  # Press 'A' to toggle AI
                ai_enabled = not ai_enabled
                print(f"ИИ {'включен' if ai_enabled else 'выключен'}")
                if ai_enabled:
                    print(f"ИИ играет за {ai_color}, уровень: {difficulty_names[ai_difficulty]}")
            elif event.key == pygame.K_r:  # Press 'R' to restart
                board = Board()
                board.setup_initial_position()
                cur_color = 'white'
                points_pos = []
                chosen_piece = None
                ai_thinking = False
                rendering()
                print("Игра перезапущена")
            elif event.key == pygame.K_1:  # Easy
                ai_difficulty = 1
                ai_engine = ChessEngine(depth=difficulty_depths[ai_difficulty])
                print(f"Уровень сложности: {difficulty_names[ai_difficulty]}")
            elif event.key == pygame.K_2:  # Medium
                ai_difficulty = 2
                ai_engine = ChessEngine(depth=difficulty_depths[ai_difficulty])
                print(f"Уровень сложности: {difficulty_names[ai_difficulty]}")
            elif event.key == pygame.K_3:  # Hard
                ai_difficulty = 3
                ai_engine = ChessEngine(depth=difficulty_depths[ai_difficulty])
                print(f"Уровень сложности: {difficulty_names[ai_difficulty]}")
            elif event.key == pygame.K_4:  # Expert
                ai_difficulty = 4
                ai_engine = ChessEngine(depth=difficulty_depths[ai_difficulty])
                print(f"Уровень сложности: {difficulty_names[ai_difficulty]}")
        elif event.type == pygame.MOUSEBUTTONDOWN and not ai_thinking:
            # Fix coordinate calculation - convert to 0-based coordinates
            mouse_x, mouse_y = event.pos
            col = (mouse_x - 50) // 81  # Adjust for board offset and cell size
            row = 7 - ((mouse_y - 50) // 81)  # Flip Y axis and adjust
            
            # Ensure coordinates are valid
            if 0 <= row < 8 and 0 <= col < 8:
                cur_pos = (row, col)
                piece = board.grid[row][col]
                
                # If clicking on a piece of the current player and no piece is selected
                if piece and piece.color == cur_color and not chosen_piece:
                    # Get only truly legal moves (not putting king in check)
                    basic_moves = piece.get_legal_moves(board)
                    legal_moves = []
                    
                    for move in basic_moves:
                        # Test if move is legal
                        captured_piece = board.get_piece(move)
                        old_pos = piece.position
                        
                        # Make move temporarily
                        board.grid[old_pos[0]][old_pos[1]] = None
                        board.grid[move[0]][move[1]] = piece
                        piece.position = move
                        
                        # Check if king is in check
                        if not board.is_in_check(piece.color):
                            legal_moves.append(move)
                        
                        # Restore board
                        board.grid[old_pos[0]][old_pos[1]] = piece
                        piece.position = old_pos
                        board.grid[move[0]][move[1]] = captured_piece
                    
                    if legal_moves:  # Only select if piece has legal moves
                        points_pos = legal_moves.copy()
                        chosen_piece = piece
                        rendering()
                        # Draw move indicators
                        for move_row, move_col in legal_moves:
                            # Convert back to screen coordinates
                            screen_x = 50 + move_col * 81 + 40
                            screen_y = 50 + (7 - move_row) * 81 + 40
                            pygame.draw.circle(screen, (102, 102, 102), (screen_x, screen_y), 15)
                        pygame.display.update()
                
                # If clicking on a valid move destination
                elif chosen_piece and cur_pos in points_pos:
                    # Make the move
                    if board.move_piece(chosen_piece.position, cur_pos):
                        # Switch turns
                        cur_color = 'black' if cur_color == 'white' else 'white'
                        
                        # Check for game over conditions
                        game_over, reason = board.is_game_over(cur_color)
                        if game_over:
                            if reason == 'checkmate':
                                winner = 'White' if cur_color == 'black' else 'Black'
                                print(f"Checkmate! {winner} wins!")
                            elif reason == 'stalemate':
                                print("Stalemate! It's a draw!")
                    # Clear selection
                    points_pos = []
                    chosen_piece = None
                    rendering()
                
                # Clear selection if clicking elsewhere
                else:
                    points_pos = []
                    chosen_piece = None
                    rendering()
    
    # AI move logic
    if ai_enabled and cur_color == ai_color and not ai_thinking:
        ai_thinking = True
        print(f"AI ({ai_color}) is thinking...")
        
        # Get AI move
        ai_move = ai_engine.get_best_move(board, ai_color)
        
        if ai_move:
            start_pos, end_pos = ai_move
            print(f"AI moves: {start_pos} -> {end_pos}")
            
            if board.move_piece(start_pos, end_pos):
                # Switch turns back to human
                cur_color = 'black' if cur_color == 'white' else 'white'
                
                # Check for game over conditions
                game_over, reason = board.is_game_over(cur_color)
                if game_over:
                    if reason == 'checkmate':
                        winner = 'White' if cur_color == 'black' else 'Black'
                        print(f"Checkmate! {winner} wins!")
                    elif reason == 'stalemate':
                        print("Stalemate! It's a draw!")
                
                rendering()
            else:
                print("AI move failed!")
        else:
            print("AI has no legal moves!")
            
        ai_thinking = False
    
    # Draw game information
    draw_game_info(screen, cur_color, ai_enabled, ai_color, ai_thinking, ai_difficulty, difficulty_names)
    
    clock.tick(60)
    pygame.display.flip()

pygame.quit()
