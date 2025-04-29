import pygame
import os
import math
from states.state import State

class EndGameButton:
    def __init__(self, text, pos, size, click_func, font):
        self.text = text
        self.pos = pos
        self.size = size
        self.click_func = click_func

        self.font = font
        self.default_color = (60, 60, 60)
        self.hover_color = (90, 90, 90)
        self.text_color = (255, 255, 255)
        self.border_color = (255, 255, 255)

        self.rect = pygame.Rect(pos, size)
        self.hovered = False

    def update(self, actions):
        mouse_pos = pygame.mouse.get_pos()
        self.hovered = self.rect.collidepoint(mouse_pos)

        if actions['mouse']['Down'] and self.hovered:
            self.click_func()

    def draw(self, surface):
        color = self.hover_color if self.hovered else self.default_color
        pygame.draw.rect(surface, color, self.rect, border_radius=8)
        pygame.draw.rect(surface, self.border_color, self.rect, width=2, border_radius=8)

        text_surf = self.font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

class EndGame(State):
    def __init__(self, game, winner, player_info, real_towers):
        super().__init__(game)
        self.state = 'EndGame'
        self.winner = winner
        self.player_info = player_info
        self.real_towers = real_towers

        self.win_width = int(self.game.SCREEN_WIDTH * 0.6)
        self.win_height = int(self.game.SCREEN_HEIGHT * 0.6)
        self.win_rect = pygame.Rect(
            (self.game.SCREEN_WIDTH - self.win_width) // 2,
            (self.game.SCREEN_HEIGHT - self.win_height) // 2,
            self.win_width,
            self.win_height
        )

        self.font = self.game.Assets.get("montserrat")
        self.button_font = self.game.Assets.get("chakra_li")

        self.oscillation_frame = 0
        
        btn_y = self.win_rect.bottom - int(80 * self.scale_factor)
        btn_w, btn_h = int(150 * self.scale_factor), int(50 * self.scale_factor)
        leaderboard_y = btn_y - int(80 * self.scale_factor)
        leaderboard_x = btn_w + (50 * self.scale_factor)
        btn_spacing = (220 * self.scale_factor)
        
        self.buttons = [
            EndGameButton("Leaderboard", (self.game.SCREEN_WIDTH // 2 - leaderboard_x // 2, leaderboard_y), (leaderboard_x, btn_h), self.leaderboard, self.button_font),
            EndGameButton("Rematch", (self.game.SCREEN_WIDTH // 2 - btn_spacing - int(25 * self.scale_factor), btn_y), (btn_w, btn_h), self.rematch, self.button_font),
            EndGameButton("New Game", (self.game.SCREEN_WIDTH // 2 - btn_w // 2, btn_y), (btn_w, btn_h), self.new_game, self.button_font),
            EndGameButton("Main Menu", (self.game.SCREEN_WIDTH // 2 + btn_spacing - btn_w + int(25 * self.scale_factor), btn_y), (btn_w, btn_h), self.quit_to_menu, self.button_font)
        ]

        self.rendered_black = False
        self.leaderboard_path = "leaderboard.txt"
        self.update_leaderboard()

    def update_leaderboard(self):
        headers = ["player name", "wins", "losses", "most chosen tower", 
                 "best tower", "global ranking", "tower_stats"]
        player_data = {}

        if os.path.exists(self.leaderboard_path):
            with open(self.leaderboard_path, "r") as f:
                file_headers = f.readline().strip().split(',')
                for line in f:
                    parts = line.strip().split(',')
                    if len(parts) < 7:
                        continue
                    name = parts[0]
                    wins = int(parts[1])
                    losses = int(parts[2])
                    tower_stats_str = parts[6]

                    tower_stats = {}
                    if tower_stats_str:
                        for entry in tower_stats_str.split(';'):
                            entry = entry.strip()
                            if not entry:
                                continue
                            tid, total, wins_tower = map(int, entry.split())
                            tower_stats[tid] = {
                                'total_plays': total,
                                'wins': wins_tower
                            }

                    player_data[name] = {
                        'wins': wins,
                        'losses': losses,
                        'tower_stats': tower_stats
                    }

        for side in ["left", "right"]:
            p = self.player_info[side]
            name = p["name"]
            tower_id = self.real_towers[side]
            if name == self.winner.name:
                is_winner = True
            else:
                is_winner = False

            if name not in player_data:
                player_data[name] = {
                    'wins': 0,
                    'losses': 0,
                    'tower_stats': {}
                }

            if is_winner:
                player_data[name]['wins'] += 1
            else:
                player_data[name]['losses'] += 1

            if tower_id not in player_data[name]['tower_stats']:
                player_data[name]['tower_stats'][tower_id] = {
                    'total_plays': 0,
                    'wins': 0
                }

            tower_data = player_data[name]['tower_stats'][tower_id]
            tower_data['total_plays'] += 1
            if is_winner:
                tower_data['wins'] += 1

        leaderboard_entries = []
        for name, data in player_data.items():
            tower_stats = data['tower_stats']

            most_chosen = -1
            max_plays = -1
            for tid, stats in tower_stats.items():
                if stats['total_plays'] > max_plays:
                    max_plays = stats['total_plays']
                    most_chosen = tid

            # Calculate best tower (highest win rate, tiebreaker: total plays)
            best_tid = -1
            best_ratio = -1.0
            best_total = -1
            for tid, stats in tower_stats.items():
                total = stats['total_plays']
                if total == 0:
                    continue
                ratio = stats['wins'] / total
                if ratio > best_ratio or (ratio == best_ratio and total > best_total):
                    best_ratio = ratio
                    best_tid = tid
                    best_total = total

            total_games = data['wins'] + data['losses']
            winrate = data['wins'] / total_games if total_games > 0 else 0
            score = winrate * (1 - 1/(1 + total_games))

            leaderboard_entries.append({
                'name': name,
                'wins': data['wins'],
                'losses': data['losses'],
                'most_chosen': most_chosen,
                'best_tower': best_tid,
                'score': score,
                'tower_stats': tower_stats
            })

        leaderboard_entries.sort(key=lambda x: (-x['score'], -x['wins']))
        current_rank = 1
        prev_score = None
        rank_count = 1

        for i, entry in enumerate(leaderboard_entries):
            if entry['score'] == prev_score:
                entry['rank'] = current_rank
                rank_count += 1
            else:
                if prev_score is not None:
                    current_rank += rank_count
                rank_count = 1
                entry['rank'] = current_rank
                prev_score = entry['score']

        # Save updated leaderboard
        with open(self.leaderboard_path, 'w') as f:
            f.write(','.join(headers) + '\n')
            for entry in leaderboard_entries:
                # Format tower stats
                tower_stats = []
                for tid in sorted(entry['tower_stats'].keys()):
                    stats = entry['tower_stats'][tid]
                    tower_stats.append(f"{tid} {stats['total_plays']} {stats['wins']}")
                tower_stats_str = ';'.join(tower_stats)

                line = [
                    entry['name'],
                    str(entry['wins']),
                    str(entry['losses']),
                    str(entry['most_chosen']),
                    str(entry['best_tower']),
                    str(entry['rank']),
                    tower_stats_str
                ]
                f.write(','.join(line) + '\n')

    def leaderboard(self):
        from states.leaderboard import Leaderboard
        self.game.reset_keys()
        Leaderboard(self.game).enter_state()

    def rematch(self):
        from states.game_world import Game_World
        self.exit_state()
        self.game.reset_keys()
        Game_World(self.game, self.player_info).enter_state()

    def new_game(self):
        from states.select import Select
        self.exit_state()
        self.game.reset_keys()
        Select(self.game).enter_state()

    def quit_to_menu(self):
        from states.main import Main
        self.exit_state()
        self.game.reset_keys()
        Main(self.game).enter_state()

    def update(self, actions):
        for button in self.buttons:
            button.update(actions)

    def render(self, display):
        if not self.rendered_black:
            overlay = pygame.Surface((self.game.SCREEN_WIDTH, self.game.SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 100))
            display.blit(overlay, (0, 0))
            self.rendered_black = True

        pygame.draw.rect(display, (30, 30, 30), self.win_rect, border_radius=12)
        pygame.draw.rect(display, (255, 255, 255), self.win_rect, width=2, border_radius=12)

        self.oscillation_frame += 1

        text = self.font.render(f"{self.winner.name} WINS!", True, (255, 255, 255))
        scale = 1.1 + 0.1 * math.sin(self.oscillation_frame / 10.0)
        text = pygame.transform.scale(text, (int(text.get_width() * scale), int(text.get_height() * scale)))
        text_rect = text.get_rect(center=(self.game.SCREEN_WIDTH//2, self.win_rect.y + int(60*self.scale_factor)))
        display.blit(text, text_rect)

        for button in self.buttons:
            button.draw(display)