import pygame
import random
import sys
import cv2
import mediapipe as mp

pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

# Game variables
GRAVITY = 0.25
BIRD_FLAP_STRENGTH = -6
PIPE_GAP_LEVEL1 = 300  # Initial gap
PIPE_GAP_LEVEL2 = 200  # Reduced gap for level 2
PIPE_WIDTH = 80
PIPE_SPACING = 300  # Horizontal distance between pipes
PIPE_SPEED_LEVEL1 = 5  # Initial speed
PIPE_SPEED_LEVEL2 = 8  # Increased speed for level 2

# Initialize screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Flappy Bird")

clock = pygame.time.Clock()

# Load the background images
background_image_level1 = pygame.image.load("background.png")
background_image_level1 = pygame.transform.scale(background_image_level1, (SCREEN_WIDTH, SCREEN_HEIGHT))
background_image_level2 = pygame.image.load("background2.png")
background_image_level2 = pygame.transform.scale(background_image_level2, (SCREEN_WIDTH, SCREEN_HEIGHT))

# Bird image
bird_img_level1 = pygame.image.load("bird.png")
bird_img_level1 = pygame.transform.scale(bird_img_level1, (36, 24))
bird_img_level2 = pygame.image.load("bird.png")
bird_img_level2 = pygame.transform.scale(bird_img_level2, (36, 24))

# Game fonts
font = pygame.font.SysFont(None, 48)

# Bird class
class Bird:
    def _init_(self):
        self.x = 100
        self.y = 200
        self.vel_y = 0
        self.image = bird_img_level1
        self.rect = self.image.get_rect(center=(self.x, self.y))

    def flap(self):
        self.vel_y = BIRD_FLAP_STRENGTH

    def update(self):
        self.vel_y += GRAVITY
        self.rect.centery += int(self.vel_y)

    def draw(self, screen):
        screen.blit(self.image, self.rect.topleft)

    def check_bounds(self):
        # Check if the bird is out of screen bounds
        if self.rect.top <= 0 or self.rect.bottom >= SCREEN_HEIGHT:
            return True
        return False

# Pipe class
class Pipe:
    def _init_(self, x, gap, speed):
        self.x = x
        self.height = random.randint(150, SCREEN_HEIGHT - 150)
        self.gap = gap
        self.speed = speed
        self.top_rect = pygame.Rect(self.x, 0, PIPE_WIDTH, self.height)
        self.bottom_rect = pygame.Rect(self.x, self.height + self.gap, PIPE_WIDTH, SCREEN_HEIGHT)
        self.passed = False  # Flag to track if bird has passed this pipe

    def update(self):
        self.x -= self.speed
        self.top_rect.x = self.x
        self.bottom_rect.x = self.x

    def draw(self, screen):
        pygame.draw.rect(screen, BLACK, self.top_rect)
        pygame.draw.rect(screen, BLACK, self.bottom_rect)

    def off_screen(self):
        return self.x < -PIPE_WIDTH

def check_collision(bird, pipes):
    bird_rect = bird.rect
    for pipe in pipes:
        if bird_rect.colliderect(pipe.top_rect) or bird_rect.colliderect(pipe.bottom_rect):
            return True
    return False

def display_text(text, size, color, position):
    font = pygame.font.SysFont(None, size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=position)
    screen.blit(text_surface, text_rect)

def main_menu():
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands()
    cap = cv2.VideoCapture(0)

    selected_option = 0  # 0: Play, 1: Exit
    options = ["Play", "Exit"]

    running = True
    while running:
        screen.fill(WHITE)
        display_text("Flappy Bird", 72, BLACK, (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4))

        for i, option in enumerate(options):
            color = RED if i == selected_option else BLACK
            display_text(option, 48, color, (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + i * 60))

        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb_frame)

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                if hand_landmarks.landmark[8].y < hand_landmarks.landmark[6].y:  # Index finger up
                    if hand_landmarks.landmark[8].x < hand_landmarks.landmark[5].x:  # Move left
                        selected_option = (selected_option - 1) % 2
                    elif hand_landmarks.landmark[8].x > hand_landmarks.landmark[5].x:  # Move right
                        selected_option = (selected_option + 1) % 2

                # Check for gesture to select the option
                if hand_landmarks.landmark[4].y < hand_landmarks.landmark[3].y:  # Thumb up
                    if selected_option == 0:
                        cap.release()
                        cv2.destroyAllWindows()
                        main()
                    elif selected_option == 1:
                        running = False

        # Display camera feed (optional, for debugging)
        cv2.imshow("Camera Feed", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        pygame.display.flip()
        clock.tick(30)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if selected_option == 0:
                        cap.release()
                        cv2.destroyAllWindows()
                        main()
                    elif selected_option == 1:
                        running = False

    cap.release()
    cv2.destroyAllWindows()
    pygame.quit()
    sys.exit()

def main():
    # Initialize game objects
    bird = Bird()
    pipes = [Pipe(SCREEN_WIDTH + PIPE_SPACING, PIPE_GAP_LEVEL1, PIPE_SPEED_LEVEL1)]
    score = 0
    level = 1

    # Initialize MediaPipe for hand detection
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands()
    cap = cv2.VideoCapture(0)

    running = True
    while running:
        # Update background and bird image based on level
        if level == 1:
            background_image = background_image_level1
            bird.image = bird_img_level1
            pipe_gap = PIPE_GAP_LEVEL1
            pipe_speed = PIPE_SPEED_LEVEL1
        elif level == 2:
            background_image = background_image_level2
            bird.image = bird_img_level2
            pipe_gap = PIPE_GAP_LEVEL2
            pipe_speed = PIPE_SPEED_LEVEL2

        screen.blit(background_image, (0, 0))

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    bird.flap()

        # Update objects
        bird.update()

        for pipe in pipes[:]:
            pipe.update()
            pipe.draw(screen)

            # Check if bird passes the pipe
            if not pipe.passed and pipe.top_rect.right < bird.rect.centerx:
                pipe.passed = True
                score += 1

            # Check for collision with pipes
            if check_collision(bird, [pipe]):
                running = False

            if pipe.off_screen():
                pipes.remove(pipe)
                pipes.append(Pipe(SCREEN_WIDTH + PIPE_SPACING, pipe_gap, pipe_speed))

        # Check for collision with bounds
        if bird.check_bounds():
            running = False

        bird.draw(screen)

        # Display score
        score_text = font.render(f"Score: {score}", True, BLACK)
        screen.blit(score_text, (10, 10))

        # Check for level up
        if score == 1 and level == 1:
            level = 2

        # Gesture recognition using OpenCV and MediaPipe
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb_frame)

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                if hand_landmarks.landmark[8].y < hand_landmarks.landmark[6].y:  # Check if index finger is up
                    bird.flap()

        # Display camera feed (optional, for debugging)
        cv2.imshow("Camera Feed", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        pygame.display.flip()
        clock.tick(30)

    # Game over screen
    game_over_text = font.render("Game Over", True, RED)
    game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
    screen.blit(game_over_text, game_over_rect)
    final_score_text = font.render(f"Final Score: {score}", True, BLACK)
    final_score_rect = final_score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
    screen.blit(final_score_text, final_score_rect)
    pygame.display.flip()

    # Wait for a few seconds before exiting
    pygame.time.wait(3000)

    cap.release()
    cv2.destroyAllWindows()
    pygame.quit()
    sys.exit()

if _name_ == "_main_":
    main_menu()
