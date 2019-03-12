import pygame
from eventloop import EventLoop
from menu import Menu, HighScoreScreen
from setup import Intro
from maze import Maze
from pacman import Pacman
from ghost import Ghost
from fruit import Fruit
from lives import Counter
from score import ScoreController, LevelTransition
from sounds import SoundManager


class PlayGame:

    game_color = (0, 0, 0)
    event_start = pygame.USEREVENT + 1
    event_remake = pygame.USEREVENT + 2
    event_next_level = pygame.USEREVENT + 3

    def __init__(self):
        pygame.init()
        pygame.mixer.music.load('sounds/fortnite-dance.wav')
        self.game_screen = pygame.display.set_mode((900, 700))

        pygame.display.set_caption('Pacman')
        self.tick_component = pygame.time.Clock()

        self.hold_score = ScoreController(screen=self.game_screen,
                                            sb_pos=((self.game_screen.get_width() // 5),
                                                    (self.game_screen.get_height() * 0.965)),
                                            items_image='apple.png',
                                            itc_pos=(int(self.game_screen.get_width() * 0.6),
                                                     self.game_screen.get_height() * 0.965))
        self.map_layout = Maze(screen=self.game_screen, maze_map_file='maze_map.txt')
        self.lives_left = Counter(screen=self.game_screen, ct_pos=((self.game_screen.get_width() // 3),
                                                                      (self.game_screen.get_height() * 0.965)),
                                          images_size=(self.map_layout.block_size, self.map_layout.block_size))
        self.next_level = LevelTransition(screen=self.game_screen, score_controller=self.hold_score)
        self.lost_game = True
        self.pause_game = False
        self.pacman_player = Pacman(screen=self.game_screen, maze=self.map_layout)
        self.pacman_ghosts = pygame.sprite.Group()
        self.pacman_ghosts_sound = SoundManager(sound_files=['ghost.wav', 'pacman_eatghost.wav', 'pacman_siren.wav'],
                                                keys=['blue', 'eaten', 'std'],
                                                channel=Ghost.ghost_audio)
        self.pacman_ghosts_interval_active = 2500
        self.pacman_ghosts_begin_chase = None
        self.pacman_ghosts_blinky = None
        self.pacman_ghosts_others = []
        self.blit_ghosts()
        self.game_actions = {PlayGame.event_start: self.init_ghosts,
                             PlayGame.event_remake: self.rebuild_maze,
                             PlayGame.event_next_level: self.next_level}

    def play_game(self):
        event_iterator = EventLoop(loop_running=True, actions={**self.pacman_player.event_map, **self.game_actions})
        self.next_level.set_show_transition()
        self.lost_game = False
        if self.pacman_player.dead:
            self.pacman_player.revive()
            self.hold_score.reset_level()
            self.lives_left.reset_counter()
            self.rebuild_maze()

        while event_iterator.loop_running:
            self.tick_component.tick(60)
            event_iterator.check_events()
            self.update_screen()
            if self.lost_game:
                pygame.mixer.stop()
                self.hold_score.reset_level()
                event_iterator.loop_running = False

    def run(self):
        play_menu = Menu(self.game_screen)
        high_score_menu = HighScoreScreen(self.game_screen, self.hold_score)
        intro_ghost_chase = Intro(self.game_screen)
        event_iterator = EventLoop(loop_running=True, actions={pygame.MOUSEBUTTONDOWN: play_menu.check_buttons})

        while event_iterator.loop_running:
            self.tick_component.tick(60)
            event_iterator.check_events()
            self.game_screen.fill(PlayGame.game_color)
            if not play_menu.high_score_menu:
                intro_ghost_chase.update()
                intro_ghost_chase.blit()
                play_menu.blit()
            else:
                high_score_menu.blit()
                high_score_menu.check_done()
            if play_menu.ready_to_play:
                pygame.mixer.music.stop()
                self.play_game()
                for g in self.pacman_ghosts:
                    g.reset_speed()
                play_menu.ready_to_play = False
                self.hold_score.save_high_scores()
                high_score_menu.prep_images()
                high_score_menu.position()
            elif not pygame.mixer.music.get_busy():
                pygame.mixer.music.play(-1)
            pygame.display.flip()

    def init_ghosts(self):
        if not self.pacman_ghosts_blinky.state['enabled']:
            self.pacman_ghosts_blinky.enable()
            self.pacman_ghosts_begin_chase = self.pacman_ghosts_others.copy()
            pygame.time.set_timer(PlayGame.event_start, 0)
            pygame.time.set_timer(PlayGame.event_start, self.pacman_ghosts_interval_active)
        else:
            try:
                g = self.pacman_ghosts_begin_chase.pop()
                g.enable()
            except IndexError:
                pygame.time.set_timer(PlayGame.event_start, 0)

    def blit_ghosts(self):
        ghost_images_file = ['pinky.png', 'inky.png', 'clyde.png', 'blinky.png']
        location = 0
        while len(self.map_layout.ghost_spawn) > 0:
            spawn_info = self.map_layout.ghost_spawn.pop()
            g = Ghost(screen=self.game_screen, maze=self.map_layout, target=self.pacman_player,
                      spawn_info=spawn_info, ghost_file=ghost_images_file[location], sound_manager=self.pacman_ghosts_sound)
            if ghost_images_file[location] == 'blinky.png':
                self.pacman_ghosts_blinky = g
            else:
                self.pacman_ghosts_others.append(g)
            self.pacman_ghosts.add(g)
            location = (location + 1) % len(ghost_images_file)

    def next_level(self):
        pygame.time.set_timer(PlayGame.event_next_level, 0)
        self.pacman_player.clear_portals()
        self.hold_score.increment_level()
        self.rebuild_maze()

    def rebuild_maze(self):
        if self.lives_left.lives > 0:
            for g in self.pacman_ghosts:
                if g.state['enabled']:
                    g.disable()
            self.map_layout.build_maze()
            self.pacman_player.reset_position()
            for g in self.pacman_ghosts:
                g.reset_position()
            if self.pacman_player.dead:
                self.pacman_player.revive()
            if self.pause_game:
                self.pause_game = False
            self.next_level.set_show_transition()
        else:
            self.lost_game = True
        pygame.time.set_timer(PlayGame.event_remake, 0)

    def check_player(self):
        pacman_player_score, pacman_player_fruits, pacman_player_ability = self.pacman_player.eat()
        self.hold_score.add_score(score=pacman_player_score, items=pacman_player_fruits if pacman_player_fruits > 0 else None)
        if pacman_player_ability:
            for g in self.pacman_ghosts:
                g.begin_blue_state()
        touch_ghost = pygame.sprite.spritecollideany(self.pacman_player, self.pacman_ghosts)
        if touch_ghost and touch_ghost.state['blue']:
            touch_ghost.set_eaten()
            self.hold_score.add_score(200)
        elif touch_ghost and not (self.pacman_player.dead or touch_ghost.state['return']):
            self.lives_left.decrement()
            self.pacman_player.clear_portals()
            self.pacman_player.set_death()
            for g in self.pacman_ghosts:
                if g.state['enabled']:
                    g.disable()
            pygame.time.set_timer(PlayGame.event_start, 0)
            pygame.time.set_timer(PlayGame.event_remake, 4000)
        elif not self.map_layout.pellets_left() and not self.pause_game:
            pygame.mixer.stop()
            self.pause_game = True
            pygame.time.set_timer(PlayGame.event_next_level, 1000)

    def update_screen(self):
        if not self.next_level.transition_show:
            self.game_screen.fill(PlayGame.game_color)
            self.check_player()
            self.map_layout.blit()
            if not self.pause_game:
                self.pacman_ghosts.update()
                self.pacman_player.update()
                self.map_layout.teleport.check_teleport(self.pacman_player.rect)
            for g in self.pacman_ghosts:
                if self.hold_score.level > 3:
                    if not g.state['speed_boost']:
                        g.increase_speed()
                    self.map_layout.teleport.check_teleport(g.rect)
                g.blit()
            self.pacman_player.blit()
            self.hold_score.blit()
            self.lives_left.blit()
        elif self.pacman_player.dead:
            self.pacman_player.update()
            self.pacman_player.blit()
        else:
            self.next_level.draw()
            if not self.next_level.transition_show:
                self.init_ghosts()
        pygame.display.flip()


if __name__ == '__main__':
    game = PlayGame()
    game.run()
