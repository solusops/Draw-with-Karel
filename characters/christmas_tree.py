from character import rotate_point
from colors import OUTLINE_COLOR

def draw_custom_character(canvas, cx, cy, cell_size, direction, color_hex):
    line_width = max(2, int(cell_size * 0.06))
    
    trunk_pts = [(-0.4, -0.1), (-0.2, -0.1), (-0.2, 0.1), (-0.4, 0.1)]
    trunk_rot = [rotate_point(x, y, direction) for x, y in trunk_pts]
    trunk_screen = [coord for pt in trunk_rot for coord in (cx + pt[0]*cell_size, cy + pt[1]*cell_size)]
    canvas.create_polygon(trunk_screen, fill="#8B4513", outline=OUTLINE_COLOR, width=line_width)
    
    tiers = [
        [(-0.2, -0.4), (0.1, 0), (-0.2, 0.4)],
        [(0.0, -0.3), (0.25, 0), (0.0, 0.3)],
        [(0.15, -0.2), (0.4, 0), (0.15, 0.2)]
    ]
    
    for tier in tiers:
        tier_rot = [rotate_point(x, y, direction) for x, y in tier]
        tier_screen = [coord for pt in tier_rot for coord in (cx + pt[0]*cell_size, cy + pt[1]*cell_size)]
        canvas.create_polygon(tier_screen, fill=color_hex, outline=OUTLINE_COLOR, width=line_width)
