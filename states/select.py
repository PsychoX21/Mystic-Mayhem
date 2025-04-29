from states.state import State
import pygame
import random
import math

class Select(State):
    def __init__(self, game):
        State.__init__(self, game)
        self.state = 'Select'
        self.name = ""
        self.font = self.game.Assets.get("pixel")
        self.input_focus = "left"
        self.cursor_visible = True
        self.cursor_timer = 0

        self.players = {
            "left": {"name": "", "selected_tower": 3, "confirmed": False},
            "right": {"name": "", "selected_tower": 3, "confirmed": False}
        }

        pygame.key.set_repeat(400, 50)

        self.bg = self.game.Assets.get("selectbg")
        self.tower_images = [self.game.Assets.get("0"), self.game.Assets.get("1"), self.game.Assets.get("2")]

        screen_width = self.game.SCREEN_WIDTH
        base_y = int(340 * self.scale_factor)

        rand_text = self.font.render("RANDOM", True, (0, 0, 0))
        text_padding = int(20 * self.scale_factor)
        random_width = rand_text.get_width() + text_padding * 2
        random_height = rand_text.get_height() + text_padding

        self.tower_templates = [
            pygame.Rect(0, 0, int(120 * self.scale_factor), int(160 * self.scale_factor)),
            pygame.Rect(0, 0, int(120 * self.scale_factor), int(160 * self.scale_factor)),
            pygame.Rect(0, 0, int(120 * self.scale_factor), int(160 * self.scale_factor)),
            pygame.Rect(0, 0, random_width, random_height)
        ]

        self.left_towers = [
            self.tower_templates[0].move(int(20 * self.scale_factor), int(160 * self.scale_factor)),
            self.tower_templates[1].move(int(180 * self.scale_factor), int(160 * self.scale_factor)),
            self.tower_templates[2].move(int(340 * self.scale_factor), int(160 * self.scale_factor)),
            self.tower_templates[3].move(screen_width//4 - random_width//2, base_y)
        ]
        self.right_towers = [
            self.tower_templates[0].move(int(500 * self.scale_factor), int(160 * self.scale_factor)),
            self.tower_templates[1].move(int(660 * self.scale_factor), int(160 * self.scale_factor)),
            self.tower_templates[2].move(int(820 * self.scale_factor), int(160 * self.scale_factor)),
            self.tower_templates[3].move(3*screen_width//4 - random_width//2, base_y)
        ]

        self.ready_buttons = {
            "left": pygame.Rect(int(110 * self.scale_factor), int(440 * self.scale_factor), int(260 * self.scale_factor), int(60 * self.scale_factor)),
            "right": pygame.Rect(int(590 * self.scale_factor), int(440 * self.scale_factor), int(260 * self.scale_factor), int(60 * self.scale_factor))
        }

        self.tower_highlights = []
        for img in self.tower_images:
            highlight = pygame.Surface(img.get_size(), pygame.SRCALPHA)
            highlight.blit(img, (0, 0))
            
            glow = pygame.Surface(img.get_size(), pygame.SRCALPHA)
            glow.fill((100, 200, 255, 10))
            highlight.blit(glow, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
            self.tower_highlights.append(highlight)

        self.countdown_start = None
        self.default_names = {"left": ["Loki", "Lara", "Logan"], "right": ["Robin", "Ryder", "Raven"]}
        self.hovered_element = None
        self.button_states = {"left": "normal", "right": "normal"}
        
        pygame.mixer.music.load(self.game.Assets.get('slugger'))
        pygame.mixer.music.play(-1)

    def check_input(self):
        mx, my = pygame.mouse.get_pos()
        self.hovered_element = None

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.game.playing = False
                self.game.running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.exit_state()
                    pygame.mixer.music.load(self.game.Assets.get('reloaded'))
                    pygame.mixer.music.play(-1)
                elif not self.players[self.input_focus]["confirmed"]:
                    if event.key == pygame.K_BACKSPACE:
                        self.players[self.input_focus]["name"] = self.players[self.input_focus]["name"][:-1]
                    elif event.unicode.isalpha() and len(self.players[self.input_focus]["name"]) < 10:
                        self.players[self.input_focus]["name"] += event.unicode.upper()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if mx < self.game.SCREEN_WIDTH // 2:
                    self.input_focus = "left"
                else:
                    self.input_focus = "right"

                for i, rect in enumerate(self.left_towers):
                    if rect.collidepoint((mx, my)) and not self.players["left"]["confirmed"]:
                        self.players["left"]["selected_tower"] = i
                        self.hovered_element = ("left", i)
                        self.game.play_sfx("select")

                for i, rect in enumerate(self.right_towers):
                    if rect.collidepoint((mx, my)) and not self.players["right"]["confirmed"]:
                        self.players["right"]["selected_tower"] = i
                        self.hovered_element = ("right", i)
                        self.game.play_sfx("select")

                if self.ready_buttons["left"].collidepoint((mx, my)):
                    self.button_states["left"] = "pressed"
                    self.players["left"]["confirmed"] = not self.players["left"]["confirmed"]
                    self.game.play_sfx("ready")
                if self.ready_buttons["right"].collidepoint((mx, my)):
                    self.button_states["right"] = "pressed"
                    self.players["right"]["confirmed"] = not self.players["right"]["confirmed"]
                    self.game.play_sfx("ready")

            elif event.type == pygame.MOUSEBUTTONUP:
                self.button_states["left"] = "normal"
                self.button_states["right"] = "normal"

    def update(self, actions):
        self.check_input()

        mx, my = pygame.mouse.get_pos()
        for side in ["left", "right"]:
            if self.ready_buttons[side].collidepoint((mx, my)):
                self.hovered_element = (side, "ready")

        if self.players["left"]["confirmed"] and self.players["right"]["confirmed"]:
            if self.countdown_start is None:
                self.countdown_start = pygame.time.get_ticks()
            elif pygame.time.get_ticks() - self.countdown_start >= 3000:
                for side in ["left", "right"]:
                    if not self.players[side]["name"]:
                        self.players[side]["name"] = random.choice(self.default_names[side])
                from states.game_world import Game_World
                self.exit_state()
                Game_World(self.game, self.players).enter_state()
        else:
            self.countdown_start = None

    def draw_player_ui(self, display, side, x_offset):
        player = self.players[side]
        is_focused = self.input_focus == side
        mouse_pos = pygame.mouse.get_pos()

        # Name input box with rounded corners
        input_box = pygame.Rect(x_offset + int(100 * self.scale_factor), int(40 * self.scale_factor), 
                            int(280 * self.scale_factor), int(60 * self.scale_factor))
        border_color = (0, 150, 255) if is_focused else (100, 100, 100)
        
        pygame.draw.rect(display, (245, 245, 245), input_box, border_radius=int(8 * self.scale_factor))
        pygame.draw.rect(display, border_color, input_box, int(3 * self.scale_factor), border_radius=int(8 * self.scale_factor))

        name_text = self.font.render(player["name"], True, (40, 40, 40))
        text_x = input_box.centerx - name_text.get_width() // 2
        text_y = input_box.centery - name_text.get_height() // 2
        display.blit(name_text, (text_x, text_y))

        if is_focused and not player["confirmed"] and self.cursor_visible:
            cursor_x = text_x + name_text.get_width()
            pygame.draw.line(display, (0, 0, 0), 
                        (cursor_x, input_box.y + int(12 * self.scale_factor)),
                        (cursor_x, input_box.y + input_box.height - int(12 * self.scale_factor)), 
                        int(3 * self.scale_factor))

        towers = self.left_towers if side == "left" else self.right_towers
        for i, rect in enumerate(towers):
            is_hovered = rect.collidepoint(mouse_pos)
            is_selected = player["selected_tower"] == i
            is_locked = player["confirmed"]

            current_scale = 1.0
            text_color = (255, 165, 0)

            if is_selected:
                pulse = abs(pygame.time.get_ticks() % 500 - 250) / 250
                current_scale = 1.05 + 0.05 * pulse

            if is_hovered and not is_locked:
                current_scale = max(current_scale, 1.1)
                if i >= 3:
                    text_color = (255, 185, 50)

            if i < 3:
                if is_selected:
                    img = self.tower_highlights[i]
                else:
                    img = self.tower_images[i]
                
                if side == "right":
                    img = pygame.transform.flip(img, True, False)
                
                scaled_img = pygame.transform.smoothscale(
                    img, 
                    (int(img.get_width() * current_scale),
                     int(img.get_height() * current_scale)
                ))
                img_rect = scaled_img.get_rect(center=rect.center)
                display.blit(scaled_img, img_rect)

            else:
                text_scale = current_scale
                rand_text = self.font.render("RANDOM", True, text_color)
                text_width = int(rand_text.get_width() * text_scale)
                text_height = int(rand_text.get_height() * text_scale)
                
                bg_rect = pygame.Rect(0, 0, text_width + 20, text_height + 10)
                bg_rect.center = rect.center
                
                if is_selected or is_hovered:
                    pygame.draw.rect(display, (255, 255, 255, 50), bg_rect, 
                                   border_radius=int(8 * self.scale_factor))
                
                scaled_text = pygame.transform.smoothscale(rand_text, (text_width, text_height))
                text_rect = scaled_text.get_rect(center=rect.center)
                display.blit(scaled_text, text_rect)

        button_rect = self.ready_buttons[side]
        button_state = self.button_states[side]
        
        base_color = (76, 175, 80) if player["confirmed"] else (244, 67, 54)
        hover_color = (56, 142, 60) if player["confirmed"] else (194, 54, 44)
        current_color = hover_color if button_rect.collidepoint(mouse_pos) else base_color
        
        if button_state == "pressed":
            button_rect = button_rect.move(0, int(2 * self.scale_factor))
        
        pygame.draw.rect(display, current_color, button_rect, border_radius=int(8 * self.scale_factor))
        pygame.draw.rect(display, (0, 0, 0), button_rect, int(3 * self.scale_factor), border_radius=int(8 * self.scale_factor))
        
        btn_text = "READY!" if player["confirmed"] else "PRESS TO READY"
        text = self.font.render(btn_text, True, (255, 255, 255))
        text_rect = text.get_rect(center=button_rect.center)
        display.blit(text, text_rect)

    def render(self, display):
        display.blit(self.bg, (0, 0))
        pygame.draw.line(display, (0, 0, 0), (self.game.SCREEN_WIDTH // 2, 0), 
                       (self.game.SCREEN_WIDTH // 2, self.game.SCREEN_HEIGHT - int(150 * self.scale_factor)), 
                       int(2 * self.scale_factor))

        self.draw_player_ui(display, "left", 0)
        self.draw_player_ui(display, "right", self.game.SCREEN_WIDTH // 2)

        if self.countdown_start:
            time_left = max(0, 3 - (pygame.time.get_ticks() - self.countdown_start) // 1000)
            countdown_text = self.game.Assets.get("pixel").render(f"STARTING IN {time_left}", True, (255, 80, 80))
            
            bounce_progress = pygame.time.get_ticks() % 1000 / 1000
            y_offset = int(15 * self.scale_factor * abs(math.sin(bounce_progress * math.pi * 2)))
            
            scale = 1.0 + 0.1 * math.sin(bounce_progress * math.pi * 4)
            scaled_text = pygame.transform.smoothscale(
                countdown_text,
                (int(countdown_text.get_width() * scale),
                int(countdown_text.get_height() * scale)
            ))
            
            rect = scaled_text.get_rect(
                centerx=self.game.SCREEN_WIDTH//2,
                centery=self.game.SCREEN_HEIGHT - int(120*self.scale_factor) + y_offset
            )
            display.blit(scaled_text, rect)

        self.cursor_timer = (self.cursor_timer + 1) % 30
        self.cursor_visible = self.cursor_timer < 20