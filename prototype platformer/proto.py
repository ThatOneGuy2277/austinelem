import pygame
import random  # Add import for random
import os  # Add import for os

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Platformer Game")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)

# Colors and background
BACKGROUND_COLOR = (135, 206, 235)  # Sky blue
PLATFORM_COLOR = (139, 69, 19)  # Brown for platforms
GROUND_COLOR = (34, 139, 34)  # Green for ground
PLAYER_COLOR = (0, 0, 255)  # Blue for the player
ENEMY_COLOR = (255, 69, 0)  # Orange-red for enemies

# Clock and FPS
clock = pygame.time.Clock()
FPS = 60

# Player settings
player_width, player_height = 50, 50
player_x, player_y = WIDTH // 2, HEIGHT - 60
player_speed = 5
player_jump = -15
player_velocity_y = 0
gravity = 0.8
on_ground = False

# Ground floor settings
ground_y = HEIGHT - 10

# Bullet settings
bullets = []
bullet_width, bullet_height = 10, 5
bullet_speed = 10
bullet_color = BLACK

# Add a flag to track spacebar press
space_pressed = False

# Add a variable to track the player's direction
player_direction = "right"

# Enemy settings
enemies = []
enemy_width, enemy_height = 40, 40
enemy_color = (255, 0, 0)
enemy_spawn_timer = 0 
enemy_spawn_interval = 120  # Spawn an enemy every 2 seconds (120 frames)

# Enemy bullet settings
enemy_bullets = []
enemy_bullet_width, enemy_bullet_height = 10, 5
enemy_bullet_speed = 5
enemy_bullet_color = (255, 0, 0)
enemy_shoot_timer = 0
enemy_shoot_interval = 90  # Enemies shoot every 1.5 seconds (90 frames)

# Score settings
score = 0
font = pygame.font.Font(pygame.font.match_font('arial'), 36)

# High score settings
high_score_file = "highscore.txt"
if os.path.exists(high_score_file):
    with open(high_score_file, "r") as file:
        high_score = int(file.read().strip())
else:
    high_score = 0

# Platform settings
platforms = [
    (200, 470, 100, 20),  # Lowered from y=450 to y=470
    (400, 370, 100, 20),  # Lowered from y=350 to y=370
    (600, 270, 100, 20)   # Lowered from y=250 to y=270
]
platform_color = GREEN

# Game loop flag
running = True

def update_high_score(new_score):
    """Update the high score in the file if the new score is higher."""
    global high_score
    if new_score > high_score:
        high_score = new_score
        with open(high_score_file, "w") as file:
            file.write(str(high_score))

def end_game_screen():
    """Display the end game screen with a retry option and the final score."""
    global score
    update_high_score(score)  # Update high score before showing the end screen

    font_large = pygame.font.Font(None, 74)
    font_medium = pygame.font.Font(None, 50)
    text = font_large.render("Game Over", True, (255, 0, 0))  # Red "Game Over" text
    score_text = font_medium.render(f"Final Score: {score}", True, (255, 255, 255))
    high_score_text = font_medium.render(f"High Score: {high_score}", True, (255, 255, 0))  # Yellow high score text
    retry_text = font_medium.render("Press R to Retry", True, (0, 0, 0))

    # Draw background
    screen.fill((0, 0, 0))  # Black background

    # Draw "Game Over" text
    screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 4))

    # Draw final score
    screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, HEIGHT // 2.5))

    # Draw high score
    screen.blit(high_score_text, (WIDTH // 2 - high_score_text.get_width() // 2, HEIGHT // 2))

    # Draw retry button-like rectangle with red border
    retry_rect = pygame.Rect(WIDTH // 2 - 150, HEIGHT // 2 + 50, 300, 60)
    pygame.draw.rect(screen, (255, 255, 255), retry_rect)  # White rectangle
    pygame.draw.rect(screen, (255, 0, 0), retry_rect, 5)  # Red border
    screen.blit(retry_text, (WIDTH // 2 - retry_text.get_width() // 2, HEIGHT // 2 + 60))

    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:  # Retry the game
                    waiting = False

# Main game loop
while running:
    screen.fill(WHITE)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:  # Detect spacebar press
                space_pressed = True
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_SPACE:  # Reset spacebar flag on release
                space_pressed = False

    # Player controls
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] or keys[pygame.K_a]:  # Left arrow or 'A' key
        player_x -= player_speed
        player_direction = "left"
    if keys[pygame.K_RIGHT] or keys[pygame.K_d]:  # Right arrow or 'D' key
        player_x += player_speed
        player_direction = "right"

    # Prevent the player from going off the sides of the screen
    player_x = max(0, min(player_x, WIDTH - player_width))

    if (keys[pygame.K_UP] or keys[pygame.K_w]) and on_ground:  # Up arrow or 'W' key for jump
        player_velocity_y = player_jump
        on_ground = False
    if space_pressed:  # Shoot only on tap
        if player_direction == "right":
            bullets.append([player_x + player_width, player_y + player_height // 2, bullet_speed])  # Right direction
        elif player_direction == "left":
            bullets.append([player_x - bullet_width, player_y + player_height // 2, -bullet_speed])  # Left direction
        space_pressed = False  # Reset after shooting

    # Apply gravity
    player_velocity_y += gravity
    player_y += player_velocity_y

    # Check for collisions with the ground floor
    if player_y + player_height >= ground_y:
        player_y = ground_y - player_height
        player_velocity_y = 0
        on_ground = True

    # Check for collisions with platforms
    for platform in platforms:
        px, py, pw, ph = platform
        if px < player_x + player_width and player_x < px + pw:  # Horizontal collision
            if py < player_y + player_height <= py + ph:  # Vertical collisiond
                player_y = py - player_height
                player_velocity_y = 0
                on_ground = True
                break

    # Ensure `on_ground` is False if no collisions are detected
    if not on_ground:
        on_ground = False

    # Spawn enemies randomly around the player
    enemy_spawn_timer += 1
    if enemy_spawn_timer >= enemy_spawn_interval:
        enemy_spawn_timer = 0
        enemy_x = random.randint(max(0, int(player_x - 200)), min(WIDTH - enemy_width, int(player_x + 200)))
        enemy_y = ground_y - enemy_height  # Ensure enemies spawn on the ground
        enemies.append([enemy_x, enemy_y])

    # Enemies shoot bullets toward the player
    enemy_shoot_timer += 1
    if enemy_shoot_timer >= enemy_shoot_interval:
        enemy_shoot_timer = 0
        for enemy in enemies:
            direction = 1 if enemy[0] < player_x else -1  # Determine direction toward the player
            enemy_bullets.append([enemy[0] + enemy_width // 2, enemy[1] + enemy_height // 2, direction * enemy_bullet_speed])

    # Update bullets
    for bullet in bullets:
        bullet[0] += bullet[2]  # Update bullet position based on its direction
    bullets = [bullet for bullet in bullets if 0 < bullet[0] < WIDTH]  # Remove off-screen bullets

    # Update enemy bullets
    for bullet in enemy_bullets:
        bullet[0] += bullet[2]  # Update bullet position based on its direction
    enemy_bullets = [bullet for bullet in enemy_bullets if 0 < bullet[0] < WIDTH]  # Remove off-screen bullets

    # Check for collisions between bullets and enemies
    for bullet in bullets[:]:
        for enemy in enemies[:]:
            if (
                bullet[0] < enemy[0] + enemy_width and
                bullet[0] + bullet_width > enemy[0] and
                bullet[1] < enemy[1] + enemy_height and
                bullet[1] + bullet_height > enemy[1]
            ):
                bullets.remove(bullet)
                enemies.remove(enemy)
                score += 1  # Increment score when an enemy is killed
                break

    # Check for collisions between enemy bullets and the player
    for bullet in enemy_bullets[:]:
        if (
            bullet[0] < player_x + player_width and
            bullet[0] + enemy_bullet_width > player_x and
            bullet[1] < player_y + player_height and
            bullet[1] + enemy_bullet_height > player_y
        ):
            print("Player hit!")
            end_game_screen()  # Show the end game screen
            # Reset game state
            player_x, player_y = WIDTH // 2, HEIGHT - 60
            player_velocity_y = 0
            bullets.clear()
            enemy_bullets.clear()
            enemies.clear()
            enemy_spawn_timer = 0
            enemy_shoot_timer = 0
            score = 0  # Reset score
            break

    # Draw background
    screen.fill(BACKGROUND_COLOR)

    # Draw ground floor
    pygame.draw.rect(screen, GROUND_COLOR, (0, ground_y, WIDTH, HEIGHT - ground_y))

    # Draw player
    pygame.draw.rect(screen, PLAYER_COLOR, (player_x, player_y, player_width, player_height))

    # Draw bullets
    for bullet in bullets:
        pygame.draw.rect(screen, bullet_color, (int(bullet[0]), int(bullet[1]), bullet_width, bullet_height))

    # Draw enemy bullets
    for bullet in enemy_bullets:
        pygame.draw.rect(screen, enemy_bullet_color, (int(bullet[0]), int(bullet[1]), enemy_bullet_width, enemy_bullet_height))

    # Draw enemies
    for enemy in enemies:
        pygame.draw.rect(screen, ENEMY_COLOR, (int(enemy[0]), int(enemy[1]), enemy_width, enemy_height))

    # Draw platforms
    for platform in platforms:
        pygame.draw.rect(screen, PLATFORM_COLOR, platform)

    # Draw score and high score with a shadow effect
    score_text = font.render(f"Score: {score}", True, (0, 0, 0))  # Shadow (black)
    screen.blit(score_text, (12, 12))
    score_text = font.render(f"Score: {score}", True, (255, 255, 255))  # Foreground (white)
    screen.blit(score_text, (10, 10))

    high_score_text = font.render(f"High Score: {high_score}", True, (0, 0, 0))  # Shadow (black)
    screen.blit(high_score_text, (12, 42))
    high_score_text = font.render(f"High Score: {high_score}", True, (255, 255, 255))  # Foreground (white)
    screen.blit(high_score_text, (10, 40))

    # Update display and tick clock
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
