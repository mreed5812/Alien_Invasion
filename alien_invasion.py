import sys
from time import sleep

import pygame

from settings import Settings
from game_stats import GameStats
from button import Button
from ship import Ship
from bullet import Bullet
from alien import Alien

class AlienInvasion:
    """Class to manage game assets and behavior."""

    def __init__(self):
        """Initialize the game and create game resources"""
        pygame.init()
        self.settings = Settings()
        self.screen = pygame.display.set_mode((self.settings.screen_width, self.settings.screen_height))
        pygame.display.set_caption("Alien Invasion") 

        self.stats = GameStats(self)
        self.ship = Ship(self)
        self.bullets = pygame.sprite.Group()
        self.aliens = pygame.sprite.Group()
        self._create_fleet()
        self.god_mode = False

        #Make the Play button
        self.play_button = Button(self, "Play")


    def run_game(self):
        while True:
            self._check_events()

            if self.stats.game_active:
                if self.god_mode:
                    self.ship.update()
                    self._update_bullets()
                    self._update_aliens()
                    self.settings.bullets_allowed = 100
                    self.settings.bullet_speed = 10
                    self.settings.bullet_height = 50
                else:
                    self.ship.update()
                    self._update_bullets()
                    self._update_aliens()
            
            self._update_screen()
         
    def _check_events(self):
        #Respond to keypresses and mouse events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                self._check_play_button(mouse_pos)
            elif event.type == pygame.KEYDOWN:
                self._check_keydown_events(event)   
            elif event.type == pygame.KEYUP:
                self._check_keyup_events(event)
    
    def _check_play_button(self, mouse_pos):
        #start game when play button is clicked
        if self.play_button.rect.collidepoint(mouse_pos):
            #reset game stats
            self.stats.reset_stats()
            self.stats.game_active = True

            self.aliens.empty()
            self.bullets.empty()

            #create new fleet and center ship
            self._create_fleet()
            self.ship.center_ship()
                    
    def _check_keydown_events(self,event):
        #Respond to key presses
        if event.key == pygame.K_RIGHT:
            #Move the ship to the right
            self.ship.moving_right = True
        elif event.key == pygame.K_LEFT:
            #Move the ship to the left
            self.ship.moving_left = True
        elif event.key == pygame.K_UP:
            #Move ship up
            self.ship.moving_up = True
        elif event.key == pygame.K_DOWN:
            #Move ship down
            self.ship.moving_down = True
        elif event.key == pygame.K_SPACE:
            #Shoot bullets
            self._fire_bullet()
        elif event.key == pygame.K_g:
            #Enable God Mode
            self.god_mode = True
        elif event.key == pygame.K_q:
            sys.exit()
        
    def _check_keyup_events(self, event):
        #Respond to key releases
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = False  
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = False
        elif event.key == pygame.K_UP:
            self.ship.moving_up = False
        elif event.key == pygame.K_DOWN:
            self.ship.moving_down = False

    def _fire_bullet(self):
        #Create a new bullet and add it to the bullets group
        if len(self.bullets) < self.settings.bullets_allowed:
            new_bullet = Bullet(self)
            self.bullets.add(new_bullet)

    def _create_fleet(self):
        #Create fleet of aliens
        #Create an alien and find the number of aliens that can fit in a row
        #Spacing between each alien is equal to one alien width
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size
        available_space_x = self.settings.screen_width - (2 * alien_width)
        number_aliens_x = available_space_x // (2 * alien_width)

        #Determine the number of rows of aliens that fit on the screen
        ship_height = self.ship.rect.height
        available_space_y = (self.settings.screen_height - (3 * alien_height) - ship_height)
        number_rows = available_space_y // (2 * alien_height)

        #Create full fleet of aliens
        for row_number in range(number_rows):
            for alien_number in range(number_aliens_x):
                self._create_alien(alien_number,row_number)

    def _create_alien(self, alien_number, row_number):
        #Create an alien and place it in the row
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size
        alien.x = alien_width + 2 * alien_width * alien_number
        alien.rect.x = alien.x
        alien.rect.y = alien.rect.height + 2 * alien.rect.height * row_number
        self.aliens.add(alien)
        

    def _update_bullets(self):
        #Update position of bullets and get rid of old bullets
        self.bullets.update()

        #Get rid of bullets that have disappeared
        for bullet in self.bullets.copy():
            if bullet.rect.bottom <= 0:
                self.bullets.remove(bullet)
        
        self._check_bullet_alien_collisions()

    def _check_bullet_alien_collisions(self):
        """Respond to bullet-alien collisions"""
        #  Remove any bullets and aliens that have collided
        #collisions = pygame.sprite.groupcollide(self.bullets, self.aliens, True, True)
        if self.god_mode:
            pygame.sprite.groupcollide(self.bullets, self.aliens, False, True)
        else:
            pygame.sprite.groupcollide(self.bullets, self.aliens, True, True)
        if not self.aliens:
            #Destory existing bullets and create new fleet.
            self.bullets.empty()
            self._create_fleet()

    def _check_aliens_bottom(self):
        #Check whether an alien has reached the bottom of the screen
        screen_rect = self.screen.get_rect()
        for alien in self.aliens.sprites():
            if alien.rect.bottom >= screen_rect.bottom:
                self._ship_hit()
                break

    def _update_aliens(self):
        #Check if fleet is at an edge then update positions of all aliens in fleet
        self._check_fleet_edges()
        self.aliens.update()

        #look for alien ship collisions
        if pygame.sprite.spritecollideany(self.ship, self.aliens):
            #print("Ship hit!")
            self._ship_hit()
        
        self._check_aliens_bottom()
    
    def _ship_hit(self):
        #respond to ship being hit 
        if self.stats.ships_left > 0:
            self.stats.ships_left -= 1
            #get rid of any remaining aliens and bullets
            self.aliens.empty()
            self.bullets.empty()

            #create a new fleet and center the ship
            self._create_fleet()
            self.ship.center_ship()

            sleep(0.5)
        else:
            self.stats.game_active = False


    def _check_fleet_edges(self):
        #Respond to aliens reaching the edge of screen
        for alien in self.aliens.sprites():
            if alien.check_edges():
                self._change_fleet_direction()
                break
    
    def _change_fleet_direction(self):
        #Drop the entire fleet and change fleet's direction
        for alien in self.aliens.sprites():
            alien.rect.y += self.settings.fleet_drop_speed
        self.settings.fleet_direction *= -1
   
    def _update_screen(self):
        #Redraw the screen during each pass through the loop
        self.screen.fill(self.settings.bg_color)
        self.ship.blitme()
        for bullet in self.bullets.sprites():
            bullet.draw_bullet()
        self.aliens.draw(self.screen)

        #Draw button if game is inactive
        if not self.stats.game_active:
            self.play_button.draw_button()

        #Make most recently drawn screen visible
        pygame.display.flip()
    
if __name__ == '__main__':
    ai = AlienInvasion()
    ai.run_game()