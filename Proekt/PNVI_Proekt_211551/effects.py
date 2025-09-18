import pygame
import math
from constants import *


class PowerUpNotification:
    def __init__(self, power_type, x, y):
        self.power_type = power_type
        self.x = x
        self.y = y
        self.life = 120
        self.max_life = 120
        self.scale = 0.1

        self.messages = {
            'triple_shot': 'TRIPLE SHOT!',
            'shield': 'SHIELD UP!',
            'heal': 'HEALTH BOOST!',
            'speed': 'SPEED BOOST!',
            'ammo': 'AMMO REFILL!',
            'mothership_spawned': 'MOTHERSHIP INCOMING!',
            'mothership_destroyed': 'MOTHERSHIP DESTROYED!'
        }

        self.colors = {
            'triple_shot': CYAN,
            'shield': GREEN,
            'heal': RED,
            'speed': YELLOW,
            'ammo': ORANGE,
            'mothership_spawned': GREEN,
            'mothership_destroyed': YELLOW
        }

    def update(self):
        self.life -= 1

        if self.life > 90:
            self.scale = min(1.5, self.scale + 0.1)
        elif self.life > 30:
            self.scale = 1.2 + 0.2 * math.sin(self.life * 0.3)
        else:
            self.scale = max(0, self.scale - 0.05)

        self.y -= 1

    def draw(self, screen, font):
        if self.life <= 0:
            return

        alpha = min(255, int(255 * (self.life / self.max_life)))
        color = self.colors.get(self.power_type, WHITE)

        message = self.messages.get(self.power_type, f'{self.power_type.upper().replace("_", " ")}!')
        text_surface = font.render(message, True, color)

        scaled_width = int(text_surface.get_width() * self.scale)
        scaled_height = int(text_surface.get_height() * self.scale)

        if scaled_width > 0 and scaled_height > 0:
            scaled_surface = pygame.transform.scale(text_surface, (scaled_width, scaled_height))

            glow_surface = pygame.Surface((scaled_width + 20, scaled_height + 20), pygame.SRCALPHA)
            for i in range(5):
                glow_alpha = max(0, min(255, alpha // (i + 1)))
                glow_color = (*color[:3], glow_alpha)
                glow_text = font.render(message, True, glow_color[:3])
                if glow_text.get_width() > 0 and glow_text.get_height() > 0:
                    glow_scaled = pygame.transform.scale(glow_text, (scaled_width, scaled_height))
                    glow_surface.blit(glow_scaled, (10 + i, 10 + i))

            screen.blit(glow_surface, (self.x - scaled_width // 2 - 10, self.y - scaled_height // 2 - 10))
            screen.blit(scaled_surface, (self.x - scaled_width // 2, self.y - scaled_height // 2))


class Particle:
    def __init__(self, x, y, color, velocity):
        self.x = x
        self.y = y
        self.color = color
        self.velocity = velocity
        self.life = 30
        self.max_life = 30

    def update(self):
        self.x += self.velocity[0]
        self.y += self.velocity[1]
        self.life -= 1

    def draw(self, screen):
        if self.life > 0:
            alpha = int(255 * (self.life / self.max_life))
            color = (*self.color[:3], alpha)
            s = pygame.Surface((6, 6), pygame.SRCALPHA)
            s.fill(color)
            screen.blit(s, (self.x, self.y))