import pygame
from PIL import ImageColor
import os
import sys
import json
import random
import re 

class sprite_type: 
    def __init__(self, name: str, width: int, height: int, default_x: int, default_y: int, file_basename: str):
        # sprite attribute
        self.name = name
        self.width = width
        self.height = height
        self.path = os.path.join("assets", file_basename)
        self.surface_unscaled = pygame.image.load(self.path)
        self.surface_scaled = pygame.transform.scale(self.surface_unscaled, (self.width, self.height))
        
        # sprite movement attributes etc.
        self.position_x = default_x
        self.position_y = default_y
        self.hitbox = pygame.Rect(self.position_x, self.position_y, self.width, self.height)
        self.move_right = False
        self.move_left = False
        self.move_down = False
        self.move_up = False
        self.sprint = False
    
    def movement_check(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RIGHT:
                self.move_right = True
            if event.key == pygame.K_LEFT:
                self.move_left = True
            if event.key == pygame.K_DOWN:
                self.move_down = True
            if event.key == pygame.K_UP:
                self.move_up = True
            if event.key == pygame.K_LSHIFT:
                self.sprint = True
                
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_RIGHT:
                self.move_right = False
            if event.key == pygame.K_LEFT:
                self.move_left = False
            if event.key == pygame.K_DOWN:
                self.move_down = False
            if event.key == pygame.K_UP:
                self.move_up = False
            if event.key == pygame.K_LSHIFT:
                self.sprint = False
    
    def movement_prompt(self):
        prev_position_x = self.position_x
        prev_position_y = self.position_y
        if self.move_right:
            self.position_x += 3
        if self.move_left:
            self.position_x -= 3
#####################################################
#        if self.move_down:                         #
#            self.position_y += 3                   #
#        if self.move_up:                           #
#            self.position_y -= 3                   #
#####################################################      
        self.hitbox = pygame.Rect(self.position_x, self.position_y, self.width, self.height)
        for wall in wall_objects:
            if self.hitbox.colliderect(wall.hitbox): # basically, this block checks sprite's collision with obstacles
                if type(wall) == obstacle_type:
                    if pygame.Rect(prev_position_x, prev_position_y, self.width, self.height).colliderect(wall.hitbox):
                        self.position_y = prev_position_y + speed
                        self.hitbox = pygame.Rect(self.position_x, self.position_y, self.width, self.height)
                        continue
                if pygame.Rect(self.position_x, prev_position_y, self.width, self.height).colliderect(wall.hitbox):
                    self.position_x = self.position_x - (self.position_x + self.width * (1 - int(prev_position_x / (wall.position_x + wall.width))) - wall.position_x - wall.width * int(prev_position_x / (wall.position_x + wall.width)))
                if pygame.Rect(prev_position_x, self.position_y, self.width, self.height).colliderect(wall.hitbox):
                    self.position_y = self.position_y - (self.position_y + self.height * (1 - int(prev_position_y / (wall.position_y + wall.height)) ) - wall.position_y - wall.height * int(prev_position_y / (wall.position_y + wall.height)))
                
                if self.hitbox.colliderect(wall.hitbox): # if still collide, it means its pushed into wall
                        self.position_x = prev_position_x
                        self.position_y = prev_position_y
                self.hitbox = pygame.Rect(self.position_x, self.position_y, self.width, self.height)
                
class wall_object_type:
    def __init__(self, name, position_x, position_y, width, height, color, image_file_basename):
        self.name = name
        self.position_x = position_x
        self.position_y = position_y
        self.width = width
        self.height = height
        self.color = color
        if image_file_basename:
            self.path = os.path.join("assets", image_file_basename)
            self.surface_unscaled = pygame.image.load(self.path)
            self.surface_scaled = pygame.transform.scale(self.surface_unscaled, (self.width, self.height))
        else:
            self.path = None
            self.surface_unscaled = None
            self.surface_scaled = None
        self.hitbox = pygame.Rect(self.position_x, self.position_y, self.width, self.height)
           
class obstacle_type(wall_object_type):
    def __init__(self, param1, param2, param3, param4, param5, param6, param7, appearance_checkpoint):
        wall_object_type.__init__(self, param1, param2, param3, param4, param5, param6, param7)
        self.position_y -= self.height
        self.hitbox.move_ip(0, - self.height)
        self.appearance_checkpoint = appearance_checkpoint

    def move(self, move_by_x: int, move_by_y: int):
        self.position_x += move_by_x
        self.position_y += move_by_y
        self.hitbox.move_ip(move_by_x, move_by_y)
        
class margin_type(wall_object_type):
    pass
    
class operation_option_type:
    def __init__(self, position_x, position_y, operators: list): # default value of y is 0 supposedly
        self.available_arithmetic_operators = operators
        self.operator = None
        self.number = None
        self.operation = None
        self.position_x = position_x
        self.position_y = position_y
        self.width = (margin_rect_width - 2 * margin_width) / 2
        self.height = 100
        self.txt_surface = None
        self.txt_surface_rect = None
        self.hitbox = None
        self.color = None
        
    def generate_random_operation(self, *add_only_flag):
        if add_only_flag:
            self.operator = "+"
        else:
            self.operator = self.available_arithmetic_operators[random.randint(0, len(self.available_arithmetic_operators) - 1)]
        self.number = random.randint(1, maximum_operation_number) 
        self.operation = self.operator + str(self.number)
        if random.randint(0, 10) == 0: # 10 % surprise
            self.txt_surface = FONT_LARGE.render("???", True, ImageColor.getrgb("black"))
        else:
            self.txt_surface = FONT_LARGE.render(self.operation, True, ImageColor.getrgb("black"))
        self.txt_surface_rect = self.txt_surface.get_rect(center = ((abs(margin_rect_width * int(self.position_x / (margin_rect_width / 2)) - margin_width) + (margin_rect_width / 2)) / 2, self.position_y))
        self.hitbox = pygame.rect.Rect(self.position_x, self.position_y, self.width, self.height)
        self.color = random_color()
    
    def initialize(self):
        self.position_y = 0

    def move(self, move_by_x: int, move_by_y: int):
        self.position_x += move_by_x
        self.position_y += move_by_y
        self.txt_surface_rect.move_ip(move_by_x, move_by_y)
        self.hitbox.move_ip(move_by_x, move_by_y)
        
class boss_type:
    def __init__(self, name, position_x, position_y, width, height, image_file_basename, difficulty_scale):
        self.name = name
        self.position_x = position_x
        self.position_y = position_y
        self.width = width
        self.height = height
        self.path = os.path.join("assets", image_file_basename)
        self.surface_unscaled = pygame.image.load(self.path)
        self.surface_scaled = pygame.transform.scale(self.surface_unscaled, (self.width, self.height))
        self.surface_scaled_rect = self.surface_scaled.get_rect(center = (margin_rect_width / 2, self.position_y))
        self.hitbox = pygame.rect.Rect(self.surface_scaled_rect)
        self.difficulty_scale = difficulty_scale 
        self.health = 1
        
    def move(self, move_by_x, move_by_y):
        self.position_x += move_by_x
        self.position_y += move_by_y
        self.surface_scaled_rect.move_ip(move_by_x, move_by_y)
        self.hitbox.move_ip(move_by_x, move_by_y)
        
class gamestats:
    def __init__(self, sum_counter, checkpoints_counter):
        self.sum_counter = sum_counter
        self.checkpoints_counter = checkpoints_counter

    

def load_sprite_property():
    global sprite
    with open("sprite.json") as sprite_file:
        sprite_prop_dict = json.loads(sprite_file.read()) # sprite property dictionary
        assets_files = os.listdir("assets")
        for asset_file_name in assets_files:
            if asset_file_name.startswith("sprite"):
                sprite_image_file_basename = asset_file_name
        sprite = sprite_type(sprite_prop_dict["name"], sprite_prop_dict["sprite_width"], sprite_prop_dict["sprite_height"], sprite_prop_dict["default_sprite_position_x"], sprite_prop_dict["default_sprite_position_y"], sprite_image_file_basename)

def load_font_property():
    with open("font.json") as font_file:
        global FONT_LARGE, FONT_SMALL
        font_prop_dict = json.loads(font_file.read())# font property dictionary
        font_size_large = font_prop_dict["font_size_large"]
        font_size_small = font_prop_dict["font_size_small"]
        font_type_path = os.path.join("assets", font_prop_dict["ttf_file_basename"])
        pygame.font.init()
        FONT_LARGE = pygame.font.Font(font_type_path, font_size_large)
        FONT_SMALL = pygame.font.Font(font_type_path, font_size_small)

def load_wall_objects():
    global wall_objects
    wall_objects = []
    with open(f"level.json") as level_file:
        level_prop_dict = json.loads(level_file.read())
        for level_prop in level_prop_dict:
            if level_prop["level"] == current_level: # Note: (if current_level exceeded the total number of level there is, the screen will simply not print any wall objects)
                
                for obstacle_object in level_prop["obstacles"]:
                    if obstacle_object["color"]:
                        wall_objects.append(obstacle_type(obstacle_object["name"], obstacle_object["position_x"], obstacle_object["position_y"], obstacle_object["width"], obstacle_object["height"], obstacle_object["color"], None, obstacle_object["appearance_checkpoint"]))
                    elif obstacle_object["image_file_basename"]:
                        wall_objects.append(obstacle_type(obstacle_object["name"], obstacle_object["position_x"], obstacle_object["position_y"], obstacle_object["width"], obstacle_object["height"], None, obstacle_object["image_file_basename"], obstacle_object["appearance_checkpoint"]))
                
                for margin_object in level_prop["margin"]:
                    
                    if margin_object["color"]:
                        wall_objects.append(margin_type(margin_object["name"], margin_object["position_x"], margin_object["position_y"], margin_object["width"], margin_object["height"], margin_object["color"], None))
                    elif margin_object["image_file_basename"]:
                        wall_objects.append(margin_type(margin_object["name"], margin_object["position_x"], margin_object["position_y"], margin_object["width"], margin_object["height"], None, margin_object["image_file_basename"]))
                    if margin_object["name"] == "left_margin":
                        global margin_width
                        margin_width = margin_object["width"]
                    if margin_object["name"] == "top_margin":
                        global margin_height
                        margin_height = margin_object["height"]
                        global margin_rect_width
                        margin_rect_width = margin_object["width"]
                        global margin_rect_height
                        margin_rect_height = screen_height
                        
def load_level_attribute():
    global maximum_operation_number
    global speed
    global arithmetic_operators
    global left_operation, right_operation
    global boss
    with open("level.json") as level_file:
        level_prop_dict = json.loads(level_file.read())
        for level_prop in level_prop_dict:
            if level_prop["level"] == current_level:
                maximum_operation_number = level_prop["maximum_operation_number"]
                speed = level_prop["speed"]
                arithmetic_operators = level_prop["arithmetic_operators"]
                left_operation = operation_option_type(margin_width, 0, arithmetic_operators)
                right_operation = operation_option_type(margin_rect_width / 2, 0, arithmetic_operators)
                left_operation.generate_random_operation()
                right_operation.generate_random_operation(1)
                boss = boss_type(level_prop["boss"]["name"], level_prop["boss"]["position_x"], level_prop["boss"]["position_y"], level_prop["boss"]["width"], level_prop["boss"]["height"], level_prop["boss"]["image_file_basename"], level_prop["boss"]["difficulty_scale"])
                break

def load_stats():
    global stats
    stats = gamestats(1, 0)
    
def operation_check():
    if sprite.hitbox.colliderect(left_operation.hitbox) and sprite.hitbox.colliderect(right_operation.hitbox):
        if (2 * sprite.position_x + sprite.width - 2 * left_operation.position_x - left_operation.width) / 2 <= (2 * right_operation.position_x + right_operation.width - 2 * sprite.position_x - sprite.width) / 2:
            stats.sum_counter = calculation(stats.sum_counter, left_operation.operation)
        else:
            stats.sum_counter = calculation(stats.sum_counter, right_operation.operation)
    elif sprite.hitbox.colliderect(left_operation.hitbox):
        stats.sum_counter = calculation(stats.sum_counter, left_operation.operation)
    elif sprite.hitbox.colliderect(right_operation.hitbox):
        stats.sum_counter = calculation(stats.sum_counter, right_operation.operation)
    else:
        return False
    return True
    
def calculation(count: int, operation: str):
    if operation[0] == "+" or operation[0] == "-":
        count += int(operation)
    elif operation[0] == "*":
        count *= int(operation[1:])
    elif operation[0] == "/":
        count /= int(operation[1:])
    if count < 0:
        return 0
    else:
        return count

def random_color():
    return (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

def update_hof_list(new_score):
    global hof_list
    if len(hof_list) == 0:
        hof_list.append(new_score)
    elif len(hof_list) == 1:
        if hof_list[0]["name"] == new_score["name"] and hof_list[0]["maximum_level_reached"] <= new_score["maximum_level_reached"]:
            hof_list[0] = new_score
        elif hof_list[0]["maximum_level_reached"] < new_score["maximum_level_reached"]:
            hof_list.insert(0, new_score)
        elif hof_list[0]["name"] != new_score["name"]:
            hof_list.append(new_score)
    else:
        for i in range(0, len(hof_list)):
            if hof_list[i]["name"] == new_score["name"] and hof_list[i]["maximum_level_reached"] < new_score["maximum_level_reached"]:
                hof_list.pop(i)
                break
        counter = 0
        while counter < len(hof_list) - 1:
            if hof_list[counter+1]["maximum_level_reached"] < new_score["maximum_level_reached"] and hof_list[counter]["maximum_level_reached"] >= new_score["maximum_level_reached"]:
                break
            else:
                counter += 1
        hof_list.insert(counter + 1, new_score)
            
    with open("hall_of_fame.json", "w") as hof_file:
        hof_file.write(json.dumps(hof_list))

def input_player_name():
    txt_surface1 = FONT_SMALL.render("Please input player name:", True, ImageColor.getrgb("black"))
    txt_surface1_rect = txt_surface1.get_rect(center = (screen_width / 2, screen_height / 2))
    inputted = False
    player_name = ""
    while not inputted:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                inputted = True
                pygame.quit()
                sys.quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    inputted = True
                    return player_name
                elif re.search("^[a-zA-Z0-9]{1}.{0}$", pygame.key.name(event.key)):
                    player_name += pygame.key.name(event.key)
                elif event.key == pygame.K_BACKSPACE:
                    player_name = player_name[:-1]
        player_name_surface = FONT_SMALL.render(player_name, True, ImageColor.getrgb("black"))
        player_name_surface_rect = player_name_surface.get_rect(center = (screen_width / 2, screen_height / 2 + 50))
        screen.fill(screen_bgcolor)
        screen.blit(txt_surface1, txt_surface1_rect)
        screen.blit(player_name_surface, player_name_surface_rect)
        pygame.display.update()
                  
def draw_main_screen():
    # initialize the map
    screen.fill(screen_bgcolor)
    
    # print the operation / boss
    if stats.checkpoints_counter < 10:
        pygame.draw.rect(screen, left_operation.color, left_operation.hitbox, 0) # left
        screen.blit(left_operation.txt_surface, left_operation.txt_surface_rect)
        
        pygame.draw.rect(screen, right_operation.color, right_operation.hitbox, 0) # right
        screen.blit(right_operation.txt_surface, right_operation.txt_surface_rect)
    else:
        screen.blit(boss.surface_scaled, boss.surface_scaled_rect)
        boss_health_surface = FONT_LARGE.render(str(int(boss.health)), True, ImageColor.getrgb("black"))
        boss_health_surface_rect = boss_health_surface.get_rect(center = ((margin_rect_width) / 2, boss.position_y))
        screen.blit(boss_health_surface, boss_health_surface_rect)
    
    # print the wall objects
    for wall in wall_objects:
        if wall.color:
            pygame.draw.rect(screen, wall.color, wall.hitbox)
        elif wall.path:
            screen.blit(wall.surface_scaled, (wall.position_x, wall.position_y))
    
    # print the player
    screen.blit(sprite.surface_scaled, (sprite.position_x, sprite.position_y))
    
    # print stats on the right side of the screen
    level_display_txt_surface = FONT_SMALL.render(f"Your current level: {current_level}", True, ImageColor.getrgb("black"))
    sum_counter_txt_surface = FONT_SMALL.render("Your current score:", True, ImageColor.getrgb("black"))
    sum_counter_surface = FONT_LARGE.render(str(int(stats.sum_counter)), True, ImageColor.getrgb("black"))
    screen.blit(level_display_txt_surface, (margin_rect_width + 20, screen_height / 2 - 50))
    screen.blit(sum_counter_txt_surface, (margin_rect_width + 20, screen_height / 2))
    screen.blit(sum_counter_surface, (margin_rect_width + 20, screen_height / 2 + 50))

    pygame.display.update()
        
def draw_level_transition_screen():
    global player
    if level_passed:
        txt_surface1 = FONT_SMALL.render(f"Congrats you have passed level {current_level}!", True, ImageColor.getrgb("black"))
        txt_surface2 = FONT_SMALL.render("Press enter to continue to the next level", True, ImageColor.getrgb("black"))
        txt_surface1_rect = txt_surface1.get_rect(center = (margin_rect_width / 2, margin_rect_height / 2))
        txt_surface2_rect = txt_surface2.get_rect(center = (margin_rect_width / 2, margin_rect_height / 2 + 50))
        txt_surface1_box_surface = pygame.rect.Rect(txt_surface1_rect)
        txt_surface2_box_surface = pygame.rect.Rect(txt_surface2_rect)
        pygame.draw.rect(screen, ImageColor.getrgb("green"), txt_surface1_box_surface, 0)
        pygame.draw.rect(screen, ImageColor.getrgb("green"), txt_surface2_box_surface, 0)
        screen.blit(txt_surface1, txt_surface1_rect)
        screen.blit(txt_surface2, txt_surface2_rect)
    else:
        # print prompt on game window
        txt_surface1 = FONT_SMALL.render(f"You have failed level {current_level}!", True, ImageColor.getrgb("black"))
        txt_surface2 = FONT_SMALL.render("Press enter to retry", True, ImageColor.getrgb("black"))
        txt_surface1_rect = txt_surface1.get_rect(center = (margin_rect_width / 2, margin_rect_height / 2))
        txt_surface2_rect = txt_surface2.get_rect(center = (margin_rect_width / 2, margin_rect_height / 2 + 50))
        txt_surface1_box_surface = pygame.rect.Rect(txt_surface1_rect)
        txt_surface2_box_surface = pygame.rect.Rect(txt_surface2_rect)
        pygame.draw.rect(screen, ImageColor.getrgb("green"), txt_surface1_box_surface, 0)
        pygame.draw.rect(screen, ImageColor.getrgb("green"), txt_surface2_box_surface, 0)
        screen.blit(txt_surface1, txt_surface1_rect)
        screen.blit(txt_surface2, txt_surface2_rect)
        # print hall of fame box:
        hof_rect = pygame.rect.Rect(margin_rect_width + 20, margin_height, 200, 200)
        hof_txt_surface = FONT_SMALL.render("Hall of Fame", True, ImageColor.getrgb("black"))
        hof_txt_surface_rect = hof_txt_surface.get_rect(center = ((margin_rect_width + screen_width) / 2, 50))
        screen.blit(hof_txt_surface, hof_txt_surface_rect)
        txt_surface3 = FONT_SMALL.render("Player             Maximum level reached", True, ImageColor.getrgb("black"))
        screen.blit(txt_surface3, (margin_rect_width + 20, margin_height))
        hof_list_cursor = 0
        for score in hof_list:
            hof_list_cursor += 30
            if player["name"] == score["name"]:
                score_surface = FONT_SMALL.render(score["name"] + "                    " + str(score["maximum_level_reached"]), True, ImageColor.getrgb("green"))
            else:
                score_surface = FONT_SMALL.render(score["name"] + "                    " + str(score["maximum_level_reached"]), True, ImageColor.getrgb("black"))
            screen.blit(score_surface, (margin_rect_width + 20, margin_height + hof_list_cursor))
        
    pygame.display.update()

def main(): # for your information, in short, this function will be executed once the program is run
    global current_level, level_passed, level_continue, level_failed
    running = True
    
    while running:
        clock = pygame.time.Clock()
        clock.tick(fps)
        for event in pygame.event.get(): ## this for-loop block checks user input
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                level_continue = True
            sprite.movement_check(event)
        sprite.movement_prompt()
        
        if level_passed == False and level_failed == False:
            if stats.checkpoints_counter < 10:
                if operation_check() or left_operation.position_y > screen_height:
                    boss.health = (calculation(boss.health, left_operation.operation) + calculation(boss.health, right_operation.operation)) / 2 # take mean to avoid overly extreme value
                    left_operation.initialize()
                    right_operation.initialize()
                    left_operation.generate_random_operation()
                    right_operation.generate_random_operation()
                    if left_operation.operation[0] == right_operation.operation[0] or stats.sum_counter <= 1: # avoid extreme value change
                        right_operation.initialize()
                        if stats.sum_counter <= 1:
                            right_operation.generate_random_operation(1)
                        else:
                            right_operation.generate_random_operation()
                    stats.checkpoints_counter += 1
                    if stats.checkpoints_counter == 10:
                        boss.health *= boss.difficulty_scale
                else:
                    left_operation.move(0, speed)
                    right_operation.move(0, speed)
                    for wall in wall_objects:
                        if type(wall) == obstacle_type and (stats.checkpoints_counter == wall.appearance_checkpoint or wall.position_y > 0):
                            if wall.position_y < 0:
                                wall.move(0, - wall.position_y)
                            wall.move(0, speed)
            else:
                boss.move(0, speed)
                if sprite.hitbox.colliderect(boss.hitbox):
                    if stats.sum_counter >= boss.health:
                        level_passed = True
                    else:
                        level_failed = True
                        player["maximum_level_reached"] = current_level
                        update_hof_list(player)
            draw_main_screen()
        else:
            if level_continue:
                if not level_failed:
                    current_level += 1
                    load_wall_objects()
                level_passed = False
                level_continue = False
                level_failed = False
                load_stats()
                load_level_attribute()
            else:
                draw_level_transition_screen()
    
## The following lines are data of the screen window
screen_width = 1000
screen_height = 700
screen_bgcolor = (225,225,225) # PIL.ImageColor.getrgb(color) to get rgb value of color
screen = pygame.display.set_mode((screen_width, screen_height)) # this line makes a screen with the width and height specified
pygame.display.set_caption("Number game")
fps = 60

## load data of sprite (can encapsulate the data into a class but only one player so whatever)
load_sprite_property()

# load font property
load_font_property()

## other game property
current_level = 1
level_passed = False
level_failed = False
level_continue = False
player = {"name": input_player_name(), "maximum_level_reached": None}
with open("hall_of_fame.json") as hof_file:
    hof_list = json.loads(hof_file.read())

load_stats()
load_wall_objects()
load_level_attribute()


if __name__ == "__main__": # this means that when the file with name "main" is run, the condition will become true
    main()