import pygame
import math
import random
from constants import *
from graphics import draw_enemy_ship, draw_boss_ship, draw_player_ship


class Bullet:
    def __init__(self, x, y, velocity, color=WHITE, damage=1, size=1.0):
        self.x = x
        self.y = y
        self.velocity = velocity
        self.color = color
        self.damage = damage
        self.size = size
        width = int(6 * size)
        height = int(12 * size)
        self.rect = pygame.Rect(x, y, width, height)

    def update(self):
        self.y += self.velocity[1]
        self.x += self.velocity[0]
        self.rect.center = (self.x, self.y)

    def draw(self, screen):
        pygame.draw.ellipse(screen, self.color, self.rect)
        inner_rect = pygame.Rect(self.rect.x + 2, self.rect.y + 2, self.rect.width - 4, self.rect.height - 4)
        pygame.draw.ellipse(screen, WHITE, inner_rect)


class PowerUp:
    def __init__(self, x, y, power_type):
        self.x = x
        self.y = y
        self.power_type = power_type
        self.rect = pygame.Rect(x, y, 45, 45)
        self.bounce = 0

        self.colors = {
            'triple_shot': CYAN,
            'shield': GREEN,
            'heal': RED,
            'speed': YELLOW,
            'ammo': ORANGE
        }

    def update(self):
        self.y += 2
        self.bounce += 0.2
        self.rect.center = (self.x, self.y + math.sin(self.bounce) * 5)

    def draw(self, screen):
        color = self.colors.get(self.power_type, WHITE)
        center = (int(self.rect.centerx), int(self.rect.centery))

        for r in range(30, 15, -3):
            alpha = int(40 * (30 - r) / 15)
            glow_surface = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
            glow_color = (*color[:3], alpha)
            pygame.draw.circle(glow_surface, glow_color, (r, r), r)
            screen.blit(glow_surface, (center[0] - r, center[1] - r))

        pygame.draw.circle(screen, color, center, 18)
        pygame.draw.circle(screen, WHITE, center, 18, 3)
        pygame.draw.circle(screen, color, center, 12)


class Enemy:
    def __init__(self, x, y, enemy_type='basic'):
        self.x = x
        self.y = y
        self.enemy_type = enemy_type
        self.health = 1 if enemy_type == 'basic' else 3 if enemy_type == 'heavy' else 2
        self.max_health = self.health
        self.speed = 2 if enemy_type == 'fast' else 1
        self.rect = pygame.Rect(x, y, 60, 60)
        self.shoot_timer = 0
        self.movement_pattern = 0

    def update(self, player_x, difficulty_multiplier):
        speed = self.speed * difficulty_multiplier

        if self.enemy_type == 'basic':
            self.y += speed
        elif self.enemy_type == 'heavy':
            self.y += speed * 0.8
            self.x += math.sin(self.y * 0.02) * 2
        elif self.enemy_type == 'fast':
            if self.x < player_x:
                self.x += speed * 0.5
            elif self.x > player_x:
                self.x -= speed * 0.5
            self.y += speed * 1.5

        self.rect.center = (self.x, self.y)
        self.shoot_timer += 1

    def shoot(self, difficulty_multiplier, sound_manager):
        shoot_frequency = max(30, int(60 / difficulty_multiplier))
        if self.shoot_timer > shoot_frequency:
            self.shoot_timer = 0
            bullet_speed = 4 * difficulty_multiplier
            sound_manager.play_sound('enemy_shoot')
            return Bullet(self.x, self.y + 30, (0, bullet_speed), RED, 1, 1.2)
        return None

    def take_damage(self, damage):
        self.health -= damage
        return self.health <= 0

    def draw(self, screen):
        draw_enemy_ship(screen, int(self.x), int(self.y), self.enemy_type)

        if self.health < self.max_health:
            bar_width = 45
            bar_height = 6
            bar_x = self.x - bar_width // 2
            bar_y = self.y - 35

            pygame.draw.rect(screen, RED, (bar_x, bar_y, bar_width, bar_height))
            health_width = int(bar_width * (self.health / self.max_health))
            pygame.draw.rect(screen, GREEN, (bar_x, bar_y, health_width, bar_height))


class Boss:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.health = 50
        self.max_health = 50
        self.rect = pygame.Rect(x, y, 180, 120)
        self.shoot_timer = 0
        self.phase = 1
        self.movement_timer = 0
        self.direction = 1

    def update(self, player_x):
        self.movement_timer += 1
        if self.movement_timer < 120:
            self.x += self.direction * 2
        else:
            self.direction *= -1
            self.movement_timer = 0

        if self.x < 90 or self.x > GAME_AREA_WIDTH - 90:
            self.direction *= -1

        self.rect.center = (self.x, self.y)
        self.shoot_timer += 1

        if self.health < self.max_health * 0.5 and self.phase == 1:
            self.phase = 2
        elif self.health < self.max_health * 0.2 and self.phase == 2:
            self.phase = 3

    def shoot(self, sound_manager):
        bullets = []
        if self.phase == 1:
            if self.shoot_timer > 30:
                bullets.append(Bullet(self.x, self.y + 60, (0, 5), ORANGE, 2, 1.5))
                sound_manager.play_sound('enemy_shoot')
                self.shoot_timer = 0
        elif self.phase == 2:
            if self.shoot_timer > 25:
                bullets.extend([
                    Bullet(self.x - 45, self.y + 60, (-2, 4), ORANGE, 2, 1.5),
                    Bullet(self.x, self.y + 60, (0, 5), ORANGE, 2, 1.5),
                    Bullet(self.x + 45, self.y + 60, (2, 4), ORANGE, 2, 1.5)
                ])
                sound_manager.play_sound('enemy_shoot')
                self.shoot_timer = 0
        elif self.phase == 3:
            if self.shoot_timer > 10:
                bullets.append(Bullet(self.x, self.y + 60, (0, 6), RED, 2, 1.5))
                sound_manager.play_sound('enemy_shoot')
                self.shoot_timer = 0

        return bullets

    def take_damage(self, damage, sound_manager):
        self.health -= damage
        sound_manager.play_sound('boss_hit')
        return self.health <= 0

    def draw(self, screen):
        draw_boss_ship(screen, int(self.x), int(self.y), self.phase)

        bar_width = 300
        bar_height = 15
        bar_x = GAME_AREA_WIDTH // 2 - bar_width // 2
        bar_y = 40

        pygame.draw.rect(screen, RED, (bar_x, bar_y, bar_width, bar_height))
        health_width = int(bar_width * (self.health / self.max_health))
        pygame.draw.rect(screen, GREEN, (bar_x, bar_y, health_width, bar_height))
        pygame.draw.rect(screen, WHITE, (bar_x, bar_y, bar_width, bar_height), 3)


class AlienMothership:
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)
        self.health = 30
        self.max_health = 30
        self.rect = pygame.Rect(int(self.x - 80), int(self.y - 40), 160, 80)
        self.shoot_timer = 0
        self.movement_timer = 0
        self.direction = 1
        self.phase = 1

    def update(self, player_x):
        self.x += self.direction * 2

        if self.x <= 100 or self.x >= GAME_AREA_WIDTH - 100:
            self.direction *= -1
            if self.x <= 100:
                self.x = 100
            if self.x >= GAME_AREA_WIDTH - 100:
                self.x = GAME_AREA_WIDTH - 100

        self.rect.centerx = int(self.x)
        self.rect.centery = int(self.y)
        self.shoot_timer += 1

        if self.health > 20:
            self.phase = 1
        elif self.health > 10:
            self.phase = 2
        else:
            self.phase = 3

    def shoot(self, sound_manager):
        bullets = []

        if self.phase == 1:
            if self.shoot_timer > 40:
                bullets.append(Bullet(self.x, self.y + 40, (0, 4), GREEN, 2, 1.5))
                sound_manager.play_sound('enemy_shoot')
                self.shoot_timer = 0

        elif self.phase == 2:
            if self.shoot_timer > 35:
                bullets.extend([
                    Bullet(self.x - 30, self.y + 40, (-1, 4), GREEN, 2, 1.5),
                    Bullet(self.x, self.y + 40, (0, 5), GREEN, 2, 1.5),
                    Bullet(self.x + 30, self.y + 40, (1, 4), GREEN, 2, 1.5)
                ])
                sound_manager.play_sound('enemy_shoot')
                self.shoot_timer = 0

        elif self.phase == 3:
            if self.shoot_timer > 25:
                for i in range(-2, 3):
                    angle = i * 0.4
                    vel_x = math.sin(angle) * 4
                    vel_y = 5 + abs(i)
                    bullets.append(Bullet(self.x + i * 25, self.y + 40, (vel_x, vel_y), (0, 255, 100), 2, 1.5))
                sound_manager.play_sound('enemy_shoot')
                self.shoot_timer = 0

        return bullets

    def take_damage(self, damage, sound_manager):
        self.health -= damage
        sound_manager.play_sound('boss_hit')
        return self.health <= 0

    def draw(self, screen):
        center = (int(self.x), int(self.y))

        pygame.draw.ellipse(screen, GREEN, (self.x - 70, self.y - 35, 140, 70))
        pygame.draw.ellipse(screen, (0, 200, 0), (self.x - 70, self.y - 35, 140, 70), 3)

        pulse = abs(math.sin(pygame.time.get_ticks() * 0.01))
        pod_color = (int(100 + 100 * pulse), int(255 - 50 * pulse), int(100 + 50 * pulse))

        pod_positions = [(-40, -10), (40, -10), (-20, 10), (20, 10), (0, -20)]
        for px, py in pod_positions:
            pod_size = int(8 + 3 * pulse)
            pygame.draw.circle(screen, pod_color, (int(self.x + px), int(self.y + py)), pod_size)
            pygame.draw.circle(screen, WHITE, (int(self.x + px), int(self.y + py)), pod_size, 2)

        pygame.draw.ellipse(screen, (150, 255, 150), (self.x - 25, self.y - 15, 50, 30))
        pygame.draw.ellipse(screen, WHITE, (self.x - 25, self.y - 15, 50, 30), 2)

        if self.phase >= 2:
            pygame.draw.circle(screen, (255, 100, 100), (int(self.x - 50), int(self.y)), 6)
            pygame.draw.circle(screen, (255, 100, 100), (int(self.x + 50), int(self.y)), 6)
        if self.phase >= 3:
            pygame.draw.circle(screen, (255, 0, 0), (int(self.x), int(self.y + 25)), 8)

        bar_width = 200
        bar_height = 12
        bar_x = GAME_AREA_WIDTH // 2 - bar_width // 2
        bar_y = 50

        pygame.draw.rect(screen, RED, (bar_x, bar_y, bar_width, bar_height))
        health_width = int(bar_width * (self.health / self.max_health))
        health_color = GREEN if self.health > 20 else ORANGE if self.health > 10 else RED
        pygame.draw.rect(screen, health_color, (bar_x, bar_y, health_width, bar_height))
        pygame.draw.rect(screen, WHITE, (bar_x, bar_y, bar_width, bar_height), 3)

        health_text = pygame.font.Font(None, 36).render(f"ALIEN MOTHERSHIP: {self.health}/30", True, WHITE)
        health_rect = health_text.get_rect(center=(GAME_AREA_WIDTH // 2, bar_y - 20))
        screen.blit(health_text, health_rect)


class Player:
    def __init__(self, x, y, difficulty='normal'):
        self.x = x
        self.y = y
        self.difficulty = difficulty

        difficulty_settings = {
            'easy': {'health': 7, 'speed': 6, 'ammo': 100},
            'normal': {'health': 5, 'speed': 5, 'ammo': 75},
            'hard': {'health': 3, 'speed': 4, 'ammo': 50}
        }

        settings = difficulty_settings.get(difficulty, difficulty_settings['normal'])
        self.health = settings['health']
        self.max_health = settings['health']
        self.speed = settings['speed']

        self.ammo = settings['ammo']
        self.max_ammo = settings['ammo']
        self.reload_timer = 0
        self.reloading = False
        self.no_ammo_display = 0

        self.rect = pygame.Rect(x, y, 60, 60)
        self.shoot_timer = 0
        self.power_ups = {
            'triple_shot': 0,
            'shield': 0,
            'speed': 0
        }

    def update(self):
        keys = pygame.key.get_pressed()

        speed = self.speed * (2 if self.power_ups['speed'] > 0 else 1)

        if keys[pygame.K_LEFT] and self.x > 30:
            self.x -= speed
        if keys[pygame.K_RIGHT] and self.x < GAME_AREA_WIDTH - 30:
            self.x += speed
        if keys[pygame.K_UP] and self.y > 30:
            self.y -= speed
        if keys[pygame.K_DOWN] and self.y < SCREEN_HEIGHT - 30:
            self.y += speed

        self.rect.center = (self.x, self.y)
        self.shoot_timer += 1

        if self.reloading:
            self.reload_timer -= 1
            if self.reload_timer <= 0:
                self.ammo = self.max_ammo
                self.reloading = False

        if self.no_ammo_display > 0:
            self.no_ammo_display -= 1

        for power in self.power_ups:
            if self.power_ups[power] > 0:
                self.power_ups[power] -= 1

    def shoot(self, sound_manager):
        if self.shoot_timer > 8:
            self.shoot_timer = 0

            if self.ammo <= 0 and not self.reloading:
                self.no_ammo_display = 60
                sound_manager.play_sound('no_ammo')
                return []

            if self.reloading:
                return []

            bullets = []

            if self.power_ups['triple_shot'] > 0 and self.ammo >= 3:
                bullets.extend([
                    Bullet(self.x - 22, self.y - 30, (0, -10), CYAN, 2, 1.3),
                    Bullet(self.x, self.y - 30, (0, -10), CYAN, 2, 1.3),
                    Bullet(self.x + 22, self.y - 30, (0, -10), CYAN, 2, 1.3)
                ])
                self.ammo -= 3
            elif self.ammo >= 1:
                bullets.append(Bullet(self.x, self.y - 30, (0, -10), WHITE, 1, 1.2))
                self.ammo -= 1

            if self.ammo <= 0:
                self.reloading = True
                self.reload_timer = 120
                sound_manager.play_sound('reload')

            sound_manager.play_sound('player_shoot')
            return bullets
        return []

    def take_damage(self, damage):
        if self.power_ups['shield'] > 0:
            return False
        self.health -= damage
        return self.health <= 0

    def heal(self, amount):
        self.health = min(self.max_health, self.health + amount)

    def add_power_up(self, power_type, sound_manager):
        if power_type == 'heal':
            self.heal(1)
        elif power_type == 'ammo':
            self.ammo = min(self.max_ammo, self.ammo + 25)
            if self.reloading:
                self.reloading = False
                self.reload_timer = 0
        elif power_type == 'shield':
            self.power_ups[power_type] = 600
            sound_manager.play_sound('shield_activate')
        else:
            self.power_ups[power_type] = 600

        sound_manager.play_sound('powerup')

    def draw(self, screen):
        ship_color = GREEN if self.power_ups['shield'] > 0 else BLUE
        draw_player_ship(screen, int(self.x), int(self.y), ship_color)

        if self.power_ups['shield'] > 0:
            shield_alpha = int(100 + 50 * math.sin(self.power_ups['shield'] * 0.2))
            shield_surface = pygame.Surface((90, 90), pygame.SRCALPHA)
            shield_color = (*GREEN[:3], shield_alpha)
            pygame.draw.circle(shield_surface, shield_color, (45, 45), 40)
            screen.blit(shield_surface, (self.x - 45, self.y - 45))

        for i in range(self.max_health):
            heart_color = GREEN if i < self.health else DARK_GRAY
            pygame.draw.circle(screen, heart_color, (30 + i * 35, 30), 12)
            pygame.draw.circle(screen, WHITE, (30 + i * 35, 30), 12, 3)

        if self.no_ammo_display > 0:
            font = pygame.font.Font(None, 48)
            no_ammo_text = font.render("NO AMMO!", True, RED)
            text_rect = no_ammo_text.get_rect(center=(self.x, self.y - 60))

            alpha = int(200 + 55 * math.sin(self.no_ammo_display * 0.5))
            no_ammo_surface = pygame.Surface(no_ammo_text.get_size(), pygame.SRCALPHA)
            red_with_alpha = (*RED[:3], alpha)
            no_ammo_surface.fill(red_with_alpha)
            screen.blit(no_ammo_surface, text_rect)