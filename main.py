# main.py
# This is the main script to run the Pygame-based Snake Game.
# It initializes Pygame and creates an instance of the Game class.

import pygame
import random
import time
import math # For sine wave or other mathematical effects

# --- CrtStyle Class ---
# This class defines a single CRT theme with all its visual parameters.
class CrtStyle:
    def __init__(self, scanline_alpha, ghosting_alpha, snake_head_color,
                 snake_body_color, background_color, scanline_color,
                 grid_color, bezel_color, border_color, inner_glow_color,
                 font_color, food_color, food_glow_color, game_over_color,
                 font_name, font_size, restart_text_color,
                 pixel_noise_density, pixel_noise_alpha, horizontal_banding_alpha,
                 horizontal_banding_thickness):
        self.scanline_alpha = scanline_alpha
        self.ghosting_alpha = ghosting_alpha
        self.snake_head_color = snake_head_color
        self.snake_body_color = snake_body_color
        self.background_color = background_color
        self.scanline_color = scanline_color
        self.grid_color = grid_color
        self.bezel_color = bezel_color
        self.border_color = border_color
        self.inner_glow_color = inner_glow_color
        self.font_color = font_color
        self.food_color = food_color
        self.food_glow_color = food_glow_color
        self.game_over_color = game_over_color
        
        # Load font. Pygame's font loading is slightly different.
        # We assume 'Courier New' is available, fallback to default if not.
        try:
            self.crt_font = pygame.font.SysFont(font_name, font_size, bold=True)
        except:
            self.crt_font = pygame.font.Font(None, font_size) # Fallback to default pygame font

        self.restart_text_color = restart_text_color

        # Artifact specific properties
        self.pixel_noise_density = pixel_noise_density
        self.pixel_noise_alpha = pixel_noise_alpha
        self.horizontal_banding_alpha = horizontal_banding_alpha
        self.horizontal_banding_thickness = horizontal_banding_thickness

# --- Game Class (Equivalent to GamePanel.java) ---
# This class manages the game logic, rendering, and CRT effects using Pygame.
class SnakeGamePygame:
    # --- Game Constants ---
    SCREEN_WIDTH = 800
    SCREEN_HEIGHT = 600
    UNIT_SIZE = 20
    DELAY_MS = 100 # Delay in milliseconds for game updates
    BORDER_SIZE = 20 # Thickness of the non-playable CRT border
    STYLE_CHANGE_SCORE_INTERVAL = 5 # Score interval to change CRT style

    def __init__(self):
        pygame.init() # Initialize Pygame modules
        pygame.font.init() # Initialize font module

        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        pygame.display.set_caption("Retro Snake Game")
        self.clock = pygame.time.Clock() # To control game frame rate

        self.random = random.Random() # Initialize random number generator

        # --- Game State Variables ---
        self.snake = []
        self.food = None
        self.direction = 'R' # 'U', 'D', 'L', 'R'
        self.running = False
        self.score = 0
        self.high_score = 0
        self.game_start_time = 0

        # For ghosting effect - we'll keep a history of previous frames
        self.ghosting_frames = []
        self.max_ghosting_frames = 5  # Number of frames to keep for ghosting

        # --- Dynamic CRT Styles ---
        self.crt_styles = []
        self._initialize_crt_styles()
        self.current_style_index = 0
        self.current_style = self.crt_styles[self.current_style_index]

        self.start_game()

    def _initialize_crt_styles(self):
        # Define and initialize all the different CRT styles.
        # Note: Pygame uses RGB tuples for colors, not java.awt.Color objects.
        # Alpha values are handled by set_alpha() on surfaces or passed as 4th element in tuple (RGBA)
        
        # Style 1: Green Monochrome (Classic Radio/Terminal)
        self.crt_styles.append(CrtStyle(
            scanline_alpha=50,  # Now using values 0-255 for better control
            ghosting_alpha=20,
            snake_head_color=(0, 255, 0),
            snake_body_color=(0, 180, 0),
            background_color=(8, 12, 8),
            scanline_color=(0, 0, 0),
            grid_color=(0, 40, 0),
            bezel_color=(20, 20, 20),
            border_color=(60, 60, 60),
            inner_glow_color=(0, 100, 0),
            font_color=(0, 255, 0),
            food_color=(255, 50, 50),
            food_glow_color=(255, 100, 100),
            game_over_color=(255, 0, 0),
            font_name="Courier New",
            font_size=16,
            restart_text_color=(255, 255, 0),
            pixel_noise_density=0.0, pixel_noise_alpha=0.0,
            horizontal_banding_alpha=0.0, horizontal_banding_thickness=0
        ))

        # Style 2: Amber Monochrome (IBM PC CGA/MDA aesthetic)
        self.crt_styles.append(CrtStyle(
            scanline_alpha=40,
            ghosting_alpha=30,
            snake_head_color=(255, 200, 0),
            snake_body_color=(180, 120, 0),
            background_color=(20, 10, 0),
            scanline_color=(0, 0, 0),
            grid_color=(50, 20, 0),
            bezel_color=(30, 20, 10),
            border_color=(80, 50, 20),
            inner_glow_color=(200, 100, 0),
            font_color=(255, 200, 0),
            food_color=(255, 255, 0),
            food_glow_color=(255, 255, 100),
            game_over_color=(255, 80, 0),
            font_name="Courier New",
            font_size=16,
            restart_text_color=(255, 220, 0),
            pixel_noise_density=0.0, pixel_noise_alpha=0.0,
            horizontal_banding_alpha=50, horizontal_banding_thickness=2
        ))

        # Style 3: Blue Monochrome (Commodore 64 / Apple IIc aesthetic)
        self.crt_styles.append(CrtStyle(
            scanline_alpha=80,
            ghosting_alpha=15,
            snake_head_color=(100, 100, 255),
            snake_body_color=(50, 50, 180),
            background_color=(0, 0, 50),
            scanline_color=(0, 0, 0),
            grid_color=(0, 0, 100),
            bezel_color=(10, 10, 30),
            border_color=(40, 40, 90),
            inner_glow_color=(0, 0, 200),
            font_color=(100, 100, 255),
            food_color=(255, 0, 255),
            food_glow_color=(255, 100, 255),
            game_over_color=(255, 50, 50),
            font_name="Courier New",
            font_size=16,
            restart_text_color=(200, 200, 255),
            pixel_noise_density=0.005, pixel_noise_alpha=50,
            horizontal_banding_alpha=0.0, horizontal_banding_thickness=0
        ))

    def start_game(self):
        # Reset game variables to initial state
        self.snake = []
        # Initial snake position centered in the playable area
        start_x = (self.SCREEN_WIDTH // 2)
        start_y = (self.SCREEN_HEIGHT // 2)
        start_x = ((start_x - self.BORDER_SIZE) // self.UNIT_SIZE) * self.UNIT_SIZE + self.BORDER_SIZE
        start_y = ((start_y - self.BORDER_SIZE) // self.UNIT_SIZE) * self.UNIT_SIZE + self.BORDER_SIZE

        self.snake.append(pygame.Rect(start_x, start_y, self.UNIT_SIZE, self.UNIT_SIZE))
        self.snake.append(pygame.Rect(start_x - self.UNIT_SIZE, start_y, self.UNIT_SIZE, self.UNIT_SIZE))
        self.snake.append(pygame.Rect(start_x - self.UNIT_SIZE * 2, start_y, self.UNIT_SIZE, self.UNIT_SIZE))

        self.direction = 'R'
        self.score = 0
        self.current_style_index = 0 # Reset style to the first one
        self.current_style = self.crt_styles[self.current_style_index]
        self.new_food()
        self.running = True
        self.game_start_time = time.time()
        self.ghosting_frames = []  # Clear ghosting frames

        # Set up a custom event for game updates (equivalent to Java's Timer)
        self.GAME_UPDATE = pygame.USEREVENT + 1
        pygame.time.set_timer(self.GAME_UPDATE, self.DELAY_MS)

    def new_food(self):
        # Generate new food coordinates within the playable area
        min_x = self.BORDER_SIZE // self.UNIT_SIZE
        max_x = (self.SCREEN_WIDTH - self.BORDER_SIZE - self.UNIT_SIZE) // self.UNIT_SIZE
        min_y = self.BORDER_SIZE // self.UNIT_SIZE
        max_y = (self.SCREEN_HEIGHT - self.BORDER_SIZE - self.UNIT_SIZE) // self.UNIT_SIZE

        while True:
            food_x = self.random.randint(min_x, max_x) * self.UNIT_SIZE
            food_y = self.random.randint(min_y, max_y) * self.UNIT_SIZE
            self.food = pygame.Rect(food_x, food_y, self.UNIT_SIZE, self.UNIT_SIZE)
            
            # Ensure food doesn't spawn on the snake
            if not any(segment.colliderect(self.food) for segment in self.snake):
                break

    def move(self):
        head = self.snake[0]
        
        # Create a new head position based on current direction
        if self.direction == 'U':
            new_head_pos = head.move(0, -self.UNIT_SIZE)
        elif self.direction == 'D':
            new_head_pos = head.move(0, self.UNIT_SIZE)
        elif self.direction == 'L':
            new_head_pos = head.move(-self.UNIT_SIZE, 0)
        elif self.direction == 'R':
            new_head_pos = head.move(self.UNIT_SIZE, 0)
        else:
            new_head_pos = head # Should not happen

        self.snake.insert(0, new_head_pos) # Add new head

        # Remove tail unless food was just eaten
        if not new_head_pos.colliderect(self.food):
            self.snake.pop()

    def check_food(self):
        if self.snake[0].colliderect(self.food):
            self.score += 1
            self.high_score = max(self.high_score, self.score)

            # Check if it's time to change the CRT style
            if self.score > 0 and self.score % self.STYLE_CHANGE_SCORE_INTERVAL == 0:
                self.current_style_index = (self.current_style_index + 1) % len(self.crt_styles)
                self.current_style = self.crt_styles[self.current_style_index]

            self.new_food()

    def check_collisions(self):
        head = self.snake[0]

        # Wall collisions (within the playable border)
        if (head.left < self.BORDER_SIZE or
            head.right > self.SCREEN_WIDTH - self.BORDER_SIZE or
            head.top < self.BORDER_SIZE or
            head.bottom > self.SCREEN_HEIGHT - self.BORDER_SIZE):
            self.running = False

        # Self-collision
        for segment in self.snake[1:]: # Check head against all body segments
            if head.colliderect(segment):
                self.running = False
                break
        
        if not self.running:
            pygame.time.set_timer(self.GAME_UPDATE, 0) # Stop the game update timer

    def draw(self):
        # Create a temporary surface for this frame
        frame_surface = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        frame_surface.fill(self.current_style.background_color)

        # Draw background artifacts
        self._draw_background_artifacts(frame_surface)

        if self.running:
            self._draw_grid(frame_surface)
            self._draw_food(frame_surface)
            self._draw_snake(frame_surface)
            self._draw_score_and_info(frame_surface)
        else:
            self._draw_game_over(frame_surface)

        # Add this frame to our ghosting frames
        self.ghosting_frames.append(frame_surface.copy())
        if len(self.ghosting_frames) > self.max_ghosting_frames:
            self.ghosting_frames.pop(0)

        # Clear the screen
        self.screen.fill((0, 0, 0))

        # Draw all ghosting frames with decreasing alpha
        for i, ghost_frame in enumerate(self.ghosting_frames):
            alpha = self.current_style.ghosting_alpha * (1 - (i / len(self.ghosting_frames)))
            ghost_frame.set_alpha(alpha)
            self.screen.blit(ghost_frame, (0, 0))

        # Draw the current frame on top
        self.screen.blit(frame_surface, (0, 0))

        # Apply scanlines to the final composition
        self._draw_scanlines()

        # Draw the CRT border last
        self._draw_screen_border()

        pygame.display.flip() # Update the full display Surface to the screen

    def _draw_background_artifacts(self, surface):
        # --- Horizontal Banding (for IBM style) ---
        if self.current_style.horizontal_banding_alpha > 0 and self.current_style.horizontal_banding_thickness > 0:
            band_color = (*self.current_style.font_color[:3], min(255, self.current_style.horizontal_banding_alpha))
            band_surface = pygame.Surface((self.SCREEN_WIDTH - self.BORDER_SIZE * 2, 
                                         self.current_style.horizontal_banding_thickness), 
                                        pygame.SRCALPHA)
            band_surface.fill(band_color)
            
            for i in range(self.BORDER_SIZE, self.SCREEN_HEIGHT - self.BORDER_SIZE, self.UNIT_SIZE // 2):
                if self.random.random() < 0.1: # Random chance to draw a band
                    surface.blit(band_surface, (self.BORDER_SIZE, i))

        # --- Chunky Pixel Noise (for Commodore style) ---
        if self.current_style.pixel_noise_density > 0 and self.current_style.pixel_noise_alpha > 0:
            pixel_size = self.UNIT_SIZE // 2
            noise_surface = pygame.Surface((pixel_size, pixel_size), pygame.SRCALPHA)
            noise_surface.fill((*self.current_style.font_color[:3], 
                              min(255, self.current_style.pixel_noise_alpha)))
            
            for x in range(self.BORDER_SIZE, self.SCREEN_WIDTH - self.BORDER_SIZE, pixel_size):
                for y in range(self.BORDER_SIZE, self.SCREEN_HEIGHT - self.BORDER_SIZE, pixel_size):
                    if self.random.random() < self.current_style.pixel_noise_density:
                        surface.blit(noise_surface, (x, y))

    def _draw_grid(self, surface):
        grid_color = self.current_style.grid_color
        # Draw vertical lines
        for i in range(self.BORDER_SIZE, self.SCREEN_WIDTH - self.BORDER_SIZE, self.UNIT_SIZE):
            pygame.draw.line(surface, grid_color, (i, self.BORDER_SIZE), (i, self.SCREEN_HEIGHT - self.BORDER_SIZE))
        # Draw horizontal lines
        for i in range(self.BORDER_SIZE, self.SCREEN_HEIGHT - self.BORDER_SIZE, self.UNIT_SIZE):
            pygame.draw.line(surface, grid_color, (self.BORDER_SIZE, i), (self.SCREEN_WIDTH - self.BORDER_SIZE, i))

    def _draw_food(self, surface):
        # Draw glow effect for food
        for i in range(8, 0, -1):
            alpha = min(255, (8 - i) * 25)  # 25, 50, 75, ..., 200
            glow_surface = pygame.Surface((self.UNIT_SIZE + i * 2, self.UNIT_SIZE + i * 2), pygame.SRCALPHA)
            pygame.draw.circle(glow_surface, (*self.current_style.food_glow_color[:3], alpha), 
                             (glow_surface.get_width() // 2, glow_surface.get_height() // 2), 
                             (self.UNIT_SIZE + i * 2) // 2)
            surface.blit(glow_surface, (self.food.x - i, self.food.y - i))

        # Draw main food
        pygame.draw.circle(surface, self.current_style.food_color, 
                         (self.food.centerx, self.food.centery), self.UNIT_SIZE // 2)
        
        # Add bright center
        bright_food_center = (
            min(255, self.current_style.food_color[0] + 50),
            min(255, self.current_style.food_color[1] + 50),
            min(255, self.current_style.food_color[2] + 50)
        )
        pygame.draw.circle(surface, bright_food_center, 
                         (self.food.centerx, self.food.centery), (self.UNIT_SIZE - 8) // 2)

    def _draw_snake(self, surface):
        for i, segment in enumerate(self.snake):
            if i == 0:
                # Snake head with bright glow
                for j in range(6, 0, -1):
                    alpha = min(255, (6 - j) * 40)  # 40, 80, 120, ..., 200
                    glow_surface = pygame.Surface((self.UNIT_SIZE + j * 2, self.UNIT_SIZE + j * 2), pygame.SRCALPHA)
                    pygame.draw.rect(glow_surface, (*self.current_style.snake_head_color[:3], alpha), 
                                     glow_surface.get_rect(), border_radius=self.UNIT_SIZE // 4)
                    surface.blit(glow_surface, (segment.x - j, segment.y - j))
                
                pygame.draw.rect(surface, self.current_style.snake_head_color, segment, border_radius=self.UNIT_SIZE // 4)
                
                # Eyes (using background color to appear "cut out")
                pygame.draw.rect(surface, self.current_style.background_color, (segment.x + 3, segment.y + 3, 4, 4))
                pygame.draw.rect(surface, self.current_style.background_color, (segment.x + 13, segment.y + 3, 4, 4))
            else:
                # Snake body with subtle glow
                for j in range(3, 0, -1):
                    alpha = min(255, (3 - j) * 60)  # 60, 120, 180
                    glow_surface = pygame.Surface((self.UNIT_SIZE + j * 2, self.UNIT_SIZE + j * 2), pygame.SRCALPHA)
                    pygame.draw.rect(glow_surface, (*self.current_style.snake_body_color[:3], alpha), 
                                     glow_surface.get_rect(), border_radius=self.UNIT_SIZE // 4)
                    surface.blit(glow_surface, (segment.x - j, segment.y - j))

                pygame.draw.rect(surface, self.current_style.snake_body_color, segment, border_radius=self.UNIT_SIZE // 4)
                
                # Add inner highlight
                highlight_surface = pygame.Surface((self.UNIT_SIZE - 4, self.UNIT_SIZE - 4), pygame.SRCALPHA)
                highlight_surface.fill((*self.current_style.snake_body_color[:3], 100))
                surface.blit(highlight_surface, (segment.x + 2, segment.y + 2))

    def _draw_text_with_glow(self, surface, text, x, y, base_color):
        # Render text with Pygame's font.render
        rendered_text = self.current_style.crt_font.render(text, True, base_color)

        # Draw multiple layers for glow
        for i in range(4, 0, -1):
            alpha = min(255, (4 - i) * 50)  # 50, 100, 150, 200
            glow_color = (*base_color[:3], alpha)
            glow_surface = self.current_style.crt_font.render(text, True, glow_color)
            surface.blit(glow_surface, (x - i, y - i))
            surface.blit(glow_surface, (x + i, y + i))
            surface.blit(glow_surface, (x - i, y + i))
            surface.blit(glow_surface, (x + i, y - i))
        
        # Draw main text
        surface.blit(rendered_text, (x, y))

        # Add bright core
        bright_core_surface = self.current_style.crt_font.render(text, True, (255, 255, 255, 180))
        surface.blit(bright_core_surface, (x, y))

    def _draw_score_and_info(self, surface):
        score_text = f"SCORE: {self.score}"
        high_score_text = f"HIGH: {self.high_score}"
        game_time = int(time.time() - self.game_start_time)
        time_text = f"TIME: {game_time}s"

        self._draw_text_with_glow(surface, score_text, 10 + self.BORDER_SIZE, 30 + self.BORDER_SIZE, self.current_style.font_color)
        self._draw_text_with_glow(surface, high_score_text, 10 + self.BORDER_SIZE, 60 + self.BORDER_SIZE, self.current_style.font_color)

        # Position time on the right side
        time_text_surface = self.current_style.crt_font.render(time_text, True, self.current_style.font_color)
        time_x = self.SCREEN_WIDTH - self.BORDER_SIZE - time_text_surface.get_width() - 10
        self._draw_text_with_glow(surface, time_text, time_x, 30 + self.BORDER_SIZE, self.current_style.font_color)

    def _draw_game_over(self, surface):
        # Game Over title
        title_font = pygame.font.SysFont("Courier New", 48, bold=True)
        game_over_text = "GAME OVER"
        rendered_title = title_font.render(game_over_text, True, self.current_style.game_over_color)
        title_rect = rendered_title.get_rect(center=(self.SCREEN_WIDTH // 2, self.SCREEN_HEIGHT // 2 - 100))
        self._draw_text_with_glow(surface, game_over_text, title_rect.x, title_rect.y, self.current_style.game_over_color)

        # Final score
        final_score_text = f"FINAL SCORE: {self.score}"
        rendered_final_score = self.current_style.crt_font.render(final_score_text, True, self.current_style.font_color)
        score_rect = rendered_final_score.get_rect(center=(self.SCREEN_WIDTH // 2, self.SCREEN_HEIGHT // 2 + 30))
        self._draw_text_with_glow(surface, final_score_text, score_rect.x, score_rect.y, self.current_style.font_color)

        high_score_text = f"HIGH SCORE: {self.high_score}"
        rendered_high_score = self.current_style.crt_font.render(high_score_text, True, self.current_style.font_color)
        high_score_rect = rendered_high_score.get_rect(center=(self.SCREEN_WIDTH // 2, self.SCREEN_HEIGHT // 2 + 60))
        self._draw_text_with_glow(surface, high_score_text, high_score_rect.x, high_score_rect.y, self.current_style.font_color)

        # Restart instruction with blinking effect
        restart_text = "PRESS SPACE TO RESTART"
        current_time = time.time()
        # Blinking effect: render every other 0.5 second interval
        if int(current_time * 2) % 2 == 0:
            rendered_restart_text = self.current_style.crt_font.render(restart_text, True, self.current_style.restart_text_color)
            restart_rect = rendered_restart_text.get_rect(center=(self.SCREEN_WIDTH // 2, self.SCREEN_HEIGHT // 2 + 120))
            self._draw_text_with_glow(surface, restart_text, restart_rect.x, restart_rect.y, self.current_style.restart_text_color)

    def _draw_scanlines(self):
        # Create a surface for scanlines
        scanline_surface = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT), pygame.SRCALPHA)
        
        # Static scanlines
        for i in range(0, self.SCREEN_HEIGHT, 3):
            pygame.draw.line(scanline_surface, (*self.current_style.scanline_color[:3], 
                            min(255, self.current_style.scanline_alpha)), 
                           (0, i), (self.SCREEN_WIDTH, i), 1)
        
        # Moving scanline
        current_time_ms = pygame.time.get_ticks()
        scan_y = int((current_time_ms / 10) % self.SCREEN_HEIGHT)
        pygame.draw.line(scanline_surface, (*self.current_style.font_color[:3], 30),
                        (0, scan_y), (self.SCREEN_WIDTH, scan_y), 2)
        
        self.screen.blit(scanline_surface, (0, 0))

    def _draw_screen_border(self):
        # Draw outer CRT bezel (non-playable area)
        pygame.draw.rect(self.screen, self.current_style.bezel_color, 
                         (0, 0, self.SCREEN_WIDTH, self.BORDER_SIZE), border_radius=15)
        pygame.draw.rect(self.screen, self.current_style.bezel_color, 
                         (0, self.SCREEN_HEIGHT - self.BORDER_SIZE, self.SCREEN_WIDTH, self.BORDER_SIZE), border_radius=15)
        pygame.draw.rect(self.screen, self.current_style.bezel_color, 
                         (0, 0, self.BORDER_SIZE, self.SCREEN_HEIGHT), border_radius=15)
        pygame.draw.rect(self.screen, self.current_style.bezel_color, 
                         (self.SCREEN_WIDTH - self.BORDER_SIZE, 0, self.BORDER_SIZE, self.SCREEN_HEIGHT), border_radius=15)

        # Draw CRT screen border (inner border)
        pygame.draw.rect(self.screen, self.current_style.border_color, 
                         (self.BORDER_SIZE - 2, self.BORDER_SIZE - 2, 
                          self.SCREEN_WIDTH - self.BORDER_SIZE * 2 + 4, 
                          self.SCREEN_HEIGHT - self.BORDER_SIZE * 2 + 4), 
                         width=4, border_radius=15)

        # Add an inner glow on the playable area edge
        inner_glow_surface = pygame.Surface((self.SCREEN_WIDTH - self.BORDER_SIZE * 2, 
                                            self.SCREEN_HEIGHT - self.BORDER_SIZE * 2), 
                                           pygame.SRCALPHA)
        pygame.draw.rect(inner_glow_surface, (*self.current_style.inner_glow_color[:3], 30),
                        (0, 0, inner_glow_surface.get_width(), inner_glow_surface.get_height()),
                        width=2, border_radius=10)
        self.screen.blit(inner_glow_surface, (self.BORDER_SIZE, self.BORDER_SIZE))

    def run(self):
        running_game = True
        while running_game:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running_game = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        if self.direction != 'R': self.direction = 'L'
                    elif event.key == pygame.K_RIGHT:
                        if self.direction != 'L': self.direction = 'R'
                    elif event.key == pygame.K_UP:
                        if self.direction != 'D': self.direction = 'U'
                    elif event.key == pygame.K_DOWN:
                        if self.direction != 'U': self.direction = 'D'
                    elif event.key == pygame.K_SPACE:
                        if not self.running:
                            self.start_game()
                elif event.type == self.GAME_UPDATE: # Custom event for game updates
                    if self.running:
                        self.move()
                        self.check_food()
                        self.check_collisions()
            
            self.draw()
            self.clock.tick(60) # Limit frame rate to 60 FPS

        pygame.quit()

if __name__ == "__main__":
    game = SnakeGamePygame()
    game.run()