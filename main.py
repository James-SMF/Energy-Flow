import pygame
from game import Game

if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((8*70, 8*70+40*2))
    pygame.display.set_caption("Energy Grid")

    game = Game(screen)
    game.run()
    pygame.quit()
