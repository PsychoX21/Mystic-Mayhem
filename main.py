import pygame
from states.main import Main
from states.loading import AssetLoader
from states.options import Options

class Game():
        def __init__(self):
            pygame.init()
            pygame.display.set_caption("Mystic Mayhem")
            icon = pygame.image.load("assets/sprites/icon.jpg")
            pygame.display.set_icon(icon)

            self.options = Options.load_options()
            self.music_volume = float(self.options["music_volume"]) * float(self.options["master_volume"])
            self.sfx_volume = float(self.options["sfx_volume"]) * float(self.options["master_volume"])

            pygame.mixer.init()
            pygame.mixer.music.set_volume(self.music_volume)

            resolution = self.options.get("resolution", "960x540")
            width, height = map(int, resolution.split("x"))
            self.start_width = width
            self.scale_factor = self.start_width / 960

            self.GAME_W,self.GAME_H = int(480 * self.scale_factor), int(270 * self.scale_factor)
            self.SCREEN_WIDTH,self.SCREEN_HEIGHT = int(960 * self.scale_factor), int(540 * self.scale_factor)

            self.game_canvas = pygame.Surface((self.GAME_W,self.GAME_H))
            self.screen = pygame.display.set_mode((self.SCREEN_WIDTH,self.SCREEN_HEIGHT))

            self.running, self.playing = True, True

            self.actions = {"left": False, "right": False, "up" : False, "down" : False, "action" : False, "start" : False, "mouse" : {"Down" : False, "Pos" : (0,0), "Right" : False}, "scroll_up" : False, "scroll_down" : False, "back": False}
            
            self.clock = pygame.time.Clock()
            self.FPS = 30

            self.music_position_start = 0
            self.music_position = 0

            self.load_assets()
            self.state_stack = []
            self.load_states()

        def play_sfx(self, sound_name):
            sound = self.Assets.get(sound_name)
            if sound != None:
                sfx = pygame.mixer.Sound(sound)
                sfx.set_volume(self.sfx_volume)
                sfx.play()

        def game_loop(self):
            while self.playing:
                if self.state_stack[-1].state != "Select":  
                    self.get_events()
                self.update()
                self.render()
                self.clock.tick(self.FPS)

        def get_events(self):
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.playing = False
                    self.running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if self.state_stack[-1].state == "Main":
                            self.playing = False
                            self.running = False
                        else:
                            self.actions['back'] = True
                    if event.key == pygame.K_a or event.key == pygame.K_LEFT:
                        self.actions['left'] = True
                    if event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                        self.actions['right'] = True
                    if event.key == pygame.K_w or event.key == pygame.K_UP:
                        self.actions['up'] = True
                    if event.key == pygame.K_s or event.key == pygame.K_DOWN:
                        self.actions['down'] = True
                    if event.key == pygame.K_o:
                        self.actions['action'] = True
                    if event.key == pygame.K_RETURN:
                        self.actions['start'] = True  

                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_ESCAPE:
                        self.actions['back'] = False
                    if event.key == pygame.K_a or event.key == pygame.K_LEFT:
                        self.actions['left'] = False
                    if event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                        self.actions['right'] = False
                    if event.key == pygame.K_w or event.key == pygame.K_UP:
                        self.actions['up'] = False
                    if event.key == pygame.K_s or event.key == pygame.K_DOWN:
                        self.actions['down'] = False
                    if event.key == pygame.K_o:
                        self.actions['action'] = False
                    if event.key == pygame.K_RETURN:
                        self.actions['start'] = False

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.actions['mouse']['Down'] = True

                    if event.button == 3:
                        self.actions['mouse']['Right'] = True

                    if event.button == 4:
                        self.actions['scroll_up'] = True

                    if event.button == 5:
                        self.actions['scroll_down'] = True

                if event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        self.actions['mouse']['Down'] = False

                    if event.button == 3:
                        self.actions['mouse']['Right'] = False

                if event.type == pygame.MOUSEMOTION:
                    self.actions['mouse']['Pos'] = tuple(x/2 for x in event.pos)

        def update(self):
            self.state_stack[-1].update(self.actions)

        def render(self):
            if self.state_stack[-1].state == "Game":
                self.state_stack[-1].render(self.game_canvas)
                self.screen.blit(pygame.transform.scale(self.game_canvas,(self.SCREEN_WIDTH, self.SCREEN_HEIGHT)), (0,0))
            else:
                self.state_stack[-1].render(self.screen)
            pygame.display.flip()

        def load_assets(self):
            self.Assets = AssetLoader(self.screen, self.SCREEN_WIDTH, self.SCREEN_HEIGHT, self.scale_factor)
            self.Assets.load_all()
            self.font = self.Assets.get("pixel")

        def load_states(self):
            self.title_screen = Main(self)
            self.state_stack.append(self.title_screen)

        def reset_keys(self):
            for action in self.actions:
                if action != "mouse":
                    self.actions[action] = False
                else:
                    self.actions["mouse"]["Down"] = False

if __name__ == "__main__":
    g = Game()
    while g.running:
        g.game_loop()