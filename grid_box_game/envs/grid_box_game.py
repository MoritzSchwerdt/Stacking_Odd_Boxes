import pygame
import numpy as np

class GridBoxGame:
    def __init__(self, grid_width=5, grid_height=5, cell_size=40, np_random=None, render_mode=None):
        # Initialize Pygame
        pygame.init()
        self.np_random = np_random or np.random.default_rng()

        # Grid settings
        self.GRID_WIDTH = grid_width
        self.GRID_HEIGHT = grid_height
        self.CELL_SIZE = cell_size

        # Screen settings
        self.SCREEN_WIDTH = self.GRID_WIDTH * self.CELL_SIZE
        self.SCREEN_HEIGHT = self.GRID_HEIGHT * self.CELL_SIZE

        # Colors
        self.BACKGROUND_COLOR = (30, 30, 30)
        self.GRID_COLOR = (50, 50, 50)
        self.BOX_COLOR = (200, 200, 200)
        self.PLACED_BOX_COLOR = (0, 0, 255)

        # Initialize screen
        self.screen = None  # Will be initialized in render
        self.clock = pygame.time.Clock()
        self.FPS = 60

        # Grid occupancy (2D array)
        self.grid = np.zeros((self.GRID_HEIGHT, self.GRID_WIDTH), dtype=int)

        # List of boxes to place (width, height)
        # Define 10 boxes
        self.boxes_to_place = [
            (2, 2), (3, 1), (1, 4), (2, 3), (1, 1),
            (3, 2), (2, 1), (1, 3), (4, 1), (2, 2)
        ]
        self.current_box_index = 0

        # Current box position
        self.current_box_x = 0
        self.current_box_y = 0

        # List of placed boxes for rendering
        self.placed_boxes = []

        # Game state
        self.is_game_over = False

        # Render mode
        self.render_mode = render_mode

    def reset(self):
        self.grid.fill(0)
        self.current_box_index = 0
        self.current_box_x = 0
        self.current_box_y = 0
        self.placed_boxes.clear()
        self.is_game_over = False
        return self.observe()

    def observe(self):
        obs = {
            'grid': self.grid.copy(),
            'current_box_position': np.array([self.current_box_x, self.current_box_y], dtype=int),
            'current_box_size': np.array(
                self.boxes_to_place[self.current_box_index], dtype=int
            ) if self.current_box_index < len(self.boxes_to_place) else np.array([0, 0], dtype=int)
        }
        return obs

    def action(self, action):
        # Actions:
        # 0: Move Left
        # 1: Move Right
        # 2: Move Up
        # 3: Move Down
        # 4: Place Box
        # 5: Discard Box

        if self.is_game_over:
            return 0  # No reward if game is over

        reward = 0
        w, h = self.boxes_to_place[self.current_box_index] if self.current_box_index < len(self.boxes_to_place) else (0, 0)

        if action == 0:  # Move Left
            if self.current_box_x > 0:
                self.current_box_x -= 1
        elif action == 1:  # Move Right
            if self.current_box_x + w < self.GRID_WIDTH:
                self.current_box_x += 1
        elif action == 2:  # Move Up
            if self.current_box_y > 0:
                self.current_box_y -= 1
        elif action == 3:  # Move Down
            if self.current_box_y + h < self.GRID_HEIGHT:
                self.current_box_y += 1
        elif action == 4:  # Place Box
            if self._can_place_box(self.current_box_x, self.current_box_y, w, h):
                self._place_box(self.current_box_x, self.current_box_y, w, h)
                reward = w * h  # Reward is the area of the box placed
                self.current_box_index += 1
                self.current_box_x, self.current_box_y = 0, 0  # Reset position for next box
                if self.current_box_index >= len(self.boxes_to_place):
                    self.is_game_over = True
            else:
                # Cannot place box here, invalid placement
                reward = -0.1  # Penalty for invalid placement
        elif action == 5:  # Discard Box
            self.current_box_index += 1
            self.current_box_x, self.current_box_y = 0, 0  # Reset position
            if self.current_box_index >= len(self.boxes_to_place):
                self.is_game_over = True
            reward = -0.5

        return reward

    def _can_place_box(self, x, y, w, h):
        if x < 0 or y < 0 or x + w > self.GRID_WIDTH or y + h > self.GRID_HEIGHT:
            return False
        if np.any(self.grid[y:y+h, x:x+w] == 1):
            return False
        return True

    def _place_box(self, x, y, w, h):
        self.grid[y:y+h, x:x+w] = 1
        self.placed_boxes.append((x, y, w, h))

    def is_done(self):
        return self.is_game_over

    def render(self, mode=None):
        if mode is None:
            mode = self.render_mode
        if self.screen is None:
            if mode == 'human':
                self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
                pygame.display.set_caption("Grid Box Placement Game")
            elif mode == 'rgb_array':
                self.screen = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
            else:
                raise ValueError(f"Unsupported render mode: {mode}")

        self.screen.fill(self.BACKGROUND_COLOR)
        self._draw_grid()
        self._draw_boxes()

        if mode == 'human':
            pygame.display.flip()
            self.clock.tick(self.FPS)
        elif mode == 'rgb_array':
            return self._get_frame()

    def _draw_grid(self):
        for x in range(self.GRID_WIDTH):
            for y in range(self.GRID_HEIGHT):
                rect = pygame.Rect(x * self.CELL_SIZE, y * self.CELL_SIZE, self.CELL_SIZE, self.CELL_SIZE)
                pygame.draw.rect(self.screen, self.GRID_COLOR, rect, 1)

    def _draw_boxes(self):
        # Draw placed boxes
        for box in self.placed_boxes:
            x, y, w, h = box
            rect = pygame.Rect(x * self.CELL_SIZE, y * self.CELL_SIZE, w * self.CELL_SIZE, h * self.CELL_SIZE)
            pygame.draw.rect(self.screen, self.PLACED_BOX_COLOR, rect)

        # Draw current box
        if not self.is_game_over and self.current_box_index < len(self.boxes_to_place):
            w, h = self.boxes_to_place[self.current_box_index]
            rect = pygame.Rect(
                self.current_box_x * self.CELL_SIZE,
                self.current_box_y * self.CELL_SIZE,
                w * self.CELL_SIZE,
                h * self.CELL_SIZE
            )
            pygame.draw.rect(self.screen, self.BOX_COLOR, rect)

    def _get_frame(self):
        # Return an array representing the RGB frame
        return np.transpose(
            pygame.surfarray.array3d(self.screen), axes=(1, 0, 2)
        )

    def close(self):
        if self.screen is not None:
            if self.render_mode == 'human':
                pygame.display.quit()
            pygame.quit()
            self.screen = None
