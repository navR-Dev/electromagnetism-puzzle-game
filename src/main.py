import pygame
from ui import draw_title_screen, draw_menu_screen
from game import run_game

pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Electromagnetism Puzzle Game")

def main():
    clock = pygame.time.Clock()
    state = "TITLE"

    while True:
        screen.fill((0, 0, 0))

        if state == "TITLE":
            draw_title_screen(screen)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                elif event.type == pygame.KEYDOWN:
                    state = "MENU"

        elif state == "MENU":
            draw_menu_screen(screen)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    x, y = event.pos
                    if 300 <= x <= 500:
                        if 250 <= y <= 300:
                            state = "LEVEL_MODE"
                        elif 350 <= y <= 400:
                            state = "GAME"

        elif state == "LEVEL_MODE":
            font = pygame.font.SysFont("Arial", 36)
            text = font.render("Level mode not implemented.", True, (255, 255, 255))
            screen.blit(text, (200, 280))
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                elif event.type == pygame.KEYDOWN:
                    state = "MENU"

        elif state == "GAME":
            run_game(screen)
            state = "MENU"

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()
