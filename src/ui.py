import pygame

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

def draw_level_select_screen(screen, unlocked):
    font = pygame.font.SysFont("Arial", 24)
    for i in range(30):
        x = 100 + (i % 8) * 80
        y = 100 + (i // 8) * 60
        label = f"L{i+1}"
        color = (255, 255, 255) if i < unlocked else (100, 100, 100)
        pygame.draw.rect(screen, (50, 50, 50), (x, y, 60, 40))
        text = font.render(label, True, color)
        screen.blit(text, (x + 10, y + 10))

def draw_game_ui(screen, level, time_sec, paused, game_charge_val, status_message):
    font = pygame.font.SysFont("Arial", 28)
    if level:
        time_text = font.render(f"Level {level}  |  Time: {time_sec}s", True, (255, 255, 255))
        charge_type = "Positive" if game_charge_val > 0 else "Negative"
        instructions = font.render(f"Left: +Charge, Right: -Charge, C: Remove | Target: {charge_type}", True, (255, 255, 255))
        status = font.render(status_message, True, (255, 100, 100)) if status_message else None
        screen.blit(time_text, (10, 10))
        screen.blit(instructions, (10, 40))
        if status:
            screen.blit(status, (10, 70))
        if paused:
            pause = pygame.font.SysFont("Arial", 32).render("PAUSED", True, (255, 100, 100))
            screen.blit(pause, (WIDTH//2 - 60, 40))
    else:
        instructions = font.render("Left: +Charge, Right: -Charge, L: Loop", True, (255, 255, 255))
        screen.blit(instructions, (10, 10))

def draw_pause_menu(screen):
    font = pygame.font.SysFont("Arial", 28)
    msg1 = font.render("Press R to restart level", True, (255, 255, 255))
    msg2 = font.render("Press B to go back to level select", True, (255, 255, 255))
    screen.blit(msg1, (200, 300))
    screen.blit(msg2, (200, 340))