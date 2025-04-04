#!/usr/bin/env python

import pygame
import sys

# Initialize Pygame
pygame.init()


def is_white_path(surface, x, y):
    # Check if the position is within bounds
    if 0 <= x < WINDOW_WIDTH and 0 <= y < WINDOW_HEIGHT:
        # Get color at position
        color = surface.get_at((int(x), int(y)))
        # Consider a pixel "white-ish" if all RGB values are above 200
        return all(c > 200 for c in color[:3])
    return False


# Constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
PLAYER_SIZE = 15
PLAYER_SPEED = 7  # Adjusted so 7 steps up reaches hallway intersection
STEP_COOLDOWN = 150  # milliseconds between steps

# Maps
FLOOR_1_MAP = 'attached_assets/floor_1.png'
FLOOR_2_MAP = 'attached_assets/floor_2.png'

# Colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
SHADOW_COLOR = (255, 100, 100)

# Set up display
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("School Map Navigation")

# Load and scale the map images
current_floor = 1
map_images = {
    1:
    pygame.transform.scale(pygame.image.load(FLOOR_1_MAP),
                           (WINDOW_WIDTH, WINDOW_HEIGHT)),
    2:
    pygame.transform.scale(pygame.image.load(FLOOR_2_MAP),
                           (WINDOW_WIDTH, WINDOW_HEIGHT))
}
map_image = map_images[current_floor]


def is_on_stairs(x, y):
    # Define stair regions for kitchen and resource room 2
    stair_regions = [
        pygame.Rect(514, 418, 50, 100),  # Stairs near kitchen
        pygame.Rect(136, 388, -50, 100),  # Stairs near resource room 2
        pygame.Rect(620, 105, 100, 50),  # Stairs near 
        pygame.Rect(125, 82, 50, 100),  # Stairs near 
    ]
    player_rect = pygame.Rect(x, y, PLAYER_SIZE, PLAYER_SIZE)
    return any(player_rect.colliderect(stair) for stair in stair_regions)


# Player class
class Player:

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.rect = pygame.Rect(x, y, PLAYER_SIZE, PLAYER_SIZE)
        self.trail = []
        self.last_key_press = {'up': 0, 'down': 0, 'left': 0, 'right': 0}
        self.double_press_window = 200  # milliseconds
        self.last_step_time = 0

    def move(self, dx, dy):
        if dx != 0 or dy != 0:
            self.trail.append((self.x, self.y))

        new_x = self.x + dx
        new_y = self.y + dy

        # Check if new position is on a white path or double pressed
        if (0 <= new_x <= WINDOW_WIDTH - PLAYER_SIZE
                and 0 <= new_y <= WINDOW_HEIGHT - PLAYER_SIZE):
            # Check corners of the player sprite
            corners = [(new_x, new_y), (new_x + PLAYER_SIZE, new_y),
                       (new_x, new_y + PLAYER_SIZE),
                       (new_x + PLAYER_SIZE, new_y + PLAYER_SIZE)]

            can_pass = all(is_white_path(map_image, x, y)
                           for x, y in corners) or self.check_double_press(
                               dx, dy)

            if can_pass:
                self.x = new_x
                self.y = new_y

                # Check if player is on stairs and switch floors
                global current_floor, map_image
                if is_on_stairs(self.x, self.y) and current_floor == 1:
                    current_floor = 2
                    map_image = map_images[current_floor]
                    self.trail = []  # Clear the trail when switching floors

        self.rect.x = self.x
        self.rect.y = self.y

    def check_double_press(self, dx, dy):
        import time
        current_time = int(round(time.time() * 1000))

        key_pressed = None
        if dx > 0: key_pressed = 'right'
        elif dx < 0: key_pressed = 'left'
        elif dy > 0: key_pressed = 'down'
        elif dy < 0: key_pressed = 'up'

        if key_pressed and current_time - self.last_key_press[
                key_pressed] < self.double_press_window:
            self.last_key_press[key_pressed] = 0  #reset timer
            return True

        if key_pressed:
            self.last_key_press[key_pressed] = current_time
        return False

    def draw(self, surface):
        # Draw permanent trail
        for trail_x, trail_y in self.trail:
            trail_rect = pygame.Rect(trail_x, trail_y, PLAYER_SIZE,
                                     PLAYER_SIZE)
            pygame.draw.rect(surface, SHADOW_COLOR, trail_rect)

        # Draw player
        pygame.draw.rect(surface, RED, self.rect)


# Create player (positioned above the vest on the white path)
player = Player(WINDOW_WIDTH * 0.617, WINDOW_HEIGHT - 105)

# Game loop
running = True
clock = pygame.time.Clock()

while running:
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Handle player movement
    current_time = pygame.time.get_ticks()
    if current_time - player.last_step_time >= STEP_COOLDOWN:
        keys = pygame.key.get_pressed()
        dx = (keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]) * PLAYER_SPEED
        dy = (keys[pygame.K_DOWN] - keys[pygame.K_UP]) * PLAYER_SPEED
        if dx != 0 or dy != 0:
            player.move(dx, dy)
            player.last_step_time = current_time

    # Draw everything
    screen.blit(map_image, (0, 0))

    player.draw(screen)

    # Display coordinates
    font = pygame.font.Font(None, 24)
    coords_text = f"{int(player.x)},{int(player.y)}"
    text_surface = font.render(coords_text, True, (0, 0, 0))
    text_rect = text_surface.get_rect()
    text_rect.topright = (WINDOW_WIDTH - 5, 5)
    screen.blit(text_surface, text_rect)

    # Draw START text only on first floor
    if current_floor == 1:
        font = pygame.font.Font(None, 14)
        start_text = font.render("START", True, (0, 0, 0))
        text_rect = start_text.get_rect()
        text_rect.midtop = (WINDOW_WIDTH * 0.6295, WINDOW_HEIGHT - 82)
        screen.blit(start_text, text_rect)

    # Draw FINISH text only on first floor
    if current_floor == 2:
        font = pygame.font.Font(None, 14)
        start_text = font.render("FINISH", True, (0, 0, 0))
        text_rect = start_text.get_rect()
        text_rect.midtop = (317, 483)
        screen.blit(start_text, text_rect)

    # Update display
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
