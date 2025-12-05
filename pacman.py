import pygame
import math
import random
import time
import wave
import struct
import os

# =============================================================================
# MODÜL 1: AYARLAR VE YARDIMCI FONKSİYONLAR
# =============================================================================

# --- SABİTLER ---
WIDTH, HEIGHT = 640, 680
CELL_SIZE = 32
FPS = 60

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (20, 20, 200)       # Duvarlar
YELLOW = (255, 255, 0)     # Pacman

# Hayalet Renkleri
RED = (255, 0, 0)          # Blinky
CYAN = (0, 255, 255)       # Inky
PINK = (255, 182, 193)     # Pinky
ORANGE = (255, 165, 0)     # Clyde
SCARED_BLUE = (50, 50, 255)# Korkmuş Hayalet (Mavi)

# Diğer
GREEN = (0, 255, 0)        # Enerji Topu
GRAY = (150, 150, 150)     # Pasif Metinler
DARK_GRAY = (50, 50, 50)   # Panel Arkaplanı
BUTTON_COLOR = (0, 128, 255)
BUTTON_HOVER = (0, 180, 255)

# Harita
MAP_LAYOUT = [
    "WWWWWWWWWWWWWWWWWWWW",
    "W........W.........W",
    "W.WW.WWW.W.WWW.WW..W",
    "W.WW.WWW.W.WWW.WW..W",
    "Wo................oW",
    "W.WW.W.WWWWW.W.WW..W",
    "W....W...W...W.....W",
    "WWWW.WWW W WWW.WWW.W",
    "W....W G   G W.....W",
    "WWWW.W G   G W.WW.WW",
    "W....W WWWWW W.....W",
    "W.WW.W.......W..WW.W",
    "Wo...W.WWWWW.W.....W",
    "W.WW...............W",
    "W.WW.WWW.W.WWW.WWP.W",
    "W........W.........W",
    "WWWWWWWWWWWWWWWWWWWW"
]


def create_beep_sound():
    filename = "beep.wav"
    if not os.path.exists(filename):
        duration = 0.05
        frequency = 440.0
        sample_rate = 44100
        n_samples = int(sample_rate * duration)
        with wave.open(filename, 'w') as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(sample_rate)
            for i in range(n_samples):
                value = int(32767.0 * 0.5 * math.sin(2.0 * math.pi * frequency * i / sample_rate))
                data = struct.pack('<h', value)
                wav_file.writeframes(data)


# =============================================================================
# MODÜL 2: KARAKTER SINIFLARI (AGENT & GHOST)
# =============================================================================

class PacmanAgent:
    def __init__(self, x, y):
        self.grid_pos = [x, y]
        self.pixel_pos = [x * CELL_SIZE + CELL_SIZE // 2, y * CELL_SIZE + CELL_SIZE // 2]
        self.direction = (0, 0)  # (dx, dy)
        self.score = 0
        self.memory = []

        # Animasyon Değişkenleri
        self.mouth_open = 0
        self.mouth_speed = 10
        self.mouth_dir = 1  # 1: açılıyor, -1: kapanıyor
        self.rotation = 0  # Ağız yönü (derece)

    def update_animation(self):
        # Ağız açılıp kapanma efekti
        self.mouth_open += self.mouth_dir * self.mouth_speed
        if self.mouth_open >= 45: self.mouth_dir = -1
        if self.mouth_open <= 0: self.mouth_dir = 1

        # Yöne göre rotasyon
        if self.direction == (1, 0):
            self.rotation = 0
        elif self.direction == (-1, 0):
            self.rotation = 180
        elif self.direction == (0, -1):
            self.rotation = 90
        elif self.direction == (0, 1):
            self.rotation = 270

    def draw(self, screen):
        self.update_animation()
        cx, cy = self.grid_pos[0] * CELL_SIZE + CELL_SIZE // 2, self.grid_pos[1] * CELL_SIZE + CELL_SIZE // 2
        radius = CELL_SIZE // 2 - 2

        # 1. Sarı Gövde
        pygame.draw.circle(screen, YELLOW, (cx, cy), radius)

        # 2. Ağız
        if self.mouth_open > 0:

            start_angle = math.radians(self.rotation - self.mouth_open)
            end_angle = math.radians(self.rotation + self.mouth_open)

            p1 = (cx + radius * math.cos(start_angle), cy - radius * math.sin(start_angle))
            p2 = (cx + radius * math.cos(end_angle), cy - radius * math.sin(end_angle))

            pygame.draw.polygon(screen, BLACK, [(cx, cy), p1, p2])

        # 3. Göz
        eye_x, eye_y = cx, cy
        eye_offset = radius * 0.5

        if self.rotation == 0:
            eye_x, eye_y = cx + 2, cy - eye_offset
        elif self.rotation == 180:
            eye_x, eye_y = cx - 2, cy - eye_offset
        elif self.rotation == 90:
            eye_x, eye_y = cx - eye_offset, cy - 2
        elif self.rotation == 270:
            eye_x, eye_y = cx + eye_offset, cy - 2

        pygame.draw.circle(screen, BLACK, (int(eye_x), int(eye_y)), 3)

    # UTILITY AI MANTIĞI
    def get_valid_moves(self, pos, layout):
        x, y = pos
        moves = []
        for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
            nx, ny = x + dx, y + dy
            if 0 <= ny < len(layout) and 0 <= nx < len(layout[0]):
                if layout[ny][nx] != 'W':
                    moves.append((dx, dy))
        return moves

    def calculate_path_utility(self, start_pos, foods, energies, layout):
        queue = [(start_pos[0], start_pos[1], 0)]
        visited = {tuple(start_pos)}
        total_score = 0
        MAX_DEPTH = 15

        while queue:
            cx, cy, dist = queue.pop(0)
            if dist > MAX_DEPTH: continue

            curr_rect = pygame.Rect(cx * CELL_SIZE, cy * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            for f in foods:
                if curr_rect.colliderect(f): total_score += 600 / ((dist + 1) ** 1.5)
            for e in energies:
                if curr_rect.colliderect(e): total_score += 2500 / ((dist + 1) ** 1.5)

            for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
                nx, ny = cx + dx, cy + dy
                if 0 <= ny < len(layout) and 0 <= nx < len(layout[0]):
                    if layout[ny][nx] != 'W' and (nx, ny) not in visited:
                        visited.add((nx, ny))
                        queue.append((nx, ny, dist + 1))
        return total_score

    def get_move(self, game_obj):

        x, y = self.grid_pos
        valid_moves = self.get_valid_moves((x, y), MAP_LAYOUT)
        if not valid_moves: return 0, 0

        best_move = None
        max_utility = -float('inf')

        are_ghosts_scared = False

        # Global Pusula
        nearest_food = None
        min_dist = float('inf')
        targets = game_obj.foods + game_obj.energies
        if targets:
            for t in targets:
                tx, ty = t.x // CELL_SIZE, t.y // CELL_SIZE
                d = abs(x - tx) + abs(y - ty)
                if d < min_dist: min_dist, nearest_food = d, (tx, ty)

        for dx, dy in valid_moves:
            nx, ny = x + dx, y + dy
            u = 0

            # 1. Zenginlik
            u += self.calculate_path_utility((nx, ny), game_obj.foods, game_obj.energies, MAP_LAYOUT) * 20

            # 2. Hafıza
            if (nx, ny) in self.memory:
                idx = self.memory.index((nx, ny))
                u -= (len(self.memory) - idx) * 2000

            # 3. Pusula
            if u < 100 and nearest_food:
                curr_d = abs(x - nearest_food[0]) + abs(y - nearest_food[1])
                new_d = abs(nx - nearest_food[0]) + abs(ny - nearest_food[1])
                if new_d < curr_d: u += 400

            min_ghost_dist = float('inf')  # En yakın hayalet için

            # 4. Hayaletler
            for ghost in game_obj.ghosts:
                gx, gy = ghost.grid_pos
                d_ghost = abs(nx - gx) + abs(ny - gy)

                if not ghost.is_scared and d_ghost < min_ghost_dist:
                    min_ghost_dist = d_ghost


                if ghost.is_scared:
                    if not ghost.is_scaringOver:
                        if d_ghost == 0:
                            u += 10000000
                        else:
                            # Mesafeye bölerek yaklaştıran yönü seç
                            u += 30000 / d_ghost
                else:
                    # Normal hayaletse kaç
                    if d_ghost <= 1:
                        u -= 500000
                    elif d_ghost < 3:
                        u -= 100000
                    elif d_ghost < 5:
                        u -= 2000

            # 5. Duvar Kontrolü
            walls = 0
            for wx, wy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
                if MAP_LAYOUT[ny + wy][nx + wx] == 'W': walls += 1
            if walls>= 2 and not are_ghosts_scared:
                if min_ghost_dist < 5:  # Hayalet yakındaysa
                    u -= 20000
                else:
                    # Hayalet yoksa bile çıkmaz sokağa girme
                    if walls == 3: u -= 1000

            if u > max_utility:
                max_utility = u
                best_move = (dx, dy)

        if best_move:
            self.direction = best_move
            self.memory.append((x + best_move[0], y + best_move[1]))
            if len(self.memory) > 6: self.memory.pop(0)
            return best_move
        return 0, 0


class Ghost:
    def __init__(self, x, y, color):
        self.grid_pos = [x, y]
        self.color = color
        self.timer = 0
        self.move_interval = 250  # ms
        self.is_scared = False
        self.is_scaringOver = False
        self.scared_timer = 0
        self.direction = (0, 0)
        self.lives = 1

    def make_scared(self):
        self.is_scared = True
        self.scared_timer = pygame.time.get_ticks()

    def update(self):
        # Korku süresi kontrolü (8 Saniye)
        if self.is_scared:
            if pygame.time.get_ticks() - self.scared_timer > 8000:
                self.is_scared = False

    def draw(self, screen):
        cx, cy = self.grid_pos[0] * CELL_SIZE + CELL_SIZE // 2, self.grid_pos[1] * CELL_SIZE + CELL_SIZE // 2

        # Renk Belirleme
        draw_color = SCARED_BLUE if self.is_scared else self.color
        if self.is_scared and (pygame.time.get_ticks() // 200) % 2 == 0 and (
                pygame.time.get_ticks() - self.scared_timer > 6000):
            draw_color = WHITE  # Sonlara doğru yanıp sönme efekti
            self.is_scaringOver = True

        # 1. Kafa
        radius = CELL_SIZE // 2 - 2
        pygame.draw.circle(screen, draw_color, (cx, cy - 4), radius)

        # 2. Gövde
        rect = pygame.Rect(cx - radius, cy - 4, radius * 2, radius + 4)
        pygame.draw.rect(screen, draw_color, rect)

        # 3. Ayaklar
        foot_r = radius // 3
        for i in range(3):
            fx = (cx - radius) + (i * 2 * foot_r) + foot_r
            fy = cy + radius
            pygame.draw.circle(screen, draw_color, (fx, int(fy)), foot_r)

        # 4. Gözler
        # Korkmuşsa şaşkın gözler, normalse Pacman'e bakan gözler
        eye_radius = 4
        pupil_radius = 2
        eye_offset_x = 6
        eye_offset_y = -6

        # Göz Beyazı
        pygame.draw.circle(screen, WHITE, (cx - eye_offset_x, cy + eye_offset_y), eye_radius)
        pygame.draw.circle(screen, WHITE, (cx + eye_offset_x, cy + eye_offset_y), eye_radius)

        # Göz Bebekleri (Yöne göre kayar)
        p_dx, p_dy = self.direction[0] * 2, self.direction[1] * 2
        pupil_color = BLUE
        if self.is_scared:
            pupil_color = WHITE
            p_dx, p_dy = 0, 0

        pygame.draw.circle(screen, pupil_color, (cx - eye_offset_x + p_dx, cy + eye_offset_y + p_dy), pupil_radius)
        pygame.draw.circle(screen, pupil_color, (cx + eye_offset_x + p_dx, cy + eye_offset_y + p_dy), pupil_radius)

    def bfs_chase(self, target_pos, layout):
        # BFS ile hedefi (Pacman) bul ve ilk adımı döndür
        start = tuple(self.grid_pos)
        target = tuple(target_pos)

        queue = [start]
        # Her dügümün nereden gelindigini tutar: parent[child] = parent
        parents = {start: None}

        found = False
        visited = {start}

        while queue:
            curr = queue.pop(0)
            if curr == target:
                found = True
                break

            cx, cy = curr
            for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
                nx, ny = cx + dx, cy + dy
                # Duvar kontrolü ve harita sınırı
                if 0 <= ny < len(layout) and 0 <= nx < len(layout[0]):
                    if layout[ny][nx] != 'W' and (nx, ny) not in visited:
                        visited.add((nx, ny))
                        parents[(nx, ny)] = curr
                        queue.append((nx, ny))

        if found:
            # Backtracking: Hedefen geriye doğru gelerek ilk hamleyi bul
            path_node = target
            while parents[path_node] != start:
                path_node = parents[path_node]
                if path_node is None: return (0, 0)  # Hata durumu


            return (path_node[0] - start[0], path_node[1] - start[1])

        return None  # Yol yoksa

    def move_logic(self, player_pos, layout):
        # Zamanlayıcı
        self.timer += 1000 / FPS  # Yaklaşık dt
        interval = self.move_interval
        if self.is_scared: interval = 400  # Korkunca yavaşla

        if self.timer >= interval:
            next_move = None

            if self.is_scared:
                # KORKU MODU: Rastgele kaçış
                directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]
                random.shuffle(directions)
                for dx, dy in directions:
                    nx, ny = self.grid_pos[0] + dx, self.grid_pos[1] + dy
                    if layout[ny][nx] != 'W':
                        next_move = (dx, dy)
                        break
            else:
                # NORMAL MOD: BFS ile Kovalama
                next_move = self.bfs_chase(player_pos, layout)
                # Eğer BFS yol bulamazsa (duvarlar kapalıysa) rastgele git
                if next_move is None:
                    directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]
                    random.shuffle(directions)
                    for dx, dy in directions:
                        if layout[self.grid_pos[1] + dy][self.grid_pos[0] + dx] != 'W':
                            next_move = (dx, dy);
                            break

            if next_move:
                self.grid_pos[0] += next_move[0]
                self.grid_pos[1] += next_move[1]
                self.direction = next_move

            self.timer = 0


# =============================================================================
# MODÜL 3: OYUN MOTORU (GAME ENGINE)
# =============================================================================

class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        create_beep_sound()
        try:
            self.eat_sound = pygame.mixer.Sound("beep.wav")
            self.eat_sound.set_volume(0.2)
        except:
            self.eat_sound = None

        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Pacman AI")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont('arial', 20)
        self.big_font = pygame.font.SysFont('arial', 40)

        self.running = True
        self.mode = None
        self.pacman = None
        self.ghosts = []
        self.foods = []
        self.energies = []
        self.walls = []

    def load_map(self):
        self.walls = []
        self.foods = []
        self.energies = []
        self.ghosts = []
        self.score = 0
        self.start_time = time.time()
        self.game_over = False
        self.win = False

        ghost_colors = [RED, CYAN, PINK, ORANGE]
        ghost_idx = 0

        for r, row in enumerate(MAP_LAYOUT):
            for c, char in enumerate(row):
                x, y = c * CELL_SIZE, r * CELL_SIZE
                if char == 'W':
                    self.walls.append(pygame.Rect(x, y, CELL_SIZE, CELL_SIZE))
                elif char == '.':
                    self.foods.append(pygame.Rect(x + 12, y + 12, 8, 8))
                elif char == 'o':
                    self.energies.append(pygame.Rect(x + 8, y + 8, 16, 16))
                elif char == 'P':
                    self.pacman = PacmanAgent(c, r)
                elif char == 'G':
                    color = ghost_colors[ghost_idx % 4]
                    self.ghosts.append(Ghost(c, r, color))
                    ghost_idx += 1

    def start(self):
        while self.running:
            self.menu()
            if self.running and self.mode:
                self.run_game()

    def menu(self):
        self.mode = None
        intro = True
        while intro and self.running:
            self.screen.fill(BLACK)
            self.draw_text_centered("PACMAN AI", -60, YELLOW)
            self.draw_text_centered("1: Insan Oyuncu", 10, WHITE)
            self.draw_text_centered("2: Yapay Zeka (AI)", 50, WHITE)
            self.draw_text_centered("Cikis: Pencereyi Kapat", 120, DARK_GRAY, size=20)
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False;
                    intro = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_1: self.mode = 'HUMAN'; intro = False
                    if event.key == pygame.K_2: self.mode = 'AI'; intro = False

    def run_game(self):
        self.load_map()
        move_timer = 0

        while self.running:
            dt = self.clock.tick(FPS)

            if not self.game_over:
                self.elapsed_time = time.time() - self.start_time

            mouse_pos = pygame.mouse.get_pos()
            mouse_click = False
            for event in pygame.event.get():
                if event.type == pygame.QUIT: self.running = False; return
                if event.type == pygame.MOUSEBUTTONDOWN: mouse_click = True

            if self.game_over:
                if self.draw_game_over(mouse_pos, mouse_click): return
                continue

            dx, dy = 0, 0
            if self.mode == 'HUMAN':
                move_timer += dt
                if move_timer > 100:
                    keys = pygame.key.get_pressed()
                    if keys[pygame.K_LEFT]:
                        dx = -1
                    elif keys[pygame.K_RIGHT]:
                        dx = 1
                    elif keys[pygame.K_UP]:
                        dy = -1
                    elif keys[pygame.K_DOWN]:
                        dy = 1
                    move_timer = 0
            elif self.mode == 'AI':
                move_timer += dt
                if move_timer > 200:  # AI Hızı
                    dx, dy = self.pacman.get_move(self)
                    move_timer = 0

            if dx != 0 or dy != 0:
                nx, ny = self.pacman.grid_pos[0] + dx, self.pacman.grid_pos[1] + dy
                if MAP_LAYOUT[ny][nx] != 'W':
                    self.pacman.grid_pos = [nx, ny]
                    self.pacman.direction = (dx, dy)


            px_rect = pygame.Rect(self.pacman.grid_pos[0] * CELL_SIZE, self.pacman.grid_pos[1] * CELL_SIZE, CELL_SIZE,
                                  CELL_SIZE)

            # 1. Yemek Yeme
            for f in self.foods[:]:
                if px_rect.colliderect(f):
                    self.foods.remove(f)
                    self.score += 10
                    if self.eat_sound: self.eat_sound.play()

            # 2. Enerji Topu Yeme
            for e in self.energies[:]:
                if px_rect.colliderect(e):
                    self.energies.remove(e)
                    self.score += 50
                    # Tüm hayaletleri korkut
                    for g in self.ghosts:
                        g.make_scared()
                    if self.eat_sound: self.eat_sound.play()

            # 3. KAZANMA KONTROLÜ
            if not self.foods and not self.energies:
                self.game_over = True
                self.win = True

            # 4. KAZANMA KONTROLÜ
            if not self.ghosts:
                self.game_over = True
                self.win = True
                self.score += 1000  # Bonus puan

            # 5. HAYALET HAREKETİ VE CAN SİSTEMİ
            for g in self.ghosts[:]:
                g.update()
                g.move_logic(self.pacman.grid_pos, MAP_LAYOUT)

                # Çarpışma Kontrolü
                if g.grid_pos == self.pacman.grid_pos:
                    if g.is_scared:
                        # --- HAYALET YENDİ ---
                        g.lives -= 1  # Canı azalt
                        self.score += 200  # Puan ver
                        if self.eat_sound: self.eat_sound.play()

                        if g.lives <= 0:
                            # Canı bittiyse sil
                            self.ghosts.remove(g)
                        else:
                            # Canı varsa merkeze ışınla
                            g.grid_pos = [9, 8]  # Haritanın ortası
                            g.is_scared = False  # Normale dön
                    else:
                        # --- PACMAN ÖLDÜ ---
                        self.game_over = True
                        self.win = False

            self.draw()

    def draw(self):
        self.screen.fill(BLACK)
        for w in self.walls: pygame.draw.rect(self.screen, BLUE, w)
        for f in self.foods: pygame.draw.circle(self.screen, (255, 182, 193), f.center, 3)
        # Enerji topu yanıp sönsün
        if (pygame.time.get_ticks() // 300) % 2 == 0:
            for e in self.energies: pygame.draw.circle(self.screen, WHITE, e.center, 7)
        else:
            for e in self.energies: pygame.draw.circle(self.screen, GREEN, e.center, 7)

        self.pacman.draw(self.screen)
        for g in self.ghosts: g.draw(self.screen)

        # UI
        sc = self.font.render(f"Skor: {self.score}", True, WHITE)
        tm = self.font.render(f"Sure: {int(self.elapsed_time)}s", True, WHITE)
        self.screen.blit(sc, (10, HEIGHT - 35));
        self.screen.blit(tm, (150, HEIGHT - 35))
        pygame.display.flip()

    def draw_text_centered(self, text, y_off, color, size=40):
        f = pygame.font.SysFont('arial', size)
        s = f.render(text, True, color)
        r = s.get_rect(center=(WIDTH // 2, HEIGHT // 2 + y_off))
        self.screen.blit(s, r)

    def draw_game_over(self, m_pos, click):
        s = pygame.Surface((WIDTH, HEIGHT));
        s.set_alpha(150);
        s.fill(BLACK)
        self.screen.blit(s, (0, 0))

        p_rect = pygame.Rect(WIDTH // 2 - 150, HEIGHT // 2 - 100, 300, 250)
        pygame.draw.rect(self.screen, DARK_GRAY, p_rect)
        pygame.draw.rect(self.screen, WHITE, p_rect, 2)

        msg, col = ("KAZANDIN!", GREEN) if self.win else ("KAYBETTIN!", RED)
        self.draw_text_centered(msg, -60, col)
        self.draw_text_centered(f"Skor: {self.score}", -10, WHITE, 25)

        self.draw_text_centered(f"Sure: {int(self.elapsed_time)}s", 20, WHITE, 25)

        b_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 50, 200, 50)
        hover = b_rect.collidepoint(m_pos)
        pygame.draw.rect(self.screen, BUTTON_HOVER if hover else BUTTON_COLOR, b_rect)
        pygame.draw.rect(self.screen, WHITE, b_rect, 2)

        t = self.font.render("ANA MENU", True, WHITE)
        self.screen.blit(t, t.get_rect(center=b_rect.center))
        pygame.display.flip()

        if hover and click: return True
        return False


# =============================================================================
# MAIN
# =============================================================================
if __name__ == "__main__":
    game = Game()
    game.start()
    pygame.quit()