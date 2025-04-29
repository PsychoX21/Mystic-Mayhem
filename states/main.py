from states.state import State
from states.select import Select
from states.credits import Credits
from states.options import Options
import pygame
import random
import math

# Button class for creating buttons with hover effects and actions
class Button:
    def __init__(self, text, x, y, width, height, font, base_color, hover_color, action=None, radius=10):
        self.text = text
        self.center_x = x
        self.center_y = y
        self.width = width
        self.height = height
        self.font = font
        self.base_color = base_color
        self.hover_color = hover_color
        self.action = action
        self.radius = radius

        self.rect = pygame.Rect(self.center_x - width // 2, self.center_y - height // 2, width, height)
        self.selected = False

    def draw(self, surface):
        if self.selected:
            scaled_width = int(self.width * 1.2)
            scaled_height = int(self.height * 1.2)
            draw_color = self.hover_color
            border_color = (255, 255, 255)
            draw_x = self.center_x - scaled_width // 2
            draw_y = self.center_y - scaled_height // 2
            draw_rect = pygame.Rect(draw_x, draw_y, scaled_width, scaled_height)
        else:
            draw_rect = self.rect
            draw_color = self.base_color
            border_color = (0, 0, 0)

        border_rect = pygame.Rect(
            draw_rect.x - 2,
            draw_rect.y - 2,
            draw_rect.width + 4,
            draw_rect.height + 4
        )
        pygame.draw.rect(surface, border_color, border_rect, border_radius=self.radius)
        pygame.draw.rect(surface, draw_color, draw_rect, border_radius=self.radius)

        text_surface = self.font.render(self.text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=draw_rect.center)
        surface.blit(text_surface, text_rect)

    def click(self):
        if self.action:
            self.action()

    def check_hover(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)

# ButtonGroup class to manage multiple buttons and handle input for vertical column of buttons
class ButtonGroup:
    def __init__(self):
        self.buttons = []
        self.selected_index = 0
        self.last_input = "keyboard"  
        self.last_mouse_pos = None

    def add_button(self, button):
        self.buttons.append(button)
        if len(self.buttons) == 1:
            button.selected = True

    def update(self, actions, mouse_pos):
        # Prioritize Keyboard if Arrow keys or Enter pressed else Mouse
        if actions["up"] or actions["down"] or actions["start"]:
            self.last_input = "keyboard"
        elif self.last_mouse_pos is None or mouse_pos != self.last_mouse_pos:
            self.last_input = "mouse"

        self.last_mouse_pos = mouse_pos

        if self.last_input == "keyboard":
            if actions["up"]:
                self.selected_index = (self.selected_index - 1) % len(self.buttons)
            elif actions["down"]:
                self.selected_index = (self.selected_index + 1) % len(self.buttons)
            
            for idx, button in enumerate(self.buttons):
                button.selected = (idx == self.selected_index)

            if actions["start"]:
                self.buttons[self.selected_index].click()

        else:
            for idx, button in enumerate(self.buttons):
                if button.check_hover(mouse_pos):
                    self.selected_index = idx
                    for j, btn in enumerate(self.buttons):
                        btn.selected = (j == idx)
                    break

            if actions["mouse"]["Down"]:
                if self.buttons[self.selected_index].check_hover(mouse_pos):
                    self.buttons[self.selected_index].click()

    def draw(self, surface):
        for button in self.buttons:
            button.draw(surface)

class Particle:
    def __init__(self, x, y, vx, vy, width, height, color, lifetime):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.width = width
        self.height = height
        self.color = color
        self.lifetime = lifetime
        self.age = 0

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.age += 1

    def draw(self, surface):
        if self.age < self.lifetime:
            ellipse_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            pygame.draw.ellipse(ellipse_surface, self.color, (0, 0, self.width, self.height))
            surface.blit(ellipse_surface, (self.x, self.y))

    def is_alive(self):
        return self.age < self.lifetime

class Main(State):
    def __init__(self, game):
        State.__init__(self, game)
        self.state = 'Main'
        self.select = 'Start'
        self.startx, self.starty = self.game.SCREEN_WIDTH/2, self.game.SCREEN_HEIGHT/2 - int(10 * self.game.scale_factor)
        self.optionsx, self.optionsy = self.game.SCREEN_WIDTH/2, self.game.SCREEN_HEIGHT/2 + int(80 * self.game.scale_factor)
        self.creditsx, self.creditsy = self.game.SCREEN_WIDTH/2, self.game.SCREEN_HEIGHT/2 + int(170 * self.game.scale_factor)

        self.title = True
        self.image = self.game.Assets.get('title')
        self.image = pygame.transform.smoothscale(self.image, (self.game.SCREEN_WIDTH, self.game.SCREEN_HEIGHT))
        self.rect = self.image.get_rect(center=(self.game.SCREEN_WIDTH/2, self.game.SCREEN_HEIGHT/2))

        self.mysticimage = self.game.Assets.get('mystic')
        self.mayhemimage = self.game.Assets.get('mayhem')
        self.mysticrect = self.mysticimage.get_rect(center = (int(680 * self.scale_factor), int(150 * self.scale_factor)))
        self.mayhemrect = self.mayhemimage.get_rect(center = (int(775 * self.scale_factor), int(285 * self.scale_factor)))

        self.enterimage = self.game.Assets.get('enter')
        self.enter_timer = 0
        self.enter_origin = (int(910 * self.scale_factor), int(490 * self.scale_factor))
        self.enter_figure8_mode = 'horizontal'
        self.enter_loop_timer = 0

        self.font = self.game.Assets.get('orbitron')

        pygame.mixer.music.load(self.game.Assets.get('reloaded'))
        pygame.mixer.music.play(-1)

        self.dust_particles = []

        # Parallax background layers
        # 1. Static layers
        self.static_layers = [
            self.game.Assets.get('pm1'),
            self.game.Assets.get('pm2'),
        ]

        # 2. Scrolling layers
        self.scroll_layers = [
            {"image": self.game.Assets.get('pm3'), "speed": 3, "offset": 0, "change": 0},
            {"image": self.game.Assets.get('pm4'), "speed": 5, "offset": 0, "change": 0},
            {"image": self.game.Assets.get('pm5'), "speed": 8, "offset": 0, "change": int(32 * self.game.scale_factor)},
        ]

        self.button_group = ButtonGroup()
        self.button_group.add_button(Button("Start Game", self.startx, self.starty, int(300 * self.scale_factor), int(60 * self.scale_factor),self.font, base_color=(255, 107, 107), hover_color=(150, 70, 70), action = self.start_game))
        self.button_group.add_button(Button("Options", self.optionsx, self.optionsy, int(300 * self.scale_factor), int(60 * self.scale_factor), self.font, base_color=(255, 107, 107), hover_color=(150, 70, 70), action = self.open_options))
        self.button_group.add_button(Button("Credits", self.creditsx, self.creditsy, int(300 * self.scale_factor), int(60 * self.scale_factor), self.font, base_color=(255, 107, 107), hover_color=(150, 70, 70), action = self.open_credits))

        self.leaderboard_image = pygame.transform.smoothscale(self.game.Assets.get('leaderboard'), (int(80 * self.scale_factor), int(80 * self.scale_factor)))
        self.leaderboardh_image = pygame.transform.smoothscale(self.game.Assets.get('leaderboardh'), (int(80 * self.scale_factor), int(80 * self.scale_factor)))
        self.leaderboard_rect = self.leaderboard_image.get_rect(center = (self.game.SCREEN_WIDTH - int(60 * self.scale_factor), self.game.SCREEN_HEIGHT - int(60 * self.scale_factor)))
        self.leaderboard_hovered = False

    def start_game(self):
        pygame.mixer.music.stop()
        self.game.play_sfx("start")
        self.game.reset_keys()
        new_state = Select(self.game)
        new_state.enter_state()

    def open_options(self):
        self.game.reset_keys()
        new_state = Options(self.game)
        new_state.enter_state()

    def open_credits(self):
        self.game.reset_keys()
        new_state = Credits(self.game)
        new_state.enter_state()
        pygame.mixer.music.load(self.game.Assets.get('hipshop'))
        pygame.mixer.music.play(-1)

    def spawn_dust_particles(self, num):
        for _ in range(num):
            x = random.randint(0, self.game.SCREEN_WIDTH)
            y = random.randint(int(self.game.SCREEN_HEIGHT * 0.65), self.game.SCREEN_HEIGHT)
            vx = -random.uniform(0.2, 0.5)
            vy = 0
            width = random.randint(3, 6)
            height = random.randint(2, 4)
            alpha = random.randint(60, 100)
            color = (150, 150, 150, alpha)
            lifetime = random.randint(150, 300)
            self.dust_particles.append(Particle(x, y, vx, vy, width, height, color, lifetime))

    def update(self, actions):
        if not self.title:
            mouse_pos = pygame.mouse.get_pos()
            self.button_group.update(actions, mouse_pos)

            if ((mouse_pos[0] - self.leaderboard_rect.centerx)**2 + (mouse_pos[1] - self.leaderboard_rect.centery)**2) < 35*35*self.scale_factor*self.scale_factor:
                self.leaderboard_hovered = True
            else:
                self.leaderboard_hovered = False

            if self.leaderboard_hovered and actions["mouse"]["Down"]:
                from states.leaderboard import Leaderboard
                new_state = Leaderboard(self.game)
                new_state.enter_state()
                self.game.reset_keys()
        else:
            self.enter_timer += 0.05
            self.enter_loop_timer += 0.05

            if self.enter_loop_timer > 2 * math.pi:
                self.enter_loop_timer = 0
                if self.enter_figure8_mode == 'horizontal':
                    self.enter_figure8_mode = 'vertical'
                else:
                    self.enter_figure8_mode = 'horizontal'
            if self.title:
                if actions["start"]:
                    self.game.play_sfx("thunder")
                    self.title = False

        self.game.reset_keys()

    def draw_parallax_background(self, display):
        for img in self.static_layers:
            display.blit(img, (0, 0))

        for layer in self.scroll_layers:
            img = layer["image"]
            speed = layer["speed"]
            offset = layer["offset"]
            change = layer["change"]

            offset -= speed

            if offset <= -img.get_width() // 2:
                offset += img.get_width() // 2 - change

            layer["offset"] = offset
            display.blit(img, (offset, 0))

    def render(self, display):
        display.blit(self.image, self.rect)

        if self.title:
            self.spawn_dust_particles(1)

            if self.enter_figure8_mode == 'horizontal':
                offset_x = math.sin(self.enter_timer) * 10
                offset_y = math.sin(self.enter_timer) * math.cos(self.enter_timer) * 10
            else:
                offset_x = math.sin(self.enter_timer) * math.cos(self.enter_timer) * 10
                offset_y = math.sin(self.enter_timer) * 10

            center_x = self.enter_origin[0] + offset_x
            center_y = self.enter_origin[1] + offset_y

            rect = self.enterimage.get_rect(center=(center_x, center_y))
            display.blit(self.enterimage, rect)

            for particle in self.dust_particles:
                particle.update()
                if particle.is_alive():
                    particle.draw(display)

            self.dust_particles = [p for p in self.dust_particles if p.is_alive()]

            display.blit(self.mysticimage, self.mysticrect)
            display.blit(self.mayhemimage, self.mayhemrect)

        if not self.title:
            self.draw_parallax_background(display)
            self.button_group.draw(display)

            if self.leaderboard_hovered:
                display.blit(self.leaderboardh_image, self.leaderboard_rect)
            else:
                display.blit(self.leaderboard_image, self.leaderboard_rect)

            if self.rect.bottom > 0:
                self.rect.y -= int(30 * self.scale_factor)
                display.blit(self.image, self.rect)