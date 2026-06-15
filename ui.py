# ui.py
# This module handles drawing everything on the screen!

import tkinter as tk
from tkinter import messagebox
import threading
from colors import *
from character import AVAILABLE_CHARACTERS, draw_character_by_name
try:
    from ai_generator import generate_shape_code, save_and_load_shape
except ImportError:
    pass

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
        # We use a container frame for the toolbar so we can swap it out easily
        self.toolbar_container = tk.Frame(self.control_panel, bg=BACKGROUND_COLOR)
        self.toolbar_container.pack(fill=tk.X, expand=True)
        
        # The standard toolbar
        self.toolbar_frame = tk.Frame(self.toolbar_container, bg=BACKGROUND_COLOR)
        self.toolbar_frame.pack(fill=tk.X, expand=True)
        
        # The AI generator toolbar (hidden initially)
        self.ai_frame = tk.Frame(self.toolbar_container, bg=BACKGROUND_COLOR)
        
        # --- Standard Toolbar Components ---
        # Color palette
        palette_frame = tk.Frame(self.toolbar_frame, bg=BACKGROUND_COLOR)
        palette_frame.pack(side=tk.LEFT, padx=10)
        
        tk.Label(palette_frame, text="Colors:", bg=BACKGROUND_COLOR, font=("Arial", 10, "bold")).pack(side=tk.LEFT)
        for c_name, c_hex in COLOR_PALETTE.items():
            btn = tk.Button(palette_frame, bg=c_hex, width=2, relief=tk.RAISED,
                            command=lambda c=c_name: self.set_color(c))
            btn.pack(side=tk.LEFT, padx=2)
            
        # Shape palette
        shape_frame = tk.Frame(self.toolbar_frame, bg=BACKGROUND_COLOR)
        shape_frame.pack(side=tk.LEFT, padx=20)
        
        tk.Label(shape_frame, text="Shapes:", bg=BACKGROUND_COLOR, font=("Arial", 10, "bold")).pack(side=tk.LEFT)
        
        # Create a dropdown for shapes so kids can pick easily
        self.shape_var = tk.StringVar(self.root)
        self.shape_var.set(AVAILABLE_CHARACTERS[0]) # default
        
        self.shape_menu = tk.OptionMenu(shape_frame, self.shape_var, *AVAILABLE_CHARACTERS, command=self.set_shape)
        self.shape_menu.config(font=("Arial", 10))
        self.shape_menu.pack(side=tk.LEFT)
            
        # Actions
        actions_frame = tk.Frame(self.toolbar_frame, bg=BACKGROUND_COLOR)
        actions_frame.pack(side=tk.LEFT, padx=20)
        
        self.btn_clear = tk.Button(actions_frame, text="Clear Board", font=("Arial", 10, "bold"),
                                   bg="#EF4444", fg="white")
        self.btn_clear.pack(side=tk.LEFT, padx=5)
        
        self.btn_play = tk.Button(actions_frame, text="Play", font=("Arial", 10, "bold"),
                                  bg="#10B981", fg="white", width=8)
        self.btn_play.pack(side=tk.LEFT, padx=5)
        
        # Submission Text!
        sub_frame = tk.Frame(self.toolbar_frame, bg=BACKGROUND_COLOR)
        sub_frame.pack(side=tk.RIGHT, padx=10)
        tk.Label(sub_frame, text="Submission by Anshuman Singh", bg=BACKGROUND_COLOR, 
                 font=("Arial", 10, "italic"), fg="#4B5563").pack()
                 
        # --- AI Toolbar Components ---
        tk.Label(self.ai_frame, text="API Key:", bg=BACKGROUND_COLOR, font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=(5,2))
        self.api_entry = tk.Entry(self.ai_frame, width=25, show="*")
        self.api_entry.pack(side=tk.LEFT, padx=2)
        import os
        if "GEMINI_API_KEY" in os.environ:
            self.api_entry.insert(0, os.environ["GEMINI_API_KEY"])

        tk.Label(self.ai_frame, text="Describe:", bg=BACKGROUND_COLOR, font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=(15,2))
        self.desc_entry = tk.Entry(self.ai_frame, width=35)
        self.desc_entry.pack(side=tk.LEFT, padx=2)
        self.desc_entry.bind("<KeyRelease>", self.update_ai_btn)

        self.gen_btn = tk.Button(self.ai_frame, text="Cancel", font=("Arial", 10, "bold"), bg="#EF4444", fg="white", command=self.handle_ai_btn)
        self.gen_btn.pack(side=tk.LEFT, padx=10)
        
        self.status_lbl = tk.Label(self.ai_frame, text="", bg=BACKGROUND_COLOR, fg="blue", font=("Arial", 9))
        self.status_lbl.pack(side=tk.LEFT, padx=10)

    def set_color(self, color_name):
        self.current_color = color_name
        
    def set_shape(self, shape_name):
        if shape_name == "Generate with AI...":
            # Swap to AI inline toolbar
            self.toolbar_frame.pack_forget()
            self.ai_frame.pack(fill=tk.X, expand=True)
            self.status_lbl.config(text="")
            self.desc_entry.delete(0, 'end')
            self.update_ai_btn(None)
            
            # Revert the dropdown until generation is complete
            self.shape_var.set(self.current_shape)
        else:
            self.current_shape = shape_name

    def update_ai_btn(self, event):
        if self.desc_entry.get().strip():
            self.gen_btn.config(text="Enter", bg="#10B981") # Green means GO
        else:
            self.gen_btn.config(text="Cancel", bg="#EF4444") # Red means Stop/Cancel

    def handle_ai_btn(self):
        desc = self.desc_entry.get().strip()
        if not desc:
            # Cancel: Restore toolbar
            self.ai_frame.pack_forget()
            self.toolbar_frame.pack(fill=tk.X, expand=True)
        else:
            # Enter: Generate!
            api_key = self.api_entry.get().strip()
            self.gen_btn.config(state=tk.DISABLED)
            self.desc_entry.config(state=tk.DISABLED)
            self.status_lbl.config(text="Generating... Please wait.", fg="blue")
            threading.Thread(target=self.do_generate_shape, args=(api_key, desc), daemon=True).start()

    def do_generate_shape(self, api_key, desc):
        try:
            # Generate the code
            raw_code = generate_shape_code(api_key, desc)
            if raw_code.startswith("ERROR:"):
                self.root.after(0, lambda: self.finish_generation(False, raw_code))
                return
                
            self.root.after(0, lambda: self.status_lbl.config(text="Saving and loading character..."))
            
            # Save it and load it into the registry
            filepath = save_and_load_shape(desc, raw_code)
            
            self.root.after(0, lambda: self.finish_generation(True, f"Success! Saved to {filepath}"))
            
        except Exception as e:
            self.root.after(0, lambda: self.finish_generation(False, f"Error: {str(e)}"))

    def finish_generation(self, success, message):
        self.gen_btn.config(state=tk.NORMAL)
        self.desc_entry.config(state=tk.NORMAL)
        if success:
            # Restore toolbar
            self.ai_frame.pack_forget()
            self.toolbar_frame.pack(fill=tk.X, expand=True)
            
            # Update the dropdown menu!
            menu = self.shape_menu["menu"]
            menu.delete(0, "end")
            for shape in AVAILABLE_CHARACTERS:
                menu.add_command(label=shape, command=tk._setit(self.shape_var, shape, self.set_shape))
            
            # Select the newly generated shape
            desc = self.desc_entry.get().strip()
            self.shape_var.set(desc)
            self.set_shape(desc)
        else:
            self.status_lbl.config(text=message, fg="red")
            messagebox.showerror("Generation Error", message)

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
        from character import get_dir_delta
        
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
            draw_character_by_name(self.canvas, cx, cy, cell_size, direction, color_hex, shape_name)
            
    def draw_speed_buttons(self, cell_size, cycle_heads):
        """Draws tiny buttons on the head of each loop to change speed."""
        for head in cycle_heads:
            x0 = head[0] * cell_size
            y0 = head[1] * cell_size
            
            speed = self.anim_state.loop_speeds.get(head, 0)
            text = ">" if speed == 0 else ">>" if speed == 1 else "!"
            
            # Draw a tiny box with text inside
            self.canvas.create_rectangle(x0 + 2, y0 + 2, x0 + 25, y0 + 25, fill="white", outline="black")
            self.canvas.create_text(x0 + 13, y0 + 13, text=text, font=("Arial", 10, "bold"), fill="black")
