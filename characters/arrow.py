from character import rotate_point
from colors import OUTLINE_COLOR

def draw_custom_character(canvas, cx, cy, cell_size, direction, color_hex):
    line_width = max(2, int(cell_size * 0.06))
    
    arrow_pts = [(-0.2, -0.15), (0.1, -0.15), (0.1, -0.3), (0.4, 0), (0.1, 0.3), (0.1, 0.15), (-0.2, 0.15)]
    arrow_rot = [rotate_point(x, y, direction) for x, y in arrow_pts]
    arrow_screen = [coord for pt in arrow_rot for coord in (cx + pt[0]*cell_size, cy + pt[1]*cell_size)]
    canvas.create_polygon(arrow_screen, fill=color_hex, outline=OUTLINE_COLOR, width=line_width)
