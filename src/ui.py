import pygame

def draw_title_screen(screen):
    font = pygame.font.SysFont("Arial", 48)
    title = font.render("Electromagnetism Puzzle Game", True, (255, 255, 255))
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
