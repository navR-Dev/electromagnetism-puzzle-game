import asyncio
import platform
import pygame
import numpy as np
import os
import json
from ui import draw_title_screen, draw_menu_screen, draw_level_select_screen, draw_game_ui, draw_pause_menu
from physics import compute_field_at_point, compute_field_grid
from levels import LEVELS, load_progress as load_levels_progress, save_progress as save_levels_progress

WIDTH, HEIGHT = 800, 600
GRID_SIZE = 20
FPS = 60
PROGRESS_FILE = "progress.json"
MAX_CHARGES = 5

def load_game_progress():
    if platform.system() != "Emscripten" and os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, 'r') as f:
            return json.load(f)
    return {"unlocked": 1}

def save_game_progress(progress):
    if platform.system() != "Emscripten":
        with open(PROGRESS_FILE, 'w') as f:
            json.dump(progress, f)

async def run_game(screen):
    clock = pygame.time.Clock()
    state = "title"
    selected_level = None
    progress = load_game_progress()
    paused = False
    level_start_time = 0
    time_elapsed = 0
    status_message = ""

    game_charge_pos = [0, 0]
    game_charge_vel = [0, 0]
    game_charge_val = 50
    placed_charges = []
    placed_charge_vals = []
    win_zone = None
    walls = []
    loops = []

    load_levels_progress()

    while True:
        screen.fill((0, 0, 0))
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_game_progress(progress)
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
                        placed_charges = []
                        placed_charge_vals = []
                        loops = []

            elif state == "level_select" and event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                col = (x - 100) // 80
                row = (y - 100) // 60
                idx = row * 8 + col
                if 0 <= col < 8 and idx < progress["unlocked"] and idx < len(LEVELS):
                    selected_level = idx + 1
                    data = LEVELS[str(selected_level)]
                    win_zone = data["goal_area"][:2]
                    walls = data["walls"]
                    game_charge_pos = data["start_pos"][:]
                    game_charge_val = data["game_charge_val"]
                    game_charge_vel = [0, 0]
                    placed_charges = []
                    placed_charge_vals = []
                    level_start_time = pygame.time.get_ticks()
                    time_elapsed = 0
                    state = "play_level"
                    status_message = ""
                    print(f"Level {selected_level} started: game_charge_pos={game_charge_pos}, game_charge_val={game_charge_val}")

            elif state == "play_level":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        paused = not paused
                    elif paused and event.key == pygame.K_r:
                        data = LEVELS[str(selected_level)]
                        win_zone = data["goal_area"][:2]
                        walls = data["walls"]
                        game_charge_pos = data["start_pos"][:]
                        game_charge_val = data["game_charge_val"]
                        game_charge_vel = [0, 0]
                        placed_charges = []
                        placed_charge_vals = []
                        level_start_time = pygame.time.get_ticks()
                        time_elapsed = 0
                        paused = False
                        status_message = ""
                        print(f"Level {selected_level} restarted: game_charge_pos={game_charge_pos}")
                    elif paused and event.key == pygame.K_b:
                        state = "level_select"
                        paused = False
                    elif not paused and event.key == pygame.K_c:
                        if placed_charges:
                            distances = [((mouse_pos[0] - c[0])**2 + (mouse_pos[1] - c[1])**2) for c in placed_charges]
                            if min(distances) < 2500:  # Within 50 pixels
                                idx = distances.index(min(distances))
                                placed_charges.pop(idx)
                                placed_charge_vals.pop(idx)
                                status_message = "Charge removed"
                            else:
                                status_message = "No charge nearby to remove"
                        else:
                            status_message = "No charges to remove"
                elif not paused and event.type == pygame.MOUSEBUTTONDOWN:
                    if len(placed_charges) < MAX_CHARGES:
                        if event.button == 1:
                            placed_charges.append(list(mouse_pos))
                            placed_charge_vals.append(50)
                            status_message = ""
                        elif event.button == 3:
                            placed_charges.append(list(mouse_pos))
                            placed_charge_vals.append(-50)
                            status_message = ""
                    else:
                        status_message = "Max charges reached (5)"

            elif state == "free_play":
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        placed_charges.append(list(mouse_pos))
                        placed_charge_vals.append(50)
                    elif event.button == 3:
                        placed_charges.append(list(mouse_pos))
                        placed_charge_vals.append(-50)
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_l:
                    loops.append(list(mouse_pos))

        if state == "play_level" and not paused:
            fx, fy = compute_field_at_point(game_charge_pos, placed_charges, placed_charge_vals, [], game_charge_val)
            print(f"Position: {game_charge_pos}, Velocity: {game_charge_vel}, Force: ({fx:.2f}, {fy:.2f})")
            game_charge_vel[0] += fx * 0.02
            game_charge_vel[1] += fy * 0.02 + 0.01

            speed = np.sqrt(game_charge_vel[0]**2 + game_charge_vel[1]**2)
            max_speed = 5.0
            if speed > max_speed:
                scale = max_speed / speed
                game_charge_vel[0] *= scale
                game_charge_vel[1] *= scale

            game_charge_vel[0] *= 0.98
            game_charge_vel[1] *= 0.98

            new_pos = [game_charge_pos[0] + game_charge_vel[0], game_charge_pos[1] + game_charge_vel[1]]

            for wall in walls:
                wx, wy, ww, wh = wall
                if wx <= new_pos[0] <= wx + ww and wy <= new_pos[1] <= wy + wh:
                    old_x, old_y = game_charge_pos
                    if old_x < wx and new_pos[0] >= wx:
                        new_pos[0] = wx - 1
                        game_charge_vel[0] = -game_charge_vel[0] * 0.5
                    elif old_x > wx + ww and new_pos[0] <= wx + ww:
                        new_pos[0] = wx + ww + 1
                        game_charge_vel[0] = -game_charge_vel[0] * 0.5
                    if old_y < wy and new_pos[1] >= wy:
                        new_pos[1] = wy - 1
                        game_charge_vel[1] = -game_charge_vel[1] * 0.5
                    elif old_y > wy + wh and new_pos[1] <= wy + wh:
                        new_pos[1] = wy + wh + 1
                        game_charge_vel[1] = -game_charge_vel[1] * 0.5
                    break

            new_pos[0] = max(0, min(new_pos[0], WIDTH))
            new_pos[1] = max(0, min(new_pos[1], HEIGHT))
            game_charge_pos = new_pos

            if (game_charge_pos[0] - win_zone[0])**2 + (game_charge_pos[1] - win_zone[1])**2 < 100:
                if selected_level == progress["unlocked"] and selected_level < 30:
                    progress["unlocked"] += 1
                    save_game_progress(progress)
                state = "level_select"

        if state == "title":
            draw_title_screen(screen)
        elif state == "menu":
            draw_menu_screen(screen)
        elif state == "level_select":
            draw_level_select_screen(screen, progress["unlocked"])
        elif state == "free_play":
            field = compute_field_grid(placed_charges, placed_charge_vals, loops, WIDTH, HEIGHT)
            for y in range(0, HEIGHT, GRID_SIZE):
                for x in range(0, WIDTH, GRID_SIZE):
                    fx, fy = field[y//GRID_SIZE][x//GRID_SIZE]
                    pygame.draw.line(screen, (0, 255, 255), (x, y), (x + fx * 2, y + fy * 2), 1)
            for c, v in zip(placed_charges, placed_charge_vals):
                color = (255, 255, 0) if v > 0 else (255, 0, 0)
                pygame.draw.circle(screen, color, c, 5)
            for l in loops:
                pygame.draw.circle(screen, (0, 0, 255), l, 5)
        elif state == "play_level":
            time_elapsed = (pygame.time.get_ticks() - level_start_time) // 1000

            for wall in walls:
                pygame.draw.rect(screen, (100, 100, 100), wall)

            color = (255, 0, 0) if game_charge_val > 0 else (0, 0, 255)
            pygame.draw.circle(screen, color, (int(game_charge_pos[0]), int(game_charge_pos[1])), 10)
            print(f"Drawing game charge at {game_charge_pos}")

            for c, v in zip(placed_charges, placed_charge_vals):
                color = (255, 255, 0) if v > 0 else (255, 0, 0)
                pygame.draw.circle(screen, color, c, 5)

            pygame.draw.circle(screen, (0, 255, 0), win_zone, 10)

            draw_game_ui(screen, selected_level, time_elapsed, paused, game_charge_val, status_message)

            if paused:
                draw_pause_menu(screen)

        pygame.display.flip()
        clock.tick(FPS)
        await asyncio.sleep(1.0 / FPS)

if platform.system() == "Emscripten":
    asyncio.ensure_future(run_game(pygame.display.get_surface()))
else:
    if __name__ == "__main__":
        asyncio.run(run_game(pygame.display.get_surface()))