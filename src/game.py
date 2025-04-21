import pygame
import json
import os
from ui import draw_title_screen, draw_menu_screen, draw_level_select_screen, draw_game_ui, draw_pause_menu
from physics import compute_fields
from levels import LEVELS

WIDTH, HEIGHT = 800, 600
GRID_SIZE = 20
PROGRESS_FILE = "progress.json"

def load_progress():
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, 'r') as f:
            return json.load(f)
    else:
        return {"unlocked": 1}

def save_progress(progress):
    with open(PROGRESS_FILE, 'w') as f:
        json.dump(progress, f)

def run_game(screen):
    clock = pygame.time.Clock()
    state = "title"
    selected_level = None
    progress = load_progress()
    paused = False
    level_start_time = 0
    time_elapsed = 0

    charges = []
    charge_vals = []
    loops = []
    win_zone = None

    while True:
        screen.fill((0, 0, 0))
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_progress(progress)
                return

            if state == "title" and event.type == pygame.KEYDOWN:
                state = "menu"

            elif state == "menu" and event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                if 300 <= x <= 500:
                    if 250 <= y <= 300:
                        state = "level_select"
                    elif 350 <= y <= 400:
                        state = "free_play"

            elif state == "level_select" and event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                col = (x - 100) // 80
                row = (y - 100) // 60
                idx = row * 8 + col
                if 0 <= col < 8 and idx < progress["unlocked"] and idx < len(LEVELS):
                    selected_level = idx + 1
                    data = LEVELS[str(selected_level)]
                    charges = data["charges"]
                    charge_vals = [50] * len(charges)
                    loops = data["loops"]
                    win_zone = data["win_zone"]
                    level_start_time = pygame.time.get_ticks()
                    time_elapsed = 0
                    state = "play_level"

            elif state == "play_level":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        paused = not paused
                    elif paused and event.key == pygame.K_r:
                        data = LEVELS[str(selected_level)]
                        charges = data["charges"]
                        charge_vals = [50] * len(charges)
                        loops = data["loops"]
                        win_zone = data["win_zone"]
                        level_start_time = pygame.time.get_ticks()
                        time_elapsed = 0
                        paused = False
                    elif paused and event.key == pygame.K_b:
                        state = "level_select"
                        paused = False

                if not paused:
                    if pygame.mouse.get_pressed()[0]:
                        charges.append(mouse_pos)
                        charge_vals.append(50)
                    elif pygame.mouse.get_pressed()[2]:
                        loops.append(mouse_pos)

        # Draw based on state
        if state == "title":
            draw_title_screen(screen)
        elif state == "menu":
            draw_menu_screen(screen)
        elif state == "level_select":
            draw_level_select_screen(screen, progress["unlocked"])
        elif state == "free_play":
            if pygame.mouse.get_pressed()[0]:
                charges.append(mouse_pos)
                charge_vals.append(50)
            elif pygame.mouse.get_pressed()[2]:
                loops.append(mouse_pos)
            field = compute_fields(charges, charge_vals, loops, WIDTH, HEIGHT)
            for y in range(0, HEIGHT, GRID_SIZE):
                for x in range(0, WIDTH, GRID_SIZE):
                    fx, fy = field[y//GRID_SIZE][x//GRID_SIZE]
                    pygame.draw.line(screen, (0, 255, 255), (x, y), (x + fx, y + fy), 1)
        elif state == "play_level":
            if not paused:
                time_elapsed = (pygame.time.get_ticks() - level_start_time) // 1000

                field = compute_fields(charges, charge_vals, loops, WIDTH, HEIGHT)
                for y in range(0, HEIGHT, GRID_SIZE):
                    for x in range(0, WIDTH, GRID_SIZE):
                        fx, fy = field[y//GRID_SIZE][x//GRID_SIZE]
                        pygame.draw.line(screen, (0, 255, 255), (x, y), (x + fx, y + fy), 1)

                # Win zone
                pygame.draw.circle(screen, (0, 255, 0), win_zone, 10)
                for c in charges:
                    if (c[0] - win_zone[0])**2 + (c[1] - win_zone[1])**2 < 100:
                        if selected_level == progress["unlocked"] and selected_level < 30:
                            progress["unlocked"] += 1
                            save_progress(progress)
                        font = pygame.font.SysFont("Arial", 32)
                        win_text = font.render(f"Level {selected_level} complete!", True, (255, 255, 0))
                        screen.blit(win_text, (240, 280))

            draw_game_ui(screen, selected_level, time_elapsed, paused)

            if paused:
                draw_pause_menu(screen)

        pygame.display.flip()
        clock.tick(60)
