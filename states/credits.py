import pygame
import random
from states.state import State

class Star:
    def __init__(self, width, height, scale_factor):
        self.x = random.randint(0, width)
        self.y = random.randint(0, height)
        self.scale_factor = scale_factor
        self.radius = random.randint(1, 2)
        self.speed = random.uniform(0.1, 0.5)

    def update(self):
        self.y += self.speed
        if self.y > int(600 * self.scale_factor):
            self.y = 0
            self.x = random.randint(0, int(960*self.scale_factor))

    def draw(self, surface):
        pygame.draw.circle(surface, (255, 255, 255), (int(self.x), int(self.y)), self.radius)

class Credits(State):
    def __init__(self, game):
        super().__init__(game)
        self.state = 'Credits'
        self.font = self.game.Assets.get("pressstart")
        self.small_font = self.game.Assets.get("jersey")

        self.credits_lines = [
            "Mystic Mayhem",
            "aka Angry Birds 1v1: Wizard Edition",
            "",
            "",
            "",
            "Lead Developer",
            "- Saksham Khandelwal",
            "",
            "",
            "Game Design",
            "- Saksham Khandelwal",
            "",
            "",
            "Art & Animation Selection",
            "- Saksham Khandelwal",
            "",
            "",
            "Music & Sound Effects Selection",
            "- Saksham Khandelwal",
            "",
            "",
            "",
            "",
            "Special Thanks:",
            "- ChatGPT",
            "- VSCode Autocomplete",
            "",
            "",
            "",
            "",
            "",
            "Thank You for Playing",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "Press ENTER to go back..."
        ]

        self.text_surfaces = [
            self.font.render(line, True, (255, 255, 255)) for line in self.credits_lines
        ]

        self.stars = [Star(game.SCREEN_WIDTH, game.SCREEN_HEIGHT, self.scale_factor) for _ in range(100)]

        self.scroll_y = game.SCREEN_HEIGHT
        self.all_credits_done = False

    def update(self, actions):
        scroll_step = 2

        if not self.all_credits_done:
            self.scroll_y -= scroll_step
            if self.scroll_y < -len(self.text_surfaces) * 30 * self.game.scale_factor + 200*self.game.scale_factor:
                self.all_credits_done = True

        for star in self.stars:
            star.update()

        if actions['start']:
            self.game.reset_keys()
            self.exit_state()
            pygame.mixer.music.load(self.game.Assets.get('reloaded'))
            pygame.mixer.music.play(-1)

    def render(self, surface):
        surface.fill((5, 5, 20))

        for star in self.stars:
            star.draw(surface)

        center_x = surface.get_width() // 2
        y_offset = self.scroll_y

        for surf in self.text_surfaces:
            text = surf.copy()
            rect = text.get_rect(center=(center_x, y_offset))
            surface.blit(text, rect)
            y_offset += int(30*self.game.scale_factor)
