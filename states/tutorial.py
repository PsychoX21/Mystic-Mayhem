from states.state import State
import pygame

class Tutorial(State):
    def __init__(self, game):
        super().__init__(game)
        self.state = "Tutorial"
        self.font = self.game.Assets.get("mono")

        self.breakpoints = [0, 21, 42, 63, 84, 106, 128, 150, 171, 195]
        self.current_page = 0
        self.target_page = 0

        self.frame_index = 0

        self.playing = False
        self.direction = 1  # +1 for forward, -1 for backward

        self.waiting_for_input = True
        self.game.reset_keys()

    def update(self, actions):
        if self.playing:
            self.frame_index += self.direction

            start = self.breakpoints[self.current_page]
            end = self.breakpoints[self.target_page]
            halfway = (start + end) // 2

            if self.direction == 1 and self.frame_index >= halfway:
                self.current_page = self.target_page
            elif self.direction == -1 and self.frame_index <= halfway:
                self.current_page = self.target_page

            if self.direction == 1:
                if self.frame_index >= end:
                    self.frame_index = end
                    self.playing = False
                    self.waiting_for_input = True
            elif self.direction == -1:
                if self.frame_index <= end:
                    self.frame_index = end
                    self.playing = False
                    self.waiting_for_input = True

        else:
            if self.waiting_for_input:
                if actions["right"]:
                    if self.current_page < len(self.breakpoints) - 1:
                        self.target_page = self.current_page + 1
                        self.direction = 1
                        self.playing = True
                        self.waiting_for_input = False
                elif actions["left"]:
                    if self.current_page > 0:
                        self.target_page = self.current_page - 1
                        self.direction = -1
                        self.playing = True
                        self.waiting_for_input = False
                elif actions["start"]:
                    self.game.reset_keys()
                    self.exit_state()

    def render(self, surface):
        surface.fill((20, 20, 20))

        frame_key = f"frame_{self.frame_index}"
        frame = self.game.Assets.get(frame_key)
        if frame:
            rect = frame.get_rect(center=(self.game.SCREEN_WIDTH // 2, self.game.SCREEN_HEIGHT // 2))
            surface.blit(frame, rect)

        page_text = f"Page {self.current_page + 1}"
        text_surface = self.font.render(page_text, True, (255, 255, 255))
        rect = text_surface.get_rect(bottomright=(self.game.SCREEN_WIDTH - 20, self.game.SCREEN_HEIGHT - 5))
        surface.blit(text_surface, rect)

        hint_surface = self.font.render("Left/Right to Navigate, Start to Exit", True, (150, 150, 150))
        hint_rect = hint_surface.get_rect(center=(self.game.SCREEN_WIDTH // 2, self.game.SCREEN_HEIGHT - 30))
        surface.blit(hint_surface, hint_rect)