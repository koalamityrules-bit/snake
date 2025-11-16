import pygame as pg
from random import randrange

# Initialize Pygame
WINDOW = 800
TILE_SIZE = 50
RANGE = (TILE_SIZE // 2, WINDOW - TILE_SIZE // 2, TILE_SIZE)
get_random_position = lambda: [randrange(*RANGE), randrange(*RANGE)]
snake = pg.rect.Rect([0, 0, TILE_SIZE - 2, TILE_SIZE - 2])
snake.center = get_random_position()
length = 1
segments = [snake.copy()]
snake_dir = (0, 0)
time, time_step = 0, 150
food = pg.rect.Rect([0, 0, TILE_SIZE - 2, TILE_SIZE - 2])
food.center = get_random_position()

screen = pg.display.set_mode((WINDOW, WINDOW))
clock = pg.time.Clock()
dirs = {pg.K_w: 1, pg.K_s: 1, pg.K_a: 1, pg.K_d: 1}

while True:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            exit()
        
        # Handle key presses for snake movement
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_w and dirs[pg.K_w]:
                snake_dir = (0, -TILE_SIZE)
                dirs = {pg.K_w: 1, pg.K_s: 0, pg.K_a: 1, pg.K_d: 1}
            if event.key == pg.K_s and dirs[pg.K_s]:
                snake_dir = (0, TILE_SIZE)
                dirs = {pg.K_w: 0, pg.K_s: 1, pg.K_a: 1, pg.K_d: 1}
            if event.key == pg.K_a and dirs[pg.K_a]:
                snake_dir = (-TILE_SIZE, 0)
                dirs = {pg.K_w: 1, pg.K_s: 1, pg.K_a: 1, pg.K_d: 0}
            if event.key == pg.K_d and dirs[pg.K_d]:
                snake_dir = (TILE_SIZE, 0)
                dirs = {pg.K_w: 1, pg.K_s: 1, pg.K_a: 0, pg.K_d: 1}

    screen.fill('black')
    # Check borders and self eating
    self_eating = snake.center in [segment.center for segment in segments[:-1]]
    if not 0 <= snake.x < WINDOW or not 0 <= snake.y < WINDOW or self_eating:
        # print("Game Over! You hit the wall.")
        # exit()
        snake.center = get_random_position()
        food.center = get_random_position()
        length, snake_dir = 1, (0, 0)
        segments = [snake.copy()]

    # Check for collision with food
    if snake.center == food.center:
        food.center = get_random_position()
        length += 1

    # Draw food
    pg.draw.circle(screen, 'red', food.center, food.width // 2)

    # Draw and update snake segments
    for segment in segments:
        pg.draw.rect(screen, 'green', segment)

    time_now = pg.time.get_ticks()
    if time_now - time > time_step:
        time = time_now
        snake.move_ip(snake_dir)
        segments.append(snake.copy())
        segments = segments[-length:]

    pg.display.flip()
    clock.tick(60)
    