import pgzrun
import random

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
platform = Actor("accessories/platform", (400, 500))

# animations
hero_idle_frames = ["hero_idle1", "hero_idle2", "hero_idle3"]
hero_walk_frames = ["hero_walk1", "hero_walk2", "hero_walk3"]
hero_frame_index = 0
hero_anim_timer = 0

# menu buttons (x,y, width and height)
buttons = {
    "start": Rect((300, 200), (200, 50)),
    "sound": Rect((300, 270), (200, 50)),
    "exit": Rect((300, 340), (200, 50))
}

music.set_volume(0.5)

def draw():
    screen.clear()
    if not game_started:
        draw_menu()
    else:
        draw_game()


# function to start the game
def draw_menu():
    screen.fill((30, 30, 60))
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
    screen.fill((100, 180, 225))
    platform.draw()
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
    if game_started and not paused:
        animate_hero()


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


# detect pressed keys
def on_keys_down(key):
    global paused
    if key == keys.P:
        paused = not paused


# hero animation
def animate_hero():
    global hero_frame_index, hero_anim_timer
    hero_anim_timer += 1
    if hero_anim_timer >= 20:
        hero_frame_index = (hero_frame_index + 1) % len(hero_idle_frames)
        hero.images = hero_idle_frames[hero_frame_index] # switch of the sprite
        hero_anim_timer = 0


# start game loop
pgzrun.go()
