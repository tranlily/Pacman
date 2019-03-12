import pygame
from spritesheet import ImageManager
from score import ScoreBoard


class Intro:
    def __init__(self, screen):
        self.screen = screen
        self.ghost_intros = [
            ChaseScene(screen, chasers=['blinky.png', 'pinky.png', 'inky.png', 'clyde.png'],
                       chased=['pacman-horiz.png'], chaser_detail='eyes.png'),
            ChaseScene(screen, chasers=['ghost_blue.png', 'ghost_white.png', 'ghost_blue.png', 'ghost_white.png'],
                       chased=['pacman-horiz.png'], reverse=True),
            GhostIntro(screen, 'blinky.png', 'BLiNKY'),
            GhostIntro(screen, 'pinky.png', 'PiNKY'),
            GhostIntro(screen, 'inky.png', 'iNKY'),
            GhostIntro(screen, 'clyde.png', 'CLYDE')
        ]
        self.run = set()
        self.intro_index = 0
        self.last_intro_start = None
        self.intro_time = 5000

    def update(self):
        if not self.last_intro_start:
            self.last_intro_start = pygame.time.get_ticks()
        elif abs(self.last_intro_start - pygame.time.get_ticks()) > self.intro_time:
            self.run.add(self.intro_index)
            self.intro_index = (self.intro_index + 1) % len(self.ghost_intros)
            self.last_intro_start = pygame.time.get_ticks()
        if self.intro_index in (0, 1) and self.intro_index in self.run:
            self.ghost_intros[self.intro_index].reset_positions()
            self.run.remove(self.intro_index)
        self.ghost_intros[self.intro_index].update()

    def blit(self):
        self.ghost_intros[self.intro_index].blit()


class GhostIntro:
    def __init__(self, screen, g_file, name):
        self.screen = screen
        self.ghost_names = Card(screen, name, pos=(screen.get_width() // 2, screen.get_height() // 2))
        self.ghost_animate = Animation(screen, g_file, sheet_offsets=[(0, 0, 32, 32), (0, 32, 32, 32)],
                                     pos=(self.ghost_names.rect.right + self.ghost_names.rect.width // 2,
                                          screen.get_height() // 2),
                                     detail='eyes.png',
                                     frame_delay=300)

    def update(self):
        self.ghost_animate.update()

    def blit(self):
        self.ghost_names.blit()
        self.ghost_animate.blit()


class Card(pygame.sprite.Sprite):
    def __init__(self, screen, text,  pos=(0, 0), color=ScoreBoard.SCORE_WHITE, size=42):
        super().__init__()
        self.screen = screen
        self.text = text
        self.color = color
        self.font = pygame.font.Font('fonts/emulogic.ttf', size)
        self.image = None
        self.rect = None
        self.pos = pos
        self.prep_image()

    def position(self, n_pos=None):
        if not n_pos:
            self.rect.centerx, self.rect.centery = self.pos
        else:
            self.rect.centerx, self.rect.centery = n_pos

    def prep_image(self):
        self.image = self.font.render(self.text, True, self.color)
        self.rect = self.image.get_rect()
        self.position()

    def blit(self):
        self.screen.blit(self.image, self.rect)


class ChaseScene:
    def __init__(self, screen, chasers, chased, reverse=False, speed=10, chaser_detail=None, chased_detail=None):
        self.screen = screen
        self.chasers = []
        self.chased = []
        self.x_start = 0 if not reverse else screen.get_width()
        self.intro_speed = speed if not reverse else -speed
        self.chaser_positions = []
        self.chased_positions = []
        self.y_pos = (screen.get_height() // 2)
        x_offset = self.x_start
        for chaser in chasers:
            self.chaser_positions.append(x_offset)
            animation = Animation(screen, chaser, sheet_offsets=[(0, 0, 32, 32), (0, 32, 32, 32)],
                                        pos=(x_offset, self.y_pos),
                                        detail=chaser_detail,
                                        frame_delay=150,
                                        flip=reverse)
            x_offset += int(animation.rect.width * 1.5)
            self.chasers.append(animation)
        x_offset += (self.intro_speed * 2)
        for target in chased:
            self.chased_positions.append(x_offset)
            animation = Animation(screen, target, sheet_offsets=[(0, 0, 32, 32),
                                                                       (32, 0, 32, 32),
                                                                       (0, 32, 32, 32),
                                                                       (32, 32, 32, 32),
                                                                       (0, 64, 32, 32)],
                                        pos=(x_offset, self.y_pos),
                                        detail=chased_detail,
                                        frame_delay=150,
                                        flip=reverse)
            x_offset += int(animation.rect.width * 1.5)
            self.chased.append(animation)

    def reset_positions(self):
        for chaser, c_offset in zip(self.chasers, self.chaser_positions):
            chaser.rect.centerx, chaser.rect.centery = c_offset, self.y_pos
        for target, t_offset in zip(self.chased, self.chased_positions):
            target.rect.centerx, target.rect.centery = t_offset, self.y_pos

    def update(self):
        for chaser in self.chasers:
            chaser.rect.centerx += self.intro_speed
            chaser.update()
        for target in self.chased:
            target.rect.centerx += self.intro_speed
            target.update()

    def blit(self):
        for chaser in self.chasers:
            chaser.blit()
        for target in self.chased:
            target.blit()


class Animation(pygame.sprite.Sprite):
    def __init__(self, screen, sprite_sheet, sheet_offsets, pos=(0, 0), resize=None,
                 detail=None, frame_delay=None, flip=False):
        super().__init__()
        self.screen = screen
        if not resize:
            resize = (self.screen.get_height() // 10, self.screen.get_height() // 10)
        self.image_manager = ImageManager(sprite_sheet, sheet=True, pos_offsets=sheet_offsets,
                                          resize=resize, animation_delay=frame_delay)
        if flip:
            self.image_manager.flip()
        self.image, self.rect = self.image_manager.get_image()
        if detail:
            self.detail_piece = ImageManager(detail, sheet=True, pos_offsets=sheet_offsets,
                                             resize=resize).all_images()[0]
            if flip:
                self.image_manager.flip()
            self.image.blit(self.detail_piece, (0, 0))
        else:
            self.detail_piece = None
        self.rect.centerx, self.rect.centery = pos

    def update(self):
        self.image = self.image_manager.next_image()
        if self.detail_piece:
            self.image.blit(self.detail_piece, (0, 0))

    def blit(self):
        self.screen.blit(self.image, self.rect)
