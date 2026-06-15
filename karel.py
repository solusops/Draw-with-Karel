# karel.py
import tkinter as tk
from colors import OUTLINE_COLOR

# A list of directions in clockwise order.
# If a Karel is facing "East" and turns 90 degrees right, it will face "South".
DIRECTIONS = ["East", "South", "West", "North"]

def get_next_direction(current_direction):
    """
    Returns the next direction when Karel is clicked (turns 90 degrees clockwise).
    """
    for i in range(len(DIRECTIONS)):
        if DIRECTIONS[i] == current_direction:
            next_index = (i + 1) % 4
            return DIRECTIONS[next_index]
    return "East"

def get_dir_delta(direction):
    """
    Returns the (dx, dy) grid movement for a given direction.
    East = +1x (Right), West = -1x (Left), North = -1y (Up), South = +1y (Down)
    """
    if direction == "East":
        return 1, 0
    elif direction == "West":
        return -1, 0
    elif direction == "North":
        return 0, -1
    elif direction == "South":
        return 0, 1
    return 0, 0

def rotate_point(x, y, direction):
    """
    Rotates a point (x, y) based on the direction.
    Base shape faces East. 
    """
    if direction == "East":
        return x, y
    elif direction == "North":
        return y, -x
    elif direction == "West":
        return -x, -y
    elif direction == "South":
        return -y, x
    return x, y

def draw_karel_shape(canvas, cx, cy, cell_size, direction, color_hex):
    """
    Draws the Karel robot at center (cx, cy) on the canvas.
    This uses the classic "SIM card" style shape.
    """
    line_width = max(2, int(cell_size * 0.06))
    
    # Body: Classic beveled card shape
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
