import pygame
from states.state import State
from states.options import Options
from states.main import Main
from states.main import Button, ButtonGroup

class PauseMenu(State):
    def __init__(self, game):
        self.game = game
        State.__init__(self, game)
        self.state = 'Pause'
        self.prev_rendered = None

        self.input_cooldown = 0
        self.input_delay_frames = 5

        self.title_font = self.game.Assets.get("fugaz")
        self.button_font = self.game.Assets.get("turret")
        self.paused_text = self.title_font.render("Paused", True, (255, 0, 0))

        self.blink_timer = 0
        self.blink_interval = 30
        self.text_visible = True

        self.button_group = ButtonGroup()
        self.create_buttons()

        pygame.mixer.music.load(self.game.Assets.get('fetus'))
        pygame.mixer.music.play(-1)

    def create_buttons(self):
        button_width = int(300 * self.scale_factor)
        button_height = int(60 * self.scale_factor)
        vertical_spacing = int(40 * self.scale_factor)

        total_height = 3 * button_height + 2 * vertical_spacing + self.paused_text.get_height()
        start_y = (self.game.SCREEN_HEIGHT - total_height) // 2

        self.text_center = (self.game.SCREEN_WIDTH // 2, start_y)

        base_y = start_y + self.paused_text.get_height() + vertical_spacing
        center_x = self.game.SCREEN_WIDTH // 2

        self.button_group.add_button(Button(text="Resume", x=center_x, y=base_y, width=button_width, height=button_height, font=self.button_font, base_color=(60, 60, 60), hover_color=(90, 90, 90), action=self.resume_action, radius=10))
        self.button_group.add_button(Button(text="Options", x=center_x, y=base_y + button_height + vertical_spacing, width=button_width, height=button_height, font=self.button_font, base_color=(60, 60, 60), hover_color=(90, 90, 90), action=self.options_action, radius=10))
        self.button_group.add_button(Button(text="Main Menu", x=center_x, y=base_y + 2*(button_height + vertical_spacing), width=button_width, height=button_height, font=self.button_font, base_color=(60, 60, 60), hover_color=(90, 90, 90), action=self.main_menu_action, radius=10))

    def update(self, actions):
        if self.input_cooldown > 0:
            self.input_cooldown -= 1

        self.blink_timer += 1
        if self.blink_timer >= self.blink_interval:
            self.blink_timer = 0
            self.text_visible = not self.text_visible

        if self.input_cooldown <= 0:
            mouse_pos = tuple(2 * x for x in actions['mouse']['Pos'])
            self.button_group.update(actions, mouse_pos)

            if any([actions["up"], actions["down"], actions["start"]]):
                self.input_cooldown = self.input_delay_frames

        if actions["back"] and self.input_cooldown <= 0:
            self.resume_action()

        self.game.reset_keys()

    def render(self, display):
        # Render background
        if self.prev_rendered:
            display.blit(self.prev_rendered, (0, 0))
        else:
            display.fill((0, 0, 0))

        # Dark overlay
        overlay = pygame.Surface((self.game.SCREEN_WIDTH, self.game.SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.set_alpha(128)
        overlay.fill((50, 50, 50))
        display.blit(overlay, (0, 0))

        # Paused text
        if self.text_visible:
            text_rect = self.paused_text.get_rect(center=self.text_center)
            display.blit(self.paused_text, text_rect)

        # Draw buttons
        self.button_group.draw(display)

    def enter_state(self):
        super().enter_state()
        
        base_surface = pygame.Surface((self.game.GAME_W, self.game.GAME_H))
        self.prev_state.render(base_surface)
        self.prev_rendered = pygame.transform.scale(base_surface, 
            (self.game.SCREEN_WIDTH, self.game.SCREEN_HEIGHT))

    # Trying to resume music from where it left off
    def resume_action(self):
        self.exit_state()
        self.game.reset_keys()
        pygame.mixer.music.stop()
        self.game.play_sfx("unpause")
        pygame.mixer.music.load(self.game.Assets.get('warrior'))
        pygame.mixer.music.play(loops=-1, start=self.game.music_position)
        self.game.music_position_start = pygame.mixer.music.get_pos() / 1000.0

    def options_action(self):
        options_state = Options(self.game)
        options_state.enter_state()
        self.game.reset_keys()

    def main_menu_action(self):
        self.game.state_stack = []
        main_menu = Main(self.game)
        main_menu.enter_state()
        self.game.reset_keys()