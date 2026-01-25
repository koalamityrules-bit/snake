import pygame as pg
from random import randrange

DEFAULT_TIME_STEP = 150

# Initialize Pygame
pg.init()
WINDOW = 800
TILE_SIZE = 50
RANGE = (TILE_SIZE // 2, WINDOW - TILE_SIZE // 2, TILE_SIZE)
get_random_position = lambda: [randrange(*RANGE), randrange(*RANGE)]
snake = pg.rect.Rect([0, 0, TILE_SIZE - 5, TILE_SIZE - 5])
snake.center = get_random_position()
length = 1
segments = [snake.copy()]
snake_dir = (0, 0)
time, time_step = 0, DEFAULT_TIME_STEP
food = pg.rect.Rect([0, 0, TILE_SIZE - 2, TILE_SIZE - 2])
food.center = get_random_position()
score = 0
level = 1
next_level_score = 50
obstacles = []
portal = None
boss_apple = None  # Boss apple for level 1
game_over = False
game_over_time = 0
game_over_display_time = 1500  # milliseconds to show the game over message
key_pressed = False
animating_level_up = False
animation_start_time = 0
animation_duration = 1000  # 1 second
boss_move_time = 0
boss_move_step = 100  # milliseconds between boss moves

screen = pg.display.set_mode((WINDOW, WINDOW))
font = pg.font.SysFont('arial', 36)
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

        keys = pg.key.get_pressed()
        if (keys[pg.K_w] and dirs[pg.K_w]) or (keys[pg.K_s] and dirs[pg.K_s]) or (keys[pg.K_a] and dirs[pg.K_a]) or (keys[pg.K_d] and dirs[pg.K_d]):
            time_step = DEFAULT_TIME_STEP // 2
            key_pressed = True
        
        if event.type == pg.KEYUP:
            if not (keys[pg.K_w] or keys[pg.K_s] or keys[pg.K_a] or keys[pg.K_d]) and key_pressed:
                time_step = DEFAULT_TIME_STEP
                key_pressed = False

    time_now = pg.time.get_ticks()

    screen.fill('black')

    if not animating_level_up:
        # Check borders and self eating
        self_eating = snake.center in [segment.center for segment in segments[:-1]]
        obstacle_collision = any(obs.collidepoint(snake.center) for obs in obstacles)
        if not 0 <= snake.x < WINDOW or not 0 <= snake.y < WINDOW or self_eating or obstacle_collision:
            if not game_over:
                print("You died! Game Over!")
                game_over = True
                game_over_time = time_now
                snake_dir = (0, 0)

        # Check for collision with food
        if snake.center == food.center:
            food.center = get_random_position()
            # Ensure food doesn't spawn on obstacles, snake, or portal
            while any(obs.collidepoint(food.center) for obs in obstacles) or any(food.collidepoint(seg.center) for seg in segments) or (portal and portal.collidepoint(food.center)):
                food.center = get_random_position()
            length += 1
            score += 10
            # Check if ready for next level
            if score >= next_level_score and not portal:
                portal = pg.rect.Rect([0, 0, TILE_SIZE, TILE_SIZE])
                portal.center = get_random_position()
                # Ensure portal doesn't overlap with food, snake, or obstacles
                while portal.colliderect(food) or any(portal.colliderect(seg) for seg in segments) or any(portal.colliderect(obs) for obs in obstacles):
                    portal.center = get_random_position()

        # Check for collision with portal
        if portal and portal.collidepoint(snake.center) and not animating_level_up:
            if level == 1:
                # Spawn boss apple instead of advancing level
                boss_apple = pg.rect.Rect([0, 0, TILE_SIZE - 2, TILE_SIZE - 2])
                boss_apple.center = get_random_position()
                portal = None
                boss_move_time = time_now
            else:
                animating_level_up = True
                animation_start_time = time_now
                portal = None
        
        # Check for collision with boss apple
        if boss_apple and abs(snake.center[0] - boss_apple.center[0]) < TILE_SIZE and abs(snake.center[1] - boss_apple.center[1]) < TILE_SIZE:
            boss_apple = None
            animating_level_up = True
            animation_start_time = time_now
            score += 50  # Bonus for defeating the boss

    # Draw food
    pg.draw.circle(screen, 'red', food.center, food.width // 2)
    
    # Draw boss apple if active
    if boss_apple:
        pg.draw.circle(screen, 'gold', boss_apple.center, boss_apple.width // 2)
        # Draw a crown on the boss
        crown_offset = boss_apple.width // 4
        pg.draw.polygon(screen, 'gold', [
            (boss_apple.center[0] - crown_offset, boss_apple.center[1] - crown_offset),
            (boss_apple.center[0], boss_apple.center[1] - crown_offset - crown_offset // 2),
            (boss_apple.center[0] + crown_offset, boss_apple.center[1] - crown_offset)
        ])

    # Draw obstacles
    for obs in obstacles:
        pg.draw.rect(screen, 'gray', obs)

    # Draw portal
    if portal:
        pg.draw.rect(screen, 'blue', portal)

    # Draw score
    score_text = font.render(f'Score: {score}', True, 'white')
    screen.blit(score_text, (10, 10))
    # Draw level
    level_text = font.render(f'Level: {level}', True, 'white')
    screen.blit(level_text, (10, 50))

    # Draw and update snake segments
    for segment in segments[:-1]:
        pg.draw.rect(screen, 'green', segment)
    # draw head (last segment) in yellow
    pg.draw.rect(screen, 'yellow', segments[-1])

    # If game over, draw the message and after a short delay reset the game
    if game_over:
        msg = font.render('You died! Game Over!', True, 'red')
        msg_rect = msg.get_rect(center=(WINDOW // 2, WINDOW // 2))
        screen.blit(msg, msg_rect)
        if time_now - game_over_time > game_over_display_time:
            # reset the game state
            snake.center = get_random_position()
            food.center = get_random_position()
            length, snake_dir = 1, (0, 0)
            segments = [snake.copy()]
            score = 0
            level = 1
            next_level_score = 50
            time_step = DEFAULT_TIME_STEP
            obstacles = []
            portal = None
            boss_apple = None
            animating_level_up = False
            game_over = False

    # Handle level up animation
    if animating_level_up:
        # Calculate fade alpha (0 to 255)
        elapsed = time_now - animation_start_time
        alpha = min(255, (elapsed / animation_duration) * 255)
        # Create a surface for the overlay
        overlay = pg.Surface((WINDOW, WINDOW))
        overlay.set_alpha(alpha)
        overlay.fill('black')
        screen.blit(overlay, (0, 0))
        # Check if animation is complete
        if elapsed > animation_duration:
            # Complete level up
            level += 1
            next_level_score += 50
            time_step = max(50, DEFAULT_TIME_STEP - (level - 1) * 20)  # Speed up but not too much
            # Add obstacles progressively
            if level == 3 and not obstacles:
                obstacles = [
                    pg.rect.Rect(200, 200, TILE_SIZE, TILE_SIZE),
                    pg.rect.Rect(400, 400, TILE_SIZE, TILE_SIZE),
                    pg.rect.Rect(600, 200, TILE_SIZE, TILE_SIZE),
                ]
            elif level > 3:
                # Add more obstacles for higher levels
                new_obs = pg.rect.Rect([0, 0, TILE_SIZE, TILE_SIZE])
                new_obs.center = get_random_position()
                while any(new_obs.colliderect(obs) for obs in obstacles) or new_obs.colliderect(food) or any(new_obs.colliderect(seg) for seg in segments):
                    new_obs.center = get_random_position()
                obstacles.append(new_obs)
            animating_level_up = False

    if (not game_over) and (not animating_level_up) and (time_now - time > time_step):
        time = time_now
        snake.move_ip(snake_dir)
        segments.append(snake.copy())
        segments = segments[-length:]
        
        # Move boss apple away from snake
        if boss_apple and (time_now - boss_move_time > boss_move_step):
            boss_move_time = time_now
            # Calculate direction away from snake
            dx = boss_apple.center[0] - snake.center[0]
            dy = boss_apple.center[1] - snake.center[1]
            # Normalize and move
            distance = (dx**2 + dy**2)**0.5
            if distance > 0:
                dx = (dx / distance) * TILE_SIZE
                dy = (dy / distance) * TILE_SIZE
                boss_apple.move_ip(dx, dy)
                # Keep boss apple in bounds
                boss_apple.x = max(TILE_SIZE // 2, min(WINDOW - TILE_SIZE // 2, boss_apple.x))
                boss_apple.y = max(TILE_SIZE // 2, min(WINDOW - TILE_SIZE // 2, boss_apple.y))

    pg.display.flip()
    clock.tick(60)
    