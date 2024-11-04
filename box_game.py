import pygame
import sys

# Initialize Pygame
pygame.init()

# Grid settings
GRID_WIDTH = 10
GRID_HEIGHT = 10
CELL_SIZE = 40  # Size of each grid cell in pixels

# Screen settings
SCREEN_WIDTH = GRID_WIDTH * CELL_SIZE
SCREEN_HEIGHT = GRID_HEIGHT * CELL_SIZE

# Colors
BACKGROUND_COLOR = (30, 30, 30)
GRID_COLOR = (50, 50, 50)
BOX_COLOR = (200, 200, 200)
PLACED_BOX_COLOR = (0, 0, 255)

# Initialize screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Grid Box Placement Game")

# Clock for controlling frame rate
clock = pygame.time.Clock()

# Grid occupancy (2D list)
grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]

# List of boxes to place (width, height)
boxes_to_place = [(2, 2), (3, 1), (1, 4), (2, 3), (1, 1)]

# Index of the current box
current_box_index = 0

# Current box position (top-left corner in grid coordinates)
current_box_x = 0
current_box_y = 0

# Flag to indicate if the game is over
game_over = False

# List of placed boxes for rendering
placed_boxes = []

def draw_grid():
    for x in range(GRID_WIDTH):
        for y in range(GRID_HEIGHT):
            rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(screen, GRID_COLOR, rect, 1)

def draw_boxes():
    # Draw placed boxes
    for box in placed_boxes:
        x, y, w, h = box
        rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, w * CELL_SIZE, h * CELL_SIZE)
        pygame.draw.rect(screen, PLACED_BOX_COLOR, rect)

    # Draw the current box
    if not game_over and current_box_index < len(boxes_to_place):
        w, h = boxes_to_place[current_box_index]
        rect = pygame.Rect(current_box_x * CELL_SIZE, current_box_y * CELL_SIZE, w * CELL_SIZE, h * CELL_SIZE)
        pygame.draw.rect(screen, BOX_COLOR, rect)

def can_place_box(x, y, w, h):
    # Check if the box is within the grid boundaries
    if x < 0 or y < 0 or x + w > GRID_WIDTH or y + h > GRID_HEIGHT:
        return False
    # Check if the box overlaps any placed boxes
    for i in range(h):
        for j in range(w):
            if grid[y + i][x + j] == 1:
                return False
    return True

def place_box(x, y, w, h):
    # Mark the grid cells as occupied
    for i in range(h):
        for j in range(w):
            grid[y + i][x + j] = 1
    # Add the box to the placed boxes list
    placed_boxes.append((x, y, w, h))

# Main game loop
while True:
    screen.fill(BACKGROUND_COLOR)
    draw_grid()
    draw_boxes()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if not game_over and event.type == pygame.KEYDOWN:
            w, h = boxes_to_place[current_box_index]

            if event.key == pygame.K_LEFT:
                if current_box_x > 0:
                    if can_place_box(current_box_x - 1, current_box_y, w, h):
                        current_box_x -= 1
            elif event.key == pygame.K_RIGHT:
                if current_box_x + w < GRID_WIDTH:
                    if can_place_box(current_box_x + 1, current_box_y, w, h):
                        current_box_x += 1
            elif event.key == pygame.K_UP:
                if current_box_y > 0:
                    if can_place_box(current_box_x, current_box_y - 1, w, h):
                        current_box_y -= 1
            elif event.key == pygame.K_DOWN:
                if current_box_y + h < GRID_HEIGHT:
                    if can_place_box(current_box_x, current_box_y + 1, w, h):
                        current_box_y += 1
            elif event.key == pygame.K_RETURN:
                if can_place_box(current_box_x, current_box_y, w, h):
                    place_box(current_box_x, current_box_y, w, h)
                    current_box_index += 1
                    # Reset position for next box
                    current_box_x, current_box_y = 0, 0
                    if current_box_index >= len(boxes_to_place):
                        game_over = True
                else:
                    print("Cannot place box here!")
            elif event.key == pygame.K_DELETE:
                # Discard the current box and move to the next one
                current_box_index += 1
                # Reset position for next box
                current_box_x, current_box_y = 0, 0
                if current_box_index >= len(boxes_to_place):
                    game_over = True

    if game_over:
        # Calculate score
        score = sum(row.count(1) for row in grid)
        font = pygame.font.SysFont(None, 48)
        text = font.render(f"Game Over! Score: {score}", True, (255, 255, 255))
        screen.blit(text, ((SCREEN_WIDTH - text.get_width()) // 2, SCREEN_HEIGHT // 2))
    else:
        # Display current score
        score = sum(row.count(1) for row in grid)
        font = pygame.font.SysFont(None, 24)
        text = font.render(f"Score: {score}", True, (255, 255, 255))
        screen.blit(text, (10, 10))

    pygame.display.flip()
    clock.tick(60)
