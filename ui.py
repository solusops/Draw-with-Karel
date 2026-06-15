# ui.py
# This module handles drawing everything on the screen!

import tkinter as tk
from colors import *
from shapes import AVAILABLE_SHAPES, draw_shape_by_name

class KarelUI:
    def __init__(self, root, world, anim_state):
        self.root = root
        self.world = world
        self.anim_state = anim_state
        
        # What is the user currently holding?
        self.current_color = "Red"
        self.current_shape = "Classic Karel"
        
        self.setup_ui()
        
    def setup_ui(self):
        self.main_frame = tk.Frame(self.root, bg=BACKGROUND_COLOR)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # The main drawing canvas
        self.canvas = tk.Canvas(self.main_frame, bg=BACKGROUND_COLOR, highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # The control panel at the bottom
        self.control_panel = tk.Frame(self.root, bg=BACKGROUND_COLOR)
        self.control_panel.pack(fill=tk.X, side=tk.BOTTOM, padx=20, pady=10)
        
        self.setup_toolbar()
        
    def setup_toolbar(self):
        # Color palette
        palette_frame = tk.Frame(self.control_panel, bg=BACKGROUND_COLOR)
        palette_frame.pack(side=tk.LEFT, padx=10)
        
        tk.Label(palette_frame, text="Colors:", bg=BACKGROUND_COLOR, font=("Arial", 10, "bold")).pack(side=tk.LEFT)
        for c_name, c_hex in COLOR_PALETTE.items():
            btn = tk.Button(palette_frame, bg=c_hex, width=2, relief=tk.RAISED,
                            command=lambda c=c_name: self.set_color(c))
            btn.pack(side=tk.LEFT, padx=2)
            
        # Shape palette
        shape_frame = tk.Frame(self.control_panel, bg=BACKGROUND_COLOR)
        shape_frame.pack(side=tk.LEFT, padx=20)
        
        tk.Label(shape_frame, text="Shapes:", bg=BACKGROUND_COLOR, font=("Arial", 10, "bold")).pack(side=tk.LEFT)
        
        # Create a dropdown for shapes so kids can pick easily
        self.shape_var = tk.StringVar(self.root)
        self.shape_var.set(AVAILABLE_SHAPES[0]) # default
        
        shape_menu = tk.OptionMenu(shape_frame, self.shape_var, *AVAILABLE_SHAPES, command=self.set_shape)
        shape_menu.config(font=("Arial", 10))
        shape_menu.pack(side=tk.LEFT)
            
        # Actions
        actions_frame = tk.Frame(self.control_panel, bg=BACKGROUND_COLOR)
        actions_frame.pack(side=tk.LEFT, padx=20)
        
        self.btn_clear = tk.Button(actions_frame, text="Clear Board", font=("Arial", 10, "bold"),
                                   bg="#EF4444", fg="white")
        self.btn_clear.pack(side=tk.LEFT, padx=5)
        
        self.btn_play = tk.Button(actions_frame, text="Play", font=("Arial", 10, "bold"),
                                  bg="#10B981", fg="white", width=8)
        self.btn_play.pack(side=tk.LEFT, padx=5)
        
        # Submission Text!
        sub_frame = tk.Frame(self.control_panel, bg=BACKGROUND_COLOR)
        sub_frame.pack(side=tk.RIGHT, padx=10)
        tk.Label(sub_frame, text="Submission by Anshuman Singh", bg=BACKGROUND_COLOR, 
                 font=("Arial", 10, "italic"), fg="#4B5563").pack()

    def set_color(self, color_name):
        self.current_color = color_name
        
    def set_shape(self, shape_name):
        self.current_shape = shape_name

    def draw_grid(self, width, height, cell_size):
        """Draws the grid lines."""
        self.canvas.delete("all")
        
        for col in range(self.world.grid_size + 1):
            x = col * cell_size
            self.canvas.create_line(x, 0, x, height, fill=GRID_LINE_COLOR, width=1)
        for row in range(self.world.grid_size + 1):
            y = row * cell_size
            self.canvas.create_line(0, y, width, y, fill=GRID_LINE_COLOR, width=1)

    def draw_loop_highlights(self, cell_size, cycles, node_to_head, cycle_heads):
        """Draws yellow boxes behind Karels that are part of a loop."""
        for pos in list(self.world.karels.keys()):
            if pos in node_to_head:
                x0 = pos[0] * cell_size
                y0 = pos[1] * cell_size
                x1 = x0 + cell_size
                y1 = y0 + cell_size
                
                head = node_to_head[pos]
                speed = self.anim_state.loop_speeds.get(head, 0)
                
                # If they are going super fast, make it red!
                bg_color = SPEED_BURST_COLOR if speed == 2 else HIGHLIGHT_COLOR
                
                self.canvas.create_rectangle(x0, y0, x1, y1, fill=bg_color, outline="")
                
    def draw_karels(self, cell_size, node_to_head, cycle_heads):
        """Draws all the Karels, including the smooth sliding animation."""
        from shapes import get_dir_delta
        
        for pos, data in self.world.karels.items():
            col, row = pos
            direction = data["direction"]
            color_hex = COLOR_PALETTE.get(data.get("color", "Red"), "#EF4444")
            shape_name = data.get("shape", "Classic Karel")
            
            # Figure out where to draw it (might be sliding!)
            draw_col = col
            draw_row = row
            
            if self.anim_state.is_playing and pos in node_to_head:
                head = node_to_head[pos]
                progress = self.anim_state.visual_progress.get(head, 0.0)
                
                dx, dy = get_dir_delta(direction)
                
                # Slide smoothly to the next cell
                draw_col = col + (dx * progress)
                draw_row = row + (dy * progress)
                
                # Handle wrap-around visually (if it crosses the edge, it just appears on the other side)
                # For simplicity, we just modulo the drawing coordinates. It might jump visually, 
                # but that's perfectly fine for a beginner version!
                draw_col = draw_col % self.world.logical_grid_size
                draw_row = draw_row % self.world.logical_grid_size

            # Center of the cell
            cx = (draw_col + 0.5) * cell_size
            cy = (draw_row + 0.5) * cell_size
            
            # Draw the chosen shape!
            draw_shape_by_name(self.canvas, cx, cy, cell_size, direction, color_hex, shape_name)
            
    def draw_speed_buttons(self, cell_size, cycle_heads):
        """Draws tiny buttons on the head of each loop to change speed."""
        for head in cycle_heads:
            x0 = head[0] * cell_size
            y0 = head[1] * cell_size
            
            speed = self.anim_state.loop_speeds.get(head, 0)
            text = "▶" if speed == 0 else "▶▶" if speed == 1 else "⚡"
            
            # Draw a tiny box with text inside
            self.canvas.create_rectangle(x0 + 2, y0 + 2, x0 + 25, y0 + 25, fill="white", outline="black")
            self.canvas.create_text(x0 + 13, y0 + 13, text=text, font=("Arial", 10, "bold"), fill="black")
