import pygame
from walls import Block
from fruit import Fruit
from random import randrange


class Maze:

    BLOCK_COLOR = 22, 41, 249
    POWER_PELLET = 255, 255, 255
    PELLET_COLOR = 214, 223, 230


    def __init__(self, screen, maze_map_file):
        self.screen = screen
        self.map_file = 'maze.txt'
        self.block_size = 22
        self.block_image = pygame.Surface((self.block_size, self.block_size // 2))
        self.block_image.fill(Maze.BLOCK_COLOR)
        self.shield_image = pygame.Surface((self.block_size, self.block_size // 2))
        self.shield_image.fill(Maze.POWER_PELLET)
        self.pellet_image = pygame.Surface((self.block_size // 4, self.block_size // 4))
        pygame.draw.circle(self.pellet_image, Maze.PELLET_COLOR,
                           (self.block_size // 8, self.block_size // 8), self.block_size // 8)
        self.ppellet_image = pygame.Surface((self.block_size // 2, self.block_size // 2))
        pygame.draw.circle(self.ppellet_image, Maze.POWER_PELLET,
                           (self.block_size // 4, self.block_size // 4), self.block_size // 4)
        with open(self.map_file, 'r') as file:
            self.map_lines = file.readlines()
        self.maze_blocks = pygame.sprite.Group()
        self.shield_blocks = pygame.sprite.Group()
        self.pellets = pygame.sprite.Group()
        self.power_pellets = pygame.sprite.Group()
        self.fruits = pygame.sprite.Group()
        self.teleport = None
        self.player_spawn = None
        self.ghost_spawn = []
        self.build_maze()

    def pellets_left(self):
        return True if self.pellets or self.power_pellets else False

    def build_maze(self):
        if self.maze_blocks or self.pellets or self.fruits or self.power_pellets or self.shield_blocks:
            self.maze_blocks.empty()
            self.pellets.empty()
            self.power_pellets.empty()
            self.fruits.empty()
            self.shield_blocks.empty()
        if len(self.ghost_spawn) > 0:
            self.ghost_spawn.clear()
        teleport_points = []
        y_start = self.screen.get_height() // 12
        y = 0
        for i in range(len(self.map_lines)):
            line = self.map_lines[i]
            x_start = self.screen.get_width() // 5
            x = 0
            for j in range(len(line)):
                co = line[j]
                if co == 'x':
                    self.maze_blocks.add(Block(x_start + (x * self.block_size),
                                               y_start + (y * self.block_size),
                                               self.block_size, self.block_size,
                                               self.block_image))
                elif co == '*':
                    if randrange(0, 100) > 1:
                        self.pellets.add(Block(x_start + (self.block_size // 3) + (x * self.block_size),
                                               y_start + (self.block_size // 3) + (y * self.block_size),
                                               self.block_size, self.block_size,
                                               self.pellet_image))
                    else:
                        self.fruits.add(Fruit(x_start + (self.block_size // 4) + (x * self.block_size),
                                              y_start + (self.block_size // 4) + (y * self.block_size),
                                              self.block_size, self.block_size))
                elif co == '@':
                    self.power_pellets.add(Block(x_start + (self.block_size // 3) + (x * self.block_size),
                                                 y_start + (self.block_size // 3) + (y * self.block_size),
                                                 self.block_size, self.block_size,
                                                 self.ppellet_image))
                elif co == 's':
                    self.shield_blocks.add(Block(x_start + (x * self.block_size),
                                                 y_start + (y * self.block_size),
                                                 self.block_size // 2, self.block_size // 2,
                                                 self.shield_image))
                elif co == 'o':
                    self.player_spawn = [(i, j), (x_start + (x * self.block_size) + (self.block_size // 2),
                                         y_start + (y * self.block_size) + (self.block_size // 2))]
                elif co == 'g':
                    self.ghost_spawn.append(((i, j), (x_start + (x * self.block_size),
                                            y_start + (y * self.block_size))))
                elif co == 't':
                    teleport_points.append(pygame.Rect(x_start + (x * self.block_size),
                                                       y_start + (y * self.block_size),
                                                       self.block_size, self.block_size))
                x += 1
            y += 1
        if len(teleport_points) == 2:
            self.teleport = Teleporter(teleport_points[0], teleport_points[1])

    def remove_shields(self):
        self.shield_blocks.empty()

    def blit(self):
        self.maze_blocks.draw(self.screen)
        self.pellets.draw(self.screen)
        self.power_pellets.draw(self.screen)
        self.fruits.draw(self.screen)
        self.shield_blocks.draw(self.screen)


class Teleporter:
    def __init__(self, port_1, port_2):
        self.port_1 = port_1
        self.port_2 = port_2

    def check_teleport(self, *args):
        for other in args:
            if pygame.Rect.colliderect(self.port_1, other):
                other.x, other.y = (self.port_2.x - self.port_2.width), self.port_2.y
            elif pygame.Rect.colliderect(self.port_2, other):
                other.x, other.y = (self.port_1.x + self.port_1.width), self.port_1.y
