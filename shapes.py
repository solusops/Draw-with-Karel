# shapes.py
# This module contains the code to draw different shapes in our world.
# Kids can easily add their own shapes here! Just create a new function
# like 'draw_my_shape' and follow the examples below.
#
# Remember: The base shape should face "East" (Right). The rotate_point
# function will automatically turn your shape when it faces North, West, or South!

import tkinter as tk
from colors import OUTLINE_COLOR

# --- DIRECTION HELPERS ---

DIRECTIONS = ["East", "South", "West", "North"]

def get_next_direction(current_direction):
    """Returns the next direction when you click a shape (turns 90 degrees clockwise)."""
    for i in range(len(DIRECTIONS)):
        if DIRECTIONS[i] == current_direction:
            next_index = (i + 1) % 4
            return DIRECTIONS[next_index]
    return "East"

def get_dir_delta(direction):
    """Returns how much to move (x, y) for a given direction."""
    if direction == "East":
        return 1, 0   # Right
    elif direction == "West":
        return -1, 0  # Left
    elif direction == "North":
        return 0, -1  # Up
    elif direction == "South":
        return 0, 1   # Down
    return 0, 0

def rotate_point(x, y, direction):
    """Rotates an (x, y) point so the shape faces the right way."""
    if direction == "East":
        return x, y
    elif direction == "North":
        return y, -x
    elif direction == "West":
        return -x, -y
    elif direction == "South":
        return -y, x
    return x, y

# --- SHAPE DRAWING FUNCTIONS ---

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

def draw_arrow(canvas, cx, cy, cell_size, direction, color_hex):
    """
    Draws a simple arrow shape.
    """
    line_width = max(2, int(cell_size * 0.06))
    
    # Arrow points East (Right)
    arrow_pts = [(-0.2, -0.15), (0.1, -0.15), (0.1, -0.3), (0.4, 0), (0.1, 0.3), (0.1, 0.15), (-0.2, 0.15)]
    arrow_rot = [rotate_point(x, y, direction) for x, y in arrow_pts]
    arrow_screen = [coord for pt in arrow_rot for coord in (cx + pt[0]*cell_size, cy + pt[1]*cell_size)]
    canvas.create_polygon(arrow_screen, fill=color_hex, outline=OUTLINE_COLOR, width=line_width)

def draw_christmas_tree(canvas, cx, cy, cell_size, direction, color_hex):
    """
    Draws a Christmas tree shape.
    """
    line_width = max(2, int(cell_size * 0.06))
    
    # Tree "points" East (top of tree faces Right)
    # Trunk
    trunk_pts = [(-0.4, -0.1), (-0.2, -0.1), (-0.2, 0.1), (-0.4, 0.1)]
    trunk_rot = [rotate_point(x, y, direction) for x, y in trunk_pts]
    trunk_screen = [coord for pt in trunk_rot for coord in (cx + pt[0]*cell_size, cy + pt[1]*cell_size)]
    canvas.create_polygon(trunk_screen, fill="#8B4513", outline=OUTLINE_COLOR, width=line_width)
    
    # Leaves (3 triangles)
    leaves_pts = [
        # Bottom tier
        (-0.2, -0.4), (0.1, 0), (-0.2, 0.4),
        # Middle tier
        (0.0, -0.3), (0.25, 0), (0.0, 0.3),
        # Top tier
        (0.15, -0.2), (0.4, 0), (0.15, 0.2)
    ]
    
    # Draw them in pieces so we can layer them
    tiers = [
        [(-0.2, -0.4), (0.1, 0), (-0.2, 0.4)],
        [(0.0, -0.3), (0.25, 0), (0.0, 0.3)],
        [(0.15, -0.2), (0.4, 0), (0.15, 0.2)]
    ]
    
    for tier in tiers:
        tier_rot = [rotate_point(x, y, direction) for x, y in tier]
        tier_screen = [coord for pt in tier_rot for coord in (cx + pt[0]*cell_size, cy + pt[1]*cell_size)]
        canvas.create_polygon(tier_screen, fill=color_hex, outline=OUTLINE_COLOR, width=line_width)

def draw_stick_man(canvas, cx, cy, cell_size, direction, color_hex):
    """
    Draws a stick man facing forward.
    """
    line_width = max(2, int(cell_size * 0.06))
    
    # Head
    # Let's draw a circle. Circles don't rotate easily with our rotate_point,
    # so we will make a small polygon for the head.
    # Stick man points East (faces Right).
    # Center of head is at x=0.2, y=0.
    head_pts = [(0.1, -0.1), (0.3, -0.1), (0.3, 0.1), (0.1, 0.1)]
    head_rot = [rotate_point(x, y, direction) for x, y in head_pts]
    head_screen = [coord for pt in head_rot for coord in (cx + pt[0]*cell_size, cy + pt[1]*cell_size)]
    canvas.create_polygon(head_screen, fill=color_hex, outline=OUTLINE_COLOR, width=line_width)
    
    # Body (line from x=-0.1 to x=0.1)
    body_pts = [(-0.1, 0), (0.1, 0)]
    body_rot = [rotate_point(x, y, direction) for x, y in body_pts]
    body_screen = [coord for pt in body_rot for coord in (cx + pt[0]*cell_size, cy + pt[1]*cell_size)]
    canvas.create_line(body_screen, fill=OUTLINE_COLOR, width=line_width)
    
    # Arms
    arms_pts = [(0, -0.2), (0, 0.2)]
    arms_rot = [rotate_point(x, y, direction) for x, y in arms_pts]
    arms_screen = [coord for pt in arms_rot for coord in (cx + pt[0]*cell_size, cy + pt[1]*cell_size)]
    canvas.create_line(arms_screen, fill=OUTLINE_COLOR, width=line_width)
    
    # Legs
    leg1_pts = [(-0.1, 0), (-0.3, -0.15)]
    leg2_pts = [(-0.1, 0), (-0.3, 0.15)]
    for leg in [leg1_pts, leg2_pts]:
        leg_rot = [rotate_point(x, y, direction) for x, y in leg]
        leg_screen = [coord for pt in leg_rot for coord in (cx + pt[0]*cell_size, cy + pt[1]*cell_size)]
        canvas.create_line(leg_screen, fill=OUTLINE_COLOR, width=line_width)

# A master list of available shapes so the UI can cycle through them!
AVAILABLE_SHAPES = ["Classic Karel", "Arrow", "Christmas Tree", "Stick Man"]

def draw_shape_by_name(canvas, cx, cy, cell_size, direction, color_hex, shape_name):
    """A helper function to draw the correct shape based on its name."""
    if shape_name == "Arrow":
        draw_arrow(canvas, cx, cy, cell_size, direction, color_hex)
    elif shape_name == "Christmas Tree":
        draw_christmas_tree(canvas, cx, cy, cell_size, direction, color_hex)
    elif shape_name == "Stick Man":
        draw_stick_man(canvas, cx, cy, cell_size, direction, color_hex)
    else:
        draw_classic_karel(canvas, cx, cy, cell_size, direction, color_hex)
