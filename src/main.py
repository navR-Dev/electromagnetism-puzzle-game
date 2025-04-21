import pygame
from game import run_game

pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Electromagnetism Puzzle Game")

def main():
    run_game(screen)

if __name__ == "__main__":
    main()
