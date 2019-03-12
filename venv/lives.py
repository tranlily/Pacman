import pygame
from score import ScoreBoard
from spritesheet import ImageManager


class Counter:
    def __init__(self, screen, initial_count=3, ct_pos=(0, 0), images_size=(32, 32)):
        self.screen = screen
        self.pacman_lives = initial_count
        self.lives = initial_count
        sheet_images = ImageManager('pacman-horiz.png', sheet=True, pos_offsets=[(0, 0, 32, 32),
                                                                                 (32, 0, 32, 32),
                                                                                 (0, 32, 32, 32),
                                                                                 (32, 32, 32, 32),
                                                                                 (0, 64, 32, 32)],
                                    resize=images_size).all_images()
        life_image = sheet_images[-1]
        self.life_display = ImageRow(screen, life_image, initial_count, 'Lives', ct_pos)

    def decrement(self):
        self.lives -= 1
        self.life_display.update(self.lives)

    def reset_counter(self):
        self.lives = self.pacman_lives
        self.life_display.update(self.lives)

    def blit(self):
        self.life_display.blit()


class ImageRow:
    def __init__(self, screen, img, count, label, pos=(0, 0), color=ScoreBoard.SCORE_WHITE):
        self.screen = screen
        if isinstance(img, str):
            self.image = pygame.image.load('images/' + img)
        else:
            self.image = img
        self.image_count = None
        self.image_rects = None
        self.color = color
        self.font = pygame.font.Font('fonts/emulogic.ttf', 24)
        self.text = label
        self.text_image = None
        self.text_image_rect = None
        self.pos = pos
        self.update(count)

    def position(self):
        self.text_image_rect.centerx, self.text_image_rect.centery = self.pos
        x_pos = self.text_image_rect.centerx + int(self.text_image_rect.width * 0.75)
        for rect in self.image_rects:
            rect.centerx, rect.centery = x_pos, self.pos[1]
            x_pos += rect.width

    def render_text(self):
        self.text_image = self.font.render(self.text, True, self.color)
        self.text_image_rect = self.text_image.get_rect()

    def update(self, n_count):
        self.image_count = n_count
        self.image_rects = []
        rect = self.image.get_rect()
        for i in range(n_count):
            self.image_rects.append(rect.copy())
        self.render_text()
        self.position()

    def blit(self):
        self.screen.blit(self.text_image, self.text_image_rect)
        for rect in self.image_rects:
            self.screen.blit(self.image, rect)
