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
        self.root.geometry("900x700")
        self.root.minsize(700, 500)
        
        # State variables
        self.grid_size = 10
        self.karels = {}  # (x, y) -> {"direction": str, "color": str}
        self.selected_color = "Red"
        self.dark_mode = False
        self.click_timer = None
        
        # GUI frames setup
        self.setup_ui()
        self.apply_theme()
        
        # Bind events
        self.canvas.bind("<Configure>", lambda e: self.redraw())
        self.canvas.bind("<Button-1>", self.handle_click)
        self.canvas.bind("<Double-Button-1>", self.handle_double_click)
        
        # Cross-platform mouse wheel bindings
        self.canvas.bind("<MouseWheel>", self.handle_mouse_wheel)
        self.canvas.bind("<Button-4>", self.handle_mouse_wheel)
        self.canvas.bind("<Button-5>", self.handle_mouse_wheel)
        
    def setup_ui(self):
        # Main Layout: Canvas on the Left (expanding), Sidebar on the Right (fixed)
        self.main_container = tk.Frame(self.root)
        self.main_container.pack(fill=tk.BOTH, expand=True)
        
        # Left container (Canvas)
        self.canvas_frame = tk.Frame(self.main_container)
        self.canvas_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.canvas = tk.Canvas(self.canvas_frame, highlightthickness=0, bd=0)
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
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
        self.action_frame = tk.LabelFrame(self.sidebar, text="Actions", font=("Segoe UI", 9, "bold"), padx=10, pady=10)
        self.action_frame.pack(fill=tk.X, padx=15, pady=5)
        
        self.import_btn = tk.Button(self.action_frame, text="Import Python File", font=("Segoe UI", 9), command=self.import_file)
        self.import_btn.pack(fill=tk.X, pady=3)
        
        self.export_btn = tk.Button(self.action_frame, text="Export Python File", font=("Segoe UI", 9), command=self.export_file)
        self.export_btn.pack(fill=tk.X, pady=3)
        
        self.copy_btn = tk.Button(self.action_frame, text="Copy Code to Clipboard", font=("Segoe UI", 9), command=self.copy_code)
        self.copy_btn.pack(fill=tk.X, pady=3)
        
        self.clear_btn = tk.Button(self.action_frame, text="Clear Board", font=("Segoe UI", 9), fg="#EF4444", command=self.clear_board)
        self.clear_btn.pack(fill=tk.X, pady=3)
        
        # Help & Controls info
        self.help_frame = tk.LabelFrame(self.sidebar, text="Controls Help", font=("Segoe UI", 9, "bold"), padx=10, pady=10)
        self.help_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=5)
        
        help_text = (
            "🖱️ Scroll Wheel:\nZoom / Adjust grid size\n\n"
            "🖱️ Left Click:\nPlace robot (on empty cell) or\nRotate robot (90° turn)\n\n"
            "🖱️ Double-Click:\nRemove robot from cell"
        )
        self.help_lbl = tk.Label(self.help_frame, text=help_text, justify=tk.LEFT, anchor=tk.NW, font=("Segoe UI", 8))
        self.help_lbl.pack(fill=tk.BOTH, expand=True)
        
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
        # Highlight active color button border
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
        for btn in [self.import_btn, self.export_btn, self.copy_btn]:
            btn.config(bg=theme["button_bg"], fg=theme["button_fg"], activebackground=theme["active_button_bg"], activeforeground=theme["button_fg"], relief=tk.GROOVE, bd=1)
        self.clear_btn.config(bg=theme["button_bg"], activebackground=theme["active_button_bg"], relief=tk.GROOVE, bd=1)
        
        # Help Panel
        self.help_frame.config(bg=theme["sidebar_bg"], fg=theme["text"])
        self.help_lbl.config(bg=theme["sidebar_bg"], fg=theme["text_sec"])
        
        # Footer
        self.footer_frame.config(bg=theme["sidebar_bg"])
        theme_btn_text = "☀️ Light Mode" if self.dark_mode else "🌙 Dark Mode"
        self.theme_btn.config(text=theme_btn_text, bg=theme["button_bg"], fg=theme["button_fg"], activebackground=theme["active_button_bg"], activeforeground=theme["button_fg"])
        
        self.update_color_buttons_highlight()

    # --- Grid Logic & Rendering ---
    def redraw(self):
        self.canvas.delete("all")
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        
        # Tkinter window size is 1x1 on first render before geometry propagation
        if w <= 1 or h <= 1:
            return
            
        cell_w = w / self.grid_size
        cell_h = h / self.grid_size
        
        theme = THEMES["dark"] if self.dark_mode else THEMES["light"]
        
        # 1. Draw Grid Lines
        for i in range(self.grid_size + 1):
            # Vertical
            self.canvas.create_line(i * cell_w, 0, i * cell_w, h, fill=theme["grid_line"], width=1)
            # Horizontal
            self.canvas.create_line(0, i * cell_h, w, i * cell_h, fill=theme["grid_line"], width=1)
            
        # 2. Draw Karels (only those inside the current visible grid bounds)
        S = min(cell_w, cell_h)
        for (col, row), data in self.karels.items():
            if col < self.grid_size and row < self.grid_size:
                cx = col * cell_w + cell_w / 2
                cy = row * cell_h + cell_h / 2
                self.draw_karel(cx, cy, S, data["direction"], COLOR_PALETTE[data["color"]])
                
        # 3. Update Labels
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

    def draw_karel(self, cx, cy, S, direction, color_hex):
        theme = THEMES["dark"] if self.dark_mode else THEMES["light"]
        outline_color = theme["karel_outline"]
        head_color = theme["karel_head"]
        
        # local coordinates for East representation (S is bounding dimension)
        # Body
        body_pts = [(-0.25, -0.25), (0.15, -0.25), (0.15, 0.25), (-0.25, 0.25)]
        body_rot = [self.rotate_point(x, y, direction) for x, y in body_pts]
        body_screen = [coord for pt in body_rot for coord in (cx + pt[0]*S, cy + pt[1]*S)]
        self.canvas.create_polygon(body_screen, fill=color_hex, outline=outline_color, width=2)
        
        # Head
        head_pts = [(0.15, -0.15), (0.32, -0.15), (0.32, 0.15), (0.15, 0.15)]
        head_rot = [self.rotate_point(x, y, direction) for x, y in head_pts]
        head_screen = [coord for pt in head_rot for coord in (cx + pt[0]*S, cy + pt[1]*S)]
        self.canvas.create_polygon(head_screen, fill=head_color, outline=outline_color, width=2)
        
        # Treads
        tread1_pts = [(-0.2, -0.32), (0.1, -0.32), (0.1, -0.25), (-0.2, -0.25)]
        tread1_rot = [self.rotate_point(x, y, direction) for x, y in tread1_pts]
        tread1_screen = [coord for pt in tread1_rot for coord in (cx + pt[0]*S, cy + pt[1]*S)]
        self.canvas.create_polygon(tread1_screen, fill="#374151", outline=outline_color, width=2)
        
        tread2_pts = [(-0.2, 0.25), (0.1, 0.25), (0.1, 0.32), (-0.2, 0.32)]
        tread2_rot = [self.rotate_point(x, y, direction) for x, y in tread2_pts]
        tread2_screen = [coord for pt in tread2_rot for coord in (cx + pt[0]*S, cy + pt[1]*S)]
        self.canvas.create_polygon(tread2_screen, fill="#374151", outline=outline_color, width=2)
        
        # Antenna stem & bulb
        stem_pts = [(-0.08, -0.1), (-0.16, -0.38)]
        stem_rot = [self.rotate_point(x, y, direction) for x, y in stem_pts]
        stem_screen = [coord for pt in stem_rot for coord in (cx + pt[0]*S, cy + pt[1]*S)]
        self.canvas.create_line(stem_screen[0], stem_screen[1], stem_screen[2], stem_screen[3], fill=outline_color, width=2)
        
        bulb_cx, bulb_cy = self.rotate_point(-0.16, -0.38, direction)
        bcx = cx + bulb_cx * S
        bcy = cy + bulb_cy * S
        br = 0.04 * S
        self.canvas.create_oval(bcx - br, bcy - br, bcx + br, bcy + br, fill=color_hex, outline=outline_color, width=1)
        
        # Eyes
        eye_radius = 0.03 * S
        pupil_radius = 0.012 * S
        for ex, ey in [(0.24, -0.06), (0.24, 0.06)]:
            # White part
            rx, ry = self.rotate_point(ex, ey, direction)
            ecx = cx + rx * S
            ecy = cy + ry * S
            self.canvas.create_oval(ecx - eye_radius, ecy - eye_radius, ecx + eye_radius, ecy + eye_radius, fill="#FFFFFF", outline=outline_color, width=1)
            
            # Pupil (slanted forward for focus)
            px, py = self.rotate_point(ex + 0.015, ey, direction)
            pcx = cx + px * S
            pcy = cy + py * S
            self.canvas.create_oval(pcx - pupil_radius, pcy - pupil_radius, pcx + pupil_radius, pcy + pupil_radius, fill="#000000", outline="", width=0)
            
        # Direction indicator (Arrow inside body)
        arrow_pts = [(-0.12, -0.08), (-0.12, 0.08), (0.04, 0)]
        arrow_rot = [self.rotate_point(x, y, direction) for x, y in arrow_pts]
        arrow_screen = [coord for pt in arrow_rot for coord in (cx + pt[0]*S, cy + pt[1]*S)]
        self.canvas.create_polygon(arrow_screen, fill="#FFFFFF", outline=outline_color, width=1)

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
        if self.click_timer is not None:
            self.root.after_cancel(self.click_timer)
            self.click_timer = None
            return
            
        self.click_timer = self.root.after(200, lambda: self.execute_single_click(event))

    def execute_single_click(self, event):
        self.click_timer = None
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

    def handle_double_click(self, event):
        if self.click_timer is not None:
            self.root.after_cancel(self.click_timer)
            self.click_timer = None
            
        col, row = self.get_cell_coords(event.x, event.y)
        if (col, row) in self.karels:
            del self.karels[(col, row)]
            self.redraw()

    def handle_mouse_wheel(self, event):
        # Determine scroll direction
        # Windows/macOS: event.delta
        # Linux: event.num (4=up, 5=down)
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
            
        # Format the KARELS list nicely with indentations
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
        self.root.geometry("600x600")
        self.root.minsize(400, 400)
        
        self.grid_size = grid_size
        self.karels = {{(k["x"], k["y"]): {{"direction": k["direction"], "color": k["color"]}} for k in karels}}
        
        # Palettes for rendering
        self.color_palette = {{
            "Red": "#EF4444", "Blue": "#3B82F6", "Green": "#10B981", "Yellow": "#FBBF24",
            "Purple": "#8B5CF6", "Orange": "#F97316", "Pink": "#EC4899", "Cyan": "#06B6D4"
        }}
        
        self.canvas = tk.Canvas(self.root, bg="#FAF9F6", highlightthickness=0, bd=0)
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.canvas.bind("<Configure>", lambda e: self.draw())
        
    def draw(self):
        self.canvas.delete("all")
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        if w <= 1 or h <= 1:
            return
            
        cell_w = w / self.grid_size
        cell_h = h / self.grid_size
        
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
                self.draw_karel(cx, cy, S, data["direction"], self.color_palette.get(data["color"], "#EF4444"))
                
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
        
    def draw_karel(self, cx, cy, S, direction, color_hex):
        outline_color = "#1F2937"
        head_color = "#D1D5DB"
        
        # Body
        body_pts = [(-0.25, -0.25), (0.15, -0.25), (0.15, 0.25), (-0.25, 0.25)]
        body_rot = [self.rotate_point(x, y, direction) for x, y in body_pts]
        body_screen = [coord for pt in body_rot for coord in (cx + pt[0]*S, cy + pt[1]*S)]
        self.canvas.create_polygon(body_screen, fill=color_hex, outline=outline_color, width=2)
        
        # Head
        head_pts = [(0.15, -0.15), (0.32, -0.15), (0.32, 0.15), (0.15, 0.15)]
        head_rot = [self.rotate_point(x, y, direction) for x, y in head_pts]
        head_screen = [coord for pt in head_rot for coord in (cx + pt[0]*S, cy + pt[1]*S)]
        self.canvas.create_polygon(head_screen, fill=head_color, outline=outline_color, width=2)
        
        # Treads
        tread1_pts = [(-0.2, -0.32), (0.1, -0.32), (0.1, -0.25), (-0.2, -0.25)]
        tread1_rot = [self.rotate_point(x, y, direction) for x, y in tread1_pts]
        tread1_screen = [coord for pt in tread1_rot for coord in (cx + pt[0]*S, cy + pt[1]*S)]
        self.canvas.create_polygon(tread1_screen, fill="#374151", outline=outline_color, width=2)
        
        tread2_pts = [(-0.2, 0.25), (0.1, 0.25), (0.1, 0.32), (-0.2, 0.32)]
        tread2_rot = [self.rotate_point(x, y, direction) for x, y in tread2_pts]
        tread2_screen = [coord for pt in tread2_rot for coord in (cx + pt[0]*S, cy + pt[1]*S)]
        self.canvas.create_polygon(tread2_screen, fill="#374151", outline=outline_color, width=2)
        
        # Antenna stem & bulb
        stem_pts = [(-0.08, -0.1), (-0.16, -0.38)]
        stem_rot = [self.rotate_point(x, y, direction) for x, y in stem_pts]
        stem_screen = [coord for pt in stem_rot for coord in (cx + pt[0]*S, cy + pt[1]*S)]
        self.canvas.create_line(stem_screen[0], stem_screen[1], stem_screen[2], stem_screen[3], fill=outline_color, width=2)
        
        bulb_cx, bulb_cy = self.rotate_point(-0.16, -0.38, direction)
        bcx = cx + bulb_cx * S
        bcy = cy + bulb_cy * S
        br = 0.04 * S
        self.canvas.create_oval(bcx - br, bcy - br, bcx + br, bcy + br, fill=color_hex, outline=outline_color, width=1)
        
        # Eyes
        eye_radius = 0.03 * S
        pupil_radius = 0.012 * S
        for ex, ey in [(0.24, -0.06), (0.24, 0.06)]:
            rx, ry = self.rotate_point(ex, ey, direction)
            ecx = cx + rx * S
            ecy = cy + ry * S
            self.canvas.create_oval(ecx - eye_radius, ecy - eye_radius, ecx + eye_radius, ecy + eye_radius, fill="#FFFFFF", outline=outline_color, width=1)
            
            px, py = self.rotate_point(ex + 0.015, ey, direction)
            pcx = cx + px * S
            pcy = cy + py * S
            self.canvas.create_oval(pcx - pupil_radius, pcy - pupil_radius, pcx + pupil_radius, pcy + pupil_radius, fill="#000000", outline="", width=0)
            
        # Direction arrow
        arrow_pts = [(-0.12, -0.08), (-0.12, 0.08), (0.04, 0)]
        arrow_rot = [self.rotate_point(x, y, direction) for x, y in arrow_pts]
        arrow_screen = [coord for pt in arrow_rot for coord in (cx + pt[0]*S, cy + pt[1]*S)]
        self.canvas.create_polygon(arrow_screen, fill="#FFFFFF", outline=outline_color, width=1)

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
                
            # Parse variables using Regex & AST for safety (instead of exec/eval)
            grid_size_match = re.search(r"^GRID_SIZE\s*=\s*(\d+)", content, re.MULTILINE)
            if not grid_size_match:
                raise ValueError("No GRID_SIZE variable found at top level.")
            imported_grid_size = int(grid_size_match.group(1))
            
            karels_match = re.search(r"^KARELS\s*=\s*(\[.*?\])", content, re.MULTILINE | re.DOTALL)
            if not karels_match:
                raise ValueError("No KARELS variable list found.")
            
            karels_str = karels_match.group(1)
            imported_karels_list = ast.literal_eval(karels_str)
            
            # Reconstruct dict format
            new_karels = {}
            for item in imported_karels_list:
                x = int(item["x"])
                y = int(item["y"])
                new_karels[(x, y)] = {
                    "direction": str(item["direction"]),
                    "color": str(item["color"])
                }
                
            # Update app state
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
