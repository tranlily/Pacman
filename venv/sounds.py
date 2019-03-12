import pygame


class SoundManager:
    # Class for handling sounds
    def __init__(self, sound_files, keys=None, channel=0, volume=None):
        self.sound_files = sound_files
        self.sounds = {}
        self.channel = pygame.mixer.Channel(channel)
        if not keys:
            for s_file in sound_files:
                self.sounds[s_file] = pygame.mixer.Sound('sounds/' + s_file)
        else:
            if len(keys) != len(sound_files):
                raise ValueError('number of keys must be the same as the number of sound files')
            for key, s_file in zip(keys, sound_files):
                self.sounds[key] = pygame.mixer.Sound('sounds/' + s_file)
        if isinstance(volume, float):
            self.channel.set_volume(volume)

    # Play a sound one time
    def play(self, key):
        self.channel.play(self.sounds[key], loops=0)

    # Infinitely play sound
    def play_loop(self, key):
        self.channel.play(self.sounds[key], loops=-1)

    # Stop sound
    def stop(self):
        self.channel.stop()
