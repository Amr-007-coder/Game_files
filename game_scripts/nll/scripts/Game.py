from game_scripts.nll.utils import *
from game_scripts.nll.scripts import _menu, _player, _enemy
from game_scripts.nll.scripts.play_video import Video

class Game:
    def __init__(self):
        Video(f"{ASSETS_PATH}/videos/intro.mp4", f"{ASSETS_PATH}/videos/intro_audio.mp3").play()
        self.initialize_display()
        self.initialize_classes()
        self.load_bg(1)
        self.initialize_variables()
        self.load_files()
        self.reset_all_with_loading()
        self.font = pygame.font.SysFont("Comic Sans MS", 40)
        self.button_actions = {"Quit": False, "Pause": False, "Return": False}
        self.button_img = pygame.image.load(f"{ASSETS_PATH}/images/buttons/button.png").convert_alpha()
        self.activebutton_img = pygame.image.load(f"{ASSETS_PATH}/images/buttons/active_button.png").convert_alpha()
        self.return_button = ImageButton(self.screen, self.button_actions, "Return", (self.SCREEN_WIDTH/2, self.SCREEN_HEIGHT*3/4), (200, 88), self.button_img, self.activebutton_img, (0, 0, 0), self.font)
        self.start_minigame = False
        SOUNDS["gameSound"].play(-1)

    def loading_screen(self, event):
        loading_font = pygame.font.SysFont("Comic Sans MS", 40)  # Custom font
        loading_text = loading_font.render("Loading...", True, (255, 255, 255))
        progress = 0
        particle_timer = 0
        particles = []
        
        gradient_colors = [
            (50, 205, 50),   # Green
            (34, 139, 34),   # Forest Green
            (0, 128, 0),     # Dark Green
            (0, 255, 255),   # Cyan
            (0, 0, 255)      # Blue
        ]
        progress_bg_color = (30, 30, 30)  # Dark gray

        while not event.is_set():
            # Background
            self.screen.fill((10, 10, 50))
            self.screen.blit(self.menu.bg, (0, 0))

            text_rect = loading_text.get_rect(center=(self.SCREEN_WIDTH // 2, self.SCREEN_HEIGHT // 2 - 100))
            self.screen.blit(loading_text, text_rect.topleft)

            progress += 1 if progress < 100 else 0

            bar_width = 400
            bar_height = 20
            bar_x = (self.SCREEN_WIDTH - bar_width) // 2
            bar_y = self.SCREEN_HEIGHT // 2 + 50
            pygame.draw.rect(self.screen, progress_bg_color, (bar_x, bar_y, bar_width, bar_height))

            progress_ratio = progress / 100
            current_width = int(bar_width * progress_ratio)
            num_colors = len(gradient_colors)
            section_width = current_width / (num_colors - 1)

            for i in range(current_width):
                section_index = int(i // section_width)
                ratio_within_section = (i % section_width) / section_width
                start_color = gradient_colors[section_index]
                end_color = gradient_colors[min(section_index + 1, num_colors - 1)]

                r = int(start_color[0] + (end_color[0] - start_color[0]) * ratio_within_section)
                g = int(start_color[1] + (end_color[1] - start_color[1]) * ratio_within_section)
                b = int(start_color[2] + (end_color[2] - start_color[2]) * ratio_within_section)

                pygame.draw.line(self.screen, (r, g, b), (bar_x + i, bar_y), (bar_x + i, bar_y + bar_height))

            if particle_timer == 0:
                particles.append([random.randint(0, self.SCREEN_WIDTH), random.randint(0, self.SCREEN_HEIGHT), random.choice([(255, 255, 255), (100, 100, 255)])])
            particle_timer = (particle_timer + 1) % 5
            for particle in particles:
                pygame.draw.circle(self.screen, particle[2], (particle[0], particle[1]), 3)
                particle[1] -= 2
            particles = [p for p in particles if p[1] > 0]

            pygame.display.flip()
            self.clock.tick(30)

    def reset_all_with_loading(self):
        reset_complete = threading.Event()
        reset_thread = threading.Thread(target=self.reset_all_and_set_event, args=(reset_complete,))
        reset_thread.start()

        self.loading_screen(reset_complete)
        reset_thread.join()

    def reset_all_and_set_event(self, event):
        self.reset_all()
        event.set()

    def reset_all(self):
        self.GameTimer = 0
        self.bg_rect = self.BG.get_rect(center=(400, 200))
        self.bg_rect_last_pos = self.bg_rect.topleft
        self.boss = [_enemy.Boss(self.screen, 100, 100)]
        self.bossSound_played = False
        self.loseSound_played = False
        self.enemy_num = 0
        self.enemies = [_enemy.Enemy(self.screen, -10000, 0) for i in range(0, 20)]
        self.enemy_spawnTimer = 200
        self.reset_spawnTimer = 100
        if self.Cam.player.score >= 100 and self.Cam.player.lifes > 0:
            self.winvideo.play()
        elif self.Cam.player.lifes <= 0:
            self.losevideo.play()
        self.Cam.reset()
        self.menu.reset()

    def load_bg(self, bg_num):
        self.BG = pygame.image.load(f"{ASSETS_PATH}/images/bg{bg_num}.png").convert_alpha()
        self.bg_rect = self.BG.get_rect(center=(400, 200))
        self.bg_rect_last_pos = self.bg_rect.topleft

    def load_files(self):
        with open(f"{DATA_PATH}/achievements.json", "r") as file:
            self.achievements = json.load(file)

    def initialize_display(self):
        self.FPS = FPS
        self.SCREEN_WIDTH = 1313
        self.SCREEN_HEIGHT = 750
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT), pygame.SCALED | pygame.FULLSCREEN)
        self.clock = pygame.time.Clock()
        self.caption = "Nine Lives Left"
        pygame.display.set_caption(self.caption)
        pygame.display.set_icon(pygame.image.load(f"{ASSETS_PATH}/images/player/0/Show.png").convert_alpha())
        pygame.mouse.set_visible(False)
        pygame.event.set_grab(True)

    def initialize_classes(self):
        self.menu = _menu.Menu(self.screen, _enemy, _player)
        self.Cam = _player.Camara(self.screen)
        self.boss = [_enemy.Boss(self.screen, 100, 100)]
        self.enemies = [_enemy.Enemy(self.screen, 0, 0)]
        self.enemy_radius = self.enemies[0].attack_radius
        self.winvideo = Video(f"{ASSETS_PATH}/videos/win.mp4", f"{ASSETS_PATH}/videos/win_audio2.mp3")
        self.losevideo = Video(f"{ASSETS_PATH}/videos/lose.mp4", f"{ASSETS_PATH}/videos/lose_audio.mp3")
        self.winvideo.video_end = True
        self.losevideo.video_end = True

    def initialize_variables(self):
        self.GameTimer = 0
        self.mouse_speed = 8
        self.mouse_pos = [self.screen.get_width()//2, self.screen.get_height()//2]
        self.box = [0, -685, -1300]
        self.mine_timer = 15
        self.start_mine_timer = False
        self.enemy_spawnTimer = 200
        self.reset_spawnTimer = 100
        self.enemy_spawnMargin = 500
        self.spawn_x_min = self.bg_rect.x + self.enemy_spawnMargin
        self.spawn_x_max = self.bg_rect.x + self.bg_rect.width - self.enemy_spawnMargin
        self.spawn_y_min = self.bg_rect.y + self.enemy_spawnMargin
        self.spawn_y_max = self.bg_rect.y + self.bg_rect.height - self.enemy_spawnMargin
        self.mouse_particles = []
        self.controllers = []
        self.singleclick = False
        self.cmoveleft = self.cmoveright = self.cmoveup = self.cmovedown = self.click = self.rclick = False
        self.achievement_timer = 0
        self.current_achievement_text = None
        self.achievement_image = None
        self.notif_y_pos = -100  # Start off-screen
        self.longclick = False
        self.bossSound_played = self.loseSound_played = False

    def move_mouse(self, move):
        if move[0] and self.mouse_pos[0] > 20:
            self.mouse_pos[0] -= self.mouse_speed
        if move[1] and self.mouse_pos[0] < self.screen.get_width() - 20:
            self.mouse_pos[0] += self.mouse_speed
        if move[2] and self.mouse_pos[1] > 20:
            self.mouse_pos[1] -= self.mouse_speed
        if move[3] and self.mouse_pos[1] < self.screen.get_height() - 20:
            self.mouse_pos[1] += self.mouse_speed

        if not move[0] and not move[1] and not move[2] and not move[3]:
            self.mouse_pos = [pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1]]
        else:
            pygame.mouse.set_pos(self.mouse_pos)

    def move_bg(self, normal_speed):
        self.spawn_x_min = self.bg_rect.x + self.enemy_spawnMargin + 80
        self.spawn_x_max = self.bg_rect.x + self.bg_rect.width - self.enemy_spawnMargin - 150
        self.spawn_y_min = self.bg_rect.y + self.enemy_spawnMargin
        self.spawn_y_max = self.bg_rect.y + self.bg_rect.height - self.enemy_spawnMargin

        speed = normal_speed * self.Cam.player.scale_factor
        if self.Cam.player.cam_moveLeft and self.bg_rect.x < self.box[0]:
            self.bg_rect.x += speed
        if self.Cam.player.cam_moveRight and self.bg_rect.x > self.box[1]:
            self.bg_rect.x -= speed
        if self.Cam.player.cam_moveUp and self.bg_rect.y < self.box[0]:
            self.bg_rect.y += speed
        if self.Cam.player.cam_moveDown and self.bg_rect.y > self.box[2]:
            self.bg_rect.y -= speed

        if self.Cam.player.moveDir[0]:
            if self.Cam.player.box_collider.centerx > self.SCREEN_WIDTH/2 + speed and self.bg_rect.x > self.box[1]:
                self.Cam.player.rect.x -= speed
                self.bg_rect.x -= speed
            if self.Cam.player.box_collider.centerx < self.SCREEN_WIDTH/2 and self.bg_rect.x < self.box[0]:
                self.Cam.player.rect.x += speed
                self.bg_rect.x += speed

            if self.Cam.player.box_collider.centery > self.SCREEN_HEIGHT/2 + speed and self.bg_rect.y > self.box[2]:
                self.Cam.player.rect.y -= speed
                self.bg_rect.y -= speed
            if self.Cam.player.box_collider.centery < self.SCREEN_HEIGHT/2 and self.bg_rect.y < self.box[0]:
                self.Cam.player.rect.y += speed
                self.bg_rect.y += speed

            #pygame.draw.line(self.screen, (0, 0, 0), (self.SCREEN_WIDTH/2, 0), (self.SCREEN_WIDTH/2, self.SCREEN_HEIGHT))
            #pygame.draw.line(self.screen, (0, 0, 0), (0, self.SCREEN_HEIGHT/2), (self.SCREEN_WIDTH, self.SCREEN_HEIGHT/2))

    def calculate_bg_delta(self):
        # Calculate how much the bg_rect moved
        current_pos = self.bg_rect.topleft
        delta_x = current_pos[0] - self.bg_rect_last_pos[0]
        delta_y = current_pos[1] - self.bg_rect_last_pos[1]
        self.bg_rect_last_pos = current_pos
        return delta_x, delta_y

    def updateEnemies(self, delta_x, delta_y):
        for enemy in self.enemies:
            enemy.draw(delta_x, delta_y, self.Cam.player, pygame.Rect(self.Cam.player.box_collider.x -20, self.Cam.player.box_collider.y -20,
                                                        self.Cam.player.box_collider.width, self.Cam.player.box_collider.height), self.Cam.player.score >= 100)
            if enemy.lifes <= 0:
                enemy.activate_tel_timer = 0
            if enemy.activate_tel_timer <= 0:
                end = enemy.teleport(random.randint(self.spawn_x_min, self.spawn_x_max), random.randint(self.spawn_y_min, self.spawn_y_max), self.menu.difficulty_lvl)
                if end:
                    enemy.reset(self.menu.difficulty_lvl)
                    enemy.activate_tel_timer = 800
            if enemy.activated:
                enemy.activate_tel_timer -= 1

        if self.enemy_spawnTimer > 0:
            self.enemy_spawnTimer -= 1
        else:
            self.enemy_spawnTimer = self.reset_spawnTimer
            if self.reset_spawnTimer > 60:
                self.reset_spawnTimer -= 1
            self.enemies[self.enemy_num].activated = True
            if self.enemy_num < len(self.enemies) - 1:
                self.enemy_num += 1

    def BossFight(self, delta_x, delta_y, player):
        if self.Cam.player.score >= 100:
            if not self.playSounds.bossSound_played:
                self.playSounds.boss()
                self.playSounds.bossSound_played = True
            self.enemies = []
            self.enemy_spawnTimer = 10
            self.boss[0].draw(delta_x, delta_y, player, player.box_collider, self.menu.difficulty_lvl)

    def achieved(self, achievement_text, duration=3000):
        self.achievement_timer = duration
        self.current_achievement_text = achievement_text
        
        if achievement_text == "Defeated Boss":
            self.achievement_image = pygame.image.load(f"{ASSETS_PATH}/images/enemies/Boss/die/18.png").convert_alpha()

    def display_achievement(self, screen):
        if self.achievement_timer > 0:
            self.achievement_timer -= self.clock.get_time()
            
            target_y = 20
            if self.notif_y_pos < target_y:
                self.notif_y_pos += 8
            notif_y = self.notif_y_pos
            
            notif_width, notif_height = 300, 100
            notif_color = (30, 30, 30)  # Dark gray background
            text_color = (255, 255, 255)  # White text
            border_color = (200, 200, 200)  # Light gray border

            screen_width, _ = screen.get_size()
            notif_x = screen_width - notif_width - 20
            notification_surface = pygame.Surface((notif_width, notif_height))
            notification_surface.fill(notif_color)

            pygame.draw.rect(notification_surface, border_color, notification_surface.get_rect(), 3)

            font = pygame.font.Font(None, 36)
            text_surface = font.render(self.current_achievement_text, True, text_color)

            text_x = 20
            text_y = (notif_height - text_surface.get_height()) // 2
            notification_surface.blit(text_surface, (text_x, text_y))

            if self.achievement_image:
                image = pygame.transform.scale(self.achievement_image, (60, 60))
                image_x = notif_width - 70
                image_y = (notif_height - 60) // 2
                notification_surface.blit(image, (image_x, image_y))

            screen.blit(notification_surface, (notif_x, notif_y))
        else:
            self.current_achievement_text = None
            self.achievement_image = None
            self.notif_y_pos = -100

    def gameOver(self):
        if self.Cam.player.lifes <= 0 or self.boss[0].lifes <= 0:
            if self.boss[0].lifes <= 0:
                displayText(self.screen, "You Won!", (self.SCREEN_WIDTH/2, 250), (0, 0, 0), self.font)
                if not self.achievements["Defeated Boss"]:
                    with open(f"{DATA_PATH}/achievements.json", "w") as file:
                        json.dump({"Defeated Boss": True}, file)
                    self.achieved("Defeated Boss")
                    self.playSounds.upgrade()
                    self.load_files()
            elif self.Cam.player.lifes <= 0:
                displayText(self.screen, "You Lost!", (self.SCREEN_WIDTH/2, 250), (255, 0, 0), self.font)

            if self.Cam.player.score > 10:
                displayText(self.screen, f"+{self.Cam.player.score//3} Coins", (self.SCREEN_WIDTH/2, 300), (0, 0, 0), self.font)

            self.return_button(True, self.click)
            if (self.winvideo.video_end or self.losevideo.video_end) and not self.menu.CONTROLLER_MODE_ENABLED["Sound"]:
                pygame.mixer.set_num_channels(8)
            else:
                pygame.mixer.set_num_channels(0)

    def handle(self):
        player_circle = self.player_movement_controller()
        if self.menu.button_actions["Quit"]:
            self.button_actions["Quit"] = True
        if self.button_actions["Return"]:
            self.button_actions["Return"] = False
            pygame.mixer.stop()
            SOUNDS["gameSound"].play(-1)
            self.reset_all_with_loading()
        if self.menu.button_actions["Play"] and not self.button_actions["Pause"]:
            self.GameTimer += 1
            if self.GameTimer == 1:
                self.load_bg(2 if self.menu.shop_actions["change_bg"] else 1)
                self.winvideo.video_end = False
                self.losevideo.video_end = False
                pygame.mixer.stop()
            delta_x, delta_y = self.calculate_bg_delta()
            self.screen.blit(self.BG, self.bg_rect)
            if not self.Cam.player.dashing:
                self.move_bg(self.Cam.player.speed)
            else:
                self.move_bg(self.Cam.player.dash_speed)
            self.updateEnemies(delta_x, delta_y)
            self.BossFight(delta_x, delta_y, self.Cam.player)
            self.Cam.draw(self.mouse_pos, self.click,  player_circle, self.enemy_radius, self.boss, self.enemies,
                          delta_x, delta_y, self.spawn_x_min + 80, self.spawn_y_min, self.spawn_x_max - 150, self.spawn_y_max)
            displayText(self.screen, f"Score: {self.Cam.player.score}", (120, 30), (0, 0, 0), self.font)
            self.gameOver()
        elif self.button_actions["Pause"]:
            self.screen.fill("lightblue")
            displayText(self.screen, "Paused", (self.SCREEN_WIDTH/2, self.SCREEN_HEIGHT/4), (0, 0, 0), self.font)
            self.menu.startMenu_buttons[2](True, self.click, (self.SCREEN_WIDTH / 2, self.SCREEN_HEIGHT * 3 / 4))
        else:
            self.menu.handle(self.Cam, self.mouse_pos, self.get_singleClick(), self.longclick, self.winvideo.video_end, self.losevideo.video_end)
        self.display_achievement(self.screen)

    def get_singleClick(self):
        if self.click:
            self.click = False
            if not self.singleclick:
                self.singleclick = True
                return True
        else:
            self.singleclick = False
            return False

    def handle_keydown(self, event):
        click = pygame.mouse.get_pressed()
        if not self.controllers:
            if click[0]: self.longclick = True
            else: self.longclick = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE and self.menu.button_actions["Play"]:
                self.button_actions["Pause"] = not self.button_actions["Pause"]
            if self.Cam.player_canMove:
                self.Cam.player.standing = False
                if event.key == pygame.K_w or event.key == pygame.K_UP:
                    self.Cam.player.moveUp = True
                if event.key == pygame.K_a or event.key == pygame.K_LEFT:
                    self.Cam.player.moveLeft = True
                if event.key == pygame.K_s or event.key == pygame.K_DOWN:
                    self.Cam.player.moveDown = True
                if event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                    self.Cam.player.moveRight = True
            if event.key == pygame.K_SPACE and self.Cam.player.mines > 0:
                self.Cam.player.mines -= 1
                self.Cam.landmines.append(_player.Landmine(self.screen, self.Cam.player.box_collider.centerx,self.Cam.player.box_collider.centery))

    def handle_keyup(self, event):
        if event.type == pygame.KEYUP:
            self.Cam.player.standing = True
            if event.key == pygame.K_w or event.key == pygame.K_UP:
                self.Cam.player.moveUp = False
            if event.key == pygame.K_a or event.key == pygame.K_LEFT:
                self.Cam.player.moveLeft = False
            if event.key == pygame.K_s or event.key == pygame.K_DOWN:
                self.Cam.player.moveDown = False
            if event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                self.Cam.player.moveRight = False

    def handle_controller(self, event):
        click = pygame.mouse.get_pressed()
        if event.type == pygame.JOYDEVICEADDED:
            joy = pygame.joystick.Joystick(event.device_index)
            self.controllers.append(joy)
            print(joy)
        if event.type == pygame.JOYDEVICEREMOVED:
            self.controllers = []
            print(self.controllers)
        if event.type == pygame.JOYBUTTONDOWN:
            if event.button == 6:
                self.button_actions["Pause"] = not self.button_actions["Pause"]

        for controller in self.controllers:
            if controller.get_button(2):
                self.longclick = True
                if self.GameTimer > 0:
                    if self.Cam.player.mines > 0:
                        self.longclick = True
                        if self.mine_timer == 15:
                            self.Cam.player.mines -= 1
                            self.Cam.landmines.append(_player.Landmine(self.screen, self.Cam.player.box_collider.centerx,self.Cam.player.box_collider.centery))
                            self.start_mine_timer = True
            elif click[0]:
                self.longclick = True
            else: self.longclick = False
            if self.start_mine_timer: self.mine_timer -= 1
            if self.mine_timer == 0: self.mine_timer = 15; self.start_mine_timer = False

    def player_movement_controller(self):
        click = pygame.mouse.get_pressed()
        for controller in self.controllers:
            lhoriz_move = controller.get_axis(1)
            lvert_move = controller.get_axis(0)
            rhoriz_move = controller.get_axis(3)
            rvert_move = controller.get_axis(2)
            dash = round(controller.get_axis(5))
            threshold = 0.5

            if controller.get_button(0) or controller.get_button(7) or controller.get_button(8):
                self.click = True
            else:
                self.click = False

            if dash == 1:
                self.rclick = True
            else:
                self.rclick = False

            if self.Cam.player_canMove:
                if lvert_move > threshold:
                    self.Cam.player.moveLeft = False
                    self.Cam.player.moveRight = True
                elif lvert_move < -threshold:
                    self.Cam.player.moveLeft = True
                    self.Cam.player.moveRight = False
                else:
                    self.Cam.player.moveLeft = False
                    self.Cam.player.moveRight = False

                if lhoriz_move < -threshold:
                    self.Cam.player.moveUp = True
                    self.Cam.player.moveDown = False
                elif lhoriz_move > threshold:
                    self.Cam.player.moveUp = False
                    self.Cam.player.moveDown = True
                else:
                    self.Cam.player.moveUp = False
                    self.Cam.player.moveDown = False

            if rvert_move > threshold: self.cmoveright = True; self.cmoveleft = False
            elif rvert_move < -threshold: self.cmoveleft = True; self.cmoveright = False
            else: self.cmoveright = False; self.cmoveleft = False
            if rhoriz_move > threshold: self.cmovedown = True; self.cmoveup = False
            elif rhoriz_move < -threshold: self.cmoveup = True; self.cmovedown = False
            else: self.cmovedown = False; self.cmoveup = False
        if click[0]:
            self.click = True
        elif not click[0]:
            if self.controllers:
                if not controller.get_button(0):
                    self.click = False
            else:
                self.click = False
        if click[2]: self.rclick = True
        elif not click[2]:
            if "dash" in locals():
                if not dash == 1:
                    self.rclick = False
            else:
                self.rclick = False
        self.move_mouse([self.cmoveleft, self.cmoveright, self.cmoveup, self.cmovedown, self.click, self.rclick])
        return [self.cmoveleft, self.cmoveright, self.cmoveup, self.cmovedown, self.click, self.rclick]

    def run(self):
        self.start_minigame = True
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.button_actions["Quit"] = True

            self.handle_controller(event)
            self.handle_keydown(event)
            self.handle_keyup(event)

        self.handle()
        smooth_smoke_effect(self.screen, self.mouse_pos, self.mouse_particles, 300)
        pygame.display.update()
        self.clock.tick(self.FPS)