import pygame, random, json
from game_scripts.nll.utils import ASSETS_PATH, DATA_PATH, get_image, draw_text_wave, displayRotatingText

pygame.init()

FPS = 60
W, H = 1313, 705
screen = pygame.display.set_mode((W, H), pygame.FULLSCREEN | pygame.SCALED)
pygame.display.set_caption("Mini Game")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Comic Sans MS", 40)
bigfont = pygame.font.SysFont("Comic Sans MS", 60)
bg_img = pygame.image.load(f"{ASSETS_PATH}/images/mini/bg.png").convert_alpha()


class Particle:
    def __init__(self, x, y, color, size, speed):
        self.x = x
        self.y = y
        self.color = color
        self.size = size
        self.speed = speed
        self.alpha = 255

    def update(self):
        self.y += self.speed
        self.x += random.randint(-2, 2)
        self.alpha -= 5
        if self.alpha <= 0:
            self.alpha = 0

    def draw(self, surface):
        pygame.draw.circle(surface, (*self.color, self.alpha), (self.x, self.y), self.size)

class ParticleManager:
    def __init__(self):
        self.particles = []

    def create_particles(self, x, y):
        for _ in range(20):
            size = random.randint(2, 4)
            speed = random.randint(1, 3)
            color = (random.randint(150, 255), random.randint(100, 150), random.randint(50, 100))
            self.particles.append(Particle(x, y, color, size, speed))

    def update(self):
        for particle in self.particles[:]:
            particle.update()
            if particle.alpha == 0:
                self.particles.remove(particle)

    def draw(self, surface):
        for particle in self.particles:
            particle.draw(surface)


class Player:
    def __init__(self, x, y):
        self.idle_img = pygame.image.load(f"{ASSETS_PATH}/images/player/0/idle.png").convert_alpha()
        self.dead_img = pygame.image.load(f"{ASSETS_PATH}/images/player/0/dead.png").convert_alpha()
        self.run_sheet = pygame.image.load(f"{ASSETS_PATH}/images/player/0/run.png").convert_alpha()
        self.run_img = [get_image(self.run_sheet, n, 144, 144, 144*2, "black") for n in range(0, 5)]
        self.rect = self.idle_img.get_rect(center=(x, y))
        self.collider = pygame.Rect(self.rect.x + 55, self.rect.y + 55, self.rect.width - 110, self.rect.height - 110)
        self.box = [80, W - 120]
        self.direction = [1, 0, 0]  # [idle, left, right]
        self.steps = 0
        self.speed = 4
        self.lifes = 3

        self.gravity = 1.8
        self.velocity_y = 0
        self.is_jumping = False
        self.jump_velocity = -20

        self.particle_manager = ParticleManager()

    def control(self):
        pressed = pygame.key.get_pressed()
        if (pressed[pygame.K_a] or pressed[pygame.K_LEFT]) and self.collider.x > self.box[0]:
            self.collider.x -= self.speed
            self.direction = [0, 1, 0]
            self.steps += 1
        elif (pressed[pygame.K_d] or pressed[pygame.K_RIGHT]) and self.collider.x < self.box[1]:
            self.collider.x += self.speed
            self.direction = [0, 0, 1]
            self.steps += 1
        else:
            self.direction = [1, 0, 0]
            self.steps = 0

        self.steps %= 20

    def apply_gravity(self, ground_y):
        self.velocity_y += self.gravity
        self.collider.y += self.velocity_y

        if self.collider.bottom >= ground_y:
            self.collider.bottom = ground_y
            self.velocity_y = 0
            if self.is_jumping:
                self.is_jumping = False
                self.particle_manager.create_particles(self.rect.centerx, self.rect.centery)

        self.rect.center = self.collider.center

    def jump(self):
        if self.collider.bottom >= ground_y and not self.is_jumping:
            self.velocity_y = self.jump_velocity
            self.is_jumping = True
            self.particle_manager.create_particles(self.rect.centerx, self.rect.centery)

    def draw(self):
        if not self.lifes <= 0:
            if self.direction[0]:
                screen.blit(self.idle_img, self.rect)
            elif self.direction[1]:
                screen.blit(self.run_img[self.steps//5], self.rect)
            elif self.direction[2]:
                screen.blit(pygame.transform.flip(self.run_img[self.steps//5], True, False).convert_alpha(), self.rect)
            self.control()
        else:
            screen.blit(self.dead_img, self.rect)
        self.apply_gravity(ground_y)
        pygame.draw.rect(screen, "green", (self.collider.x - 12, self.collider.y - 25, 35*self.lifes/2, 15))
        self.particle_manager.update()
        self.particle_manager.draw(screen)


class Enemy:
    def __init__(self, x, y):
        self.idle_img = pygame.transform.flip(pygame.image.load(f"{ASSETS_PATH}/images/enemies/4/idle/1.png"), True, False).convert_alpha()
        self.dead_img = pygame.transform.flip(pygame.image.load(f"{ASSETS_PATH}/images/enemies/4/die/19.png"), True, False).convert_alpha()
        self.run_img = [pygame.image.load(f"{ASSETS_PATH}/images/enemies/4/run/{n}.png").convert_alpha() for n in range(0, 20)]
        self.rect = self.idle_img.get_rect(center=(x, y))
        self.collider = pygame.Rect(self.rect.x + 55, self.rect.y + 55, self.rect.width - 110, self.rect.height - 110)
        self.direction = [1, 0, 0]  # [idle, left, right]
        self.steps = 0
        self.speed = 3
        self.lifes = 3

    def follow(self, player):
        if self.lifes > 0:
            if not self.collider.colliderect(player.collider):
                if player.collider.x > self.collider.x:
                    self.rect.x += self.speed
                    self.direction = [0, 0, 1]
                    self.steps += 1
                if player.collider.x < self.collider.x:
                    self.rect.x -= self.speed
                    self.direction = [0, 1, 0]
                    self.steps += 1
            else:
                self.direction = [1, 0, 0]
                self.steps = 0
    
        self.steps %= 100

        self.collider = pygame.Rect(self.rect.x + 120, self.rect.y + 55, self.rect.width - 220, self.rect.height -50)
        self.draw()

    def draw(self):
        if self.lifes > 0:
            if self.direction[0]:
                screen.blit(self.idle_img, self.rect)
            if self.direction[1]:
                screen.blit(pygame.transform.flip(self.run_img[self.steps//5], True, False).convert_alpha(), self.rect)
            if self.direction[2]:
                screen.blit(self.run_img[self.steps//5], self.rect)
        else:
            screen.blit(self.dead_img, self.rect)
        pygame.draw.rect(screen, "green", (self.collider.x, self.collider.y, 50*self.lifes/2, 25))
        #pygame.draw.rect(screen, "green", self.collider, 3)

enemy = Enemy(500, 500)
player = Player(100, 0)
ground_y = 600
light_radius = 155
light_radius_direction = 1
time = 0

def map_draw():
    surface = pygame.Surface((W, H), pygame.SRCALPHA)
    surface.fill((0, 0, 0, 255))
    
    global light_radius, light_radius_direction
    light_radius += light_radius_direction * 0.2
    if light_radius > 160 or light_radius < 150:
        light_radius_direction *= -1

    circle_center = player.rect.center
    fade_steps = 50

    for i in range(fade_steps):
        alpha = int(255 * (1 - (i / fade_steps)))
        color = (0, 0, 0, alpha)
        pygame.draw.circle(surface, color, circle_center, light_radius - i)

    player.draw()
    screen.blit(surface, (0, 0))
    draw_text_wave(screen, "Esc", font, (50, 20), (255, 255, 255), pygame.time.get_ticks(), 3, 1)

def check_collision():
    global time
    if enemy.lifes > 0:
        if player.collider.colliderect(enemy.collider):
            time += 1
            if time == 2*60 - 5:
                player.lifes -= 1
                time = 0
        else:
            if time > 60:
                enemy.lifes -= 1
                time = 0
            else:
                time = 0
        displayRotatingText(screen, str(time//40), (screen.get_width()/2, 50), "red", bigfont, pygame.time.get_ticks(), 5)
    else:
        displayRotatingText(screen, "You Win", (screen.get_width()/2, 50), "red", bigfont, pygame.time.get_ticks(), speed=0.002)

def draw_coins(allready_won):
    if enemy.lifes <= 0:
        if not allready_won:
            displayRotatingText(screen, "+20 Coins!", (screen.get_width()/2, 180), "green", font, pygame.time.get_ticks(), 5, 0.001)

def load_start_data():
    with open(f"{DATA_PATH}/mini_game.json", "r") as file:
        data = json.load(file)

    return data["won"]

def load_data():
    with open(f"{DATA_PATH}/mini_game.json", "r") as file:
        data = json.load(file)
    with open(f"{DATA_PATH}/coins.json", "r") as file:
        coins = json.load(file)

    return data, coins

bonus = 20
def give_money(data, coins):
    if enemy.lifes <= 0:
        if not data["won"]:
            with open(f"{DATA_PATH}/mini_game.json", "w") as file:
                json.dump({"won": True}, file)
            load_data()
            with open(f"{DATA_PATH}/coins.json", "w") as file:
                json.dump({"Coins": coins["Coins"] + bonus}, file)
        
def main():
    start_data = load_start_data()
    data, coins = load_data()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if player.lifes > 0:
                    if event.key == pygame.K_SPACE or event.key == pygame.K_w or event.key == pygame.K_UP:
                        player.jump()

        screen.blit(bg_img, (0, 0))
        enemy.follow(player)
        map_draw()
        check_collision()
        give_money(data, coins)
        draw_coins(start_data)
        pygame.display.update()
        clock.tick(FPS)