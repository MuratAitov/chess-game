# импортируемые библиотеки
import sys
from pathlib import Path

import pygame

current_path = Path(__file__).resolve()
project_root = current_path.parents[1]
sys.path.append(str(project_root))
from InitRender import cur_color, running, points_pos, chosen_piece, screen, board, rendering

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            start_running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            cur_pos = (cur_alpha, cur_num) = ((event.pos[0] - 51) // 76 + 1, (662 - event.pos[1]) // 76 + 1)
            piece = board.grid[cur_alpha][cur_num]
            if (piece) and (cur_pos not in points_pos) and (piece.color == cur_color) and chosen_piece:
                if not points_pos:
                    rendering()
                moves = piece.get_legal_moves()
                points_pos = moves.copy()
                chosen_piece = piece
                for i in moves:
                    pygame.draw.circle(screen, (102, 102, 102), (i + 38, i + 38), 9)
            elif (cur_pos in points_pos) and (piece.color == cur_color):
                board.move_piece(chosen_piece.position, cur_pos)
                rendering()
            elif points_pos:
                points_pos = []
                chosen_piece = ''
                rendering()

        pygame.display.flip()
