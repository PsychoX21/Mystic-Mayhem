import pygame
import os
from states.state import State

class Options(State):
    def __init__(self, game):
        super().__init__(game)
        self.state = 'Options'
        self.options = self.load_options()

        self.font = self.game.Assets.get("grotesk")

        self.labels = ["Master Volume", "Music Volume", "SFX Volume", "Show Tutorial", "Resolution"]
        self.keys = ["master_volume", "music_volume", "sfx_volume", "tutorial", "resolution"]

        self.resolutions = ["960x540", "1280x720", "1440x810", "1600x900", "1920x1080"]

        self.selection = 0
        self.show_restart_dialog = False
        self.game.reset_keys()

        self.input_timer = 0
        self.input_cooldown = 5

    @classmethod
    def load_options(self):
        default_options = {
            "master_volume": "1.0",
            "music_volume": "1.0",
            "sfx_volume": "1.0",
            "tutorial": "Press Right to View",
            "resolution": "1600x900"
        }

        if not os.path.exists("options.txt"):
            return default_options

        with open("options.txt", "r") as f:
            lines = f.readlines()
        for line in lines:
            if '=' in line:
                k, v = line.strip().split('=')
                default_options[k] = v
        return default_options

    def save_options(self):
        with open("options.txt", "w") as f:
            for k, v in self.options.items():
                f.write(f"{k}={v}\n")

    def apply_settings(self):
        master_volume = float(self.options["master_volume"])
        sfx_volume = float(self.options["sfx_volume"])
        music_volume = float(self.options["music_volume"])
        pygame.mixer.music.set_volume(float(music_volume * master_volume))
        self.game.sfx_volume = sfx_volume

    def update(self, actions):
        self.input_timer += 1

        if self.input_timer >= self.input_cooldown:
            if actions["down"]:
                self.selection = (self.selection + 1) % len(self.labels)
                self.input_timer = 0
            elif actions["up"]:
                self.selection = (self.selection - 1) % len(self.labels)
                self.input_timer = 0

            key = self.keys[self.selection]
            if actions["right"]:
                if key in ["master_volume", "music_volume", "sfx_volume"]:
                    self.options[key] = str(round(min(float(self.options[key]) + 0.1, 1.0), 2))
                    self.apply_settings()
                elif key == "tutorial":
                    from states.tutorial import Tutorial
                    new_state = Tutorial(self.game)
                    new_state.enter_state()
                elif key == "resolution":
                    idx = self.resolutions.index(self.options[key])
                    self.options[key] = self.resolutions[(idx + 1) % len(self.resolutions)]
                    self.show_restart_dialog = True
                self.input_timer = 0

            elif actions["left"]:
                if key in ["master_volume", "music_volume", "sfx_volume"]:
                    self.options[key] = str(round(max(float(self.options[key]) - 0.1, 0.0), 2))
                    self.apply_settings()
                elif key == "resolution":
                    idx = self.resolutions.index(self.options[key])
                    self.options[key] = self.resolutions[(idx - 1) % len(self.resolutions)]
                    self.show_restart_dialog = True
                self.input_timer = 0

            if actions["start"]:
                self.save_options()
                self.game.reset_keys()
                self.exit_state()

    def render(self, surface):
        surface.fill((30, 30, 30))
        y = int(100 * self.scale_factor)

        for i, label in enumerate(self.labels):
            color = (255, 255, 0) if i == self.selection else (255, 255, 255)
            value = self.options[self.keys[i]]
            if self.keys[i] == "tutorial":
                value = "Press Right to View"
            text_surface = self.font.render(f"{label}: {value}", True, color)
            rect = text_surface.get_rect(center=(self.game.SCREEN_WIDTH // 2, y))
            surface.blit(text_surface, rect)
            y += int(40 * self.scale_factor)

        if self.show_restart_dialog:
            self.draw_restart_dialog(surface)

        text_surface = self.font.render("Press START to Save and Exit", True, (255, 255, 255))
        rect = text_surface.get_rect(center=(self.game.SCREEN_WIDTH // 2, y + int(40 * self.scale_factor)))
        surface.blit(text_surface, rect)

    def draw_restart_dialog(self, surface):
        msg = "Resolution change will apply after restart."
        text_surface = self.font.render(msg, True, (255, 255, 255))
        text_rect = text_surface.get_rect()

        padding_x = int(40 * self.scale_factor)
        padding_y = int(20 * self.scale_factor)

        dialog_width = text_rect.width + padding_x * 2
        dialog_height = text_rect.height + padding_y * 2

        dialog_rect = pygame.Rect(
            (self.game.SCREEN_WIDTH - dialog_width) // 2,
            (self.game.SCREEN_HEIGHT * 7 // 8) - (dialog_height // 2),
            dialog_width,
            dialog_height
        )

        pygame.draw.rect(surface, (50, 50, 50), dialog_rect)
        pygame.draw.rect(surface, (255, 255, 0), dialog_rect, 4)

        text_pos = text_surface.get_rect(center=dialog_rect.center)
        surface.blit(text_surface, text_pos)