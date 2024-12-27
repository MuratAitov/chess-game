import sys
from pathlib import Path

import pygame

current_path = Path(__file__).resolve()
project_root = current_path.parents[1]
sys.path.append(str(project_root))
from chess_logic.board import Board

# общие переменные
cur_color = 'white'
assets = {}
start_size = w, h = 700, 700
running = True
# для флажков
chosen_piece = ''
points_pos = []


def rendering(assets):
    global screen
    global board
    screen.fill((255, 255, 255))
    # главное поле
    Main_field = pygame.image.load('images/doska.jpg')
    Main_field = pygame.transform.scale(Main_field, (700, 700))
    Main_field_rect = Main_field.get_rect(bottomright=(700, 700))
    screen.blit(Main_field, Main_field_rect)

    # отрисовка фигур
    for i in range(8):
        for j in range(8):
            if board.grid[i][j]:
                image = assets[str(board.grid[i][j])]
                piece_image = pygame.image.load('../../images/Start_monopoly_image.webp')
                piece_image = pygame.transform.scale(piece_image, (76, 76))
                piece_image_rect = piece_image.get_rect(bottomleft=(((j - 1) * 76 + 51, 120), 662 - (i - 1) * 76))
                screen.blit(piece_image, piece_image_rect)
    pygame.display.update()


def init():
    global screen
    global board
    pygame.init()

    screen = pygame.display.set_mode(start_size)
    screen.fill((255, 255, 255))
    pygame.display.set_caption("chess")
    board = Board()
    board.setup_initial_position()
    rendering(assets)
