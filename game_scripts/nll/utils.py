from pathlib import Path
import pygame
import math
import random
import time
import threading
import multiprocessing
import json
import os
import webbrowser

pygame.init()
pygame.joystick.init()

FPS = 60
# Farben
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 200, 0)
ORANGE = (255, 165, 0)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)

SAVE_DIR_NAME = "Baai.org"
LOCAL_APPDATA_PATH = Path(os.getenv("LOCALAPPDATA")) / SAVE_DIR_NAME
ASSETS_PATH = LOCAL_APPDATA_PATH / "assets"
SOUNDS_PATH = ASSETS_PATH / "sounds"
DATA_PATH = ASSETS_PATH / "data"

with open(f"{DATA_PATH}/settings.json", "r") as file:
    settings = json.load(file)

show_buttonInfo = settings["Buttons"]["show_info"]
sound_settings = settings["Sounds"]
effectvolume = sound_settings["volume"]["effect"]
bgvolume = sound_settings["volume"]["bg"]

SOUND_PATHS = {
    "gameSound": f"{SOUNDS_PATH}/game.wav",
    "miauSound": f"{SOUNDS_PATH}/menu/miau.wav",
    "deepmiauSound": f"{SOUNDS_PATH}/menu/miau_deep.wav",
    "hmmSound": f"{SOUNDS_PATH}/menu/hmm.wav",
    "upgradeSound": f"{SOUNDS_PATH}/menu/upgrade.wav",
    "cancelSound": f"{SOUNDS_PATH}/menu/cancel.wav",
    "buttonSound": f"{SOUNDS_PATH}/menu/button.wav",
    "walkSound": f"{SOUNDS_PATH}/player/walking.wav",
    "loseSound": f"{SOUNDS_PATH}/player/lose.wav",
    "explosionSound": f"{SOUNDS_PATH}/player/explosion2.wav",
    "collectSound": f"{SOUNDS_PATH}/player/collect.wav",
    "dashSound": f"{SOUNDS_PATH}/player/dash.wav",
    "attackSound": f"{SOUNDS_PATH}/enemies/attack.wav",
    "enemydieSound": f"{SOUNDS_PATH}/enemies/enemy_die.ogg",
    "bossattackSound": f"{SOUNDS_PATH}/enemies/boss_attack.wav",
    "bossdieSound": f"{SOUNDS_PATH}/enemies/boss_die.wav",
    "bossSound": f"{SOUNDS_PATH}/enemies/boss.wav",
}

SOUNDS = {}
for name, path in SOUND_PATHS.items():
    sound = pygame.mixer.Sound(path)
    if name != "gameSound":
        sound.set_volume(effectvolume)
    else:
        sound.set_volume(bgvolume)
    SOUNDS[name] = sound

skins_sounds = {}
for skin_id, path in {
    "0": "hmm",
    "1": "hmm",
    "2": "hmm",
    "3": "deep_hmm",
    "4": "high_hmm",
    "5": "arr",
    "6": "deep_hmm"
}.items():
    skins_sounds[skin_id] = pygame.mixer.Sound(f"{SOUNDS_PATH}/menu/{path}.wav")
    skins_sounds[skin_id].set_volume(effectvolume)

def displayText(display, msg, pos, textColor, font):
    obj = font.render(msg, True, textColor)
    rect = obj.get_rect(center=pos)
    display.blit(obj, rect)

class Settings:
    def __init__(self, screen):
        self.screen = screen
        self.settings_font = pygame.font.SysFont("Comic Sans MS", 40)
        self.clicked = False
        self.wait = 10

    def draw_volume_slider(self, x, y, width, volume, is_dragging, mouse_pos, info):
        handle_radius = 12
        slider_height = 6
        slider_rect = pygame.Rect(x, y, width, slider_height)
        handle_x = int(x + volume * width)
        handle_y = y + slider_height // 2

        mx, my = mouse_pos
        if pygame.mouse.get_pressed()[0]:
            if not is_dragging and abs(mx - handle_x) <= handle_radius and abs(my - handle_y) <= handle_radius:
                is_dragging = True
            if is_dragging:
                mx = max(x, min(mx, x + width))
                volume = (mx - x) / width
        else:
            is_dragging = False

        pygame.draw.rect(self.screen, (100, 100, 100), slider_rect)
        pygame.draw.circle(self.screen, (0, 200, 0), (int(x + volume * width), handle_y), handle_radius)
        displayText(self.screen, info, (slider_rect.centerx - slider_rect.w, slider_rect.centery), (0, 0, 0), self.settings_font)

        return volume, is_dragging

    def checkbox_with_text(self, mouse, click, msg, pos, textColor, checkbox_value, box_size=50, box_color=(100, 100, 100), tick_color=(0, 255, 0)):
        text_surface = self.settings_font.render(msg, True, textColor)
        text_rect = text_surface.get_rect(midright=(pos[0], pos[1]))
        text_rect.center = pos

        box_rect = pygame.Rect(text_rect.right + 10, text_rect.centery - box_size // 2, box_size, box_size)

        pygame.draw.rect(self.screen, box_color, box_rect, 2)

        if checkbox_value:
            pygame.draw.line(self.screen, tick_color, (box_rect.left + 4, box_rect.centery),
                            (box_rect.centerx, box_rect.bottom - 4), 3)
            pygame.draw.line(self.screen, tick_color, (box_rect.centerx, box_rect.bottom - 4),
                            (box_rect.right - 4, box_rect.top + 4), 3)

        if box_rect.collidepoint(mouse) and click and not self.clicked:
            self.clicked = True
            checkbox_value = not checkbox_value

        if self.clicked and not click:
            if self.wait > 0:
                self.wait -= 1
            else:
                self.wait = 10
                self.clicked = False

        self.screen.blit(text_surface, text_rect)
        return checkbox_value

class MagnetSlider:
    def __init__(self, centerx, y, width, height, options, font, font_color, capsule_color, slider_color, track_color):
        self.x = centerx - width // 2
        self.y = y
        self.width = width
        self.height = height
        self.options = options
        self.font = font
        self.font_color = font_color
        self.capsule_color = capsule_color
        self.slider_color = slider_color
        self.track_color = track_color

        self.num_options = len(options)
        self.segment_width = width // self.num_options
        self.current_index = 0

        self.handle_rect = pygame.Rect(self.x, y + 30, self.segment_width, height)

    def draw(self, screen):
        for i, option in enumerate(self.options):
            text_surface = self.font.render(option, True, self.font_color)
            text_rect = text_surface.get_rect(center=(self.x + i * self.segment_width + self.segment_width // 2, self.y))

            capsule_rect = pygame.Rect(text_rect.x - 10, text_rect.y - 5, text_rect.width + 20, text_rect.height + 10)
            pygame.draw.rect(screen, self.capsule_color, capsule_rect, border_radius=15)
            screen.blit(text_surface, text_rect)

        pygame.draw.rect(screen, self.track_color, (self.x, self.y + 30 + self.height // 2, self.width, 5))
        pygame.draw.rect(screen, self.slider_color, self.handle_rect)

        return self.options[self.current_index]

    def handle_event(self, click, mouse):
        if click and self.handle_rect.collidepoint(mouse):
            self.dragging = True
            if hasattr(self, 'dragging') and self.dragging:
                self.handle_rect.x = max(self.x, min(mouse[0] - self.handle_rect.width // 2, self.x + self.width - self.segment_width))
        elif not click:
            if hasattr(self, 'dragging') and self.dragging:
                self.dragging = False
                self.snap_to_segment()

    def snap_to_segment(self):
        relative_x = self.handle_rect.x - self.x
        self.current_index = round(relative_x / self.segment_width)
        self.handle_rect.x = self.x + self.current_index * self.segment_width

class SmoothSwitchButton:
    def __init__(self, x, y, width, height, knob_radius, on_color, off_color, border_color, screen):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.knob_radius = knob_radius
        self.on_color = on_color
        self.off_color = off_color
        self.border_color = border_color
        self.screen = screen
        
        self.knob_pos = x + knob_radius
        self.target_pos = x + knob_radius
        self.state = False

    def handle_event(self, click, mouse_pos):
        if click:
            mx, my = mouse_pos
            if self.x <= mx <= self.x + self.width and self.y <= my <= self.y + self.height:
                self.state = not self.state
                self.target_pos = self.x + self.width - self.knob_radius if self.state else self.x + self.knob_radius

    def update(self):
        self.knob_pos += (self.target_pos - self.knob_pos) * 0.2

    def draw(self, click, mouse_pos):
        self.handle_event(click, mouse_pos)
        self.update()
        pygame.draw.rect(self.screen, self.on_color if self.state else self.off_color, 
                         (self.x, self.y, self.width, self.height), border_radius=25)

        pygame.draw.circle(self.screen, (255, 255, 255), (int(self.knob_pos), self.y + self.height // 2), self.knob_radius)
        pygame.draw.rect(self.screen, self.border_color, 
                         (self.x, self.y, self.width, self.height), width=2, border_radius=25)
        return self.state

class SmoothSmokeParticle:
    def __init__(self, pos, size, color, lifetime, start_alpha):
        self.x, self.y = pos
        self.size = size
        self.color = color
        self.lifetime = lifetime
        self.current_lifetime = lifetime
        self.alpha = start_alpha

    def update(self):
        self.current_lifetime -= 1
        self.size += 0.3
        self.alpha = max(0, int(self.alpha * (self.current_lifetime / self.lifetime)))

    def draw(self, surface):
        if self.current_lifetime > 0:
            surf = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
            smooth_color = (*self.color[:3], self.alpha)
            pygame.draw.circle(surf, smooth_color, (self.size, self.size), int(self.size))
            surface.blit(surf, (self.x - self.size, self.y - self.size))

def smooth_smoke_effect(screen, mouse_pos, particles, max_particles):
    if len(particles) < max_particles:
        size = random.randint(8, 15)
        lifetime = random.randint(40, 80)
        color = (255, 255, 255)
        start_alpha = random.randint(150, 200)
        particles.append(SmoothSmokeParticle(mouse_pos, size, color, lifetime, start_alpha))

    for particle in particles[:]:
        particle.update()
        particle.draw(screen)
        if particle.current_lifetime <= 0:
            particles.remove(particle)

class WaterWaveEffect:
    def __init__(self, image, screen, amplitude=5, frequency=0.1, speed=5):
        self.original_image = image
        self.screen = screen
        self.amplitude = amplitude
        self.frequency = frequency
        self.speed = speed
        self.time = 0
        self.water_drops = []

    def add_water_drop(self, x, y):
        self.water_drops.append({"pos": [x, y], "radius": 5, "max_radius": 50, "speed": 2})

    def update_water_drops(self):
        for drop in self.water_drops[:]:
            drop["radius"] += drop["speed"]
            if drop["radius"] > drop["max_radius"]:
                self.water_drops.remove(drop)

    def apply_wave(self):
        width, height = self.original_image.get_size()
        wave_image = pygame.Surface((width, height), pygame.SRCALPHA)
        for y in range(height):
            offset = int(self.amplitude * math.sin(self.frequency * y + self.time))
            line = self.original_image.subsurface((0, y, width, 1))
            wave_image.blit(line, (offset, y))
        return wave_image

    def draw(self):
        self.time += self.speed * 0.01

        wave_image = self.apply_wave()
        self.screen.blit(wave_image, (0, 0))

        self.update_water_drops()
        for drop in self.water_drops:
            pygame.draw.circle(self.screen, (173, 216, 230, 100), drop["pos"], drop["radius"], 1)

class GlitterEffect:
    def __init__(self, screen, intensity=20, sparkle_color=(255, 255, 255), sparkle_size=2, speed=1, spawn_delay=0.1, max_top=100):
        self.screen = screen
        self.intensity = intensity
        self.sparkle_color = sparkle_color
        self.sparkle_size = sparkle_size
        self.speed = speed
        self.spawn_delay = spawn_delay
        self.max_top = max_top
        self.sparkles = []
        self.last_spawn_time = time.time()

    def create_sparkle(self, target_rect=None):
        width, height = self.screen.get_size()
        area = target_rect or pygame.Rect(0, 0, width, height)

        x = random.randint(area.left, area.right - 1)
        y = area.bottom - random.randint(1, 10)
        alpha = random.randint(100, 255)
        drift = random.uniform(-0.3, 0.3)
        max_y = y - random.randint(50, self.max_top)
        self.sparkles.append({'pos': [x, y], 'alpha': alpha, 'drift': drift, 'max_y': max_y})

    def update(self, target_rect=None):
        width, height = self.screen.get_size()
        area = target_rect or pygame.Rect(0, 0, width, height)
        current_time = time.time()

        if len(self.sparkles) < self.intensity and current_time - self.last_spawn_time >= self.spawn_delay:
            self.create_sparkle(target_rect)
            self.last_spawn_time = current_time

        for sparkle in self.sparkles[:]:
            sparkle['pos'][1] -= self.speed
            sparkle['pos'][0] += sparkle['drift']
            sparkle['alpha'] = max(50, min(255, sparkle['alpha'] + random.choice([-1, 1])))
            if sparkle['pos'][1] <= sparkle['max_y']:
                self.sparkles.remove(sparkle)

    def draw(self, target_surface=None):
        surface = target_surface or self.screen

        for sparkle in self.sparkles:
            s = pygame.Surface((self.sparkle_size, self.sparkle_size), pygame.SRCALPHA)
            s.fill((*self.sparkle_color, sparkle['alpha']))
            surface.blit(s, sparkle['pos'])
        self.update(target_surface)

class SmoothMovingImage:
    def __init__(self, image_path, screen):
        pygame.init()
        self.screen = screen
        screen_size = self.screen.get_size()
        
        # Laden des Bildes und Skalierung
        self.image_original = pygame.image.load(image_path).convert_alpha()
        self.image_rect = self.image_original.get_rect()
        self.image_rect.center = (screen_size[0] // 2, screen_size[1] // 2)
        self.screen_width, self.screen_height = screen_size
        
        self.velocity = [2, 1]
        self.angle = 0
        self.angular_velocity = 0.7

    def move(self):
        self.image_rect.x += self.velocity[0]
        self.image_rect.y += self.velocity[1]

        if self.image_rect.left <= 0 or self.image_rect.right >= self.screen_width:
            self.velocity[0] = -self.velocity[0]
        if self.image_rect.top <= 0 or self.image_rect.bottom >= self.screen_height:
            self.velocity[1] = -self.velocity[1]

    def draw(self):
        self.angle = (self.angle + self.angular_velocity) % 360
        rotated_image = pygame.transform.rotate(self.image_original, self.angle)
        rotated_rect = rotated_image.get_rect(center=self.image_rect.center)
        self.screen.blit(rotated_image, rotated_rect.topleft)
        self.move()

def draw_aurora(surface, width, height, wave_params, time_offset, scale=1.0):
    surface.fill((0, 0, 20))

    for wave in wave_params:
        color = wave['color']
        amplitude = wave['amplitude'] * scale
        frequency = wave['frequency'] / scale
        speed = wave['speed']
        vertical_offset = wave['offset'] * scale

        for y in range(0, height):
            alpha = max(0, int(255 * math.exp(-(y - height//2) ** 2 / (2 * amplitude ** 2))))
            if alpha > 0:
                x_offset = int(amplitude * math.sin(frequency * y + time_offset * speed))
                start_x = max(0, width // 2 + x_offset - int(200 * scale))
                end_x = min(width, width // 2 + x_offset + int(200 * scale))

                line_surface = pygame.Surface((width, 1), pygame.SRCALPHA)
                pygame.draw.line(line_surface, (*color, alpha), (start_x, 0), (end_x, 0))
                surface.blit(line_surface, (0, y))

def move_image_left(display, image, action, final_offset, current_x_pos, speed=10, text_char=">", 
                    font=pygame.font.SysFont("Comic Sans MS", 40), text_color=(0, 0, 0)):
    image_width, image_height = image.get_size()

    initial_x_pos = 0
    final_x_pos = -image_width + final_offset
    target_x_pos = final_x_pos if action else initial_x_pos

    delta_x = target_x_pos - current_x_pos
    if abs(delta_x) > 0.1:
        if delta_x * 0.1 * (1 - math.exp(-0.05 * abs(delta_x))) >= 1:
            current_x_pos += delta_x * 0.1 * (1 - math.exp(-0.05 * abs(delta_x)))
        else: current_x_pos += delta_x * 0.1

    surface = pygame.Surface((image_width, image_height), pygame.SRCALPHA)
    surface.fill((0, 0, 0, 0))
    surface.blit(image, (0, 0))

    text_x_pos = current_x_pos + image_width
    text_y_pos = image_height / 2 - font.get_height() / 2
    display.blit(surface, (current_x_pos, 0))

    text_surface = font.render(text_char, True, text_color)
    display.blit(text_surface, (text_x_pos, text_y_pos))

    return current_x_pos, surface.get_rect(left=current_x_pos)

def get_image(sheet: pygame.image, frame: int, width: int, height: int, y: int, colour: pygame.Color):
    image = pygame.Surface((width, height)).convert_alpha()
    image.blit(sheet, (0, 0), ((frame * width), y, width, height))
    image.set_colorkey(colour)

    return image

def displayRotatingText(display, msg, pos, textColor, font, time, max_angle = 15, speed = 1):
    text_surface = font.render(msg, True, textColor)
    text_rect = text_surface.get_rect(center=pos)

    angle = math.sin(time * speed) * max_angle
    rotated_surface = pygame.transform.rotate(text_surface, angle)
    rotated_rect = rotated_surface.get_rect(center=pos)
    display.blit(rotated_surface, rotated_rect)

def draw_text_wave(display, text, font, position, color, time, amplitude=10, frequency=5):
    total_width = sum(font.render(char, True, color).get_width() for char in text)
    x, y = position
    x -= total_width // 2

    for i, char in enumerate(text):
        offset = amplitude * math.sin(2 * math.pi * (time / 1000 * frequency - i / len(text)))
        char_surface = font.render(char, True, color)
        char_width = char_surface.get_width()
        display.blit(char_surface, (x, y + offset))
        x += char_width

def draw_progress_bar(surface, width, height, progress, title="Loading", bar_color=(0, 128, 255), bg_color=(30, 30, 30), text_color=(255, 255, 255), border_color=(255, 255, 255)):
    surface_rect = surface.get_rect()
    center_x, center_y = surface_rect.center

    bar_width = int(width * 0.8)
    bar_height = int(height * 0.1)
    bar_x = center_x - bar_width // 2
    bar_y = center_y - bar_height // 2 + height // 8
    
    pygame.draw.rect(surface, bg_color, (bar_x, bar_y, bar_width, bar_height))
    
    progress_width = int((progress / 100) * bar_width)
    pygame.draw.rect(surface, bar_color, (bar_x, bar_y, progress_width, bar_height))
    pygame.draw.rect(surface, border_color, (bar_x, bar_y, bar_width, bar_height), 2)

    font = pygame.font.SysFont("Arial", 24)
    title_surface = font.render(title, True, text_color)
    percentage_surface = font.render(f"{int(progress)}%", True, text_color)

    title_x = center_x - title_surface.get_width() // 2
    title_y = bar_y - title_surface.get_height() - 10
    percentage_x = center_x - percentage_surface.get_width() // 2
    percentage_y = bar_y + bar_height // 2 - percentage_surface.get_height() // 2

    surface.blit(title_surface, (title_x, title_y))
    surface.blit(percentage_surface, (percentage_x, percentage_y))

class ScrollableTextDisplay:
    def __init__(self, screen, text_list, font, text_color, surface_width, surface_height, bg_color, scroll_speed):
        self.screen = screen
        self.text_list = text_list
        self.font = font
        self.text_color = text_color
        self.surface_width = surface_width
        self.surface_height = surface_height
        self.bg_color = bg_color
        self.scroll_speed = scroll_speed

        self.transparent_surface = pygame.Surface((surface_width, surface_height), pygame.SRCALPHA)
        self.transparent_surface.fill(bg_color)
        self.text_height = font.size("Tg")[1] + 10  # Height of a single line with padding
        self.content_height = len(text_list) * self.text_height

        self.scroll_offset = 0
        self.scroll_bar_width = 20
        self.running = True

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 4:
                    self.scroll_offset = max(self.scroll_offset - self.scroll_speed, 0)
                elif event.button == 5:
                    self.scroll_offset = min(self.scroll_offset + self.scroll_speed, max(0, self.content_height - self.surface_height))

    def update_scroll_offset(self):
        mouse_pos = pygame.mouse.get_pos()
        if mouse_pos[1] <= 100:
            distance_from_top = 100 - mouse_pos[1]
            speed = self.scroll_speed * (distance_from_top * 0.005)
            self.scroll_offset = max(self.scroll_offset - speed, 0)
        elif mouse_pos[1] >= self.surface_height - 100:
            distance_from_bottom = mouse_pos[1] - (self.surface_height - 100)
            speed = self.scroll_speed * (distance_from_bottom * 0.005)
            self.scroll_offset = min(self.scroll_offset + speed, max(0, self.content_height - self.surface_height))

    def render(self):
        self.transparent_surface.fill(self.bg_color)

        y_offset = -self.scroll_offset
        for msg in self.text_list:
            text_surface = self.font.render(msg, True, self.text_color)
            text_rect = text_surface.get_rect(topleft=(10, y_offset))
            if 0 <= y_offset <= self.surface_height - self.text_height:
                self.transparent_surface.blit(text_surface, text_rect)
            y_offset += self.text_height

        self.screen.blit(self.transparent_surface, (0, 0))
        
        if self.content_height > self.surface_height:
            scroll_bar_height = max((self.surface_height / self.content_height) * self.surface_height, 20)
            scroll_bar_y = (self.scroll_offset / self.content_height) * self.surface_height
            pygame.draw.rect(self.screen, (200, 200, 200),
                             (self.surface_width - self.scroll_bar_width, scroll_bar_y, self.scroll_bar_width, scroll_bar_height))

    def run(self):
        self.handle_events()
        self.update_scroll_offset()
        self.render()

class ImageButton:
    def __init__(self, screen, msgs, msg, pos, size, buttonImage, active_buttonImage, textColor, font, info=None, moveUp_by=10):
        self.screen = screen
        self.msgs = msgs
        self.msg = msg
        self.img = pygame.transform.scale(buttonImage, size).convert_alpha()
        self.active_image = pygame.transform.scale(active_buttonImage, size).convert_alpha()
        self.textColor = textColor
        self.font = font
        self.small_font = pygame.font.SysFont("Liberation Serif", 25)
        self.orig_pos = pos
        self.rect = self.img.get_rect(center=(pos))
        self.move_up = moveUp_by
        self.clicked = False
        self.cool_down = 10
        self.base_y = self.rect.y
        self.hover_progress = 0.0
        self.hover_speed = 0.1
        self.show_info = show_buttonInfo
        self.info = info

    def set_images(self, image, both=True):
        if both:
            self.img = self.active_image = image
        else:
            self.img, self.active_image = image

    def update(self, show_buttonText, click, new_pos):
        mouse = pygame.mouse.get_pos()

        if new_pos:
            self.rect.center = new_pos
        else:
            self.rect.center = self.orig_pos
        self.base_y = self.rect.y


        hovering = self.rect.collidepoint(mouse)

        if hovering:
            self.hover_progress = min(1.0, self.hover_progress + self.hover_speed)
            if self.info and self.show_info:
                displayText(self.screen, self.info, (self.rect.centerx, self.rect.bottom + self.rect.h/4), (0, 0, 0), self.small_font)
        else:
            self.hover_progress = max(0.0, self.hover_progress - self.hover_speed)

        eased_offset = self.move_up * (1 - math.cos(math.pi * self.hover_progress)) / 2
        current_img = self.active_image if hovering else self.img

        if hovering and click and not self.clicked:
            self.clicked = True
            self.msgs[self.msg] = not self.msgs[self.msg]
            SOUNDS["buttonSound"].play()

        if self.clicked:
            if self.cool_down > 0:
                self.cool_down -= 1
            else:
                self.cool_down = 10
                self.clicked = False

        self.screen.blit(current_img, (self.rect.x, self.base_y - eased_offset))

        if show_buttonText:
            displayText(self.screen, self.msg, (self.rect.centerx, self.rect.centery - eased_offset), self.textColor, self.font)

    def __call__(self, show_buttonText, click, new_pos=None):
        return self.update(show_buttonText, click, new_pos)