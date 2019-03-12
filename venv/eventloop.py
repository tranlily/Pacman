import pygame
from sys import exit


class EventLoop:
    def __init__(self, loop_running=False, actions=None):
        self.action_map = {pygame.QUIT: exit, }
        if isinstance(actions, dict):
            self.action_map.update(actions)
        self.loop_running = loop_running

    def check_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.action_map[event.type]()
            elif event.type in self.action_map:
                try:
                    self.action_map[event.type](event)
                except TypeError:
                    self.action_map[event.type]()
