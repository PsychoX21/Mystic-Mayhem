from states.state import State
from states.main import Main
import pygame

class Button:
    def __init__(self, text, pos, size, font, bg_color=(80, 80, 80), hover_color=(120, 120, 120), text_color=(255, 255, 255), action=None, scale_factor=1):
        self.text = text
        self.pos = pos
        self.size = size
        self.font = font
        self.bg_color = bg_color
        self.hover_color = hover_color
        self.text_color = text_color
        self.action = action
        self.scale_factor = scale_factor

        self.rect = pygame.Rect(pos, size)
        self.hovered = False

        self.text_surf = self.font.render(self.text, True, self.text_color)
        self.text_rect = self.text_surf.get_rect(center=self.rect.center)

    def draw(self, surface):
        color = self.hover_color if self.hovered else self.bg_color
        pygame.draw.rect(surface, color, self.rect, border_radius=8)
        surface.blit(self.text_surf, self.text_rect)

    def update(self, mouse_pos, mouse_click):
        self.hovered = self.rect.collidepoint(mouse_pos)
        if self.hovered and mouse_click and self.action:
            self.action()

class Leaderboard(State):
    def __init__(self, game):
        super().__init__(game)
        pygame.mixer.music.load(self.game.Assets.get('trigger'))
        pygame.mixer.music.play(-1)
        self.state = 'Leaderboard'
        self.font = self.game.Assets.get("jetbrains")
        self.title_font = self.game.Assets.get("courier")

        self.leaderboard_data = self.load_leaderboard_data()

        self.scroll_offset = 0
        self.scroll_speed = 1
        self.visible_rows = 8
        self.recalculate_max_scroll()

        font = self.game.Assets.get("chakra_sbs")
        self.buttons = [
            Button("Back", (int(self.scale_factor*50), self.game.SCREEN_HEIGHT - int(self.scale_factor*60)), (int(self.scale_factor*120), int(self.scale_factor*40)), font, action=self.back),
            Button("Main Menu", (int(self.scale_factor*200), self.game.SCREEN_HEIGHT - int(self.scale_factor*60)), (int(self.scale_factor*160), int(self.scale_factor*40)), font, action=self.main_menu)
        ]

        self.scroll_cooldown_counter = 0
        self.scroll_cooldown_frames = 5

        self.up_img = self.game.Assets.get("up")
        self.down_img = self.game.Assets.get("down")

    def recalculate_max_scroll(self):
        self.max_scroll = max(0, len(self.leaderboard_data) - self.visible_rows)

    def load_leaderboard_data(self):
        leaderboard = []
        with open("leaderboard.txt", "r") as file:
            lines = file.readlines()[1:]
            for line in lines:
                parts = line.strip().split(",")
                leaderboard.append(parts)
        return leaderboard

    def update(self, actions):
        self.scroll_cooldown_counter += 1

        if (actions['scroll_up'] or actions['up']) and self.scroll_cooldown_counter >= self.scroll_cooldown_frames:
            # Prevent scrolling beyond the top
            self.scroll_offset = max(0, self.scroll_offset - self.scroll_speed)
            self.scroll_cooldown_counter = 0

        if (actions['scroll_down'] or actions['down']) and self.scroll_cooldown_counter >= self.scroll_cooldown_frames:
            # Prevent scrolling beyond the bottom
            self.scroll_offset = min(self.max_scroll, self.scroll_offset + self.scroll_speed)
            self.scroll_cooldown_counter = 0

        actions['scroll_up'] = False
        actions['scroll_down'] = False

        mouse_pos = tuple(2 * x for x in actions['mouse']['Pos'])
        mouse_click = actions['mouse']['Down']

        for button in self.buttons:
            button.update(mouse_pos, mouse_click)

        self.recalculate_max_scroll()
        self.scroll_offset = max(0, min(self.max_scroll, self.scroll_offset))

    def render(self, surface):
        surface.fill((30, 30, 30))

        title = self.title_font.render("Leaderboard", True, (255, 255, 255))
        surface.blit(title, (self.game.SCREEN_WIDTH // 2 - title.get_width() // 2, int(30 * self.scale_factor)))

        headers = ["Rank", "Name", "Wins", "Losses", "Most Chosen", "Best Tower"]
        col_x = [int(100 * self.scale_factor), int(200 * self.scale_factor), int(370 * self.scale_factor), int(450 * self.scale_factor), int(560 * self.scale_factor), int(730 * self.scale_factor)]
        for i, header in enumerate(headers):
            header_text = self.font.render(header, True, (200, 200, 0))
            surface.blit(header_text, (col_x[i], int(120 * self.scale_factor)))

        y_offset = int(160 * self.scale_factor) 
        for idx in range(self.scroll_offset, min(self.scroll_offset + self.visible_rows, len(self.leaderboard_data))):
            player = self.leaderboard_data[idx]
            values = [player[5], player[0], player[1], player[2], player[3], player[4]]
            for i, val in enumerate(values):
                cell_text = self.font.render(val, True, (255, 255, 255))
                surface.blit(cell_text, (col_x[i], y_offset))
            y_offset += int(40 * self.scale_factor)

        if self.scroll_offset > 0:
            surface.blit(self.up_img, (int(880 * self.scale_factor), int(110 * self.scale_factor)))
        if self.scroll_offset < self.max_scroll:
            surface.blit(self.down_img, (int(880 * self.scale_factor), int(460 * self.scale_factor)))

        for button in self.buttons:
            button.draw(surface)

    def back(self):
        self.game.screen.fill((0, 0, 0))
        pygame.display.flip()
        self.game.reset_keys()
        self.exit_state()
        if self.game.state_stack[-1].state == "Main":
            pygame.mixer.music.load(self.game.Assets.get('reloaded'))
            pygame.mixer.music.play(-1)

    def main_menu(self):
        self.game.reset_keys()
        self.exit_state()
        new_state = Main(self.game)
        new_state.enter_state()
        pygame.mixer.music.load(self.game.Assets.get('reloaded'))
        pygame.mixer.music.play(-1)