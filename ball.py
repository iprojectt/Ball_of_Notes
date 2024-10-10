import pygame
import random
import sys

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 1200, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Perfect Pitch Game')

# Fonts and colors
FONT = pygame.font.SysFont('Arial', 36)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
ORANGE = (255, 165, 0)  # Define the orange color

# Musical notes
NOTES = ['Sa', 'Re', 'G', 'M', 'P', 'Dha', 'Ni']
note_heights = {  # Heights for the note holes in increasing order
    'Sa': HEIGHT - 100,
    'Re': HEIGHT - 150,
    'G': HEIGHT - 200,
    'M': HEIGHT - 250,
    'P': HEIGHT - 300,
    'Dha': HEIGHT - 350,
    'Ni': HEIGHT - 400
}

# Load sound files
sounds = {
    'Sa': pygame.mixer.Sound('c1.wav'),  # Replace with actual file paths
    'Re': pygame.mixer.Sound('d1.wav'),
    'G': pygame.mixer.Sound('e1.wav'),
    'M': pygame.mixer.Sound('f1.wav'),
    'P': pygame.mixer.Sound('g1.wav'),
    'Dha': pygame.mixer.Sound('a1.wav'),
    'Ni': pygame.mixer.Sound('b1.wav')
}

# Game variables
current_note = random.choice(NOTES)
user_note = ''
score = 0
walls_passed = 0  # New variable to track how many walls have been passed

# Ball settings
ball_x, ball_y = WIDTH // 8, HEIGHT  # Set initial ball position at the bottom
ball_radius = 20
ball_speed_x = 0.6  # Slower speed for horizontal movement
ball_direction = 1  # 1 = moving right, -1 = moving left

# Wall settings
wall_width = 50
wall_spacing = 200

# Updated variable to track walls after passing
left_wall = WIDTH // 8  # Initial left wall
right_wall = WIDTH // 2  # Initial right wall where the first wall is

# Camera offset to keep the ball in sight
camera_offset = 0
camera_speed = 0.8  # Speed of camera scrolling

# Transition flag
is_transitioning = False
target_camera_offset = 0

# Ball height transition variables
height_increment_speed = 0.8  # Speed at which the ball rises to the target height
target_ball_height = HEIGHT  # Target ball height for rising

# Timer for sound duration
sound_timer = None  # Timer to keep track of sound play duration
sound_duration = 3000  # Duration to play sound in milliseconds

def is_ball_in_hole(ball_y, note):
    """ Check if the ball's y position is within the hole for the current note. """
    hole_center_y = note_heights[note]
    hole_radius = 40  # Assuming the hole has a radius of 40 pixels
    return hole_center_y - hole_radius <= ball_y <= hole_center_y + hole_radius

def reset_game():
    """ Reset all game variables to restart the game. """
    global ball_x, ball_y, ball_direction, current_note, user_note, walls_passed, left_wall, right_wall, score, camera_offset, is_transitioning, target_camera_offset, target_ball_height, sound_timer
    ball_x, ball_y = WIDTH // 8, HEIGHT  # Reset ball position to the bottom
    ball_direction = 1
    current_note = random.choice(NOTES)
    user_note = ''
    walls_passed = 0
    left_wall = WIDTH // 8
    right_wall = WIDTH // 2
    score = 0
    camera_offset = 0  # Reset the camera
    is_transitioning = False
    target_camera_offset = 0
    target_ball_height = HEIGHT  # Reset target ball height
    sound_timer = None  # Reset sound timer

def game_loop():
    global current_note, user_note, score, ball_x, ball_y, ball_direction, left_wall, right_wall, camera_offset, walls_passed, is_transitioning, target_camera_offset, target_ball_height, sound_timer

    running = True
    while running:
        screen.fill(WHITE)

        # Draw walls
        for i in range(len(NOTES)):
            wall_x = WIDTH // 2 + i * wall_spacing - camera_offset  # Adjust wall position by camera offset
            pygame.draw.rect(screen, BLACK, (wall_x, 0, wall_width, HEIGHT))  # Draw the wall

        # Calculate the index of the current wall based on walls_passed
        current_wall_index = walls_passed % len(NOTES)
        current_wall_x = WIDTH // 2 + current_wall_index * wall_spacing - camera_offset  # Calculate the x position of the current wall

        # Draw the hole for the current note at the current wall
        pygame.draw.circle(screen, WHITE, (current_wall_x + wall_width // 2, note_heights[current_note]), 20)  # Draw the hole at the correct height

        # Draw the ball
        pygame.draw.circle(screen, BLUE, (ball_x - camera_offset, int(ball_y)), ball_radius)

        # Move the ball
        ball_x += ball_speed_x * ball_direction

        # Check if the ball reaches the right wall
        if ball_x >= right_wall and ball_direction > 0:  # Ball at the wall moving right
            if is_ball_in_hole(ball_y, current_note):  # Check if the ball is in the correct hole
                if user_note == current_note:  # Check if the user input matches the current note
                    # Ball passes through the hole, shift walls
                    left_wall = right_wall
                    right_wall = right_wall + wall_spacing
                    ball_direction = -1  # Reverse direction
                    current_note = random.choice(NOTES)  # Generate new target note
                    walls_passed += 1  # Increase walls passed counter
                    score += 1  # Increase the score when the note is matched correctly
                    
                    # Start the camera transition
                    is_transitioning = True
                    target_camera_offset = camera_offset + wall_spacing  # New target offset

                    # Reset ball height to the bottom
                    target_ball_height = HEIGHT
                    
                    if walls_passed >= 7:
                        # Display "FINISHED" and wait 2 seconds
                        finished_text = FONT.render("FINISHED", True, ORANGE)
                        screen.blit(finished_text, (WIDTH // 2 - finished_text.get_width() // 2, HEIGHT // 2 - finished_text.get_height() // 2))
                        pygame.display.update()
                        pygame.time.wait(2000)  # Wait for 2 seconds

                        # Restart the game
                        reset_game()
                else:
                    # User note does not match the current note, ball bounces back
                    ball_direction *= -1
                    target_ball_height = HEIGHT  # Reset to bottom on wrong input
            else:
                # Ball misses the hole, bounce back
                ball_direction *= -1
                target_ball_height = HEIGHT  # Reset to bottom on wrong input

        # Check if the ball reaches the left wall
        if ball_x <= left_wall and ball_direction < 0:  # Ball at the left wall moving left
            ball_direction *= -1

        # Handle camera transition
        if is_transitioning:
            if camera_offset < target_camera_offset:
                camera_offset += camera_speed  # Increment camera offset
                if camera_offset >= target_camera_offset:
                    camera_offset = target_camera_offset  # Clamp to target value
                    is_transitioning = False  # End transition

        # Gradually increase ball height towards target height or decrease if key is released
        if ball_y > target_ball_height:
            ball_y -= height_increment_speed  # Gradually move up
        elif ball_y < target_ball_height:
            ball_y += height_increment_speed  # Gradually move down to bottom

        # Display the target note (draw this last to keep it on top)
        target_text = FONT.render(f"Sing: {current_note}", True, ORANGE)
        screen.blit(target_text, (WIDTH // 2 - target_text.get_width() // 2, 10))

        # Display score
        score_text = FONT.render(f"Score: {score}", True, BLUE)
        screen.blit(score_text, (10, 10))

        # Display the note keys
        for i, note in enumerate(NOTES):
            note_text = FONT.render(f"{note} - {i + 1}", True, ORANGE)
            screen.blit(note_text, (10, 60 + i * 40))  # Display notes on the left side

        # Display the pressed input number
        input_text = FONT.render(f"Input: {user_note}", True, ORANGE)
        screen.blit(input_text, (WIDTH // 2 - input_text.get_width() // 2, 50))

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()

            # Simulating note input using keys
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    user_note = 'Sa'
                    target_ball_height = note_heights['Sa']  # Set target height
                    sounds['Sa'].play(-1)  # Play sound indefinitely
                    sound_timer = pygame.time.get_ticks()  # Start the timer
                elif event.key == pygame.K_2:
                    user_note = 'Re'
                    target_ball_height = note_heights['Re']
                    sounds['Re'].play(-1)
                    sound_timer = pygame.time.get_ticks()
                elif event.key == pygame.K_3:
                    user_note = 'G'
                    target_ball_height = note_heights['G']
                    sounds['G'].play(-1)
                    sound_timer = pygame.time.get_ticks()
                elif event.key == pygame.K_4:
                    user_note = 'M'
                    target_ball_height = note_heights['M']
                    sounds['M'].play(-1)
                    sound_timer = pygame.time.get_ticks()
                elif event.key == pygame.K_5:
                    user_note = 'P'
                    target_ball_height = note_heights['P']
                    sounds['P'].play(-1)
                    sound_timer = pygame.time.get_ticks()
                elif event.key == pygame.K_6:
                    user_note = 'Dha'
                    target_ball_height = note_heights['Dha']
                    sounds['Dha'].play(-1)
                    sound_timer = pygame.time.get_ticks()
                elif event.key == pygame.K_7:
                    user_note = 'Ni'
                    target_ball_height = note_heights['Ni']
                    sounds['Ni'].play(-1)
                    sound_timer = pygame.time.get_ticks()

            # Clear the user note on key release
            if event.type == pygame.KEYUP:
                if event.key in (pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5, pygame.K_6, pygame.K_7):
                    user_note = ''  # Reset user input when key is released
                    for sound in sounds.values():
                        sound.stop()  # Stop all sounds when the key is released

                    # Set target ball height to the bottom when any note key is released
                    target_ball_height = HEIGHT  # Set to the bottom

            # Timer handling for sound duration
            if sound_timer is not None and pygame.time.get_ticks() - sound_timer > sound_duration:
                for sound in sounds.values():
                    sound.stop()  # Stop all sounds after the duration

    pygame.quit()

# Start the game
game_loop()
