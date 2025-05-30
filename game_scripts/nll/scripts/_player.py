from utils import *
from game_scripts.nll.scripts.items import MineBox, Landmine
from game_scripts.nll.scripts.player_attackradius import *

class Player:
    def __init__(self, screen, camBox, skin_num):
        self.screen = screen
        self.camBox = camBox
        self.skin_num = skin_num
        self.load_images(skin_num)
        self.load_upgrades()
        self._init_stats()
        self._init_rects()
        self._init_animation()

    def _init_stats(self):
        self.restoreTime = 10 * FPS
        self.reset_restoreTime = 10 * FPS
        self.lifes = 6
        self.score = 0
        self.mines = 3

    def load_images(self, current):
        other = False
        if self.skin_num < 2:
            skin = str(self.skin_num)
            size = (144, 144)
        elif self.skin_num == 2:
            skin = "special"
            size = (52, 72)
        else:
            other = True
            skin = f"other/{current}"
            size = (52, 72)

        path = f"{ASSETS_PATH}/images/player/{skin}"
        dpath = path if not other else f"{ASSETS_PATH}/images/player/other"
        self.idle_img = pygame.image.load(f"{path}/idle.png").convert_alpha()
        self.dash_img = pygame.transform.scale(pygame.image.load(f"{dpath}/roll_small.png"), (41, 50)).convert_alpha()
        self.dead_img = pygame.image.load(f"{path}/dead.png").convert_alpha()
        self.run_sheet = pygame.image.load(f"{path}/run.png").convert_alpha()
        width = self.run_sheet.width
        order = [0, 3, 1, 2] if other else [0, 1, 2, 3]
        self.runDown_img = [get_image(self.run_sheet, n, size[0], size[1], 0, "black") for n in range(0, width//size[0])]
        self.runUp_img = [get_image(self.run_sheet, n, size[0], size[1], size[1]*order[1], "black") for n in range(0, width//size[0])]
        self.runLeft_img = [get_image(self.run_sheet, n, size[0], size[1], size[1]*order[2], "black") for n in range(0, width//size[0])]
        self.runRight_img = [get_image(self.run_sheet, n, size[0], size[1], size[1]*order[3], "black") for n in range(0, width//size[0])]
        self.heart = [pygame.image.load(f"{ASSETS_PATH}/images/heart/{state}.png").convert_alpha() for state in ["half", "full"]]
        self.explosion_img = [pygame.transform.scale(pygame.image.load(f"{ASSETS_PATH}/images/explosion/{n}.png"), (85, 52)).convert_alpha() for n in range(0, 8)]

    def load_upgrades(self):
        with open(f"{DATA_PATH}/saved_upgrades.json", "r") as file:
            self.upgrades = json.load(file)
        self.speed = self.upgrades["Speed"]["value"]
        self.speed_level = self.upgrades["Speed"]["lvl"]
        self.damage = self.upgrades["Damage"]["value"]
        self.damage_level = self.upgrades["Damage"]["lvl"]
        self.mine_dmg = self.upgrades["Damage"]["mine_dmg"]
        self.restore_lifes = self.upgrades["Health Regeneration"]

    def _init_rects(self):
        self.width, self.height = 96, 96
        self.rect = pygame.Rect(self.screen.get_width()/2, self.screen.get_height()/2, self.width, self.height)
        self.rect.center = (self.rect.x - 500, self.rect.y - 500)
        self.box_collider = pygame.Rect(self.rect.x + self.width/2, self.rect.y + self.height/2, self.rect.width/2, self.rect.height/2)
    
    def _init_animation(self):
        self.animation_speed = 5
        self.scale_factor = 1
        self.moveDir = [1, 0, 0, 0, 0, 0] #[idle, left, right, up, down, dash]
        self.steps = self.stepsx = self.stepsy = 0
        self.attack_counter = 0
        self.explosionTimer = 0
        self.explode = False
        self.standing = True
        self.moveLeft = self.moveRight = self.moveUp = self.moveDown = False
        self.cam_moveLeft = self.cam_moveRight = self.cam_moveUp = self.cam_moveDown = False
        self.move_horizontal = False
        self.move_vertical = False
        self._init_dash()
    
    def _init_dash(self):
        self.dash_speed = 9
        self.dashTimer = 20
        self.dashing = False
        self.clicked = False

    def reset(self):
        if self.score > 10:
            with open(f"{DATA_PATH}/coins.json", "r") as file:
                coins = json.load(file)
            with open(f"{DATA_PATH}/coins.json", "w") as file:
                json.dump({"Coins": coins["Coins"] + self.score//3}, file)
            self.score = 0

    def dash(self, click):
        if click and not self.clicked:
            self.clicked = True
            self.dashing = True
        if not click:
            self.clicked = False
        if self.dashing:
            self.moveDir = [0, 0, 0, 0, 0, 1]
            if self.dashTimer > 0:            
                self.dashTimer -= 1
                if self.dashTimer == 15:
                    SOUNDS["dashSound"].play()
            else:
                self.dashing = False
                self.dashTimer = 20

    def movesound(self):
        move_left = self.moveLeft or self.cam_moveLeft
        move_right = self.moveRight or self.cam_moveRight
        move_up = self.moveUp or self.cam_moveUp
        move_down = self.moveDown or self.cam_moveDown
        self.move_horizontal = move_left or move_right
        self.move_vertical = move_up or move_down
        if self.move_horizontal or self.move_vertical:
            self.steps += 1

        if self.steps == 9 and not self.dashing:
            SOUNDS["walkSound"].play()

        self.steps %= 21

    def control(self, rclick):
        self.cam_moveLeft = self.cam_moveRight = self.cam_moveUp = self.cam_moveDown = False

        if self.move_horizontal and self.move_vertical:
            self.scale_factor = 1/math.sqrt(2)
        else:
            self.scale_factor = 1.0

        if self.moveLeft and self.rect.x + self.width/2 > self.camBox.x:
            self.cam_moveRight = False
            self.cam_moveLeft = False
            self.moveDir = [0, 1, 0, 0, 0, 0]
            self.rect.x -= self.speed * self.scale_factor
            self.stepsx += 1
        elif self.moveLeft and self.rect.x <= self.camBox.x:
            self.moveDir = [0, 1, 0, 0, 0, 0]
            self.cam_moveLeft = True
            self.stepsx += 1

        if self.moveRight and self.rect.x < self.camBox.right - self.width:
            self.cam_moveLeft = False
            self.cam_moveRight = False
            self.moveDir = [0, 0, 1, 0, 0, 0]
            self.rect.x += self.speed * self.scale_factor
            self.stepsx += 1
        elif self.moveRight and self.rect.x >= self.camBox.right - self.width:
            self.moveDir = [0, 0, 1, 0, 0, 0]
            self.cam_moveRight = True
            self.stepsx += 1

        if self.moveUp and self.rect.y + self.height*1/2 > self.camBox.y:
            self.cam_moveDown = False
            self.cam_moveUp = False
            self.moveDir = [0, 0, 0, 1, 0, 0]
            self.rect.y -= self.speed * self.scale_factor
            self.stepsy += 1
        elif self.moveUp and self.rect.y <= self.camBox.y:
            self.moveDir = [0, 0, 0, 1, 0, 0]
            self.cam_moveUp = True
            self.stepsy += 1

        if self.moveDown and self.rect.y < self.camBox.bottom - self.height:
            self.cam_moveUp = False
            self.cam_moveDown = False
            self.moveDir = [0, 0, 0, 0, 1, 0]
            self.rect.y += self.speed * self.scale_factor  
            self.stepsy += 1 
        elif self.moveDown and self.rect.y >= self.camBox.bottom - self.height:
            self.moveDir = [0, 0, 0, 0, 1, 0]
            self.cam_moveDown = True
            self.stepsy += 1
        
        if (not self.moveLeft and not self.cam_moveLeft and not self.moveRight and not self.cam_moveRight and
            not self.moveUp and not self.cam_moveUp and not self.moveDown and not self.cam_moveDown):
            self.moveDir = [1, 0, 0, 0, 0, 0]
            self.steps = 0
            self.stepsx = 0
            self.stepsy = 0

        self.stepsx %= len(self.runDown_img) * self.animation_speed
        self.stepsy %= len(self.runDown_img) * self.animation_speed

        self.box_collider = pygame.Rect(self.rect.x + self.width/2 + 8, self.rect.y + self.height/2 + 8, self.rect.width/2 - 16, self.rect.height/2 - 16)
        self.dash(rclick)
        self.movesound()

    def attack(self, click, mouse, cattack, radius, enemies):
        distance = math.sqrt((mouse[0] - self.box_collider.centerx)**2 + (mouse[1] - self.box_collider.centery)**2)
        if distance <= radius:
            pygame.draw.line(self.screen, (0, 0, 0), self.box_collider.center, mouse, 5)
            pygame.draw.circle(self.screen, (255, 0, 0), mouse, radius//7, 5)
            attack_rects = create_circle_rects(mouse, radius//7, 10)
        else:
            attack_rects = create_circle_rects((-1000, -1000), 10, 10)

        for attack_rect in attack_rects:
            for enemy in enemies:
                if cattack:
                    if not hasattr(enemy, "lifebox_collider"):
                        enemy_rect = enemy.rect
                    else:
                        enemy_rect = enemy.lifebox_collider
                    if attack_rect.colliderect(enemy_rect):
                        if self.attack_counter == 0:
                            SOUNDS["explosionSound"].play()
                            enemy.lifes -= self.damage
                            self.attack_counter = 1
                        elif self.attack_counter == 1:
                            self.explode = True
                else:
                    self.attack_counter = 0
        
        if self.explode and not click:
            self.explosionTimer += 1
            if self.explosionTimer == 24:
                self.explode = False
                self.explosionTimer = 0

            self.screen.blit(self.explosion_img[self.explosionTimer // 3], self.explosion_img[0].get_rect(center=(mouse)))

    def draw_hearts(self):
        heart_pos_x = self.screen.get_width() / 2 - 50
        heart_pos_y = 20
        margin = 10

        for i in range(3):
            x = heart_pos_x + (self.heart[1].get_width() + margin) * i
            if self.lifes >= (i + 1) * 2:
                self.screen.blit(self.heart[1], (x, heart_pos_y))
            elif self.lifes == (i * 2 + 1):
                self.screen.blit(self.heart[0], (x, heart_pos_y))
            else:
                break

        if self.restore_lifes:
            if self.lifes < 6 and self.lifes > 0:
                if self.restoreTime > 0:
                    self.restoreTime -= 1
                else:
                    self.lifes += 1
                    self.restoreTime = self.reset_restoreTime

    def player_dead(self):
        self.mines = 0
        self.standing = self.moveLeft = self.moveRight = self.moveUp = self.moveDown = False
        self.cam_moveLeft = self.cam_moveRight = self.cam_moveUp = self.cam_moveDown = False

    def draw(self, click, mouse, circle, radius, enemies):
        self.draw_hearts()
        margin = (48, 30) if self.skin_num >= 2 else (0, 0)
        draw_rect = pygame.Rect(self.rect.x + margin[0], self.rect.y + margin[1], self.rect.height, self.rect.height)
        if self.lifes > 0:
            draw_dashed_circle(self.screen, self.box_collider.center, radius, 20, 10, "grey", 5)
            if self.moveDir[0]:
                self.screen.blit(self.idle_img, draw_rect)
            if self.moveDir[1]:
                self.screen.blit(self.runLeft_img[self.stepsx//self.animation_speed], draw_rect)
            if self.moveDir[2]:
                self.screen.blit(self.runRight_img[self.stepsx//self.animation_speed], draw_rect)
            if self.moveDir[3]:
                self.screen.blit(self.runUp_img[self.stepsy//self.animation_speed], draw_rect)
            if self.moveDir[4]:
                self.screen.blit(self.runDown_img[self.stepsy//self.animation_speed], draw_rect)
            if self.moveDir[5]:
                self.screen.blit(self.dash_img, self.box_collider)
            self.control(circle[5])
            self.attack(click, mouse, circle[4], radius, enemies)
        else:
            self.player_dead()
            self.screen.blit(self.dead_img, draw_rect)

class Camara:
    def __init__(self, screen):
        self.screen = screen
        screen_width, screen_height = self.screen.get_size()
        self.rect = pygame.Rect(579, 300, screen_width - 1163, screen_height - 600)
        self._init_playerProperties()
        self._init_itemProperties()

    def _init_playerProperties(self):
        self.player_skin_num = 0
        self.player = Player(self.screen, self.rect, self.player_skin_num)
        self.player_canMove = False

    def _init_itemProperties(self):
        self.landmines = [Landmine(self.screen, -10000, -10000)]
        self.mineboxes = []
        self.minebox_spawnTimer = 200
        self.minebox_resetTimer = 250

    def reset(self):
        self.player.reset()
        self.player = Player(self.screen, self.rect, self.player_skin_num)
        self.landmines = [Landmine(self.screen, -10000, -10000)]
        self.mineboxes = []
        self.minebox_spawnTimer = 200
        self.minebox_resetTimer = 250

    def check_collision(self):
        if self.rect.colliderect(self.player.box_collider):
            self.player_canMove = True
        else:
            self.player_canMove = False

    def spawn_mineBox(self, min_x, min_y, max_x, max_y):
        if self.minebox_spawnTimer > 0:
            self.minebox_spawnTimer -= 1
        else:
            self.minebox_spawnTimer = self.minebox_resetTimer
            self.mineboxes.append(MineBox(self.screen, random.randint(min_x, max_x), random.randint(min_y, max_y)))

    def draw(self, mouse, click, player_circle, radius, boss, enemies, delta_x, delta_y, loot_min_x, loot_min_y, loot_max_x, loot_max_y):
        for mine in self.landmines[:]:
            if not self.player.score >= 100:
                mine.draw(delta_x, delta_y, enemies, self.player.mines, self.player.mine_dmg)
            else:
                mine.draw(delta_x, delta_y, boss, self.player.mines, self.player.mine_dmg)
            if mine.exploded:
                self.landmines.remove(mine)

        for minebox in self.mineboxes[:]:
            minebox.spawn(delta_x, delta_y, self.player.box_collider)
            if minebox.collected:
                self.mineboxes.remove(minebox)
                if not minebox.empty:
                    self.player.mines += 1

        if self.player.score < 100:
            enemy_type = enemies
        else:
            enemy_type = boss
        self.player.draw(click, mouse, player_circle, radius, enemy_type)
        self.spawn_mineBox(loot_min_x, loot_min_y, loot_max_x, loot_max_y)

        self.check_collision()