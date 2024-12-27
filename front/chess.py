# импортируемые библиотеки
import sys
from pathlib import Path

import pygame

current_path = Path(__file__).resolve()
project_root = current_path.parents[1]
sys.path.append(str(project_root))
from chess_logic.board import Board
from InitRender import *


init()


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
