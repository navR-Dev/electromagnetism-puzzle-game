import pygame
import concurrent.futures
import os

WIDTH = 800
HEIGHT = 600

def draw_title_screen(screen):
    font = pygame.font.SysFont("Arial", 48)
    title = font.render("Electromagnetism Maze Game", True, (255, 255, 255))
    prompt = pygame.font.SysFont("Arial", 24).render("Press any key to continue...", True, (180, 180, 180))
    screen.blit(title, (100, 200))
    screen.blit(prompt, (230, 300))

def draw_menu_screen(screen):
    font = pygame.font.SysFont("Arial", 36)
    level_button = font.render("Level Mode", True, (255, 255, 255))
    free_play_button = font.render("Free Play", True, (255, 255, 255))
    pygame.draw.rect(screen, (70, 70, 70), (300, 250, 200, 50))
    pygame.draw.rect(screen, (70, 70, 70), (300, 350, 200, 50))
    screen.blit(level_button, (320, 255))
    screen.blit(free_play_button, (320, 355))

def render_level_button(i, unlocked):
    # Create a new font instance for thread safety
    font = pygame.font.SysFont("Arial", 24)
    label = f"L{i+1}"
    color = (255, 255, 255) if i < unlocked else (100, 100, 100)
    text = font.render(label, True, color)
    x = 100 + (i % 8) * 80
    y = 100 + (i // 8) * 60
    return i, text, x, y

def draw_level_select_screen(screen, unlocked):
    # Parallelize text rendering
    max_workers = min(30, os.cpu_count() or 4)
    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(render_level_button, i, unlocked) for i in range(30)]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]
    except Exception:
        # Fallback to sequential rendering if parallel fails (e.g., Emscripten)
        results = [render_level_button(i, unlocked) for i in range(30)]

    # Sort results by index to maintain order
    results.sort(key=lambda x: x[0])

    # Draw rectangles and blit text surfaces sequentially
    for _, text, x, y in results:
        pygame.draw.rect(screen, (50, 50, 50), (x, y, 60, 40))
        screen.blit(text, (x + 10, y + 10))

def draw_game_ui(screen, level, time_sec, paused, game_charge_val, status_message):
    font = pygame.font.SysFont("Arial", 28)
    if level:
        time_text = font.render(f"Level {level}  |  Time: {time_sec}s", True, (255, 255, 255))
        menu_prompt = font.render("M: Pause", True, (180, 180, 180))
        status = font.render(status_message, True, (255, 100, 100)) if status_message else None
        screen.blit(time_text, (10, 10))
        screen.blit(menu_prompt, (10, 70))
        if status:
            screen.blit(status, (10, 100))
        if paused:
            pause = pygame.font.SysFont("Arial", 32).render("PAUSED", True, (255, 100, 100))
            screen.blit(pause, (WIDTH//2 - 60, 40))
    else:
        instructions = font.render("Left: +Charge, Right: -Charge, L: Loop", True, (255, 255, 255))
        menu_prompt = font.render("M: Pause", True, (180, 180, 180))
        status = font.render(status_message, True, (255, 100, 100)) if status_message else None
        screen.blit(instructions, (10, 10))
        screen.blit(menu_prompt, (10, 40))
        if status:
            screen.blit(status, (10, 70))

def draw_pause_menu(screen, level):
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))  # semi-transparent black overlay
    screen.blit(overlay, (0, 0))

    font = pygame.font.SysFont("Arial", 32, bold=True)
    button_font = pygame.font.SysFont("Arial", 28)
    control_font = pygame.font.SysFont("Arial", 24)

    # Draw pause box
    box_rect = pygame.Rect(WIDTH // 2 - 150, HEIGHT // 2 - 200, 300, 400)
    pygame.draw.rect(screen, (50, 50, 50), box_rect, border_radius=15)
    pygame.draw.rect(screen, (255, 255, 255), box_rect, 4, border_radius=15)

    # Pause title
    title_text = font.render("Game Paused", True, (255, 255, 255))
    screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, box_rect.top + 20))

    # Controls (different for level and free play)
    if level:
        controls_text = control_font.render("Left: +Charge, Right: -Charge, N: Magnet, C: Remove", True, (200, 200, 200))
        screen.blit(controls_text, (WIDTH // 2 - controls_text.get_width() // 2, box_rect.top + 60))
    else:
        controls_text = control_font.render("Left: +Charge, Right: -Charge, L: Loop", True, (200, 200, 200))
        screen.blit(controls_text, (WIDTH // 2 - controls_text.get_width() // 2, box_rect.top + 60))

    # Buttons
    buttons = [
        ("Resume (M)", HEIGHT // 2 - 60),
        ("Restart (R)" if level else "Reset (R)", HEIGHT // 2 - 10),
        ("Back to Menu (B)", HEIGHT // 2 + 40),
        ("Quit (Q)", HEIGHT // 2 + 90),
    ]

    for label, y in buttons:
        button_rect = pygame.Rect(WIDTH // 2 - 110, y, 220, 40)
        pygame.draw.rect(screen, (100, 100, 100), button_rect, border_radius=10)
        pygame.draw.rect(screen, (255, 255, 255), button_rect, 2, border_radius=10)

        text = button_font.render(label, True, (255, 255, 255))
        screen.blit(text, (button_rect.centerx - text.get_width() // 2, button_rect.centery - text.get_height() // 2))

def draw_menu_prompt(screen):
    font = pygame.font.SysFont("Arial", 24)
    prompt = font.render("Press M for Menu", True, (180, 180, 180))
    screen.blit(prompt, (10, HEIGHT - 40))