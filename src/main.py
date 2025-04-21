import pygame
import asyncio
from game import run_game

pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Electromagnetism Maze Game")

def main():
    asyncio.run(run_game(screen))

if __name__ == "__main__":
    main()