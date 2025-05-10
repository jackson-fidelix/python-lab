import pgzrun
import random
from pygame import Rect

WIDTH = 800
HEIGHT = 600
TITLE = "Jumping Bytes"

# game state
game_started = False
paused = False
sound_on = True

# actors
hero = Actor("hero/hero_idle1", (100, 500))
enemies = [
    Actor("enemy/fire_idle1", (600, 500)),
    Actor("enemy/skeleton_idle1", (300, 500))
]    

background = Actor("accessories/background", (0, 0))
background.width = WIDTH
background.height = HEIGHT

platform = [Actor("accessories/spike", (400, 550))]  # only is solid
hazards = [Actor("accessories/box", (400,500), anchor=('center', 'bottom'))]   # it's hurt the hero

# animations
hero_idle_frames = ["hero_idle1", "hero_idle2", "hero_idle3"]
hero_walk_frames = ["hero_walk1", "hero_walk2", "hero_walk3"]
hero_frame_index = 0
hero_anim_timer = 0
hero.vx = 0
hero.vy = 0
hero.on_ground = False
gravity = 1
jump_strength = -18
move_speed = 5

fire_idle_frames = ["fire_idle1", "fire_idle2", "fire_idle3"]
fire_walk_frames = ["fire_walk1", "fire_walk2", "fire_walk3"]

skeleton_idle_frames = ["skeleton_idle1", "skeleton_idle2", "skeleton_idle3"]
skeleton_walk_frames = ["skeleton_walk1", "skeleton_walk2", "skeleton_walk3"]

def update_enemies(): 
    for enemy in enemies:
        enemy.x += enemy.vx
        if abs(enemy.x - enemy.initial_x) > enemy.patrol_range:
            enemy.vx = -enemy.vx
            enemy.flip_x = enemy.vx < 0

        enemy.anim_timer += 1
        if enemy.frame_index = (enemy.frame_index +1) % 3 # 3 frames
        if enemy == enemies[0]:
            enemy.image = f"enemy/{frames[enemy.frame_index]}"
        elif enemy == enemies[1]:
            frames = skeleton_walk_frames if enemy.vx != 0 else skeleton_idle_frames
            enemy.image = f"enemy/{frames[enemy.frame_index]}"
        enemy.anim_timer = 0

# menu buttons (x,y, width and height)
buttons = {
    "start": Rect((300, 200), (200, 50)),
    "sound": Rect((300, 270), (200, 50)),
    "exit": Rect((300, 340), (200, 50))
}

music.set_volume(0.5)

def draw():
    try:
        screen.blit("accessories/background", (0,0))
    except:
        print("Error: Não foi possível carregar a imagem de fundo!")
        screen.fill((0, 0, 0))
    for p in platform:
        p.draw()
    for h in hazards:
        h.draw()
    hero.draw()
    for enemy in enemies:
        enemy.draw()
    
    if not game_started:
        draw_menu()
    else:
        draw_game()


# function to start the game
def draw_menu():
    screen.draw.filled_rect(Rect((0, 0), (WIDTH, HEIGHT)), (225, 205, 0, 10))
    screen.draw.text("Jumping Bytes", center=(WIDTH//2, 100), fontsize=60, color="white")

    #draw start game button
    screen.draw.filled_rect(buttons["start"], "darkgreen")
    screen.draw.text("Start Game", center=buttons["start"].center, fontsize=30, color="white")

    #draw to sound ON and sound OFF
    screen.draw.filled_rect(buttons["sound"], "darkblue")
    text = "Sound: ON" if sound_on else "Sound: OFF"
    screen.draw.text(text, center=buttons["sound"].center, fontsize=30, color="white")

    #draw exit button
    screen.draw.filled_rect(buttons["exit"], "darkred")
    screen.draw.text("Exit", center=buttons["exit"].center, fontsize=30, color="white")

# function to draw the game screen
def draw_game():
    for p in platform:
        p.draw()
    for h in hazards:
        h.draw()
    hero.draw()
    for enemy in enemies:
        enemy.draw()

    # if game paused, show "PAUSED"
    if paused:
        screen.draw.text("PAUSED", center=(WIDTH//2, HEIGHT//2), fontsize=60, color="yellow")


# when the mouse clicked
def on_mouse_down(pos):
    global game_started, sound_on
    if not game_started:
        if buttons["start"].collidepoint(pos):
            start_game()
        elif buttons["sound"].collidepoint(pos):
            toggle_sound()
        elif buttons["exit"].collidepoint(pos):
            exit()


# update of the game
def update():
    global game_started, game_over
    if game_started and not paused:
        if game_over:
            game_started = False
            game_over = False # reset game
            hero.x, hero.y = 100, 500 # reboot position
            hero.vy = 0
            music.stop()
            return
        animate_hero()
        handle_input()
        apply_gravity()
        check_collisions()
        check_hazards()
        update_enemies()

# start game
def start_game():
    global game_started
    game_started = True
    if sound_on:
        music.play("start")


# turn on/turn off the sound
def toggle_sound():
    global sound_on
    sound_on = not sound_on
    if not sound_on:
        music.stop()
    else:
        if game_started:
            music.play("music")

# detect new inputs
def handle_input():
    hero.vx = 0
    if keyboard.left:
        hero.vx = -move_speed
    if keyboard.right:
        hero.vx = move_speed
    if keyboard.space and hero.on_ground:
        hero.vy = jump_strength
        hero.on_ground = True
        if sound_on:
            sounds.jump.play()
    hero.x += hero.vx


def apply_gravity():
    hero.vy += gravity
    hero.y += hero.vy
    if hero.y > HEIGHT:
        print("Game Over! Caiu da tela!")
        global game_over
        game_over = True


def check_collisions():
    hero.on_ground = False
    for p in platform:
        if hero.colliderect(p) and hero.vy >= 0:
            hero.y = p.top - hero.height
            hero.vy = 0
            hero.on_ground = True

game_over = False

def check_hazards():
    for h in hazards:
        if hero.colliderect(h):
            if sound_on:
                sounds.hurt.play()
        game_over = True
    
    for enemy in enemies:
        if hero.colliderect(enemy):
            if sound_on:
                sounds.hurt.play()
            game_over = True

# detect pressed keys
def on_key_down(key):
    global paused
    if key == keys.P:
        paused = not paused

# hero animation
def animate_hero():
    global hero_frame_index, hero_anim_timer
    hero_anim_timer += 1
    if hero_anim_timer >= 20:
        hero_frame_index = (hero_frame_index + 1) % len(hero_idle_frames)
        if hero.vx != 0:
            hero.image = "hero/" + hero_walk_frames[hero_frame_index] # switch of the sprite
        else:
            hero.image = "hero/" + hero_idle_frames[hero_frame_index] # switch of the sprite
        hero_anim_timer = 0

    # flip horizontal is walking to left
    if hero.vx < 0:
        hero.flip_x = True
    elif hero.vx > 0:
        hero.flip_x = False
    
    # screen limits
    if hero.left < 0:
        hero.left = 0
    if hero.right > WIDTH:
        hero.right = WIDTH

# start game loop
pgzrun.go()
