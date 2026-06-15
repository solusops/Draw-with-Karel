# character.py
# This module contains the code to draw different characters in our world.
# Kids can easily add their own characters here! Just create a new function
# like 'draw_my_character' and follow the examples below.
#
# Remember: The base character should face "East" (Right). The rotate_point
# function will automatically turn your character when it faces North, West, or South!

import tkinter as tk
from colors import OUTLINE_COLOR

import math

# --- DIRECTION HELPERS ---

DIRECTIONS = ["East", "SouthEast", "South", "SouthWest", "West", "NorthWest", "North", "NorthEast"]

def get_next_direction(current_direction):
    """Returns the next direction when you click a shape (turns 45 degrees clockwise)."""
    for i in range(len(DIRECTIONS)):
        if DIRECTIONS[i] == current_direction:
            next_index = (i + 1) % len(DIRECTIONS)
            return DIRECTIONS[next_index]
    return "East"

def get_dir_delta(direction):
    """Returns how much to move (x, y) for a given direction."""
    if direction == "East": return 1, 0
    elif direction == "SouthEast": return 1, 1
    elif direction == "South": return 0, 1
    elif direction == "SouthWest": return -1, 1
    elif direction == "West": return -1, 0
    elif direction == "NorthWest": return -1, -1
    elif direction == "North": return 0, -1
    elif direction == "NorthEast": return 1, -1
    return 0, 0

def rotate_point(x, y, direction):
    """Rotates an (x, y) point so the shape faces the right way."""
    angles = {
        "East": 0, "SouthEast": 45, "South": 90, "SouthWest": 135,
        "West": 180, "NorthWest": 225, "North": 270, "NorthEast": 315
    }
    angle_deg = angles.get(direction, 0)
    angle_rad = math.radians(angle_deg)
    
    new_x = x * math.cos(angle_rad) - y * math.sin(angle_rad)
    new_y = x * math.sin(angle_rad) + y * math.cos(angle_rad)
    
    return new_x, new_y

# --- CHARACTER DRAWING FUNCTIONS ---

def draw_classic_karel(canvas, cx, cy, cell_size, direction, color_hex):
    """
    Draws the classic Karel robot (the SIM card shape).
    """
    line_width = max(2, int(cell_size * 0.06))
    
    # Body
    body_pts = [(-0.25, -0.35), (0.1, -0.35), (0.25, -0.2), (0.25, 0.35), (-0.1, 0.35), (-0.25, 0.2)]
    body_rot = [rotate_point(x, y, direction) for x, y in body_pts]
    body_screen = [coord for pt in body_rot for coord in (cx + pt[0]*cell_size, cy + pt[1]*cell_size)]
    canvas.create_polygon(body_screen, fill=color_hex, outline=OUTLINE_COLOR, width=line_width)
    
    # Screen
    screen_pts = [(-0.12, -0.22), (0.12, -0.22), (0.12, 0.08), (-0.12, 0.08)]
    screen_rot = [rotate_point(x, y, direction) for x, y in screen_pts]
    screen_screen = [coord for pt in screen_rot for coord in (cx + pt[0]*cell_size, cy + pt[1]*cell_size)]
    canvas.create_polygon(screen_screen, fill="#FFFFFF", outline=OUTLINE_COLOR, width=max(1, line_width // 2))
    
    # Mouth
    mouth_pts = [(-0.06, 0.18), (0.06, 0.18)]
    mouth_rot = [rotate_point(x, y, direction) for x, y in mouth_pts]
    mouth_screen = [coord for pt in mouth_rot for coord in (cx + pt[0]*cell_size, cy + pt[1]*cell_size)]
    canvas.create_line(mouth_screen[0], mouth_screen[1], mouth_screen[2], mouth_screen[3], fill=OUTLINE_COLOR, width=max(1.5, line_width // 2))
    
    # Left foot
    left_foot_pts = [(-0.25, 0.08), (-0.35, 0.08), (-0.35, 0.18)]
    left_foot_rot = [rotate_point(x, y, direction) for x, y in left_foot_pts]
    left_foot_screen = [coord for pt in left_foot_rot for coord in (cx + pt[0]*cell_size, cy + pt[1]*cell_size)]
    canvas.create_line(left_foot_screen, fill=OUTLINE_COLOR, width=line_width, capstyle=tk.PROJECTING, joinstyle=tk.MITER)
    
    # Bottom foot
    bottom_foot_pts = [(0.08, 0.35), (0.08, 0.45), (0.18, 0.45)]
    bottom_foot_rot = [rotate_point(x, y, direction) for x, y in bottom_foot_pts]
    bottom_foot_screen = [coord for pt in bottom_foot_rot for coord in (cx + pt[0]*cell_size, cy + pt[1]*cell_size)]
    canvas.create_line(bottom_foot_screen, fill=OUTLINE_COLOR, width=line_width, capstyle=tk.PROJECTING, joinstyle=tk.MITER)

import os

# A dictionary to hold custom AI generated characters mapping: character_name -> function
CUSTOM_CHARACTERS = {}

# A master list of available characters so the UI can cycle through them!
AVAILABLE_CHARACTERS = ["Classic Karel"]

def load_characters_from_folder():
    characters_dir = "characters"
    if not os.path.exists(characters_dir):
        return
        
    for filename in os.listdir(characters_dir):
        if filename.endswith(".py"):
            filepath = os.path.join(characters_dir, filename)
            with open(filepath, "r") as f:
                code = f.read()
                
            local_scope = {"rotate_point": rotate_point, "tk": tk, "OUTLINE_COLOR": OUTLINE_COLOR}
            try:
                exec(code, globals(), local_scope)
                if "draw_custom_character" in local_scope:
                    # Nice formatting for the name (e.g. stick_man.py -> Stick Man)
                    shape_name = filename[:-3].replace("_", " ").title()
                    
                    CUSTOM_CHARACTERS[shape_name] = local_scope["draw_custom_character"]
                    if shape_name not in AVAILABLE_CHARACTERS:
                        AVAILABLE_CHARACTERS.append(shape_name)
            except Exception as e:
                print(f"Failed to load character {filename}: {e}")

# Load all characters dynamically
load_characters_from_folder()

# Add Generate with AI at the very end
AVAILABLE_CHARACTERS.append("Generate with AI...")

def draw_character_by_name(canvas, cx, cy, cell_size, direction, color_hex, character_name):
    """A helper function to draw the correct character based on its name."""
    if character_name in CUSTOM_CHARACTERS:
        CUSTOM_CHARACTERS[character_name](canvas, cx, cy, cell_size, direction, color_hex)
    else:
        # Default fallback
        draw_classic_karel(canvas, cx, cy, cell_size, direction, color_hex)
