from sounds import SoundManager
import pygame


class ScoreBoard:

    SCORE_WHITE = (255, 255, 255)

    def __init__(self, screen, pos=(0, 0)):
        self.screen = screen
        self.current_score = 0
        self.color = ScoreBoard.SCORE_WHITE
        self.score_font = pygame.font.Font('fonts/emulogic.ttf', 24)
        self.image = None
        self.rect = None
        self.prep_image()
        self.pos = pos
        self.position()

    def position(self):
        self.rect.centerx, self.rect.centery = self.pos

    def prep_image(self):
        score_str = str(self.current_score)
        self.image = self.score_font.render(score_str, True, self.color)
        self.rect = self.image.get_rect()

    def update(self, n_score):
        self.current_score += n_score
        self.prep_image()
        self.position()

    def reset(self):
        self.current_score = 0
        self.prep_image()
        self.position()

    def blit(self):
        self.screen.blit(self.image, self.rect)


class ScoreController:
    def __init__(self, screen, items_image, sb_pos=(0, 0), itc_pos=(0, 0)):
        self.current_score = 0
        self.level = 1
        self.high_scores = []
        self.scoreboard = ScoreBoard(screen=screen, pos=sb_pos)
        self.item_counter = ItemCounter(screen=screen, pos=itc_pos, image_name=items_image)

    def increment_level(self, up=1):
        self.level += up

    def reset_level(self):
        self.level = 1
        self.scoreboard.reset()
        self.item_counter.reset_items()

    def add_score(self, score, items=None):
        self.scoreboard.update(score)
        self.current_score = self.scoreboard.current_score
        if items:
            self.item_counter.add_items(items)

    def blit(self):
        self.scoreboard.blit()
        self.item_counter.blit()


class ItemCounter:
    def __init__(self, screen, image_name, pos=(0, 0)):
        self.screen = screen
        self.counter = 0
        self.item_font = pygame.font.Font('fonts/emulogic.ttf', 24)
        self.color = ScoreBoard.SCORE_WHITE
        self.text_image = None
        self.text_rect = None
        self.pos = pos
        self.prep_image()

    def add_items(self, n_items):
        self.counter += n_items
        self.prep_image()

    def reset_items(self):
        self.counter = 0
        self.prep_image()

    def prep_image(self):
        text = str(self.counter) + ' X '
        self.text_image = self.item_font.render(text, True, self.color)
        self.text_rect = self.text_image.get_rect()
        self.position()

    def position(self):
        self.text_rect.centerx, self.text_rect.centery = self.pos
        x_offset = int(self.text_rect.width * 1.25)

    def blit(self):
        self.screen.blit(self.text_image, self.text_rect)


class LevelTransition:
    TRANSITION_CHANNEL = 4

    def __init__(self, screen, score_controller, transition_time=5000):
        self.screen = screen
        self.score_controller = score_controller
        self.sound = SoundManager(['pacman_beginning.wav'], keys=['transition'],
                                  channel=LevelTransition.TRANSITION_CHANNEL, volume=0.6)
        self.score_font = pygame.font.Font('fonts/emulogic.ttf', 24)
        ready_pos = screen.get_width() // 2, int(screen.get_height() * 0.65)
        self.level_msg = None
        self.level_msg_rect = None
        self.transition_time = transition_time     # total time to wait until the transition ends
        self.transition_begin = None
        self.transition_show = False

    def prep_level_msg(self):
        text = 'level ' + str(self.score_controller.level)
        self.level_msg = self.score_font.render(text, True, ScoreBoard.SCORE_WHITE)
        self.level_msg_rect = self.level_msg.get_rect()
        level_pos = self.screen.get_width() // 2, self.screen.get_height() // 2
        self.level_msg_rect.centerx, self.level_msg_rect.centery = level_pos

    def set_show_transition(self):
        self.prep_level_msg()
        self.transition_begin = pygame.time.get_ticks()
        self.transition_show = True
        self.sound.play('transition')

    def draw(self):
        if abs(self.transition_begin - pygame.time.get_ticks()) > self.transition_time:
            self.transition_show = False
        else:
            self.screen.fill((0, 0, 0))
            self.screen.blit(self.level_msg, self.level_msg_rect)
