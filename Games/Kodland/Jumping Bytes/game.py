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
lion = Actor("lion_idle1", (100, 500))
enemies = [
    Actor("enemy1", (600, 500)),
    Actor("enemy2", (300, 500)),
    Actor("enemy3", (700, 450))
]    
platform = Actor("platform", (400, 500))

# animations
lion_idle_frames = ["lion_idle1", "lion_idle2"]
lion_walk_frames = ["lion_walk1", "lion_walk2"]
lion_frame_index = 0
lion_anim_timer = 0

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
    screen.draw.filled_rect(buttons["exit"], "darked")
    screen.draw.text("Exit", center=buttons["exit"].center, fontsize=30, color="white")

# function to draw the game screen
