from pygame import time, sysfont
from pygame.sprite import Sprite, spritecollideany
from spritesheet import ImageManager


class Ghost(Sprite):
    ghost_audio = 1

    def __init__(self, screen, maze, target, spawn_info, sound_manager, ghost_file='blinky.png'):
        super().__init__()
        self.screen = screen
        self.maze = maze
        self.internal_map = maze.map_lines
        self.pacman_position = target
        self.ghost_sound_manager = sound_manager
        self.regular_ghosts = ImageManager(ghost_file, sheet=True, pos_offsets=[(0, 0, 32, 32), (0, 32, 32, 32)],
                                        resize=(self.maze.block_size, self.maze.block_size),
                                        animation_delay=250)

        self.blue_ghosts = ImageManager('ghost_blue.png', sheet=True, pos_offsets=[(0, 0, 32, 32), (0, 32, 32, 32)],
                                        resize=(self.maze.block_size, self.maze.block_size),
                                        animation_delay=150)

        self.blue_ghosts_warning = ImageManager('ghost_white.png', sheet=True, pos_offsets=[(0, 0, 32, 32),
                                                                                             (0, 32, 32, 32)],
                                          resize=(self.maze.block_size, self.maze.block_size),
                                          animation_delay=150)

        self.ghosts_eyes = ImageManager('eyes.png', sheet=True, pos_offsets=[(0, 0, 32, 32), (32, 0, 32, 32),
                                                                            (0, 32, 32, 32), (32, 32, 32, 32)],
                                 resize=(self.maze.block_size, self.maze.block_size),
                                 keys=['r', 'u', 'd', 'l'])

        self.score_font = sysfont.SysFont(None, 22)
        self.score_image = None
        self.image, self.rect = self.regular_ghosts.get_image()
        self.ghosts_eye_right, _ = self.ghosts_eyes.get_image(key='r')
        self.image.blit(self.ghosts_eye_right, (0, 0))
        self.return_tile = spawn_info[0]
        self.return_path = None
        self.return_delay = 1000
        self.eaten_time = None
        self.start_pos = spawn_info[1]
        self.reset_position()
        self.tile = spawn_info[0]
        self.direction = None
        self.last_position = None
        self.speed = maze.block_size / 10
        self.state = {'enabled': False, 'blue': False, 'return': False, 'speed_boost': False}
        self.blue_interval = 5000
        self.blue_start = None
        self.blink = False
        self.last_blink = time.get_ticks()
        self.blink_interval = 250

    def find_path(maze_map, start, target):
        path = []
        tried = set()
        done = False
        curr_tile = start
        while not done:
            if curr_tile == target:
                done = True
            else:
                options = [
                    (curr_tile[0] + 1, curr_tile[1]),
                    (curr_tile[0] - 1, curr_tile[1]),
                    (curr_tile[0], curr_tile[1] + 1),
                    (curr_tile[0], curr_tile[1] - 1)
                ]
                test = (abs(target[0] - start[0]), abs(target[1] - start[0]))
                prefer = test.index(max(test[0], test[1]))
                if prefer == 0:
                    options.sort(key=lambda x: x[0], reverse=True)
                else:
                    options.sort(key=lambda x: x[1], reverse=True)
                backtrack = True
                for opt in options:
                    try:
                        if maze_map[opt[0]][opt[1]] not in ('x', ) and opt not in tried:
                            backtrack = False
                            path.append(opt)
                            tried.add(opt)
                            curr_tile = opt
                            break
                    except IndexError:
                        continue
                if backtrack:
                    curr_tile = path.pop()
        return path

    def increase_speed(self):
        self.state['speed_boost'] = True
        self.speed = self.maze.block_size / 8

    def reset_speed(self):
        self.state['speed_boost'] = False
        self.speed = self.maze.block_size / 10

    def reset_position(self):
        self.rect.left, self.rect.top = self.start_pos

    def get_dir_from_path(self):
        try:
            next_step = self.return_path[0]
            if next_step[0] > self.tile[0]:
                return 'd'
            if next_step[0] < self.tile[0]:
                return 'u'
            if next_step[1] > self.tile[1]:
                return 'r'
            if next_step[1] < self.tile[1]:
                return 'l'
        except IndexError as ie:
            print('Error while trying to get new path direction', ie)
            return None

    def set_eaten(self):
        self.state['return'] = True
        self.state['blue'] = False
        self.tile = (self.get_nearest_row(), self.get_nearest_col())
        self.return_path = Ghost.find_path(self.internal_map, self.tile, self.return_tile)
        self.direction = self.get_dir_from_path()
        self.image = self.score_font.render('200', True, (255, 255, 255))
        self.eaten_time = time.get_ticks()

    def get_direction_options(self):
        tests = {
            'u': self.rect.move((0, -self.speed)),
            'l': self.rect.move((-self.speed, 0)),
            'd': self.rect.move((0, self.speed)),
            'r': self.rect.move((self.speed, 0))
        }

        remove = []
        original_pos = self.rect

        for d, t in tests.items():
            self.rect = t
            if spritecollideany(self, self.maze.maze_blocks) and d not in remove:
                remove.append(d)
            if spritecollideany(self, self.pacman_position.portal_controller.blue_portal) and d not in remove:
                remove.append(d)
            if spritecollideany(self, self.pacman_position.portal_controller.orange_portal) and d not in remove:
                remove.append(d)
        for rem in remove:
            del tests[rem]
        self.rect = original_pos
        return list(tests.keys())

    def begin_blue_state(self):
        if not self.state['return']:
            self.state['blue'] = True
            self.image, _ = self.blue_ghosts.get_image()
            self.blue_start = time.get_ticks()
            self.ghost_sound_manager.stop()
            self.ghost_sound_manager.play_loop('blue')

    def change_eyes(self, look_direction):
        self.image, _ = self.regular_ghosts.get_image()
        self.ghosts_eye_right, _ = self.ghosts_eyes.get_image(key=look_direction)
        self.image.blit(self.ghosts_eye_right, (0, 0))

    def get_chase_direction(self, options):
        pick_direction = None
        target_pos = (self.pacman_position.rect.centerx, self.pacman_position.rect.centery)
        test = (abs(target_pos[0]), abs(target_pos[1]))
        prefer = test.index(max(test[0], test[1]))
        if prefer == 0:
            if target_pos[prefer] < self.rect.centerx:
                pick_direction = 'l'
            elif target_pos[prefer] > self.rect.centerx:
                pick_direction = 'r'
        else:
            if target_pos[prefer] < self.rect.centery:
                pick_direction = 'u'
            elif target_pos[prefer] > self.rect.centery:
                pick_direction = 'd'
        if pick_direction not in options:
            if 'u' in options:
                return 'u'
            if 'l' in options:
                return 'l'
            if 'r' in options:
                return 'r'
            if 'd' in options:
                return 'd'
        else:
            return pick_direction

    def get_flee_direction(self, options):
        pick_direction = None
        target_pos = (self.pacman_position.rect.centerx, self.pacman_position.rect.centery)
        test = (abs(target_pos[0]), abs(target_pos[1]))
        prefer = test.index(max(test[0], test[1]))
        if prefer == 0:
            if target_pos[prefer] < self.rect.centerx:
                pick_direction = 'r'
            elif target_pos[prefer] > self.rect.centerx:
                pick_direction = 'l'
        else:
            if target_pos[prefer] < self.rect.centery:
                pick_direction = 'd'
            elif target_pos[prefer] > self.rect.centery:
                pick_direction = 'u'
        if pick_direction not in options:
            if 'u' in options:
                return 'u'
            if 'l' in options:
                return 'l'
            if 'd' in options:
                return 'd'
            if 'r' in options:
                return 'r'
        else:
            return pick_direction

    def get_nearest_col(self):
        return (self.rect.left - (self.screen.get_width() // 5)) // self.maze.block_size

    def get_nearest_row(self):
        return (self.rect.top - (self.screen.get_height() // 12)) // self.maze.block_size

    def is_at_intersection(self):
        directions = 0
        self.tile = (self.get_nearest_row(), self.get_nearest_col())
        if self.internal_map[self.tile[0] - 1][self.tile[1]] not in ('x', ):
            directions += 1
        if self.internal_map[self.tile[0] + 1][self.tile[1]] not in ('x', ):
            directions += 1
        if self.internal_map[self.tile[0]][self.tile[1] - 1] not in ('x', ):
            directions += 1
        if self.internal_map[self.tile[0]][self.tile[1] + 1] not in ('x', ):
            directions += 1
        return True if directions > 2 else False

    def enable(self):
        options = self.get_direction_options()
        self.direction = options[0]
        self.state['enabled'] = True
        self.ghost_sound_manager.play_loop('std')

    def disable(self):
        self.direction = None
        self.state['enabled'] = False
        self.state['return'] = False
        self.return_path = None
        if self.state['blue']:
            self.stop_blue_state(resume_audio=False)
        self.image, _ = self.regular_ghosts.get_image()
        self.ghost_sound_manager.stop()

    def stop_blue_state(self, resume_audio=True):
        self.state['blue'] = False
        self.state['return'] = False
        self.image, _ = self.regular_ghosts.get_image()
        self.ghost_sound_manager.stop()
        if resume_audio:
            self.ghost_sound_manager.play_loop('std')

    def check_path_tile(self):
        self.tile = (self.get_nearest_row(), self.get_nearest_col())
        if self.return_path and self.tile == self.return_path[0]:
            del self.return_path[0]
            if not len(self.return_path) > 0:
                return '*'
        return None

    def update_normal(self):
        options = self.get_direction_options()
        if self.is_at_intersection() or self.last_position == (self.rect.centerx, self.rect.centery):
            self.direction = self.get_chase_direction(options)
        if self.direction == 'u' and 'u' in options:
            self.rect.centery -= self.speed
        elif self.direction == 'l' and 'l' in options:
            self.rect.centerx -= self.speed
        elif self.direction == 'd' and 'd' in options:
            self.rect.centery += self.speed
        elif self.direction == 'r' and 'r' in options:
            self.rect.centerx += self.speed
        self.change_eyes(self.direction or 'r')
        self.image = self.regular_ghosts.next_image()

    def update_blue(self):
        self.image = self.blue_ghosts.next_image()
        options = self.get_direction_options()
        if self.is_at_intersection() or self.last_position == (self.rect.centerx, self.rect.centery):
            self.direction = self.get_flee_direction(options)
        if self.direction == 'u' and 'u' in options:
            self.rect.centery -= self.speed
        elif self.direction == 'l' and 'l' in options:
            self.rect.centerx -= self.speed
        elif self.direction == 'd' and 'd' in options:
            self.rect.centery += self.speed
        elif self.direction == 'r' and 'r' in options:
            self.rect.centerx += self.speed
        if abs(self.blue_start - time.get_ticks()) > self.blue_interval:
            self.stop_blue_state()
        elif abs(self.blue_start - time.get_ticks()) > int(self.blue_interval * 0.5):
            if self.blink:
                self.image = self.blue_ghosts_warning.next_image()
                self.blink = False
                self.last_blink = time.get_ticks()
            elif abs(self.last_blink - time.get_ticks()) > self.blink_interval:
                self.blink = True

    def update_return(self):
        if abs(self.eaten_time - time.get_ticks()) > self.return_delay:
            self.image, _ = self.ghosts_eyes.get_image(key=self.direction)
            test = self.check_path_tile()
            if test == '*':
                self.state['return'] = False
                self.direction = self.get_chase_direction(self.get_direction_options())
            else:
                self.direction = self.get_dir_from_path()
            if self.direction == 'u':
                self.rect.centery -= self.speed
            elif self.direction == 'l':
                self.rect.centerx -= self.speed
            elif self.direction == 'd':
                self.rect.centery += self.speed
            elif self.direction == 'r':
                self.rect.centerx += self.speed

    def update(self):
        if self.state['enabled']:
            if not self.state['blue'] and not self.state['return']:
                self.update_normal()
            elif self.state['blue']:
                self.update_blue()
            elif self.state['return']:
                self.update_return()
            self.last_position = (self.rect.centerx, self.rect.centery)

    def blit(self):
        self.screen.blit(self.image, self.rect)
