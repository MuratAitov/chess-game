import pygame
import pygame.gfxdraw

class EvaluationBar:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.center_y = y + height // 2
        self.evaluation = 0
        self.target_evaluation = 0
        self.smoothing_speed = 0.1  # Скорость анимации
        
        # Цвета
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.GRAY = (128, 128, 128)
        self.POSITIVE_COLOR = (113, 173, 71)  # Зеленый для белых
        self.NEGATIVE_COLOR = (40, 40, 40)    # Темный для черных

    def update(self, evaluation):
        """Обновляет целевое значение эвалюации"""
        # Ограничиваем значения для визуализации
        self.target_evaluation = max(min(evaluation, 2000), -2000)

    def animate(self):
        """Плавная анимация изменения значения"""
        diff = self.target_evaluation - self.evaluation
        self.evaluation += diff * self.smoothing_speed

    def draw(self, surface):
        """Отрисовка полоски эвалюации"""
        # Фон
        pygame.draw.rect(surface, self.GRAY, 
                        (self.x, self.y, self.width, self.height))
        
        # Вычисляем высоту заполнения
        max_value = 2000
        fill_height = int((self.evaluation + max_value) * 
                         self.height / (2 * max_value))
        
        # Заполняем цветом в зависимости от эвалюации
        if self.evaluation >= 0:
            color = self.POSITIVE_COLOR
            rect = (self.x, self.center_y - fill_height, 
                   self.width, fill_height)
        else:
            color = self.NEGATIVE_COLOR
            rect = (self.x, self.center_y, 
                   self.width, fill_height)
            
        pygame.draw.rect(surface, color, rect)
        
        # Центральная линия
        pygame.draw.line(surface, self.WHITE,
                        (self.x, self.center_y),
                        (self.x + self.width, self.center_y), 1)
        
        # Отображаем числовое значение
        self._draw_evaluation_text(surface)

    def _draw_evaluation_text(self, surface):
        """Отоб��ажает числовое значение эвалюации"""
        font = pygame.font.Font(None, 20)
        eval_text = f"{abs(self.evaluation/100):.1f}"
        
        text = font.render(eval_text, True, self.WHITE)
        text_rect = text.get_rect()
        
        # Позиционируем текст справа от полоски
        text_x = self.x + self.width + 5
        if self.evaluation >= 0:
            text_y = self.center_y - text_rect.height - 2
        else:
            text_y = self.center_y + 2
            
        surface.blit(text, (text_x, text_y))

class DetailedEvaluation:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.components = {
            "Material": 0,
            "Position": 0,
            "Pawn Structure": 0,
            "King Safety": 0,
            "Mobility": 0
        }
        
    def update(self, evaluation_components):
        """Обновляет значения компонентов эвалюации"""
        self.components.update(evaluation_components)

    def draw(self, surface):
        """Отрисовка детальной информации об эвалюации"""
        font = pygame.font.Font(None, 20)
        y_offset = self.y
        
        for component, value in self.components.items():
            text = f"{component}: {value/100:.2f}"
            text_surface = font.render(text, True, (255, 255, 255))
            surface.blit(text_surface, (self.x, y_offset))
            y_offset += 25

# Пример использования:
"""
# В основном игровом цикле:

evaluation_bar = EvaluationBar(750, 100, 30, 400)
detailed_eval = DetailedEvaluation(750, 520, 200, 150)

while running:
    # Обновление состояния доски
    current_evaluation = evaluator.evaluate_position(board)
    evaluation_components = {
        "Material": evaluator.evaluate_material(board),
        "Position": evaluator.evaluate_piece_positions(board),
        "Pawn Structure": evaluator.evaluate_pawn_structure(board),
        "King Safety": evaluator.evaluate_king_safety(board),
        "Mobility": evaluator.evaluate_mobility(board)
    }
    
    # Обновление визуализации
    evaluation_bar.update(current_evaluation)
    evaluation_bar.animate()
    detailed_eval.update(evaluation_components)
    
    # Отрисовка
    evaluation_bar.draw(screen)
    detailed_eval.draw(screen)
    
    pygame.display.flip()
""" 