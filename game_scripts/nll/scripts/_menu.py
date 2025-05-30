from utils import *
from game_scripts.nll.scripts.play_video import Video
import game_scripts.nll.scripts.mini_game as mini_game

class Menu:
    def __init__(self, screen, enemy, player):
        self.screen = screen
        self.SW, self.SH = self.screen.get_size()
        self._init_ui()
        self._init_player(player)
        self._init_enemy(enemy)
        self.load_skins()
        self._load_images()
        self._load_dictionaries()
        self._load_buttons()
        self._init_bg()
        self._load_files()

        self.coins_file = None
        self.playsounds = True
        self.reset_sound = True
        self.dragging = self.dragging2 = False
        self.volume = effectvolume
        self.music_volume = bgvolume
        self.show_buttonInfo = show_buttonInfo
        self.settings_prop = Settings(self.screen)

    def _init_player(self, player):
        self.rotateimage = SmoothMovingImage(f"{ASSETS_PATH}/images/player/0/dead.png", self.screen)
        self.player = player.Player(self.screen, pygame.Rect(0, 0, 0, 0), 1)
        self.player.lifes = 0
        self.reset_player = True

    def _init_enemy(self, enemy):
        self.difficulty_lvl = "Easy"
        self.current_lvl = MagnetSlider(self.SW/2, 150, 300, 18, ["Easy", "Medium", "Hard"], self.small_font, (0, 0, 0), (200, 200, 200), (50, 100, 200), (150, 150, 150))
        self.enemy_switch = SmoothSwitchButton(5, 115, 60, 30, 12, GREEN, RED, BLACK, self.screen)
        self.enemy = enemy.Enemy(self.screen, self.screen.get_width()/2 - 50, self.screen.get_height()/2 - 30)
        self.enemy.activated = True

    def _init_ui(self):
        self.font = pygame.font.SysFont("Comic Sans MS", 40)
        self.small_font = pygame.font.SysFont("Comic Sans MS", 25)
        self.verysmall_font = pygame.font.SysFont("Comic Sans MS", 18)
        self.button_margin = (180, 160)
        self.current_x_pos = 0
        #timers
        self.timer = 0
        self.speedmessage_timer = -10000
        self.damagemessage_timer = -10000
        self.Time = 3
        self.Time_reset = 3

    def _init_bg(self):
        self.glitterscreen = GlitterEffect(self.screen)
        self.waves = WaterWaveEffect(self.bg, self.screen)
        self.credits = ScrollableTextDisplay(self.screen, self.credits_text, self.small_font, (0, 0, 0), 1313, 730, (173, 216, 230, 240), 10)

    def _load_images(self):
        def load(path, scale=None):
            image = pygame.image.load(path).convert_alpha()
            if scale:
                image = pygame.transform.scale(image, scale)
            return image

        # Backgrounds
        self.text_bg = load(f"{ASSETS_PATH}/images/menu/text.png", (550, 570))
        self.text_bg2 = load(f"{ASSETS_PATH}/images/menu/text.png", (850, 570))
        self.bg = load(f"{ASSETS_PATH}/images/menu/bg.png")
        displayText(self.bg, "Nine Lives Left", (self.SW/2, 50), (255, 255, 255), self.font)
        self.bg1_img = load(f"{ASSETS_PATH}/images/bg1.png", (40, 40))
        self.bg2_img = load(f"{ASSETS_PATH}/images/bg2.png", (40, 40))
        self.active_bg1_img = load(f"{ASSETS_PATH}/images/active_bg1.png", (40, 40))
        self.active_bg2_img = load(f"{ASSETS_PATH}/images/active_bg2.png", (40, 40))
        self.current_bg1 = self.active_bg1_img
        self.current_bg2 = self.bg2_img

        # Player skins
        self.player_skin1 = load(f"{ASSETS_PATH}/images/player/0/Show.png", (106, 120))
        self.player_skin2 = load(f"{ASSETS_PATH}/images/player/1/Show.png", (106, 120))
        self.player_skin_special = load(f"{ASSETS_PATH}/images/player/special/Show.png")
        self.player_skin_special_hidden = load(f"{ASSETS_PATH}/images/player/special/hidden.png")

        # Enemy / boss
        self.boss_img = load(f"{ASSETS_PATH}/images/enemies/Boss/die/18.png", (60, 60))

        # Menu elements
        self.lock_img = load(f"{ASSETS_PATH}/images/menu/lock.png", (106, 120))
        self.imgframe_img = load(f"{ASSETS_PATH}/images/menu/img_frame.png")
        self.button_img = load(f"{ASSETS_PATH}/images/buttons/button.png")
        self.active_button_img = load(f"{ASSETS_PATH}/images/buttons/active_button.png")
        self.button_bg_img = load(f"{ASSETS_PATH}/images/menu/button_bg.png", (300, 106))
        self.button_bg_rect = pygame.Rect(self.button_bg_img.get_width() - 30, 0, 30, self.button_bg_img.get_height())

        # Sound
        self.soundon_img = load(f"{ASSETS_PATH}/images/buttons/sound_on.png")
        self.soundoff_img = load(f"{ASSETS_PATH}/images/buttons/sound_off.png")
        self.sound_img = self.soundon_img
        self.button_sound = pygame.mixer.Sound(f"{ASSETS_PATH}/sounds/menu/button.wav")

        # Help / UI
        self.video_img = load(f"{ASSETS_PATH}/images/help/video.png")
        self.help_img = load(f"{ASSETS_PATH}/images/help/0.png")
        self.big_help_img = load(f"{ASSETS_PATH}/images/help/explanation.png")
        self.keyboard_img = load(f"{ASSETS_PATH}/images/buttons/keyboard.png")
        self.controller_img = load(f"{ASSETS_PATH}/images/buttons/controller.png")

        # Shop / UI Icons
        self.achievements_img = load(f"{ASSETS_PATH}/images/menu/achievements.png")
        self.shop_img = load(f"{ASSETS_PATH}/images/buttons/shop.png")
        self.coin_img = load(f"{ASSETS_PATH}/images/buttons/coin.png")
        self.upgrade_img = load(f"{ASSETS_PATH}/images/buttons/upgrade.png")
        self.darkupgrade_img = load(f"{ASSETS_PATH}/images/buttons/darkupgrade.png")
        self.empty_img = load(f"{ASSETS_PATH}/images/mini/empty.png")

        # Hyperlinks
        self.github_img = load(f"{ASSETS_PATH}/images/hyperlinks/github.png")
        self.youtube_img = load(f"{ASSETS_PATH}/images/hyperlinks/youtube.png")
        self.itch_img = load(f"{ASSETS_PATH}/images/hyperlinks/itch.png")
        self.discord_img = load(f"{ASSETS_PATH}/images/hyperlinks/discord.png")

    def _load_dictionaries(self):
        self.button_pos = [(self.SW*2/4, self.SH/2 - self.button_margin[1]),
                           (self.SW*3/4 - self.button_margin[0], self.SH/4 + self.button_margin[1]*1.2), (self.SW/4 + self.button_margin[0], self.SH/4 + self.button_margin[1]*1.2),
                           (self.SW*2/4, self.SH*2/4 + self.button_margin[1])]
        
        self.startMenu_infos = ["Start Game", "Tutorial", "More Settings", "Exit Game"]
        self.button_actions = {
            "Play": False,
            "Help": False,
            "Settings": False,
            "Quit": False,
        }
        self.shop_actions = {
            "Open": False,
            "Speed": False,
            "Damage": False,
            "Health Regeneration": False,
            "More Skins": False,
            "change_bg": False
        }
        self.hyper_infos = ["Github", "Youtube", "Itch", "Discord"]
        self.hyperlinks = {"Github": False, "Youtube": False, "Itch": False, "Discord": False}
        self.hyperlinks_pos = [(self.SW - 80, 40), (self.SW - 160, 40), (self.SW - 245, 40), (self.SW - 325, 40)]
        self.hyperlinks_imgs = [pygame.transform.scale(self.github_img, (50, 50)), pygame.transform.scale(self.youtube_img, (57, 40)),
                                pygame.transform.scale(self.itch_img, (60, 50)), pygame.transform.scale(self.discord_img, (50, 50))]
        self.hyperlink_urls = {
            "Github": "https://github.com/Amr-007-coder/",
            "Youtube": "https://www.youtube.com/",
            "Itch": "https://pygame-programmierer.itch.io/",
            "Discord": "https://discord.com/"
        }
        self.otheractions = {"BG": True, "Help": False, "Controls": False, "Achievements": False, "Credits": False, "Mini Game": False}
        self.help_actions = {"Show image": False, "Show video": False}
        self.CONTROLLER_MODE_ENABLED = {"Controller": False, "Sound": False}
        self.controls_pos = [(self.SW/2, self.SH/10 + 30), (self.SW/2, self.SH*3/10), (self.SW/2, self.SH*4/10),
                             (self.SW/2, self.SH*5/10), (self.SW/2, self.SH*6/10)]
        self.controls_msgs = ["Controls", "Movement: wasd", "Attack: LMB", "Place Mine: SPACE", "Dash: RMB"]

        self.credits_text = ["Credits","","",
            "Dev: ","Amr Mawloud","",
            "Assets:","Images:",
            "https://cupnooble.itch.io/sprout-lands-asset-pack",
            "https://craftpix.net/freebies/free-monster-enemy-game-sprites",
            "","Sounds:","https://pixabay.com/sound-effects","","","","","","Have fun!!!"
        ]

        self.wave_params = [
        {
            'color': (34, 139, 34),  # Grün
            'amplitude': 50,
            'frequency': 0.03,
            'speed': 0.02,
            'offset': random.randint(0, 50)
        },
        {
            'color': (0, 255, 127),  # Türkis
            'amplitude': 70,
            'frequency': 0.02,
            'speed': 0.015,
            'offset': random.randint(-50, 0)
        },
        {
            'color': (72, 61, 139),  # Dunkles Blau
            'amplitude': 50,
            'frequency': 0.03,
            'speed': 0.02,
            'offset': random.randint(0, 50)
        },
        ]

    def _load_buttons(self):
        self.startMenu_buttons = [ImageButton(self.screen, self.button_actions, msg, pos, (250, 109),
                                              self.button_img, self.active_button_img, (0, 0, 0), self.font, info=info)
                                              for msg, pos, info in zip(self.button_actions, self.button_pos, self.startMenu_infos)]
        self.hyperLink_buttons = [ImageButton(self.screen, self.hyperlinks, msg, pos, img.get_size(), img, img, (0, 0, 0), self.font, info=info)
                                              for msg, pos, img, info in zip(self.hyperlinks, self.hyperlinks_pos, self.hyperlinks_imgs, self.hyper_infos)]
        
        self.help_button = ImageButton(self.screen, self.button_actions, "Help", (self.SW / 2, 200), (250, 109), self.button_img, self.active_button_img, (0, 0, 0), self.font)
        self.controls_button = ImageButton(self.screen, self.otheractions, "Controls", (self.SW / 2, self.SH - 200), (250, 109), self.button_img, self.active_button_img, (0, 0, 0), self.font)
        self.keyboard_button = ImageButton(self.screen, self.CONTROLLER_MODE_ENABLED, 'Controller', (150, 50), (65, 30), self.keyboard_img, self.keyboard_img, (0, 0, 0), self.font)
        self.controller_button = ImageButton(self.screen, self.CONTROLLER_MODE_ENABLED, "Controller", (250, 50), (49, 30), self.controller_img, self.controller_img, (0, 0, 0), self.font)
        self.sound_button = ImageButton(self.screen, self.CONTROLLER_MODE_ENABLED, 'Sound', (50, 50), (60, 60), self.sound_img, self.sound_img, (0, 0, 0), self.font)
        self.open_button = ImageButton(self.screen, self.shop_actions, 'Open', (self.SW / 2 - 25, self.SH * 13 / 14), (60, 60), self.shop_img, self.shop_img, (0, 0, 0), self.font)
        self.achivements_button = ImageButton(self.screen, self.otheractions, 'Achievements', (self.SW / 2 + 32, self.SH * 13 / 14), (50, 50), self.achievements_img, self.achievements_img, (0, 0, 0), self.font)
        self.miniGame_button = ImageButton(self.screen, self.otheractions, 'Mini Game', (195, self.SH - 10), (75, 25), self.empty_img, self.empty_img, (255, 255, 255), self.verysmall_font)
        self.credits_button = ImageButton(self.screen, self.otheractions, 'Credits', (100, self.SH - 10), (75, 25), self.empty_img, self.empty_img, (255, 255, 255), self.verysmall_font)
        self.helpImage_button = ImageButton(self.screen, self.help_actions, 'Show image', (self.SW / 3, self.SH / 2), (336, 200), self.help_img, self.help_img, (0, 0, 0), self.font)
        self.helpVideo_button = ImageButton(self.screen, self.help_actions, 'Show video', (self.SW * 2 / 3, self.SH / 2), (336, 200), self.video_img, self.video_img, (0, 0, 0), self.font)
        self.coin_button = ImageButton(self.screen, self.shop_actions, 'Open', (self.SW / 2, self.SH / 10), (80, 80), self.coin_img, self.coin_img, (0, 0, 0), self.font)
        self.healthUpgrade_button = ImageButton(self.screen, self.shop_actions, 'Health Regeneration', (self.SW / 2, self.SH * 3.65 / 10), (250, 50), self.upgrade_img, self.upgrade_img, (0, 0, 0), self.small_font)
        self.speedUpgrade_button = ImageButton(self.screen, self.shop_actions, 'Speed', (self.SW / 2 - 265, self.SH * 3.5 / 10), (173, 50), self.upgrade_img, self.upgrade_img, (0, 0, 0), self.small_font)
        self.damageUpgrade_button = ImageButton(self.screen, self.shop_actions, 'Damage', (self.SW / 2 + 265, self.SH * 3.5 / 10), (173, 50), self.upgrade_img, self.upgrade_img, (0, 0, 0), self.small_font)
        self.bg2_button = ImageButton(self.screen, self.shop_actions, 'change_bg', (self.SW / 2 - 32, 215), (40, 40), self.current_bg1, self.current_bg1, (0, 0, 0), self.font)
        self.bg1_button = ImageButton(self.screen, self.shop_actions, 'change_bg', (self.SW / 2 + 33, 215), (40, 40), self.current_bg2, self.current_bg2, (0, 0, 0), self.font)
        self.moreSkins_button = ImageButton(self.screen, self.shop_actions, "More Skins", (self.SW/2 - 180, self.SH - 172.5), (173, 50), self.upgrade_img, self.upgrade_img, (0, 0, 0), self.small_font)
        self._moreSkins_button = ImageButton(self.screen, {"More Skins": False}, "More Skins", (self.SW/2 - 180, self.SH - 172.5), (173, 50), self.darkupgrade_img, self.darkupgrade_img, (0, 0, 0), self.small_font)    

    def _load_files(self):
        with open(f"{DATA_PATH}/speed.json", "r") as f:
            self.speed_levels = json.load(f)["levels"]
        with open(f"{DATA_PATH}/damage.json", "r") as f:
            self.damage_levels = json.load(f)["levels"]
        with open(f"{DATA_PATH}/saved_upgrades.json", "r") as file:
            self.upgrades = json.load(file)
        with open(f"{DATA_PATH}/achievements.json", "r") as file:
            self.achivements = json.load(file)

    def load_skins(self):
        with open(f"{DATA_PATH}/skins.json") as file:
            self.skins = json.load(file)
        self.selected_skin = 0
        self.other_skin = False
        self.skin0_rect = pygame.Rect(0, 0, 0, 0)
        self.skin1_rect = pygame.Rect(0, 0, 0, 0)
        self.skin2_rect = pygame.Rect(0, 0, 0, 0)
        self.skins_pos = [(self.SW*2/11, self.SH*3/10), (self.SW*4/11, self.SH*3/10), (self.SW*6/11, self.SH*3/10), (self.SW*8/11, self.SH*3/10),
                         (self.SW*3/11, self.SH*6/10), (self.SW*5/11, self.SH*6/10), (self.SW*7/11, self.SH*6/10)]
        self.skins_imgs = [pygame.image.load(f"{ASSETS_PATH}/images/player/other/{n}/Show.png").convert_alpha() for n in range(0, 7)]
        self.skins_owned = self.skins["other_skins"]

    def change_jsonFile(self, input, file):
        with open(file, "w") as opened_file:
            json.dump(input, opened_file)

    def change_jsonValue(self, file_path, key, new_value, second_key=None):
        with open(file_path, "r") as file:
            data = json.load(file)

        if key in data:
            if second_key:
                data[key][second_key] = new_value
            else:
                data[key] = new_value
        
        with open(file_path, "w") as file:
            json.dump(data, file, indent=4)
        
    def save_upgrades(self):
        self.change_jsonFile(self.upgrades, f"{DATA_PATH}/saved_upgrades.json")

    def reset(self):
        self.reset_sound = True
        self._load_dictionaries()
        self._load_buttons()

    def show_controls(self):
        if self.CONTROLLER_MODE_ENABLED["Controller"]:
            self.controller_button.set_images(pygame.image.load(f"{ASSETS_PATH}/images/buttons/controller_.png").convert_alpha())
            self.keyboard_button.set_images(pygame.image.load(f"{ASSETS_PATH}/images/buttons/keyboard.png").convert_alpha())
            self.controls_msgs = ["Controls", "Movement: Sticks", "Attack: Cross", "Place Mine: Square", "Dash: R2"]        
        else:
            self.controls_msgs = ["Controls", "Movement: wasd", "Attack: LMB", "Place Mine: SPACE", "Dash: RMB"]
            self.controller_button.set_images(pygame.image.load(f"{ASSETS_PATH}/images/buttons/controller.png").convert_alpha())
            self.keyboard_button.set_images(pygame.image.load(f"{ASSETS_PATH}/images/buttons/keyboard_.png").convert_alpha())
        if self.CONTROLLER_MODE_ENABLED["Sound"]:
            self.sound_button.set_images(self.soundoff_img)
        else:
            self.sound_button.set_images(self.soundon_img)
            if not pygame.mixer.get_busy():
                SOUNDS["gameSound"].play(-1)

    def handle_hyperlinks(self):
        for key, active in self.hyperlinks.items():
            if active:
                webbrowser.open(self.hyperlink_urls[key])
                self.hyperlinks[key] = False

    def start(self, click):
        mouse = pygame.mouse.get_pos()
        for button in self.startMenu_buttons:
            button.show_info = self.show_buttonInfo
            button(True, click)

        for button in self.hyperLink_buttons:
            button.show_info = self.show_buttonInfo
            button(False, click)

        self.current_x_pos, rect = move_image_left(self.screen, self.button_bg_img, self.otheractions["BG"], self.button_bg_rect.width, self.current_x_pos)
        if not self.otheractions["BG"]:
            self.controller_button(False, click)
            self.keyboard_button(False, click)
            self.sound_button(False, click)

        self.open_button(False, click)
        self.achivements_button(False, click)
        self.credits_button(True, click)
        self.miniGame_button(True, click)

        self.handle_minigame()
        self.show_credits(click)
        self.rotateimage.draw()
        displayText(self.screen, "v2.12", (30, self.SH - 10), (255, 255, 255), pygame.font.SysFont("Comic Sans MS", 18))
        self.handle_hyperlinks()
        if rect.collidepoint(mouse):
            if click:
                self.otheractions["BG"] = not self.otheractions["BG"]

    def handle_help(self):
        if self.help_actions["Show image"]:
            self.screen.blit(pygame.transform.scale(self.big_help_img, (self.SW, self.SH)), (0, 0))
        if self.help_actions["Show video"]:
            Video(f'{ASSETS_PATH}/videos/game.mp4', f'{ASSETS_PATH}/sounds/menu/button.wav').play()
            self.help_actions["Show video"] = False

    def help(self, click):
        if click:
            self.help_actions["Show image"] = False
        self.help_button(True, click)
        self.helpImage_button(False, click)
        self.helpVideo_button(False, click)
        self.handle_help()
        self.controls_button(True, click)

        if self.otheractions["Controls"]:
            self.screen.blit(self.text_bg, (self.SW/2 - 275, 0))
            self.controls_text(self.controls_msgs, self.controls_pos)
            if self.Time > 0:
                self.Time -= 1
            else:
                if click:
                    self.Time = self.Time_reset
                    self.otheractions["Controls"] = False

    def shop(self, player, cam, mouse, click):
        with open(f"{DATA_PATH}/coins.json", "r") as file:
            self.coins_file = json.load(file)
            self.coins = self.coins_file["Coins"]
        self.screen.blit(self.text_bg2, (240, 180))
        self.open_button(False, click)
        displayText(self.screen, f"{self.coins}", (self.SW/2, self.SH*2/10), (0, 0, 0), self.font)
        self.coin_button(False, click)
        self.healthUpgrade_button(True, click)
        hg_msg = "(Cost: 8)" if not self.upgrades["Health Regeneration"] else "(Purchased!)"
        displayText(self.screen, hg_msg, (self.SW/2, self.SH*4.3/10), (0, 0, 0), self.small_font)
        self.speedUpgrade_button(True, click)
        self.damageUpgrade_button(True, click)
        self.handle_bgs(click)
        current_level = next((level for level in self.speed_levels if level["lvl"] == player.speed_level), None)
        offset = 260
        displayText(self.screen, f"Speed: {player.speed}", (self.SW/2 - offset, self.SH*4.3/10), (0, 0, 0), self.small_font)
        if current_level and not current_level["max"]:
            speed_msg = f"(Next: {current_level['value']} for {current_level['nextprice']} coins)"
        elif current_level and current_level["max"]:
            speed_msg = "(Max Level)"
        displayText(self.screen, speed_msg, (self.SW/2 - offset, self.SH*4.7/10), (0, 0, 0), self.small_font)
        
        current_damage_level = next((level for level in self.damage_levels if level["lvl"] == player.damage_level), None)
        displayText(self.screen, f"Damage: {player.damage}", (self.SW/2 + offset, self.SH*4.3/10), (0, 0, 0), self.small_font)
        if current_damage_level and not current_damage_level["max"]:
            damage_msg = f"(Next: {current_damage_level['value']} for {current_damage_level['nextprice']} coins)"
        elif current_damage_level and current_damage_level["max"]:
            damage_msg = "(Max Level)"
        displayText(self.screen, damage_msg, (self.SW/2 + offset, self.SH*4.7/10), (0, 0, 0), self.small_font)
            
        if self.shop_actions["Health Regeneration"]:
            if not self.upgrades["Health Regeneration"]:
                if self.coins >= 8:
                    
                    self.change_jsonFile({"Coins": self.coins - 8}, f"{DATA_PATH}/coins.json")
                    self.upgrades["Health Regeneration"] = True
            self.save_upgrades()
            self._load_files()
            self.shop_actions["Health Regeneration"] = False
        if not self.shop_actions["More Skins"]:
            self.handle_shop(cam, click)
        else:
            self.handle_skins(cam, mouse, click)

    def handle_bgs(self, click):
        bg_rect = pygame.Rect(self.SW/2, 215, 46, 46)
        bg_rect.center = (self.SW/2, 215)
        pygame.draw.rect(self.screen, (0, 0, 0), (bg_rect.x - 33, bg_rect.y, bg_rect.width, bg_rect.height))
        pygame.draw.rect(self.screen, (0, 0, 0), (bg_rect.x + 32, bg_rect.y, bg_rect.width, bg_rect.height))
        self.bg2_button(False, click)
        self.bg1_button(False, click)
        if not self.shop_actions["change_bg"]:
            self.bg2_button.set_images(self.active_bg1_img)
            self.bg1_button.set_images(self.bg2_img)
        else:
            self.bg2_button.set_images(self.bg1_img)
            self.bg1_button.set_images(self.active_bg2_img)

    def handle_damage(self, player):
        offset = 260
        if self.shop_actions["Damage"]:
            self.shop_actions["Damage"] = False
            
            current_level = next((level for level in self.damage_levels if level["lvl"] == player.damage_level), None)
            
            if current_level:
                if not current_level["max"]:
                    upgrade_cost = current_level["nextprice"]
                    
                    if self.coins >= upgrade_cost:
                        self.change_jsonFile({"Coins": self.coins - upgrade_cost}, f"{DATA_PATH}/coins.json")
                        player.damage = current_level["value"]
                        player.mine_damage = current_level["mine_dmg"]
                        player.damage_level += 1
                        
                        self.upgrades["Damage"]["lvl"] += 1
                        self.upgrades["Damage"]["value"] = player.damage
                        self.upgrades["Damage"]["mine_dmg"] = player.mine_damage
                        self.save_upgrades()
                        SOUNDS["upgradeSound"].play()
                    else:
                        SOUNDS["cancelSound"].play()
                        self.damagemessage_timer = pygame.time.get_ticks()
                elif current_level["max"]:
                    SOUNDS["cancelSound"].play()
                    self.damagemessage_timer = pygame.time.get_ticks()
            else:
                self.damagemessage_timer = pygame.time.get_ticks()
                displayText(self.screen, "Max Level Reached!", 
                            (self.SW/2 + offset, self.SH*4/10), (255, 255, 255), self.small_font)

        if pygame.time.get_ticks() - self.damagemessage_timer <= 3000:
            if "current_level" in locals() and not current_level["max"]:
                message = "Not enough Coins!"
            else:
                message = "Not enough Coins!"
            displayText(self.screen, message, (self.SW/2 + offset, self.SH*4/10), (255, 0, 0), self.small_font)

    def handle_speed(self, player):
        offset = 260
        if self.shop_actions["Speed"]:
            self.shop_actions["Speed"] = False
            
            current_level = next((level for level in self.speed_levels if level["lvl"] == player.speed_level), None)
            
            if current_level:
                if not current_level["max"]:
                    upgrade_cost = current_level["nextprice"]
                    
                    if self.coins >= upgrade_cost:
                        self.change_jsonFile({"Coins": self.coins - upgrade_cost}, f"{DATA_PATH}/coins.json")
                        player.speed = current_level["value"]
                        player.dash_speed = current_level["dash_speed"]
                        player.speed_level += 1
                        
                        self.upgrades["Speed"]["lvl"] += 1
                        self.upgrades["Speed"]["value"] = player.speed
                        self.save_upgrades()
                        if self.playsounds:
                            SOUNDS["upgradeSound"].play()
                    else:
                        SOUNDS["cancelSound"].play()
                        self.speedmessage_timer = pygame.time.get_ticks()
                elif current_level["max"]:
                    SOUNDS["cancelSound"].play()
                    self.speedmessage_timer = pygame.time.get_ticks()
            else:
                self.speedmessage_timer = pygame.time.get_ticks()
                displayText(self.screen, "Max Level Reached!", 
                            (self.SW/2 - offset, self.SH*4/10), (255, 255, 255), self.small_font)

        if pygame.time.get_ticks() - self.speedmessage_timer <= 3000:
            if "current_level" in locals() and not current_level["max"]:
                message = "Not enough Coins!"
            else:
                message = "Not enough Coins!"
            displayText(self.screen, message, (self.SW/2 - offset, self.SH*4/10), (255, 0, 0), self.small_font)

    def draw_skin(self, img, pos, locked: bool, size=None, skin_num=0, is_special=False):
        if not size:
            size=img.get_size()
        surface = pygame.Surface(size)
        if not locked:
            if skin_num == self.selected_skin and is_special == self.other_skin:
                draw_aurora(surface, size[0], size[1], self.wave_params, self.timer, 0.2)
            surface.blit(pygame.transform.scale(img, (53, 60)), (53/2, 30))
        if locked:
            surface.blit(pygame.transform.scale(img, (53, 60)), (53/2, 30))
            surface.blit(self.lock_img, (0, 0))
        self.screen.blit(surface, pos)
        self.screen.blit(pygame.transform.scale(self.imgframe_img, (size[0] + 12, size[1] + 15)), (pos[0] - 6, pos[1] - 6))

        self.timer += 3
        return pygame.Rect(pos[0], pos[1], size[0], size[1])

    def handle_skins(self, cam, mouse, click):
        self.screen.fill("lightblue")
        displayText(self.screen, f"{self.coins}", (self.SW/2, self.SH*2/10), (0, 0, 0), self.font)
        self.coin_button(False, click)
        displayText(self.screen, "Each Price: 10", (self.SW/2, self.SH/2 + 10), (255, 0, 0), self.font)
        self.moreSkins_button(True, click, new_pos=(self.SW/2, self.SH - 100))
        for n in range(7):
            current_skin = self.draw_skin(self.skins_imgs[n], self.skins_pos[n], not self.skins_owned[str(n + 1)], (106, 120), n, True)

            if click:
                if current_skin.collidepoint(mouse):
                    if self.skins_owned[str(n + 1)]:
                        self.selected_skin = n
                        cam.player_skin_num = n
                        cam.reset()
                        skins_sounds[str(n)].play()
                        self.other_skin = True
                    elif not self.skins_owned[str(n + 1)]:
                        if self.coins >= self.skins["other_skins"]["Price"]:
                            self.change_jsonValue(f"{DATA_PATH}/coins.json", "Coins", self.coins - self.skins["other_skins"]["Price"])
                            self.change_jsonValue(f"{DATA_PATH}/skins.json", "other_skins", True, str(n + 1))
                            self.load_skins()

    def handle_shop(self, cam, click):
        mouse = pygame.mouse.get_pos()
        if self.skins["skin2"]["Owned"]:
            player_special_skin = self.player_skin_special
        else:
            player_special_skin = self.player_skin_special_hidden
        self.handle_speed(cam.player)
        self.handle_damage(cam.player)
        self.skin0_rect = self.draw_skin(self.player_skin1, (self.SW/3, self.SH*5.7/10), False, size=None, skin_num=0)
        self.skin1_rect = self.draw_skin(self.player_skin2, (self.SW*0.46, self.SH*5.7/10), not self.skins["skin1"]["Owned"], size=None, skin_num=1)
        self.skin2_rect = self.draw_skin(player_special_skin, (self.SW*0.588, self.SH*5.7/10), not self.skins["skin2"]["Owned"], size=(106, 120), skin_num=2)

        if click:
            if self.skin0_rect.collidepoint(mouse):
                self.other_skin = False
                self.selected_skin = 0
                cam.player_skin_num = 0
                SOUNDS["miauSound"].play()
            if self.skin1_rect.collidepoint(mouse):
                if self.skins["skin1"]["Owned"]:
                    self.other_skin = False
                    self.selected_skin = 1
                    cam.player_skin_num = 1
                    SOUNDS["deepmiauSound"].play()
                elif not self.skins["skin1"]["Owned"]:
                    if self.coins >= self.skins["skin1"]["Price"]:
                        self.change_jsonFile({"Coins": self.coins_file["Coins"] - self.skins["skin1"]["Price"]}, f"{DATA_PATH}/coins.json")
                        self.change_jsonValue(f"{DATA_PATH}/skins.json", "skin1", True, "Owned")
                        self.load_skins()
            if self.skin2_rect.collidepoint(mouse):
                if self.skins["skin2"]["Owned"]:
                    self.other_skin = False
                    self.selected_skin = 2
                    cam.player_skin_num = 2
                    SOUNDS["hmmSound"].play()
                elif not self.skins["skin2"]["Owned"]:
                    if self.coins >= self.skins["skin2"]["Price"]:
                        self.change_jsonFile({"Coins": self.coins_file["Coins"] - self.skins["skin2"]["Price"]}, f"{DATA_PATH}/coins.json")
                        self.change_jsonValue(f"{DATA_PATH}/skins.json", "skin2", True, "Owned")
                        self.load_skins()

        if not self.skins["skin1"]["Owned"]:
            displayText(self.screen, "Price: " + str(self.skins["skin1"]["Price"]), (self.SW*0.5, self.SH*7.6/10), (255, 0, 0), self.small_font)
        if not self.skins["skin2"]["Owned"]:
            displayText(self.screen, "Price: " + str(self.skins["skin2"]["Price"]), (self.SW*0.63, self.SH*7.6/10), (255, 0, 0), self.small_font)

        _rect_ = pygame.Rect(self.SW/2 - 90, self.SH - 150, 180, 45)
        if self.skins["skin1"]["Owned"] and self.skins["skin2"]["Owned"]:
            self.moreSkins_button(True, click, new_pos=_rect_.center)
        else:
            self._moreSkins_button(True, click, new_pos=_rect_.center)
            if _rect_.collidepoint(mouse):
                displayText(self.screen, "Unlock other skins first", (_rect_.centerx, _rect_.bottom), (255, 0, 0), self.small_font)

    def handle_achievements(self, click):
        with open(f"{DATA_PATH}/achievements.json", "r")as file:
            self.achivements = json.load(file)
        draw_text_wave(self.screen, "Achievements", self.font, (self.SW/2, 120), (255, 255, 255), pygame.time.get_ticks(), 3, 0.5)
        if self.achivements["Defeated Boss"]:
            surface = pygame.Surface((300, 100))
            surface.fill((0, 0, 0))
            pygame.draw.rect(surface, (200, 200, 200), surface.get_rect(), 3)
            font = pygame.font.Font(None, 36)
            text_surface = font.render("Defeated Boss", True, (255, 255, 255))
            surface.blit(text_surface, (15, surface.get_height()/2 - 12.5))
            surface.blit(self.boss_img, (surface.get_width() - self.boss_img.get_width()*1.2, 0))
            self.screen.blit(surface, (self.SW/2 - 150, self.SH/2))

        self.achivements_button(False, click)

    def controls_text(self, msgs: list, pos: list):
        for n in range(len(pos)):
            displayText(self.screen, msgs[n], pos[n], (0, 0, 0), self.font)

    def show_credits(self, click):
        if self.otheractions["Credits"]:
            self.credits_button(True, click)
            self.credits.run()

    def handle_minigame(self):
        if self.otheractions["Mini Game"]:
            process1 = multiprocessing.Process(target=mini_game.main)
            process1.start()
            self.CONTROLLER_MODE_ENABLED["Sound"] = True
            self.otheractions["Mini Game"] = False

    def handle_settings_sounds(self, mouse, click):
        self.startMenu_buttons[2](True, click, new_pos=(self.SW/2, 200))
        self.volume, self.dragging = self.settings_prop.draw_volume_slider(self.SW/2, self.SH/2, 300, self.volume, self.dragging, mouse, "SFX")
        for (name, sound), (skin_index, skin_sound) in zip(SOUNDS.items(), skins_sounds.items()):
            if name != "gameSound":
                sound.set_volume(self.volume)
            skin_sound.set_volume(self.volume)

        self.music_volume, self.dragging2 = self.settings_prop.draw_volume_slider(self.SW/2, self.SH/2 + 50, 300, self.music_volume, self.dragging2, mouse, "Music")
        SOUNDS["gameSound"].set_volume(self.music_volume)

    def settings(self, mouse, click):
        self.handle_settings_sounds(mouse, click)
        self.show_buttonInfo = self.settings_prop.checkbox_with_text(mouse, click, "Show Button Information", (self.SW/2, self.SH*2/3), (0, 0, 0), self.show_buttonInfo)

    def save_settings(self):
        self.change_jsonValue(f"{DATA_PATH}/settings.json", "Sounds", second_key="volume", new_value={"effect": self.volume, "bg": self.music_volume})
        self.change_jsonValue(f"{DATA_PATH}/settings.json", "Buttons", second_key="show_info", new_value=self.show_buttonInfo)

    def handle(self, cam, mouse, singleclick, click, video1_end, video2_end):
        if (video1_end or video2_end) and not self.CONTROLLER_MODE_ENABLED["Sound"]:
            pygame.mixer.set_num_channels(8)
        else:
            pygame.mixer.set_num_channels(0)

        self.screen.blit(self.bg, (0, 0))
        self.waves.draw()
        self.glitterscreen.draw()
        
        if singleclick:
            self.waves.add_water_drop(mouse[0], mouse[1])
        if not self.button_actions["Play"] and not self.button_actions["Settings"] and not self.shop_actions["Open"] and not self.otheractions["Achievements"] and not self.button_actions["Help"]:
            if self.enemy_switch.draw(singleclick, mouse):
                self.enemy.draw(0, 0, self.player, pygame.Rect(mouse[0], mouse[1], 5, 5), False)
                if self.achivements["Defeated Boss"]:
                    self.current_lvl.handle_event(click, mouse)
                    self.difficulty_lvl = self.current_lvl.draw(self.screen)
            self.start(singleclick)
            self.show_controls()
        elif self.button_actions["Settings"]:
            self.settings(mouse, click)
        elif self.button_actions["Help"]:
            self.help(singleclick)
        elif self.shop_actions["Open"]:
            self.shop(cam.player, cam, mouse, singleclick)
            if not self.shop_actions["Open"]:
                cam.reset()
        elif self.otheractions["Achievements"]:
            self.handle_achievements(singleclick)