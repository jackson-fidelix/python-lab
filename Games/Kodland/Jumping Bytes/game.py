import pgzrun
import random
from pygame import Rect

WIDTH = 800
HEIGHT = 600
TITLE = "Jumping Bytes"

# Game state
game_started = False
paused = False
sound_on = True
game_over = False
game_won = False


# Actors
hero = Actor("hero/hero_idle1", (100, 500), anchor=('center', 'bottom'))
enemies = [
    Actor("enemy/skeleton_idle1", (300, 550), anchor=('center', 'bottom'))
]
INITIAL_ENEMIES = enemies.copy()
for enemy in enemies:
    enemy.frame_index = 0
    enemy.anim_timer = 0
    enemy.vx = 1
    enemy.initial_x = enemy.x
    enemy.patrol_range = 100

# Animations
hero_idle_frames = ["hero_idle1", "hero_idle2", "hero_idle3"]
hero_walk_frames = ["hero_walk1", "hero_walk2", "hero_walk3"]
hero_frame_index = 0
hero_anim_timer = 0
hero.vx = 0
hero.vy = 0
hero.on_ground = True
gravity = 1
jump_strength = -18
move_speed = 5


skeleton_idle_frames = ["skeleton_idle1", "skeleton_idle2", "skeleton_idle3"]
skeleton_walk_frames = ["skeleton_walk1", "skeleton_walk2"]

def update_enemies():
    for enemy in enemies:
        enemy.x += enemy.vx
        if abs(enemy.x - enemy.initial_x) > enemy.patrol_range:
            enemy.vx = -enemy.vx
            enemy.flip_x = enemy.vx < 0
        enemy.anim_timer += 1
        if enemy.anim_timer >= 25:
            if enemy == enemies[0]:
                frames = skeleton_walk_frames if enemy.vx != 0 else skeleton_idle_frames
            else:
                frames = skeleton_walk_frames if enemy.vx != 0 else skeleton_idle_frames
            enemy.frame_index = (enemy.frame_index + 1) % len(frames)
            enemy.image = f"enemy/{frames[enemy.frame_index]}"
            enemy.anim_timer = 0

# Menu buttons
buttons = {
    "start": Rect((300, 200), (200, 50)),
    "sound": Rect((300, 270), (200, 50)),
    "exit": Rect((300, 340), (200, 50))
}

music.set_volume(0.5)

def draw():
    try:
        screen.blit("accessories/background", (0, 0))
    except:
        print("Erro ao carregar o fundo")
        screen.fill((0, 0, 0))
    hero.draw()
    for enemy in enemies:
        enemy.draw()
    if not game_started:
        draw_menu()
    else:
        draw_game()

def draw_menu():
    screen.draw.filled_rect(Rect((0, 0), (WIDTH, HEIGHT)), (225, 205, 0))
    screen.draw.text("Jumping Bytes", center=(WIDTH//2, 100), fontsize=60, color="white")
    screen.draw.filled_rect(buttons["start"], "darkgreen")
    screen.draw.text("Start Game", center=buttons["start"].center, fontsize=30, color="white")
    screen.draw.filled_rect(buttons["sound"], "darkblue")
    text = "Sound: ON" if sound_on else "Sound: OFF"
    screen.draw.text(text, center=buttons["sound"].center, fontsize=30, color="white")
    screen.draw.filled_rect(buttons["exit"], "darkred")
    screen.draw.text("Exit", center=buttons["exit"].center, fontsize=30, color="white")
    screen.draw.text("Type P for everytime for 'pause' the game", center=(WIDTH//2, 450), fontsize=30, color="black")
    

def draw_game():
    if paused:
        screen.draw.text("PAUSED", center=(WIDTH//2, HEIGHT//2), fontsize=60, color="yellow")
    elif game_over:
        screen.draw.text("GAME OVER", center=(WIDTH//2, HEIGHT//2), fontsize=60, color="red")
        screen.draw.text("Pressione Enter para voltar ao menu", center=(WIDTH//2, HEIGHT//2 + 50), fontsize=30, color="white")
    elif game_won:
        screen.draw.text("🎉 PARABÉNS! VOCÊ VENCEU! 🎉", center=(WIDTH//2, HEIGHT//2), fontsize=50, color="green")
        screen.draw.text("Pressione Enter para jogar novamente", center=(WIDTH//2, HEIGHT//2 + 50), fontsize=30, color="white")


def on_mouse_down(pos):
    global game_started, sound_on
    if not game_started:
        if buttons["start"].collidepoint(pos):
            start_game()
        elif buttons["sound"].collidepoint(pos):
            toggle_sound()
        elif buttons["exit"].collidepoint(pos):
            exit()

def update():
    global game_won, game_started, game_over

    if game_started and not paused:
        if not game_over and not game_won:
            check_ground()
            animate_hero()
            handle_input()
            apply_gravity()
            check_enemies()
            update_enemies()

        if hero.right >= WIDTH:
            game_won = True


def start_game():
    global game_started, game_over, game_won, hero, enemies, INITIAL_ENEMIES
    
    game_started = True
    game_over = False
    game_won = False
    
    # Agora a variável está reconhecida globalmente
    enemies = INITIAL_ENEMIES.copy() 
    
    hero.pos = (100, 500)
    hero.vx = 0
    hero.vy = 0
    hero.on_ground = True

    for enemy in enemies:
        enemy.x = enemy.initial_x  

    if sound_on:
        music.play("start")



def toggle_sound():
    global sound_on
    sound_on = not sound_on
    if not sound_on:
        music.stop()
    else:
        if game_started:
            music.play("music")

def handle_input():
    hero.vx = 0
    if keyboard.left:
        hero.vx = -move_speed
    if keyboard.right:
        hero.vx = move_speed
    if keyboard.space and hero.on_ground:
        hero.vy = jump_strength
        hero.on_ground = False
    hero.x += hero.vx

def apply_gravity():
    if not hero.on_ground:
        hero.vy += gravity
        hero.y += hero.vy
    if hero.y > HEIGHT:
        print("Game Over! Caiu da tela!")
        global game_over
        game_over = True

def check_ground():
    ground_level = 550
    if hero.y >= ground_level:
        hero.y = ground_level
        hero.vy = 0
        hero.on_ground = True
    else:
        hero.on_ground = False


def check_enemies():
    global game_over

    enemies_to_remove = []
    for enemy in enemies[:]:
        hero_rect = hero._rect
        enemy_rect = enemy._rect

        print(f"Hero: {hero_rect}")
        print(f"Enemy: {enemy_rect}")

        if hero.vy > 0 and hero_rect.bottom <= enemy_rect.top:
            if hero.vy > 0 and hero._rect.bottom - 10 <= enemy._rect.top:
                enemies_to_remove.append(enemy)
                hero.vy = -12 
            else:
                game_over = True
        elif abs(hero.x - enemy.x) <= 20 and abs(hero.y - enemy.y) <= 15:  
            print("⚠️ O herói está muito próximo do inimigo! GAME OVER!")
            game_over = True
    for enemy in enemies_to_remove:
        if enemy in enemies:  
            enemies.remove(enemy)

def animate_hero():
    global hero_frame_index, hero_anim_timer
    hero_anim_timer += 1
    if hero_anim_timer >= 20:
        hero_frame_index = (hero_frame_index + 1) % len(hero_idle_frames)
        hero.image = f"hero/{hero_walk_frames[hero_frame_index]}" if hero.vx != 0 else f"hero/{hero_idle_frames[hero_frame_index]}"
        hero_anim_timer = 0
    if hero.vx < 0:
        hero.flip_x = True
    elif hero.vx > 0:
        hero.flip_x = False
    if hero.left < 0:
        hero.left = 0
    if hero.right > WIDTH:
        hero.right = WIDTH

def on_key_down(key):
    global paused
    if key == keys.P:
        paused = not paused
    elif key == keys.RETURN and game_over:
        start_game()
def on_key_down(key):
    global paused, game_won

    if key == keys.P:
        paused = not paused
    elif key == keys.RETURN and (game_over or game_won):
        start_game()

pgzrun.go()
