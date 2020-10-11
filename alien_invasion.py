import sys
import pygame

from settings import Settings
from ship import Ship

class AlienInvasion:
    """Class to manage game assets and behavior."""

    def __init__(self):
        """Initialize the game and create game resources"""
        pygame.init()
        self.settings = Settings()

        self.screen = pygame.display.set_mode((self.settings.screen_width, self.settings.screen_height))
        pygame.display.set_caption("Alien Invasion") 

        self.ship = Ship(self)


    def run_game(self):
        while True:
            self._check_events()
            self._update_screen()
  
            
    def _check_events(self):
        #Respond to keypresses and mouse events
        for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()

    def _update_screen(self):
        #Redraw the screen during each pass through the loop
        self.screen.fill(self.settings.bg_color)
        self.ship.blitme()

        #Make most recently drawn screen visible
        pygame.display.flip()
    

if __name__ == '__main__':
    ai = AlienInvasion()
    ai.run_game()