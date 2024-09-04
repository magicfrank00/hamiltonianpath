import pygame


class Button:
    def __init__(self, rect, color, hover_color, text, text_color, font):
        self.rect = pygame.Rect(rect)
        self.color = color
        self.hover_color = hover_color
        self.text = text
        self.text_color = text_color
        self.font = font
        self.hovered = False

    def draw(self, screen):
        current_color = self.hover_color if self.hovered else self.color

        pygame.draw.rect(screen, current_color, self.rect, border_radius=12)

        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def check_hover(self, mouse_pos):
        self.hovered = self.rect.collidepoint(mouse_pos)

    def check_click(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)
