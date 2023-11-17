import pygame
from PIL import ImageColor
import os
from functools import reduce
import json
import re
import sys
import time
import random
from copy import copy

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
            #if event.key == pygame.K_DOWN:
            #    self.move_down = True
            #if event.key == pygame.K_UP:
            #    self.move_up = True
            if event.key == pygame.K_LSHIFT:
                self.sprint = True
                
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_RIGHT:
                self.move_right = False
            if event.key == pygame.K_LEFT:
                self.move_left = False
            #if event.key == pygame.K_DOWN:
            #    self.move_down = False
            #if event.key == pygame.K_UP:
            #    self.move_up = False
            if event.key == pygame.K_LSHIFT:
                self.sprint = False
    
    def movement_prompt(self):
        prev_position_x = copy(self.position_x)
        prev_position_y = copy(self.position_y)
        if self.move_right:
            self.position_x += 3
        if self.move_left:
            self.position_x -= 3
        #if self.move_down:
        #    self.position_y += 3
        #if self.move_up:
        #    self.position_y -= 3   
        
        self.hitbox = pygame.Rect(self.position_x, self.position_y, self.width, self.height)
        for wall in wall_objects:
            if self.hitbox.colliderect(wall.hitbox): # basically, this block checks sprite's collision with obstacles
                if pygame.Rect(self.position_x, prev_position_y, self.width, self.height).colliderect(wall.hitbox):
                    self.position_x = self.position_x - (self.position_x + self.width * (1 - int(prev_position_x / (wall.position_x + wall.width))) - wall.position_x - wall.width * int(prev_position_x / (wall.position_x + wall.width)))
                if pygame.Rect(prev_position_x, self.position_y, self.width, self.height).colliderect(wall.hitbox):
                    self.position_y = self.position_y - (self.position_y + self.height * (1 - int(prev_position_y / (wall.position_y + wall.height)) ) - wall.position_y - wall.height * int(prev_position_y / (wall.position_y + wall.height)))
                
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
            self.surface_scaled = pygame.transform.scale(surface_unscaled, (self.width, self.height))
        else:
            self.path = None
            self.surface_unscaled = None
            self.surface_scaled = None
        self.hitbox = pygame.Rect(self.position_x, self.position_y, self.width, self.height)
           
class obstacle_type(wall_object_type):
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
        self.width = 100
        self.height = 100
        self.txt_surface = None
        self.txt_surface_rect = None
        self.hitbox = None
        
    def generate_random_operation(self):
        self.operator = self.available_arithmetic_operators[random.randint(0, len(self.available_arithmetic_operators) - 1)]
        self.number = random.randint(1, maximum_operation_number) 
        self.operation = self.operator + str(self.number)
        self.txt_surface = FONT.render(self.operation, True, ImageColor.getrgb("black"), ImageColor.getrgb("green"))
        self.txt_surface_rect = self.txt_surface.get_rect(center = ((abs(screen_width * int(self.position_x / (screen_width / 2)) - margin_width) + (screen_width / 2)) / 2, self.position_y))
        self.hitbox = pygame.rect.Rect(self.txt_surface_rect)
    
    def initialize(self):
        self.position_y = 0

    def move(self, move_by_x: int, move_by_y: int):
        self.position_x += move_by_x
        self.position_y += move_by_y
        self.txt_surface_rect.move_ip(move_by_x, move_by_y)
        self.hitbox.move_ip(move_by_x, move_by_y)
        
class boss_type:
    def __init__(self, name, position_x, position_y, width, height):
        self.name = name
        self.position_x = position_x
        self.position_y = position_y
        self.width = width
        self.height = height
        
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
        global font_size
        global font_type_path
        global FONT
        font_prop_dict = json.loads(font_file.read())# font property dictionary
        font_size = font_prop_dict["Font_size"]
        font_type_path = os.path.join("assets", font_prop_dict["ttf_file_basename"])
        pygame.font.init()
        FONT = pygame.font.Font(font_type_path, font_size)

def load_wall_objects():
    global wall_objects
    wall_objects = []
    with open(f"level.json") as level_file:
        level_prop_dict = json.loads(level_file.read())
        for level_prop in level_prop_dict:
            if level_prop["level"] == current_level: # Note: (if current_level exceeded the total number of level there is, the screen will simply not print any wall objects)
                
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
                        
                for obstacle_object in level_prop["obstacles"]:
                    if obstacle_object["color"]:
                        wall_objects.append(obstacle_type(margin_object["name"], margin_object["position_x"], margin_object["position_y"], margin_object["width"], margin_object["height"], margin_object["color"], None))
                    elif obstacle_object["image_file_basename"]:
                        wall_objects.append(obstacle_type(margin_object["name"], margin_object["position_x"], margin_object["position_y"], margin_object["width"], margin_object["height"], None, margin_object["image_file_basename"]))
    
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
                left_operation = operation_option_type(200, 0, arithmetic_operators)
                right_operation = operation_option_type(screen_width / 2 + 100, 0, arithmetic_operators)
                left_operation.generate_random_operation()
                right_operation.generate_random_operation()
                boss = boss_type(level_prop["boss"]["name"], level_prop["boss"]["position_x"], level_prop["boss"]["position_y"], level_prop["boss"]["width"], level_prop["boss"]["height"])
                break

def load_stats():
    global stats
    stats = gamestats(1, 0)
    
def operation_check():
    if sprite.hitbox.colliderect(left_operation.hitbox):
        stats.sum_counter = calculation(stats.sum_counter, left_operation.operation)
        left_operation.initialize()
        right_operation.initialize()
        stats.checkpoints_counter += 1
    elif sprite.hitbox.colliderect(right_operation.hitbox):
        stats.sum_counter = calculation(stats.sum_counter, right_operation.operation)
        left_operation.initialize()
        right_operation.initialize()
        stats.checkpoints_counter += 1
    else:
        return False
    return True
    
        
def calculation(count, operation: str):
    if operation[0] == "+" or operation[0] == "-":
        count += int(operation)
    elif operation[0] == "*":
        count *= int(operation[1:])
    elif operation[0] == "/":
        count /= int(operation[1:])
    return count

def draw_main_screen():
    # initialize the screen by filling it with color white
    screen.fill(screen_bgcolor)
    
    # print the operation
    pygame.draw.rect(screen, ImageColor.getrgb("green"), left_operation.hitbox, 0) # left
    screen.blit(left_operation.txt_surface, left_operation.txt_surface_rect)
    
    pygame.draw.rect(screen, ImageColor.getrgb("green"), right_operation.hitbox, 0) # right
    screen.blit(right_operation.txt_surface, right_operation.txt_surface_rect)
    
    # print the wall objects
    for wall in wall_objects:
        if wall.color:
            pygame.draw.rect(screen, wall.color, wall.hitbox)
        elif wall.path:
            screen.blit(wall.surface_scaled, (wall.position_x, wall.position_y))
    
    # print the player
    screen.blit(sprite.surface_scaled, (sprite.position_x, sprite.position_y))
    
    # print stats on the right side of the screen

    pygame.display.update()
        
def main(): # for your information, in short, this function will be executed once the program is run
    running = True
    
    while running:
        clock = pygame.time.Clock()
        clock.tick(fps)
        for event in pygame.event.get(): ## this for-loop block checks user input
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
            sprite.movement_check(event)
        
        if (left_operation.position_y <= screen_height) and stats.checkpoints_counter <= 10:
            if operation_check():
                left_operation.initialize()
                left_operation.generate_random_operation()
                right_operation.initialize()
                right_operation.generate_random_operation()  
            left_operation.move(0, speed)   
            
        if (right_operation.position_y <= screen_height) and stats.checkpoints_counter <= 10:
            if operation_check():
                left_operation.initialize()
                left_operation.generate_random_operation()
                right_operation.initialize()
                right_operation.generate_random_operation()
            right_operation.move(0, speed)   
        
        sprite.movement_prompt()
        
        draw_main_screen()
    

## The following lines are data of the screen window
screen_width = 700
screen_height = 700
screen_bgcolor = ImageColor.getrgb("white") # PIL.ImageColor.getrgb(color) to get rgb value of color
screen = pygame.display.set_mode((screen_width, screen_height)) # this line makes a screen with the width and height specified
pygame.display.set_caption("Number game")
fps = 60

## load data of sprite (can encapsulate the data into a class but only one player so whatever)
load_sprite_property()

# load font property
load_font_property()

## other game property
current_level = 1

load_stats()
load_wall_objects()
load_level_attribute()


if __name__ == "__main__": # this means that when the file with name "main" is run, the condition will become true
    main()