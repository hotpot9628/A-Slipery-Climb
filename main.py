import pygame
import sys
import math
import random
import os
import json
from enum import Enum
import i18n
import backdrop
import achievements
import chatter
import paths
# Register chatter translations (GameObject text renders via i18n.text)
for _ci, _cen in enumerate(chatter.LINES["en"]):
    for _code, _lines in chatter.LINES.items():
        if _code != "en" and _ci < len(_lines):
            i18n.STRINGS.setdefault(_code, {})[_cen] = _lines[_ci]
import time

pygame.init()
pygame.mixer.init()  # init the mixer

# Screen setup
screen_info = pygame.display.Info()
WIDTH, HEIGHT = screen_info.current_w, screen_info.current_h
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.NOFRAME)
pygame.display.set_caption("A SLIPERY CLIMB")

# Colors
NIGHT_WHITE = (178, 178, 178)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 127)
YELLOW = (255, 255, 0)
SKY_BLUE = (25, 25, 112)
ORANGE = (255, 165, 0)
LIGHT_BLUE = (173, 216, 230)
LIGHT_GREEN = (144, 238, 144)
ICE_BLUE = (121, 151, 161, 150)
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)

# Explosion colors
EXPLOSION_RED_INNER = (255, 50, 0, 255)
EXPLOSION_RED_MIDDLE = (255, 100, 0, 255)
EXPLOSION_RED_OUTER = (255, 150, 50, 255)
EXPLOSION_GREEN_INNER = (50, 255, 0, 255)
EXPLOSION_GREEN_MIDDLE = (100, 255, 50, 255)
EXPLOSION_GREEN_OUTER = (150, 255, 100, 255)

class GameState(Enum):
    MENU = 1
    SAVES = 4
    ACHIEVEMENTS = 5
    PLAYING = 2
    SETTINGS = 3
    CUTSCENE = 6

# Game constants
ground_level = HEIGHT - 200

# ========== Backdrop: snow mountain + summit cabin (clearer the higher you climb) ==========
backdrop_layer = backdrop.Backdrop(WIDTH, HEIGHT, sky=SKY_BLUE,
                                   ground_level=ground_level,
                                   final_height=18000, summit_x=6000, summit_top=18000)
clock = pygame.time.Clock()
FPS = 60
font = i18n.get_font(max(10, int(48 * i18n.scale())))
small_font = i18n.get_font(max(10, int(24 * i18n.scale())))
medium_font = i18n.get_font(max(10, int(72 * i18n.scale())))
big_font = i18n.get_font(max(10, int(120 * i18n.scale())))

# World bounds
WORLD_LEFT_BORDER = -float('inf')
WORLD_RIGHT_BORDER = float('inf')
WORLD_TOP_BORDER = -float('inf')
WORLD_BOTTOM_BORDER = ground_level

# Player stats
player_width = 50
player_height = 50
player_x = 100
player_y = ground_level - player_height
player_velocity_x = 0
player_velocity_y = 0
player_gravity = 0.5
player_max_horizontal_speed = 15
ice_friction = 0.02
summit_friction = 0.60   # more friction on the summit platform, but still slides
air_resistance = 0.005
player_is_on_ground = False
player_ground_platform = None
player_facing_right = True

# Candy system
candy_power_base = 5.0
candy_power_max = 25.0
candies = []
candy_radius = 8
candy_lifetime = 3.0
candy_trail_length = 15
candy_gravity = 0.5
MIN_THROW_DISTANCE = 0
MAX_THROW_DISTANCE = 300

# Click to throw
can_throw = True
mouse_button_down = False

# Explosion system
explosions = []
explosion_max_radius = 60
explosion_duration = 0.4
explosion_force = 6.0

# Screen shake
screen_shake = 0.0
screen_shake_decay = 0.9
screen_shake_offset_x = 0
screen_shake_offset_y = 0

# Camera
camera_x = 0
camera_y = 0
camera_smoothness = 0.1

# Player momentum
player_base_speed = 8.0
player_velocity_decay_threshold = 12.0
player_velocity_decay_factor = 0.03
player_momentum_decay = 0.05
player_last_ground_time = 0.0
player_continuous_air_time = 0.0
player_momentum = 1.0

# Cursor
cursor_radius = 10
cursor_width = 2
cursor_color = NIGHT_WHITE
cursor_border_color = BLACK

# Game state
current_state = GameState.MENU
level_cleared = False
summit_locked = False
summit_msg_timer = 0.0
summit_msg_shown = False
SUMMIT_MSG_TIME = 4.5
SUMMIT_MSG_HEIGHT = 13900

# Random chatter
chatter_timer = 22.0
chatter_text = ""
chatter_life = 0.0
chatter_last = None
CHATTER_TIME = 4.0
CHATTER_MIN, CHATTER_MAX = 18.0, 38.0

# Cutscenes
cutscene_kind = "intro"
cutscene_t = 0.0
cutscene_len = 9.0
CUTSCENE_INTRO_LEN = 9.5
CUTSCENE_WIN_LEN = 8.5
cutscene_hold = False
current_slot = 1

# File paths
SAVE_FILE = paths.user("save_data.json")
SETTINGS_FILE = paths.user("settings.json")

# Sound settings
sound_volume = 0.7
music_volume = 0.5

# Entry protection
player_entry_time = 0.0
ENTRY_PROTECTION_TIME = 0.5  

# ========== Snowflake system ==========
class Snowflake:
    """Snowflake particle."""
    def __init__(self, x=None, y=None, size=None, speed=None, sway=None):
        self.x = x if x is not None else random.uniform(0, WIDTH)
        self.y = y if y is not None else random.uniform(-HEIGHT, 0)
        self.size = size if size is not None else random.uniform(2, 8)
        self.speed = speed if speed is not None else random.uniform(1, 4)
        self.sway = sway if sway is not None else random.uniform(0.5, 2)
        self.sway_offset = random.uniform(0, math.pi * 2)
        self.alpha = random.randint(100, 255)
        
        # Flake shape variation
        self.rotation = random.uniform(0, math.pi * 2)
        self.rotation_speed = random.uniform(0.5, 2)
        
        # Subtle twinkle
        self.flicker_speed = random.uniform(1, 3)
        self.flicker_offset = random.uniform(0, math.pi * 2)
    
    def update(self, dt):
        """Update the flake position."""
        # Falling
        self.y += self.speed * dt * 60
        
        # Swaying
        self.x += math.sin(self.sway_offset) * self.sway * 0.3 * dt * 60
        self.sway_offset += 0.05 * dt * 60
        
        # Rotation
        self.rotation += self.rotation_speed * dt * 60
        
        # Recycle flakes that left the screen
        if self.y > HEIGHT + 50:
            self.y = -50
            self.x = random.uniform(0, WIDTH)
        
        if self.x < -50:
            self.x = WIDTH + 50
        elif self.x > WIDTH + 50:
            self.x = -50
    
    def draw(self, screen):
        """Draw the flake."""
        # Current alpha (with twinkle)
        flicker = 0.5 + 0.3 * math.sin(self.flicker_offset + pygame.time.get_ticks() / 1000 * self.flicker_speed)
        current_alpha = int(min(255, self.alpha * flicker))
        
        # Create an alpha surface
        snow_surface = pygame.Surface((int(self.size * 2), int(self.size * 2)), pygame.SRCALPHA)
        
        # Pick a flake shape by size
        if self.size < 4:
            # Small flake: simple dot
            pygame.draw.circle(snow_surface, (255, 255, 255, current_alpha), 
                              (int(self.size), int(self.size)), int(self.size))
        else:
            # Large flake: hexagon or star
            center_x = self.size
            center_y = self.size
            points = []
            num_points = 6
            
            for i in range(num_points * 2):
                angle = self.rotation + (i * math.pi / num_points)
                radius = self.size if i % 2 == 0 else self.size * 0.6
                x = center_x + math.cos(angle) * radius
                y = center_y + math.sin(angle) * radius
                points.append((x, y))
            
            pygame.draw.polygon(snow_surface, (255, 255, 255, current_alpha), points)
            
            # Add a bright center
            inner_radius = self.size * 0.3
            pygame.draw.circle(snow_surface, (255, 255, 255, current_alpha), 
                              (int(center_x), int(center_y)), int(inner_radius))
        
        screen.blit(snow_surface, (int(self.x - self.size), int(self.y - self.size)))


class SnowSystem:
    """Snowflake system manager."""
    def __init__(self, snowflake_count=150):
        self.snowflakes = []
        self.snowflake_count = snowflake_count
        self.enabled = True
        self.intensity = 1.0  # flake density
        
        self.init_snowflakes()
    
    def init_snowflakes(self):
        """Create all flakes."""
        self.snowflakes = []
        for _ in range(self.snowflake_count):
            self.snowflakes.append(Snowflake())
    
    def update(self, dt):
        """Update all flakes."""
        if not self.enabled:
            return
        
        for snowflake in self.snowflakes:
            snowflake.update(dt)
    
    def draw(self, screen):
        """Draw all flakes."""
        if not self.enabled:
            return
        
        # Sort by size: small first, large later (depth)
        sorted_snowflakes = sorted(self.snowflakes, key=lambda s: s.size)
        for snowflake in sorted_snowflakes:
            snowflake.draw(screen)
    
    def set_intensity(self, intensity):
        """Set flake density (0-1)."""
        self.intensity = max(0, min(1, intensity))
        target_count = int(self.snowflake_count * self.intensity)
        
        if len(self.snowflakes) > target_count:
            self.snowflakes = self.snowflakes[:target_count]
        elif len(self.snowflakes) < target_count:
            for _ in range(target_count - len(self.snowflakes)):
                self.snowflakes.append(Snowflake())
    
    def reset(self):
        """Respawn all flakes."""
        for snowflake in self.snowflakes:
            snowflake.y = random.uniform(-HEIGHT, 0)
            snowflake.x = random.uniform(0, WIDTH)


# Snowflake system instance
snow_system = SnowSystem(snowflake_count=120)

# ========== Sound system ==========
class SoundManager:
    def __init__(self):
        self.sound_volume = 0.7
        self.music_volume = 0.5
        self.bgm_playing = False
        
        # Sound cache
        self.sounds = {
            'throw': [],
            'explosion': []
        }
        
        self.load_sounds()
    
    def load_sounds(self):
        """Load all sounds."""
        # Load BGM
        try:
            bgm_path = paths.asset("sounds", "BGM.wav")
            if os.path.exists(bgm_path):
                pygame.mixer.music.load(bgm_path)
        except Exception as e:
            print(f"Could not load BGM: {e}")
        
        # Load throw sound
        for i in range(1, 3):
            try:
                path = paths.asset("sounds", f"throw-{i}.wav")
                if os.path.exists(path):
                    sound = pygame.mixer.Sound(path)
                    self.sounds['throw'].append(sound)
            except Exception as e:
                print(f"Could not load throw-{i}.wav: {e}")
        
        # Load explosion sound
        for i in range(1, 3):
            try:
                path = paths.asset("sounds", f"explosion-{i}.wav")
                if os.path.exists(path):
                    sound = pygame.mixer.Sound(path)
                    self.sounds['explosion'].append(sound)
            except Exception as e:
                print(f"Could not load explosion-{i}.wav: {e}")
    
    def play_bgm(self):
        """Play background music."""
        if not self.bgm_playing:
            pygame.mixer.music.set_volume(self.music_volume)
            pygame.mixer.music.play(-1)  # loop
            self.bgm_playing = True
    
    def stop_bgm(self):
        """Stop background music."""
        pygame.mixer.music.stop()
        self.bgm_playing = False
    
    def set_music_volume(self, volume):
        """Set music volume."""
        self.music_volume = volume
        pygame.mixer.music.set_volume(volume)
    
    def set_sound_volume(self, volume):
        """Set sound volume."""
        self.sound_volume = volume
        for sound_list in self.sounds.values():
            for sound in sound_list:
                sound.set_volume(volume)
    
    def play_throw(self):
        """Play a random throw sound."""
        if self.sounds['throw']:
            sound = random.choice(self.sounds['throw'])
            sound.play()
    
    def play_explosion(self):
        """Play a random explosion sound."""
        if self.sounds['explosion']:
            sound = random.choice(self.sounds['explosion'])
            sound.play()

# Sound manager instance
sound_manager = SoundManager()

# ========== Utility functions ==========
def apply_camera_offset(x, y):
    return x - camera_x + screen_shake_offset_x, y - camera_y + screen_shake_offset_y

def draw_text(screen, text, x, y, color=NIGHT_WHITE, font_obj=None, align="center"):
    if font_obj is None:
        font_obj = font
    text_surface = font_obj.render(text, True, color)
    text_rect = text_surface.get_rect()
    
    if align == "center":
        text_rect.center = (x, y)
    elif align == "left":
        text_rect.topleft = (x, y)
    elif align == "right":
        text_rect.topright = (x, y)
    
    screen.blit(text_surface, text_rect)
    return text_rect

# ========== GameObject class ==========
class GameObject:
    def __init__(self, obj_type='platform', **kwargs):
        self.obj_type = obj_type
        
        self.x = kwargs.get('x', 0)
        self.y = kwargs.get('y', 0)
        self.width = kwargs.get('width', 100)
        self.height = kwargs.get('height', 20)
        
        if self.obj_type == 'platform' or self.obj_type == 'none':
            self._init_platform(kwargs)
        elif self.obj_type == 'text':
            self._init_text(kwargs)
    
    def _init_platform(self, kwargs):
        self.start_x = self.x
        self.start_y = ground_level - self.y
        
        end_x = kwargs.get('end_x', None)
        end_y = kwargs.get('end_y', None)
        self.end_x = end_x if end_x is not None else self.start_x
        self.end_y = ground_level - end_y if end_y is not None else self.start_y
        
        self.border_color = kwargs.get('border_color', None)
        self.move_speed = kwargs.get('move_speed', 2)
        self.texture_type = kwargs.get('texture_type', None)
        # Curved movement: curve='arc' (bulge) or 'sine' (wobble)
        self.curve = kwargs.get('curve', None)
        self.curve_amp = kwargs.get('curve_amp', 120)
        
        color = kwargs.get('color', None)
        if color is None:
            self.is_moving = not (self.start_x == self.end_x and self.start_y == self.end_y)
            self.color = ORANGE if self.is_moving else LIGHT_GREEN
        else:
            self.color = color
            self.is_moving = not (self.start_x == self.end_x and self.start_y == self.end_y)
        
        self.x = self.start_x
        self.y = self.start_y
        
        dx = self.end_x - self.start_x
        dy = self.end_y - self.start_y
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance > 0:
            self.direction_x = dx / distance
            self.direction_y = dy / distance
        else:
            self.direction_x = 0
            self.direction_y = 0
            
        self.distance = distance
        self.progress = 0
        self.forward = True
        
        self.last_x = self.x
        self.last_y = self.y
    
    def _init_text(self, kwargs):
        self.text = kwargs.get('text', '')
        self.text_color = kwargs.get('text_color', NIGHT_WHITE)
        self.text_size = kwargs.get('text_size', None)
        
        if self.text_size is not None:
            self.text_font = i18n.get_font(max(10, int(self.text_size * i18n.scale())))
        else:
            self.text_font = kwargs.get('text_font', font)
        
        self.text_align = kwargs.get('text_align', 'topleft')
        self.text_visible = kwargs.get('text_visible', True)
        self.text_permanent = kwargs.get('text_permanent', True)
        self.text_duration = kwargs.get('text_duration', 5.0)
        self.text_timer = 0.0
        
        self.y = ground_level - kwargs.get('y', 0)
        
        self.render_text_surface()
    
    def _update_text_rect_position(self):
        if self.text_align == "center":
            self.text_rect.center = (self.x, self.y)
        elif self.text_align == "topleft":
            self.text_rect.topleft = (self.x, self.y)
        elif self.text_align == "topright":
            self.text_rect.topright = (self.x, self.y)
        elif self.text_align == "bottomleft":
            self.text_rect.bottomleft = (self.x, self.y)
        elif self.text_align == "bottomright":
            self.text_rect.bottomright = (self.x, self.y)
    
    def render_text_surface(self):
        label = i18n.text(self.text)
        self.text_surface = self.text_font.render(label, True, self.text_color)
        self.text_rect = self.text_surface.get_rect()
        self._update_text_rect_position()

    def update(self, dt):
        if self.obj_type == 'platform' or self.obj_type == 'none':
            self._update_platform(dt)
        elif self.obj_type == 'text':
            self._update_text(dt)
    
    def _update_platform(self, dt):
        if self.is_moving:
            self.last_x = self.x
            self.last_y = self.y
            
            move_distance = self.move_speed * dt * 60
            
            if self.forward:
                self.progress += move_distance
                if self.progress >= self.distance:
                    self.progress = self.distance
                    self.forward = False
            else:
                self.progress -= move_distance
                if self.progress <= 0:
                    self.progress = 0
                    self.forward = True
            
            base_x = self.start_x + self.direction_x * self.progress
            base_y = self.start_y + self.direction_y * self.progress
            if self.curve and self.distance > 0:
                t = self.progress / self.distance
                if self.curve == 'arc':
                    off = math.sin(math.pi * t) * self.curve_amp
                else:                      # 'sine'
                    off = math.sin(2.0 * math.pi * t) * self.curve_amp
                # Perpendicular offset -> curved path
                base_x += -self.direction_y * off
                base_y += self.direction_x * off
            self.x = base_x
            self.y = base_y
    
    def _update_text(self, dt):
        if not self.text_permanent and self.text_visible:
            self.text_timer += dt
            if self.text_timer >= self.text_duration:
                self.text_visible = False
                
    def check_collision(self, player_x, player_y, player_width, player_height, player_velocity_y):
        if self.obj_type != 'platform':
            return None, 0, 0
            
        platform_top = self.y - self.height
        
        if (player_x < self.x + self.width and
            player_x + player_width > self.x and
            player_y < self.y and
            player_y + player_height > platform_top):
            
            return self._handle_collision(player_x, player_y, player_width, player_height, player_velocity_y)
        
        return None, 0, 0

    def _handle_collision(self, player_x, player_y, player_width, player_height, player_velocity_y):
        platform_top = self.y - self.height
        
        dx = (player_x + player_width/2) - (self.x + self.width/2)
        dy = (player_y + player_height/2) - (platform_top + self.height/2)
        
        overlap_x = (player_width/2 + self.width/2) - abs(dx)
        overlap_y = (player_height/2 + self.height/2) - abs(dy)
        
        if overlap_x < overlap_y:
            if dx > 0:
                return "side", self.x + self.width, player_y
            else:
                return "side", self.x - player_width, player_y
        else:
            if dy > 0:
                return "bottom", player_x, self.y
            else:
                return "top", player_x, platform_top - player_height
    
    def draw_with_texture(self, screen):
        if self.obj_type != 'platform':
            self.draw(screen)
            return

        if not TEXTURES_LOADED:
            self.draw(screen)
            return

        draw_x, draw_y = apply_camera_offset(self.x, self.y)
        platform_top = draw_y - self.height

        origin_x, corners = self._texture_span()
        phase = int((self.x - origin_x) % complete_nine_patch.center.get_width())
        complete_nine_patch.draw(screen, draw_x, platform_top, self.width, self.height,
                                 phase=phase, corners=corners)

    def _texture_span(self):
        """Platforms in the same row share a texture origin and drop the seam-side corner."""
        info = getattr(self, '_tex_info', None)
        if info is not None:
            return info
        if getattr(self, 'is_moving', False):
            return (self.x, (True, True, True, True))

        top = self.y - self.height
        peers = []
        for obj in game:
            if getattr(obj, 'obj_type', '') != 'platform':
                continue
            if getattr(obj, 'texture_type', None) is None or getattr(obj, 'is_moving', False):
                continue
            if abs((obj.y - obj.height) - top) <= 1.0:
                peers.append(obj)
        peers.sort(key=lambda obj: obj.x)
        i = peers.index(self)
        left_open = True
        while i > 0 and abs(peers[i - 1].x + peers[i - 1].width - peers[i].x) <= 1.0:
            i -= 1
            left_open = False
        j = peers.index(self)
        right_open = True
        while j < len(peers) - 1 and abs(peers[j].x + peers[j].width - peers[j + 1].x) <= 1.0:
            j += 1
            right_open = False

        standing = self._has_bottom_contact()
        corners = (left_open, right_open,
                   left_open and not standing, right_open and not standing)
        info = (peers[i].x, corners)
        self._tex_info = info
        return info

    def _has_bottom_contact(self):
        """True when this platform sits exactly on another one (ground blocks stay square)."""
        for obj in game:
            if obj is self or getattr(obj, 'obj_type', '') != 'platform':
                continue
            if getattr(obj, 'texture_type', None) is None:
                continue
            if abs((obj.y - obj.height) - self.y) <= 1.0:
                overlap = min(self.x + self.width, obj.x + obj.width) - max(self.x, obj.x)
                if overlap > self.width * 0.5:
                    return True
        return False
    
    def draw(self, screen):
        draw_x, draw_y = apply_camera_offset(self.x, self.y)
        
        if self.obj_type == 'platform' or self.obj_type == 'none':
            self._draw_platform(screen, draw_x, draw_y)
        elif self.obj_type == 'text':
            self._draw_text(screen, draw_x, draw_y)
    
    def _draw_platform(self, screen, draw_x, draw_y):
        pygame.draw.rect(screen, self.color, (draw_x, draw_y - self.height, self.width, self.height))
        if self.border_color:
            pygame.draw.rect(screen, self.border_color, (draw_x, draw_y - self.height, self.width, self.height), 2)
    
    def _draw_text(self, screen, draw_x, draw_y):
        if not self.text_visible:
            return
        temp_rect = self.text_rect.copy()
        temp_rect.x = draw_x
        temp_rect.y = draw_y
        screen.blit(self.text_surface, temp_rect)

# ========== Explosion class ==========
class Explosion:
    def __init__(self, x, y, radius=explosion_max_radius, color_type='red'):
        self.x = x
        self.y = y
        self.radius = 5
        self.max_radius = radius
        self.duration = explosion_duration
        self.time = 0.0
        self.active = True
        self.color_type = color_type
        
        # Play explosion sound
        sound_manager.play_explosion()
    
    def update(self, dt):
        self.time += dt
        progress = self.time / self.duration
        self.radius = int(self.max_radius * progress)
        
        if progress >= 1.0:
            self.active = False
            
        return self.active
    
    def get_colors(self):
        if self.color_type == 'green':
            return EXPLOSION_GREEN_INNER, EXPLOSION_GREEN_MIDDLE, EXPLOSION_GREEN_OUTER
        else:
            return EXPLOSION_RED_INNER, EXPLOSION_RED_MIDDLE, EXPLOSION_RED_OUTER
    
    def draw(self, screen):
        if not self.active:
            return
            
        draw_x, draw_y = apply_camera_offset(self.x, self.y)
        progress = self.time / self.duration
        inner_color, middle_color, outer_color = self.get_colors()
        
        for i in range(3):
            ring_radius = int(self.radius * (1 - i * 0.2))
            alpha = int(200 * (1 - progress) * (1 - i * 0.3))
            
            if ring_radius > 0:
                ring_surface = pygame.Surface((ring_radius*2, ring_radius*2), pygame.SRCALPHA)
                
                if i == 0:
                    color = (*inner_color[:3], alpha)
                elif i == 1:
                    color = (*middle_color[:3], alpha)
                else:
                    color = (*outer_color[:3], alpha)
                
                pygame.draw.circle(ring_surface, color, (ring_radius, ring_radius), ring_radius)
                screen.blit(ring_surface, (draw_x - ring_radius, draw_y - ring_radius))
        
        if progress < 0.5:
            highlight_radius = int(5 * (1 - progress * 2))
            if highlight_radius > 0:
                pygame.draw.circle(screen, NIGHT_WHITE, (int(draw_x), int(draw_y)), highlight_radius)
    
    def check_player_collision(self, player_x, player_y, player_width, player_height):
        if not self.active:
            return False
        player_center_x = player_x + player_width // 2
        player_center_y = player_y + player_height // 2
        dx = player_center_x - self.x
        dy = player_center_y - self.y
        distance = math.sqrt(dx*dx + dy*dy)
        return distance < self.radius

# ========== Candy class ==========
class Candy:
    def __init__(self, x, y, velocity_x, velocity_y, trail_color=None):
        self.x = x
        self.y = y
        self.velocity_x = velocity_x
        self.velocity_y = velocity_y
        self.radius = candy_radius
        self.color = EXPLOSION_RED_INNER
        self.trail_color = trail_color if trail_color else EXPLOSION_RED_INNER
        self.lifetime = candy_lifetime
        self.trail = []
        self.trail_max_length = candy_trail_length
        self.exploded = False
        self.rotation = 0
        self.rotation_speed = random.uniform(2, 5) * (1 if random.random() > 0.5 else -1)
        
        self.candy_type = random.choice(['red', 'green'])
        self.texture = candy_textures.get(self.candy_type) if CANDY_TEXTURES_LOADED else None
        
        # Sound-related attributes
        self.throw_sound_played = False
        self.creation_time = pygame.time.get_ticks() / 1000.0

    def check_collision(self):
        if self.y + self.radius > WORLD_BOTTOM_BORDER:
            adjusted_x = self.x
            adjusted_y = WORLD_BOTTOM_BORDER - self.radius
            return True, "world_bottom", adjusted_x, adjusted_y
            
        for obj in game:
            if obj.obj_type != 'platform':
                continue
                
            platform_top = obj.y - obj.height
            
            if (self.x > obj.x - self.radius and 
                self.x < obj.x + obj.width + self.radius and
                self.y > platform_top - self.radius and 
                self.y < obj.y + self.radius):
                
                left_dist = abs(self.x - obj.x)
                right_dist = abs(self.x - (obj.x + obj.width))
                top_dist = abs(self.y - platform_top)
                bottom_dist = abs(self.y - obj.y)
                
                min_dist = min(left_dist, right_dist, top_dist, bottom_dist)
                adjusted_x, adjusted_y = self.x, self.y
                collision_type = None
                
                if min_dist == left_dist:
                    adjusted_x = obj.x - self.radius
                    collision_type = "left"
                elif min_dist == right_dist:
                    adjusted_x = obj.x + obj.width + self.radius
                    collision_type = "right"
                elif min_dist == top_dist:
                    adjusted_y = platform_top - self.radius
                    collision_type = "top"
                else:
                    adjusted_y = obj.y + self.radius
                    collision_type = "bottom"
                    
                return True, f"platform_{collision_type}", adjusted_x, adjusted_y
                
        summit = summit_solid_rect()
        if summit is not None and summit.collidepoint(self.x, self.y):
            return True, "summit", self.x, self.y

        return False, None, self.x, self.y
    
    def update(self, dt):
        if self.exploded:
            return False
            
        self.rotation += self.rotation_speed * dt * 60
        self.trail.append((self.x, self.y, self.rotation))
        if len(self.trail) > self.trail_max_length:
            self.trail.pop(0)
        
        self.velocity_y += candy_gravity * dt * 60
        prev_x, prev_y = self.x, self.y
        self.x += self.velocity_x * dt * 60
        self.y += self.velocity_y * dt * 60
        
        collision, collision_type, adjusted_x, adjusted_y = self.check_collision()
        
        if collision:
            if abs(self.velocity_x) > 5 or abs(self.velocity_y) > 5:
                move_dx = self.x - prev_x
                move_dy = self.y - prev_y
                move_distance = math.sqrt(move_dx * move_dx + move_dy * move_dy)
                
                if move_distance > 0:
                    steps = int(move_distance / 2) + 1
                    for i in range(1, steps + 1):
                        t = i / steps
                        test_x = prev_x + move_dx * t
                        test_y = prev_y + move_dy * t
                        
                        temp_x, temp_y = self.x, self.y
                        self.x, self.y = test_x, test_y
                        
                        test_collision, test_type, test_adj_x, test_adj_y = self.check_collision()
                        
                        if test_collision:
                            self.x, self.y = test_adj_x, test_adj_y
                            self.explode()
                            return False
                        
                        self.x, self.y = temp_x, temp_y
            else:
                self.x, self.y = adjusted_x, adjusted_y
            
            self.explode()
            return False
        
        # Play throw sound if not exploded after 0.1 s
        current_time = pygame.time.get_ticks() / 1000.0
        if not self.throw_sound_played and not self.exploded:
            if current_time - self.creation_time >= 0.1:
                sound_manager.play_throw()
                self.throw_sound_played = True
        
        if (abs(self.x - camera_x) > WIDTH * 2 or abs(self.y - camera_y) > HEIGHT * 2):
            return False
            
        self.lifetime -= dt
        return self.lifetime > 0
    
    def explode(self):
        self.exploded = True
        
        collision, collision_type, adjusted_x, adjusted_y = self.check_collision()
        if collision:
            self.x, self.y = adjusted_x, adjusted_y
        
        if self.y + self.radius >= WORLD_BOTTOM_BORDER:
            self.y = WORLD_BOTTOM_BORDER - self.radius - 1
        
        explosions.append(Explosion(self.x, self.y, color_type=self.candy_type))
        
        global screen_shake
        screen_shake = 10.0
        
        apply_explosion_force(self.x, self.y)
    
    def draw(self, screen):
        if self.exploded:
            return
        
        draw_x, draw_y = apply_camera_offset(self.x, self.y)
        
        if self.texture and CANDY_TEXTURES_LOADED:
            for i, (trail_x, trail_y, trail_rotation) in enumerate(self.trail):
                alpha = int(255 * (i / len(self.trail)))
                trail_draw_x, trail_draw_y = apply_camera_offset(trail_x, trail_y)
                trail_size = int(self.radius * 2 * (i / len(self.trail)))
                
                if trail_size > 0:
                    trail_surface = pygame.Surface((trail_size, trail_size), pygame.SRCALPHA)
                    if self.candy_type == 'red':
                        trail_color = (*EXPLOSION_RED_INNER[:3], alpha)
                    else:
                        trail_color = (0, 200, 0, alpha)
                    pygame.draw.circle(trail_surface, trail_color, (trail_size//2, trail_size//2), trail_size//2)
                    screen.blit(trail_surface, (trail_draw_x - trail_size//2, trail_draw_y - trail_size//2))
            
            self.texture.draw(screen, draw_x, draw_y, self.rotation)
        else:
            if self.candy_type == 'red':
                candy_color = EXPLOSION_RED_INNER
                inner_color = (255, 150, 150)
            else:
                candy_color = (0, 200, 0)
                inner_color = (150, 255, 150)
            
            for i, (trail_x, trail_y, trail_rotation) in enumerate(self.trail):
                alpha = int(255 * (i / len(self.trail)))
                trail_draw_x, trail_draw_y = apply_camera_offset(trail_x, trail_y)
                radius = int(self.radius * (i / len(self.trail)))
                
                trail_surface = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
                trail_color = (*candy_color[:3], alpha)
                pygame.draw.circle(trail_surface, trail_color, (radius, radius), radius)
                screen.blit(trail_surface, (trail_draw_x - radius, trail_draw_y - radius))
            
            candy_surface = pygame.Surface((self.radius*2, self.radius*2), pygame.SRCALPHA)
            pygame.draw.circle(candy_surface, candy_color, (self.radius, self.radius), self.radius)
            pygame.draw.circle(candy_surface, inner_color, (self.radius, self.radius), self.radius - 2)
            
            stripe_width = 2
            pygame.draw.line(candy_surface, NIGHT_WHITE, (self.radius, 0), (self.radius, self.radius*2), stripe_width)
            pygame.draw.line(candy_surface, NIGHT_WHITE, (0, self.radius), (self.radius*2, self.radius), stripe_width)
            
            rotated_candy = pygame.transform.rotate(candy_surface, self.rotation)
            rotated_rect = rotated_candy.get_rect(center=(draw_x, draw_y))
            screen.blit(rotated_candy, rotated_rect)
        
        if not self.texture or not CANDY_TEXTURES_LOADED:
            flame_length = 10
            flame_width = 6
            speed = math.sqrt(self.velocity_x*self.velocity_x + self.velocity_y*self.velocity_y)
            
            if speed > 0:
                flame_dir_x = -self.velocity_x / speed
                flame_dir_y = -self.velocity_y / speed
                
                flame_end_x = draw_x + flame_dir_x * flame_length
                flame_end_y = draw_y + flame_dir_y * flame_length
                
                flame_points = [
                    (flame_end_x, flame_end_y),
                    (draw_x - flame_width//2, draw_y),
                    (draw_x + flame_width//2, draw_y)
                ]
                
                pygame.draw.polygon(screen, (255, 200, 0), flame_points)

# ========== Player sprite system ==========
class PlayerTextureSystem:
    def __init__(self):
        self.texture_loaded = False
        self.idle_textures = []
        self.air_texture = None
        self.hat_texture = None
        self.current_texture = None
        self.current_frame = 0
        self.animation_timer = 0.0
        self.animation_speed = 0.2
        self.flipped = False
        
        self.hat_offset_x = 0
        self.hat_offset_y = -player_height * 0.5
        self.hat_width_ratio = 1
        self.hat_height_ratio = 0.7
        
        self.load_textures()
    
    def load_textures(self):
        try:
            idle1 = pygame.image.load(paths.asset("textures", "Idle-1.png")).convert_alpha()
            idle2 = pygame.image.load(paths.asset("textures", "Idle-2.png")).convert_alpha()
            
            target_width = player_width
            target_height = player_height
            
            self.idle_textures = [
                pygame.transform.scale(idle1, (target_width, target_height)),
                pygame.transform.scale(idle2, (target_width, target_height))
            ]
            
            air_texture = pygame.image.load(paths.asset("textures", "InAir.png")).convert_alpha()
            self.air_texture = pygame.transform.scale(air_texture, (target_width, target_height))
            
            self.load_hat_texture()
            
            self.current_texture = self.idle_textures[0]
            self.texture_loaded = True
        except pygame.error:
            self.texture_loaded = False
    
    def load_hat_texture(self):
        try:
            hat_original = pygame.image.load(paths.asset("textures", "Hat.png")).convert_alpha()
            hat_width = int(player_width * self.hat_width_ratio)
            hat_height = int(player_height * self.hat_height_ratio)
            self.hat_texture = pygame.transform.scale(hat_original, (hat_width, hat_height))
        except pygame.error:
            self.hat_texture = None
    
    def update(self, dt, is_on_ground, facing_right):
        self.flipped = not facing_right
        
        if self.texture_loaded:
            if is_on_ground:
                self.animation_timer += dt
                if self.animation_timer >= self.animation_speed:
                    self.animation_timer = 0.0
                    self.current_frame = (self.current_frame + 1) % len(self.idle_textures)
                    self.current_texture = self.idle_textures[self.current_frame]
            else:
                self.current_texture = self.air_texture
                self.animation_timer = 0.0
                self.current_frame = 0
    
    def draw(self, screen, x, y, width, height):
        if not self.texture_loaded or self.current_texture is None:
            pygame.draw.rect(screen, BLUE, (x, y, width, height))
            pygame.draw.rect(screen, NIGHT_WHITE, (x, y, width, height), 2)
            self.draw_default_hat(screen, x, y, width, height)
            return
        
        texture_to_draw = self.current_texture
        if self.flipped:
            texture_to_draw = pygame.transform.flip(texture_to_draw, True, False)
        
        screen.blit(texture_to_draw, (x, y))
        self.draw_hat(screen, x, y, width, height)
    
    def draw_hat(self, screen, player_x, player_y, player_width, player_height):
        hat_width = int(player_width * self.hat_width_ratio)
        hat_height = int(player_height * self.hat_height_ratio)
        
        if self.flipped:
            hat_center_x = player_x + player_width // 2 - self.hat_offset_x
        else:
            hat_center_x = player_x + player_width // 2 + self.hat_offset_x
        
        hat_y = player_y + self.hat_offset_y
        hat_x = hat_center_x - hat_width // 2
        
        if self.hat_texture is not None:
            hat_to_draw = self.hat_texture
            if self.flipped:
                hat_to_draw = pygame.transform.flip(hat_to_draw, True, False)
            screen.blit(hat_to_draw, (hat_x, hat_y))
        else:
            self.draw_default_hat(screen, player_x, player_y, player_width, player_height, hat_x, hat_y, hat_width, hat_height)
    
    def draw_default_hat(self, screen, player_x, player_y, player_width, player_height, hat_x=None, hat_y=None, hat_width=None, hat_height=None):
        if hat_x is None:
            hat_width = int(player_width * self.hat_width_ratio)
            hat_height = int(player_height * self.hat_height_ratio)
            
            if self.flipped:
                hat_center_x = player_x + player_width // 2 - self.hat_offset_x
            else:
                hat_center_x = player_x + player_width // 2 + self.hat_offset_x
            
            hat_y = player_y + self.hat_offset_y
            hat_x = hat_center_x - hat_width // 2
        
        hat_color = (101, 67, 33)
        pygame.draw.rect(screen, hat_color, (hat_x, hat_y, hat_width, hat_height))
        
        brim_color = (139, 69, 19)
        brim_height = max(2, hat_height // 5)
        pygame.draw.rect(screen, brim_color, (hat_x, hat_y, hat_width, brim_height))
        
        if hat_width > 10:
            ball_x = hat_x + hat_width // 2
            ball_y = hat_y - 3
            ball_radius = max(2, hat_width // 8)
            pygame.draw.circle(screen, (200, 0, 0), (ball_x, ball_y), ball_radius)
            
            band_y = hat_y + brim_height
            band_height = max(1, hat_height // 10)
            pygame.draw.rect(screen, (255, 215, 0), (hat_x, band_y, hat_width, band_height))

player_textures = PlayerTextureSystem()

# ========== Explosion force ==========
def apply_explosion_force(explosion_x, explosion_y):
    global player_velocity_x, player_velocity_y
    
    player_center_x = player_x + player_width // 2
    player_center_y = player_y + player_height // 2
    
    dx = player_center_x - explosion_x
    dy = player_center_y - explosion_y
    distance = math.sqrt(dx*dx + dy*dy)
    
    if distance == 0:
        distance = 0.1
        dir_x = 0
        dir_y = -1
    else:
        dir_x = dx / distance
        dir_y = dy / distance
    
    explosion_radius = explosion_max_radius
    if distance < explosion_radius:
        force_factor = (1.0 - (distance / explosion_radius)) ** 0.5
        force = explosion_force * force_factor * 2.5
        
        vel_x_add = dir_x * force
        vel_y_add = dir_y * force
        
        current_speed = math.sqrt(player_velocity_x**2 + player_velocity_y**2)
        
        new_vel_x = player_velocity_x + vel_x_add
        new_vel_y = player_velocity_y + vel_y_add
        new_speed = math.sqrt(new_vel_x**2 + new_vel_y**2)
        
        max_single_bomb_speed = 25.0
        
        if new_speed > max_single_bomb_speed:
            scale_factor = max_single_bomb_speed / new_speed
            new_vel_x *= scale_factor
            new_vel_y *= scale_factor
            
            limited_vel_x_add = new_vel_x - player_velocity_x
            limited_vel_y_add = new_vel_y - player_velocity_y
            
            player_velocity_x += limited_vel_x_add
            player_velocity_y += limited_vel_y_add
        else:
            player_velocity_x += vel_x_add
            player_velocity_y += vel_y_add

def check_world_border_collision():
    global player_x, player_y, player_velocity_x, player_velocity_y, player_is_on_ground
    
    collision_occurred = False
    new_x, new_y = player_x, player_y
    new_vel_x, new_vel_y = player_velocity_x, player_velocity_y
    collision_type = None
    
    if player_y + player_height > WORLD_BOTTOM_BORDER:
        new_y = WORLD_BOTTOM_BORDER - player_height
        new_vel_y = -abs(player_velocity_y) * 0.3
        collision_occurred = True
        collision_type = "world_bottom"
        player_is_on_ground = True
    
    if collision_occurred:
        return collision_type, new_x, new_y, new_vel_x, new_vel_y
    
    return None

# ========== Game object list ==========
# ========== Fixed level data: all platforms + all hints (hand-made map) ==========
game = [
    # Two big side walls (height 20000)
    GameObject(x=-1000, y=-1200, width=1000, height=20000, texture_type='center'),
    GameObject(x=12000, y=-1200, width=1000, height=20000, texture_type='center'),
    GameObject(x=-1000, y=-1200, width=20000, height=1200, texture_type='center', color=(144, 238, 144)),
    GameObject(x=4000, y=0, width=200, height=100, texture_type='top', color=(144, 238, 144)),
    GameObject(x=9000, y=0, width=200, height=100, texture_type='top', color=(144, 238, 144)),
    GameObject(x=9400, y=0, width=200, height=100, texture_type='top', color=(144, 238, 144)),
    GameObject(x=9800, y=0, width=200, height=100, texture_type='top', color=(144, 238, 144)),
    GameObject(x=9600, y=175, width=200, height=50, texture_type='top', color=(144, 238, 144)),
    GameObject(x=9900, y=250, width=150, height=50, texture_type='top', color=(144, 238, 144)),
    GameObject(x=10200, y=250, width=150, height=50, texture_type='top', color=(144, 238, 144)),
    GameObject(x=10450, y=350, width=400, height=50, texture_type='top', color=(144, 238, 144)),
    GameObject(x=10900, y=450, width=250, height=50, texture_type='top', color=(144, 238, 144)),
    GameObject(x=11200, y=550, width=200, height=50, texture_type='top', color=(144, 238, 144)),
    GameObject(x=11500, y=650, width=250, height=50, texture_type='top', color=(144, 238, 144)),
    GameObject(x=11200, y=750, width=200, height=50, texture_type='top', color=(144, 238, 144)),
    GameObject(x=10750, y=870, width=300, height=50, texture_type='top', color=(144, 238, 144)),
    GameObject(x=10050, y=990, width=500, height=50, texture_type='top', color=(144, 238, 144)),
    GameObject(x=9350, y=990, width=500, height=50, texture_type='top', color=(144, 238, 144)),
    GameObject(x=9000, y=990, width=300, height=50, texture_type='top', color=(255, 165, 0), end_x=8300, move_speed=4),
    GameObject(x=7950, y=990, width=300, height=50, texture_type='top', color=(144, 238, 144)),
    GameObject(x=7550, y=1110, width=300, height=50, texture_type='top', color=(255, 165, 0), end_y=1470, move_speed=2.5),
    GameObject(x=7150, y=1590, width=250, height=50, texture_type='top', color=(144, 238, 144)),
    GameObject(x=6800, y=1710, width=250, height=50, texture_type='top', color=(144, 238, 144)),
    GameObject(x=7200, y=1770, width=300, height=50, texture_type='top', color=(144, 238, 144)),
    GameObject(x=7600, y=1870, width=200, height=50, texture_type='top', color=(144, 238, 144)),
    GameObject(x=7900, y=1970, width=200, height=50, texture_type='top', color=(144, 238, 144)),
    GameObject(x=8200, y=2045, width=200, height=50, texture_type='top', color=(144, 238, 144)),
    GameObject(x=8300, y=2050, width=100, height=150, texture_type='top', color=(144, 238, 144)),
    GameObject(x=7950, y=2265, width=150, height=50, texture_type='top', color=(144, 238, 144)),
    GameObject(x=7750, y=2365, width=150, height=50, texture_type='top', color=(144, 238, 144)),
    GameObject(x=7450, y=2485, width=200, height=50, texture_type='top', color=(144, 238, 144)),
    GameObject(x=6850, y=2585, width=400, height=50, texture_type='top', color=(144, 238, 144)),
    GameObject(x=6500, y=2705, width=200, height=50, texture_type='top', color=(144, 238, 144)),
    GameObject(x=6150, y=2745, width=250, height=50, texture_type='top', color=(255, 165, 0), end_y=3165, move_speed=2.6),
    GameObject(x=6500, y=3265, width=300, height=50, texture_type='top', color=(144, 238, 144)),
    GameObject(x=7000, y=3385, width=200, height=50, texture_type='top', color=(144, 238, 144)),
    GameObject(x=7300, y=3485, width=200, height=50, texture_type='top', color=(144, 238, 144)),
    GameObject(x=7600, y=3560, width=150, height=50, texture_type='top', color=(144, 238, 144)),
    GameObject(x=7850, y=3660, width=400, height=50, texture_type='top', color=(144, 238, 144)),
    GameObject(x=8450, y=3780, width=400, height=50, texture_type='top', color=(144, 238, 144)),
    GameObject(x=8900, y=3800, width=300, height=50, texture_type='top', color=(255, 165, 0), end_x=9500, move_speed=4, curve='arc', curve_amp=80),
    GameObject(x=9150, y=3900, width=250, height=50, texture_type='top', color=(144, 238, 144)),
    GameObject(x=8900, y=4000, width=150, height=50, texture_type='top', color=(144, 238, 144)),
    GameObject(x=8400, y=4075, width=400, height=50, texture_type='top', color=(144, 238, 144)),
    GameObject(x=8050, y=4195, width=150, height=50, texture_type='top', color=(144, 238, 144)),
    GameObject(x=7700, y=4195, width=150, height=50, texture_type='top', color=(144, 238, 144)),
    GameObject(x=7350, y=4295, width=300, height=50, texture_type='top', color=(144, 238, 144)),
    GameObject(x=7750, y=4435, width=200, height=50, texture_type='top', color=(144, 238, 144)),
    GameObject(x=8050, y=4535, width=400, height=50, texture_type='top', color=(144, 238, 144)),
    GameObject(x=8650, y=4655, width=300, height=50, texture_type='top', color=(144, 238, 144)),
    GameObject(x=8250, y=4775, width=250, height=50, texture_type='top', color=(144, 238, 144)),
    GameObject(x=7950, y=4900, width=300, height=50, texture_type='top', color=(144, 238, 144)),
    GameObject(x=7700, y=5025, width=250, height=50, texture_type='top', color=(144, 238, 144)),
    GameObject(x=7400, y=5145, width=150, height=50, texture_type='top', color=(144, 238, 144)),
    GameObject(x=7050, y=5185, width=250, height=50, texture_type='top', color=(255, 165, 0), end_y=5705, move_speed=2.6),
    GameObject(x=7450, y=5825, width=250, height=50, texture_type='top', color=(144, 238, 144)),
    GameObject(x=7900, y=5945, width=150, height=50, texture_type='top', color=(144, 238, 144)),
    GameObject(x=8200, y=5945, width=250, height=50, texture_type='top', color=(144, 238, 144)),
    GameObject(x=8650, y=5945, width=150, height=50, texture_type='top', color=(144, 238, 144)),
    GameObject(x=8800, y=6070, width=300, height=50, texture_type='top', color=(144, 238, 144)),
    GameObject(x=9200, y=6170, width=300, height=50, texture_type='top', color=(144, 238, 144)),
    GameObject(x=9550, y=6190, width=300, height=50, texture_type='top', color=(255, 165, 0), end_x=10150, move_speed=4, curve='arc', curve_amp=80),
    GameObject(x=9750, y=6310, width=250, height=50, texture_type='top', color=(144, 238, 144)),
    GameObject(x=9550, y=6435, width=200, height=50, texture_type='top', color=(144, 238, 144)),
    GameObject(x=9150, y=6510, width=300, height=50, texture_type='top', color=(144, 238, 144)),
    GameObject(x=8750, y=6585, width=300, height=50, texture_type='top', color=(144, 238, 144)),
    GameObject(x=9150, y=6685, width=250, height=50, texture_type='top', color=(144, 238, 144)),
    GameObject(x=9450, y=6785, width=200, height=50, texture_type='top', color=(144, 238, 144)),
    GameObject(x=9750, y=6860, width=200, height=50, texture_type='top', color=(144, 238, 144)),
    GameObject(x=9600, y=6860, width=400, height=50, texture_type='top', color=(144, 238, 144)),
    GameObject(x=9200, y=6935, width=300, height=50, texture_type='top', color=(144, 238, 144)),
    GameObject(x=8850, y=6935, width=300, height=50, texture_type='top', color=(144, 238, 144)),
    GameObject(x=8400, y=7035, width=400, height=50, texture_type='top', color=(144, 238, 144)),
    GameObject(x=8100, y=7135, width=250, height=50, texture_type='top', color=(144, 238, 144)),
    GameObject(x=7750, y=7175, width=250, height=50, texture_type='top', color=(255, 165, 0), end_y=7595, move_speed=2.6),
    GameObject(x=8100, y=7695, width=300, height=50, texture_type='top', color=(144, 238, 144)),
    GameObject(x=8400, y=7820, width=150, height=50, texture_type='top', color=(144, 238, 144)),
    GameObject(x=8700, y=7820, width=150, height=50, texture_type='top', color=(144, 238, 144)),
    GameObject(x=8950, y=7895, width=150, height=50, texture_type='top', color=(144, 238, 144)),
    GameObject(x=9150, y=7915, width=300, height=50, texture_type='top', color=(255, 165, 0), end_x=9750, move_speed=4),
    GameObject(x=9350, y=8035, width=250, height=50, texture_type='top', color=(144, 238, 144)),
    GameObject(x=8800, y=8145, width=400, height=50, texture_type='top', color=(144, 238, 144)),
    GameObject(x=9350, y=8265, width=250, height=50, texture_type='top', color=(144, 238, 144)),
    GameObject(x=9700, y=8305, width=250, height=50, texture_type='top', color=(255, 165, 0), end_y=8825, move_speed=2.6),
    GameObject(x=9300, y=8945, width=250, height=50, texture_type='top', color=(144, 238, 144)),
    GameObject(x=9000, y=9020, width=200, height=50, texture_type='top', color=(144, 238, 144)),
    GameObject(x=8600, y=9020, width=250, height=50, texture_type='top', color=(144, 238, 144)),
    GameObject(x=8400, y=9145, width=200, height=50, texture_type='top', color=(144, 238, 144)),
    GameObject(x=8200, y=9265, width=250, height=50, texture_type='top', color=(144, 238, 144)),
    GameObject(x=8450, y=9390, width=400, height=50, texture_type='top', color=(144, 238, 144)),
    GameObject(x=8900, y=9390, width=400, height=50, texture_type='top', color=(144, 238, 144)),
    GameObject(x=9450, y=9510, width=150, height=50, texture_type='top', color=(144, 238, 144)),
    GameObject(x=9050, y=9630, width=250, height=50, texture_type='top', color=(144, 238, 144)),
    GameObject(x=8450, y=9750, width=400, height=50, texture_type='top', color=(144, 238, 144)),
    GameObject(x=8300, y=9875, width=150, height=50, texture_type='top', color=(144, 238, 144)),
    GameObject(x=7900, y=9995, width=200, height=50, texture_type='top', color=(144, 238, 144)),
    GameObject(x=7500, y=10115, width=300, height=50, texture_type='top', color=(144, 238, 144)),
    GameObject(x=7900, y=10215, width=200, height=50, texture_type='top', color=(144, 238, 144)),
    GameObject(x=8200, y=10290, width=150, height=50, texture_type='top', color=(144, 238, 144)),
    GameObject(x=8500, y=10410, width=200, height=50, texture_type='top', color=(144, 238, 144)),
    GameObject(x=8700, y=10535, width=250, height=50, texture_type='top', color=(144, 238, 144)),
    GameObject(x=8300, y=10655, width=250, height=50, texture_type='top', color=(144, 238, 144)),
    GameObject(x=8050, y=10730, width=150, height=50, texture_type='top', color=(144, 238, 144)),
    GameObject(x=7650, y=10855, width=400, height=50, texture_type='top', color=(144, 238, 144)),
    GameObject(x=7100, y=10975, width=400, height=50, texture_type='top', color=(144, 238, 144)),
    GameObject(x=6800, y=11050, width=200, height=50, texture_type='top', color=(144, 238, 144)),
    GameObject(x=6400, y=11170, width=200, height=50, texture_type='top', color=(144, 238, 144)),
    GameObject(x=6050, y=11190, width=300, height=50, texture_type='top', color=(255, 165, 0), end_x=5300, move_speed=4),
    GameObject(x=5750, y=11310, width=300, height=50, texture_type='top', color=(144, 238, 144)),
    GameObject(x=6150, y=11410, width=300, height=50, texture_type='top', color=(144, 238, 144)),
    GameObject(x=6500, y=11410, width=300, height=50, texture_type='top', color=(144, 238, 144)),
    GameObject(x=6150, y=11585, width=200, height=50, texture_type='top', color=(144, 238, 144)),
    GameObject(x=5850, y=11585, width=250, height=50, texture_type='top', color=(144, 238, 144)),
    GameObject(x=5500, y=11685, width=250, height=50, texture_type='top', color=(144, 238, 144)),
    GameObject(x=5150, y=11805, width=200, height=50, texture_type='top', color=(144, 238, 144)),
    GameObject(x=4550, y=11805, width=400, height=50, texture_type='top', color=(144, 238, 144)),
    GameObject(x=4200, y=11845, width=250, height=50, texture_type='top', color=(255, 165, 0), end_y=12365, move_speed=2.6),
    GameObject(x=4550, y=12465, width=300, height=50, texture_type='top', color=(144, 238, 144)),
    GameObject(x=4950, y=12565, width=200, height=50, texture_type='top', color=(144, 238, 144)),
    GameObject(x=5250, y=12665, width=200, height=50, texture_type='top', color=(144, 238, 144)),
    GameObject(x=5500, y=12765, width=400, height=50, texture_type='top', color=(144, 238, 144)),
    GameObject(x=6100, y=12885, width=250, height=50, texture_type='top', color=(144, 238, 144)),
    GameObject(x=6450, y=12925, width=250, height=50, texture_type='top', color=(255, 165, 0), end_y=13345, move_speed=2.6),
    GameObject(x=6050, y=13445, width=300, height=50, texture_type='top', color=(144, 238, 144)),
    GameObject(x=5700, y=13520, width=250, height=50, texture_type='top', color=(144, 238, 144)),
    GameObject(x=5450, y=13620, width=200, height=50, texture_type='top', color=(144, 238, 144)),
    GameObject(x=5200, y=13745, width=250, height=50, texture_type='top', color=(144, 238, 144)),
    GameObject(x=4850, y=13745, width=300, height=50, texture_type='top', color=(144, 238, 144)),
    GameObject(x=4300, y=13865, width=400, height=50, texture_type='top', color=(144, 238, 144)),
    GameObject(x=3950, y=13885, width=300, height=50, texture_type='top', color=(255, 165, 0), end_x=3200, move_speed=4),
    GameObject(x=3650, y=14005, width=250, height=50, texture_type='top', color=(144, 238, 144)),
    GameObject(x=4100, y=14125, width=400, height=50, texture_type='top', color=(144, 238, 144)),
    GameObject(x=4600, y=14225, width=300, height=50, texture_type='top', color=(144, 238, 144)),
    GameObject(x=5100, y=14345, width=300, height=50, texture_type='top', color=(144, 238, 144)),
    GameObject(x=5550, y=14345, width=300, height=50, texture_type='top', color=(144, 238, 144)),
    GameObject(x=6000, y=14465, width=400, height=50, texture_type='top', color=(144, 238, 144)),
    GameObject(x=6500, y=14505, width=250, height=50, texture_type='top', color=(255, 165, 0), end_y=14985, move_speed=2.6),
    GameObject(x=6100, y=15085, width=300, height=50, texture_type='top', color=(144, 238, 144)),
    GameObject(x=5500, y=15205, width=400, height=50, texture_type='top', color=(144, 238, 144)),
    GameObject(x=4900, y=15325, width=400, height=50, texture_type='top', color=(144, 238, 144)),
    GameObject(x=4500, y=15450, width=400, height=50, texture_type='top', color=(144, 238, 144)),
    GameObject(x=4100, y=15525, width=300, height=50, texture_type='top', color=(144, 238, 144)),
    GameObject(x=3750, y=15565, width=250, height=50, texture_type='top', color=(255, 165, 0), end_y=16045, move_speed=2.6),
    GameObject(x=4150, y=16165, width=250, height=50, texture_type='top', color=(144, 238, 144)),
    GameObject(x=4550, y=16225, width=250, height=50, texture_type='top', color=(144, 238, 144)),
    GameObject(x=4950, y=16285, width=250, height=50, texture_type='top', color=(144, 238, 144)),
    GameObject(x=5350, y=16345, width=250, height=50, texture_type='top', color=(144, 238, 144)),
    GameObject(x=5750, y=16405, width=250, height=50, texture_type='top', color=(144, 238, 144)),
    GameObject(x=6150, y=16465, width=250, height=50, texture_type='top', color=(144, 238, 144)),
    GameObject(x=6550, y=16525, width=250, height=50, texture_type='top', color=(144, 238, 144)),
    GameObject(x=6950, y=16585, width=250, height=50, texture_type='top', color=(144, 238, 144)),
    GameObject(x=7350, y=16645, width=250, height=50, texture_type='top', color=(144, 238, 144)),
    GameObject(x=7750, y=16705, width=250, height=50, texture_type='top', color=(144, 238, 144)),
    GameObject(x=8150, y=16765, width=250, height=50, texture_type='top', color=(144, 238, 144)),
    GameObject(x=8550, y=16825, width=250, height=50, texture_type='top', color=(144, 238, 144)),
    GameObject(x=8950, y=16885, width=250, height=50, texture_type='top', color=(144, 238, 144)),
    GameObject(x=9350, y=16945, width=250, height=50, texture_type='top', color=(144, 238, 144)),
    GameObject(x=9750, y=17005, width=250, height=50, texture_type='top', color=(144, 238, 144)),
    GameObject(x=10150, y=17065, width=250, height=50, texture_type='top', color=(144, 238, 144)),
    GameObject(x=10550, y=17185, width=250, height=50, texture_type='top', color=(144, 238, 144)),
    GameObject(x=10150, y=17305, width=250, height=50, texture_type='top', color=(144, 238, 144)),
    GameObject(x=9750, y=17365, width=250, height=50, texture_type='top', color=(144, 238, 144)),
    GameObject(x=9350, y=17425, width=250, height=50, texture_type='top', color=(144, 238, 144)),
    GameObject(x=8950, y=17485, width=250, height=50, texture_type='top', color=(144, 238, 144), end_y=18450, move_speed=2.6),
    GameObject(x=8150, y=18430, width=750, height=50, texture_type='top', color=(144, 238, 144)),
    GameObject(obj_type='text', x=100, y=300, text='Welcome to the game!', text_color=(255, 255, 0), text_size=60, text_align='center'),
    GameObject(obj_type='text', x=100, y=200, text='Try clicking your left button of your mouse :)', text_color=(255, 255, 0), text_size=60, text_align='center'),
    GameObject(obj_type='text', x=1500, y=300, text='If you see this', text_color=(255, 255, 0), text_size=60, text_align='center'),
    GameObject(obj_type='text', x=1500, y=200, text='Good job! You learned how to move horizontally', text_color=(255, 255, 0), text_size=60, text_align='center'),
    GameObject(obj_type='text', x=3500, y=300, text='Hmm...how can we get over this?', text_color=(255, 255, 0), text_size=60, text_align='center'),
    GameObject(obj_type='text', x=3500, y=200, text='Maybe try throwing candy so it hits yourself?', text_color=(255, 255, 0), text_size=60, text_align='center'),
    GameObject(obj_type='text', x=5000, y=300, text='Wow! you learned how to jump!', text_color=(255, 255, 0), text_size=60, text_align='center'),
    GameObject(obj_type='text', x=5000, y=200, text='You were smarter that I thought!', text_color=(255, 255, 0), text_size=60, text_align='center'),
    GameObject(obj_type='text', x=6000, y=300, text='You learned everything you can!', text_color=(255, 255, 0), text_size=60, text_align='center'),
    GameObject(obj_type='text', x=6000, y=200, text='Good luck :)', text_color=(255, 255, 0), text_size=60, text_align='center'),
    GameObject(obj_type='text', x=6000, y=100, text='That way --------->', text_color=(255, 255, 0), text_size=60, text_align='center'),
    GameObject(obj_type='text', x=10000, y=700, text="We are getting up aren't we?!", text_color=(255, 255, 0), text_size=60, text_align='center'),
    GameObject(obj_type='text', x=11000, y=900, text='By the way forgot to tell you', text_color=(255, 255, 0), text_size=60, text_align='center'),
    GameObject(obj_type='text', x=11000, y=800, text='You can actually control distance of the throw', text_color=(255, 255, 0), text_size=60, text_align='center'),
    GameObject(obj_type='text', x=11000, y=700, text='By keeping your mouse closer or further to the character :)', text_color=(255, 255, 0), text_size=60, text_align='center'),
    GameObject(obj_type='text', x=11000, y=150, text='<---------', text_color=(255, 255, 0), text_size=60, text_align='center'),
    GameObject(obj_type='text', x=11000, y=100, text="Go to that way, you ain't supposed to be here :)", text_color=(255, 255, 0), text_size=60, text_align='center'),
    GameObject(obj_type='text', x=10300, y=1120, text='Left first. Then up.', text_color=(255, 255, 0), text_size=60, text_align='center'),
    GameObject(obj_type='text', x=9450, y=1120, text='This platform moves. Wait for it, then jump on.', text_color=(255, 255, 0), text_size=60, text_align='center'),
    GameObject(obj_type='text', x=7950, y=1220, text='Stand on it and it will carry you up.', text_color=(255, 255, 0), text_size=60, text_align='center'),
    GameObject(obj_type='text', x=6950, y=1820, text='This is the top. For now.', text_color=(255, 255, 0), text_size=60, text_align='center'),
    GameObject(obj_type='text', x=8000, y=2150, text='Nice throw.', text_color=(170, 220, 255), text_size=50, text_align='center'),
    GameObject(obj_type='text', x=7825, y=2545, text='That looked painful.', text_color=(170, 220, 255), text_size=50, text_align='center'),
    GameObject(obj_type='text', x=6650, y=3445, text='Almost.', text_color=(170, 220, 255), text_size=50, text_align='center'),
    GameObject(obj_type='text', x=8050, y=3840, text="Don't look down. Or do.", text_color=(170, 220, 255), text_size=50, text_align='center'),
    GameObject(obj_type='text', x=8125, y=4375, text="The summit won't climb itself.", text_color=(170, 220, 255), text_size=50, text_align='center'),
    GameObject(obj_type='text', x=8250, y=4715, text='Candy is for eating, not for physics.', text_color=(170, 220, 255), text_size=50, text_align='center'),
    GameObject(obj_type='text', x=7825, y=5205, text="You're getting good at this.", text_color=(170, 220, 255), text_size=50, text_align='center'),
    GameObject(obj_type='text', x=8725, y=6125, text="I'm not judging. Much.", text_color=(170, 220, 255), text_size=50, text_align='center'),
    GameObject(obj_type='text', x=9650, y=6615, text="Take your time. The mountain isn't going anywhere.", text_color=(170, 220, 255), text_size=50, text_align='center'),
    GameObject(obj_type='text', x=9550, y=6965, text='That platform has seen better days.', text_color=(170, 220, 255), text_size=50, text_align='center'),
    GameObject(obj_type='text', x=9000, y=7115, text="We've come a long way.", text_color=(170, 220, 255), text_size=50, text_align='center'),
    GameObject(obj_type='text', x=8775, y=8000, text='Still here? Good.', text_color=(170, 220, 255), text_size=50, text_align='center'),
    GameObject(obj_type='text', x=9475, y=8445, text='Nice throw.', text_color=(170, 220, 255), text_size=50, text_align='center'),
    GameObject(obj_type='text', x=8500, y=9325, text='That looked painful.', text_color=(170, 220, 255), text_size=50, text_align='center'),
    GameObject(obj_type='text', x=9525, y=9690, text='Almost.', text_color=(170, 220, 255), text_size=50, text_align='center'),
    GameObject(obj_type='text', x=7650, y=10295, text="Don't look down. Or do.", text_color=(170, 220, 255), text_size=50, text_align='center'),
    GameObject(obj_type='text', x=8825, y=10715, text="The summit won't climb itself.", text_color=(170, 220, 255), text_size=50, text_align='center'),
    GameObject(obj_type='text', x=7300, y=11155, text='Candy is for eating, not for physics.', text_color=(170, 220, 255), text_size=50, text_align='center'),
    GameObject(obj_type='text', x=6300, y=11590, text="You're getting good at this.", text_color=(170, 220, 255), text_size=50, text_align='center'),
    GameObject(obj_type='text', x=5250, y=11985, text="I'm not judging. Much.", text_color=(170, 220, 255), text_size=50, text_align='center'),
    GameObject(obj_type='text', x=5350, y=12845, text="Take your time. The mountain isn't going anywhere.", text_color=(170, 220, 255), text_size=50, text_align='center'),
    GameObject(obj_type='text', x=5825, y=13700, text='That platform has seen better days.', text_color=(170, 220, 255), text_size=50, text_align='center'),
    GameObject(obj_type='text', x=3775, y=14185, text="We've come a long way.", text_color=(170, 220, 255), text_size=50, text_align='center'),
    GameObject(obj_type='text', x=5700, y=14525, text='Still here? Good.', text_color=(170, 220, 255), text_size=50, text_align='center'),
    GameObject(obj_type='text', x=5100, y=15505, text='Nice throw.', text_color=(170, 220, 255), text_size=50, text_align='center'),
    GameObject(obj_type='text', x=4675, y=16405, text='That looked painful.', text_color=(170, 220, 255), text_size=50, text_align='center'),
    GameObject(obj_type='text', x=6675, y=16705, text='Almost.', text_color=(170, 220, 255), text_size=50, text_align='center'),
    GameObject(obj_type='text', x=8275, y=16945, text="Don't look down. Or do.", text_color=(170, 220, 255), text_size=50, text_align='center'),
    GameObject(obj_type='text', x=9875, y=17185, text="The summit won't climb itself.", text_color=(170, 220, 255), text_size=50, text_align='center'),
    GameObject(obj_type='text', x=9875, y=17545, text='Candy is for eating, not for physics.', text_color=(170, 220, 255), text_size=50, text_align='center'),
]

# ========== Summit: platform and cabin come from the backdrop (see backdrop.summit_geometry) ==========


# ========== i18n / fonts / language selection ==========
def rebuild_fonts():
    global font, small_font, medium_font, big_font
    font = i18n.get_font(max(10, int(48 * i18n.scale())))
    small_font = i18n.get_font(max(10, int(24 * i18n.scale())))
    medium_font = i18n.get_font(max(10, int(72 * i18n.scale())))
    big_font = i18n.get_font(max(10, int(120 * i18n.scale())))


def refresh_texts():
    for obj in game:
        if getattr(obj, 'obj_type', '') != 'text':
            continue
        if getattr(obj, 'text_size', None) is not None:
            obj.text_font = i18n.get_font(max(10, int(obj.text_size * i18n.scale())))
        obj.render_text_surface()


def language_layout_top():
    return HEIGHT // 2 + 90


def language_button_rects():
    cols, rows, gap = 3, 3, 8
    top = language_layout_top()
    span = max(60, (HEIGHT - 180) - top)
    bh = max(24, min(44, (span - (rows - 1) * gap) // rows))
    bw = max(110, min(180, (WIDTH - 120) // cols - gap))
    total_w = cols * bw + (cols - 1) * gap
    x0 = WIDTH // 2 - total_w // 2
    rects = []
    for i, (code, name) in enumerate(i18n.LANGS):
        rect = pygame.Rect(x0 + (i % cols) * (bw + gap),
                           top + (i // cols) * (bh + gap), bw, bh)
        rects.append((code, name, rect))
    return rects


def update_camera(dt):
    global camera_x, camera_y
    target_x = player_x - WIDTH // 2 + player_width // 2
    target_y = player_y - HEIGHT // 2 + player_height // 2
    camera_x += (target_x - camera_x) * camera_smoothness
    camera_y += (target_y - camera_y) * camera_smoothness

def update_screen_shake(dt):
    global screen_shake, screen_shake_offset_x, screen_shake_offset_y
    
    if screen_shake > 0:
        screen_shake_offset_x = random.uniform(-screen_shake, screen_shake)
        screen_shake_offset_y = random.uniform(-screen_shake, screen_shake)
    else:
        screen_shake_offset_x = 0
        screen_shake_offset_y = 0
    
    screen_shake *= screen_shake_decay
    if screen_shake < 0.1:
        screen_shake = 0.0
        screen_shake_offset_x = 0
        screen_shake_offset_y = 0

def update_explosions(dt):
    explosions_to_remove = []
    for i, explosion in enumerate(explosions):
        if not explosion.update(dt):
            explosions_to_remove.append(i)
    
    for i in sorted(explosions_to_remove, reverse=True):
        if i < len(explosions):
            explosions.pop(i)

def draw_explosions(screen):
    for explosion in explosions:
        explosion.draw(screen)

def update_player(keys, dt, mouse_pos):
    global player_x, player_y, player_velocity_x, player_velocity_y
    global player_is_on_ground, player_facing_right
    global player_ground_platform, level_cleared
    global player_last_ground_time, player_continuous_air_time, player_momentum
    global can_throw, mouse_button_down
    global player_entry_time
    
    if player_is_on_ground:
        player_last_ground_time = 0.0
        player_continuous_air_time = 0.0
        player_momentum = min(1.0, player_momentum + dt * 0.5)
    else:
        player_last_ground_time += dt
        player_continuous_air_time += dt
        player_momentum = max(0.3, player_momentum - dt * 0.2)
    
    mouse_pressed = pygame.mouse.get_pressed()[0]
    
    current_time = pygame.time.get_ticks() / 1000.0
    is_protected = (current_time - player_entry_time) < ENTRY_PROTECTION_TIME
    
    if mouse_pressed and not is_protected:
        if can_throw and not mouse_button_down:
            throw_candy(mouse_pos)
            can_throw = False
            mouse_button_down = True
    else:
        can_throw = True
        mouse_button_down = False
    
    if player_is_on_ground:
        base_friction = summit_friction if summit_locked else ice_friction
        current_friction = base_friction * player_momentum
        if player_velocity_x > 0:
            player_velocity_x = max(0, player_velocity_x - current_friction * dt * 60)
        elif player_velocity_x < 0:
            player_velocity_x = min(0, player_velocity_x + current_friction * dt * 60)
    else:
        if player_velocity_x > 0:
            player_velocity_x = max(0, player_velocity_x - air_resistance * dt * 60)
        elif player_velocity_x < 0:
            player_velocity_x = min(0, player_velocity_x + air_resistance * dt * 60)
    
    current_max_speed = player_max_horizontal_speed
    
    if player_is_on_ground:
        current_max_speed = player_max_horizontal_speed * 1.2
    elif player_continuous_air_time > 1.0:
        current_max_speed = player_max_horizontal_speed * 0.7
    
    speed_ratio = abs(player_velocity_x) / current_max_speed
    
    if speed_ratio > 0.8:
        decay_factor = (speed_ratio - 0.8) * 2.0
        if player_velocity_x > 0:
            player_velocity_x -= player_velocity_x * decay_factor * player_velocity_decay_factor * dt * 60
        elif player_velocity_x < 0:
            player_velocity_x -= player_velocity_x * decay_factor * player_velocity_decay_factor * dt * 60
    
    if abs(player_velocity_x) > player_velocity_decay_threshold:
        excess_ratio = (abs(player_velocity_x) - player_velocity_decay_threshold) / player_velocity_decay_threshold
        excess_decay = excess_ratio * player_momentum_decay
        if player_velocity_x > 0:
            player_velocity_x -= player_velocity_x * excess_decay * dt * 60
        elif player_velocity_x < 0:
            player_velocity_x -= player_velocity_x * excess_decay * dt * 60
    
    player_velocity_x = max(-current_max_speed * 1.5, min(player_velocity_x, current_max_speed * 1.5))
    player_x += player_velocity_x * dt * 60
    player_velocity_y += player_gravity * dt * 60
    player_y += player_velocity_y * dt * 60
    
    check_collisions(dt)

def throw_candy(mouse_pos):
    achievements.add_candy()
    global player_velocity_x, candies, held_candy_state
    
    mouse_world_x = mouse_pos[0] + camera_x
    mouse_world_y = mouse_pos[1] + camera_y
    
    player_center_x = player_x + player_width // 2
    player_center_y = player_y + player_height // 2
    
    dx = mouse_world_x - player_center_x
    dy = mouse_world_y - player_center_y
    distance = math.sqrt(dx*dx + dy*dy)
    
    min_distance = MIN_THROW_DISTANCE
    max_distance = MAX_THROW_DISTANCE
    
    if distance > min_distance:
        dir_x = dx / distance
        dir_y = dy / distance
        
        start_x = player_center_x
        start_y = player_center_y
        
        distance_factor = min(distance / max_distance, 1.0)
        current_candy_power = candy_power_base + (candy_power_max - candy_power_base) * distance_factor
        
        candy_vel_x = dir_x * current_candy_power
        candy_vel_y = dir_y * current_candy_power
        
        recoil_strength = current_candy_power * 0.3
        player_velocity_x -= dir_x * recoil_strength
        
        # Remove the immediate sound here
        # sound_manager.play_throw()
        
        if 'held_candy_state' in globals():
            candy_type = held_candy_state['next_candy_type']
        else:
            candy_type = random.choice(['red', 'green'])
        
        trail_color = random.choice([
            EXPLOSION_RED_INNER,
            (255, 150, 50),
            (255, 100, 0),
            (255, 200, 100)
        ])
        
        candy = Candy(start_x, start_y, candy_vel_x, candy_vel_y, trail_color)
        candy.candy_type = candy_type
        if CANDY_TEXTURES_LOADED:
            candy.texture = candy_textures[candy_type]
        
        candies.append(candy)
        
        if 'held_candy_state' in globals():
            held_candy_state['next_candy_type'] = random.choice(['red', 'green'])
        
        global screen_shake
        screen_shake = 3.0
        
        return True
    
    return False

def update_candies(dt):
    candies_to_remove = []
    for i, candy in enumerate(candies):
        if not candy.update(dt):
            candies_to_remove.append(i)
    
    for i in sorted(candies_to_remove, reverse=True):
        if i < len(candies):
            candies.pop(i)

def draw_candies(screen):
    for candy in candies:
        candy.draw(screen)

def check_collisions(dt):
    global player_x, player_y, player_velocity_x, player_velocity_y, player_is_on_ground
    global player_ground_platform

    was_on_ground = player_is_on_ground
    standing_platform = player_ground_platform
    player_is_on_ground = False
    player_ground_platform = None

    # Carry the player with moving platforms first, then fix collisions to avoid jitter
    if was_on_ground and standing_platform is not None and standing_platform.is_moving:
        player_x += standing_platform.x - standing_platform.last_x
        player_y += standing_platform.y - standing_platform.last_y

    border_collision = check_world_border_collision()
    if border_collision:
        border_type, new_x, new_y, new_vel_x, new_vel_y = border_collision
        player_x = new_x
        player_y = new_y
        player_velocity_x = new_vel_x
        player_velocity_y = new_vel_y
        player_is_on_ground = True
    
    for obj in game:
        if obj.obj_type != 'platform':
            continue
            
        collision_type, new_x, new_y = obj.check_collision(
            player_x, player_y, player_width, player_height, player_velocity_y
        )
        
        if collision_type:
            if collision_type == "top":
                player_y = new_y
                player_velocity_y = 0
                player_is_on_ground = True
                
                player_ground_platform = obj
            
            elif collision_type == "side":
                player_x = new_x
                player_velocity_x *= -0.3
            
            elif collision_type == "bottom":
                player_y = new_y
                player_velocity_y = abs(player_velocity_y) * 0.3

def draw_player(screen, mouse_pos):
    draw_x, draw_y = apply_camera_offset(player_x, player_y)
    player_textures.draw(screen, draw_x, draw_y, player_width, player_height)

def draw_hand(screen, mouse_pos, is_ready=True):
    x, y = mouse_pos
    
    mouse_world_x = x + camera_x
    mouse_world_y = y + camera_y
    
    player_center_x = player_x + player_width // 2
    player_center_y = player_y + player_height // 2
    
    dx = mouse_world_x - player_center_x
    dy = mouse_world_y - player_center_y
    distance = math.sqrt(dx*dx + dy*dy)
    
    max_distance = player_width * 0.7
    if distance > max_distance:
        scale = max_distance / distance
        dx *= scale
        dy *= scale
        distance = max_distance
    
    hand_x = player_center_x + dx
    hand_y = player_center_y + dy
    
    hand_x, hand_y = check_hand_collision(hand_x, hand_y, player_center_x, player_center_y, distance)
    
    draw_x, draw_y = apply_camera_offset(hand_x, hand_y)
    
    if hand_texture_loaded and hand_texture is not None:
        if distance > 0:
            hand_angle = math.degrees(math.atan2(dy, dx))
        else:
            hand_angle = 0 if player_facing_right else 180
        
        rotated_hand = pygame.transform.rotate(hand_texture, -hand_angle)
        hand_rect = rotated_hand.get_rect(center=(draw_x, draw_y))
        screen.blit(rotated_hand, hand_rect)
        
        if is_ready:
            draw_held_candy(screen, draw_x, draw_y, hand_angle)
    else:
        pygame.draw.circle(screen, cursor_border_color, (int(draw_x), int(draw_y)), cursor_radius + cursor_width)
        pygame.draw.circle(screen, cursor_color, (int(draw_x), int(draw_y)), cursor_radius)
        
        if distance > 0:
            end_x = draw_x + (dx / distance) * cursor_radius * 1.5
            end_y = draw_y + (dy / distance) * cursor_radius * 1.5
            pygame.draw.line(screen, BLACK, (draw_x, draw_y), (end_x, end_y), 3)
        
        if not is_ready:
            cooling_surface = pygame.Surface((cursor_radius*2, cursor_radius*2), pygame.SRCALPHA)
            pygame.draw.circle(cooling_surface, ICE_BLUE, (cursor_radius, cursor_radius), cursor_radius)
            screen.blit(cooling_surface, (draw_x - cursor_radius, draw_y - cursor_radius))

def check_hand_collision(hand_x, hand_y, player_x, player_y, original_distance):
    collision_radius = candy_radius * 1.5
    
    for obj in game:
        if obj.obj_type != 'platform':
            continue
            
        platform_top = obj.y - obj.height
        platform_bottom = obj.y
        platform_left = obj.x
        platform_right = obj.x + obj.width
        
        if (hand_x > platform_left and hand_x < platform_right and
            hand_y > platform_top and hand_y < platform_bottom):
            
            dist_to_left = hand_x - platform_left
            dist_to_right = platform_right - hand_x
            dist_to_top = hand_y - platform_top
            dist_to_bottom = platform_bottom - hand_y
            
            min_dist = min(dist_to_left, dist_to_right, dist_to_top, dist_to_bottom)
            
            if min_dist == dist_to_left:
                hand_x = platform_left - collision_radius
            elif min_dist == dist_to_right:
                hand_x = platform_right + collision_radius
            elif min_dist == dist_to_top:
                hand_y = platform_top - collision_radius
            else:
                hand_y = platform_bottom + collision_radius
            break
    
    adjusted_x, adjusted_y = hand_x, hand_y
    for obj in game:
        if obj.obj_type != 'platform':
            continue
            
        platform_top = obj.y - obj.height
        platform_left = obj.x
        platform_right = obj.x + obj.width
        platform_bottom = obj.y
        
        closest_x = max(platform_left, min(adjusted_x, platform_right))
        closest_y = max(platform_top, min(adjusted_y, platform_bottom))
        
        distance_x = adjusted_x - closest_x
        distance_y = adjusted_y - closest_y
        distance = math.sqrt(distance_x*distance_x + distance_y*distance_y)
        
        if distance < collision_radius and distance > 0:
            overlap = collision_radius - distance
            adjusted_x += (distance_x / distance) * overlap * 1.1
            adjusted_y += (distance_y / distance) * overlap * 1.1
    
    dx = adjusted_x - player_x
    dy = adjusted_y - player_y
    new_distance = math.sqrt(dx*dx + dy*dy)
    
    max_distance = player_width * 3
    if new_distance > max_distance:
        scale = max_distance / new_distance
        adjusted_x = player_x + dx * scale
        adjusted_y = player_y + dy * scale
    
    return adjusted_x, adjusted_y

def draw_held_candy(screen, hand_x, hand_y, hand_angle):
    global held_candy_state
    
    if 'held_candy_state' not in globals():
        global held_candy_state
        held_candy_state = {
            'next_candy_type': random.choice(['red', 'green']),
            'wobble_offset': 0,
            'wobble_speed': 2.0,
            'wobble_amount': 0.3,
            'last_update_time': pygame.time.get_ticks(),
            'candy_rotation': 0,
            'rotation_speed': 2.0
        }
    
    candy_type = held_candy_state['next_candy_type']
    
    current_time = pygame.time.get_ticks()
    delta_time = (current_time - held_candy_state['last_update_time']) / 1000.0
    held_candy_state['last_update_time'] = current_time
    
    held_candy_state['wobble_offset'] += held_candy_state['wobble_speed'] * delta_time
    wobble = math.sin(held_candy_state['wobble_offset']) * held_candy_state['wobble_amount']
    
    candy_distance = candy_radius * 1.2
    candy_angle_rad = math.radians(hand_angle) + wobble
    
    offset_distance = candy_radius * 0.2
    candy_x = hand_x + math.cos(candy_angle_rad) * (candy_distance + offset_distance)
    candy_y = hand_y + math.sin(candy_angle_rad) * (candy_distance + offset_distance)
    
    if candy_type in candy_textures and candy_textures[candy_type] is not None:
        candy_textures[candy_type].draw(screen, candy_x, candy_y, hand_angle)
    else:
        draw_simple_candy_with_wobble(screen, candy_x, candy_y, candy_type, hand_angle, wobble)

def draw_simple_candy_with_wobble(screen, x, y, candy_type, hand_angle, wobble):
    if candy_type == 'red':
        candy_color = (255, 50, 50)
        highlight_color = (255, 150, 150)
        stripe_color = (255, 255, 200, 200)
    else:
        candy_color = (50, 255, 50)
        highlight_color = (150, 255, 150)
        stripe_color = (255, 255, 200, 200)
    
    candy_size = candy_radius * 2
    candy_surface = pygame.Surface((candy_size, candy_size), pygame.SRCALPHA)
    
    wobble_factor = abs(math.sin(wobble * 2)) * 0.2
    
    center_x, center_y = candy_radius, candy_radius
    
    pygame.draw.circle(candy_surface, candy_color, (center_x, center_y), candy_radius)
    
    highlight_offset = wobble * 10
    highlight_x = center_x + math.cos(wobble) * candy_radius * 0.3 + highlight_offset
    highlight_y = center_y + math.sin(wobble) * candy_radius * 0.3
    
    highlight_width = candy_radius * (0.6 + wobble_factor * 0.2)
    highlight_height = candy_radius * (0.4 - wobble_factor * 0.1)
    
    highlight_surface = pygame.Surface((int(highlight_width * 2), int(highlight_height * 2)), pygame.SRCALPHA)
    pygame.draw.ellipse(highlight_surface, highlight_color, (0, 0, highlight_width * 2, highlight_height * 2))
    
    highlight_angle = math.degrees(wobble)
    rotated_highlight = pygame.transform.rotate(highlight_surface, highlight_angle)
    highlight_rect = rotated_highlight.get_rect(center=(int(highlight_x), int(highlight_y)))
    
    combined_surface = pygame.Surface((candy_size, candy_size), pygame.SRCALPHA)
    combined_surface.blit(candy_surface, (0, 0))
    combined_surface.blit(rotated_highlight, highlight_rect)
    
    stripe_width = 2
    stripe_length = candy_radius * 1.5
    
    stripe_angle = hand_angle + 90
    stripe_angle_rad = math.radians(stripe_angle)
    
    bend_amount = math.sin(wobble) * 0.3
    
    for i in range(3):
        offset = (i - 1) * candy_radius * 0.4
        
        start_x = center_x + math.cos(stripe_angle_rad) * offset
        start_y = center_y + math.sin(stripe_angle_rad) * offset
        
        end_x = start_x + math.cos(stripe_angle_rad + bend_amount) * stripe_length
        end_y = start_y + math.sin(stripe_angle_rad + bend_amount) * stripe_length
        
        end_x2 = start_x - math.cos(stripe_angle_rad + bend_amount) * stripe_length
        end_y2 = start_y - math.sin(stripe_angle_rad + bend_amount) * stripe_length
        
        pygame.draw.line(combined_surface, stripe_color, (int(start_x), int(start_y)), (int(end_x), int(end_y)), stripe_width)
        pygame.draw.line(combined_surface, stripe_color, (int(start_x), int(start_y)), (int(end_x2), int(end_y2)), stripe_width)
    
    glow_alpha = int(100 + abs(math.sin(wobble)) * 100)
    glow_surface = pygame.Surface((candy_size, candy_size), pygame.SRCALPHA)
    glow_radius = candy_radius * (1.2 + wobble_factor * 0.3)
    pygame.draw.circle(glow_surface, (*candy_color[:3], glow_alpha), (center_x, center_y), int(glow_radius))
    
    final_surface = pygame.Surface((candy_size, candy_size), pygame.SRCALPHA)
    final_surface.blit(glow_surface, (0, 0))
    final_surface.blit(combined_surface, (0, 0))
    
    candy_draw_angle = hand_angle + math.degrees(wobble * 0.5)
    
    rotated_candy = pygame.transform.rotate(final_surface, candy_draw_angle)
    rotated_rect = rotated_candy.get_rect(center=(x, y))
    screen.blit(rotated_candy, rotated_rect)

def draw_simple_candy(screen, x, y, candy_type):
    if candy_type == 'red':
        candy_color = (255, 50, 50)
        highlight_color = (255, 150, 150)
    else:
        candy_color = (50, 255, 50)
        highlight_color = (150, 255, 150)
    
    candy_size = candy_radius * 2
    candy_surface = pygame.Surface((candy_size, candy_size), pygame.SRCALPHA)
    
    pygame.draw.circle(candy_surface, candy_color, (candy_radius, candy_radius), candy_radius)
    
    highlight_x = candy_radius * 1.3
    highlight_y = candy_radius * 0.7
    pygame.draw.circle(candy_surface, highlight_color, (int(highlight_x), int(highlight_y)), candy_radius // 2)
    
    stripe_color = (255, 255, 255, 200)
    stripe_width = 2
    pygame.draw.line(candy_surface, stripe_color, (candy_radius, 2), (candy_radius, candy_size - 2), stripe_width)
    pygame.draw.line(candy_surface, stripe_color, (2, candy_radius), (candy_size - 2, candy_radius), stripe_width)
    
    candy_rect = candy_surface.get_rect(center=(x, y))
    screen.blit(candy_surface, candy_rect)

def update_candy_type():
    global held_candy_state
    if 'held_candy_state' in globals():
        held_candy_state['next_candy_type'] = random.choice(['red', 'green'])
        held_candy_state['wobble_offset'] = 0

# Hand sprite
hand_texture = None
hand_texture_loaded = False

try:
    hand_texture = pygame.image.load(paths.asset("textures", "Hand.png")).convert_alpha()
    hand_size = int(cursor_radius * 3)
    hand_texture = pygame.transform.scale(hand_texture, (hand_size, hand_size))
    hand_texture_loaded = True
except pygame.error:
    pass

def draw_custom_cursor(screen, mouse_pos, is_ready=True):
    x, y = mouse_pos
    
    cursor_radius = 15
    border_width = 2
    inner_radius = cursor_radius - border_width
    
    mouse_pressed = pygame.mouse.get_pressed()[0]
    
    border_color = (0, 0, 0)
    inner_color_default = (255, 255, 255, 150)
    inner_color_pressed = (173, 216, 230, 200)
    
    if mouse_pressed:
        inner_color = inner_color_pressed
    else:
        inner_color = inner_color_default
    
    cursor_size = cursor_radius * 2
    cursor_surface = pygame.Surface((cursor_size, cursor_size), pygame.SRCALPHA)
    
    pygame.draw.circle(cursor_surface, border_color, (cursor_radius, cursor_radius), cursor_radius)
    pygame.draw.circle(cursor_surface, inner_color, (cursor_radius, cursor_radius), inner_radius)
    
    if not is_ready:
        cooling_surface = pygame.Surface((cursor_size, cursor_size), pygame.SRCALPHA)
        pygame.draw.circle(cooling_surface, (100, 100, 255, 100), (cursor_radius, cursor_radius), inner_radius)
        cursor_surface.blit(cooling_surface, (0, 0))
    
    pygame.draw.circle(cursor_surface, (255, 255, 255, 200), (cursor_radius, cursor_radius), 3)
    
    cursor_rect = cursor_surface.get_rect(center=(x, y))
    screen.blit(cursor_surface, cursor_rect)
    
    if mouse_pressed:
        effect_size = int(cursor_radius * 2.5)
        effect_surface = pygame.Surface((effect_size, effect_size), pygame.SRCALPHA)
        pygame.draw.circle(effect_surface, (173, 216, 230, 80), (effect_size//2, effect_size//2), effect_size//2)
        effect_rect = effect_surface.get_rect(center=(x, y))
        screen.blit(effect_surface, effect_rect)

def draw_game_objects_with_textures(screen):
    # Draw in layers: platforms first, then all texts on top
    for obj in game:
        if obj.obj_type == 'text':
            continue
        if obj.obj_type == 'platform' and hasattr(obj, 'texture_type') and obj.texture_type is not None:
            obj.draw_with_texture(screen)
        else:
            obj.draw(screen)
    for obj in game:
        if obj.obj_type == 'text':
            obj.draw(screen)

MENU_KEYS = ("continue", "new_game", "saves", "achievements", "settings", "exit")


def menu_buttons():
    bw, bh = 330, 56
    x = WIDTH // 2 - bw // 2
    y0 = HEIGHT // 2 - 135
    return [(key, pygame.Rect(x, y0 + i * 66, bw, bh)) for i, key in enumerate(MENU_KEYS)]


def draw_menu():
    title_text = big_font.render("A SLIPERY CLIMB", True, WHITE)
    screen.blit(title_text, title_text.get_rect(center=(WIDTH // 2, HEIGHT // 5)))
    return menu_buttons()


def saves_slot_rects():
    bw, bh = 560, 66
    x = WIDTH // 2 - bw // 2
    y0 = HEIGHT // 4 + 45
    out = []
    for i in range(1, SaveManager.SLOT_COUNT + 1):
        y = y0 + (i - 1) * 78
        out.append((i, pygame.Rect(x, y, bw - 70, bh), pygame.Rect(x + bw - 60, y, 60, bh)))
    return out


def first_empty_slot():
    for i in range(1, SaveManager.SLOT_COUNT + 1):
        if not SaveManager.slot_exists(i):
            return i
    return None


def any_empty_slot():
    return first_empty_slot() is not None


def saves_back_rect():
    bw, bh = 260, 56
    return pygame.Rect(WIDTH // 2 - bw // 2, HEIGHT - 120, bw, bh)


def victory_button_rect():
    bw, bh = 320, 60
    return pygame.Rect(WIDTH // 2 - bw // 2, HEIGHT - 150, bw, bh)


def load_slot_into_game(slot):
    global current_slot, player_x, player_y, camera_x, camera_y
    current_slot = slot
    data = SaveManager.load_slot(slot)
    if data:
        player_x = data.get("player_x", 100)
        player_y = data.get("player_y", ground_level - player_height)
        camera_x = player_x - WIDTH // 2
        camera_y = player_y - HEIGHT // 2
    else:
        reset_game()

def reset_game():
    """Reset the game."""
    global player_x, player_y, player_velocity_x, player_velocity_y
    global player_is_on_ground, player_facing_right
    global player_last_ground_time, player_continuous_air_time, player_momentum
    global candies, explosions, camera_x, camera_y
    global can_throw, mouse_button_down
    global player_ground_platform, level_cleared, summit_locked
    global summit_msg_timer, summit_msg_shown
    
    player_x = 100
    player_y = ground_level - player_height
    player_velocity_x = 0
    player_velocity_y = 0
    player_is_on_ground = False
    player_ground_platform = None
    player_facing_right = True
    level_cleared = False
    summit_locked = False
    summit_msg_timer = 0.0
    summit_msg_shown = False
    
    player_last_ground_time = 0.0
    player_continuous_air_time = 0.0
    player_momentum = 1.0
    
    candies.clear()
    explosions.clear()
    
    camera_x = 0
    camera_y = 0
    
    can_throw = True
    mouse_button_down = False
    
    SaveManager.delete_slot(current_slot)
    achievements.reset_run()
    flavor.reset_tutorials()  # FLAVOR

class SaveManager:
    SLOT_COUNT = 5

    @staticmethod
    def slot_file(slot):
        return paths.user("save_slot_%d.json" % int(slot))

    @staticmethod
    def slot_exists(slot):
        return os.path.exists(SaveManager.slot_file(slot))

    @staticmethod
    def save_slot(slot, player_x, player_y):
        data = {"player_x": player_x, "player_y": player_y,
                "height": int(round(ground_level - (player_y + player_height))),
                "cleared": bool(level_cleared), "clears": achievements.clears(),
                "time": time.time()}
        try:
            with open(SaveManager.slot_file(slot), "w") as f:
                json.dump(data, f)
            return True
        except Exception:
            return False

    @staticmethod
    def load_slot(slot):
        try:
            path = SaveManager.slot_file(slot)
            if os.path.exists(path):
                with open(path, "r") as f:
                    return json.load(f)
        except Exception:
            pass
        return None

    @staticmethod
    def delete_slot(slot):
        try:
            path = SaveManager.slot_file(slot)
            if os.path.exists(path):
                os.remove(path)
            return True
        except Exception:
            return False

    @staticmethod
    def save_exists():
        return any(SaveManager.slot_exists(i)
                   for i in range(1, SaveManager.SLOT_COUNT + 1))

    @staticmethod
    def latest_slot():
        best, best_t = None, -1.0
        for i in range(1, SaveManager.SLOT_COUNT + 1):
            d = SaveManager.load_slot(i)
            if d:
                t = float(d.get("time", 0.0))
                if t > best_t:
                    best, best_t = i, t
        return best
    
    @staticmethod
    def save_settings(sound_vol, music_vol):
        settings_data = {"sound_volume": sound_vol, "music_volume": music_vol,
                         "language": i18n.current}
        try:
            with open(SETTINGS_FILE, 'w') as f:
                json.dump(settings_data, f)
            return True
        except:
            return False
    
    @staticmethod
    def load_settings():
        try:
            if os.path.exists(SETTINGS_FILE):
                with open(SETTINGS_FILE, 'r') as f:
                    return json.load(f)
        except:
            pass
        return None

settings = SaveManager.load_settings()
if settings:
    sound_volume = settings.get("sound_volume", 0.7)
    music_volume = settings.get("music_volume", 0.5)
    sound_manager.set_sound_volume(sound_volume)
    sound_manager.set_music_volume(music_volume)

i18n.set_lang(settings.get("language", "en") if settings else "en")
rebuild_fonts()
refresh_texts()

# ========== Nine-patch system ==========
class CompleteTiledNinePatch:
    """Terrain texture (three slices + rounded corners + edge joining).

    * The body tiles tundraCenter seamlessly; the snow line uses the first
      26 rows of tundraMid;
    * Corners borrow only the alpha of the four outer corner pixels, so the
      shape holds at any height;
    * corners=(top-left, top-right, bottom-left, bottom-right): edges that
      touch neighbours or the ground skip the round corner;
    * phase makes one row of platforms share the texture origin so the snow
      line is continuous;
    * cached by (width, height, phase, corners), one blit per static platform;
    * huge platforms (ground / walls) tile only the visible part of the screen.
    """

    CORNER = 12
    BAND = 26
    CACHE_LIMIT = 2_000_000

    def __init__(self, left_path, mid_path, right_path, center_path, border_size=8):
        self.border_size = border_size
        self.left = self._load(left_path)
        self.mid = self._load(mid_path)
        self.right = self._load(right_path)
        self.center = self._load(center_path)
        self.cap_w = self.left.get_width()
        self._cache = {}
        self._alpha_left = self._white_alpha(self.left)
        self._alpha_right = self._white_alpha(self.right)

    # ---------------- loading ----------------
    @staticmethod
    def darken_texture(texture, factor=0.7):
        shade = pygame.Surface(texture.get_size(), pygame.SRCALPHA)
        shade.fill((int(255 * factor),) * 3 + (255,))
        out = texture.copy()
        out.blit(shade, (0, 0), special_flags=pygame.BLEND_RGB_MULT)
        return out

    def _load(self, path):
        return self.darken_texture(pygame.image.load(path).convert_alpha())

    @staticmethod
    def _white_alpha(tex):
        w, h = tex.get_size()
        out = pygame.Surface((w, h), pygame.SRCALPHA)
        out.fill((255, 255, 255, 0))
        for y in range(h):
            for x in range(w):
                a = tex.get_at((x, y)).a
                if a:
                    out.set_at((x, y), (255, 255, 255, a))
        return out

    # ---------------- helpers ----------------
    @staticmethod
    def _tile_from(surf, tex, sx, sy, w, h):
        tw, th = tex.get_size()
        yy = sy
        while yy < h:
            xx = sx
            while xx < w:
                surf.blit(tex, (xx, yy))
                xx += tw
            yy += th

    @staticmethod
    def _tile_area(target, tex, start_x, start_y, rect):
        tw, th = tex.get_size()
        xx = start_x + max(0, (rect.left - start_x) // tw) * tw
        yy0 = start_y + max(0, (rect.top - start_y) // th) * th
        while xx < rect.right:
            yy = yy0
            while yy < rect.bottom:
                target.blit(tex, (xx, yy))
                yy += th
            xx += tw

    # ---------------- rendering ----------------
    def _render(self, w, h, phase, corners):
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        self._tile_from(surf, self.center, -phase, 0, w, h)
        self._tile_from(surf, self.mid, -phase, 0, w, min(self.BAND, h))

        tl, tr, bl, br = corners
        if w >= self.cap_w * 2 and h >= 2 and any(corners):
            c = min(self.CORNER, h // 2)
            mask = pygame.Surface((w, h), pygame.SRCALPHA)
            mask.fill((255, 255, 255, 255))
            cap_h = self._alpha_left.get_height()
            if tl:
                mask.blit(self._alpha_left.subsurface((0, 0, self.cap_w, c)),
                          (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            if bl:
                mask.blit(self._alpha_left.subsurface((0, cap_h - c, self.cap_w, c)),
                          (0, h - c), special_flags=pygame.BLEND_RGBA_MULT)
            if tr:
                mask.blit(self._alpha_right.subsurface((0, 0, self.cap_w, c)),
                          (w - self.cap_w, 0), special_flags=pygame.BLEND_RGBA_MULT)
            if br:
                mask.blit(self._alpha_right.subsurface((0, cap_h - c, self.cap_w, c)),
                          (w - self.cap_w, h - c), special_flags=pygame.BLEND_RGBA_MULT)
            surf.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        return surf

    def draw(self, screen, x, y, width, height, phase=0, corners=(True, True, True, True)):
        if width <= 0 or height <= 0:
            return
        x, y, width, height = int(x), int(y), int(width), int(height)
        phase = int(phase) % self.center.get_width()

        key = (width, height, phase, corners)
        surf = self._cache.get(key)
        if surf is None and width * height <= self.CACHE_LIMIT:
            surf = self._render(width, height, phase, corners)
            self._cache[key] = surf
        if surf is not None:
            screen.blit(surf, (x, y))
            return

        screen_rect = screen.get_rect()
        rect = pygame.Rect(x, y, width, height).clip(screen_rect)
        if rect.width <= 0 or rect.height <= 0:
            return
        self._tile_area(screen, self.center, x - phase, y, rect)
        band = pygame.Rect(x, y, width, min(self.BAND, height)).clip(screen_rect)
        if band.width > 0 and band.height > 0:
            self._tile_area(screen, self.mid, x - phase, y, band)

# Load nine-patch
complete_nine_patch = CompleteTiledNinePatch(
    paths.asset("textures", "tundraLeft.png"),
    paths.asset("textures", "tundraMid.png"),
    paths.asset("textures", "tundraRight.png"),
    paths.asset("textures", "tundraCenter.png"),
    border_size=8
)
TEXTURES_LOADED = True

# ========== Candy texture ==========
class CandyCannonTexture:
    def __init__(self, stick_path, top_path, scale=1.0):
        try:
            self.stick_texture = pygame.image.load(stick_path).convert_alpha()
            self.top_texture = pygame.image.load(top_path).convert_alpha()
            self.texture_loaded = True
        except pygame.error:
            self.texture_loaded = False
        
        if scale != 1.0 and self.texture_loaded:
            stick_w = int(self.stick_texture.get_width() * scale)
            stick_h = int(self.stick_texture.get_height() * scale)
            self.stick_texture = pygame.transform.scale(self.stick_texture, (stick_w, stick_h))
            
            top_w = int(self.top_texture.get_width() * scale)
            top_h = int(self.top_texture.get_height() * scale)
            self.top_texture = pygame.transform.scale(self.top_texture, (top_w, top_h))
        
        self.stick_width = self.stick_texture.get_width()
        self.stick_height = self.stick_texture.get_height()
        self.top_width = self.top_texture.get_width()
        self.top_height = self.top_texture.get_height()
        
        self.combined_height = self.stick_height + self.top_height
        self.combined_width = max(self.stick_width, self.top_width)
        
        self.rotated_cache = {}
    
    def get_rotated_texture(self, angle):
        angle_key = int(angle) % 360
        
        if angle_key in self.rotated_cache:
            return self.rotated_cache[angle_key]
        
        combined = pygame.Surface((self.combined_width, self.combined_height), pygame.SRCALPHA)
        
        stick_x = (self.combined_width - self.stick_width) // 2
        combined.blit(self.stick_texture, (stick_x, self.top_height))
        
        top_x = (self.combined_width - self.top_width) // 2
        combined.blit(self.top_texture, (top_x, 0))
        
        rotated = pygame.transform.rotate(combined, angle)
        self.rotated_cache[angle_key] = rotated
        
        return rotated
    
    def draw(self, screen, x, y, angle=0):
        if not self.texture_loaded:
            return
        
        rotated_texture = self.get_rotated_texture(angle)
        texture_rect = rotated_texture.get_rect(center=(x, y))
        screen.blit(rotated_texture, texture_rect)

candy_textures = {'red': None, 'green': None}

try:
    candy_textures['red'] = CandyCannonTexture(
        paths.asset("textures", "caneRed.png"),
        paths.asset("textures", "caneRedTop.png"),
        scale=0.3
    )
    candy_textures['green'] = CandyCannonTexture(
        paths.asset("textures", "caneGreen.png"),
        paths.asset("textures", "caneGreenTop.png"),
        scale=0.3
    )
    CANDY_TEXTURES_LOADED = True
except:
    CANDY_TEXTURES_LOADED = False

# ========== Slider class ==========
class Slider:
    def __init__(self, x, y, width, height, min_val, max_val, initial_val, label):
        self.rect = pygame.Rect(x, y, width, height)
        self.min_val = min_val
        self.max_val = max_val
        self.value = initial_val
        self.label = label
        self.dragging = False
        self.drag_started_in_rect = False
        self.selected = False  # selected?
        
        self.handle_radius = 15
        progress = (initial_val - min_val) / (max_val - min_val)
        self.handle_x = x + (width * progress)
        
        # Plus / minus buttons
        self.button_size = 30
        self.minus_button = pygame.Rect(x - self.button_size - 5, y + height//2 - self.button_size//2, 
                                        self.button_size, self.button_size)
        self.plus_button = pygame.Rect(x + width + 5, y + height//2 - self.button_size//2, 
                                       self.button_size, self.button_size)
        
        # Repeat adjustment
        self.repeat_timer = 0
        self.repeat_delay = 0.3  # initial delay (s)
        self.repeat_interval = 0.01  # repeat interval (s)
        self.repeat_direction = None  # 'left', 'right', 'minus', 'plus'
        self.last_repeat_time = 0
        
        # Step size
        self.step = 0.01
    
    def draw(self, screen):
        # Bar color depends on selection
        bar_color = GREEN if self.selected else DARK_GRAY
        
        # Draw slider track
        pygame.draw.rect(screen, bar_color, self.rect)
        pygame.draw.rect(screen, WHITE, self.rect, 2)
        
        # Draw slider handle
        handle_x = max(self.rect.left, min(self.handle_x, self.rect.right))
        
        pygame.draw.circle(screen, GREEN, (int(handle_x), self.rect.centery), self.handle_radius)
        pygame.draw.circle(screen, WHITE, (int(handle_x), self.rect.centery), self.handle_radius, 2)
        
        # Draw plus/minus buttons (highlighted when selected)
        minus_color = YELLOW if (self.selected and self.minus_button.collidepoint(pygame.mouse.get_pos())) else (LIGHT_BLUE if self.minus_button.collidepoint(pygame.mouse.get_pos()) else GRAY)
        pygame.draw.rect(screen, minus_color, self.minus_button)
        pygame.draw.rect(screen, WHITE, self.minus_button, 2)
        minus_text = small_font.render("-", True, WHITE)
        minus_rect = minus_text.get_rect(center=self.minus_button.center)
        screen.blit(minus_text, minus_rect)
        
        plus_color = YELLOW if (self.selected and self.plus_button.collidepoint(pygame.mouse.get_pos())) else (LIGHT_BLUE if self.plus_button.collidepoint(pygame.mouse.get_pos()) else GRAY)
        pygame.draw.rect(screen, plus_color, self.plus_button)
        pygame.draw.rect(screen, WHITE, self.plus_button, 2)
        plus_text = small_font.render("+", True, WHITE)
        plus_rect = plus_text.get_rect(center=self.plus_button.center)
        screen.blit(plus_text, plus_rect)
        
        # Draw label and value (highlighted when selected)
        label_color = YELLOW if self.selected else WHITE
        label_text = small_font.render(f"{i18n.ui(self.label)}: {int(self.value * 100)}%", True, label_color)
        screen.blit(label_text, (self.rect.x, self.rect.y - 25))
        
        
    
    def handle_event(self, event):
        mouse_pos = pygame.mouse.get_pos()
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                # Check plus/minus clicks
                if self.minus_button.collidepoint(mouse_pos):
                    self.adjust_value(-self.step)
                    # Start repeat adjustment
                    self.start_repeat('minus')
                    return "value_changed"
                elif self.plus_button.collidepoint(mouse_pos):
                    self.adjust_value(self.step)
                    # Start repeat adjustment
                    self.start_repeat('plus')
                    return "value_changed"
                
                # Check clicks on the track or handle
                if (self.rect.top - self.handle_radius <= mouse_pos[1] <= self.rect.bottom + self.handle_radius and
                    self.rect.left - self.handle_radius <= mouse_pos[0] <= self.rect.right + self.handle_radius):
                    
                    self.dragging = True
                    self.drag_started_in_rect = True
                    self.handle_x = max(self.rect.left, min(mouse_pos[0], self.rect.right))
                    progress = (self.handle_x - self.rect.left) / self.rect.width
                    self.value = self.min_val + progress * (self.max_val - self.min_val)
                    return "selected_and_changed"
                
                # Check clicks elsewhere on the slider (selection)
                if self.rect.collidepoint(mouse_pos):
                    return "selected"
                    
        elif event.type == pygame.MOUSEMOTION:
            # Keep dragging while the drag flag is set
            if self.dragging:
                self.handle_x = max(self.rect.left, min(mouse_pos[0], self.rect.right))
                progress = (self.handle_x - self.rect.left) / self.rect.width
                self.value = self.min_val + progress * (self.max_val - self.min_val)
                return "value_changed"
                    
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                if self.dragging:
                    self.dragging = False
                    self.drag_started_in_rect = False
                    return "value_changed"
                # Stop repeat adjustment
                if self.repeat_direction:
                    self.stop_repeat()
        
        return None
    
    def update_repeat(self, dt):
        """Update repeat adjustment."""
        if not self.repeat_direction:
            return False
        
        current_time = pygame.time.get_ticks() / 1000.0
        
        # Initial delay
        if self.repeat_timer == 0:
            self.repeat_timer = current_time
            return False
        
        # Check if it is time to trigger
        if current_time - self.repeat_timer >= self.repeat_delay:
            # Check repeat interval
            if self.last_repeat_time == 0 or current_time - self.last_repeat_time >= self.repeat_interval:
                self.last_repeat_time = current_time
                
                # Apply adjustment
                if self.repeat_direction == 'left':
                    self.adjust_value(-self.step)
                elif self.repeat_direction == 'right':
                    self.adjust_value(self.step)
                elif self.repeat_direction == 'minus':
                    self.adjust_value(-self.step)
                elif self.repeat_direction == 'plus':
                    self.adjust_value(self.step)
                
                return True
        
        return False
    
    def start_repeat(self, direction):
        """Start repeat adjustment."""
        self.repeat_direction = direction
        self.repeat_timer = 0
        self.last_repeat_time = 0
    
    def stop_repeat(self):
        """Stop repeat adjustment."""
        self.repeat_direction = None
        self.repeat_timer = 0
        self.last_repeat_time = 0
    
    def adjust_value(self, delta):
        """Adjust the value by one step."""
        self.value = max(self.min_val, min(self.max_val, self.value + delta))
        self.update_handle_position()
    
    def update_handle_position(self):
        """Update the handle position."""
        progress = (self.value - self.min_val) / (self.max_val - self.min_val)
        self.handle_x = self.rect.left + (self.rect.width * progress)
    
    def handle_keyboard(self, key, is_pressed=False):
        """Handle keyboard adjustment."""
        if not self.selected:
            return False
        
        if key == pygame.K_LEFT:
            if is_pressed:
                self.start_repeat('left')
            self.adjust_value(-self.step)
            return True
        elif key == pygame.K_RIGHT:
            if is_pressed:
                self.start_repeat('right')
            self.adjust_value(self.step)
            return True
        return False
    
    def handle_keyboard_release(self, key):
        """Handle keyboard release."""
        if key == pygame.K_LEFT and self.repeat_direction == 'left':
            self.stop_repeat()
        elif key == pygame.K_RIGHT and self.repeat_direction == 'right':
            self.stop_repeat()
    
    def select(self):
        """Select this slider."""
        self.selected = True
    
    def deselect(self):
        """Deselect this slider."""
        self.selected = False
        self.stop_repeat()  # stop repeat adjustment when deselected

# ========== Main loop ==========
def draw_summit_hint(screen):
    """Summit: put the arrow + hint on the side where the cabin is."""
    if level_cleared:
        return
    feet = ground_level - (player_y + player_height)
    if feet < 17800:
        return
    x0, x1, top_h, house_rect, anchored = backdrop_layer.summit_geometry(
        camera_x, camera_y, feet)
    if not anchored:
        return
    to_left = house_rect.centerx < player_x
    hint = i18n.text("Gifts first: walk to the cabin!")
    surf = font.render(hint, True, (255, 228, 140))
    arrow_font = i18n.get_font(max(10, int(64 * i18n.scale())))
    arrow = arrow_font.render("<---------" if to_left else "--------->",
                              True, (255, 228, 140))
    bob = int(6 * math.sin(pygame.time.get_ticks() / 300.0))
    y = int(HEIGHT * 0.13)
    if to_left:
        screen.blit(surf, surf.get_rect(topleft=(40, y)))
        screen.blit(arrow, arrow.get_rect(topleft=(50, y + 58 + bob)))
    else:
        screen.blit(surf, surf.get_rect(topright=(WIDTH - 40, y)))
        screen.blit(arrow, arrow.get_rect(topright=(WIDTH - 50, y + 58 + bob)))


def draw_victory(screen):
    veil = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    veil.fill((0, 0, 0, 150))
    screen.blit(veil, (0, 0))
    draw_text(screen, i18n.ui("win_title"), WIDTH // 2, int(HEIGHT * 0.30),
              WHITE, big_font, "center")
    draw_text(screen, i18n.ui("win_hint"), WIDTH // 2, int(HEIGHT * 0.38),
              YELLOW, font, "center")
    btn = victory_button_rect()
    hover = btn.collidepoint(pygame.mouse.get_pos())
    pygame.draw.rect(screen, WHITE if hover else LIGHT_BLUE, btn)
    pygame.draw.rect(screen, BLACK, btn, 2)
    surface = font.render(i18n.ui("return"), True, BLACK)
    screen.blit(surface, surface.get_rect(center=btn.center))


def draw_summit_msg(screen):
    feet = ground_level - (player_y + player_height)
    if feet >= 17800:      # summit uses the final hint, no repeated summit message
        return
    if summit_msg_timer <= 0:
        return
    text = i18n.ui("summit_msg")
    surface = font.render(text, True, (255, 228, 140))
    surface.set_alpha(int(255 * min(1.0, summit_msg_timer / 0.9)))
    rect = surface.get_rect(center=(WIDTH // 2, int(HEIGHT * 0.20)))
    screen.blit(surface, rect)


def draw_chatter(screen):
    if chatter_life <= 0 or not chatter_text:
        return
    surf = i18n.get_font(max(10, int(30 * i18n.scale()))).render(
        chatter_text, True, (230, 236, 255))
    alpha = int(255 * min(1.0, chatter_life / 0.6) * min(1.0, (CHATTER_TIME - chatter_life) / 0.5 + 0.35))
    surf.set_alpha(max(0, min(255, alpha)))
    rect = surf.get_rect(center=(WIDTH // 2, int(HEIGHT * 0.80)))
    pad = 18
    box = pygame.Surface((rect.width + pad * 2, rect.height + pad), pygame.SRCALPHA)
    pygame.draw.rect(box, (20, 24, 60, int(alpha * 0.55)),
                     box.get_rect(), border_radius=12)
    screen.blit(box, (rect.x - pad, rect.y - pad // 2))
    screen.blit(surf, rect)


# ========== Cutscenes: new-save intro / victory ==========
CUTSCENE_STARS = [(random.random(), random.random(), random.random()) for _ in range(110)]


def start_cutscene(kind):
    global current_state, cutscene_kind, cutscene_t, cutscene_len, cutscene_hold
    cutscene_kind = kind
    cutscene_t = 0.0
    cutscene_hold = False
    cutscene_len = CUTSCENE_INTRO_LEN if kind == "intro" else CUTSCENE_WIN_LEN
    current_state = GameState.CUTSCENE


def end_cutscene():
    global current_state, level_cleared, player_entry_time, cutscene_hold, cutscene_t
    if cutscene_kind == "win":
        level_cleared = True          # black victory screen appears after the cutscene (or skip)
    cutscene_hold = False
    current_state = GameState.PLAYING
    player_entry_time = pygame.time.get_ticks() / 1000.0


def update_cutscene(dt):
    global cutscene_t
    cutscene_t += dt
    if cutscene_t >= cutscene_len:
        cutscene_t = cutscene_len
        end_cutscene()


_CUT_BG = None


def _cut_bg():
    global _CUT_BG
    if _CUT_BG is None or _CUT_BG.get_size() != (WIDTH, HEIGHT):
        small = pygame.Surface((1, 48))
        for i in range(48):
            k = i / 47.0
            small.set_at((0, i), (int(8 + 20 * k), int(10 + 26 * k), int(40 + 46 * k)))
        _CUT_BG = pygame.transform.smoothscale(small, (WIDTH, HEIGHT))
    return _CUT_BG


def _cut_sky(screen, t):
    screen.blit(_cut_bg(), (0, 0))
    for sx, sy, ph in CUTSCENE_STARS:
        tw = 0.55 + 0.45 * math.sin(t * 2.2 + ph * 12)
        c = int(150 + 100 * tw)
        pygame.draw.circle(screen, (c, c, min(255, c + 20)),
                           (int(sx * WIDTH), int(sy * HEIGHT * 0.55)), 2)


def _cut_mountain(screen, base_y, peak_y, half_w, body, snow):
    cx = WIDTH // 2
    h = max(1, base_y - peak_y)
    pygame.draw.polygon(screen, body, [(cx - half_w, base_y), (cx, peak_y), (cx + half_w, base_y)])
    # Right half slightly brighter
    pygame.draw.polygon(screen, (min(255, body[0] + 12), min(255, body[1] + 14),
                                 min(255, body[2] + 20)),
                        [(cx, peak_y), (cx + half_w, base_y), (cx, base_y)])
    # Snow cap: white triangle with jagged bottom
    cap_h = h * 0.26
    cap_w = half_w * 0.24
    pts = [(cx, peak_y)]
    n = 7
    for k in range(1, n + 1):
        t = k / n
        pts.append((cx + cap_w * t, peak_y + cap_h * t + (5 if k % 2 else 0)))
    for k in range(n, -1, -1):
        t = k / n
        pts.append((cx - cap_w * t, peak_y + cap_h * t + (5 if k % 2 else 0)))
    pygame.draw.polygon(screen, snow, pts)


def _cut_santa(screen, cx, cy, s, t):
    cy += math.sin(t * 3.0) * 3 * s
    pygame.draw.circle(screen, (110, 74, 42), (int(cx - 30 * s), int(cy + 12 * s)), int(15 * s))
    pygame.draw.circle(screen, (150, 105, 60), (int(cx - 30 * s), int(cy + 8 * s)), int(8 * s))
    pygame.draw.rect(screen, (196, 30, 44), (int(cx - 15 * s), int(cy - 8 * s),
                                             int(30 * s), int(32 * s)), border_radius=int(9 * s))
    pygame.draw.circle(screen, (244, 198, 168), (int(cx), int(cy - 18 * s)), int(12 * s))
    pygame.draw.circle(screen, (250, 250, 250), (int(cx), int(cy - 11 * s)), int(9 * s))
    pygame.draw.polygon(screen, (212, 30, 44), [
        (cx - 12 * s, cy - 26 * s), (cx + 12 * s, cy - 26 * s), (cx + 4 * s, cy - 42 * s)])
    pygame.draw.circle(screen, (255, 255, 255), (int(cx + 4 * s), int(cy - 42 * s)), int(4 * s))


def draw_cutscene(screen):
    t = cutscene_t
    intro = cutscene_kind == "intro"
    _cut_sky(screen, t)
    _cut_mountain(screen, int(HEIGHT * 0.94), int(HEIGHT * 0.28), int(WIDTH * 0.64),
                  (30, 36, 78), (226, 232, 246))
    _cut_mountain(screen, int(HEIGHT * 0.99), int(HEIGHT * 0.47), int(WIDTH * 0.46),
                  (20, 26, 60), (206, 214, 236))
    pygame.draw.rect(screen, (222, 228, 240), (0, int(HEIGHT * 0.93), WIDTH, HEIGHT))
    if intro:
        prog = min(1.0, t / max(0.1, cutscene_len - 1.0))
        sx = WIDTH * (0.34 + 0.32 * prog)
        sy = HEIGHT * (0.88 - 0.40 * prog)
        _cut_santa(screen, sx, sy, 1.7, t)
    else:
        cx, cy = WIDTH // 2, int(HEIGHT * 0.62)
        pygame.draw.rect(screen, (120, 82, 52), (cx - 70, cy - 40, 140, 90))
        pygame.draw.polygon(screen, (200, 60, 60),
                            [(cx - 90, cy - 40), (cx, cy - 104), (cx + 90, cy - 40)])
        pygame.draw.rect(screen, (255, 226, 140), (cx - 20, cy - 20, 40, 40))
        _cut_santa(screen, cx + 120, cy + 44, 1.7, t)
        gifts = [((cx - 150, cy + 34), (60, 180, 120)), ((cx - 190, cy + 24), (200, 70, 70)),
                 ((cx - 110, cy + 44), (80, 120, 220))]
        for i, ((gx, gy), col) in enumerate(gifts):
            if t > 1.2 + i * 0.8:
                pygame.draw.rect(screen, col, (gx, gy, 36, 30))
                pygame.draw.rect(screen, (240, 220, 120), (gx + 14, gy, 8, 30))
        for k in range(18):
            ang = k * 0.7 + t * 1.2
            rr = 120 + 60 * math.sin(t * 2 + k)
            px = WIDTH // 2 + math.cos(ang) * rr * 1.7
            py = HEIGHT * 0.30 + math.sin(ang) * rr * 0.7
            c = (255, int(180 + 60 * math.sin(t * 3 + k)), 120)
            pygame.draw.circle(screen, c, (int(px), int(py)), 3)
    keys = (("intro_line1", "intro_line2", "intro_line3") if intro
            else ("win_line1", "win_line2", "win_line3"))
    for i, key in enumerate(keys):
        start = 0.5 + i * 1.5
        if t < start:
            continue
        alpha = min(1.0, (t - start) / 0.7)
        if cutscene_len - t < 0.7:
            alpha *= max(0.0, (cutscene_len - t) / 0.7)
        surf = font.render(i18n.ui(key), True, (255, 255, 255))
        surf.set_alpha(int(255 * alpha))
        screen.blit(surf, surf.get_rect(
            center=(WIDTH // 2, int(HEIGHT * 0.12) + i * int(60 * i18n.scale()))))
    # Skip button (top right)
    btn = cutscene_skip_rect()
    hover = btn.collidepoint(pygame.mouse.get_pos())
    pygame.draw.rect(screen, (238, 244, 255) if hover else (196, 210, 240),
                     btn, border_radius=12)
    pygame.draw.rect(screen, (40, 48, 90), btn, 2, border_radius=12)
    label = font.render(i18n.ui("skip"), True, (20, 26, 50))
    screen.blit(label, label.get_rect(center=btn.center))

    hint = small_font.render(i18n.ui("cutscene_skip"), True, (200, 206, 230))
    hint.set_alpha(int(150 + 70 * math.sin(t * 3)))
    screen.blit(hint, hint.get_rect(center=(WIDTH // 2, HEIGHT - 60)))


def cutscene_skip_rect():
    w, h = 190, 54
    return pygame.Rect(WIDTH - w - 30, 28, w, h)


def summit_solid_rect():
    """Solid rect of the backdrop summit platform (candy collision)."""
    feet = ground_level - (player_y + player_height)
    x0, x1, top_h, _house, anchored = backdrop_layer.summit_geometry(
        camera_x, camera_y, feet)
    if not anchored:
        return None
    top_px = ground_level - top_h
    return pygame.Rect(int(x0), int(top_px), max(1, int(x1 - x0)), 4000)


def apply_summit():
    """Once the backdrop is big enough, the peak is a platform (no extra GameObject)."""
    global player_x, player_y, player_velocity_x, player_velocity_y
    global player_is_on_ground, level_cleared, summit_locked
    global summit_msg_timer, summit_msg_shown
    feet = ground_level - (player_y + player_height)
    achievements.update_height(feet)
    if not summit_msg_shown and feet >= SUMMIT_MSG_HEIGHT:
        summit_msg_shown = True
        summit_msg_timer = SUMMIT_MSG_TIME
    x0, x1, top_h, house_rect, anchored = backdrop_layer.summit_geometry(
        camera_x, camera_y, feet)
    if anchored:
        top_px = ground_level - top_h
        over_plateau = (player_x + player_width > x0) and (player_x < x1)
        if over_plateau and (top_h - 160) <= feet <= (top_h + 8) and player_velocity_y >= 0:
            player_y = top_px - player_height
            player_velocity_y = 0
            player_is_on_ground = True
            summit_locked = True
        if summit_locked:
            # One-way air wall: can enter but not leave
            if player_x < x0 + 2:
                player_x = x0 + 2
                if player_velocity_x < 0:
                    player_velocity_x = 0
            elif player_x + player_width > x1 - 2:
                player_x = x1 - 2 - player_width
                if player_velocity_x > 0:
                    player_velocity_x = 0
    if not level_cleared:
        player_rect = pygame.Rect(int(player_x), int(player_y),
                                  player_width, player_height)
        if house_rect.colliderect(player_rect):
            achievements.add_clear()
            SaveManager.delete_slot(current_slot)   # delete this save after clearing
            start_cutscene("win")


def run_game():
    pygame.mouse.set_visible(False)
    
    global current_state, player_x, player_y, camera_x, camera_y, sound_volume, music_volume
    global level_cleared, summit_msg_timer, current_slot
    global player_entry_time
    
    last_time = pygame.time.get_ticks()
    just_entered_game = False
    
    # Create sliders (persistent)
    slider_width, slider_height = 400, 10
    slider_x = WIDTH // 2 - slider_width // 2
    
    sound_slider = Slider(slider_x, HEIGHT // 2 - 50, slider_width, slider_height, 0, 1, sound_volume, "sound")
    music_slider = Slider(slider_x, HEIGHT // 2 + 30, slider_width, slider_height, 0, 1, music_volume, "music")
    
    # Currently selected slider (None = none)
    selected_slider = None
    
    # Start background music
    sound_manager.play_bgm()
    
    running = True
    while running:
        current_time = pygame.time.get_ticks()
        dt = (current_time - last_time) / 1000.0
        dt = min(dt, 0.05)
        last_time = current_time
        
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()
        
        # Update repeat adjustment
        if current_state == GameState.SETTINGS:
            sound_changed = sound_slider.update_repeat(dt)
            music_changed = music_slider.update_repeat(dt)
            
            if sound_changed:
                sound_volume = sound_slider.value
                sound_manager.set_sound_volume(sound_volume)
            if music_changed:
                music_volume = music_slider.value
                sound_manager.set_music_volume(music_volume)
        
        for event in pygame.event.get():
            flavor.handle_event(event)  # FLAVOR
            if event.type == pygame.MOUSEBUTTONDOWN and getattr(event, "button", 0) == 1 \
                    and current_state == GameState.SETTINGS:  # I18N
                for _code, _name, _rect in language_button_rects():
                    if _rect.collidepoint(event.pos):
                        if _code != i18n.current:
                            i18n.set_lang(_code)
                            rebuild_fonts()
                            refresh_texts()
                            SaveManager.save_settings(sound_volume, music_volume)
                        break
            if event.type == pygame.QUIT:
                running = False
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if current_state == GameState.CUTSCENE:
                        end_cutscene()
                    elif current_state == GameState.MENU:
                        for key, rect in menu_buttons():
                            if not rect.collidepoint(event.pos):
                                continue
                            if key == "continue":
                                if SaveManager.save_exists():
                                    load_slot_into_game(SaveManager.latest_slot())
                                    current_state = GameState.PLAYING
                                    just_entered_game = True
                                    player_entry_time = pygame.time.get_ticks() / 1000.0
                            elif key == "new_game":
                                slot = first_empty_slot()
                                if slot is not None:
                                    current_slot = slot
                                    reset_game()
                                    SaveManager.save_slot(current_slot, player_x, player_y)
                                    start_cutscene("intro")
                                    just_entered_game = True
                                    player_entry_time = pygame.time.get_ticks() / 1000.0
                            elif key == "saves":
                                current_state = GameState.SAVES
                            elif key == "achievements":
                                current_state = GameState.ACHIEVEMENTS
                            elif key == "settings":
                                current_state = GameState.SETTINGS
                                selected_slider = None
                                sound_slider.deselect()
                                music_slider.deselect()
                            elif key == "exit":
                                running = False
                            break

                    elif current_state == GameState.SAVES:
                        if saves_back_rect().collidepoint(event.pos):
                            current_state = GameState.MENU
                        else:
                            for slot, load_rect, del_rect in saves_slot_rects():
                                if del_rect.collidepoint(event.pos):
                                    SaveManager.delete_slot(slot)
                                    break
                                if load_rect.collidepoint(event.pos):
                                    made_new = False
                                    if SaveManager.slot_exists(slot):
                                        load_slot_into_game(slot)
                                    else:
                                        current_slot = slot
                                        reset_game()
                                        SaveManager.save_slot(current_slot, player_x, player_y)
                                        made_new = True
                                    if made_new:
                                        start_cutscene("intro")
                                    else:
                                        current_state = GameState.PLAYING
                                    just_entered_game = True
                                    player_entry_time = pygame.time.get_ticks() / 1000.0
                                    break

                    elif current_state == GameState.ACHIEVEMENTS:
                        if saves_back_rect().collidepoint(event.pos):
                            current_state = GameState.MENU

                    elif current_state == GameState.PLAYING:
                        back_rect = victory_button_rect()
                        return_button_rect = pygame.Rect(20, 20, 150, 50)
                        if level_cleared and back_rect.collidepoint(event.pos):
                            current_state = GameState.MENU
                        elif return_button_rect.collidepoint(event.pos):
                            if not level_cleared:
                                SaveManager.save_slot(current_slot, player_x, player_y)
                            current_state = GameState.MENU
                    
                    elif current_state == GameState.SETTINGS:
                        # Slider selected before the click
                        click_on_slider = False
                        result = None
                        
                        # Sound-effect slider
                        sound_result = sound_slider.handle_event(event)
                        # Music slider
                        music_result = music_slider.handle_event(event)
                        
                        # Check slider area clicks
                        sound_clicked = (sound_slider.rect.collidepoint(event.pos) or 
                                        sound_slider.minus_button.collidepoint(event.pos) or 
                                        sound_slider.plus_button.collidepoint(event.pos))
                        music_clicked = (music_slider.rect.collidepoint(event.pos) or 
                                        music_slider.minus_button.collidepoint(event.pos) or 
                                        music_slider.plus_button.collidepoint(event.pos))
                        
                        # Selection logic
                        if sound_clicked:
                            # Click on sound-effect slider
                            if selected_slider != sound_slider:
                                # Deselect previous
                                if selected_slider:
                                    selected_slider.deselect()
                                # Select this slider
                                selected_slider = sound_slider
                                selected_slider.select()
                            click_on_slider = True
                        elif music_clicked:
                            # Click on music slider
                            if selected_slider != music_slider:
                                # Deselect previous
                                if selected_slider:
                                    selected_slider.deselect()
                                # Select this slider
                                selected_slider = music_slider
                                selected_slider.select()
                            click_on_slider = True
                        else:
                            # Click empty space: deselect all
                            if selected_slider:
                                selected_slider.deselect()
                                selected_slider = None
                        
                        # Handle value change
                        if sound_result == "value_changed" or sound_result == "selected_and_changed":
                            sound_volume = sound_slider.value
                            sound_manager.set_sound_volume(sound_volume)
                        if music_result == "value_changed" or music_result == "selected_and_changed":
                            music_volume = music_slider.value
                            sound_manager.set_music_volume(music_volume)
                        
                        # Check the back button
                        return_rect = pygame.Rect(WIDTH // 2 - 150, HEIGHT - 150, 300, 60)
                        if return_rect.collidepoint(event.pos):
                            SaveManager.save_settings(sound_volume, music_volume)
                            current_state = GameState.MENU
                            # Clear selection when leaving settings
                            if selected_slider:
                                selected_slider.deselect()
                                selected_slider = None
            
            elif event.type == pygame.MOUSEMOTION:
                if current_state == GameState.SETTINGS:
                    # Handle slider drag
                    sound_result = sound_slider.handle_event(event)
                    music_result = music_slider.handle_event(event)
                    
                    if sound_result == "value_changed":
                        sound_volume = sound_slider.value
                        sound_manager.set_sound_volume(sound_volume)
                    if music_result == "value_changed":
                        music_volume = music_slider.value
                        sound_manager.set_music_volume(music_volume)
            
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1 and current_state == GameState.SETTINGS:
                    # Handle slider release
                    sound_result = sound_slider.handle_event(event)
                    music_result = music_slider.handle_event(event)
                    
                    if sound_result == "value_changed":
                        sound_volume = sound_slider.value
                        sound_manager.set_sound_volume(sound_volume)
                    if music_result == "value_changed":
                        music_volume = music_slider.value
                        sound_manager.set_music_volume(music_volume)
                elif event.button == 1 and current_state == GameState.PLAYING:
                    just_entered_game = False
            
            elif event.type == pygame.KEYDOWN:
                if current_state == GameState.SETTINGS:
                    # Only the selected slider reacts to the keyboard
                    if selected_slider:
                        sound_changed = False
                        music_changed = False
                        
                        if selected_slider == sound_slider:
                            sound_changed = sound_slider.handle_keyboard(event.key, is_pressed=True)
                        elif selected_slider == music_slider:
                            music_changed = music_slider.handle_keyboard(event.key, is_pressed=True)
                        
                        if sound_changed:
                            sound_volume = sound_slider.value
                            sound_manager.set_sound_volume(sound_volume)
                        if music_changed:
                            music_volume = music_slider.value
                            sound_manager.set_music_volume(music_volume)
                    
                    # Optional: number keys adjust quickly (selection unchanged)
                    if event.key == pygame.K_0:
                        if selected_slider:
                            selected_slider.value = 0
                            selected_slider.update_handle_position()
                            if selected_slider == sound_slider:
                                sound_volume = 0
                                sound_manager.set_sound_volume(0)
                            else:
                                music_volume = 0
                                sound_manager.set_music_volume(0)
                    elif event.key == pygame.K_9:
                        if selected_slider:
                            selected_slider.value = 0.5
                            selected_slider.update_handle_position()
                            if selected_slider == sound_slider:
                                sound_volume = 0.5
                                sound_manager.set_sound_volume(0.5)
                            else:
                                music_volume = 0.5
                                sound_manager.set_music_volume(0.5)
                    elif event.key == pygame.K_8:
                        if selected_slider:
                            selected_slider.value = 1
                            selected_slider.update_handle_position()
                            if selected_slider == sound_slider:
                                sound_volume = 1
                                sound_manager.set_sound_volume(1)
                            else:
                                music_volume = 1
                                sound_manager.set_music_volume(1)
                
                elif current_state == GameState.CUTSCENE:
                    if event.key in (pygame.K_ESCAPE, pygame.K_SPACE,
                                     pygame.K_RETURN, pygame.K_KP_ENTER):
                        end_cutscene()

                elif current_state == GameState.MENU:
                    # Menu keyboard navigation
                    if event.key == pygame.K_RETURN:
                        save_data = SaveManager.load_game()
                        if save_data:
                            player_x = save_data["player_x"]
                            player_y = save_data["player_y"]
                            camera_x = player_x - WIDTH // 2
                            camera_y = player_y - HEIGHT // 2
                        else:
                            reset_game()
                        current_state = GameState.PLAYING
                        just_entered_game = True
                        player_entry_time = pygame.time.get_ticks() / 1000.0
                    elif event.key == pygame.K_ESCAPE:
                        running = False
                
                elif current_state == GameState.PLAYING:
                    # In-game shortcuts
                    if event.key == pygame.K_ESCAPE:
                        if not level_cleared:
                            SaveManager.save_slot(current_slot, player_x, player_y)
                        current_state = GameState.MENU
            
            elif event.type == pygame.KEYUP:
                if current_state == GameState.SETTINGS:
                    # Key released: stop repeat adjustment
                    if selected_slider:
                        selected_slider.handle_keyboard_release(event.key)
        
        screen.fill(SKY_BLUE)
        if current_state == GameState.PLAYING:  # BACKDROP
            backdrop_layer.draw(screen, camera_x, camera_y,
                                ground_level - (player_y + player_height))
        
        # Draw snow first (bottom layer)
        snow_system.update(dt)
        snow_system.draw(screen)
        
        if current_state == GameState.PLAYING:
            global mouse_button_down
            player_textures.update(dt, player_is_on_ground, player_facing_right)
            
            for obj in game:
                obj.update(dt)
            
            update_candies(dt)
            update_explosions(dt)
            update_screen_shake(dt)
            
            keys = pygame.key.get_pressed()
            
            current_time_sec = pygame.time.get_ticks() / 1000.0
            if (current_time_sec - player_entry_time) >= ENTRY_PROTECTION_TIME:
                just_entered_game = False
            
            update_player(keys, dt, mouse_pos)
            flavor.update(dt)  # FLAVOR
            summit_msg_timer = max(0.0, summit_msg_timer - dt)  # summit message
            # Random chatter
            global chatter_timer, chatter_text, chatter_life, chatter_last
            if chatter_life > 0:
                chatter_life = max(0.0, chatter_life - dt)
            else:
                chatter_timer -= dt
                if chatter_timer <= 0:
                    chatter_text = chatter.pick(i18n.current, chatter_last)
                    chatter_last = chatter_text
                    chatter_life = CHATTER_TIME
                    chatter_timer = random.uniform(CHATTER_MIN, CHATTER_MAX)
  # Summit platform comes from the backdrop
            
            if just_entered_game:
                mouse_button_down = False
            
            update_camera(dt)
            apply_summit()  # summit platform comes from the backdrop
            
            draw_game_objects_with_textures(screen)
            draw_candies(screen)
            draw_explosions(screen)
            draw_player(screen, mouse_pos)
            
            is_ready = can_throw and not just_entered_game
            draw_hand(screen, mouse_pos, is_ready)
            flavor.draw(screen)  # FLAVOR
            
            # Exit button
            return_button_rect = pygame.Rect(20, 20, 150, 50)
            return_hovered = return_button_rect.collidepoint(mouse_pos)
            return_color = DARK_GRAY if return_hovered else GRAY
            pygame.draw.rect(screen, return_color, return_button_rect)
            pygame.draw.rect(screen, BLACK, return_button_rect, 2)
            return_surface = small_font.render(i18n.ui("exit").upper(), True, BLACK)
            return_rect_text = return_surface.get_rect(center=return_button_rect.center)
            screen.blit(return_surface, return_rect_text)
            
            # Show entry protection timer
            if just_entered_game:
                protection_time_left = max(0, ENTRY_PROTECTION_TIME - (current_time_sec - player_entry_time))
                if protection_time_left > 0:
                    tip_text = small_font.render(f"Protection: {protection_time_left:.1f}s", True, YELLOW)
                    tip_rect = tip_text.get_rect(center=(WIDTH // 2, 50))
                    screen.blit(tip_text, tip_rect)
            
            draw_custom_cursor(screen, mouse_pos, is_ready)
            draw_summit_msg(screen)  # summit message
            draw_summit_hint(screen)  # summit hint + text arrow
            if level_cleared:
                draw_victory(screen)   # old black victory screen (after the cutscene)
            draw_chatter(screen)  # random chatter
            

        elif current_state == GameState.CUTSCENE:
            update_cutscene(dt)
            draw_cutscene(screen)

        elif current_state == GameState.MENU:
            for key, rect in draw_menu():
                hovered = rect.collidepoint(mouse_pos)
                enabled = True
                if key == "continue":
                    label = i18n.ui("continue")
                    enabled = SaveManager.save_exists()
                elif key == "new_game":
                    label = i18n.ui("new_game")
                    enabled = any_empty_slot()
                else:
                    label = i18n.ui(key)
                if not enabled:
                    color = GRAY
                    text_color = DARK_GRAY
                else:
                    color = WHITE if hovered else LIGHT_BLUE
                    text_color = BLACK
                pygame.draw.rect(screen, color, rect)
                pygame.draw.rect(screen, BLACK, rect, 2)
                surface = font.render(label, True, text_color)
                screen.blit(surface, surface.get_rect(center=rect.center))
            draw_custom_cursor(screen, mouse_pos, True)

        elif current_state == GameState.SAVES:
            title_text = big_font.render(i18n.ui("saves"), True, WHITE)
            screen.blit(title_text, title_text.get_rect(center=(WIDTH // 2, HEIGHT // 4)))
            for slot, load_rect, del_rect in saves_slot_rects():
                data = SaveManager.load_slot(slot)
                hovered = load_rect.collidepoint(mouse_pos)
                color = GRAY if not data else (WHITE if hovered else LIGHT_BLUE)
                pygame.draw.rect(screen, color, load_rect)
                pygame.draw.rect(screen, BLACK, load_rect, 2)
                if data:
                    label = "%s %d  ·  %s %d m" % (i18n.ui("slot"), slot,
                                                   i18n.ui("height"),
                                                   data.get("height", 0) // 100)
                else:
                    label = "%s %d  ·  %s" % (i18n.ui("slot"), slot, i18n.ui("empty"))
                surface = font.render(label, True, BLACK if data else DARK_GRAY)
                screen.blit(surface, surface.get_rect(center=load_rect.center))
                del_color = GRAY if data else DARK_GRAY
                pygame.draw.rect(screen, del_color, del_rect)
                pygame.draw.rect(screen, BLACK, del_rect, 2)
                xs = font.render("X", True, WHITE if data else DARK_GRAY)
                screen.blit(xs, xs.get_rect(center=del_rect.center))
            back = saves_back_rect()
            hovered = back.collidepoint(mouse_pos)
            pygame.draw.rect(screen, WHITE if hovered else LIGHT_BLUE, back)
            pygame.draw.rect(screen, BLACK, back, 2)
            surface = font.render(i18n.ui("back"), True, BLACK)
            screen.blit(surface, surface.get_rect(center=back.center))
            draw_custom_cursor(screen, mouse_pos, True)

        elif current_state == GameState.ACHIEVEMENTS:
            title_text = big_font.render(i18n.ui("achievements"), True, WHITE)
            screen.blit(title_text, title_text.get_rect(center=(WIDTH // 2, HEIGHT // 6)))
            rows = achievements.get_list(i18n.current)
            y = HEIGHT // 6 + 110
            for row in rows:
                unlocked = row["unlocked"]
                mark = "[x]" if unlocked else "[ ]"
                line = "%s  %s · Lv.%d/%d  %s" % (
                    mark, row["name"], row["level"], row["max_level"], row["tier_name"])
                surface = font.render(line, True,
                                      (255, 226, 130) if unlocked else (150, 152, 170))
                screen.blit(surface, (WIDTH // 2 - 430, y))
                surface2 = small_font.render(row["desc"], True,
                                             (210, 216, 232) if unlocked else (120, 122, 140))
                screen.blit(surface2, (WIDTH // 2 - 380, y + 42))
                y += 100
            back = saves_back_rect()
            hovered = back.collidepoint(mouse_pos)
            pygame.draw.rect(screen, WHITE if hovered else LIGHT_BLUE, back)
            pygame.draw.rect(screen, BLACK, back, 2)
            surface = font.render(i18n.ui("back"), True, BLACK)
            screen.blit(surface, surface.get_rect(center=back.center))
            draw_custom_cursor(screen, mouse_pos, True)

        elif current_state == GameState.SETTINGS:
            
            title_text = big_font.render(i18n.ui("settings"), True, WHITE)
            title_rect = title_text.get_rect(center=(WIDTH // 2, HEIGHT // 4))
            screen.blit(title_text, title_rect)
            
            # Update slider values and draw
            sound_slider.value = sound_volume
            sound_slider.update_handle_position()
            music_slider.value = music_volume
            music_slider.update_handle_position()
            
            sound_slider.draw(screen)
            music_slider.draw(screen)

            # Language selection
            lang_title = small_font.render(i18n.ui("language"), True, WHITE)
            screen.blit(lang_title, lang_title.get_rect(
                center=(WIDTH // 2, language_layout_top() - 24)))
            for code, name, rect in language_button_rects():
                selected = (code == i18n.current)
                hovered = rect.collidepoint(mouse_pos)
                if selected:
                    color = YELLOW
                elif hovered:
                    color = WHITE
                else:
                    color = LIGHT_BLUE
                pygame.draw.rect(screen, color, rect)
                pygame.draw.rect(screen, BLACK, rect, 2)
                name_surface = i18n.font_for(code, max(14, rect.height - 14)).render(name, True, BLACK)
                screen.blit(name_surface, name_surface.get_rect(center=rect.center))
            
            # Back button
            return_rect = pygame.Rect(WIDTH // 2 - 150, HEIGHT - 150, 300, 60)
            return_hovered = return_rect.collidepoint(mouse_pos)
            return_color = WHITE if return_hovered else LIGHT_BLUE
            pygame.draw.rect(screen, return_color, return_rect)
            pygame.draw.rect(screen, BLACK, return_rect, 2)
            return_surface = font.render(i18n.ui("return"), True, BLACK)
            return_rect_text = return_surface.get_rect(center=return_rect.center)
            screen.blit(return_surface, return_rect_text)
            
            draw_custom_cursor(screen, mouse_pos, True)
        
        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    import flavor                 # FLAVOR
    flavor.attach(globals())      # FLAVOR
    run_game()
