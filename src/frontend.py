"""
Frontend for G_Sim:

Use Case Outline:
    - User starts application
    - User is presented with WELCOME SCREEN allowing for selection from
        1. Already EXISTING SIMULATIONS
        2. Creating a NEW SIMULATIONS
            - Allows user to create an object (option to make ghost particles not offered)
            - When parameters have been selected, present LOADING screen that updates a bar as the calculations are completed
    - Allow user to play and pause the simulation
"""
import backend as b_end
import pygame
import sys
import os
import utils

print(os.getcwd())
pygame.init()


window_size = width, height = 800, 600
screen = pygame.display.set_mode(window_size)


###########COLOURS###########
#       (RRR, GGG, BBB)
BLACK = (000, 000, 000)
BLUE  = (000, 000, 255)
#############################

FPS = 240

def welcome_screen():
    pass


def main_screen():
    pass


def main():
    CLOCK = pygame.time.Clock()
    # new_screen = pygame.display.set_mode((900, 300))
    new_screen.fill(BLUE)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: sys.exit()
        pass

        
        
        screen.fill(BLACK)
        pygame.display.flip()
        CLOCK.tick(FPS)
        


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        pass