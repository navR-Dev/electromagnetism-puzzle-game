import pygame
import numpy as np
from physics import compute_fields

WIDTH, HEIGHT = 800, 600
GRID_SPACING = 20
FPS = 30

POSITIVE_CHARGE_COLOR = (255, 0, 0)
NEGATIVE_CHARGE_COLOR = (0, 0, 255)
LOOP_COLOR = (0, 255, 0)
FIELD_LINE_COLOR = (200, 200, 255)
BACKGROUND_COLOR = (0, 0, 0)

def draw_charges(screen, charges, charge_vals):
    for (x, y), val in zip(charges, charge_vals):
        color = POSITIVE_CHARGE_COLOR if val > 0 else NEGATIVE_CHARGE_COLOR
        pygame.draw.circle(screen, color, (int(x), int(y)), 8)

def draw_loops(screen, loops):
    for x, y in loops:
        pygame.draw.circle(screen, LOOP_COLOR, (int(x), int(y)), 8, 2)

def draw_field_lines(screen, field):
    for y in range(field.shape[0]):
        for x in range(field.shape[1]):
            fx, fy = field[y, x]
            start_pos = (x * GRID_SPACING, y * GRID_SPACING)
            end_pos = (start_pos[0] + fx * 0.5, start_pos[1] + fy * 0.5)
            pygame.draw.line(screen, FIELD_LINE_COLOR, start_pos, end_pos, 1)

def run_game(screen):
    clock = pygame.time.Clock()
    charges = []
    charge_vals = []
    loops = []

    running = True
    while running:
        screen.fill(BACKGROUND_COLOR)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click - positive charge
                    charges.append(event.pos)
                    charge_vals.append(5)
                elif event.button == 3:  # Right click - negative charge
                    charges.append(event.pos)
                    charge_vals.append(-5)
                elif event.button == 2:  # Middle click - current loop
                    loops.append(event.pos)

        field = compute_fields(charges, charge_vals, loops, WIDTH, HEIGHT)
        draw_field_lines(screen, field)
        draw_charges(screen, charges, charge_vals)
        draw_loops(screen, loops)

        pygame.display.flip()
        clock.tick(FPS)
