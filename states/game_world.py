import pygame
import numpy as np
from states.state import State
from states.pause_menu import PauseMenu
from states.end_game import EndGame
import random

class Game_World(State):
    def __init__(self, game, players):
        super().__init__(game)
        self.player_info = players
        self.real_towers = {"left": self.player_info["left"]["selected_tower"], "right": self.player_info["right"]["selected_tower"]}
        self.state = 'Game'
        self.game = game
        self.background = pygame.transform.scale(game.Assets.get("background"),
            (int(game.Assets.get("background").get_width() * 960 * self.scale_factor / 1600), int(game.Assets.get("background").get_height() * 960 * self.scale_factor / 1600)))
        
        pygame.mixer.music.load(game.Assets.get("warrior"))
        pygame.mixer.music.play(-1, start=1.1)
        self.game.music_position_start = pygame.mixer.music.get_pos() / 1000

        global width, height
        width, height = game.GAME_W, game.GAME_H
        height = height - int(20 * self.scale_factor)

        self.players = pygame.sprite.Group()
        self.player1_blocks = pygame.sprite.Group()
        self.player2_blocks = pygame.sprite.Group()
        self.blocks = pygame.sprite.Group()
        self.ball_group = pygame.sprite.Group()

        self.game_over = False
        self.winner = None

        self.ball_selection_p1 = []
        self.ball_selection_p2 = []
        self.current_selected_index_p1 = 0
        self.current_selected_index_p2 = 0

        global gravity, elasticity, air_drag
        
        gravity = np.array([0,1 * self.scale_factor], dtype=float)
        elasticity = 0.7
        air_drag = 0.02

        self.setup()

    def setup(self):
        self.player1 = Player(self.game, int(50 * self.scale_factor), height - int(80 * self.scale_factor), inverted=True, name=self.player_info["left"]["name"])
        self.player2 = Player(self.game, width - int(130 * self.scale_factor), height - int(80 * self.scale_factor), inverted=False, name=self.player_info["right"]["name"])
        self.players.add(self.player1, self.player2)

        self.create_ball_selection(self.player1)
        self.create_ball_selection(self.player2)

        self.current_player = random.choice([self.player1, self.player2])

        self.ball_images = [
            pygame.transform.smoothscale(self.game.Assets.get("spell1"), (int(16 * self.scale_factor), int(16 * self.scale_factor))),
            pygame.transform.smoothscale(self.game.Assets.get("spell2"), (int(16 * self.scale_factor), int(16 * self.scale_factor))),
            pygame.transform.smoothscale(self.game.Assets.get("spell3"), (int(16 * self.scale_factor), int(16 * self.scale_factor))),
            pygame.transform.smoothscale(self.game.Assets.get("spell4"), (int(16 * self.scale_factor), int(16 * self.scale_factor))),
        ]

        self.spawn_selected_ball()

        # Define the tower shapes as lists of strings (where 'X' represents a block)
        # The tower formed will be vertically flipped.
        tower_shapes = {
            0: [
                ".XX.",
                "XXXX",
                "X..X",
                ".XX.",
                ".XX.",
                "X..X",
                ".XX."
            ],
            1: [
                "XX.X",
                "XX.X",
                ".XX.",
                ".XX.",
                "XX.X",
                "XX.X"
            ],
            2: [
                "X...",
                "XX..",
                ".XX.",
                "..XX",
                "..XX",
                "..XX",
                ".XX.",
                "XX..",
                "X..."
            ]
        }

        def build_tower(self, base_x, base_y, group, player_selection, mirror=False):
            # Select the tower shape based on the player's selection
            if player_selection == 3:
                tower_number = random.randint(0, 2)
                tower_shape = tower_shapes[tower_number]
                if mirror:
                    self.real_towers["left"] = tower_number
                else:
                    self.real_towers["right"] = tower_number
            else:
                tower_shape = tower_shapes.get(player_selection)

            if mirror:
                tower_shape = [row[::-1] for row in tower_shape]
            
            for row_idx, row in enumerate(tower_shape):
                for col_idx, char in enumerate(row):
                    if char == 'X':
                        block_x = base_x + col_idx * int(16 * self.scale_factor)
                        block_y = base_y - row_idx * int(16 * self.scale_factor)
                        block = Block(self.game, block_x, block_y, random.choice(['1', '2', '3', '4']))

                        if row_idx == 0:
                            block.base = True

                        group.add(block)
                        self.blocks.add(block)

        build_tower(self, self.player1.position_x - int(50 * self.scale_factor), self.player1.position_y + int(64 * self.scale_factor), self.player1_blocks, self.player_info["left"]["selected_tower"], mirror=True)
        build_tower(self, self.player2.position_x + int(66 * self.scale_factor), self.player2.position_y + int(64 * self.scale_factor), self.player2_blocks, self.player_info["right"]["selected_tower"])

        self.ready_state = True
        self.ready_timer = 0
        self.ready_img = self.game.Assets.get("fight")

# Gravity Implementation (Will work on it later)
    # def check_block_stability(self):
    #     tolerance = 3 * self.scale_factor

    #     for group in [self.player1_blocks, self.player2_blocks]:
    #         # Step 2: Make ground-touching blocks stable
    #         for block in group:
    #             if block.base or block.rect.bottom >= height:
    #                 block.stable = True

    #         # Step 3: Propagate stability
    #         # Changed variable to check if new stable block arrived to check if any other block can become stable due to it
    #         changed = True
    #         while changed:
    #             changed = False
    #             for block in group:
    #                 if block.stable:
    #                     continue
    #                 adjacent_positions = [
    #                     (block.rect.x + int(16 * self.scale_factor), block.rect.y),
    #                     (block.rect.x - int(16 * self.scale_factor), block.rect.y),
    #                     (block.rect.x, block.rect.y + int(16 * self.scale_factor)),
    #                     (block.rect.x, block.rect.y - int(16 * self.scale_factor))
    #                 ]
    #                 for pos in adjacent_positions:
    #                     for neighbor in group:
    #                         if abs(neighbor.rect.x - pos[0]) <= tolerance and abs(neighbor.rect.y - pos[1]) <= tolerance:
    #                             if neighbor.stable:
    #                                 block.stable = True
    #                                 changed = True
    #                                 break
    #                     if block.stable:
    #                         break

    #         for block in group:
    #             block.in_motion = not block.stable

    # def update_falling_blocks(self):
    #     for block in self.blocks:
    #         if block.in_motion:
    #             block.velocity += gravity
    #             block.velocity[1] *= (1 - air_drag)
                
    #             new_y = block.rect.y + block.velocity[1]
                
    #             if new_y + block.rect.height >= height:
    #                 new_y = height - block.rect.height
    #                 block.velocity[1] *= -0.2
    #                 if abs(block.velocity[1]) < 0.5:
    #                     block.velocity = np.array([0.0, 0.0])
    #                     block.in_motion = False
                
    #             block.rect.y = new_y
    #             collisions = pygame.sprite.spritecollide(block, self.blocks, False)
    #             for other in collisions:
    #                 if other == block:
    #                     continue
    #                 if block.velocity[1] > 0 and block.rect.colliderect(other.rect):
    #                     block.rect.bottom = other.rect.top
    #                     block.velocity[1] *= -0.2
    #                     if abs(block.velocity[1]) < 0.5:
    #                         block.velocity = np.array([0.0, 0.0])
    #                         block.in_motion = False

    def create_ball_selection(self, player):
        base_y = int(35 * self.scale_factor)
        spacing = int(30 * self.scale_factor)

        if player == self.player1:
            base_x = int(20 * self.scale_factor)
        else:
            base_x = width - int(20 * self.scale_factor) - 2*spacing

        selections = []

        for i in range(3):
            ball_type = random.choice(['1', '2', '3', '4'])
            pos = (base_x + i * spacing, base_y)
            selections.append({'type': ball_type, 'pos': pos, 'radius': int(10 * self.scale_factor)})

        if player == self.player1:
            self.ball_selection_p1 = selections
            self.current_selected_index_p1 = 0
        else:
            self.ball_selection_p2 = selections
            self.current_selected_index_p2 = 0

    def get_current_ball_selection(self):
        return self.ball_selection_p1 if self.current_player == self.player1 else self.ball_selection_p2

    def get_current_index(self):
        return self.current_selected_index_p1 if self.current_player == self.player1 else self.current_selected_index_p2

    def set_current_index(self, index):
        if self.current_player == self.player1:
            self.current_selected_index_p1 = index
        else:
            self.current_selected_index_p2 = index
    
    def spawn_selected_ball(self):
        ball_selection = self.get_current_ball_selection()
        index = self.get_current_index()
        if not ball_selection:
            return

        ball_type = ball_selection[index]['type']
        if self.current_player == self.player1:
            ball_pos = (self.player1.position_x + int(60 * self.scale_factor), self.player1.position_y + int(25 * self.scale_factor))
        else:
            ball_pos = (self.player2.position_x + int(20 * self.scale_factor), self.player2.position_y + int(25 * self.scale_factor))

        self.ball = Ball(self.game, *ball_pos, type=ball_type)
        self.ball.reset_spawn_anim()
        self.ball_group.add(self.ball)
        self.current_player.reset_animation()

    def switch_turn(self):
        self.current_player = self.player2 if self.current_player == self.player1 else self.player1

        if self.current_player is self.player1:
            self.current_selected_index_p1 = 0
        else:
            self.current_selected_index_p2 = 0

        self.spawn_selected_ball()

    def check_ball_selection(self, actions):
        # Checking if dragging or thrown
        if self.ball.is_dragging or self.ball.thrown:
            return
    
        if actions['mouse']["Down"]:
            mouse_pos = actions['mouse']["Pos"]
            selection = self.get_current_ball_selection()
            for idx, option in enumerate(selection):
                center = option['pos']
                radius = option['radius']
                if np.linalg.norm(np.array(mouse_pos) - np.array(center)) <= radius:
                    self.set_current_index(idx)

                    # Kill current ball and spawn new
                    for b in self.ball_group:
                        b.kill()
                    
                    self.spawn_selected_ball()
                    break

    def update(self, actions):
        if self.ready_timer==0 or self.ready_state == False:
            if actions["back"]:
                self.game.music_position = self.game.music_position + (pygame.mixer.music.get_pos() / 1000 - self.game.music_position_start)
                self.game.play_sfx("pause")
                PauseMenu(self.game).enter_state()
                self.game.reset_keys()

            self.players.update(actions)
            # Player Dying Animation Setup
            if (self.player1.start or self.player2.start):
                if (self.player1.done or self.player2.done):
                    self.win_state(self.winner)
                else:
                    return
            self.blocks.update(actions)
            
            if not self.game_over:
                self.ball_group.update(actions)

            self.check_ball_selection(actions)
            
            if self.ball.current_explosion_frame >= len(self.ball.explosion_sprites):
                self.finish_ball()
                self.check_win_condition()

            if self.ball.is_exploding == False:
                if self.ball.ground_bounce_count >= 2:
                    self.ball.kill()
                    current_selection = self.get_current_ball_selection()
                    index = self.get_current_index()

                    if 0 <= index < len(current_selection):
                        del current_selection[index]
                    
                    if len(current_selection) == 0:
                        if self.current_player == self.player1:
                            self.player1.ball_selection = self.create_ball_selection(self.player1)
                        else:
                            self.player2.ball_selection = self.create_ball_selection(self.player2)
                        
                    self.switch_turn()
                    return

                if hasattr(self, 'ball') and self.ball.alive():
                    if (actions["mouse"]["Right"] or actions["action"]) and self.ball.thrown:
                        # Explosion handling
                        self.handle_explosion()
                        self.game.play_sfx("explosion")
                        self.ball.is_exploding = True
                        actions["action"] = False
                        actions["mouse"]["Right"] = False
                    else:
                        # Normal collision
                        hits = self.detect_hits()

                        for block in hits:
                            if not self.ball.has_hit:
                                self.handle_block_hit(block)
                                self.game.play_sfx(f"{self.ball.type}s")
                                self.finish_ball()
                                break

                self.check_win_condition()

            # for block in self.blocks:
            #     block.stable = False
            # self.check_block_stability()
            # self.update_falling_blocks()

    def detect_hits(self):
        opponent_blocks = self.player2_blocks if self.current_player == self.player1 else self.player1_blocks
        hits = pygame.sprite.spritecollide(self.ball, opponent_blocks, False)
        hits.sort(key=lambda blk: 
            (blk.rect.centerx - self.ball.position[0])**2 +
            (blk.rect.centery - self.ball.position[1])**2
        )
        return hits

    def handle_block_hit(self, block):
        if self.ball.type == block.type:
            block.health -= 3
        else:
            block.health -= 2

        tolerance = 3 * self.scale_factor # Pixel tolerance for adjacent
        # Adjacent blocks damage
        group = self.player1_blocks if block in self.player1_blocks else self.player2_blocks
        adjacent_positions = [
            (block.rect.x + int(16 * self.scale_factor), block.rect.y),
            (block.rect.x - int(16 * self.scale_factor), block.rect.y),
            (block.rect.x, block.rect.y + int(16 * self.scale_factor)),
            (block.rect.x, block.rect.y - int(16 * self.scale_factor))
        ]

        for pos in adjacent_positions:
            for adjacent_block in group:
                if abs(adjacent_block.rect.x - pos[0]) <= tolerance and abs(adjacent_block.rect.y - pos[1]) <= tolerance:
                    if self.ball.type == adjacent_block.type:
                        adjacent_block.health -= 2
                    else:
                        adjacent_block.health -= 1

                    if self.ball.ground_bounce_count == 1:
                        adjacent_block.health += 1

    def handle_explosion(self):
        # Still Feels OP, but will work on it later
        explosion_radii = [
            (20 * self.scale_factor, 2),
            (32 * self.scale_factor, 1),
        ]

        group = self.player1_blocks if self.current_player == self.player2 else self.player2_blocks

        for block in group:
            distance = ((block.rect.centerx - self.ball.position[0])**2 + (block.rect.centery - self.ball.position[1])**2)**0.5

            for radius, damage in explosion_radii:
                if distance <= radius:
                    if block.type == self.ball.type:
                        block.health -= 1
                    block.health -= damage
                    break

    def finish_ball(self):
        self.ball.has_hit = True
        self.ball.kill()

        current_selection = self.get_current_ball_selection()
        index = self.get_current_index()

        if 0 <= index < len(current_selection):
            del current_selection[index]

        if len(current_selection) == 0:
            if self.current_player == self.player1:
                self.player1.ball_selection = self.create_ball_selection(self.player1)
            else:
                self.player2.ball_selection = self.create_ball_selection(self.player2)

        self.switch_turn()

    def render_ball_selection(self, display):
        current_selection = self.get_current_ball_selection()
        current_index = self.get_current_index()

        for idx, option in enumerate(current_selection):
            pos = option['pos']
            radius = option['radius']
            ball_type = option['type']

            outline_color = (255, 0, 0) if idx == current_index else (180, 180, 180)
            pygame.draw.circle(display, outline_color, pos, radius, 1)

            image_rect = self.ball_images[int(ball_type) - 1].get_rect(center=pos)
            display.blit(self.ball_images[int(ball_type) - 1], image_rect)

    def render(self, display):
        display.blit(self.background, (0, 0))
        self.blocks.draw(display)
        self.ball_group.draw(display)

        font = self.game.Assets.get("notable")
        left_name_surf = font.render(self.player1.name, True, (255, 255, 255))
        left_name_rect = left_name_surf.get_rect(topleft=((int(15 * self.scale_factor)), 0))
        display.blit(left_name_surf, left_name_rect)

        right_name_surf = font.render(self.player2.name, True, (255, 255, 255))
        right_name_rect = right_name_surf.get_rect(topright=((width - int(15 * self.scale_factor)), 0))
        display.blit(right_name_surf, right_name_rect)

        for ball in self.ball_group:
            ball.draw_path(display)

        self.render_ball_selection(display)
        self.players.draw(display)

        # Fight Animation
        t = self.ready_timer
        if t < 40:
            self.ready_timer += 1
            t = self.ready_timer

            if t < 15:
                scale = 7.0 - 6.5 * (t / 15)
                angle = 0
                shake = 5 * np.sin(t * np.pi / 4)
            elif t < 30:
                scale = 0.5 + 0.2 * np.sin((t - 15) / 10 * np.pi)
                angle = 0
                shake = 3 * np.sin(t * np.pi / 2)
            else:
                progress = (t - 30) / 10
                scale = 0.5 - 0.5 * progress
                angle = 0 + 1080 * progress
                shake = 5 * np.sin(progress * 6 * np.pi)

            final_scale = scale * self.scale_factor / 4
            new_width = int(1920 * final_scale)
            new_height = int(1080 * final_scale)

            if new_width > 0 and new_height > 0:
                fight_surf = pygame.transform.smoothscale(self.ready_img, (new_width, new_height)).convert_alpha()

                if t >= 30:
                    fight_surf = pygame.transform.rotate(fight_surf, angle)

                fight_surf.set_alpha(255)
                fight_rect = fight_surf.get_rect(center=(self.game.GAME_W // 2 + int(shake), self.game.GAME_H // 2))
                display.blit(fight_surf, fight_rect)

        else:
            self.ready_state = False

    def check_win_condition(self):
        if len(self.player1_blocks) == 0:
            self.game_over = True
            self.winner = self.player2
            self.player1.start = True
        elif len(self.player2_blocks) == 0:
            self.game_over = True
            self.winner = self.player1
            self.player2.start = True

    def win_state(self, winner):
        self.exit_state()
        (EndGame(self.game, winner, self.player_info, self.real_towers)).enter_state()

class Ball(pygame.sprite.Sprite):
    def __init__(self, game, x=75, y=200, v=None, type='1', loaded=True):
        super().__init__()
        self.game = game
        self.position = np.array([x,y], dtype=float)
        self.velocity = np.array(v, dtype=float) if v is not None else np.array([0,0], dtype=float)

        self.radius = int(8 * self.game.scale_factor)
        self.type = type
        self.loaded = loaded
        self.loaded_position = np.array([x,y], dtype=float)
        self.thrown = False
        self.is_dragging = False
        
        self.ground_bounce_count = 0
        self.has_hit = False

        self.spawn_anim_progress = 0
        self.spawn_anim_duration = 30

        self.is_exploding = False
        self.current_explosion_frame = 0

        self.load_assets()
        self.current_frame, self.frame_counter = 0,0
        self.image = self.ball_sprites[self.current_frame]
        self.rect = self.image.get_rect(center=self.position)

    def load_assets(self):
        x_start, y_start = 496, 160
        sprite_width, sprite_height = 16, 16

        exp_x_start, exp_y_start = 192, 160
        exp_sprite_width, exp_sprite_height = 32, 32

        def get_sprite(sheet, frame_x, frame_y, width, height):
            rect = pygame.Rect(frame_x, frame_y, width, height)
            image = sheet.subsurface(rect).copy()
            scaled_image = pygame.transform.smoothscale(image, (int(width * self.game.scale_factor), int(height * self.game.scale_factor)))
            return scaled_image
        
        self.ball_sprites = [get_sprite(self.game.Assets.get(f"{self.type}_bullet"), x_start + i * sprite_width, y_start, sprite_width, sprite_height) for i in range(4)]
        self.explosion_sprites = [pygame.transform.smoothscale(get_sprite(self.game.Assets.get(f"{self.type}_explosion"), exp_x_start + i * exp_sprite_width, exp_y_start, exp_sprite_width, exp_sprite_height), (int(56 * self.game.scale_factor), int(56 * self.game.scale_factor))) for i in range(4)]

    def reset_spawn_anim(self):
        self.spawn_anim_progress = 0
        self.loaded = True
        self.thrown = False
        self.velocity = np.array([0,0], dtype=float)
        self.position = self.loaded_position.copy()

        # Animation Start ( At 1 pixel size and 0 opacity )
        target_size = self.ball_sprites[0].get_size()
        initial_progress = 0.001  
        new_size = (max(1, int(target_size[0] * initial_progress)),
                    max(1, int(target_size[1] * initial_progress)))
        scaled_image = pygame.transform.scale(self.ball_sprites[self.current_frame], new_size)
        scaled_image.set_alpha(0)
        self.image = scaled_image
        self.rect = self.image.get_rect(center=self.position)

    def animate_exploding(self):
        self.is_exploding = True
        self.image = self.explosion_sprites[int(self.current_explosion_frame)]
        self.rect = self.image.get_rect(center=self.position)
        self.current_explosion_frame += 0.5

    def update(self, actions):
        if self.spawn_anim_progress < self.spawn_anim_duration:
            self.spawn_anim_progress += 1
            if self.spawn_anim_progress == 1:
                self.game.play_sfx("regen")
            progress = self.spawn_anim_progress / self.spawn_anim_duration

            target_size = self.ball_sprites[0].get_size()
            new_size = (max(1, int(target_size[0] * progress)), max(1, int(target_size[1] * progress)))
            scaled_image = pygame.transform.scale(self.ball_sprites[self.current_frame], new_size)
            scaled_image.set_alpha(int(255 * progress))
            self.image = scaled_image
            self.rect = self.image.get_rect(center=self.position)
            self.animate()
            return

        if not self.thrown:
            self.reposition(actions)
        else:
            if self.is_exploding:
                self.animate_exploding()
                return
            self.move()

        self.animate()
        self.image = self.ball_sprites[self.current_frame]
        self.rect = self.image.get_rect(center=self.position)

    def move(self):
        self.velocity += gravity
        self.position += self.velocity
        self.velocity *= (1 - air_drag)

        if self.position[0] < self.radius:
            self.position[0] = 2 * self.radius - self.position[0]
            self.velocity[0] *= -elasticity
        elif self.position[0] > width - self.radius:
            self.position[0] = 2 * (width - self.radius) - self.position[0]
            self.velocity[0] *= -elasticity

        if self.position[1] < self.radius:
            self.position[1] = 2 * self.radius - self.position[1]
            self.velocity[1] *= -elasticity
        elif self.position[1] > height - self.radius:
            self.position[1] = 2 * (height - self.radius) - self.position[1]
            self.velocity[1] *= -elasticity

            self.ground_bounce_count += 1

    def reposition(self, actions):
        if actions['mouse']["Down"]:
            dist = np.linalg.norm(self.loaded_position - np.array(actions['mouse']["Pos"]))
            if dist < int(20 * self.game.scale_factor):
                self.is_dragging = True

        if self.loaded and actions['mouse']["Down"] and self.is_dragging:
            diff = np.array(actions['mouse']["Pos"]) - np.array(self.loaded_position)
            magnitude = min(np.linalg.norm(diff) - int(10 * self.game.scale_factor), int(27 * self.game.scale_factor))
            if magnitude > 0: 
                self.velocity = -(diff / np.linalg.norm(diff)) * magnitude
            else:
                self.velocity = np.array([0,0])
            self.position = self.loaded_position

        elif self.is_dragging and not actions['mouse']["Down"]:
            if np.linalg.norm(self.velocity) > int(3 * self.game.scale_factor):
                self.loaded = False
                self.thrown = True
            else:
                self.velocity = np.array([0,0])
                self.position = self.loaded_position
            self.is_dragging = False

    def draw_path(self, display):
        if not self.thrown and self.is_dragging and np.linalg.norm(self.velocity) > int(3 * self.game.scale_factor):
            temp_pos = np.copy(self.loaded_position)
            temp_vel = np.copy(self.velocity)
            path = []

            for _ in range(5):
                temp_vel += gravity
                temp_pos += temp_vel
                temp_vel *= (1 - air_drag)
                if len(path) == 0 or np.linalg.norm(path[-1] - temp_pos) > 3:
                    path.append(temp_pos.copy())

            for point in path:
                pygame.draw.circle(display, (255, 255, 255), point.astype(int), 2)

    def animate(self):
        self.frame_counter += 1
        if self.frame_counter >= 10:
            self.frame_counter = 0
            self.current_frame = (self.current_frame + 1) % len(self.ball_sprites)

    def render(self, display):
        self.draw_path(display)
        display.blit(self.image, self.rect)

class Player(pygame.sprite.Sprite):
    def __init__(self, game, x, y, inverted=False, name=""):
        super().__init__()
        self.game = game
        self.name = name
        self.position_x, self.position_y = x, y
        self.current_frame, self.frame_counter = 0,0
        self.killed = False
        self.inverted = inverted

        self.load_sprites()
        self.curr_anim_list = self.idle_sprites
        self.image = self.curr_anim_list[self.current_frame]
        if self.inverted:
            self.image = pygame.transform.flip(self.image, True, False)
        self.rect = self.image.get_rect(topleft=(self.position_x, self.position_y))

        self.start = False
        self.done = False

    def update(self, actions):
        if self.start and not self.killed:
            self.curr_anim_list = self.die_sprites
            self.current_frame = 0
            self.killed = True
            self.game.play_sfx("death")
            
        self.animate()
        self.image = self.curr_anim_list[self.current_frame]

        if self.inverted:
            self.image = pygame.transform.flip(self.image, True, False)

    def animate(self):
        self.frame_counter += 1
        if self.frame_counter > 4:
            self.frame_counter = 0
            if not self.killed:
                if self.current_frame == 9:
                    self.current_frame = 6
                self.current_frame += 1
            else:
                if self.current_frame < 10:
                    self.current_frame += 1
                else:
                    self.done = True

    def load_sprites(self):
        def get_sprite(sheet, frame_x, frame_y, width, height):
            rect = pygame.Rect(frame_x * width, frame_y * height, width, height)
            image = sheet.subsurface(rect).copy()
            scaled_image = pygame.transform.smoothscale(image, (int(width * self.game.scale_factor), int(height * self.game.scale_factor)))
            return scaled_image

        self.idle_sprites = [get_sprite(self.game.Assets.get("idle"), i, j, 80, 80) for j in range(4) for i in range(3)]
        self.die_sprites = [get_sprite(self.game.Assets.get("die"), i, j, 80, 80) for j in range(4) for i in range(3)]

    def reset_animation(self):
        self.current_frame = 0

class Block(pygame.sprite.Sprite):
    def __init__(self, game, x, y, type='1', size=(2,2)):
        super().__init__()
        self.game = game
        self.x, self.y = x, y
        self.type = type
        self.size = size
        self.health = 3
        self.destroyed = False
        self.current_frame = 0

        self.stable = False
        self.base = False
        self.velocity = np.array([0.0, 0.0], dtype=float)
        self.in_motion = False

        self.load_assets()
        self.image = self.block_sprites[self.current_frame]
        self.rect = self.image.get_rect(topleft=(self.x, self.y))

    def load_assets(self):
        self.block_sprites = [self.game.Assets.get(f"{self.type}_block{i}") for i in range(1,10)]

    def update(self, actions):
        if self.health == 2:
            self.current_frame = 1
        elif self.health == 1:
            self.current_frame = 2
        elif self.health <= 0:
            self.current_frame += 1

        if self.current_frame >= len(self.block_sprites):
            self.destroyed = True

        if not self.destroyed:
            self.image = self.block_sprites[self.current_frame]
        else:
            self.kill()