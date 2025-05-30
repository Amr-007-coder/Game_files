from utils import *

class Enemy:
    _image_cache = {}
    teleport_imgs = None
    def __init__(self, screen, x, y):
        self.screen = screen
        self.rect = pygame.Rect(x, y, 50, 50)
        self._init_imageLoad()
        self._init_stateVariables()
        self._init_attackVariables()
        self._init_animationVariables()
        self.load_images("Easy")

    def _init_attackVariables(self):
        self.lifes = 3
        self.lifebox_collider = pygame.Rect(self.rect.centerx, self.rect.centery, self.rect.width, self.rect.height)
        self.speed = 3
        self.attack_radius = 300

    def _init_animationVariables(self):
        self.moveTimer = 0
        self.attackTimer = 0
        self.dieTimer = 0
        self.removeTimer = 200
        self.activate_tel_timer = 800
        self.teleportTimer = 0
        self.flip = False

    def _init_stateVariables(self):
        self.activated = False
        self.first_teleport = False

    def _init_imageLoad(self):
        Enemy.teleport_imgs = [
            pygame.transform.scale(
                pygame.image.load(f"{ASSETS_PATH}/images/enemies/teleport/{n}.png"), 
                (250, 90)
            ).convert_alpha() 
            for n in range(0, 12)
        ]

    def _add_missingImages(self, skin_num):
        Enemy._image_cache[skin_num] = {
            'idle': [
                pygame.transform.scale(
                    pygame.image.load(f"{ASSETS_PATH}/images/enemies/{skin_num}/idle/{n}.png"), 
                    (96, 90)
                ).convert_alpha() 
                for n in range(0, 20)
            ],
            'run': [
                pygame.transform.scale(
                    pygame.image.load(f"{ASSETS_PATH}/images/enemies/{skin_num}/run/{n}.png"), 
                    (96, 90)
                ).convert_alpha() 
                for n in range(0, 20)
            ],
            'attack': [
                pygame.transform.scale(
                    pygame.image.load(f"{ASSETS_PATH}/images/enemies/{skin_num}/attack/{n}.png"), 
                    (96, 90)
                ).convert_alpha() 
                for n in range(0, 20)
            ],
            'die': [
                pygame.transform.scale(
                    pygame.image.load(f"{ASSETS_PATH}/images/enemies/{skin_num}/die/{n}.png"), 
                    (96, 90)
                ).convert_alpha() 
                for n in range(0, 20)
            ]
        }

    def load_images(self, lvl):
        if lvl == "Easy":
            skin_num = random.randint(0, 80)
            if skin_num == 0: skin_num = 1
            if skin_num >= 10: skin_num = 1
            if skin_num > 5 and skin_num <= 10: self.lifes = skin_num -1.5

        elif lvl == "Medium":
            skin_num = random.randint(0, 80)
            if skin_num == 0: skin_num = 9
            if skin_num >= 10: skin_num = 9
            if skin_num > 5 and skin_num <= 10: self.lifes = skin_num -1.5

        elif lvl == "Hard":
            skin_num = 9
            self.lifes = skin_num

        if skin_num not in Enemy._image_cache:
            self._add_missingImages(skin_num)
        
        cached = Enemy._image_cache[skin_num]
        self.idle_img = cached['idle']
        self.run_img = cached['run']
        self.attack_img = cached['attack']
        self.die_img = cached['die']
        self.teleport_imgs = Enemy.teleport_imgs

    def reset(self, difficulty):
        self.first_teleport = False
        self.removeTimer = 200
        self.activate_tel_timer = 800
        self.teleportTimer = 0
        self.dieTimer = 0
        if self.lifes <= 0:
            self.lifes = 3 if difficulty == "Easy" else 9
            if difficulty == "Medium":
                self.lifes = 6
        self.moveTimer = 0
        self.attackTimer = 0

    def teleport(self, x, y, difficulty):
        if self.teleportTimer < 90:
            self.teleportTimer += 2.5
            self.screen.blit(self.teleport_imgs[round(self.teleportTimer*0.12)], (self.rect.left - 78, self.rect.top + 40))
            return False
        else:
            self.teleportTimer = 90
            if not self.first_teleport:
                self.load_images(difficulty)
                self.first_teleport = True
            self.rect.x = x
            self.rect.y = y
            return True

    def idle(self):
        self.moveTimer += 1
        self.moveTimer %= 80
        self.screen.blit(self.idle_img[self.moveTimer//4], self.rect)

    def move(self, delta_x, delta_y, player_rect):
        self.rect.move_ip(delta_x, delta_y)
        if not self.rect.colliderect(player_rect):
            self.attackTimer = 0

    def moveto(self, x, y):
        self.moveTimer += 1
        self.moveTimer %= 80

        dx = x - self.rect.x
        dy = y - self.rect.y
        distance = (dx**2 + dy**2) ** 0.5

        if distance != 0:
            norm_dx = (dx / distance) * self.speed if abs(dx) > self.speed else dx
            norm_dy = (dy / distance) * self.speed if abs(dy) > self.speed else dy
        else:
            norm_dx, norm_dy = 0, 0

        self.flip = norm_dx < 0
        self.rect.x += round(norm_dx)
        self.rect.y += round(norm_dy)

        self.screen.blit(pygame.transform.flip(self.run_img[self.moveTimer // 4], self.flip, False), self.rect)

    def attack(self, player):
        self.attackTimer += 1
        self.attackTimer %= 20
        if self.attackTimer == 10:
            player.lifes -= 1
            if player.lifes > 0:
                SOUNDS["attackSound"].play()
        self.screen.blit(pygame.transform.flip(self.attack_img[self.attackTimer], self.flip, False), self.rect)

    def inreach(self, player_x, player_y):
        valx = abs(abs(self.rect.x) - abs(player_x))
        valy = abs(abs(self.rect.y) - abs(player_y))
        if valx <= self.attack_radius and valy <= self.attack_radius:
            return True
        else:
            return False

    def die(self, player, boss):
        if self.dieTimer < 79:
            self.dieTimer += 1
        if self.dieTimer == 11 and not boss:
            player.score += 1
            SOUNDS["enemydieSound"].play()

        self.screen.blit(self.die_img[self.dieTimer // 4], self.rect)

    def draw(self, delta_x, delta_y, player, player_rect, boss):
        if self.activated:
            if self.lifes > 0:
                if self.inreach(player_rect.x - 20, player_rect.y - 20) and not self.rect.colliderect(player_rect):
                    self.moveto(player_rect.x - 20, player_rect.y - 20)
                elif self.rect.colliderect(player_rect):
                    self.attack(player)
                else:
                    self.idle()

            else:
                self.die(player, boss)
            self.move(delta_x, delta_y, player_rect)
            self.lifebox_collider = pygame.Rect(self.rect.centerx, self.rect.centery, self.rect.width, self.rect.height)


class Boss:
    def __init__(self, screen, x, y):
        self.screen = screen
        self._init_loadImages()
        self.rect = self.run_img[0].get_rect(center=(x, y))
        self._init_attackVariables()
        self._init_animationVariables()

    def _load_image(self, action, index):
        return pygame.image.load(f"{ASSETS_PATH}/images/enemies/Boss/{action}/{index}.png").convert_alpha()

    def _load_images(self, action):
        return [self._load_image(action, n) for n in range(20)]

    def _create_collider(self, x_offset, y_offset, width, height):
        return pygame.Rect(self.rect.x + x_offset, self.rect.y + y_offset, width, height)

    def _init_loadImages(self):
        self.stand = self._load_image("idle", 0)
        self.walk_img = self._load_images("walk")
        self.run_img = self._load_images("run")
        self.attack_img = self._load_images("attack")
        self.die_img = self._load_images("die")

    def _init_attackVariables(self):
        self.lvl = "Easy"
        self.lvl_updated = False
        self.activated = True
        self.lifes = 150
        self.speed = 3.5
        self.radius = 300
        self.width, self.height = 80, 170
        self.box_collider = self._create_collider(self.width * 2, self.width * 2, self.rect.width * 2 / 8 - 60, self.rect.height - self.height * 1.5)
        self.lifebox_collider = self._create_collider(self.width * 2, self.width * 2.5, self.rect.width * 0.25, self.rect.height * 0.26)
        self.dash_speed = 15
        self.waitTimer = 150
        self.dashTime = 30

    def _init_animationVariables(self):
        self.moveTimer = 0
        self.attackTimer = 0
        self.dieTimer = 0
        self.removeTimer = 400
        self.flip = False
        self.dashing = False
        self.start_dash = False

    def move(self, delta_x, delta_y, player_rect):
        self.lifebox_collider.move_ip(delta_x, delta_y)
        self.box_collider.move_ip(delta_x, delta_y)
        self.rect.move_ip(delta_x, delta_y)
        
        if not self.box_collider.colliderect(player_rect):
            self.attackTimer = 0

        self.lifebox_collider.x = self.rect.x + self.width + (135 if self.flip else 0)

    def moveto(self, x, y, speed):
        self.moveTimer = (self.moveTimer + 1) % 80
        dx, dy = x - self.box_collider.x, y - self.box_collider.y
        distance = (dx**2 + dy**2) ** 0.5

        if distance != 0:
            norm_dx = (dx / distance) * speed if abs(dx) > speed else dx
            norm_dy = (dy / distance) * speed if abs(dy) > speed else dy
        else:
            norm_dx, norm_dy = 0, 0

        self.flip = norm_dx < 0
        self._update_colliders(round(norm_dx), round(norm_dy))

    def _update_colliders(self, delta_x, delta_y):
        self.lifebox_collider.move_ip(delta_x, delta_y)
        self.box_collider.move_ip(delta_x, delta_y)
        self.rect.move_ip(delta_x, delta_y)

    def attack(self, player):
        self.attackTimer = (self.attackTimer + 1) % 20
        if self.attackTimer == 10:
            player.lifes -= 2
            SOUNDS["bossattackSound"].play()
        self.screen.blit(pygame.transform.flip(self.attack_img[self.attackTimer], self.flip, False), self.rect)

    def superattack(self, player):
        if self.start_dash:
            if self.waitTimer > 0:
                self.waitTimer -= 1
                self.dash_speed = 0
            else:
                self.dashing = True
                if self.dashTime > 0:
                    self.dashTime -= 1
                    self.dash_speed = 15
                else:
                    self._reset_dash()

        if self.box_collider.colliderect(player.rect) and self.dashing:
            player.lifes -= 5
        
        self.moveto(player.rect.x - 20, player.rect.y - 20, self.dash_speed)
        self.screen.blit(pygame.transform.flip(self.run_img[self.moveTimer // 4], self.flip, False), self.rect)

    def _reset_dash(self):
        self.waitTimer = 140
        self.dashTime = 30
        self.dashing = False
        self.start_dash = False

    def die(self):
        if self.dieTimer < 79:
            self.dieTimer += 1
            if self.dieTimer == 1:
                SOUNDS["bossdieSound"].play()
        self.screen.blit(self.die_img[self.dieTimer // 4], self.rect)

    def draw(self, delta_x, delta_y, player, player_rect, lvl):
        if not self.lvl_updated:
            self.lvl = lvl
            if self.lvl == "Easy": self.lifes = 150
            elif self.lvl == "Medium": self.lifes = 225
            elif self.lvl == "Hard": self.lifes = 300
            self.lvl_updated = True
        if self.lifes > 0:
            self.start_dash = self.lifes in range(1, 50)

            if not self.start_dash:
                if not self.box_collider.colliderect(player_rect):
                    self.moveto(player_rect.x - 20, player_rect.y - 20, self.speed)
                    self.screen.blit(pygame.transform.flip(self.walk_img[self.moveTimer // 4], self.flip, False), self.rect)
                else:
                    self.attack(player)
            else:
                self.superattack(player)
        else:
            self.die()

        self.move(delta_x, delta_y, player_rect)