import math
import pygame
import random
import sys
import os
import time

# Initialize Pygame
pygame.init()
try:
    pygame.mixer.init()
    SOUND_ENABLED = True
except pygame.error:
    print("Warning: Audio device not available. Running without sound.")
    SOUND_ENABLED = False

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
CYAN = (0, 255, 255)
ORANGE = (255, 165, 0)

# Game settings
PLAYER_SPEED = 5
BULLET_SPEED = 7
ENEMY_SPEED = 1
ENEMY_DROP_SPEED = 20
ENEMY_ROWS = 5
ENEMY_COLS = 10

# Power-up settings
POWERUP_CHANCE = 0.3  # 30% chance to drop power-up when enemy is killed
POWERUP_DURATION = 10  # seconds

class Star:
    def __init__(self):
        self.x = random.randint(0, SCREEN_WIDTH)
        self.y = random.randint(0, SCREEN_HEIGHT)
        self.speed = random.uniform(0.5, 3.0)
        self.brightness = random.randint(100, 255)

    def update(self):
        self.y += self.speed
        if self.y > SCREEN_HEIGHT:
            self.y = 0
            self.x = random.randint(0, SCREEN_WIDTH)

    def draw(self, screen):
        color = (self.brightness, self.brightness, self.brightness)
        pygame.draw.circle(screen, color, (int(self.x), int(self.y)), 1)

class PowerUp:
    def __init__(self, x, y, power_type):
        self.x = x
        self.y = y
        self.width = 30
        self.height = 30
        self.speed = 2
        self.power_type = power_type  # 'triple_shot', 'rapid_fire', 'shield'
        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.pulse = 0  # For visual effect

    def update(self):
        self.y += self.speed
        self.rect.y = self.y
        self.pulse += 0.2

    def draw(self, screen):
        # Pulsing effect
        pulse_size = int(5 * abs(math.cos(self.pulse)))

        if self.power_type == 'triple_shot':
            color = CYAN
            # Draw triple shot icon
            pygame.draw.circle(screen, color, (self.x + self.width // 2, self.y + self.height // 2),
                              self.width // 2 + pulse_size, 3)
            # Three lines representing triple shot
            for i in range(3):
                start_y = self.y + 5 + i * 7
                pygame.draw.line(screen, color, (self.x + 5, start_y), (self.x + 25, start_y), 2)

        elif self.power_type == 'rapid_fire':
            color = ORANGE
            # Draw rapid fire icon
            pygame.draw.circle(screen, color, (self.x + self.width // 2, self.y + self.height // 2),
                              self.width // 2 + pulse_size, 3)
            # Lightning bolt shape
            points = [(self.x + 10, self.y + 5), (self.x + 15, self.y + 12), (self.x + 12, self.y + 15),
                      (self.x + 18, self.y + 25), (self.x + 13, self.y + 18), (self.x + 16, self.y + 15)]
            pygame.draw.polygon(screen, color, points)

        elif self.power_type == 'shield':
            color = PURPLE
            # Draw shield icon
            pygame.draw.circle(screen, color, (self.x + self.width // 2, self.y + self.height // 2),
                              self.width // 2 + pulse_size, 3)
            # Shield shape
            pygame.draw.arc(screen, color, (self.x + 5, self.y + 5, 20, 20), 0, 3.14, 3)

    def is_off_screen(self):
        return self.y > SCREEN_HEIGHT

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 50
        self.height = 30
        self.speed = PLAYER_SPEED
        self.rect = pygame.Rect(x, y, self.width, self.height)

        # Power-up states
        self.triple_shot = False
        self.rapid_fire = False
        self.shield = False
        self.power_up_end_time = 0
        self.last_shot_time = 0
        self.shot_cooldown = 0.2  # Normal cooldown between shots

    def move_left(self):
        if self.x > 0:
            self.x -= self.speed
            self.rect.x = self.x

    def move_right(self):
        if self.x < SCREEN_WIDTH - self.width:
            self.x += self.speed
            self.rect.x = self.x

    def can_shoot(self):
        current_time = time.time()
        cooldown = 0.1 if self.rapid_fire else self.shot_cooldown
        return current_time - self.last_shot_time >= cooldown

    def shoot(self):
        if not self.can_shoot():
            return []

        self.last_shot_time = time.time()
        bullets = []

        if self.triple_shot:
            # Triple shot: center, left, and right bullets
            bullets.append(Bullet(self.x + self.width // 2 - 2, self.y))
            bullets.append(Bullet(self.x + self.width // 2 - 10, self.y, angle=-0.2))
            bullets.append(Bullet(self.x + self.width // 2 + 6, self.y, angle=0.2))
        else:
            # Normal single shot
            bullets.append(Bullet(self.x + self.width // 2 - 2, self.y))

        return bullets

    def activate_power_up(self, power_type):
        self.power_up_end_time = time.time() + POWERUP_DURATION

        # Reset all power-ups first
        self.triple_shot = False
        self.rapid_fire = False
        self.shield = False

        # Activate the specific power-up
        if power_type == 'triple_shot':
            self.triple_shot = True
        elif power_type == 'rapid_fire':
            self.rapid_fire = True
        elif power_type == 'shield':
            self.shield = True

    def update_power_ups(self):
        if time.time() > self.power_up_end_time:
            self.triple_shot = False
            self.rapid_fire = False
            self.shield = False

    def draw(self, screen):
        # Draw shield effect if active
        if self.shield:
            pygame.draw.circle(screen, PURPLE,
                              (self.x + self.width // 2, self.y + self.height // 2),
                              35, 3)

        # Draw a simple spaceship shape
        points = [
            (self.x + self.width // 2, self.y),
            (self.x, self.y + self.height),
            (self.x + self.width // 4, self.y + self.height - 10),
            (self.x + 3 * self.width // 4, self.y + self.height - 10),
            (self.x + self.width, self.y + self.height)
        ]

        # Change color based on power-up
        color = GREEN
        if self.triple_shot:
            color = CYAN
        elif self.rapid_fire:
            color = ORANGE
        elif self.shield:
            color = PURPLE

        pygame.draw.polygon(screen, color, points)

class Bullet:
    def __init__(self, x, y, direction=1, angle=0):
        self.x = x
        self.y = y
        self.width = 4
        self.height = 10
        self.speed = BULLET_SPEED * direction  # direction: 1 for up, -1 for down
        self.angle = angle  # For angled shots (triple shot)
        self.rect = pygame.Rect(x, y, self.width, self.height)

    def update(self):
        self.y -= self.speed
        self.x += self.speed * self.angle  # Apply angle for triple shot
        self.rect.x = self.x
        self.rect.y = self.y

    def draw(self, screen):
        color = YELLOW if self.speed > 0 else RED
        pygame.draw.rect(screen, color, self.rect)

    def is_off_screen(self):
        return self.y < 0 or self.y > SCREEN_HEIGHT or self.x < 0 or self.x > SCREEN_WIDTH

class Enemy:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 40
        self.height = 30
        self.speed = ENEMY_SPEED
        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.direction = 1  # 1 for right, -1 for left

    def update(self):
        self.x += self.speed * self.direction
        self.rect.x = self.x

    def drop_down(self):
        self.y += ENEMY_DROP_SPEED
        self.rect.y = self.y
        self.direction *= -1  # Change direction

    def draw(self, screen):
        # Draw a simple enemy shape
        pygame.draw.rect(screen, RED, self.rect)
        # Add some details
        pygame.draw.rect(screen, WHITE, (self.x + 5, self.y + 5, 10, 10))
        pygame.draw.rect(screen, WHITE, (self.x + 25, self.y + 5, 10, 10))

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Space Invaders")
        self.clock = pygame.time.Clock()

        # Game objects
        self.player = Player(SCREEN_WIDTH // 2 - 25, SCREEN_HEIGHT - 50)
        self.bullets = []
        self.enemy_bullets = []
        self.enemies = []
        self.power_ups = []
        self.stars = []

        # Game state
        self.score = 0
        self.game_over = False
        self.victory = False
        self.font = pygame.font.Font(None, 36)
        self.big_font = pygame.font.Font(None, 72)
        self.small_font = pygame.font.Font(None, 24)

        # Create sound effects (using basic tones)
        self.create_sounds()

        # Create enemies and stars
        self.create_enemies()
        self.create_starfield()

    def create_starfield(self):
        """Create a scrolling starfield background"""
        self.stars = []
        for _ in range(100):  # 100 stars
            self.stars.append(Star())

    def create_sounds(self):
        """Create basic sound effects"""
        if not SOUND_ENABLED:
            self.shoot_sound = None
            self.hit_sound = None
            self.game_over_sound = None
            self.powerup_sound = None
            return

        try:
            # Create simple sound effects using pygame's sound generation
            self.shoot_sound = pygame.mixer.Sound(buffer=self.generate_tone(440, 0.1))
            self.hit_sound = pygame.mixer.Sound(buffer=self.generate_tone(220, 0.2))
            self.game_over_sound = pygame.mixer.Sound(buffer=self.generate_tone(110, 0.5))
            self.powerup_sound = pygame.mixer.Sound(buffer=self.generate_tone(660, 0.3))
        except:
            # If sound creation fails, create dummy sounds
            self.shoot_sound = None
            self.hit_sound = None
            self.game_over_sound = None
            self.powerup_sound = None

    def generate_tone(self, frequency, duration):
        """Generate a simple tone for sound effects"""
        if not SOUND_ENABLED:
            return None

        try:
            import numpy as np
            sample_rate = 22050
            frames = int(duration * sample_rate)
            arr = np.zeros((frames, 2))

            for i in range(frames):
                time_val = float(i) / sample_rate
                wave = 4096 * np.sin(frequency * 2 * np.pi * time_val)
                arr[i][0] = wave
                arr[i][1] = wave

            return arr.astype(np.int16)
        except ImportError:
            return None

    def create_enemies(self):
        """Create a grid of enemies"""
        self.enemies = []
        for row in range(ENEMY_ROWS):
            for col in range(ENEMY_COLS):
                x = 50 + col * 60
                y = 50 + row * 50
                self.enemies.append(Enemy(x, y))

    def handle_events(self):
        """Handle all game events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not self.game_over:
                    # Shoot bullet(s)
                    new_bullets = self.player.shoot()
                    self.bullets.extend(new_bullets)
                    if new_bullets and self.shoot_sound:
                        self.shoot_sound.play()
                elif event.key == pygame.K_r and self.game_over:
                    # Restart game
                    self.restart_game()

        return True

    def update(self):
        """Update game state"""
        if self.game_over:
            return

        # Update starfield
        for star in self.stars:
            star.update()

        # Update player power-ups
        self.player.update_power_ups()

        # Handle continuous key presses
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.player.move_left()
        if keys[pygame.K_RIGHT]:
            self.player.move_right()

        # Update bullets
        for bullet in self.bullets[:]:
            bullet.update()
            if bullet.is_off_screen():
                self.bullets.remove(bullet)

        # Update enemy bullets
        for bullet in self.enemy_bullets[:]:
            bullet.update()
            if bullet.is_off_screen():
                self.enemy_bullets.remove(bullet)

        # Update power-ups
        for power_up in self.power_ups[:]:
            power_up.update()
            if power_up.is_off_screen():
                self.power_ups.remove(power_up)

        # Update enemies
        edge_hit = False
        for enemy in self.enemies:
            enemy.update()
            if enemy.x <= 0 or enemy.x >= SCREEN_WIDTH - enemy.width:
                edge_hit = True

        # If any enemy hits the edge, all drop down
        if edge_hit:
            for enemy in self.enemies:
                enemy.drop_down()

        # Enemy shooting (random)
        if self.enemies and random.randint(1, 100) == 1:
            shooter = random.choice(self.enemies)
            bullet = Bullet(shooter.x + shooter.width // 2 - 2,
                           shooter.y + shooter.height, -1)
            self.enemy_bullets.append(bullet)

        # Check collisions
        self.check_collisions()

        # Check win/lose conditions
        if not self.enemies:
            self.victory = True
            self.game_over = True
        elif any(enemy.y + enemy.height >= self.player.y for enemy in self.enemies):
            self.game_over = True
            if self.game_over_sound:
                self.game_over_sound.play()

    def check_collisions(self):
        """Check all collision detection"""
        # Player bullets vs enemies
        for bullet in self.bullets[:]:
            for enemy in self.enemies[:]:
                if bullet.rect.colliderect(enemy.rect):
                    self.bullets.remove(bullet)
                    self.enemies.remove(enemy)
                    self.score += 10
                    if self.hit_sound:
                        self.hit_sound.play()

                    # Chance to drop power-up
                    if random.random() < POWERUP_CHANCE:
                        power_types = ['triple_shot', 'rapid_fire', 'shield']
                        power_type = random.choice(power_types)
                        power_up = PowerUp(enemy.x, enemy.y, power_type)
                        self.power_ups.append(power_up)

                    break

        # Enemy bullets vs player (check shield)
        for bullet in self.enemy_bullets[:]:
            if bullet.rect.colliderect(self.player.rect):
                if self.player.shield:
                    # Shield blocks the bullet
                    self.enemy_bullets.remove(bullet)
                    if self.hit_sound:
                        self.hit_sound.play()
                else:
                    # Player is hit
                    self.game_over = True
                    if self.game_over_sound:
                        self.game_over_sound.play()
                break

        # Player vs power-ups
        for power_up in self.power_ups[:]:
            if power_up.rect.colliderect(self.player.rect):
                self.power_ups.remove(power_up)
                self.player.activate_power_up(power_up.power_type)
                if self.powerup_sound:
                    self.powerup_sound.play()

    def draw(self):
        """Draw all game objects"""
        self.screen.fill(BLACK)

        # Draw starfield
        for star in self.stars:
            star.draw(self.screen)

        if not self.game_over:
            # Draw game objects
            self.player.draw(self.screen)

            for bullet in self.bullets:
                bullet.draw(self.screen)

            for bullet in self.enemy_bullets:
                bullet.draw(self.screen)

            for enemy in self.enemies:
                enemy.draw(self.screen)

            for power_up in self.power_ups:
                power_up.draw(self.screen)

        # Draw UI
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (10, 10))

        # Draw power-up status
        if self.player.triple_shot or self.player.rapid_fire or self.player.shield:
            remaining_time = max(0, self.player.power_up_end_time - time.time())
            if self.player.triple_shot:
                power_text = self.small_font.render(f"TRIPLE SHOT: {remaining_time:.1f}s", True, CYAN)
            elif self.player.rapid_fire:
                power_text = self.small_font.render(f"RAPID FIRE: {remaining_time:.1f}s", True, ORANGE)
            elif self.player.shield:
                power_text = self.small_font.render(f"SHIELD: {remaining_time:.1f}s", True, PURPLE)

            self.screen.blit(power_text, (10, 50))

        # Draw game over screen
        if self.game_over:
            if self.victory:
                game_over_text = self.big_font.render("VICTORY!", True, GREEN)
            else:
                game_over_text = self.big_font.render("GAME OVER", True, RED)

            text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            self.screen.blit(game_over_text, text_rect)

            restart_text = self.font.render("Press R to restart", True, WHITE)
            restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
            self.screen.blit(restart_text, restart_rect)

        pygame.display.flip()

    def restart_game(self):
        """Restart the game"""
        self.player = Player(SCREEN_WIDTH // 2 - 25, SCREEN_HEIGHT - 50)
        self.bullets = []
        self.enemy_bullets = []
        self.power_ups = []
        self.score = 0
        self.game_over = False
        self.victory = False
        self.create_enemies()
        self.create_starfield()

    def run(self):
        """Main game loop"""
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(60)  # 60 FPS

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    # Check if numpy is available for sound generation
    try:
        import numpy as np
    except ImportError:
        print("Note: numpy not found. Sound effects will be disabled.")
        print("Install numpy with: pip install numpy")

    print("Space Invaders Game - Enhanced Edition")
    print("New Features:")
    print("- Scrolling starfield background")
    print("- Power-ups: Triple Shot, Rapid Fire, Shield")
    print("- Power-ups last 10 seconds")
    print("- 30% chance for power-up when enemy is destroyed")
    print()
    print("Controls:")
    print("- Left/Right Arrow Keys: Move")
    print("- Spacebar: Shoot")
    print("- R: Restart (when game over)")
    print()

    game = Game()
    game.run()