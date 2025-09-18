import pygame
from constants import *


def draw_player_ship(screen, x, y, color=BLUE, size=1.0):
    scale = size * 1.5
    points = [
        (x, y - int(20 * scale)),
        (x - int(18 * scale), y + int(15 * scale)),
        (x - int(9 * scale), y + int(8 * scale)),
        (x + int(9 * scale), y + int(8 * scale)),
        (x + int(18 * scale), y + int(15 * scale))
    ]
    pygame.draw.polygon(screen, color, points)
    pygame.draw.polygon(screen, WHITE, points, 3)

    flame_points = [
        (x - int(6 * scale), y + int(12 * scale)),
        (x, y + int(25 * scale)),
        (x + int(6 * scale), y + int(12 * scale))
    ]
    pygame.draw.polygon(screen, ORANGE, flame_points)

    pygame.draw.circle(screen, CYAN, (x - int(12 * scale), y + int(3 * scale)), int(4 * scale))
    pygame.draw.circle(screen, CYAN, (x + int(12 * scale), y + int(3 * scale)), int(4 * scale))

    pygame.draw.circle(screen, LIGHT_BLUE, (x, y - int(3 * scale)), int(6 * scale))
    pygame.draw.circle(screen, WHITE, (x, y - int(3 * scale)), int(6 * scale), 2)


def draw_enemy_ship(screen, x, y, enemy_type, size=1.0):
    scale = size * 1.5

    if enemy_type == 'basic':
        points = [
            (x, y + int(20 * scale)),
            (x - int(15 * scale), y - int(12 * scale)),
            (x - int(6 * scale), y - int(4 * scale)),
            (x + int(6 * scale), y - int(4 * scale)),
            (x + int(15 * scale), y - int(12 * scale))
        ]
        pygame.draw.polygon(screen, RED, points)
        pygame.draw.polygon(screen, DARK_RED, points, 3)
        pygame.draw.circle(screen, ORANGE, (x, y - int(7 * scale)), int(4 * scale))

    elif enemy_type == 'heavy':
        points = [
            (x, y + int(25 * scale)),
            (x - int(22 * scale), y + int(12 * scale)),
            (x - int(18 * scale), y - int(12 * scale)),
            (x, y - int(18 * scale)),
            (x + int(18 * scale), y - int(12 * scale)),
            (x + int(22 * scale), y + int(12 * scale))
        ]
        pygame.draw.polygon(screen, ORANGE, points)
        pygame.draw.polygon(screen, RED, points, 3)
        pygame.draw.circle(screen, YELLOW, (x - int(9 * scale), y - int(3 * scale)), int(4 * scale))
        pygame.draw.circle(screen, YELLOW, (x + int(9 * scale), y - int(3 * scale)), int(4 * scale))

    elif enemy_type == 'fast':
        points = [
            (x, y + int(18 * scale)),
            (x - int(12 * scale), y + int(6 * scale)),
            (x - int(9 * scale), y - int(15 * scale)),
            (x, y - int(12 * scale)),
            (x + int(9 * scale), y - int(15 * scale)),
            (x + int(12 * scale), y + int(6 * scale))
        ]
        pygame.draw.polygon(screen, PURPLE, points)
        pygame.draw.polygon(screen, WHITE, points, 3)
        for i in range(3):
            trail_y = y + int(12 * scale) + i * int(4 * scale)
            pygame.draw.line(screen, CYAN, (x - int(4 * scale), trail_y), (x + int(4 * scale), trail_y), 3)


def draw_boss_ship(screen, x, y, phase=1, size=1.0):
    scale = size * 2.0

    main_color = YELLOW if phase == 1 else ORANGE if phase == 2 else RED

    points = [
        (x, y - int(35 * scale)),
        (x - int(45 * scale), y - int(22 * scale)),
        (x - int(60 * scale), y + int(15 * scale)),
        (x - int(30 * scale), y + int(35 * scale)),
        (x + int(30 * scale), y + int(35 * scale)),
        (x + int(60 * scale), y + int(15 * scale)),
        (x + int(45 * scale), y - int(22 * scale))
    ]
    pygame.draw.polygon(screen, main_color, points)
    pygame.draw.polygon(screen, WHITE, points, 4)

    pygame.draw.ellipse(screen, GRAY, (x - int(50 * scale), y - int(15 * scale), int(30 * scale), int(22 * scale)))
    pygame.draw.ellipse(screen, GRAY, (x + int(20 * scale), y - int(15 * scale), int(30 * scale), int(22 * scale)))

    for i in range(-3, 4):
        engine_x = x + i * int(12 * scale)
        pygame.draw.circle(screen, CYAN, (engine_x, y + int(28 * scale)), int(6 * scale))
        pygame.draw.circle(screen, WHITE, (engine_x, y + int(28 * scale)), int(6 * scale), 2)

    pygame.draw.ellipse(screen, LIGHT_BLUE, (x - int(22 * scale), y - int(12 * scale), int(44 * scale), int(24 * scale)))
    pygame.draw.ellipse(screen, WHITE, (x - int(22 * scale), y - int(12 * scale), int(44 * scale), int(24 * scale)), 3)

    if phase >= 2:
        pygame.draw.circle(screen, RED, (x - int(35 * scale), y), int(7 * scale))
        pygame.draw.circle(screen, RED, (x + int(35 * scale), y), int(7 * scale))
    if phase >= 3:
        pygame.draw.circle(screen, DARK_RED, (x, y + int(15 * scale)), int(9 * scale))