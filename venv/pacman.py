import pygame
from pygame.sprite import Sprite
from spritesheet import ImageManager
from sounds import SoundManager
from portal import PortalController


# For Pacman sprite controls

class Pacman(Sprite):
    PAC_YELLOW = (255, 255, 0)
    PAC_AUDIO_CHANNEL = 0

    def __init__(self, screen, maze):
        super().__init__()
        self.screen = screen
        self.radius = maze.block_size // 1
        self.maze = maze
        self.sound_manager = SoundManager(sound_files=['pacman_chomp.wav', 'pacman_eatfruit.wav', 'pacman_death.wav', 'portal.wav'],
                                          keys=['eat', 'fruit', 'dead', 'portal'],
                                          channel=Pacman.PAC_AUDIO_CHANNEL)

        self.pacman_horizontal = ImageManager('pacman-horiz.png', sheet=True, pos_offsets=[(0, 0, 32, 32),
                                                                                           (32, 0, 32, 32),
                                                                                           (0, 32, 32, 32),
                                                                                           (32, 32, 32, 32),
                                                                                           (0, 64, 32, 32)],
                                              resize=(self.maze.block_size, self.maze.block_size),
                                              reversible=True)

        self.pacman_vertical = ImageManager('pacman-vert.png', sheet=True, pos_offsets=[(0, 0, 32, 32),
                                                                                        (32, 0, 32, 32),
                                                                                        (0, 32, 32, 32),
                                                                                        (32, 32, 32, 32),
                                                                                        (0, 64, 32, 32)],
                                            resize=(self.maze.block_size, self.maze.block_size),
                                            reversible=True)

        self.pacman_dead = ImageManager('pacman-death.png', sheet=True, pos_offsets=[(0, 0, 32, 32),
                                                                                      (32, 0, 32, 32),
                                                                                      (0, 32, 32, 32),
                                                                                      (32, 32, 32, 32),
                                                                                      (0, 64, 32, 32),
                                                                                      (32, 64, 32, 32)],
                                        resize=(self.maze.block_size, self.maze.block_size),
                                        animation_delay=150, repeat=False)

        self.flip_status = {'use_horiz': True, 'h_flip': False, 'v_flip': False}
        self.spawn_info = self.maze.player_spawn[1]
        self.tile = self.maze.player_spawn[0]
        self.direction = None
        self.moving = False
        self.speed = maze.block_size // 7
        self.image, self.rect = self.pacman_horizontal.get_image()
        self.rect.centerx, self.rect.centery = self.spawn_info
        self.dead = False
        self.portal_controller = PortalController(screen, self, maze)

        # Key Actions
        self.event_map = {pygame.KEYDOWN: self.perform_action, pygame.KEYUP: self.reset_direction}
        self.action_map = {pygame.K_UP: self.set_move_up, pygame.K_LEFT: self.set_move_left,
                           pygame.K_DOWN: self.set_move_down, pygame.K_RIGHT: self.set_move_right,
                           pygame.K_a: self.blue_portal, pygame.K_s: self.orange_portal}

    def eat(self):
        score = 0
        fruit_count = 0
        power = None
        collision = pygame.sprite.spritecollideany(self, self.maze.pellets)
        if collision:
            collision.kill()
            score += 10
            self.sound_manager.play('eat')
        collision = pygame.sprite.spritecollideany(self, self.maze.fruits)
        if collision:
            collision.kill()
            score += 20
            fruit_count += 1
            self.sound_manager.play('fruit')
        collision = pygame.sprite.spritecollideany(self, self.maze.power_pellets)
        if collision:
            collision.kill()
            score += 20
            power = True
            self.sound_manager.play('eat')
        return score, fruit_count, power

    def is_blocked(self):
        result = False
        if self.direction is not None and self.moving:
            original_pos = self.rect
            if self.direction == 'u':
                test = self.rect.move((0, -self.speed))
            elif self.direction == 'l':
                test = self.rect.move((-self.speed, 0))
            elif self.direction == 'd':
                test = self.rect.move((0, self.speed))
            else:
                test = self.rect.move((self.speed, 0))
            self.rect = test

            if pygame.sprite.spritecollideany(self, self.maze.maze_blocks):
                result = True
            elif pygame.sprite.spritecollideany(self, self.maze.shield_blocks):
                result = True
            elif not self.portal_controller.portables_usable():
                result = self.portal_controller.collide_portals(self)
            self.rect = original_pos
        return result

    def set_move_up(self):
        if self.direction != 'u':
            self.direction = 'u'
            if self.flip_status['v_flip']:
                self.pacman_vertical.flip(False, True)
                self.flip_status['v_flip'] = False
            self.flip_status['use_horiz'] = False
        self.moving = True

    def set_move_left(self):
        if self.direction != 'l':
            self.direction = 'l'
            if not self.flip_status['h_flip']:
                self.pacman_horizontal.flip()
                self.flip_status['h_flip'] = True
            self.flip_status['use_horiz'] = True
        self.moving = True

    def set_move_down(self):
        if self.direction != 'd':
            self.direction = 'd'
            if not self.flip_status['v_flip']:
                self.pacman_vertical.flip(x_bool=False, y_bool=True)
                self.flip_status['v_flip'] = True
            self.flip_status['use_horiz'] = False
        self.moving = True

    def set_move_right(self):
        if self.direction != 'r':
            self.direction = 'r'
            if self.flip_status['h_flip']:
                self.pacman_horizontal.flip()
                self.flip_status['h_flip'] = False
            self.flip_status['use_horiz'] = True
        self.moving = True          


    def clear_portals(self):
        self.portal_controller.clear_portals()


    def blue_portal(self):
        self.sound_manager.play('portal')
        self.portal_controller.fire_b_portal_projectile()

    def orange_portal(self):
        self.sound_manager.play('portal')
        self.portal_controller.fire_o_portal_projectile()

    def set_death(self):
        self.sound_manager.play('dead')
        self.dead = True
        self.image, _ = self.pacman_dead.get_image()

    def revive(self):
        self.dead = False
        self.image, _ = self.pacman_horizontal.get_image()
        self.pacman_dead.image_index = 0

    def reset_position(self):
        self.rect.centerx, self.rect.centery = self.spawn_info  # screen coordinates for spawn

    def reset_direction(self, event):
        if event.key in (pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT):
            self.moving = False

    def perform_action(self, event):
        if event.key in self.action_map:
            self.action_map[event.key]()

    def get_nearest_col(self):
        return (self.rect.x - (self.screen.get_width() // 5)) // self.maze.block_size

    def get_nearest_row(self):
        return (self.rect.y - (self.screen.get_height() // 12)) // self.maze.block_size

    def update(self):
        if not self.dead:
            self.portal_controller.update()
            self.portal_controller.check_portals(self)
            if self.direction and self.moving:
                if self.flip_status['use_horiz']:
                    self.image = self.pacman_horizontal.next_image()
                else:
                    self.image = self.pacman_vertical.next_image()
                if not self.is_blocked():
                    if self.direction == 'u':
                        self.rect.centery -= self.speed
                    elif self.direction == 'l':
                        self.rect.centerx -= self.speed
                    elif self.direction == 'd':
                        self.rect.centery += self.speed
                    elif self.direction == 'r':
                        self.rect.centerx += self.speed
                self.tile = (self.get_nearest_row(), self.get_nearest_col())
        else:
            self.image = self.pacman_dead.next_image()

    def blit(self):
        self.portal_controller.blit()
        self.screen.blit(self.image, self.rect)