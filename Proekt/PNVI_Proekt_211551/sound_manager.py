import pygame
import os


class SoundManager:
    def __init__(self):
        self.sounds = {}
        self.music_playing = False

        try:
            self.load_sounds()
        except pygame.error:
            print("Warning: Could not load sound files. Game will run without audio.")

    def load_sounds(self):
        sound_files = {
            'player_shoot': 'sounds/player_shoot.wav',
            'enemy_shoot': 'sounds/enemy_shoot.wav',
            'explosion': 'sounds/explosion.wav',
            'powerup': 'sounds/powerup.wav',
            'boss_hit': 'sounds/boss_hit.wav',
            'mothership_spawn': 'sounds/mothership_spawn.wav',
            'mothership_destroy': 'sounds/mothership_destroy.wav',
            'shield_activate': 'sounds/shield.wav',
            'reload': 'sounds/reload.wav',
            'no_ammo': 'sounds/no_ammo.wav',
            'game_over': 'sounds/game_over.wav'
        }

        for sound_name, file_path in sound_files.items():
            try:
                if os.path.exists(file_path):
                    self.sounds[sound_name] = pygame.mixer.Sound(file_path)
                    self.sounds[sound_name].set_volume(0.7)
                else:
                    self.sounds[sound_name] = None
            except pygame.error:
                self.sounds[sound_name] = None

    def play_sound(self, sound_name):
        if sound_name in self.sounds and self.sounds[sound_name]:
            self.sounds[sound_name].play()

    def play_music(self, music_file):
        try:
            if os.path.exists(music_file) and not self.music_playing:
                pygame.mixer.music.load(music_file)
                pygame.mixer.music.set_volume(0.3)
                pygame.mixer.music.play(-1)
                self.music_playing = True
        except pygame.error:
            pass

    def stop_music(self):
        pygame.mixer.music.stop()
        self.music_playing = False