from utils import *

class MineBox:
    def __init__(self, screen, x, y):
        self.screen = screen
        self.number = random.randint(0, 101)
        self.empty = False if self.number >= 60 else True
        self.img = pygame.transform.scale(pygame.image.load(f"{ASSETS_PATH}/images/items/{"mine_chest" if not self.empty else "chest"}.png").convert_alpha(), (100, 100))
        self.rect = self.img.get_rect(center=(x, y))
        self.collected = False

    def move(self, delta_x, delta_y):
        self.rect.move_ip(delta_x, delta_y)

    def collect(self, player_rect):
        if self.rect.colliderect(player_rect):
            self.collected = True
            SOUNDS["collectSound"].play()

    def spawn(self, delta_x, delta_y, player_rect):
        self.screen.blit(self.img, self.rect)
        self.move(delta_x, delta_y)
        self.collect(player_rect)


class Landmine:
    def __init__(self, screen, x, y):
        self.screen = screen
        self.img = pygame.transform.scale(pygame.image.load(f"{ASSETS_PATH}/images/explosion/landmine.png"), (50, 50)).convert_alpha()
        self.rect = self.img.get_rect(center=(x,y))
        self.exploded = False

    def move(self, delta_x, delta_y):
        self.rect.move_ip(delta_x, delta_y)

    def explode(self, enemies, mine_dmg):
        for enemy in enemies:
            if enemy.activated:
                if not hasattr(enemy, "lifebox_collider"):
                    if self.rect.colliderect(enemy.rect):
                        self.exploded = True
                        self.rect = pygame.Rect(-10000, 0, 0, 0) #=> doesnt kill more than 1 enemy
                        enemy.lifes -= mine_dmg
                else:
                    if self.rect.colliderect(enemy.lifebox_collider):
                        self.exploded = True
                        self.rect = pygame.Rect(-10000, 0, 0, 0) #=> doesnt kill more than 1 enemy
                        enemy.lifes -= mine_dmg

    def draw_mines(self, mine_num): #inventory
        for n in range(mine_num):
            self.screen.blit(pygame.transform.scale(self.img, (25, 25)), (40 + (self.img.get_width()-20)*n, 60))

    def draw(self, delta_x, delta_y, enemies, mine_num, mine_dmg):
        self.screen.blit(self.img, self.rect)
        self.move(delta_x, delta_y)
        self.explode(enemies, mine_dmg)
        self.draw_mines(mine_num)
