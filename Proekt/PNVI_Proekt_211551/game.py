import pygame
import random
import math
import json
from constants import *
from sound_manager import SoundManager
from effects import PowerUpNotification, Particle
from entities import Player, Enemy, Boss, AlienMothership, PowerUp, Bullet
from graphics import draw_player_ship


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Galactic Defense Shooter - Петар Пејоски 211551")
        self.clock = pygame.time.Clock()

        self.sound_manager = SoundManager()

        self.state = 'menu'
        self.difficulty = 'normal'
        self.difficulty_multipliers = {
            'easy': 0.7,
            'normal': 1.0,
            'hard': 1.5
        }

        self.level = 1
        self.score = 0
        self.high_score = self.load_high_score()

        self.player = None
        self.player_bullets = []
        self.enemy_bullets = []
        self.enemies = []
        self.boss = None
        self.alien_mothership = None
        self.mothership_spawned = False
        self.power_ups = []
        self.particles = []
        self.power_up_notifications = []

        self.enemy_spawn_timer = 0
        self.power_up_spawn_timer = 0
        self.level_timer = 0

        self.font = pygame.font.Font(None, 48)
        self.big_font = pygame.font.Font(None, 96)
        self.small_font = pygame.font.Font(None, 32)
        self.tiny_font = pygame.font.Font(None, 24)

        self.stars = [(random.randint(0, GAME_AREA_WIDTH), random.randint(0, SCREEN_HEIGHT)) for _ in range(150)]

    def load_high_score(self):
        try:
            with open('high_score.json', 'r') as f:
                data = json.load(f)
                return data.get('high_score', 0)
        except:
            return 0

    def save_high_score(self):
        try:
            with open('high_score.json', 'w') as f:
                json.dump({'high_score': self.high_score}, f)
        except:
            pass

    def create_explosion(self, x, y, color=ORANGE):
        self.sound_manager.play_sound('explosion')
        for _ in range(20):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(3, 12)
            velocity = (math.cos(angle) * speed, math.sin(angle) * speed)
            self.particles.append(Particle(x, y, color, velocity))

    def spawn_enemies(self):
        self.enemy_spawn_timer += 1
        difficulty_mult = self.difficulty_multipliers[self.difficulty]
        spawn_rate = max(20, int((60 - self.level * 5) / difficulty_mult))

        if self.enemy_spawn_timer > spawn_rate:
            self.enemy_spawn_timer = 0
            enemy_type = random.choice(['basic', 'basic', 'heavy', 'fast'])
            x = random.randint(50, GAME_AREA_WIDTH - 50)
            self.enemies.append(Enemy(x, -50, enemy_type))

    def spawn_boss(self):
        if not self.boss and len(self.enemies) == 0 and self.level_timer > 1800:
            self.boss = Boss(GAME_AREA_WIDTH // 2, 150)

    def spawn_mothership(self):
        if not self.mothership_spawned and not self.alien_mothership and self.score >= 200:
            for enemy in self.enemies:
                self.create_explosion(enemy.x, enemy.y, ORANGE)

            if self.boss:
                self.create_explosion(self.boss.x, self.boss.y, YELLOW)

            self.enemies.clear()
            self.boss = None
            self.enemy_bullets.clear()
            self.power_ups.clear()

            self.alien_mothership = AlienMothership(GAME_AREA_WIDTH // 2, 150)
            self.mothership_spawned = True
            self.sound_manager.play_sound('mothership_spawn')

            for _ in range(50):
                angle = random.uniform(0, 2 * math.pi)
                speed = random.uniform(5, 15)
                velocity = (math.cos(angle) * speed, math.sin(angle) * speed)
                self.particles.append(Particle(GAME_AREA_WIDTH // 2, 100, GREEN, velocity))

            self.power_up_notifications.append(
                PowerUpNotification('mothership_spawned', GAME_AREA_WIDTH // 2, SCREEN_HEIGHT // 2)
            )

    def spawn_power_ups(self):
        self.power_up_spawn_timer += 1
        power_up_rate = 600 if self.difficulty == 'easy' else 900 if self.difficulty == 'normal' else 1200

        if self.power_up_spawn_timer > power_up_rate:
            self.power_up_spawn_timer = 0
            if random.random() < 0.8:
                x = random.randint(50, GAME_AREA_WIDTH - 50)
                power_type = random.choice(['triple_shot', 'shield', 'heal', 'speed', 'ammo'])
                self.power_ups.append(PowerUp(x, -30, power_type))

    def handle_collisions(self):
        difficulty_mult = self.difficulty_multipliers[self.difficulty]

        for bullet in self.player_bullets[:]:
            for enemy in self.enemies[:]:
                if bullet.rect.colliderect(enemy.rect):
                    self.player_bullets.remove(bullet)
                    if enemy.take_damage(bullet.damage):
                        self.enemies.remove(enemy)
                        self.score += int((10 + self.level * 5) * difficulty_mult)
                        self.create_explosion(enemy.x, enemy.y)
                    break

        if self.boss:
            for bullet in self.player_bullets[:]:
                if bullet.rect.colliderect(self.boss.rect):
                    self.player_bullets.remove(bullet)
                    if self.boss.take_damage(bullet.damage, self.sound_manager):
                        self.score += int(500 * difficulty_mult)
                        self.create_explosion(self.boss.x, self.boss.y, YELLOW)
                        self.boss = None
                        self.level += 1
                        self.level_timer = 0

        if self.alien_mothership:
            for bullet in self.player_bullets[:]:
                if bullet.rect.colliderect(self.alien_mothership.rect):
                    self.player_bullets.remove(bullet)
                    if self.alien_mothership.take_damage(bullet.damage, self.sound_manager):
                        self.score += int(1000 * difficulty_mult)
                        self.sound_manager.play_sound('mothership_destroy')
                        for _ in range(50):
                            angle = random.uniform(0, 2 * math.pi)
                            speed = random.uniform(8, 20)
                            velocity = (math.cos(angle) * speed, math.sin(angle) * speed)
                            color = random.choice([GREEN, YELLOW, WHITE])
                            self.particles.append(
                                Particle(self.alien_mothership.x, self.alien_mothership.y, color, velocity))

                        self.power_up_notifications.append(
                            PowerUpNotification('mothership_destroyed', GAME_AREA_WIDTH // 2, SCREEN_HEIGHT // 2)
                        )

                        self.alien_mothership = None
                        self.level += 2

                        for _ in range(3):
                            power_type = random.choice(['triple_shot', 'shield', 'ammo'])
                            self.power_ups.append(PowerUp(random.randint(100, GAME_AREA_WIDTH - 100), -30, power_type))
                    break

        for bullet in self.enemy_bullets[:]:
            if bullet.rect.colliderect(self.player.rect):
                self.enemy_bullets.remove(bullet)
                if self.player.take_damage(bullet.damage):
                    self.state = 'game_over'
                    self.sound_manager.play_sound('game_over')
                    if self.score > self.high_score:
                        self.high_score = self.score
                        self.save_high_score()

        for power_up in self.power_ups[:]:
            if power_up.rect.colliderect(self.player.rect):
                self.power_ups.remove(power_up)
                self.player.add_power_up(power_up.power_type, self.sound_manager)
                self.score += 50

                self.power_up_notifications.append(
                    PowerUpNotification(power_up.power_type, self.player.x, self.player.y - 80)
                )

    def draw_info_panel(self):
        panel_x = GAME_AREA_WIDTH
        panel_rect = pygame.Rect(panel_x, 0, INFO_PANEL_WIDTH, SCREEN_HEIGHT)

        pygame.draw.rect(self.screen, (20, 20, 40), panel_rect)
        pygame.draw.line(self.screen, WHITE, (panel_x, 0), (panel_x, SCREEN_HEIGHT), 3)

        y_offset = 30

        title_text = self.font.render("INFO PANEL", True, CYAN)
        title_rect = title_text.get_rect(centerx=panel_x + INFO_PANEL_WIDTH // 2)
        title_rect.y = y_offset
        self.screen.blit(title_text, title_rect)
        y_offset += 70

        if self.state == 'playing' and self.player:
            ammo_title = self.small_font.render("AMMO STATUS", True, WHITE)
            ammo_title_rect = ammo_title.get_rect(centerx=panel_x + INFO_PANEL_WIDTH // 2)
            ammo_title_rect.y = y_offset
            self.screen.blit(ammo_title, ammo_title_rect)
            y_offset += 40

            bar_width = 200
            bar_height = 20
            bar_x = panel_x + (INFO_PANEL_WIDTH - bar_width) // 2
            bar_y = y_offset

            pygame.draw.rect(self.screen, DARK_GRAY, (bar_x, bar_y, bar_width, bar_height))
            if self.player.reloading:
                reload_progress = 1 - (self.player.reload_timer / 120)
                progress_width = int(bar_width * reload_progress)
                pygame.draw.rect(self.screen, YELLOW, (bar_x, bar_y, progress_width, bar_height))
                reload_text = self.tiny_font.render("RELOADING...", True, YELLOW)
            else:
                ammo_ratio = self.player.ammo / self.player.max_ammo
                ammo_width = int(bar_width * ammo_ratio)
                ammo_color = GREEN if ammo_ratio > 0.5 else ORANGE if ammo_ratio > 0.2 else RED
                pygame.draw.rect(self.screen, ammo_color, (bar_x, bar_y, ammo_width, bar_height))
                reload_text = self.tiny_font.render(f"{self.player.ammo}/{self.player.max_ammo}", True, WHITE)

            pygame.draw.rect(self.screen, WHITE, (bar_x, bar_y, bar_width, bar_height), 2)
            reload_rect = reload_text.get_rect(centerx=panel_x + INFO_PANEL_WIDTH // 2)
            reload_rect.y = y_offset + 25
            self.screen.blit(reload_text, reload_rect)
            y_offset += 80

        powerup_title = self.small_font.render("POWER-UPS GUIDE", True, WHITE)
        powerup_title_rect = powerup_title.get_rect(centerx=panel_x + INFO_PANEL_WIDTH // 2)
        powerup_title_rect.y = y_offset
        self.screen.blit(powerup_title, powerup_title_rect)
        y_offset += 50

        power_up_info = [
            ("TRIPLE SHOT", "Fires 3 bullets at once", CYAN),
            ("SHIELD", "Blocks incoming damage", GREEN),
            ("HEALTH", "Restores 1 health point", RED),
            ("SPEED BOOST", "Increases movement speed", YELLOW),
            ("AMMO REFILL", "Restores ammunition", ORANGE)
        ]

        for name, description, color in power_up_info:
            icon_x = panel_x + 20
            icon_y = y_offset + 5
            pygame.draw.circle(self.screen, color, (icon_x, icon_y), 12)
            pygame.draw.circle(self.screen, WHITE, (icon_x, icon_y), 12, 2)

            name_text = self.tiny_font.render(name, True, color)
            desc_text = self.tiny_font.render(description, True, WHITE)

            self.screen.blit(name_text, (icon_x + 25, icon_y - 15))
            self.screen.blit(desc_text, (icon_x + 25, icon_y + 2))

            y_offset += 35

        y_offset += 20
        enemy_title = self.small_font.render("ENEMY TYPES", True, WHITE)
        enemy_title_rect = enemy_title.get_rect(centerx=panel_x + INFO_PANEL_WIDTH // 2)
        enemy_title_rect.y = y_offset
        self.screen.blit(enemy_title, enemy_title_rect)
        y_offset += 40

        enemy_info = [
            ("RED", "Basic Fighter - Straight attack", RED),
            ("ORANGE", "Heavy Assault - Zigzag pattern", ORANGE),
            ("PURPLE", "Fast Interceptor - Tracks player", PURPLE),
            ("YELLOW", "Phase Boss - Multi-phase attacks", YELLOW),
            ("GREEN", "ALIEN MOTHERSHIP at 200pts!", GREEN)
        ]

        for name, description, color in enemy_info:
            icon_x = panel_x + 20
            icon_y = y_offset + 5
            if name == "GREEN":
                pygame.draw.polygon(self.screen, color, [
                    (icon_x - 8, icon_y), (icon_x + 8, icon_y),
                    (icon_x + 6, icon_y + 8), (icon_x - 6, icon_y + 8)
                ])
                pygame.draw.circle(self.screen, (0, 255, 100), (icon_x, icon_y), 4)
            else:
                pygame.draw.polygon(self.screen, color, [
                    (icon_x, icon_y - 8), (icon_x - 8, icon_y + 8), (icon_x + 8, icon_y + 8)
                ])
            pygame.draw.polygon(self.screen, WHITE, [
                (icon_x, icon_y - 8), (icon_x - 8, icon_y + 8), (icon_x + 8, icon_y + 8)
            ], 1)

            name_text = self.tiny_font.render(name, True, color)
            desc_text = self.tiny_font.render(description, True, WHITE)

            self.screen.blit(name_text, (icon_x + 25, icon_y - 10))
            self.screen.blit(desc_text, (icon_x + 25, icon_y + 5))

            y_offset += 30

        y_offset += 20
        controls_title = self.small_font.render("CONTROLS", True, WHITE)
        controls_title_rect = controls_title.get_rect(centerx=panel_x + INFO_PANEL_WIDTH // 2)
        controls_title_rect.y = y_offset
        self.screen.blit(controls_title, controls_title_rect)
        y_offset += 30

        controls = [
            "Arrow Keys: Move",
            "SPACE: Shoot",
            "P: Pause Game"
        ]

        for control in controls:
            control_text = self.tiny_font.render(control, True, WHITE)
            control_rect = control_text.get_rect(centerx=panel_x + INFO_PANEL_WIDTH // 2)
            control_rect.y = y_offset
            self.screen.blit(control_text, control_rect)
            y_offset += 20

    def update_game(self):
        if self.state != 'playing':
            return

        self.level_timer += 1
        difficulty_mult = self.difficulty_multipliers[self.difficulty]

        self.player.update()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            self.player_bullets.extend(self.player.shoot(self.sound_manager))

        if keys[pygame.K_m] and not self.alien_mothership and not self.mothership_spawned:
            self.spawn_mothership()

        for bullet in self.player_bullets[:]:
            bullet.update()
            if bullet.y < 0 or bullet.x < 0 or bullet.x > GAME_AREA_WIDTH:
                self.player_bullets.remove(bullet)

        for bullet in self.enemy_bullets[:]:
            bullet.update()
            if bullet.y > SCREEN_HEIGHT or bullet.x < 0 or bullet.x > GAME_AREA_WIDTH:
                self.enemy_bullets.remove(bullet)

        if not self.boss and not self.alien_mothership:
            self.spawn_enemies()

        for enemy in self.enemies[:]:
            enemy.update(self.player.x, difficulty_mult)
            bullet = enemy.shoot(difficulty_mult, self.sound_manager)
            if bullet:
                self.enemy_bullets.append(bullet)
            if enemy.y > SCREEN_HEIGHT or enemy.x < 0 or enemy.x > GAME_AREA_WIDTH:
                self.enemies.remove(enemy)

        if not self.boss and self.level_timer > 1800 and not self.alien_mothership:
            self.spawn_boss()

        if self.boss:
            self.boss.update(self.player.x)
            new_bullets = self.boss.shoot(self.sound_manager)
            self.enemy_bullets.extend(new_bullets)

        if self.alien_mothership:
            self.alien_mothership.update(self.player.x)
            new_bullets = self.alien_mothership.shoot(self.sound_manager)
            self.enemy_bullets.extend(new_bullets)

        self.spawn_mothership()

        if not self.alien_mothership:
            self.spawn_power_ups()

        for power_up in self.power_ups[:]:
            power_up.update()
            if power_up.y > SCREEN_HEIGHT or power_up.x < 0 or power_up.x > GAME_AREA_WIDTH:
                self.power_ups.remove(power_up)

        for particle in self.particles[:]:
            particle.update()
            if particle.life <= 0:
                self.particles.remove(particle)

        for notification in self.power_up_notifications[:]:
            notification.update()
            if notification.life <= 0:
                self.power_up_notifications.remove(notification)

        self.handle_collisions()

    def draw_stars(self):
        for i, (x, y) in enumerate(self.stars):
            self.stars[i] = (x, (y + 1) % SCREEN_HEIGHT)

            if self.alien_mothership:
                brightness = random.choice([(0, 255, 100), (100, 255, 150), (150, 255, 200)])
            else:
                brightness = random.choice([WHITE, GRAY, LIGHT_BLUE])
            pygame.draw.circle(self.screen, brightness, (int(x), int(y)), random.choice([1, 2]))

    def draw_game(self):
        if self.state != 'playing':
            return

        if self.alien_mothership:
            self.screen.fill((0, 20, 10))
        else:
            self.screen.fill(BLACK)
        self.draw_stars()

        if self.alien_mothership:
            glow_surface = pygame.Surface((GAME_AREA_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            glow_alpha = int(20 + 10 * math.sin(pygame.time.get_ticks() * 0.01))
            glow_surface.fill((0, 100, 0, glow_alpha))
            self.screen.blit(glow_surface, (0, 0))

            encounter_text = pygame.font.Font(None, 42).render("MOTHERSHIP BATTLE", True, YELLOW)
            encounter_rect = encounter_text.get_rect(center=(GAME_AREA_WIDTH // 2, 30))
            alpha = int(200 + 55 * math.sin(pygame.time.get_ticks() * 0.02))
            encounter_surface = pygame.Surface(encounter_text.get_size(), pygame.SRCALPHA)
            encounter_surface.fill((255, 255, 0, alpha))
            self.screen.blit(encounter_surface, encounter_rect)

        pygame.draw.line(self.screen, WHITE, (GAME_AREA_WIDTH, 0), (GAME_AREA_WIDTH, SCREEN_HEIGHT), 3)

        self.player.draw(self.screen)

        for bullet in self.player_bullets:
            bullet.draw(self.screen)

        for bullet in self.enemy_bullets:
            bullet.draw(self.screen)

        for enemy in self.enemies:
            enemy.draw(self.screen)

        if self.boss:
            self.boss.draw(self.screen)

        if self.alien_mothership:
            self.alien_mothership.draw(self.screen)

        for power_up in self.power_ups:
            power_up.draw(self.screen)

        for particle in self.particles:
            particle.draw(self.screen)

        for notification in self.power_up_notifications:
            notification.draw(self.screen, self.font)

        score_text = self.small_font.render(f"Score: {self.score}", True, WHITE)
        level_text = self.small_font.render(f"Level: {self.level}", True, WHITE)

        self.screen.blit(score_text, (GAME_AREA_WIDTH - 200, 70))
        self.screen.blit(level_text, (GAME_AREA_WIDTH - 200, 100))

        if self.score >= 180 and self.score < 200 and not self.mothership_spawned and not self.alien_mothership:
            points_needed = 200 - self.score
            warning_text = self.small_font.render(f"MOTHERSHIP IN {points_needed} PTS!", True, GREEN)
            warning_rect = warning_text.get_rect(center=(GAME_AREA_WIDTH // 2, 130))
            alpha = int(200 + 55 * math.sin(pygame.time.get_ticks() * 0.01))
            warning_surface = pygame.Surface(warning_text.get_size(), pygame.SRCALPHA)
            warning_surface.fill((0, 255, 0, alpha))
            self.screen.blit(warning_surface, warning_rect)

        self.draw_info_panel()

    def draw_menu(self):
        if not self.sound_manager.music_playing:
            self.sound_manager.play_music('sounds/menu_music.mp3')

        self.screen.fill(BLACK)
        self.draw_stars()

        draw_player_ship(self.screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 150, CYAN, 2.0)

        title_text = self.big_font.render("GALACTIC DEFENSE", True, CYAN)
        subtitle_text = self.big_font.render("SHOOTER", True, CYAN)
        start_text = self.font.render("Press SPACE to Select Difficulty", True, WHITE)
        quit_text = self.font.render("Press Q to Quit", True, WHITE)

        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 200))
        subtitle_rect = subtitle_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 150))
        start_rect = start_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 250))
        quit_rect = quit_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 300))

        self.screen.blit(title_text, title_rect)
        self.screen.blit(subtitle_text, subtitle_rect)
        self.screen.blit(start_text, start_rect)
        self.screen.blit(quit_text, quit_rect)

        if self.high_score > 0:
            high_score_text = self.font.render(f"High Score: {self.high_score}", True, YELLOW)
            high_score_rect = high_score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 350))
            self.screen.blit(high_score_text, high_score_rect)

    def draw_difficulty_selection(self):
        self.screen.fill(BLACK)
        self.draw_stars()

        title_text = self.big_font.render("SELECT DIFFICULTY", True, CYAN)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 120))
        self.screen.blit(title_text, title_rect)

        difficulties = [
            ("EASY", "More health, ammo, slower enemies", GREEN),
            ("NORMAL", "Balanced gameplay experience", YELLOW),
            ("HARD", "Less health, ammo, faster enemies", RED)
        ]

        for i, (diff_name, description, color) in enumerate(difficulties):
            y_pos = 300 + i * 150

            if diff_name.lower() == self.difficulty:
                pygame.draw.rect(self.screen, color, (SCREEN_WIDTH // 2 - 300, y_pos - 50, 600, 100), 4)

            diff_text = self.font.render(f"{i + 1}. {diff_name}", True, color)
            desc_text = self.small_font.render(description, True, WHITE)

            diff_rect = diff_text.get_rect(center=(SCREEN_WIDTH // 2, y_pos - 20))
            desc_rect = desc_text.get_rect(center=(SCREEN_WIDTH // 2, y_pos + 20))

            self.screen.blit(diff_text, diff_rect)
            self.screen.blit(desc_text, desc_rect)

        instruction_text = self.font.render("Press 1, 2, or 3 to select, ENTER to start", True, WHITE)
        instruction_rect = instruction_text.get_rect(center=(SCREEN_WIDTH // 2, 750))
        self.screen.blit(instruction_text, instruction_rect)

        back_text = self.small_font.render("Press ESC to go back", True, GRAY)
        back_rect = back_text.get_rect(center=(SCREEN_WIDTH // 2, 800))
        self.screen.blit(back_text, back_rect)

    def draw_game_over(self):
        self.screen.fill(BLACK)
        self.draw_stars()

        game_over_text = self.big_font.render("GAME OVER", True, RED)
        score_text = self.font.render(f"Final Score: {self.score}", True, WHITE)
        high_score_text = self.font.render(f"High Score: {self.high_score}", True, YELLOW)
        difficulty_text = self.font.render(f"Difficulty: {self.difficulty.title()}", True, CYAN)
        restart_text = self.font.render("Press R to Restart", True, WHITE)
        menu_text = self.font.render("Press M for Menu", True, WHITE)

        game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 150))
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 75))
        high_score_rect = high_score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 25))
        difficulty_rect = difficulty_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 25))
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100))
        menu_rect = menu_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 150))

        self.screen.blit(game_over_text, game_over_rect)
        self.screen.blit(score_text, score_rect)
        self.screen.blit(high_score_text, high_score_rect)
        self.screen.blit(difficulty_text, difficulty_rect)
        self.screen.blit(restart_text, restart_rect)
        self.screen.blit(menu_text, menu_rect)

    def reset_game(self):
        self.player = Player(GAME_AREA_WIDTH // 2, SCREEN_HEIGHT - 150, self.difficulty)
        self.player_bullets = []
        self.enemy_bullets = []
        self.enemies = []
        self.boss = None
        self.alien_mothership = None
        self.mothership_spawned = False
        self.power_ups = []
        self.particles = []
        self.power_up_notifications = []
        self.level = 1
        self.score = 0
        self.enemy_spawn_timer = 0
        self.power_up_spawn_timer = 0
        self.level_timer = 0

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.KEYDOWN:
                if self.state == 'menu':
                    if event.key == pygame.K_SPACE:
                        self.state = 'difficulty'
                    elif event.key == pygame.K_q:
                        return False

                elif self.state == 'difficulty':
                    if event.key == pygame.K_1:
                        self.difficulty = 'easy'
                    elif event.key == pygame.K_2:
                        self.difficulty = 'normal'
                    elif event.key == pygame.K_3:
                        self.difficulty = 'hard'
                    elif event.key == pygame.K_RETURN:
                        self.state = 'playing'
                        self.sound_manager.stop_music()
                        self.sound_manager.play_music('sounds/game_music.mp3')
                        self.reset_game()
                    elif event.key == pygame.K_ESCAPE:
                        self.state = 'menu'

                elif self.state == 'playing':
                    if event.key == pygame.K_p:
                        self.state = 'paused'

                elif self.state == 'paused':
                    if event.key == pygame.K_p:
                        self.state = 'playing'
                    elif event.key == pygame.K_m:
                        self.state = 'menu'
                        self.sound_manager.stop_music()

                elif self.state == 'game_over':
                    if event.key == pygame.K_r:
                        self.state = 'playing'
                        self.reset_game()
                    elif event.key == pygame.K_m:
                        self.state = 'menu'
                        self.sound_manager.stop_music()

        return True

    def run(self):
        running = True

        while running:
            running = self.handle_events()

            if self.state == 'playing':
                self.update_game()
                self.draw_game()
            elif self.state == 'menu':
                self.draw_menu()
            elif self.state == 'difficulty':
                self.draw_difficulty_selection()
            elif self.state == 'game_over':
                self.draw_game_over()
            elif self.state == 'paused':
                self.draw_game()
                pause_text = self.big_font.render("PAUSED", True, YELLOW)
                pause_rect = pause_text.get_rect(center=(GAME_AREA_WIDTH // 2, SCREEN_HEIGHT // 2))
                pygame.draw.rect(self.screen, BLACK,
                                 (pause_rect.x - 30, pause_rect.y - 30, pause_rect.width + 60, pause_rect.height + 60))
                pygame.draw.rect(self.screen, YELLOW,
                                 (pause_rect.x - 30, pause_rect.y - 30, pause_rect.width + 60, pause_rect.height + 60),
                                 4)
                self.screen.blit(pause_text, pause_rect)

            pygame.display.flip()
            self.clock.tick(FPS)

        pygame.quit()