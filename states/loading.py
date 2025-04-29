import pygame
import os

def LoadScaledImage(image_path: str, scaling_factor: float = 1.0, scaling_dim: tuple = (0, 0)):
    image = pygame.image.load(image_path).convert_alpha()
    if scaling_dim != (0, 0):
        resized_image = pygame.transform.scale(image, scaling_dim)
    elif scaling_factor != 1:
        new_width = int(image.get_width() * scaling_factor)
        new_height = int(image.get_height() * scaling_factor)
        resized_image = pygame.transform.smoothscale(image, (new_width, new_height))
    else:
        resized_image = image
    return resized_image

class AssetLoader:
    def __init__(self, screen, screen_width, screen_height, scale_factor):
        self.screen = screen
        self.SCREEN_WIDTH = screen_width
        self.SCREEN_HEIGHT = screen_height
        self.scale_factor = scale_factor
        self.assets = {}

        self.assets_directory = "assets"
        self.sprite_directory = os.path.join(self.assets_directory, "sprites")
        self.font_directory = os.path.join(self.assets_directory, "font")
        self.sound_directory = os.path.join(self.assets_directory, "sound")

        self.font = pygame.font.Font(None, int(36 * self.scale_factor))

    def load_all(self):
        self.font_files = [
            ("Pixeltype.ttf", "pixel", 48),
            ("Pixeltype.ttf", "pixelsmall", 24),
            ("PressStart2P.ttf", "pressstart", 24),
            ("ChakraPetch-SB.ttf", "chakra_sb", 54),
            ("ChakraPetch-SB.ttf", "chakra_sbs", 28),
            ("ChakraPetch-LI.ttf", "chakra_li", 28),
            ("Jersey15.ttf", "jersey", 20),
            ("Micro5.ttf", "micro", 36),
            ("Orbitron.ttf", "orbitron", 45),
            ("SpaceGrotesk.ttf", "grotesk", 30),
            ("SpaceMono.ttf", "mono", 24),
            ("Tiny5.ttf", "tiny", 36),
            ("04B30.TTF", "04b30", 36),
            ("Minecraft.ttf", "minecraft", 36),
            ("Road_Rage.otf", "roadrage", 36),
            ("VCR.ttf", "vcr", 36),
            ("CourierPrime.ttf", "courier", 96),
            ("JetBrainsMono.ttf", "jetbrains", 24),
            ("Montserrat.ttf", "montserrat", 48),
            ("Fugaz.ttf", "fugaz", 96),
            ("TurretRoad.ttf", "turret", 48),
            ("Notable.ttf", "notable", 18),
        ]

        self.image_files = [
            ("bg.png", "background", (0,0)),
            ("cursor.png", "cursor", (0,0)),
            ("menu.png", "menu", (0,0)),
            ("wizard_idle.png", "idle", (0,0)),
            ("wizard_die.png", "die", (0,0)),
            ("Title.jpg", "title", (0,0)),
            ("enter.png", "enter", (50,50)),
            ("Mystic.png", "mystic", (346,195)),
            ("Mayhem.png", "mayhem", (310,173)),
            ("parallax-mountain-bg.png", "pm1", (960,540)),
            ("parallax-mountain-montain-far.png", "pm2", (960,540)),
            ("parallax-mountain-mountains.png", "pm3", (1920, 540)),
            ("parallax-mountain-trees.png", "pm4", (1920, 540)),
            ("parallax-mountain-foreground-trees.png", "pm5", (1920, 540)),
            ("0.png", "0", (120, 160)),
            ("1.png", "1", (120, 160)),
            ("2.png", "2", (120, 160)),
            ("selectbg.jpg", "selectbg", (960, 540)),
            ("redqm.jpg", "redqm", (0, 0)),
            ("blueqm.jpg", "blueqm", (0, 0)),
            ("spell1.png", "spell1", (0, 0)),
            ("spell2.png", "spell2", (0, 0)),
            ("spell3.png", "spell3", (0, 0)),
            ("spell4.png", "spell4", (0, 0)),
            ("Fight!.png", "fight", (0, 0)),
            ("up.png", "up", (45, 30)),
            ("down.png", "down", (45, 30)),
            ("leaderboard.png", "leaderboard", (0, 0)),
            ("leaderboard_hovered.png", "leaderboardh", (0, 0)),
            ("settings.png", "settings", (40, 40)),
        ]

        self.music_files = [
            ("8-Bit Warrior.mp3", "warrior"),
            ("At Doom's Gate.mp3", "doomgate"),
            ("BFG Division.mp3", "bfg"),
            ("Dr Fetus Castle.mp3", "fetus"),
            ("Reloaded Installer #10.mp3", "reloaded"),
            ("The Battle of Lil Slugger.mp3", "slugger"),
            ("The Only Thing They Fear is You.mp3", "you"),
            ("Goodbye Alola.mp3", "alola"),
            ("hipshop.mp3", "hipshop"),
            ("Trigger.mp3", "trigger"),
        ]

        self.sfx_files = [
            ("spell.wav", "spell"),
            ("regen.wav", "regen"),
            ("bolt.wav", "1s"),
            ("fire.wav", "2s"),
            ("ice.wav", "3s"),
            ("earth.wav", "4s"),
            ("click.wav", "click"),
            ("death.wav", "death"),
            ("gameover.wav", "gameover"),
            ("select.wav", "select"),
            ("explosion.wav", "explosion"),
            ("loud-thunder.wav", "thunder"),
            ("game-start.wav", "start"),
            ("ready.wav", "ready"),
            ("pause.wav", "pause"),
            ("unpause.wav", "unpause"),
        ]

        self.sprite_folders = [
            ("1", "1"),
            ("2", "2"),
            ("3", "3"),
            ("4", "4"),
        ]

        self.tutorial_folders = [
            ("Tutorial Frames"),
        ]

        total_assets = len(self.font_files) + len(self.image_files) + len(self.music_files) + sum(
            [len(os.listdir(os.path.join(self.sprite_directory, folder))) for folder, _ in self.sprite_folders]
        ) + sum(
            [len(os.listdir(os.path.join(self.sprite_directory, folder))) for folder in self.tutorial_folders]
        ) + len(self.sfx_files)

        progress = 0

        for font_file, alias, size in self.font_files:
            path = os.path.join(self.font_directory, font_file)
            self.assets[alias] = pygame.font.Font(path, int(size * self.scale_factor))
            progress += 1
            self.draw_loading_bar(progress, total_assets)

        for img_file, alias, dim in self.image_files:
            path = os.path.join(self.sprite_directory, img_file)
            self.assets[alias] = LoadScaledImage(path, scaling_dim=(int(dim[0] * self.scale_factor), int(dim[1] * self.scale_factor)))
            progress += 1
            self.draw_loading_bar(progress, total_assets)

        for music_file, alias in self.music_files:
            path = os.path.join(self.sound_directory, music_file)
            self.assets[alias] = path
            progress += 1
            self.draw_loading_bar(progress, total_assets)

        for sfx_file, alias in self.sfx_files:
            path = os.path.join(self.sound_directory, sfx_file)
            self.assets[alias] = pygame.mixer.Sound(path)
            progress += 1
            self.draw_loading_bar(progress, total_assets)

        for folder, alias_prefix in self.sprite_folders:
            folder_path = os.path.join(self.sprite_directory, folder)
            for filename in os.listdir(folder_path):
                name = filename.split(".")[0]
                key = f"{alias_prefix}_{name}"
                path = os.path.join(folder_path, filename)
                if "block" in filename:
                    self.assets[key] = LoadScaledImage(path, scaling_dim=(int(16 * self.scale_factor), int(16 * self.scale_factor)))
                else:
                    self.assets[key] = pygame.image.load(path).convert_alpha()
                progress += 1
                self.draw_loading_bar(progress, total_assets)

        for folder in self.tutorial_folders:
            folder_path = os.path.join(self.sprite_directory, folder)
            for filename in os.listdir(folder_path):
                name = filename.split(".")[0]
                path = os.path.join(folder_path, filename)
                self.assets[name] = LoadScaledImage(path, scaling_dim=(self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
                progress += 1
                self.draw_loading_bar(progress, total_assets)

    def get(self, name):
        return self.assets.get(name, self.assets.get("cursor"))

    def draw_loading_bar(self, progress, total):
        self.screen.fill((10, 10, 10))

        dots = "." * ((pygame.time.get_ticks() // 500) % 4)

        loading_text = self.font.render(f"LOADING{dots}", True, (0, 255, 0))
        text_rect = loading_text.get_rect(center=(self.SCREEN_WIDTH // 2, self.SCREEN_HEIGHT // 2 - int(30 * self.scale_factor)))
        self.screen.blit(loading_text, text_rect)

        # Loading Bar
        bar_width, bar_height = int(600 * self.scale_factor), int(30 * self.scale_factor)
        x = (self.SCREEN_WIDTH - bar_width) // 2
        y = self.SCREEN_HEIGHT // 2
        filled_width = int((progress / total) * bar_width)

        pygame.draw.rect(self.screen, (255, 255, 255), (x - 2, y - 2, bar_width + 4, bar_height + 4), 2)
        pygame.draw.rect(self.screen, (30, 30, 30), (x, y, bar_width, bar_height))
        pygame.draw.rect(self.screen, (0, 255, 0), (x, y, filled_width, bar_height))


        pygame.display.flip()