import tkinter as tk
from character import rotate_point
from colors import OUTLINE_COLOR

def draw_custom_character(canvas, cx, cy, cell_size, direction, color_hex):
    line_width = max(2, int(cell_size * 0.06))
    
    head_pts = [(0.1, -0.1), (0.3, -0.1), (0.3, 0.1), (0.1, 0.1)]
    head_rot = [rotate_point(x, y, direction) for x, y in head_pts]
    head_screen = [coord for pt in head_rot for coord in (cx + pt[0]*cell_size, cy + pt[1]*cell_size)]
    canvas.create_polygon(head_screen, fill=color_hex, outline=OUTLINE_COLOR, width=line_width)
    
    body_pts = [(-0.1, 0), (0.1, 0)]
    body_rot = [rotate_point(x, y, direction) for x, y in body_pts]
    body_screen = [coord for pt in body_rot for coord in (cx + pt[0]*cell_size, cy + pt[1]*cell_size)]
    canvas.create_line(body_screen, fill=OUTLINE_COLOR, width=line_width)
    
    arms_pts = [(0, -0.2), (0, 0.2)]
    arms_rot = [rotate_point(x, y, direction) for x, y in arms_pts]
    arms_screen = [coord for pt in arms_rot for coord in (cx + pt[0]*cell_size, cy + pt[1]*cell_size)]
    canvas.create_line(arms_screen, fill=OUTLINE_COLOR, width=line_width)
    
    leg1_pts = [(-0.1, 0), (-0.3, -0.15)]
    leg2_pts = [(-0.1, 0), (-0.3, 0.15)]
    for leg in [leg1_pts, leg2_pts]:
        leg_rot = [rotate_point(x, y, direction) for x, y in leg]
        leg_screen = [coord for pt in leg_rot for coord in (cx + pt[0]*cell_size, cy + pt[1]*cell_size)]
        canvas.create_line(leg_screen, fill=OUTLINE_COLOR, width=line_width)
