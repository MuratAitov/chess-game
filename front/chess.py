# импортируемые библиотеки
import sys
from pathlib import Path

import pygame

current_path = Path(__file__).resolve()
project_root = current_path.parents[1]
sys.path.append(str(project_root))
from chess_logic.board import Board


# функции
def rendering(assets):
    global screen
    global board
    screen.fill((255, 255, 255))
    # главное поле
    Main_field = pygame.image.load('../../images/doska.jpg')
    Main_field = pygame.transform.scale(Main_field, (700, 700))
    Main_field_rect = Main_field.get_rect(bottomright=(700, 700))
    screen.blit(Main_field, Main_field_rect)

    # отрисовка фигур
    for i in range(8):
        for j in range(8):
            if board.grid[i][j][0]:
                image = assets[str(board.grid[i][j])[0]]
                piece_image = pygame.image.load('../../images/Start_monopoly_image.webp')
                piece_image = pygame.transform.scale(piece_image, (76, 76))
                piece_image_rect = piece_image.get_rect(bottomleft=(((j - 1) * 76 + 51, 120), 662 - (i - 1) * 76))
                screen.blit(piece_image, piece_image_rect)
    pygame.display.update()


# общие переменные
cur_color = 'white'
assets = {}
start_size = w, h = 700, 700
running = True

# для флажков
chosen_fig = ''
points_piece = []

# общая инициализация
pygame.init()

screen = pygame.display.set_mode(start_size)
screen.fill((255, 255, 255))
pygame.display.set_caption("chess")
board = Board()
board.setup_initial_position()
rendering(assets)

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            start_running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            cur_alpha = (event.pos[0] - 51) // 76 + 1
            cur_num = (662 - event.pos[1]) // 76 + 1
            piece = board.grid[cur_alpha][cur_num]
            if piece:
                if piece.color == cur_color:
                    moves = piece.get_legal_moves()
                    points_pos = moves.copy()
                    chosen_piece = piece
                    for i in moves:
                        pygame.draw.circle(screen, (102, 102, 102), (i + 38, i + 38), 9)

                if (cur_alpha, cur_num) in points_pos:
                    board.move_piece()

        pygame.display.flip()
