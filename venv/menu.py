import pygame
from pacman import Pacman
from setup import Card


class Menu:
    def __init__(self, screen):
        self.screen = screen

        self.title = Card(screen, 'Pacman', pos=(int(screen.get_width() * 0.5),
                                                             int(screen.get_height() * 0.15)))

        self.play_button = Button(screen, 'Play Game', pos=(int(screen.get_width() * 0.5),
                                                            int(screen.get_height() * 0.8)),
                                  alt_color=Pacman.PAC_YELLOW)
        self.high_scores_button = Button(screen, 'High Scores', pos=(int(screen.get_width() * 0.5),
                                                                     int(screen.get_height() * 0.9)),
                                         alt_color=Pacman.PAC_YELLOW)
        self.high_score_menu = False
        self.ready_to_play = False

    def check_buttons(self):
        self.ready_to_play = self.play_button.check_button(*pygame.mouse.get_pos())
        self.high_score_screen = self.high_scores_button.check_button(*pygame.mouse.get_pos())



    def blit(self):
        self.title.blit()
        self.play_button.blit()
        self.high_scores_button.blit()


class HighScoreScreen:
    def __init__(self, screen, score_controller, size=24, background=(0, 0, 0)):
        self.screen = screen
        self.score_controller = score_controller
        self.back_button = Button(screen, 'Back', pos=(int(screen.get_width() * 0.25), int(screen.get_height() * 0.9)),
                                  alt_color=Pacman.PAC_YELLOW)
        self.font = pygame.font.Font('fonts/emulogic.ttf', size)
        self.images = []
        self.active = False
        self.background = background
        self.prep_images()
        self.position()

    def position(self):
        y_offset = int(self.screen.get_height() * 0.1)
        for image in self.images:
            image[1].centerx = int(self.screen.get_width() * 0.5)
            image[1].centery = y_offset
            y_offset += int(image[1].height * 2)

    def check_done(self):
        self.back_button.alter_text_color(*pygame.mouse.get_pos())
        self.active = not self.back_button.check_button(*pygame.mouse.get_pos())

    def prep_images(self):
        self.images.clear()
        for num, score in enumerate(self.score_controller.high_scores):
            image = self.font.render('#' + str(num + 1) + ' :  ' + str(score), True, (255, 255, 255))
            rect = image.get_rect()
            self.images.append([image, rect])

    def blit(self):
        for image in self.images:
            self.screen.blit(*image)
        self.back_button.blit()


class Button:
    def __init__(self, screen, msg, size=24, pos=(0, 0), text_color=(255, 255, 255), alt_color=(0, 255, 0)):
        self.screen = screen
        self.screen_rect = screen.get_rect()

        self.text_color = text_color
        self.font = pygame.font.Font('fonts/emulogic.ttf', size)
        self.pos = pos

        self.button_message = msg
        self.msg_image, self.msg_image_rect = None, None
        self.prep_msg(self.text_color)

    def check_button(self, mouse_x, mouse_y):
        if self.msg_image_rect.collidepoint(mouse_x, mouse_y):
            return True
        else:
            return False


    def prep_msg(self, color):
        self.msg_image = self.font.render(self.button_message, True, color)
        self.msg_image_rect = self.msg_image.get_rect()
        self.msg_image_rect.centerx, self.msg_image_rect.centery = self.pos

    def blit(self):
        self.screen.blit(self.msg_image, self.msg_image_rect)
