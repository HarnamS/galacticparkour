import pygame, time, random

#  INIT & CONSTANTS 

pygame.init()
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
WHITE, BLACK, RED, GREEN, BLUE, ORANGE, PURPLE = (255,255,255), (0,0,0), (255,0,0), (0,255,0), (0,0,255), (255,165,0), (128,0,128)
DIFFICULTY_EASY, DIFFICULTY_MEDIUM, DIFFICULTY_HARD = 0, 1, 2
AIR_BOMB_SPAWN_INTERVAL = 5
PLAYER_WIDTH, PLAYER_HEIGHT = 50, 65  # Player hitbox and image size
PLAYER_SPEED_X, JUMP_STRENGTH, JUMP_PAD_BOOST, GRAVITY = 5, -15, -25, 1
PLATFORM_WIDTH, PLATFORM_HEIGHT, JUMP_PAD_WIDTH, JUMP_PAD_HEIGHT, LASER_WIDTH, LASER_HEIGHT, LASER_SPEED = 100, 20, 50, 20, 20, 5, 10

#  PYGAME WINDOW & FONTS 
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Galactic Parkour")
font = pygame.font.Font("coolepicfont.ttf", 36)
title_font = pygame.font.Font("coolepicfont.ttf", 64)
small_font = pygame.font.Font("coolepicfont.ttf", 24)

#  IMAGE LOADING HELPERS 
def load_img(name, size=None, flip=False):
    img = pygame.image.load(name)
    if size: img = pygame.transform.scale(img, size)
    if flip: img = pygame.transform.flip(img, True, False)
    return img

def load_spritesheet(filename):
    sheet = pygame.image.load(filename).convert_alpha()
    # Sprite frame coordinates for each animation frame
    coords = [
        (31, 15, 94, 100),    # frame 1 (index 0)
        (156, 15, 218, 100),  # frame 2 (index 1)
        (31, 140, 94, 227),   # frame 3 (index 2)
        (164, 133, 226, 226), # frame 4 (index 3)
        (30, 265, 94, 350),   # frame 6 (index 4)
        (156, 265, 218, 350), # frame 7 (index 5)
        (281, 265, 344, 350), # frame 8 (index 6)
    ]
    frames = []
    for x1, y1, x2, y2 in coords:
        frame = sheet.subsurface(pygame.Rect(x1, y1, x2 - x1, y2 - y1))
        frame = pygame.transform.scale(frame, (PLAYER_WIDTH, PLAYER_HEIGHT))
        frames.append(frame)
    return frames

#  LOAD SOUNDS & IMAGES 
laser_sound = pygame.mixer.Sound("lazer.mp3")
explosion_sound = pygame.mixer.Sound("explosion.mp3")

background_image = load_img("spacebackground.jpg", (SCREEN_WIDTH, SCREEN_HEIGHT))
menu_background = background_image.copy()
block_image = load_img("block.png", (PLATFORM_WIDTH, PLATFORM_HEIGHT))
jump_pad_image = load_img("jumppad.png", (JUMP_PAD_WIDTH, JUMP_PAD_HEIGHT))
portal_image = load_img("portal.png", (75,75))
air_bomb_image = load_img("airspike.png", (30,30))
red_laser_gun_image = load_img("redlazergun.png", (75,85))
red_laser_gun_image_flipped = load_img("redlazergun.png", (75,85), True)
explosion_image = load_img("explosion.png")
wasd_image = load_img("wasd.png", (150,100))
arrows_image = load_img("arrows.png", (150,100))

#  SPRITESHEETS & ANIMATION FRAMES 
player1_all_frames = load_spritesheet("player1.png")
player2_all_frames = load_spritesheet("player2.png")

# Animation frame indices for each state
JUMP_ANIM = [0, 1, 0]
WALK_ANIM = [2, 3, 2]
IDLE_ANIM = [4, 5, 6, 5, 4]  # frames 6,7,8,7,6

player1_frames = {
    "jump": [player1_all_frames[i] for i in JUMP_ANIM],
    "walk": [player1_all_frames[i] for i in WALK_ANIM],
    "idle": [player1_all_frames[i] for i in IDLE_ANIM]
}
player2_frames = {
    "jump": [player2_all_frames[i] for i in JUMP_ANIM],
    "walk": [player2_all_frames[i] for i in WALK_ANIM],
    "idle": [player2_all_frames[i] for i in IDLE_ANIM]
}

# level layout
def gun(rect, direction, image): return {"rect": pygame.Rect(*rect), "direction": direction, "image": image}
def plat(x, y): return pygame.Rect(x, y, PLATFORM_WIDTH, PLATFORM_HEIGHT)
def jpad(x, y): return pygame.Rect(x, y, JUMP_PAD_WIDTH, JUMP_PAD_HEIGHT)
levels = [
    {"platforms":[plat(200,520),plat(400,420),plat(600,370),plat(675,220)],"jump_pad":jpad(625,350),"goal":(650,70),"guns":[gun((100,460,75,75),'right',red_laser_gun_image_flipped)]},
    {"platforms":[plat(100,500),plat(300,400),plat(500,300),plat(700,210)],"jump_pad":jpad(350,380),"goal":(700,90),"guns":[gun((700,220,75,75),'left',red_laser_gun_image)]},
    {"platforms":[plat(150,520),plat(350,420),plat(550,320)],"jump_pad":jpad(600,300),"goal":(700,70),"guns":[gun((50,460,75,75),'right',red_laser_gun_image_flipped)]},
    {"platforms":[plat(100,510),plat(300,430),plat(500,350),plat(700,270),plat(400,240)],"jump_pad":jpad(350,410),"goal":(400,110),"guns":[gun((700,280,75,75),'left',red_laser_gun_image)]},
    {"platforms":[plat(50,510),plat(250,410),plat(450,310),plat(600,350),plat(350,160)],"jump_pad":jpad(600,330),"goal":(400,60),"guns":[gun((10,410,75,75),'right',red_laser_gun_image_flipped)]},
    {"platforms":[plat(250,510),plat(400,430),plat(600,350),plat(400,270),plat(200,190)],"jump_pad":jpad(250,490),"goal":(250,60),"guns":[gun((700,350,75,75),'left',red_laser_gun_image)]},
    {"platforms":[plat(100,510),plat(300,450),plat(500,390),plat(400,290),plat(550,190),plat(575,580)],"jump_pad":jpad(600,560),"goal":(700,60),"guns":[gun((50,450,75,75),'right',red_laser_gun_image_flipped),gun((700,200,75,75),'left',red_laser_gun_image)]},
    {"platforms":[plat(50,510),plat(250,440),plat(450,370),plat(650,300),plat(350,270),plat(150,230),plat(575,580)],"jump_pad":jpad(600,560),"goal":(150,130),"guns":[gun((700,320,75,75),'left',red_laser_gun_image),gun((25,200,75,75),'right',red_laser_gun_image_flipped)]},
    {"platforms":[plat(200,510),plat(400,420),plat(600,330),plat(300,240),plat(100,150),plat(500,240)],"jump_pad":jpad(550,220),"goal":(150,60),"guns":[gun((50,420,75,75),'right',red_laser_gun_image_flipped),gun((50,180,75,75),'right',red_laser_gun_image_flipped)]}
]
tutorial_level = {"platforms":[plat(200,510),plat(400,410)],"jump_pad":jpad(450,390),"goal":(SCREEN_WIDTH//2,110),"guns":[gun((100,460,75,75),'right',red_laser_gun_image_flipped)]}

current_level, current_difficulty, game_mode, player_points = 0, DIFFICULTY_EASY, None, 0

#  GAME CLASSES 
class Explosion:
    # Handles explosion animation for player death
    def __init__(self, x, y): self.x, self.y, self.size, self.max_size, self.growth_rate, self.active = x, y, 10, 100, 20, True
    def update(self): self.size += self.growth_rate; self.active = self.size < self.max_size
    def draw(self, screen): screen.blit(pygame.transform.scale(explosion_image, (self.size, self.size)), (self.x-self.size//2, self.y-self.size//2)) if explosion_image else pygame.draw.circle(screen, ORANGE, (self.x, self.y), self.size//2)

class Laser:
    # Laser projectiles shot by guns
    def __init__(self, x, y, direction): self.x, self.y, self.direction, self.width, self.height, self.speed, self.rect = x-10, y-12, direction, LASER_WIDTH, LASER_HEIGHT, LASER_SPEED, pygame.Rect(x-10, y-12, LASER_WIDTH, LASER_HEIGHT)
    def update(self): self.x += self.speed if self.direction=="right" else -self.speed; self.rect.x = self.x
    def draw(self, screen): pygame.draw.rect(screen, RED, (self.x, self.y, self.width, self.height))
    def is_off_screen(self): return self.x < 0 or self.x > SCREEN_WIDTH

class AirBomb:
    # Moving bomb hazards
    def __init__(self, x, y): self.x, self.y, self.rect, self.speed, self.direction = x, y, pygame.Rect(x, y, 30, 30), 2, random.choice([-1, 1])
    def update(self): self.x += self.speed * self.direction; self.rect.x = self.x; self.direction *= -1 if self.x <= 0 or self.x >= SCREEN_WIDTH - 30 else 1
    def draw(self, screen): screen.blit(air_bomb_image, (self.x, self.y)) if air_bomb_image else pygame.draw.rect(screen, RED, self.rect)

class Player:
    # Main player class, handles movement, animation, collisions, etc.
    def __init__(self, x, y, animations):
        self.x, self.y = x, y
        self.animations = animations
        self.state = "idle"
        self.frame_idx = 0
        self.frame_timer = 0
        self.frame_rate = {"idle": 0.35, "walk": 0.15, "jump": 0.15}  # idle slower
        self.speed_y, self.on_ground = 0, False
        self.rect = pygame.Rect(x - PLAYER_WIDTH // 2, y - PLAYER_HEIGHT // 2, PLAYER_WIDTH, PLAYER_HEIGHT)
        self.explosion, self.has_scored, self.just_died = None, False, False

    def set_state(self, moving, jumping):
        # Switch animation state
        if jumping:
            if self.state != "jump":
                self.state = "jump"
                self.frame_idx = 0
                self.frame_timer = 0
        elif moving:
            if self.state != "walk":
                self.state = "walk"
                self.frame_idx = 0
                self.frame_timer = 0
        else:
            if self.state != "idle":
                self.state = "idle"
                self.frame_idx = 0
                self.frame_timer = 0

    def animate(self):
        # Advance animation frame
        self.frame_timer += 1/60  # assuming 60 FPS
        frames = self.animations[self.state]
        rate = self.frame_rate[self.state]
        if self.frame_timer >= rate:
            self.frame_idx = (self.frame_idx + 1) % len(frames)
            self.frame_timer = 0

    def move(self, keys, left_key, right_key, jump_key):
        # Handle player movement and state
        moving = False
        if keys[left_key]: self.x -= PLAYER_SPEED_X; moving = True
        if keys[right_key]: self.x += PLAYER_SPEED_X; moving = True
        jumping = not self.on_ground or (keys[jump_key] and self.on_ground)
        if keys[jump_key] and self.on_ground: self.speed_y, self.on_ground = JUMP_STRENGTH, False
        self.set_state(moving, jumping)
        self.rect.x, self.rect.y = self.x - PLAYER_WIDTH // 2, self.y - PLAYER_HEIGHT // 2

    def apply_gravity(self): self.speed_y += GRAVITY; self.y += self.speed_y; self.rect.y = self.y - PLAYER_HEIGHT // 2

    def check_collisions(self, platforms, guns, other_player=None):
        # Collisions with platforms, guns, and other player
        self.on_ground = False
        if other_player and not (self.has_scored or other_player.has_scored) and self.rect.colliderect(other_player.rect):
            self.x = other_player.x - PLAYER_WIDTH if self.x < other_player.x else other_player.x + PLAYER_WIDTH
            self.rect.x = self.x - PLAYER_WIDTH // 2
        def handle_side_collision(rect):
            dx_left, dx_right, dy_top, dy_bottom = self.rect.right - rect.left, rect.right - self.rect.left, self.rect.bottom - rect.top, rect.bottom - self.rect.top
            min_dx, min_dy = min(dx_left, dx_right), min(dy_top, dy_bottom)
            if min_dx < min_dy:
                self.x = rect.left - PLAYER_WIDTH // 2 if dx_left < dx_right else rect.right + PLAYER_WIDTH // 2
                self.rect.x = self.x - PLAYER_WIDTH // 2
            else:
                if self.speed_y > 0 and self.rect.bottom > rect.top and self.rect.top < rect.top:
                    self.y, self.speed_y, self.on_ground = rect.top - PLAYER_HEIGHT // 2, 0, True
                elif self.speed_y < 0 and self.rect.top < rect.bottom and self.rect.bottom > rect.bottom:
                    self.y, self.speed_y = rect.bottom + PLAYER_HEIGHT // 2, 0
                self.rect.y = self.y - PLAYER_HEIGHT // 2
        for gun in guns:
            if self.rect.colliderect(gun["rect"]): handle_side_collision(gun["rect"])
        for platform in platforms:
            if self.rect.colliderect(platform): handle_side_collision(platform)
        self.rect.x, self.rect.y = self.x - PLAYER_WIDTH // 2, self.y - PLAYER_HEIGHT // 2

    def check_jump_pad(self, jump_pad):
        # Jump pad collision
        if self.rect.colliderect(jump_pad):
            if self.speed_y > 0 and self.rect.bottom > jump_pad.top and self.rect.top < jump_pad.top:
                self.speed_y, self.on_ground = JUMP_PAD_BOOST, False
            elif self.rect.right > jump_pad.left and self.rect.left < jump_pad.left:
                self.x, self.speed_y, self.on_ground = jump_pad.left - PLAYER_WIDTH // 2, JUMP_PAD_BOOST, False
            elif self.rect.left < jump_pad.right and self.rect.right > jump_pad.right:
                self.x, self.speed_y, self.on_ground = jump_pad.right + PLAYER_WIDTH // 2, JUMP_PAD_BOOST, False

    def check_floor_collision(self):
        # Prevent falling through floor
        if self.rect.bottom > SCREEN_HEIGHT:
            self.y, self.speed_y, self.on_ground, self.rect.y = SCREEN_HEIGHT - PLAYER_HEIGHT // 2, 0, True, SCREEN_HEIGHT - PLAYER_HEIGHT // 2

    def check_walls(self):
        # Prevent going off screen
        if self.rect.left < 0: self.x, self.rect.x = PLAYER_WIDTH // 2, 0
        if self.rect.right > SCREEN_WIDTH: self.x, self.rect.right = SCREEN_WIDTH - PLAYER_WIDTH // 2, SCREEN_WIDTH
        if self.rect.top < 0: self.y, self.rect.top, self.speed_y = PLAYER_HEIGHT // 2, 0, 0

    def check_laser_collision(self, lasers):
        # Laser collision
        for laser in lasers[:]:
            if self.rect.colliderect(laser.rect) and not self.just_died:
                self.explosion, self.just_died = Explosion(self.x, self.y), True
                if explosion_sound: explosion_sound.play()
                self.x -= 10
                return True
        return False

    def check_bomb_collision(self, bombs):
        # Bomb collision
        for bomb in bombs[:]:
            if self.rect.colliderect(bomb.rect) and not self.just_died:
                self.explosion, self.just_died = Explosion(self.x, self.y), True
                if explosion_sound: explosion_sound.play()
                self.x -= 10
                return True
        return False

    def draw(self, screen):
        # Draw player or explosion
        if self.explosion:
            self.explosion.update(); self.explosion.draw(screen)
            if not self.explosion.active: self.just_died = False; return False
            return True
        else:
            self.animate()
            frame = self.animations[self.state][self.frame_idx]
            screen.blit(frame, (self.x - PLAYER_WIDTH // 2, self.y - PLAYER_HEIGHT // 2))
            return True

class Button:
    # Simple button class for menus
    def __init__(self, text, x, y, width=325, height=50, color=BLUE, hover_color=GREEN, action=None, difficulty=None):
        self.text, self.rect, self.color, self.hover_color, self.action, self.difficulty = text, pygame.Rect(x, y, width, height), color, hover_color, action, difficulty
    def draw(self, screen):
        mouse_pos, mouse_click = pygame.mouse.get_pos(), pygame.mouse.get_pressed()
        pygame.draw.rect(screen, self.hover_color if self.rect.collidepoint(mouse_pos) else self.color, self.rect)
        if self.rect.collidepoint(mouse_pos) and mouse_click[0] == 1 and self.action is not None:
            return self.action(self.difficulty) if self.difficulty is not None else self.action()
        text_surface = font.render(self.text, True, WHITE)
        screen.blit(text_surface, (self.rect.x + (self.rect.width - text_surface.get_width()) // 2, self.rect.y + (self.rect.height - text_surface.get_height()) // 2))
        return None

#  MENU & GAME STATE 
def single_player_action(difficulty=None): global game_mode, current_difficulty; game_mode = 1; current_difficulty = difficulty if difficulty is not None else current_difficulty; return True
def two_player_action(difficulty=None): global game_mode, current_difficulty; game_mode = 2; current_difficulty = difficulty if difficulty is not None else current_difficulty; return True
def tutorial_action(): global game_mode; game_mode = 0; return True
def restart_game(): global current_level, player_points, start_time, lasers, last_shot_time, game_mode, air_bombs; current_level, player_points, start_time, lasers, last_shot_time, air_bombs, game_mode = 0, 0, time.time(), [], 0, [], None; return True
def return_to_menu(): global game_mode; game_mode = None; return False

def show_menu():
    # Main menu and difficulty selection
    global current_difficulty
    bw, bx = 375, SCREEN_WIDTH//2-375//2
    single_btn = Button("Single Player", bx, 200, bw)
    two_btn = Button("Two Player", bx, 270, bw)
    tut_btn = Button("Tutorial", bx, 340, bw, action=tutorial_action)
    bw, bx = 250, SCREEN_WIDTH//2-250//2
    easy_btn = Button("Easy", bx, 250, bw, color=GREEN, hover_color=BLUE, action=single_player_action, difficulty=DIFFICULTY_EASY)
    med_btn = Button("Medium", bx, 320, bw, color=ORANGE, hover_color=BLUE, action=single_player_action, difficulty=DIFFICULTY_MEDIUM)
    hard_btn = Button("Hard", bx, 390, bw, color=RED, hover_color=BLUE, action=single_player_action, difficulty=DIFFICULTY_HARD)
    back_btn = Button("Back", bx, 460, bw, color=PURPLE, hover_color=BLUE, action=return_to_menu)
    t_easy_btn = Button("Easy", bx, 250, bw, color=GREEN, hover_color=BLUE, action=two_player_action, difficulty=DIFFICULTY_EASY)
    t_med_btn = Button("Medium", bx, 320, bw, color=ORANGE, hover_color=BLUE, action=two_player_action, difficulty=DIFFICULTY_MEDIUM)
    t_hard_btn = Button("Hard", bx, 390, bw, color=RED, hover_color=BLUE, action=two_player_action, difficulty=DIFFICULTY_HARD)
    t_back_btn = Button("Back", bx, 460, bw, color=PURPLE, hover_color=BLUE, action=return_to_menu)
    menu_state = "main"
    while True:
        if menu_background: screen.blit(menu_background, (0, 0))
        else: screen.fill(BLACK)
        title_text = title_font.render("GALACTIC PARKOUR", True, WHITE)
        screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 80))
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if menu_state == "main":
                    if single_btn.rect.collidepoint(event.pos): menu_state = "difficulty_single"
                    elif two_btn.rect.collidepoint(event.pos): menu_state = "difficulty_two"
                    elif tut_btn.rect.collidepoint(event.pos):
                        result = tut_btn.draw(screen)
                        if result: return game_mode
        if menu_state == "main":
            single_btn.draw(screen); two_btn.draw(screen); tut_btn.draw(screen)
        elif menu_state == "difficulty_single":
            screen.blit(font.render("SELECT DIFFICULTY", True, WHITE), (SCREEN_WIDTH // 2 - 225, 150))
            result = easy_btn.draw(screen) or med_btn.draw(screen) or hard_btn.draw(screen) or back_btn.draw(screen)
            if result is not None: return game_mode if result else menu_state == "main"
        elif menu_state == "difficulty_two":
            screen.blit(font.render("SELECT DIFFICULTY", True, WHITE), (SCREEN_WIDTH // 2 - 225, 150))
            result = t_easy_btn.draw(screen) or t_med_btn.draw(screen) or t_hard_btn.draw(screen) or t_back_btn.draw(screen)
            if result is not None: return game_mode if result else menu_state == "main"
        pygame.display.flip()
        if game_mode is not None: return game_mode

def show_win_screen():
    # Win screen after all levels
    win_btn = Button("Main Menu", SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 + 100, 300, 50, color=GREEN, hover_color=BLUE, action=restart_game)
    while True:
        if menu_background: screen.blit(menu_background, (0, 0))
        else: screen.fill(BLACK)
        win_text = title_font.render("CONGRATULATIONS!", True, GREEN)
        win_text2 = font.render("You completed all levels!", True, GREEN)
        points_text = font.render(f"Total Points: {player_points}", True, GREEN)
        screen.blit(win_text, (SCREEN_WIDTH // 2 - win_text.get_width() // 2, SCREEN_HEIGHT // 2 - 100))
        screen.blit(win_text2, (SCREEN_WIDTH // 2 - win_text2.get_width() // 2, SCREEN_HEIGHT // 2 - 40))
        screen.blit(points_text, (SCREEN_WIDTH // 2 - points_text.get_width() // 2, SCREEN_HEIGHT // 2 + 20))
        if win_btn.draw(screen): return
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); exit()

def game_loop(two_player=False, tutorial=False):
    # Main game loop
    global current_level, player_points, start_time, lasers, last_shot_time, air_bombs, air_bomb_spawn_timer
    clock = pygame.time.Clock()
    player1 = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT - PLAYER_HEIGHT // 2 - 10, player1_frames)
    player2 = Player(SCREEN_WIDTH // 4, SCREEN_HEIGHT - PLAYER_HEIGHT // 2 - 10, player2_frames) if two_player else None
    player1_finished = player2_finished = False
    lasers, air_bombs, last_shot_time, air_bomb_spawn_timer = [], [], 0, 0
    start_time = time.time()
    tutorial_air_bomb_spawned = False
    show_controls, controls_start_time = True, time.time()
    while True:
        current_time = time.time()
        if background_image: screen.blit(background_image, (0, 0))
        else: screen.fill(BLACK)
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); return
        if show_controls and current_time - controls_start_time < 2:
            screen.blit(wasd_image, (player1.x - wasd_image.get_width()//2, player1.y - wasd_image.get_height() - 20))
            if two_player: screen.blit(arrows_image, (player2.x - arrows_image.get_width()//2, player2.y - arrows_image.get_height() - 20))
        else: show_controls = False
        keys = pygame.key.get_pressed()
        if not player1_finished:
            player_alive = player1.draw(screen)
            if not player_alive:
                player1 = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT - PLAYER_HEIGHT // 2 - 10, player1_frames)
                player1.has_scored = False
                continue
            player1.move(keys, pygame.K_a, pygame.K_d, pygame.K_w)
            player1.apply_gravity()
            if tutorial:
                player1.check_collisions(tutorial_level["platforms"], tutorial_level["guns"], player2 if two_player else None)
                player1.check_jump_pad(tutorial_level["jump_pad"])
            else:
                if current_level < len(levels):
                    player1.check_collisions(levels[current_level]["platforms"], levels[current_level]["guns"], player2 if two_player else None)
                    player1.check_jump_pad(levels[current_level]["jump_pad"])
                else:
                    show_win_screen(); return
            player1.check_floor_collision(); player1.check_walls()
        if two_player and not player2_finished:
            player_alive = player2.draw(screen)
            if not player_alive:
                player2 = Player(SCREEN_WIDTH // 4, SCREEN_HEIGHT - PLAYER_HEIGHT // 2 - 10, player2_frames)
                player2.has_scored = False
                continue
            player2.move(keys, pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP)
            player2.apply_gravity()
            if current_level < len(levels):
                player2.check_collisions(levels[current_level]["platforms"], levels[current_level]["guns"], player1)
                player2.check_jump_pad(levels[current_level]["jump_pad"])
            player2.check_floor_collision(); player2.check_walls()
        # Air bombs
        if tutorial:
            if not tutorial_air_bomb_spawned and len(air_bombs) == 0:
                air_bombs.append(AirBomb(random.randint(0, SCREEN_WIDTH - 30), random.randint(50, SCREEN_HEIGHT - 200)))
                tutorial_air_bomb_spawned = True
        elif not tutorial and (current_difficulty in [DIFFICULTY_MEDIUM, DIFFICULTY_HARD]):
            # Bomb limit logic for medium/hard
            bomb_limit = 10 if current_difficulty == DIFFICULTY_MEDIUM else 20 if current_difficulty == DIFFICULTY_HARD else 0
            spawn_interval = AIR_BOMB_SPAWN_INTERVAL * (2 if current_difficulty == DIFFICULTY_MEDIUM else 1)
            if (bomb_limit == 0 or len(air_bombs) < bomb_limit) and current_time - air_bomb_spawn_timer > spawn_interval:
                air_bombs.append(AirBomb(random.randint(0, SCREEN_WIDTH - 30), random.randint(50, SCREEN_HEIGHT - 200)))
                air_bomb_spawn_timer = current_time
        for bomb in air_bombs[:]:
            bomb.update(); bomb.draw(screen)
            if not player1_finished and player1.check_bomb_collision([bomb]): air_bombs.remove(bomb); continue
            if two_player and not player2_finished and player2.check_bomb_collision([bomb]): air_bombs.remove(bomb); continue
        if not player1_finished and player1.check_laser_collision(lasers): continue
        if two_player and not player2_finished and player2.check_laser_collision(lasers): continue
        # Goal
        if tutorial: goal_x, goal_y = tutorial_level["goal"]
        elif current_level < len(levels): goal_x, goal_y = levels[current_level]["goal"]
        else: show_win_screen(); return
        if not player1_finished and ((player1.x - goal_x) ** 2 + (player1.y - goal_y) ** 2) ** 0.5 < PLAYER_WIDTH // 2 + 20:
            player1_finished = True
            if not player1.has_scored:
                time_bonus = max(0, 60 - (current_time - start_time))
                player_points += int(time_bonus * [1, 1.5, 2][current_difficulty])
                player1.has_scored = True
        if two_player and not player2_finished and ((player2.x - goal_x) ** 2 + (player2.y - goal_y) ** 2) ** 0.5 < PLAYER_WIDTH // 2 + 20:
            player2_finished = True
            if not player2.has_scored:
                time_bonus = max(0, 60 - (current_time - start_time))
                player_points += int(time_bonus * [1, 1.5, 2][current_difficulty])
                player2.has_scored = True
        if player1_finished and (not two_player or player2_finished):
            if tutorial or current_level + 1 >= len(levels): show_win_screen(); return
            current_level += 1
            player1 = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT - PLAYER_HEIGHT // 2 - 10, player1_frames)
            if two_player: player2 = Player(SCREEN_WIDTH // 4, SCREEN_HEIGHT - PLAYER_HEIGHT // 2 - 10, player2_frames)
            player1_finished = player2_finished = False
            start_time = time.time()
            lasers = []
            air_bombs = []
            last_shot_time = 0
            air_bomb_spawn_timer = 0
            show_controls, controls_start_time = True, time.time()
        # Lasers
        if current_time - last_shot_time > 2:
            shoot_laser = random.random() < [0.7, 0.85, 1][current_difficulty]
            if shoot_laser:
                guns = tutorial_level["guns"] if tutorial else levels[current_level]["guns"] if current_level < len(levels) else []
                for gun in guns:
                    if random.random() < 0.7:
                        gun_rect, direction = gun["rect"], gun["direction"]
                        x = gun_rect.x + gun_rect.width if direction == "right" else gun_rect.x
                        lasers.append(Laser(x, gun_rect.y + gun_rect.height // 2, direction))
                        if laser_sound: laser_sound.play()
                last_shot_time = current_time
        for laser in lasers[:]:
            laser.update(); laser.draw(screen)
            if laser.is_off_screen(): lasers.remove(laser)
        # Draw elements
        if tutorial:
            goal_x, goal_y = tutorial_level["goal"]
            screen.blit(portal_image, (goal_x - 20, goal_y - 20))
            if ((player1.x - goal_x) ** 2 + (player1.y - goal_y) ** 2) ** 0.5 < 400:
                portal_text = small_font.render("I'm the Goal!", True, WHITE)
                text_x = max(10, min(goal_x - portal_text.get_width() // 2, SCREEN_WIDTH - portal_text.get_width() - 10))
                text_y = max(10, goal_y - 50)
                screen.blit(portal_text, (text_x, text_y))
            for rect in tutorial_level["platforms"]:
                screen.blit(block_image, (rect.x, rect.y))
                if ((player1.x - (rect.x + rect.width/2)) ** 2 + (player1.y - rect.y) ** 2) ** 0.5 < 100:
                    platform_text = small_font.render("Stand on ME!", True, WHITE)
                    text_x = max(10, min(rect.x, SCREEN_WIDTH - platform_text.get_width() - 10))
                    text_y = max(10, rect.y - 30)
                    screen.blit(platform_text, (text_x, text_y))
            screen.blit(jump_pad_image, (tutorial_level["jump_pad"].x, tutorial_level["jump_pad"].y))
            jp = tutorial_level["jump_pad"]
            if ((player1.x - (jp.x + jp.width/2)) ** 2 + (player1.y - jp.y) ** 2) ** 0.5 < 100:
                jump_pad_text = small_font.render("Jump on me!", True, WHITE)
                text_x = max(10, min(jp.x, SCREEN_WIDTH - jump_pad_text.get_width() - 10))
                text_y = max(10, jp.y - 30)
                screen.blit(jump_pad_text, (text_x, text_y))
            for gun in tutorial_level["guns"]:
                gun_rect, gun_image = gun["rect"], gun["image"]
                screen.blit(gun_image, (gun_rect.x, gun_rect.y))
                if ((player1.x - (gun_rect.x + gun_rect.width/2)) ** 2 + (player1.y - (gun_rect.y + gun_rect.height/2)) ** 2) ** 0.5 < 100:
                    gun_text = small_font.render("Avoid the lasers!", True, WHITE)
                    text_x = max(10, min(gun_rect.x, SCREEN_WIDTH - gun_text.get_width() - 10))
                    text_y = max(10, gun_rect.y - 30)
                    screen.blit(gun_text, (text_x, text_y))
            for bomb in air_bombs:
                bomb.draw(screen)
                if ((player1.x - (bomb.x + 15)) ** 2 + (player1.y - (bomb.y + 32)) ** 2) ** 0.5 < 400:
                    bomb_text = small_font.render("Don't touch me!", True, WHITE)
                    text_x = max(10, min(bomb.x, SCREEN_WIDTH - bomb_text.get_width() - 10))
                    text_y = max(10, bomb.y - 30)
                    screen.blit(bomb_text, (text_x, text_y))
        elif current_level < len(levels):
            screen.blit(portal_image, (goal_x - 20, goal_y - 20))
            for rect in levels[current_level]["platforms"]:
                screen.blit(block_image, (rect.x, rect.y))
            screen.blit(jump_pad_image, (levels[current_level]["jump_pad"].x, levels[current_level]["jump_pad"].y))
            for gun in levels[current_level]["guns"]:
                gun_rect, gun_image = gun["rect"], gun["image"]
                screen.blit(gun_image, (gun_rect.x, gun_rect.y))
        points_text = font.render(f"Points: {player_points}", True, WHITE)
        level_text = font.render(f"Level: {current_level + 1 if current_level < len(levels) else 'COMPLETE'}", True, WHITE)
        time_text = font.render(f"Time: {current_time - start_time:.1f}s", True, WHITE)
        difficulty_text = font.render(f"Difficulty: {['Easy', 'Medium', 'Hard'][current_difficulty]}", True, WHITE)
        right_margin = SCREEN_WIDTH - 10
        screen.blit(points_text, (right_margin - points_text.get_width(), 10))
        screen.blit(level_text, (right_margin - level_text.get_width(), 50))
        screen.blit(time_text, (10, 10))
        screen.blit(difficulty_text, (10, 50))
        pygame.display.flip(); clock.tick(60)

#  MAIN LOOP 
while True:
    mode = show_menu()
    if mode is not None:
        game_loop(two_player=(mode == 2), tutorial=(mode == 0))
