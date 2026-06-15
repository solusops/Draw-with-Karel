import tkinter as tk
from tkinter import filedialog, messagebox
import ast
import re

# Theme colors
THEMES = {
    "light": {
        "bg": "#FFFFFF",
        "canvas_bg": "#FAF9F6",
        "grid_line": "#E5E7EB",
        "sidebar_bg": "#F3F4F6",
        "text": "#1F2937",
        "text_sec": "#4B5563",
        "accent": "#3B82F6",
        "border": "#D1D5DB",
        "button_bg": "#E5E7EB",
        "button_fg": "#1F2937",
        "active_button_bg": "#D1D5DB",
        "karel_outline": "#1F2937",
        "karel_head": "#D1D5DB"
    },
    "dark": {
        "bg": "#111827",
        "canvas_bg": "#1F2937",
        "grid_line": "#374151",
        "sidebar_bg": "#111827",
        "text": "#F9FAFB",
        "text_sec": "#9CA3AF",
        "accent": "#60A5FA",
        "border": "#4B5563",
        "button_bg": "#374151",
        "button_fg": "#F9FAFB",
        "active_button_bg": "#4B5563",
        "karel_outline": "#F9FAFB",
        "karel_head": "#4B5563"
    }
}

COLOR_PALETTE = {
    "Red": "#EF4444",
    "Blue": "#3B82F6",
    "Green": "#10B981",
    "Yellow": "#FBBF24",
    "Purple": "#8B5CF6",
    "Orange": "#F97316",
    "Pink": "#EC4899",
    "Cyan": "#06B6D4"
}

class KarelDrawingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Draw with Karel")
        self.root.geometry("950x750")
        self.root.minsize(750, 550)
        
        # State variables
        self.grid_size = 10
        self.karels = {}  # (x, y) -> {"direction": str, "color": str}
        self.selected_color = "Red"
        self.dark_mode = False
        self.click_timer = None
        self.drag_start = None
        self.is_dragging = False
        self.is_playing = False
        
        # Simulation scheduler states
        self.loop_speeds = {}        # head_cell -> speed_level (0=1x, 1=2x, 2=3x)
        self.loop_accumulators = {}  # head_cell -> accumulated_ms
        self.loop_steps_count = {}   # head_cell -> current_step_tick (for blinking)
        self.speed_buttons = {}      # head_cell -> (x1, y1, x2, y2)
        
        # GUI frames setup
        self.setup_ui()
        self.apply_theme()
        
        # Bind events
        self.canvas.bind("<Configure>", lambda e: self.redraw())
        self.canvas.bind("<Button-1>", self.handle_click)
        self.canvas.bind("<Double-Button-1>", self.handle_double_click)
        self.canvas.bind("<B1-Motion>", self.handle_drag)
        self.canvas.bind("<ButtonRelease-1>", self.handle_release)
        
        # Cross-platform mouse wheel bindings
        self.canvas.bind("<MouseWheel>", self.handle_mouse_wheel)
        self.canvas.bind("<Button-4>", self.handle_mouse_wheel)
        self.canvas.bind("<Button-5>", self.handle_mouse_wheel)
        
    def setup_ui(self):
        # Main Layout: Canvas Frame on the Left (expanding), Sidebar on the Right (fixed width)
        self.main_container = tk.Frame(self.root)
        self.main_container.pack(fill=tk.BOTH, expand=True)
        
        # Left container (Canvas + Help underneath)
        self.canvas_frame = tk.Frame(self.main_container)
        self.canvas_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.canvas = tk.Canvas(self.canvas_frame, highlightthickness=0, bd=0)
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=(10, 5))
        
        # Help panel placed at the bottom of the canvas
        self.help_frame = tk.LabelFrame(self.canvas_frame, text="Controls Help", font=("Segoe UI", 9, "bold"), padx=15, pady=8)
        self.help_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        help_text = (
            "🖱️ Scroll Wheel: Zoom / Adjust grid size\n"
            "🖱️ Left Click:   Place robot (on empty cell)\n"
            "                Rotate robot (90° turn on occupied cell)\n"
            "🖱️ Click & Drag: Paint cells with robots\n"
            "🖱️ Double-Click: Remove robot from cell"
        )
        self.help_lbl = tk.Label(self.help_frame, text=help_text, justify=tk.LEFT, anchor=tk.W, font=("Consolas", 9))
        self.help_lbl.pack(fill=tk.X)
        
        # Right container (Sidebar)
        self.sidebar = tk.Frame(self.main_container, width=280)
        self.sidebar.pack(side=tk.RIGHT, fill=tk.Y, padx=5, pady=5)
        self.sidebar.pack_propagate(False)
        
        # --- Sidebar Widgets ---
        # App Title
        self.title_lbl = tk.Label(self.sidebar, text="Draw with Karel", font=("Segoe UI", 18, "bold"))
        self.title_lbl.pack(anchor=tk.W, padx=15, pady=(15, 2))
        
        self.subtitle_lbl = tk.Label(self.sidebar, text="Pixel-by-pixel robot drawer", font=("Segoe UI", 9, "italic"))
        self.subtitle_lbl.pack(anchor=tk.W, padx=15, pady=(0, 15))
        
        # Grid settings & Stats Frame
        self.info_frame = tk.LabelFrame(self.sidebar, text="Board Stats", font=("Segoe UI", 9, "bold"), padx=10, pady=10)
        self.info_frame.pack(fill=tk.X, padx=15, pady=5)
        
        self.grid_size_lbl = tk.Label(self.info_frame, text=f"Grid Size: {self.grid_size} x {self.grid_size}", font=("Segoe UI", 10))
        self.grid_size_lbl.pack(anchor=tk.W, pady=2)
        
        self.karel_count_lbl = tk.Label(self.info_frame, text="Total Karels: 0", font=("Segoe UI", 10))
        self.karel_count_lbl.pack(anchor=tk.W, pady=2)
        
        # Grid Size Slider
        self.slider_frame = tk.Frame(self.info_frame)
        self.slider_frame.pack(fill=tk.X, pady=(5, 0))
        self.slider_lbl = tk.Label(self.slider_frame, text="Adjust Grid Size:", font=("Segoe UI", 9))
        self.slider_lbl.pack(side=tk.LEFT)
        self.grid_slider = tk.Scale(self.slider_frame, from_=1, to=100, orient=tk.HORIZONTAL, showvalue=True, command=self.on_slider_change)
        self.grid_slider.set(self.grid_size)
        self.grid_slider.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(5, 0))
        
        # Color Selector Frame
        self.color_frame = tk.LabelFrame(self.sidebar, text="Select Color", font=("Segoe UI", 9, "bold"), padx=10, pady=10)
        self.color_frame.pack(fill=tk.X, padx=15, pady=5)
        
        self.color_buttons_container = tk.Frame(self.color_frame)
        self.color_buttons_container.pack(fill=tk.X)
        
        # Create grid of color buttons (4x2)
        self.color_buttons = {}
        colors_list = list(COLOR_PALETTE.keys())
        for idx, col_name in enumerate(colors_list):
            row = idx // 4
            col = idx % 4
            color_hex = COLOR_PALETTE[col_name]
            
            btn = tk.Button(
                self.color_buttons_container,
                bg=color_hex,
                activebackground=color_hex,
                width=3,
                height=1,
                relief=tk.FLAT,
                command=lambda name=col_name: self.set_color(name)
            )
            btn.grid(row=row, column=col, padx=4, pady=4)
            self.color_buttons[col_name] = btn
            
        self.color_status_lbl = tk.Label(self.color_frame, text=f"Active Color: {self.selected_color}", font=("Segoe UI", 9, "bold"))
        self.color_status_lbl.pack(anchor=tk.W, pady=(5, 0))
        
        # Actions Frame
        self.action_frame = tk.LabelFrame(self.sidebar, text="Actions & Simulation", font=("Segoe UI", 9, "bold"), padx=10, pady=10)
        self.action_frame.pack(fill=tk.X, padx=15, pady=5)
        
        self.play_btn = tk.Button(self.action_frame, text="▶ Play Simulation", font=("Segoe UI", 9, "bold"), fg="#10B981", command=self.toggle_play)
        self.play_btn.pack(fill=tk.X, pady=3)
        
        self.import_btn = tk.Button(self.action_frame, text="Import Python File", font=("Segoe UI", 9), command=self.import_file)
        self.import_btn.pack(fill=tk.X, pady=3)
        
        self.export_btn = tk.Button(self.action_frame, text="Export Python File", font=("Segoe UI", 9), command=self.export_file)
        self.export_btn.pack(fill=tk.X, pady=3)
        
        self.copy_btn = tk.Button(self.action_frame, text="Copy Code to Clipboard", font=("Segoe UI", 9), command=self.copy_code)
        self.copy_btn.pack(fill=tk.X, pady=3)
        
        self.clear_btn = tk.Button(self.action_frame, text="Clear Board", font=("Segoe UI", 9), fg="#EF4444", command=self.clear_board)
        self.clear_btn.pack(fill=tk.X, pady=3)
        
        # Footer (Theme Toggle)
        self.footer_frame = tk.Frame(self.sidebar)
        self.footer_frame.pack(fill=tk.X, side=tk.BOTTOM, padx=15, pady=10)
        
        self.theme_btn = tk.Button(self.footer_frame, text="🌙 Dark Mode", font=("Segoe UI", 9), command=self.toggle_theme)
        self.theme_btn.pack(fill=tk.X)

    def set_color(self, name):
        self.selected_color = name
        self.color_status_lbl.config(text=f"Active Color: {name}", fg=COLOR_PALETTE[name])
        self.update_color_buttons_highlight()
        
    def update_color_buttons_highlight(self):
        for name, btn in self.color_buttons.items():
            if name == self.selected_color:
                btn.config(relief=tk.SUNKEN, bd=2, highlightbackground="#1F2937", highlightcolor="#1F2937")
            else:
                btn.config(relief=tk.FLAT, bd=0, highlightbackground=btn.cget("bg"), highlightcolor=btn.cget("bg"))

    def toggle_theme(self):
        self.dark_mode = not self.dark_mode
        self.apply_theme()
        self.redraw()
        
    def apply_theme(self):
        theme = THEMES["dark"] if self.dark_mode else THEMES["light"]
        
        # Main background
        self.root.config(bg=theme["bg"])
        self.main_container.config(bg=theme["bg"])
        self.canvas_frame.config(bg=theme["bg"])
        
        # Canvas colors
        self.canvas.config(bg=theme["canvas_bg"])
        
        # Sidebar
        self.sidebar.config(bg=theme["sidebar_bg"], highlightbackground=theme["border"], highlightcolor=theme["border"])
        self.title_lbl.config(bg=theme["sidebar_bg"], fg=theme["text"])
        self.subtitle_lbl.config(bg=theme["sidebar_bg"], fg=theme["text_sec"])
        
        # Info Panel
        self.info_frame.config(bg=theme["sidebar_bg"], fg=theme["text"], highlightcolor=theme["border"])
        self.grid_size_lbl.config(bg=theme["sidebar_bg"], fg=theme["text"])
        self.karel_count_lbl.config(bg=theme["sidebar_bg"], fg=theme["text"])
        self.slider_frame.config(bg=theme["sidebar_bg"])
        self.slider_lbl.config(bg=theme["sidebar_bg"], fg=theme["text"])
        self.grid_slider.config(bg=theme["sidebar_bg"], fg=theme["text"], highlightbackground=theme["sidebar_bg"])
        
        # Color Selector Panel
        self.color_frame.config(bg=theme["sidebar_bg"], fg=theme["text"])
        self.color_buttons_container.config(bg=theme["sidebar_bg"])
        self.color_status_lbl.config(bg=theme["sidebar_bg"])
        self.set_color(self.selected_color) # refresh color text color
        
        # Actions Panel
        self.action_frame.config(bg=theme["sidebar_bg"], fg=theme["text"])
        for btn in [self.import_btn, self.export_btn, self.copy_btn, self.play_btn]:
            btn.config(bg=theme["button_bg"], activebackground=theme["active_button_bg"], relief=tk.GROOVE, bd=1)
            
        if self.is_playing:
            self.play_btn.config(fg="#EF4444", activeforeground="#EF4444")
        else:
            self.play_btn.config(fg="#10B981", activeforeground="#10B981")
            
        self.clear_btn.config(bg=theme["button_bg"], fg="#EF4444", activebackground=theme["active_button_bg"], activeforeground="#EF4444", relief=tk.GROOVE, bd=1)
        
        # Bottom Help Panel colors
        self.help_frame.config(bg=theme["bg"], fg=theme["text"])
        self.help_lbl.config(bg=theme["bg"], fg=theme["text_sec"])
        
        # Footer
        self.footer_frame.config(bg=theme["sidebar_bg"])
        theme_btn_text = "☀️ Light Mode" if self.dark_mode else "🌙 Dark Mode"
        self.theme_btn.config(text=theme_btn_text, bg=theme["button_bg"], fg=theme["button_fg"], activebackground=theme["active_button_bg"], activeforeground=theme["button_fg"])
        
        self.update_color_buttons_highlight()

    # --- Grid Logic & Rendering ---
    def redraw(self):
        self.canvas.delete("all")
        self.speed_buttons.clear()
        
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        
        if w <= 1 or h <= 1:
            return
            
        cell_w = w / self.grid_size
        cell_h = h / self.grid_size
        
        theme = THEMES["dark"] if self.dark_mode else THEMES["light"]
        
        # 1. Cycle detection & highlight loops with dull yellow
        cycles, node_to_head, cycle_heads = self.detect_loops_and_chains()
        highlight_color = "#3F3715" if self.dark_mode else "#FEF08A"
        
        cycle_cells = set()
        for cycle in cycles:
            cycle_cells.update(cycle)
            
        for (col, row) in cycle_cells:
            if col < self.grid_size and row < self.grid_size:
                x1 = col * cell_w
                y1 = row * cell_h
                x2 = x1 + cell_w
                y2 = y1 + cell_h
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=highlight_color, outline="")
        
        # 2. Draw Grid Lines
        for i in range(self.grid_size + 1):
            self.canvas.create_line(i * cell_w, 0, i * cell_w, h, fill=theme["grid_line"], width=1)
            self.canvas.create_line(0, i * cell_h, w, i * cell_h, fill=theme["grid_line"], width=1)
            
        # 3. Draw Karels
        S = min(cell_w, cell_h)
        for (col, row), data in self.karels.items():
            if col < self.grid_size and row < self.grid_size:
                cx = col * cell_w + cell_w / 2
                cy = row * cell_h + cell_h / 2
                
                # Check if this robot is moving (associated with a cycle head)
                parent_head = node_to_head.get((col, row))
                self.draw_karel(cx, cy, S, data["direction"], COLOR_PALETTE[data["color"]], col, row, parent_head)
                
        # 4. Draw Speed Buttons on top left of the head cell for each active loop
        for head in cycle_heads:
            col, row = head
            if col < self.grid_size and row < self.grid_size:
                x1 = col * cell_w + 4
                y1 = row * cell_h + 4
                x2 = x1 + 22
                y2 = y1 + 22
                
                self.canvas.create_oval(x1, y1, x2, y2, fill="#E5E7EB" if not self.dark_mode else "#374151", outline="#9CA3AF", width=1, tags="speed_btn")
                
                speed = self.loop_speeds.get(head, 0)
                speed_text = "1x" if speed == 0 else "2x" if speed == 1 else "3x"
                self.canvas.create_text((x1 + x2) / 2, (y1 + y2) / 2, text=speed_text, font=("Segoe UI", 8, "bold"), fill="#1F2937" if not self.dark_mode else "#F9FAFB", tags="speed_btn")
                
                # Bounding box for click triggers
                self.speed_buttons[head] = (x1, y1, x2, y2)
                
        # 5. Update Sidebar Stats Labels
        self.grid_size_lbl.config(text=f"Grid Size: {self.grid_size} x {self.grid_size}")
        self.karel_count_lbl.config(text=f"Total Karels: {len(self.karels)}")

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
        theme = THEMES["dark"] if self.dark_mode else THEMES["light"]
        outline_color = theme["karel_outline"]
        
        line_width = max(2, int(S * 0.06))
        
        # Screen Christmas light flashing effect (only blinks if robot is in an active cycle)
        if self.is_playing and parent_head is not None:
            # Sync blinking with this loop's steps counter
            state = (col + row + self.loop_steps_count.get(parent_head, 0)) % 2
            screen_fill = "#EF4444" if state == 0 else "#10B981"
        else:
            screen_fill = "#FFFFFF" if not self.dark_mode else "#1F2937"
            
        # Body: Classic beveled card shape
        body_pts = [(-0.25, -0.35), (0.1, -0.35), (0.25, -0.2), (0.25, 0.35), (-0.1, 0.35), (-0.25, 0.2)]
        body_rot = [self.rotate_point(x, y, direction) for x, y in body_pts]
        body_screen = [coord for pt in body_rot for coord in (cx + pt[0]*S, cy + pt[1]*S)]
        self.canvas.create_polygon(body_screen, fill=color_hex, outline=outline_color, width=line_width)
        
        # Screen
        screen_pts = [(-0.12, -0.22), (0.12, -0.22), (0.12, 0.08), (-0.12, 0.08)]
        screen_rot = [self.rotate_point(x, y, direction) for x, y in screen_pts]
        screen_screen = [coord for pt in screen_rot for coord in (cx + pt[0]*S, cy + pt[1]*S)]
        self.canvas.create_polygon(screen_screen, fill=screen_fill, outline=outline_color, width=max(1, line_width // 2))
        
        # Mouth
        mouth_pts = [(-0.06, 0.18), (0.06, 0.18)]
        mouth_rot = [self.rotate_point(x, y, direction) for x, y in mouth_pts]
        mouth_screen = [coord for pt in mouth_rot for coord in (cx + pt[0]*S, cy + pt[1]*S)]
        self.canvas.create_line(mouth_screen[0], mouth_screen[1], mouth_screen[2], mouth_screen[3], fill=outline_color, width=max(1.5, line_width // 2))
        
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

    # --- Mouse Event Handlers ---
    def get_cell_coords(self, click_x, click_y):
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        cell_w = w / self.grid_size
        cell_h = h / self.grid_size
        
        col = max(0, min(self.grid_size - 1, int(click_x / cell_w)))
        row = max(0, min(self.grid_size - 1, int(click_y / cell_h)))
        return col, row

    def handle_click(self, event):
        # 1. Check if click falls within any speed buttons
        for head, bbox in self.speed_buttons.items():
            x1, y1, x2, y2 = bbox
            if x1 <= event.x <= x2 and y1 <= event.y <= y2:
                # Cycle speed setting: 1x (0) -> 2x (1) -> 3x (2)
                curr_speed = self.loop_speeds.get(head, 0)
                self.loop_speeds[head] = (curr_speed + 1) % 3
                self.redraw()
                return
                
        # 2. Otherwise run double click checks
        if self.click_timer is not None:
            self.root.after_cancel(self.click_timer)
            self.click_timer = None
            return
            
        self.drag_start = (event.x, event.y)
        self.is_dragging = False
        self.click_timer = self.root.after(200, lambda: self.execute_single_click(event))

    def execute_single_click(self, event):
        self.click_timer = None
        if self.is_dragging:
            return
            
        col, row = self.get_cell_coords(event.x, event.y)
        
        if (col, row) in self.karels:
            # Cycle direction: East -> North -> West -> South
            dirs = ["East", "North", "West", "South"]
            curr_dir = self.karels[(col, row)]["direction"]
            next_idx = (dirs.index(curr_dir) + 1) % 4
            self.karels[(col, row)]["direction"] = dirs[next_idx]
        else:
            # Place new Karel
            self.karels[(col, row)] = {
                "direction": "East",
                "color": self.selected_color
            }
            
        self.redraw()

    def handle_drag(self, event):
        if self.drag_start is None:
            return
            
        dx = event.x - self.drag_start[0]
        dy = event.y - self.drag_start[1]
        
        if (dx*dx + dy*dy) > 25:
            self.is_dragging = True
            if self.click_timer is not None:
                self.root.after_cancel(self.click_timer)
                self.click_timer = None
                
        if self.is_dragging:
            col, row = self.get_cell_coords(event.x, event.y)
            if (col, row) not in self.karels:
                self.karels[(col, row)] = {
                    "direction": "East",
                    "color": self.selected_color
                }
                self.redraw()

    def handle_release(self, event):
        self.drag_start = None
        self.is_dragging = False

    def handle_double_click(self, event):
        if self.click_timer is not None:
            self.root.after_cancel(self.click_timer)
            self.click_timer = None
            
        col, row = self.get_cell_coords(event.x, event.y)
        if (col, row) in self.karels:
            del self.karels[(col, row)]
            self.redraw()

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
            self.grid_slider.set(new_size)
            self.redraw()

    def on_slider_change(self, val):
        self.grid_size = int(val)
        self.redraw()

    def clear_board(self):
        if not self.karels:
            return
        if messagebox.askyesno("Clear Board", "Are you sure you want to remove all Karels?"):
            self.karels.clear()
            self.redraw()

    # --- Simulation Logic ---
    def toggle_play(self):
        self.is_playing = not self.is_playing
        if self.is_playing:
            self.play_btn.config(text="⏸ Pause Simulation", fg="#EF4444")
            self.animate_tick()
        else:
            self.play_btn.config(text="▶ Play Simulation", fg="#10B981")
        self.apply_theme()

    def animate_tick(self):
        if not self.is_playing:
            return
            
        self.run_simulation_step()
        self.root.after(50, self.animate_tick)  # Faster scheduling loop (50ms increments)

    def get_dir_delta(self, direction):
        if direction == "East": return 1, 0
        elif direction == "West": return -1, 0
        elif direction == "North": return 0, -1
        elif direction == "South": return 0, 1
        return 0, 0

    def detect_loops_and_chains(self):
        cycles = []
        node_to_head = {}
        visited_global = set()
        
        # 1. Cycle detection (find loops >= 4)
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
                    break
                if curr in visited_global:
                    break
                
                visited_local[curr] = len(path)
                path.append(curr)
                
                col, row = curr
                data = self.karels[curr]
                dx, dy = self.get_dir_delta(data["direction"])
                curr = ((col + dx) % self.grid_size, (row + dy) % self.grid_size)
                
            for node in path:
                visited_global.add(node)
                
        # 2. Sort out head cell for each cycle (highest, leftest)
        cycle_heads = set()
        for cycle in cycles:
            head = min(cycle, key=lambda p: (p[1], p[0]))
            cycle_heads.add(head)
            for node in cycle:
                node_to_head[node] = head
                
        # 3. Propagation along matching direction head-to-back links
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
                front_pos = ((col + dx) % self.grid_size, (row + dy) % self.grid_size)
                
                if front_pos in moving:
                    front_data = self.karels[front_pos]
                    if front_data["direction"] == direction:
                        node_to_head[pos] = node_to_head[front_pos]
                        moving.add(pos)
                        changed = True
                        
        return cycles, node_to_head, cycle_heads

    def run_simulation_step(self):
        cycles, node_to_head, cycle_heads = self.detect_loops_and_chains()
        
        # Clean up stale loop states
        self.loop_speeds = {h: self.loop_speeds[h] for h in self.loop_speeds if h in cycle_heads}
        self.loop_accumulators = {h: self.loop_accumulators[h] for h in self.loop_accumulators if h in cycle_heads}
        self.loop_steps_count = {h: self.loop_steps_count[h] for h in self.loop_steps_count if h in cycle_heads}
        
        robots_to_move = set()
        
        # Check loops independently using their specific speeds
        for head in cycle_heads:
            self.loop_accumulators[head] = self.loop_accumulators.get(head, 0) + 50
            speed = self.loop_speeds.get(head, 0)
            threshold = 500 if speed == 0 else 250 if speed == 1 else 100
            
            if self.loop_accumulators[head] >= threshold:
                self.loop_accumulators[head] -= threshold
                
                # Advance blink state tick
                self.loop_steps_count[head] = (self.loop_steps_count.get(head, 0) + 1) % 2
                
                # Add all associated loop and chain cells to move set
                for pos, parent_head in node_to_head.items():
                    if parent_head == head:
                        robots_to_move.add(pos)
                        
        if not robots_to_move:
            self.redraw() # Still redraw for blink updates
            return
            
        new_karels = {}
        for pos, data in self.karels.items():
            if pos not in robots_to_move:
                new_karels[pos] = data
                
        for pos in robots_to_move:
            col, row = pos
            data = self.karels[pos]
            dx, dy = self.get_dir_delta(data["direction"])
            next_pos = ((col + dx) % self.grid_size, (row + dy) % self.grid_size)
            new_karels[next_pos] = data
            
        self.karels = new_karels
        self.redraw()

    # --- Import / Export Logic ---
    def generate_code_string(self):
        karels_list = []
        for (x, y), data in self.karels.items():
            karels_list.append({
                "x": x,
                "y": y,
                "direction": data["direction"],
                "color": data["color"]
            })
            
        karels_formatted_lines = []
        for k in karels_list:
            karels_formatted_lines.append(f'    {{"x": {k["x"]}, "y": {k["y"]}, "direction": "{k["direction"]}", "color": "{k["color"]}"}},')
            
        karels_str = "[\n" + "\n".join(karels_formatted_lines) + "\n]" if len(karels_list) > 0 else "[]"
        
        code_template = f'''# Draw with Karel - Exported Drawing
# Run this script standalone to view your drawing, or load it in the editor.

GRID_SIZE = {self.grid_size}
KARELS = {karels_str}

# --- STANDALONE VIEWER CODE ---
import tkinter as tk

class KarelStaticViewer:
    def __init__(self, root, grid_size, karels):
        self.root = root
        self.root.title("Karel Drawing Viewer")
        self.root.geometry("700x750")
        self.root.minsize(450, 500)
        
        self.grid_size = grid_size
        self.karels = {{(k["x"], k["y"]): {{"direction": k["direction"], "color": k["color"]}} for k in karels}}
        self.is_playing = False
        
        # Simulation loop variables
        self.loop_speeds = {{}}
        self.loop_accumulators = {{}}
        self.loop_steps_count = {{}}
        self.speed_buttons = {{}}
        
        # Palettes for rendering
        self.color_palette = {{
            "Red": "#EF4444", "Blue": "#3B82F6", "Green": "#10B981", "Yellow": "#FBBF24",
            "Purple": "#8B5CF6", "Orange": "#F97316", "Pink": "#EC4899", "Cyan": "#06B6D4"
        }}
        
        # Canvas Layout (Canvas Frame + Help underneath)
        self.canvas_frame = tk.Frame(self.root)
        self.canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        self.canvas = tk.Canvas(self.canvas_frame, bg="#FAF9F6", highlightthickness=0, bd=0)
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=(10, 5))
        
        # Help Frame placed horizontally below canvas
        self.help_frame = tk.LabelFrame(self.canvas_frame, text="Controls Help", font=("Segoe UI", 9, "bold"), padx=15, pady=8)
        self.help_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        help_text = (
            "🖱️ Scroll Wheel: Zoom / Adjust grid size\\n"
            "🖱️ Left Click:   Place robot (on empty cell)\\n"
            "                Rotate robot (90° turn on occupied cell)\\n"
            "🖱️ Click & Drag: Paint cells with robots\\n"
            "🖱️ Double-Click: Remove robot from cell"
        )
        self.help_lbl = tk.Label(self.help_frame, text=help_text, justify=tk.LEFT, anchor=tk.W, font=("Consolas", 9), bg="#FAF9F6", fg="#4B5563")
        self.help_lbl.pack(fill=tk.X)
        
        # Control bar at bottom
        self.control_frame = tk.Frame(self.root, bg="#F3F4F6", height=50)
        self.control_frame.pack(fill=tk.X, side=tk.BOTTOM, padx=10, pady=(0, 10))
        
        self.play_btn = tk.Button(
            self.control_frame, 
            text="▶ Play Simulation", 
            font=("Segoe UI", 10, "bold"), 
            fg="#10B981", 
            command=self.toggle_play,
            relief=tk.GROOVE,
            bd=1
        )
        self.play_btn.pack(side=tk.LEFT, padx=15, pady=5)
        
        self.info_lbl = tk.Label(
            self.control_frame, 
            text=f"Grid: {{self.grid_size}}x{{self.grid_size}} | Karels: {{len(self.karels)}}", 
            font=("Segoe UI", 9, "bold"),
            bg="#F3F4F6",
            fg="#4B5563"
        )
        self.info_lbl.pack(side=tk.RIGHT, padx=15, pady=5)
        
        self.canvas.bind("<Configure>", lambda e: self.draw())
        self.canvas.bind("<Button-1>", self.handle_click)
        
    def handle_click(self, event):
        for head, bbox in self.speed_buttons.items():
            x1, y1, x2, y2 = bbox
            if x1 <= event.x <= x2 and y1 <= event.y <= y2:
                curr_speed = self.loop_speeds.get(head, 0)
                self.loop_speeds[head] = (curr_speed + 1) % 3
                self.draw()
                return

    def toggle_play(self):
        self.is_playing = not self.is_playing
        if self.is_playing:
            self.play_btn.config(text="⏸ Pause Simulation", fg="#EF4444")
            self.animate_tick()
        else:
            self.play_btn.config(text="▶ Play Simulation", fg="#10B981")
            
    def animate_tick(self):
        if not self.is_playing:
            return
        self.run_simulation_step()
        self.root.after(50, self.animate_tick)
        
    def get_dir_delta(self, direction):
        if direction == "East": return 1, 0
        elif direction == "West": return -1, 0
        elif direction == "North": return 0, -1
        elif direction == "South": return 0, 1
        return 0, 0
        
    def detect_loops_and_chains(self):
        cycles = []
        node_to_head = {{}}
        visited_global = set()
        
        for start in list(self.karels.keys()):
            if start in visited_global:
                continue
            path = []
            visited_local = {{}}
            curr = start
            while curr in self.karels:
                if curr in visited_local:
                    cycle_start_idx = visited_local[curr]
                    cycle = path[cycle_start_idx:]
                    if len(cycle) >= 4:
                        cycles.append(set(cycle))
                    break
                if curr in visited_global:
                    break
                visited_local[curr] = len(path)
                path.append(curr)
                col, row = curr
                data = self.karels[curr]
                dx, dy = self.get_dir_delta(data["direction"])
                curr = ((col + dx) % self.grid_size, (row + dy) % self.grid_size)
            for node in path:
                visited_global.add(node)
                
        cycle_heads = set()
        for cycle in cycles:
            head = min(cycle, key=lambda p: (p[1], p[0]))
            cycle_heads.add(head)
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
                front_pos = ((col + dx) % self.grid_size, (row + dy) % self.grid_size)
                if front_pos in moving:
                    front_data = self.karels[front_pos]
                    if front_data["direction"] == direction:
                        node_to_head[pos] = node_to_head[front_pos]
                        moving.add(pos)
                        changed = True
                        
        return cycles, node_to_head, cycle_heads

    def run_simulation_step(self):
        cycles, node_to_head, cycle_heads = self.detect_loops_and_chains()
        
        self.loop_speeds = {{h: self.loop_speeds[h] for h in self.loop_speeds if h in cycle_heads}}
        self.loop_accumulators = {{h: self.loop_accumulators[h] for h in self.loop_accumulators if h in cycle_heads}}
        self.loop_steps_count = {{h: self.loop_steps_count[h] for h in self.loop_steps_count if h in cycle_heads}}
        
        robots_to_move = set()
        for head in cycle_heads:
            self.loop_accumulators[head] = self.loop_accumulators.get(head, 0) + 50
            speed = self.loop_speeds.get(head, 0)
            threshold = 500 if speed == 0 else 250 if speed == 1 else 100
            if self.loop_accumulators[head] >= threshold:
                self.loop_accumulators[head] -= threshold
                self.loop_steps_count[head] = (self.loop_steps_count.get(head, 0) + 1) % 2
                for pos, parent_head in node_to_head.items():
                    if parent_head == head:
                        robots_to_move.add(pos)
                        
        if not robots_to_move:
            self.draw()
            return
            
        new_karels = {{}}
        for pos, data in self.karels.items():
            if pos not in robots_to_move:
                new_karels[pos] = data
        for pos in robots_to_move:
            col, row = pos
            data = self.karels[pos]
            dx, dy = self.get_dir_delta(data["direction"])
            next_pos = ((col + dx) % self.grid_size, (row + dy) % self.grid_size)
            new_karels[next_pos] = data
            
        self.karels = new_karels
        self.draw()
        self.info_lbl.config(text=f"Grid: {{self.grid_size}}x{{self.grid_size}} | Karels: {{len(self.karels)}}")
        
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
        
        if self.is_playing and parent_head is not None:
            state = (col + row + self.loop_steps_count.get(parent_head, 0)) % 2
            screen_fill = "#EF4444" if state == 0 else "#10B981"
        else:
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
'''
        return code_template

    def export_file(self):
        filepath = filedialog.asksaveasfilename(
            defaultextension=".py",
            filetypes=[("Python Files", "*.py")],
            title="Export Karel Drawing"
        )
        if not filepath:
            return
            
        try:
            code = self.generate_code_string()
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(code)
            messagebox.showinfo("Export Successful", f"Saved successfully to:\n{filepath}")
        except Exception as e:
            messagebox.showerror("Export Error", f"An error occurred while exporting:\n{str(e)}")

    def copy_code(self):
        try:
            code = self.generate_code_string()
            self.root.clipboard_clear()
            self.root.clipboard_append(code)
            self.root.update()
            messagebox.showinfo("Clipboard", "Python script copied to clipboard successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to copy to clipboard:\n{str(e)}")

    def import_file(self):
        filepath = filedialog.askopenfilename(
            filetypes=[("Python Files", "*.py")],
            title="Import Karel Drawing"
        )
        if not filepath:
            return
            
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
                
            grid_size_match = re.search(r"^GRID_SIZE\s*=\s*(\d+)", content, re.MULTILINE)
            if not grid_size_match:
                raise ValueError("No GRID_SIZE variable found at top level.")
            imported_grid_size = int(grid_size_match.group(1))
            
            karels_match = re.search(r"^KARELS\s*=\s*(\[.*?\])", content, re.MULTILINE | re.DOTALL)
            if not karels_match:
                raise ValueError("No KARELS variable list found.")
            
            karels_str = karels_match.group(1)
            imported_karels_list = ast.literal_eval(karels_str)
            
            new_karels = {}
            for item in imported_karels_list:
                x = int(item["x"])
                y = int(item["y"])
                new_karels[(x, y)] = {
                    "direction": str(item["direction"]),
                    "color": str(item["color"])
                }
                
            self.grid_size = imported_grid_size
            self.grid_slider.set(imported_grid_size)
            self.karels = new_karels
            self.redraw()
            
            messagebox.showinfo("Import Successful", f"Loaded board successfully!\nGrid Size: {self.grid_size}\nRobots: {len(self.karels)}")
            
        except Exception as e:
            messagebox.showerror("Import Error", f"Could not parse the drawing file. Ensure it was exported by this program.\n\nError details:\n{str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = KarelDrawingApp(root)
    root.mainloop()
