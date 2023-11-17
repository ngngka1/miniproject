import time
import curses
import random
stdscr = curses.initscr()

def draw_screen(Pscreen: list):
    print(f"Level {level}:".center(20))
    print("".join(Pscreen))
    
def load_level_attribute():
    global level
    with open(f"level_{level}.md") as level_files:
        for line in level_files:
            if not line.startswith("#"):
                
    
point = 1
level = 1
running = True
screen = []
arithmetic_opeartor = ("+", "-", "x", "/")
default_distance_to_player = 10
distance_to_player = default_distance_to_player # how many lines till the arithemetic calculation hits the player
left_calculation = None
right_calculation = None

with open("map.md", "r+") as map:
    map.seek(0)
    screen = map.readlines()
    


#while running:
    if not left_calculation:
        left_calculation = arithmetic_opeartor[random.randint(0, len(arithmetic_opeartor))] + random.randint(0,level_max)
    if not right_calculation:
        
        
    draw_screen(screen)