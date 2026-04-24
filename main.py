import asyncio
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
POWERUP_CHANCE = 0.3
POWERUP_DURATION = 10

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
        self.power_type = power_type
        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.pulse = 0

    def update(self):
        self.y += self.speed
        self.rect.y = self.y
        self.pulse += 0.2

    def draw(self, screen):
        pulse_size = int(5 * abs(math.cos(self.pulse)))
        if self.power_type == 'triple_shot':
            color = CYAN
            pygame.draw.circle(screen, color, (self.x + self.width // 2, self.y + self.height // 2), self.width // 2 + pulse_size, 3)
        elif self.power_type == 'rapid_fire':
            color = ORANGE
            pygame.draw.circle(screen, color, (self.x + self.width // 2, self.y + self.height // 2), self.width // 2 + pulse_size, 3)
        elif self.power_type == 'shield':
            color = PURPLE
            pygame.draw.circle(screen, color, (self.x + self.width // 2, self.y + self.height // 2), self.width // 2 + pulse_size, 3)

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
        self.triple_shot = False
        self.rapid_fire = False
        self.shield = False
        self.power_up_end_time = 0
        self.last_shot_time = 0
        self.shot_cooldown = 0.2

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
            bullets.append(Bullet(self.x + self.width // 2 - 2, self.y))
            bullets.append(Bullet(self.x + self.width // 2 - 10, self.y, angle=-0.2))
            bullets.append(Bullet(self.x + self.width // 2 + 6, self.y, angle=0.2))
        else:
            bullets.append(Bullet(self.x + self.width // 2 - 2, self.y))
        return bullets

    def activate_power_up(self, power_type):
        self.power_up_end_time = time.time() + POWERUP_DURATION
        self.triple_shot = False
        self.rapid_fire = False
        self.shield = False
        if power_type == 'triple_shot': self.triple_shot = True
        elif power_type == 'rapid_fire': self.rapid_fire = True
        elif power_type == 'shield': self.shield = True

    def update_power_ups(self):
        if time.time() > self.power_up_end_time:
            self.triple_shot = self.rapid_fire = self.shield = False

    def draw(self, screen):
        if self.shield:
            pygame.draw.circle(screen, PURPLE, (self.x + self.width // 2, self.y + self.height // 2), 35, 3)
        color = CYAN if self.triple_shot else ORANGE if self.rapid_fire else PURPLE if self.shield else GREEN
        points = [(self.x + self.width // 2, self.y), (self.x, self.y + self.height), (self.x + self.width // 4, self.y + self.height - 10), (self.x + 3 * self.width // 4, self.y + self.height - 10), (self.x + self.width, self.y + self.height)]
        pygame.draw.polygon(screen, color, points)

class Bullet:
    def __init__(self, x, y, direction=1, angle=0):
        self.x = x
        self.y = y
        self.width = 4
        self.height = 10
        self.speed = BULLET_SPEED * direction
        self.angle = angle
        self.rect = pygame.Rect(x, y, self.width, self.height)

    def update(self):
        self.y -= self.speed
        self.x += self.speed * self.angle
        self.rect.x, self.rect.y = self.x, self.y

    def draw(self, screen):
        color = YELLOW if self.speed > 0 else RED
        pygame.draw.rect(screen, color, self.rect)

    def is_off_screen(self):
        return self.y < 0 or self.y > SCREEN_HEIGHT or self.x < 0 or self.x > SCREEN_WIDTH

class Enemy:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.width, self.height = 40, 30
        self.speed = ENEMY_SPEED
        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.direction = 1

    def update(self):
        self.x += self.speed * self.direction
        self.rect.x = self.x

    def drop_down(self):
        self.y += ENEMY_DROP_SPEED
        self.rect.y = self.y
        self.direction *= -1

    def draw(self, screen):
        pygame.draw.rect(screen, RED, self.rect)
        pygame.draw.rect(screen, WHITE, (self.x + 5, self.y + 5, 10, 10))
        pygame.draw.rect(screen, WHITE, (self.x + 25, self.y + 5, 10, 10))

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Space Invaders Web")
        self.clock = pygame.time.Clock()
        self.player = Player(SCREEN_WIDTH // 2 - 25, SCREEN_HEIGHT - 50)
        self.bullets, self.enemy_bullets, self.enemies, self.power_ups, self.stars = [], [], [], [], []
        self.score = 0
        self.game_over = self.victory = False
        self.font = pygame.font.SysFont(None, 36)
        self.big_font = pygame.font.SysFont(None, 72)
        self.small_font = pygame.font.SysFont(None, 24)
        self.create_sounds()
        self.create_enemies()
        self.create_starfield()

    def create_starfield(self):
        self.stars = [Star() for _ in range(100)]

    def create_sounds(self):
        self.shoot_sound = self.hit_sound = self.game_over_sound = self.powerup_sound = None

    def create_enemies(self):
        for row in range(ENEMY_ROWS):
            for col in range(ENEMY_COLS):
                self.enemies.append(Enemy(50 + col * 60, 50 + row * 50))

    def update(self):
        if self.game_over: return
        for star in self.stars: star.update()
        self.player.update_power_ups()
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]: self.player.move_left()
        if keys[pygame.K_RIGHT]: self.player.move_right()

        for b in self.bullets[:]:
            b.update()
            if b.is_off_screen(): self.bullets.remove(b)
        for b in self.enemy_bullets[:]:
            b.update()
            if b.is_off_screen(): self.enemy_bullets.remove(b)
        for p in self.power_ups[:]:
            p.update()
            if p.is_off_screen(): self.power_ups.remove(p)

        edge_hit = any(e.x <= 0 or e.x >= SCREEN_WIDTH - e.width for e in self.enemies)
        if edge_hit:
            for e in self.enemies: e.drop_down()
        for e in self.enemies: e.update()

        if self.enemies and random.randint(1, 100) == 1:
            s = random.choice(self.enemies)
            self.enemy_bullets.append(Bullet(s.x + s.width // 2 - 2, s.y + s.height, -1))

        self.check_collisions()
        if not self.enemies: self.victory = self.game_over = True
        elif any(e.y + e.height >= self.player.y for e in self.enemies): self.game_over = True

    def check_collisions(self):
        for b in self.bullets[:]:
            for e in self.enemies[:]:
                if b.rect.colliderect(e.rect):
                    if b in self.bullets: self.bullets.remove(b)
                    self.enemies.remove(e)
                    self.score += 10
                    if random.random() < POWERUP_CHANCE:
                        self.power_ups.append(PowerUp(e.x, e.y, random.choice(['triple_shot', 'rapid_fire', 'shield'])))
                    break

        for b in self.enemy_bullets[:]:
            if b.rect.colliderect(self.player.rect):
                if self.player.shield: self.enemy_bullets.remove(b)
                else: self.game_over = True
                break

        for p in self.power_ups[:]:
            if p.rect.colliderect(self.player.rect):
                self.power_ups.remove(p)
                self.player.activate_power_up(p.power_type)

    def draw(self):
        self.screen.fill(BLACK)
        for s in self.stars: s.draw(self.screen)
        if not self.game_over:
            self.player.draw(self.screen)
            for b in self.bullets: b.draw(self.screen)
            for b in self.enemy_bullets: b.draw(self.screen)
            for e in self.enemies: e.draw(self.screen)
            for p in self.power_ups: p.draw(self.screen)

        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (10, 10))

        if self.game_over:
            msg = "VICTORY!" if self.victory else "GAME OVER"
            color = GREEN if self.victory else RED
            text = self.big_font.render(msg, True, color)
            self.screen.blit(text, text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)))
            retry = self.font.render("Press R to restart", True, WHITE)
            self.screen.blit(retry, retry.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 60)))
        pygame.display.flip()

    def restart(self):
        self.__init__()

async def main():
    game = Game()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not game.game_over:
                    game.bullets.extend(game.player.shoot())
                if event.key == pygame.K_r and game.game_over:
                    game.restart()

        game.update()
        game.draw()
        await asyncio.sleep(0) # Critical for web deployment
        game.clock.tick(60)
    pygame.quit()

if __name__ == "__main__":
    asyncio.run(main())
