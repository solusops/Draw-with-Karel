# main.py
# Welcome to Draw with Karel!
# This is the main file that runs the entire program.

import tkinter as tk
import json
import os
from world import World
from animation import AnimationState, advance_simulation, toggle_loop_speed
from ui import KarelUI
from character import get_next_direction
from path_finding import detect_loops_and_chains

class KarelApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Draw with Karel")
        self.root.geometry("1100x800")
        self.root.configure(bg="#F3F4F6")
        
        # Initialize our game state
        self.world = World(initial_grid_size=3)
        self.anim_state = AnimationState()
        
        # Initialize the User Interface (UI)
        self.ui = KarelUI(self.root, self.world, self.anim_state)
        
        self.pan_x = 0
        self.pan_y = 0
        self.is_panning = False
        self.long_press_timer = None
        self.start_click_x = 0
        self.start_click_y = 0
        
        # Bind events
        self.bind_events()
        
        # Start the game loop
        self.last_update_time = None
        self.update_canvas()
        self.animate_loop()

    def bind_events(self):
        # Mouse clicks
        self.last_placed_direction = "East"
        self.ui.canvas.bind("<ButtonPress-1>", self.on_left_click_press)
        self.ui.canvas.bind("<B1-Motion>", self.on_left_click_drag)
        self.ui.canvas.bind("<ButtonRelease-1>", self.on_left_click_release)
        self.ui.canvas.bind("<Button-3>", self.on_right_click)
        self.ui.canvas.bind("<B3-Motion>", self.on_right_click_drag)
        
        # Mouse wheel (scrolling)
        # Windows/Mac
        self.ui.canvas.bind("<MouseWheel>", self.on_mouse_wheel)
        # Linux
        self.ui.canvas.bind("<Button-4>", self.on_mouse_wheel)
        self.ui.canvas.bind("<Button-5>", self.on_mouse_wheel)
        
        # Buttons
        self.ui.btn_clear.config(command=self.clear_board)
        self.ui.btn_play.config(command=self.toggle_play)
        self.ui.btn_export.config(command=self.export_config)
        self.ui.btn_import.config(command=self.import_config)

    def get_cell_from_click(self, event):
        """Helper to convert a mouse click into grid coordinates (col, row)."""
        width = self.ui.canvas.winfo_width()
        height = self.ui.canvas.winfo_height()
        
        if width <= 1 or height <= 1:
            return None, None
            
        cell_size = min(width, height) / self.world.grid_size
        col = int((event.x - self.pan_x) // cell_size)
        row = int((event.y - self.pan_y) // cell_size)
        
        return col, row

    def start_pan_mode(self):
        self.is_panning = True
        self.long_press_timer = None
        self.ui.canvas.config(cursor="fleur")
        
    def on_left_click_press(self, event):
        self.start_click_x = event.x
        self.start_click_y = event.y
        self.is_panning = False
        
        # Start a 300ms timer for long press
        if self.long_press_timer is not None:
            self.root.after_cancel(self.long_press_timer)
        self.long_press_timer = self.root.after(300, self.start_pan_mode)
        
    def on_left_click_drag(self, event):
        if self.is_panning:
            # Pan the screen
            dx = event.x - self.start_click_x
            dy = event.y - self.start_click_y
            self.pan_x += dx
            self.pan_y += dy
            self.start_click_x = event.x
            self.start_click_y = event.y
            self.update_canvas()
        else:
            # If we move more than 5 pixels before the timer fires, it's a draw drag!
            if abs(event.x - self.start_click_x) > 5 or abs(event.y - self.start_click_y) > 5:
                if self.long_press_timer is not None:
                    self.root.after_cancel(self.long_press_timer)
                    self.long_press_timer = None
                    
                col, row = self.get_cell_from_click(event)
                if col is None: return
                if self.world.get_karel(col, row) is None:
                    self.world.add_karel(col, row, self.last_placed_direction, self.ui.current_color)
                    self.world.karels[(col, row)]["shape"] = self.ui.current_shape
                    self.update_canvas()
                    
    def on_left_click_release(self, event):
        self.ui.canvas.config(cursor="")
        
        if self.long_press_timer is not None:
            # We released before the long press triggered! This was a normal click.
            self.root.after_cancel(self.long_press_timer)
            self.long_press_timer = None
            
            # Normal click logic (place or rotate Karel)
            col, row = self.get_cell_from_click(event)
            if col is None: return
                
            # Speed buttons
            if self.anim_state.is_playing:
                cycles, node_to_head, cycle_heads = detect_loops_and_chains(self.world)
                for head in cycle_heads:
                    if col == head[0] and row == head[1]:
                        toggle_loop_speed(self.anim_state, head)
                        self.update_canvas()
                        return
            
            karel = self.world.get_karel(col, row)
            if karel is None:
                self.world.add_karel(col, row, self.last_placed_direction, self.ui.current_color)
                self.world.karels[(col, row)]["shape"] = self.ui.current_shape
            else:
                karel["direction"] = get_next_direction(karel["direction"])
                self.last_placed_direction = karel["direction"]
                
            self.update_canvas()
            
        self.is_panning = False
        
    def on_right_click_drag(self, event):
        """Erases Karels when dragging with right click."""
        col, row = self.get_cell_from_click(event)
        if col is not None and self.world.get_karel(col, row) is not None:
            self.world.remove_karel(col, row)
            self.update_canvas()

    def on_right_click(self, event):
        """When the user right clicks (to delete)."""
        col, row = self.get_cell_from_click(event)
        if col is not None:
            self.world.remove_karel(col, row)
            self.update_canvas()

    def on_mouse_wheel(self, event):
        """When the user scrolls the mouse wheel to zoom in/out."""
        # A positive delta means scrolling UP (zoom in).
        if hasattr(event, 'delta') and event.delta != 0:
            if event.delta > 0:
                self.world.zoom_in()
            else:
                self.world.zoom_out()
        elif hasattr(event, 'num'):
            if event.num == 4:
                self.world.zoom_in()
            elif event.num == 5:
                self.world.zoom_out()
                
        self.update_canvas()

    def clear_board(self):
        """Clears everything instantly! No dialog boxes."""
        self.world.clear()
        
        # Reset animation state without replacing the object
        self.anim_state.is_playing = False
        self.anim_state.loop_speeds.clear()
        self.anim_state.loop_accumulators.clear()
        self.anim_state.visual_progress.clear()
        
        self.ui.btn_play.config(text="Play", bg="#10B981")
        self.update_canvas()

    def export_config(self):
        """Saves the current board to config.json"""
        data = {
            "grid_size": self.world.grid_size,
            "karels": {f"{c},{r}": v for (c, r), v in self.world.karels.items()}
        }
        with open("config.json", "w") as f:
            json.dump(data, f, indent=4)
        print("Config exported successfully to config.json")

    def import_config(self):
        """Loads the board from config.json"""
        if not os.path.exists("config.json"):
            print("config.json not found!")
            return
            
        try:
            with open("config.json", "r") as f:
                data = json.load(f)
            
            self.clear_board()
            self.world.grid_size = data.get("grid_size", 3)
            self.world.logical_grid_size = self.world.grid_size
            
            for k_str, v in data.get("karels", {}).items():
                c, r = map(int, k_str.split(","))
                self.world.karels[(c, r)] = v
                
            self.update_canvas()
            print("Config imported successfully from config.json")
        except Exception as e:
            print(f"Failed to import config: {e}")

    def toggle_play(self):
        """Starts or stops the animation."""
        self.anim_state.is_playing = not self.anim_state.is_playing
        
        if self.anim_state.is_playing:
            self.ui.btn_play.config(text="Pause", bg="#F59E0B")
            # We don't need to sync logical grid bounds anymore! The world is infinite.
        else:
            self.ui.btn_play.config(text="Play", bg="#10B981")
            
        self.update_canvas()

    def update_canvas(self):
        self.ui.canvas.delete("all")
        
        width = self.ui.canvas.winfo_width()
        height = self.ui.canvas.winfo_height()
        
        if width <= 1 or height <= 1:
            return
            
        cell_size = min(width, height) / self.world.grid_size
        
        # 1. Draw the background grid
        self.ui.draw_grid(width, height, cell_size, self.pan_x, self.pan_y)
        
        # Calculate loops ONLY if we are playing
        cycles, node_to_head, cycle_heads = [], {}, []
        if self.anim_state.is_playing:
            cycles, node_to_head, cycle_heads = detect_loops_and_chains(self.world)
            
        # 2. Draw yellow highlight blocks for active loops
        if self.anim_state.is_playing:
            self.ui.draw_loop_highlights(cell_size, cycles, node_to_head, cycle_heads, self.pan_x, self.pan_y)
            
        # 3. Draw all Karels
        self.ui.draw_karels(cell_size, node_to_head, cycle_heads, self.pan_x, self.pan_y)
        
        # 4. Draw speed control buttons on the loop heads
        if self.anim_state.is_playing:
            self.ui.draw_speed_buttons(cell_size, cycle_heads, self.pan_x, self.pan_y)

    def animate_loop(self):
        """This function calls itself 60 times a second to run the game."""
        dt_ms = 16  # Approximately 60 frames per second
        
        if self.anim_state.is_playing:
            cycles, node_to_head, cycle_heads = detect_loops_and_chains(self.world)
            step_occurred = advance_simulation(self.world, self.anim_state, node_to_head, cycle_heads, dt_ms)
            
            # We always update canvas while playing to show the smooth sliding progress
            self.update_canvas()
            
        # Ask Tkinter to run this function again in ~16 milliseconds
        self.root.after(dt_ms, self.animate_loop)

if __name__ == "__main__":
    root = tk.Tk()
    app = KarelApp(root)
    root.mainloop()
