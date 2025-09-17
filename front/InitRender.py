import sys
from pathlib import Path

import pygame

current_path = Path(__file__).resolve()
project_root = current_path.parents[1]
sys.path.append(str(project_root))
from chess_logic.board import Board

# общие переменные
assets = {}
start_size = w, h = 1100, 750


def rendering():
    global screen
    global board
    screen.fill((50, 50, 50))
    
    # Draw main board  
    board_path = Path(__file__).parent / 'images' / 'boards' / 'blue.png'
    Main_field = pygame.image.load(str(board_path))
    Main_field = pygame.transform.scale(Main_field, (650, 650))
    Main_field_rect = Main_field.get_rect(bottomright=(700, 700))
    screen.blit(Main_field, Main_field_rect)

    # Draw pieces
    for row in range(8):
        for col in range(8):
            if board.grid[row][col]:
                piece_filename = repr(board.grid[row][col]) + '.svg'
                piece_path = Path(__file__).parent / 'images' / 'pieces' / 'classic' / piece_filename
                piece_image = pygame.image.load(str(piece_path))
                # Calculate correct screen position: row 0 at bottom, row 7 at top
                screen_x = 50 + col * 81
                screen_y = 50 + (7 - row) * 81  # Flip Y axis so row 0 is at bottom
                piece_image_rect = piece_image.get_rect(bottomleft=(screen_x, screen_y + 81))
                screen.blit(piece_image, piece_image_rect)
    
    # Highlight kings in check
    for color in ['white', 'black']:
        if board.is_in_check(color):
            # Find the king
            for row in range(8):
                for col in range(8):
                    piece = board.get_piece((row, col))
                    if piece and piece.__class__.__name__ == 'King' and piece.color == color:
                        # Draw red highlight around king in check
                        king_x = 50 + col * 81 + 10
                        king_y = 50 + (7 - row) * 81 + 10
                        pygame.draw.rect(screen, (255, 0, 0), (king_x, king_y, 61, 61), 3)
                        break
    
    pygame.display.update()

def draw_game_info(screen, cur_color, ai_enabled, ai_color, ai_thinking, ai_difficulty=2, difficulty_names=None):
    """Draw game information on the side panel"""
    font = pygame.font.Font(None, 24)
    small_font = pygame.font.Font(None, 20)
    
    if difficulty_names is None:
        difficulty_names = {1: "Легкий", 2: "Средний", 3: "Тяжелый", 4: "Эксперт"}
    
    # Current turn
    turn_text = font.render(f"Ход: {cur_color.capitalize()}", True, (255, 255, 255))
    screen.blit(turn_text, (720, 50))
    
    # AI status
    if ai_enabled:
        ai_text = font.render(f"ИИ: {ai_color.capitalize()}", True, (0, 255, 0))
        screen.blit(ai_text, (720, 80))
        
        # AI difficulty
        diff_text = small_font.render(f"Уровень: {difficulty_names[ai_difficulty]}", True, (0, 255, 0))
        screen.blit(diff_text, (720, 105))
        
        if ai_thinking:
            thinking_text = small_font.render("ИИ думает...", True, (255, 255, 0))
            screen.blit(thinking_text, (720, 125))
    else:
        ai_text = font.render("ИИ: Выключен", True, (255, 0, 0))
        screen.blit(ai_text, (720, 80))
    
    # Check status
    check_y = 150 if ai_enabled else 110
    for i, color in enumerate(['white', 'black']):
        if board.is_in_check(color):
            check_text = font.render(f"{color.capitalize()} - ШАХ!", True, (255, 100, 100))
            screen.blit(check_text, (720, check_y + i * 25))
    
    # Controls
    controls = [
        "Управление:",
        "A - Вкл/выкл ИИ",
        "R - Новая игра",
        "1-4 - Уровень ИИ",
        "",
        "Клик - выбрать фигуру",
        "Клик на подсветку - ход"
    ]
    
    y_offset = 220
    for line in controls:
        if line == "Управление:":
            control_text = font.render(line, True, (255, 255, 255))
        else:
            control_text = small_font.render(line, True, (200, 200, 200))
        screen.blit(control_text, (720, y_offset))
        y_offset += 22



pygame.init()
pygame.font.init()  # Initialize font module
screen = pygame.display.set_mode(start_size)
screen.fill((50, 50, 50))
pygame.display.set_caption("Chess Game - Press A for AI, R to Restart")
board = Board()
board.setup_initial_position()
rendering()

if __name__ == '__main__':
    pass
