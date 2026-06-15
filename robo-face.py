# Draw with Karel - Exported Drawing
# Run this script standalone to view your drawing, or load it in the editor.

GRID_SIZE = 5
KARELS = [
    {"x": 0, "y": 0, "direction": "East", "color": "Red"},
    {"x": 1, "y": 0, "direction": "South", "color": "Blue"},
    {"x": 1, "y": 1, "direction": "West", "color": "Yellow"},
    {"x": 0, "y": 1, "direction": "North", "color": "Purple"},
    {"x": 3, "y": 0, "direction": "East", "color": "Blue"},
    {"x": 4, "y": 0, "direction": "South", "color": "Green"},
    {"x": 4, "y": 1, "direction": "West", "color": "Orange"},
    {"x": 3, "y": 1, "direction": "North", "color": "Cyan"},
    {"x": 1, "y": 3, "direction": "North", "color": "Red"},
    {"x": 2, "y": 3, "direction": "East", "color": "Blue"},
    {"x": 3, "y": 3, "direction": "East", "color": "Yellow"},
    {"x": 3, "y": 4, "direction": "South", "color": "Purple"},
    {"x": 2, "y": 4, "direction": "West", "color": "Orange"},
    {"x": 1, "y": 4, "direction": "West", "color": "Pink"},
]

# --- STANDALONE VIEWER CODE ---
import tkinter as tk

class KarelStaticViewer:
    def __init__(self, root, grid_size, karels):
        self.root = root
        self.root.title("Karel Drawing Viewer")
        self.root.geometry("700x750")
        self.root.minsize(450, 500)
        
        self.grid_size = grid_size
        self.logical_grid_size = grid_size
        self.karels = {(k["x"], k["y"]): {"direction": k["direction"], "color": k["color"]} for k in karels}
        self.is_playing = False
        
        # Simulation loop variables
        self.loop_speeds = {}
        self.loop_accumulators = {}
        self.loop_steps_count = {}
        self.speed_buttons = {}
        self._head_to_ordered = {}
        
        # Palettes for rendering
        self.color_palette = {
            "Red": "#EF4444", "Blue": "#3B82F6", "Green": "#10B981", "Yellow": "#FBBF24",
            "Purple": "#8B5CF6", "Orange": "#F97316", "Pink": "#EC4899", "Cyan": "#06B6D4"
        }
        
        # Canvas Layout (Canvas Frame + Help underneath)
        self.canvas_frame = tk.Frame(self.root)
        self.canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        self.canvas = tk.Canvas(self.canvas_frame, bg="#FAF9F6", highlightthickness=0, bd=0)
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=(10, 5))
        
        # Help Frame placed horizontally below canvas
        self.help_frame = tk.LabelFrame(self.canvas_frame, text="Controls Help", font=("Segoe UI", 9, "bold"), padx=15, pady=8)
        self.help_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        help_text = (
            "\U0001f5b1\ufe0f Scroll Wheel: Zoom / Adjust grid size\n"
            "\U0001f5b1\ufe0f Left Click:   Place robot (on empty cell)\n"
            "                Rotate robot (90\u00b0 turn on occupied cell)\n"
            "\U0001f5b1\ufe0f Click & Drag: Paint cells with robots\n"
            "\U0001f5b1\ufe0f Double-Click: Remove robot from cell"
        )
        self.help_lbl = tk.Label(self.help_frame, text=help_text, justify=tk.LEFT, anchor=tk.W, font=("Consolas", 9), bg="#FAF9F6", fg="#4B5563")
        self.help_lbl.pack(fill=tk.X)
        
        # Control bar at bottom
        self.control_frame = tk.Frame(self.root, bg="#F3F4F6", height=50)
        self.control_frame.pack(fill=tk.X, side=tk.BOTTOM, padx=10, pady=(0, 10))
        
        self.play_btn = tk.Button(
            self.control_frame, 
            text="\u25b6 Play Simulation", 
            font=("Segoe UI", 10, "bold"), 
            fg="#10B981", 
            command=self.toggle_play,
            relief=tk.GROOVE,
            bd=1
        )
        self.play_btn.pack(side=tk.LEFT, padx=15, pady=5)
        
        self.info_lbl = tk.Label(
            self.control_frame, 
            text=f"Grid: {self.grid_size}x{self.grid_size} | Karels: {len(self.karels)}", 
            font=("Segoe UI", 9, "bold"),
            bg="#F3F4F6",
            fg="#4B5563"
        )
        self.info_lbl.pack(side=tk.RIGHT, padx=15, pady=5)
        
        self.canvas.bind("<Configure>", lambda e: self.draw())
        self.canvas.bind("<Button-1>", self.handle_click)
        self.canvas.bind("<MouseWheel>", self.handle_mouse_wheel)
        self.canvas.bind("<Button-4>", self.handle_mouse_wheel)
        self.canvas.bind("<Button-5>", self.handle_mouse_wheel)
        
    def handle_click(self, event):
        for head, bbox in self.speed_buttons.items():
            x1, y1, x2, y2 = bbox
            if x1 <= event.x <= x2 and y1 <= event.y <= y2:
                curr_speed = self.loop_speeds.get(head, 0)
                self.loop_speeds[head] = (curr_speed + 1) % 3
                self.draw()
                return

    def handle_mouse_wheel(self, event):
        change = 0
        if event.num == 4 or (event.delta and event.delta > 0):
            change = 1
        elif event.num == 5 or (event.delta and event.delta < 0):
            change = -1
            
        if change != 0:
            self.adjust_grid_size(change)

    def adjust_grid_size(self, change):
        new_size = self.grid_size + change
        if 1 <= new_size <= 100:
            self.grid_size = new_size
            self.draw()
            self.info_lbl.config(text=f"Grid: {self.grid_size}x{self.grid_size} | Karels: {len(self.karels)}")

    def toggle_play(self):
        self.is_playing = not self.is_playing
        if self.is_playing:
            self.play_btn.config(text="\u23f8 Pause Simulation", fg="#EF4444")
            self.animate_tick()
        else:
            self.play_btn.config(text="\u25b6 Play Simulation", fg="#10B981")
            
    def animate_tick(self):
        if not self.is_playing:
            return
        try:
            self.run_simulation_step()
        except Exception:
            pass
        self.root.after(50, self.animate_tick)
        
    def get_dir_delta(self, direction):
        if direction == "East": return 1, 0
        elif direction == "West": return -1, 0
        elif direction == "North": return 0, -1
        elif direction == "South": return 0, 1
        return 0, 0
        
    def detect_loops_and_chains(self):
        cycles = []
        ordered_cycles = []
        node_to_head = {}
        visited_global = set()
        
        for start in list(self.karels.keys()):
            if start in visited_global:
                continue
            path = []
            visited_local = {}
            curr = start
            while curr in self.karels:
                if curr in visited_local:
                    cycle_start_idx = visited_local[curr]
                    cycle = path[cycle_start_idx:]
                    if len(cycle) >= 4:
                        cycles.append(set(cycle))
                        ordered_cycles.append(list(cycle))
                    break
                if curr in visited_global:
                    break
                visited_local[curr] = len(path)
                path.append(curr)
                col, row = curr
                data = self.karels[curr]
                dx, dy = self.get_dir_delta(data["direction"])
                curr = ((col + dx) % self.logical_grid_size, (row + dy) % self.logical_grid_size)
            for node in path:
                visited_global.add(node)
                
        cycle_heads = set()
        self._head_to_ordered = {}
        for i, cycle in enumerate(cycles):
            head = min(cycle, key=lambda p: (p[1], p[0]))
            cycle_heads.add(head)
            self._head_to_ordered[head] = ordered_cycles[i]
            for node in cycle:
                node_to_head[node] = head
                
        moving = set(node_to_head.keys())
        changed = True
        while changed:
            changed = False
            for pos, data in self.karels.items():
                if pos in moving:
                    continue
                col, row = pos
                direction = data["direction"]
                dx, dy = self.get_dir_delta(direction)
                front_pos = ((col + dx) % self.logical_grid_size, (row + dy) % self.logical_grid_size)
                if front_pos in moving:
                    front_data = self.karels[front_pos]
                    if front_data["direction"] == direction:
                        node_to_head[pos] = node_to_head[front_pos]
                        moving.add(pos)
                        changed = True
                        
        return cycles, node_to_head, cycle_heads

    def run_simulation_step(self):
        cycles, node_to_head, cycle_heads = self.detect_loops_and_chains()
        
        self.loop_speeds = {h: self.loop_speeds[h] for h in self.loop_speeds if h in cycle_heads}
        self.loop_accumulators = {h: self.loop_accumulators[h] for h in self.loop_accumulators if h in cycle_heads}
        self.loop_steps_count = {h: self.loop_steps_count[h] for h in self.loop_steps_count if h in cycle_heads}
        
        for head in cycle_heads:
            self.loop_accumulators[head] = self.loop_accumulators.get(head, 0) + 50
            speed = self.loop_speeds.get(head, 0)
            threshold = 500 if speed == 0 else 250 if speed == 1 else 100
            if self.loop_accumulators[head] >= threshold:
                self.loop_accumulators[head] -= threshold
                self.loop_steps_count[head] = (self.loop_steps_count.get(head, 0) + 1) % 2
                
                ordered = self._head_to_ordered.get(head, [])
                if len(ordered) >= 4:
                    colors = [self.karels[pos]["color"] for pos in ordered]
                    for i, pos in enumerate(ordered):
                        self.karels[pos]["color"] = colors[(i - 1) % len(colors)]
        
        self.draw()
        self.info_lbl.config(text=f"Grid: {self.grid_size}x{self.grid_size} | Karels: {len(self.karels)}")
        
    def draw(self):
        self.canvas.delete("all")
        self.speed_buttons.clear()
        
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        if w <= 1 or h <= 1:
            return
            
        cell_w = w / self.grid_size
        cell_h = h / self.grid_size
        
        # Draw Loop Highlights (dull yellow)
        cycles, node_to_head, cycle_heads = self.detect_loops_and_chains()
        highlight_color = "#FEF08A"
        cycle_cells = set()
        for cycle in cycles:
            cycle_cells.update(cycle)
        for (col, row) in cycle_cells:
            if col < self.grid_size and row < self.grid_size:
                self.canvas.create_rectangle(col*cell_w, row*cell_h, (col+1)*cell_w, (row+1)*cell_h, fill=highlight_color, outline="")
                
        # Draw grid
        for i in range(self.grid_size + 1):
            self.canvas.create_line(i * cell_w, 0, i * cell_w, h, fill="#E5E7EB", width=1)
            self.canvas.create_line(0, i * cell_h, w, i * cell_h, fill="#E5E7EB", width=1)
            
        # Draw Karel robots
        S = min(cell_w, cell_h)
        for (col, row), data in self.karels.items():
            if col < self.grid_size and row < self.grid_size:
                cx = col * cell_w + cell_w / 2
                cy = row * cell_h + cell_h / 2
                parent_head = node_to_head.get((col, row))
                
                if self.is_playing and parent_head is not None:
                    acc = self.loop_accumulators.get(parent_head, 0)
                    speed = self.loop_speeds.get(parent_head, 0)
                    threshold = 500 if speed == 0 else 250 if speed == 1 else 100
                    progress = min(1.0, acc / threshold)
                    
                    dx, dy = self.get_dir_delta(data["direction"])
                    cx += dx * progress * cell_w
                    cy += dy * progress * cell_h
                    
                self.draw_karel(cx, cy, S, data["direction"], self.color_palette.get(data["color"], "#EF4444"), col, row, parent_head)
                
        # Draw Speed Buttons
        for head in cycle_heads:
            col, row = head
            if col < self.grid_size and row < self.grid_size:
                x1 = col * cell_w + 4
                y1 = row * cell_h + 4
                x2 = x1 + 22
                y2 = y1 + 22
                self.canvas.create_oval(x1, y1, x2, y2, fill="#E5E7EB", outline="#9CA3AF", width=1, tags="speed_btn")
                speed = self.loop_speeds.get(head, 0)
                speed_text = "1x" if speed == 0 else "2x" if speed == 1 else "3x"
                self.canvas.create_text((x1 + x2) / 2, (y1 + y2) / 2, text=speed_text, font=("Segoe UI", 8, "bold"), fill="#1F2937", tags="speed_btn")
                self.speed_buttons[head] = (x1, y1, x2, y2)
                
    def rotate_point(self, x, y, direction):
        if direction == "East":
            return x, y
        elif direction == "North":
            return y, -x
        elif direction == "West":
            return -x, -y
        elif direction == "South":
            return -y, x
        return x, y
        
    def draw_karel(self, cx, cy, S, direction, color_hex, col=0, row=0, parent_head=None):
        outline_color = "#1F2937"
        line_width = max(2, int(S * 0.06))
        
        screen_fill = "#FFFFFF"
            
        # Body
        body_pts = [(-0.25, -0.35), (0.1, -0.35), (0.25, -0.2), (0.25, 0.35), (-0.1, 0.35), (-0.25, 0.2)]
        body_rot = [self.rotate_point(x, y, direction) for x, y in body_pts]
        body_screen = [coord for pt in body_rot for coord in (cx + pt[0]*S, cy + pt[1]*S)]
        self.canvas.create_polygon(body_screen, fill=color_hex, outline=outline_color, width=line_width)
        
        # Screen
        screen_pts = [(-0.12, -0.22), (0.12, -0.22), (0.12, 0.08), (-0.12, 0.08)]
        screen_rot = [self.rotate_point(x, y, direction) for x, y in screen_pts]
        screen_screen = [coord for pt in screen_rot for coord in (cx + pt[0]*S, cy + pt[1]*S)]
        self.canvas.create_polygon(screen_screen, fill=screen_fill, outline=outline_color, width=max(1, line_width//2))
        
        # Mouth
        mouth_pts = [(-0.06, 0.18), (0.06, 0.18)]
        mouth_rot = [self.rotate_point(x, y, direction) for x, y in mouth_pts]
        mouth_screen = [coord for pt in mouth_rot for coord in (cx + pt[0]*S, cy + pt[1]*S)]
        self.canvas.create_line(mouth_screen[0], mouth_screen[1], mouth_screen[2], mouth_screen[3], fill=outline_color, width=max(1.5, line_width//2))
        
        # Left foot
        left_foot_pts = [(-0.25, 0.08), (-0.35, 0.08), (-0.35, 0.18)]
        left_foot_rot = [self.rotate_point(x, y, direction) for x, y in left_foot_pts]
        left_foot_screen = [coord for pt in left_foot_rot for coord in (cx + pt[0]*S, cy + pt[1]*S)]
        self.canvas.create_line(left_foot_screen, fill=outline_color, width=line_width, capstyle=tk.PROJECTING, joinstyle=tk.MITER)
        
        # Bottom foot
        bottom_foot_pts = [(0.08, 0.35), (0.08, 0.45), (0.18, 0.45)]
        bottom_foot_rot = [self.rotate_point(x, y, direction) for x, y in bottom_foot_pts]
        bottom_foot_screen = [coord for pt in bottom_foot_rot for coord in (cx + pt[0]*S, cy + pt[1]*S)]
        self.canvas.create_line(bottom_foot_screen, fill=outline_color, width=line_width, capstyle=tk.PROJECTING, joinstyle=tk.MITER)

if __name__ == "__main__":
    root = tk.Tk()
    app = KarelStaticViewer(root, GRID_SIZE, KARELS)
    root.mainloop()
