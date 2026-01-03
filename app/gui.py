"""
███████╗ ██████╗ ██╗  ██╗      ██████╗ 
██╔════╝██╔═══██╗╚██╗██╔╝      ╚════██╗
█████╗  ██║   ██║ ╚███╔╝  █████╗ █████╔╝
██╔══╝  ██║   ██║ ██╔██╗  ╚════╝ ╚═══██╗
██║     ╚██████╔╝██╔╝ ██╗      ██████╔╝
╚═╝      ╚═════╝ ╚═╝  ╚═╝      ╚═════╝ 

FOX-3 COMBAT SYSTEMS INTERFACE
High-Fidelity Sci-Fi Tactical HUD
Pure Canvas Graphics - No External Images

LAYOUT: 1366x768 fixed window
- Left Panel:   280px
- Center Panel: 746px (flexible)
- Right Panel:  280px
- Margins:      20px total (10px each side)
"""

import tkinter as tk
from tkinter import font as tkfont
from datetime import datetime
import math
import random

# Import the bot engine
from app.main import NovaBotEngine


# ==================== COLOR PALETTE ====================
class Colors:
    """Sci-Fi Combat Color Scheme"""
    BG_DEEP = "#020A18"           # Deep midnight blue
    BG_PANEL = "#051528"          # Panel background
    BG_CIRCUIT = "#071E35"        # Circuit pattern color
    CYAN_GLOW = "#00F0FF"         # Primary neon cyan
    CYAN_DIM = "#006080"          # Dimmed cyan
    BLUE_ELECTRIC = "#007BFF"     # Electric blue accent
    BLUE_DIM = "#003366"          # Dimmed blue
    ORANGE_GLOW = "#FF9900"       # Alert/active orange
    ORANGE_DIM = "#804D00"        # Dimmed orange
    RED_ALERT = "#FF3333"         # Critical alert
    GREEN_OK = "#00FF66"          # Success green
    TEXT_BRIGHT = "#FFFFFF"       # Bright text
    TEXT_DIM = "#4A6A8A"          # Dimmed text
    GRID_LINE = "#0A2540"         # Grid lines
    SCROLLBAR_BG = "#0A1A2E"      # Scrollbar background (dark)
    SCROLLBAR_FG = "#1A3A5E"      # Scrollbar thumb (slightly lighter)


# ==================== CIRCUIT BACKGROUND CANVAS ====================
class CircuitBackground(tk.Canvas):
    """Animated circuit board pattern background."""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=Colors.BG_DEEP, highlightthickness=0, **kwargs)
        self.bind("<Configure>", self._on_resize)
        self.data_flows = []
        self._animating = True
        self._draw_patterns()
    
    def _on_resize(self, event):
        self._draw_patterns()
    
    def _draw_patterns(self):
        """Draw circuit board patterns."""
        self.delete("circuit")
        w = self.winfo_width() or 1366
        h = self.winfo_height() or 768
        
        # Hex grid pattern
        hex_size = 40
        for row in range(0, h + hex_size, hex_size):
            offset = (row // hex_size % 2) * (hex_size // 2)
            for col in range(-hex_size, w + hex_size, hex_size):
                x = col + offset
                y = row
                self._draw_hex(x, y, hex_size // 2 - 2, Colors.BG_CIRCUIT)
        
        # Circuit traces
        for _ in range(15):
            self._draw_circuit_trace(w, h)
        
        # Corner brackets
        self._draw_corner_brackets(w, h)
    
    def _draw_hex(self, cx, cy, size, color):
        """Draw a hexagon."""
        points = []
        for i in range(6):
            angle = math.pi / 6 + i * math.pi / 3
            x = cx + size * math.cos(angle)
            y = cy + size * math.sin(angle)
            points.extend([x, y])
        self.create_polygon(points, outline=color, fill="", width=1, tags="circuit")
    
    def _draw_circuit_trace(self, w, h):
        """Draw a circuit trace line."""
        side = random.choice(['top', 'left', 'right', 'bottom'])
        if side == 'top':
            x, y = random.randint(0, w), 0
        elif side == 'bottom':
            x, y = random.randint(0, w), h
        elif side == 'left':
            x, y = 0, random.randint(0, h)
        else:
            x, y = w, random.randint(0, h)
        
        points = [(x, y)]
        for _ in range(random.randint(3, 8)):
            direction = random.choice(['h', 'v'])
            if direction == 'h':
                x = x + random.randint(-200, 200)
            else:
                y = y + random.randint(-150, 150)
            x = max(0, min(w, x))
            y = max(0, min(h, y))
            points.append((x, y))
        
        if len(points) > 1:
            flat_points = [coord for point in points for coord in point]
            self.create_line(flat_points, fill=Colors.BG_CIRCUIT, width=1, tags="circuit")
            
            for px, py in points[1:-1]:
                self.create_oval(px-2, py-2, px+2, py+2, fill=Colors.CYAN_DIM, outline="", tags="circuit")
    
    def _draw_corner_brackets(self, w, h):
        """Draw glowing corner brackets."""
        size = 30
        thickness = 3
        color = Colors.CYAN_DIM
        
        corners = [
            (0, 0, 1, 1),
            (w, 0, -1, 1),
            (0, h, 1, -1),
            (w, h, -1, -1),
        ]
        
        for x, y, dx, dy in corners:
            self.create_line(x, y, x + dx * size, y, fill=color, width=thickness, tags="circuit")
            self.create_line(x, y, x, y + dy * size, fill=color, width=thickness, tags="circuit")


# ==================== ADVANCED RADAR ====================
class AdvancedRadar(tk.Canvas):
    """High-fidelity tactical radar with terrain grid."""
    
    def __init__(self, parent, size=240, **kwargs):
        super().__init__(parent, width=size, height=size, bg=Colors.BG_DEEP, 
                        highlightthickness=2, highlightbackground=Colors.CYAN_DIM, **kwargs)
        self.size = size
        self.center = size // 2
        self.sweep_angle = 0
        self.blips = []
        self.targets = []
        self.state = "offline"
        self._animating = True
        
        self._draw_static()
        self._animate()
    
    def _draw_static(self):
        """Draw static radar elements."""
        grid_color = Colors.GRID_LINE
        for i in range(1, 6):
            r = (self.center - 20) * i / 5
            self.create_oval(
                self.center - r, self.center - r,
                self.center + r, self.center + r,
                outline=Colors.CYAN_DIM if i % 2 == 0 else grid_color, width=1
            )
        
        for i in range(8):
            angle = i * math.pi / 4
            x = self.center + (self.center - 15) * math.cos(angle)
            y = self.center - (self.center - 15) * math.sin(angle)
            self.create_line(self.center, self.center, x, y, fill=grid_color, width=1)
        
        self._draw_reticle()
        self.create_oval(8, 8, self.size-8, self.size-8, outline=Colors.CYAN_GLOW, width=2)
        
        for i in range(36):
            angle = i * math.pi / 18
            inner_r = self.center - 18
            outer_r = self.center - 10 if i % 3 == 0 else self.center - 14
            x1 = self.center + inner_r * math.cos(angle)
            y1 = self.center - inner_r * math.sin(angle)
            x2 = self.center + outer_r * math.cos(angle)
            y2 = self.center - outer_r * math.sin(angle)
            self.create_line(x1, y1, x2, y2, fill=Colors.CYAN_DIM, width=1)
    
    def _draw_reticle(self):
        """Draw center targeting reticle."""
        c = self.center
        s = 15
        color = Colors.CYAN_GLOW
        
        self.create_line(c - s, c, c - 5, c, fill=color, width=2)
        self.create_line(c + 5, c, c + s, c, fill=color, width=2)
        self.create_line(c, c - s, c, c - 5, fill=color, width=2)
        self.create_line(c, c + 5, c, c + s, fill=color, width=2)
        self.create_oval(c - 3, c - 3, c + 3, c + 3, fill=color, outline="")
    
    def set_state(self, state):
        self.state = state
    
    def _get_color(self):
        """Get color based on state."""
        return {
            "offline": Colors.CYAN_DIM,
            "online": Colors.CYAN_GLOW,
            "listening": Colors.CYAN_GLOW,
            "processing": Colors.ORANGE_GLOW,
            "executing": Colors.RED_ALERT,
        }.get(self.state, Colors.CYAN_GLOW)
    
    def _animate(self):
        """Animate radar sweep."""
        if not self._animating:
            return
        
        self.delete("dynamic")
        
        if self.state != "offline":
            color = self._get_color()
            sweep_len = self.center - 20
            
            end_x = self.center + sweep_len * math.cos(self.sweep_angle)
            end_y = self.center - sweep_len * math.sin(self.sweep_angle)
            
            for i in range(30):
                trail_angle = self.sweep_angle - i * 0.03
                trail_len = sweep_len * (1 - i * 0.01)
                tx = self.center + trail_len * math.cos(trail_angle)
                ty = self.center - trail_len * math.sin(trail_angle)
                trail_color = Colors.CYAN_DIM if i > 10 else color
                self.create_line(self.center, self.center, tx, ty, 
                               fill=trail_color, width=max(1, 3 - i//10), tags="dynamic")
            
            self.create_line(self.center, self.center, end_x, end_y,
                           fill=color, width=3, tags="dynamic")
            
            if random.random() < 0.03:
                self._spawn_target()
            
            self._draw_targets()
            
            self.sweep_angle += 0.08
            if self.sweep_angle >= 2 * math.pi:
                self.sweep_angle = 0
        
        self.after(25, self._animate)
    
    def _spawn_target(self):
        """Spawn a new target."""
        if len(self.targets) < 6:
            dist = random.randint(40, self.center - 30)
            angle = random.uniform(0, 2 * math.pi)
            target_type = random.choice(['hostile', 'friendly', 'unknown'])
            self.targets.append({
                'dist': dist, 'angle': angle, 'type': target_type,
                'life': 100, 'trail': []
            })
    
    def _draw_targets(self):
        """Draw all targets with trails."""
        to_remove = []
        
        for target in self.targets:
            x = self.center + target['dist'] * math.cos(target['angle'])
            y = self.center - target['dist'] * math.sin(target['angle'])
            
            color = {
                'hostile': Colors.RED_ALERT,
                'friendly': Colors.GREEN_OK,
                'unknown': Colors.ORANGE_GLOW
            }[target['type']]
            
            target['trail'].append((x, y))
            if len(target['trail']) > 10:
                target['trail'].pop(0)
            
            for i, (tx, ty) in enumerate(target['trail']):
                size = 2 + i * 0.3
                self.create_oval(tx - size/2, ty - size/2, tx + size/2, ty + size/2,
                               fill=color, outline="", tags="dynamic")
            
            self._draw_target_marker(x, y, color, target['type'])
            
            target['life'] -= 1
            if target['life'] <= 0:
                to_remove.append(target)
        
        for t in to_remove:
            self.targets.remove(t)
    
    def _draw_target_marker(self, x, y, color, target_type):
        """Draw a target marker."""
        size = 8
        if target_type == 'hostile':
            self.create_polygon(x, y - size, x + size, y, x, y + size, x - size, y,
                              outline=color, fill="", width=2, tags="dynamic")
        elif target_type == 'friendly':
            self.create_oval(x - size, y - size, x + size, y + size,
                           outline=color, fill="", width=2, tags="dynamic")
        else:
            self.create_polygon(x, y - size, x + size, y + size, x - size, y + size,
                              outline=color, fill="", width=2, tags="dynamic")
    
    def stop(self):
        self._animating = False


# ==================== GLOWING ENGAGE BUTTON ====================
class EngageButton(tk.Canvas):
    """Large, glowing Start/Stop button with pulse animation."""
    
    def __init__(self, parent, command=None, width=240, height=60, **kwargs):
        super().__init__(parent, width=width, height=height, bg=Colors.BG_PANEL, 
                        highlightthickness=0, **kwargs)
        self.btn_width = width
        self.btn_height = height
        self.command = command
        self.engaged = False
        self.pulse_phase = 0
        self.hover = False
        self._animating = True
        
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Button-1>", self._on_click)
        
        self._animate()
    
    def _on_enter(self, event):
        self.hover = True
    
    def _on_leave(self, event):
        self.hover = False
    
    def _on_click(self, event):
        if self.command:
            self.command()
    
    def set_engaged(self, engaged):
        self.engaged = engaged
    
    def _animate(self):
        if not self._animating:
            return
        
        self.delete("all")
        
        w, h = self.btn_width, self.btn_height
        cx, cy = w / 2, h / 2  # True center
        
        self.pulse_phase += 0.1
        pulse = (math.sin(self.pulse_phase) + 1) / 2
        
        if self.engaged:
            main_color = Colors.RED_ALERT
            glow_color = "#FF6666"
            text = "■  DISENGAGE"
        else:
            main_color = Colors.ORANGE_GLOW
            glow_color = "#FFCC66"
            text = "▶  ENGAGE SYSTEMS"
        
        # Outer glow (pulsing)
        glow_size = 4 + pulse * 3
        for i in range(int(glow_size), 0, -1):
            self.create_rectangle(
                5 - i, 5 - i, w - 5 + i, h - 5 + i,
                outline=glow_color if i < 3 else main_color,
                width=1
            )
        
        # Main button body
        if self.hover:
            fill = main_color
            text_color = Colors.BG_DEEP
        else:
            fill = Colors.BG_PANEL
            text_color = main_color
        
        # Button shape
        self.create_rectangle(8, 8, w - 8, h - 8, fill=fill, outline=main_color, width=3)
        
        # Corner accents
        corner_size = 10
        for x, y, dx, dy in [(8, 8, 1, 1), (w-8, 8, -1, 1), (8, h-8, 1, -1), (w-8, h-8, -1, -1)]:
            self.create_line(x, y, x + dx * corner_size, y, fill=Colors.CYAN_GLOW, width=2)
            self.create_line(x, y, x, y + dy * corner_size, fill=Colors.CYAN_GLOW, width=2)
        
        # Text - perfectly centered (offset left to compensate for symbol width)
        text_x = (w // 2) - 4
        text_y = h // 2
        self.create_text(text_x, text_y, text=text, fill=text_color,
                        font=("Consolas", 11, "bold"), anchor="center", justify="center")
        
        # Scanning line effect when hovering
        if self.hover:
            scan_y = 10 + (self.pulse_phase * 20) % (h - 20)
            self.create_line(12, scan_y, w - 12, scan_y, fill=glow_color, width=1)
        
        self.after(30, self._animate)
    
    def stop(self):
        self._animating = False


# ==================== POWER BAR ====================
class PowerBar(tk.Canvas):
    """Vertical power level indicator."""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, width=50, height=180, bg=Colors.BG_DEEP,
                        highlightthickness=1, highlightbackground=Colors.CYAN_DIM, **kwargs)
        self.level = 0.75
        self._animating = True
        self._animate()
    
    def set_level(self, level):
        self.level = max(0, min(1, level))
    
    def _animate(self):
        if not self._animating:
            return
        
        self.delete("all")
        w, h = 50, 180
        
        self.create_text(w // 2, 12, text="POWER", fill=Colors.CYAN_GLOW,
                        font=("Consolas", 7, "bold"))
        
        bar_x, bar_y = 12, 25
        bar_w, bar_h = 26, 135
        
        self.create_rectangle(bar_x, bar_y, bar_x + bar_w, bar_y + bar_h,
                            outline=Colors.CYAN_DIM, fill=Colors.BG_PANEL, width=2)
        
        fill_h = int(bar_h * self.level)
        fill_y = bar_y + bar_h - fill_h
        
        segment_h = 10
        for i in range(0, fill_h, segment_h):
            seg_y = bar_y + bar_h - i - segment_h
            if seg_y >= fill_y:
                ratio = i / bar_h
                if ratio > 0.7:
                    color = Colors.GREEN_OK
                elif ratio > 0.3:
                    color = Colors.CYAN_GLOW
                else:
                    color = Colors.ORANGE_GLOW
                
                self.create_rectangle(
                    bar_x + 3, seg_y + 2,
                    bar_x + bar_w - 3, seg_y + segment_h - 2,
                    fill=color, outline=""
                )
        
        pct = int(self.level * 100)
        self.create_text(w // 2, bar_y + bar_h + 10, text=f"{pct}%",
                        fill=Colors.CYAN_GLOW, font=("Consolas", 9, "bold"))
        
        self.level = max(0.4, min(1.0, self.level + random.uniform(-0.02, 0.02)))
        
        self.after(100, self._animate)
    
    def stop(self):
        self._animating = False


# ==================== WAVEFORM VISUALIZER ====================
class WaveformVisualizer(tk.Canvas):
    """Audio waveform visualization."""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, height=50, bg=Colors.BG_DEEP,
                        highlightthickness=1, highlightbackground=Colors.CYAN_DIM, **kwargs)
        self.waveform = [0] * 50
        self.active = False
        self._animating = True
        self._animate()
    
    def set_active(self, active):
        self.active = active
    
    def _animate(self):
        if not self._animating:
            return
        
        self.delete("all")
        w = self.winfo_width() or 400
        h = 50
        
        if self.active:
            self.waveform.pop(0)
            self.waveform.append(random.uniform(0.2, 1.0))
        else:
            self.waveform.pop(0)
            self.waveform.append(random.uniform(0, 0.1))
        
        self.create_line(0, h // 2, w, h // 2, fill=Colors.CYAN_DIM, width=1)
        
        bar_width = w / len(self.waveform)
        for i, val in enumerate(self.waveform):
            x = i * bar_width
            bar_h = val * (h // 2 - 5)
            
            color = Colors.CYAN_GLOW if self.active else Colors.CYAN_DIM
            
            self.create_rectangle(
                x + 1, h // 2 - bar_h,
                x + bar_width - 1, h // 2 + bar_h,
                fill=color, outline=""
            )
        
        self.after(50, self._animate)
    
    def stop(self):
        self._animating = False


# ==================== WEAPON BAY BUTTON ====================
class WeaponButton(tk.Canvas):
    """Stylized weapon bay command button."""
    
    def __init__(self, parent, text, command=None, width=180, height=38, **kwargs):
        super().__init__(parent, width=width, height=height, bg=Colors.BG_PANEL,
                        highlightthickness=0, **kwargs)
        self.text = text
        self.btn_width = width
        self.btn_height = height
        self.command = command
        self.hover = False
        
        self.bind("<Enter>", lambda e: self._set_hover(True))
        self.bind("<Leave>", lambda e: self._set_hover(False))
        self.bind("<Button-1>", self._on_click)
        
        self._draw()
    
    def _set_hover(self, hover):
        self.hover = hover
        self._draw()
    
    def _on_click(self, event):
        if self.command:
            self.command()
    
    def _draw(self):
        self.delete("all")
        w, h = self.btn_width, self.btn_height
        cx, cy = w / 2, h / 2
        
        if self.hover:
            fill = Colors.ORANGE_GLOW
            text_color = Colors.BG_DEEP
            border = Colors.ORANGE_GLOW
        else:
            fill = Colors.BG_PANEL
            text_color = Colors.CYAN_GLOW
            border = Colors.CYAN_DIM
        
        # Hexagonal shape
        points = [
            12, 4,
            w - 12, 4,
            w - 4, h // 2,
            w - 12, h - 4,
            12, h - 4,
            4, h // 2
        ]
        self.create_polygon(points, fill=fill, outline=border, width=2)
        
        # Tech decorations
        self.create_line(16, 10, 32, 10, fill=border, width=1)
        self.create_line(w - 32, h - 10, w - 16, h - 10, fill=border, width=1)
        
        # Text - perfectly centered
        self.create_text(cx, cy, text=self.text, fill=text_color,
                        font=("Consolas", 9, "bold"), anchor="center")


# ==================== AI CORE ANIMATION ====================
class AICore(tk.Canvas):
    """Rotating orbital ring AI status indicator."""
    
    def __init__(self, parent, size=60, **kwargs):
        super().__init__(parent, width=size, height=size, bg=Colors.BG_PANEL,
                        highlightthickness=0, **kwargs)
        self.size = size
        self.center = size // 2
        self.angle = 0
        self.state = "offline"
        self._animating = True
        self._animate()
    
    def set_state(self, state):
        self.state = state
    
    def _animate(self):
        if not self._animating:
            return
        
        self.delete("all")
        c = self.center
        
        color = Colors.CYAN_GLOW if self.state != "offline" else Colors.CYAN_DIM
        
        self.create_oval(5, 5, self.size - 5, self.size - 5, outline=color, width=2)
        
        for i in range(3):
            orbit_angle = self.angle + i * (2 * math.pi / 3)
            ox = c + (c - 10) * math.cos(orbit_angle)
            oy = c + (c - 10) * math.sin(orbit_angle)
            self.create_oval(ox - 3, oy - 3, ox + 3, oy + 3, fill=color, outline="")
        
        pulse = (math.sin(self.angle * 2) + 1) / 2
        core_size = 8 + pulse * 3
        self.create_oval(c - core_size, c - core_size, c + core_size, c + core_size,
                        fill=color if self.state != "offline" else Colors.BG_PANEL,
                        outline=color, width=2)
        
        self.angle += 0.05
        self.after(30, self._animate)
    
    def stop(self):
        self._animating = False


# ==================== FLIGHT DATA RECORDER ====================
class FlightDataRecorder(tk.Frame):
    """Mission log display with hidden scrollbar (mouse wheel scroll enabled)."""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=Colors.BG_DEEP, **kwargs)
        
        # Header
        header = tk.Frame(self, bg=Colors.BG_DEEP)
        header.pack(fill="x", pady=(0, 5))
        
        tk.Label(header, text="◆ MISSION LOG ◆",
                font=("Consolas", 9, "bold"),
                fg=Colors.CYAN_GLOW, bg=Colors.BG_DEEP).pack(side="left")
        
        # Clear button
        clr = tk.Label(header, text="[CLR]", font=("Consolas", 8),
                      fg=Colors.TEXT_DIM, bg=Colors.BG_DEEP, cursor="hand2")
        clr.pack(side="right")
        clr.bind("<Button-1>", lambda e: self.clear())
        clr.bind("<Enter>", lambda e: clr.config(fg=Colors.CYAN_GLOW))
        clr.bind("<Leave>", lambda e: clr.config(fg=Colors.TEXT_DIM))
        
        # Log area with border - NO visible scrollbar
        border = tk.Frame(self, bg=Colors.CYAN_DIM, padx=2, pady=2)
        border.pack(fill="both", expand=True)
        
        # Text widget without scrollbar (mouse wheel scrolling works)
        self.log = tk.Text(border, bg=Colors.BG_DEEP, fg=Colors.CYAN_GLOW,
                          font=("Consolas", 9), wrap="word",
                          insertbackground=Colors.CYAN_GLOW,
                          selectbackground=Colors.BLUE_DIM,
                          relief="flat", padx=8, pady=8)
        self.log.pack(fill="both", expand=True)
        self.log.config(state="disabled")
        
        # Enable mouse wheel scrolling
        self.log.bind("<MouseWheel>", self._on_mousewheel)
        self.log.bind("<Button-4>", self._on_mousewheel)  # Linux scroll up
        self.log.bind("<Button-5>", self._on_mousewheel)  # Linux scroll down
        
        # Tags
        self.log.tag_configure("time", foreground=Colors.TEXT_DIM)
        self.log.tag_configure("info", foreground=Colors.CYAN_GLOW)
        self.log.tag_configure("warn", foreground=Colors.ORANGE_GLOW)
        self.log.tag_configure("error", foreground=Colors.RED_ALERT)
        self.log.tag_configure("success", foreground=Colors.GREEN_OK)
    
    def _on_mousewheel(self, event):
        """Handle mouse wheel scrolling."""
        if event.num == 4:  # Linux scroll up
            self.log.yview_scroll(-3, "units")
        elif event.num == 5:  # Linux scroll down
            self.log.yview_scroll(3, "units")
        else:  # Windows
            self.log.yview_scroll(int(-1 * (event.delta / 120)), "units")
        return "break"
    
    def write(self, message):
        """Write message to log."""
        self.log.config(state="normal")
        
        time_str = datetime.now().strftime("%H:%M:%S")
        
        msg_lower = message.lower()
        if "error" in msg_lower or "fault" in msg_lower or "!!" in message:
            tag = "error"
        elif "warning" in msg_lower or "caution" in msg_lower:
            tag = "warn"
        elif "success" in msg_lower or "splash" in msg_lower or "✅" in message:
            tag = "success"
        else:
            tag = "info"
        
        clean = message
        for emoji in ["🤖", "🚀", "🔊", "📝", "🟢", "🟡", "❓", "❌", "⚠️", "✅", "👋", "🗣️", "⚡", "💬", "📋", "⏹️", "🛑", "🔵", "🖥️", "🧠"]:
            clean = clean.replace(emoji, "")
        
        self.log.insert("end", f"[{time_str}] ", "time")
        self.log.insert("end", f"{clean.strip()}\n", tag)
        self.log.see("end")
        self.log.config(state="disabled")
    
    def clear(self):
        self.log.config(state="normal")
        self.log.delete("1.0", "end")
        self.log.config(state="disabled")


# ==================== TELEMETRY BAR ====================
class TelemetryBar(tk.Canvas):
    """Bottom telemetry strip with scrolling data."""
    
    def __init__(self, parent, height=35, **kwargs):
        super().__init__(parent, height=height, bg=Colors.BG_DEEP,
                        highlightthickness=0, **kwargs)
        self.bar_height = height
        self.scroll_offset = 0
        self._animating = True
        self._animate()
    
    def _animate(self):
        if not self._animating:
            return
        
        self.delete("all")
        w = self.winfo_width() or 1366
        h = self.bar_height
        
        self.create_line(0, 0, w, 0, fill=Colors.CYAN_DIM, width=2)
        
        data = [
            f"LAT: {random.uniform(30, 40):.4f}°N",
            f"LON: {random.uniform(-120, -110):.4f}°W",
            f"ALT: {random.randint(28000, 42000):,} FT",
            f"SPD: MACH {random.uniform(0.85, 1.5):.2f}",
            f"HDG: {random.randint(0, 359):03d}°",
            f"G: +{random.uniform(0.8, 2.5):.1f}",
            f"FUEL: {random.randint(60, 95)}%",
            f"SYS: NOMINAL",
        ]
        
        seg_width = w / len(data)
        for i, text in enumerate(data):
            x = i * seg_width + seg_width / 2
            
            if i > 0:
                self.create_line(i * seg_width, 5, i * seg_width, h - 5,
                               fill=Colors.CYAN_DIM, width=1)
            
            self.create_text(x, h // 2 + 2, text=text,
                           fill=Colors.CYAN_GLOW, font=("Consolas", 8))
        
        self.after(300, self._animate)
    
    def stop(self):
        self._animating = False


# ==================== MAIN HUD ====================
class Fox3HUD(tk.Tk):
    """FOX-3 Combat Systems Interface - High Fidelity HUD
    
    Fixed Layout: 1366x768
    - Left Panel:   280px
    - Center Panel: Flexible (fills remaining ~746px)
    - Right Panel:  280px
    - Margins:      10px on each side
    """
    
    # Layout constants
    WINDOW_WIDTH = 1366
    WINDOW_HEIGHT = 768
    MARGIN = 10
    LEFT_WIDTH = 280
    RIGHT_WIDTH = 280
    HEADER_HEIGHT = 45
    TELEMETRY_HEIGHT = 35
    
    def __init__(self):
        super().__init__()
        
        self.title("FOX-3 // COMBAT SYSTEMS")
        self.geometry(f"{self.WINDOW_WIDTH}x{self.WINDOW_HEIGHT}")
        self.resizable(False, False)
        self.configure(bg=Colors.BG_DEEP)
        
        self.engine = None
        self.is_running = False
        self.animated = []
        
        self._build_ui()
        
        self.log("FOX-3 COMBAT SYSTEMS INITIALIZED")
        self.log("ALL SUBSYSTEMS: NOMINAL")
        self.log("AWAITING PILOT AUTHORIZATION")
        
        self.protocol("WM_DELETE_WINDOW", self._on_close)
    
    def _build_ui(self):
        """Build the complete interface using grid layout."""
        # Background canvas
        self.bg_canvas = CircuitBackground(self)
        self.bg_canvas.place(x=0, y=0, relwidth=1, relheight=1)
        
        # Main container frame with fixed margins
        main = tk.Frame(self, bg=Colors.BG_DEEP)
        main.place(
            x=self.MARGIN, 
            y=self.MARGIN, 
            width=self.WINDOW_WIDTH - 2 * self.MARGIN,
            height=self.WINDOW_HEIGHT - 2 * self.MARGIN
        )
        
        # Configure grid weights
        main.grid_rowconfigure(0, weight=0, minsize=self.HEADER_HEIGHT)  # Header
        main.grid_rowconfigure(1, weight=1)  # Content
        main.grid_rowconfigure(2, weight=0, minsize=self.TELEMETRY_HEIGHT)  # Telemetry
        
        # Strict column widths: 280 + 746 + 280 = 1306 (fits in 1346 with 10px gaps)
        main.grid_columnconfigure(0, weight=0, minsize=self.LEFT_WIDTH)
        main.grid_columnconfigure(1, weight=1)  # Center expands
        main.grid_columnconfigure(2, weight=0, minsize=self.RIGHT_WIDTH)
        
        # Build sections
        self._build_header(main)
        self._build_left_panel(main)
        self._build_center_panel(main)
        self._build_right_panel(main)
        self._build_telemetry(main)
    
    def _build_header(self, parent):
        """Build header bar."""
        header = tk.Frame(parent, bg=Colors.BG_DEEP, height=self.HEADER_HEIGHT)
        header.grid(row=0, column=0, columnspan=3, sticky="ew", pady=(0, 5))
        header.grid_propagate(False)
        
        # Left - Title (reduced font size to prevent overlap)
        tk.Label(header, text="FOX-3 // COMBAT SYSTEMS",
                font=("Consolas", 14, "bold"),
                fg=Colors.CYAN_GLOW, bg=Colors.BG_DEEP).pack(side="left", padx=(5, 0))
        
        # Right container
        right = tk.Frame(header, bg=Colors.BG_DEEP)
        right.pack(side="right", padx=(0, 5))
        
        # Clock (first, so it's rightmost)
        self.clock = tk.Label(right, text="00:00:00",
                             font=("Consolas", 16, "bold"),
                             fg=Colors.CYAN_GLOW, bg=Colors.BG_DEEP)
        self.clock.pack(side="right")
        self._update_clock()
        
        # Status indicator
        status_frame = tk.Frame(right, bg=Colors.BG_DEEP)
        status_frame.pack(side="right", padx=(0, 20))
        
        self.status_dot = tk.Canvas(status_frame, width=10, height=10,
                                   bg=Colors.BG_DEEP, highlightthickness=0)
        self.status_dot.pack(side="left", padx=(0, 5))
        self.status_dot.create_oval(1, 1, 9, 9, fill=Colors.TEXT_DIM, outline="")
        
        self.status_label = tk.Label(status_frame, text="OFFLINE",
                                    font=("Consolas", 10, "bold"),
                                    fg=Colors.TEXT_DIM, bg=Colors.BG_DEEP)
        self.status_label.pack(side="left")
    
    def _build_left_panel(self, parent):
        """Build left avionics panel."""
        left = tk.Frame(parent, bg=Colors.BG_PANEL, width=self.LEFT_WIDTH)
        left.grid(row=1, column=0, sticky="nsew", padx=(0, 5))
        left.grid_propagate(False)
        
        inner = tk.Frame(left, bg=Colors.BG_PANEL)
        inner.pack(fill="both", expand=True, padx=8, pady=8)
        
        # Radar
        tk.Label(inner, text="◆ TACTICAL RADAR ◆",
                font=("Consolas", 9, "bold"),
                fg=Colors.CYAN_GLOW, bg=Colors.BG_PANEL).pack(pady=(0, 5))
        
        self.radar = AdvancedRadar(inner, size=240)
        self.radar.pack()
        self.animated.append(self.radar)
        
        # ENGAGE BUTTON
        tk.Label(inner, text="◆ PRIMARY CONTROL ◆",
                font=("Consolas", 9, "bold"),
                fg=Colors.ORANGE_GLOW, bg=Colors.BG_PANEL).pack(pady=(12, 5))
        
        self.engage_btn = EngageButton(inner, command=self._toggle_system, width=240, height=55)
        self.engage_btn.pack(pady=5)
        self.animated.append(self.engage_btn)
        
        # AI Core
        tk.Label(inner, text="◆ AI STATUS ◆",
                font=("Consolas", 9, "bold"),
                fg=Colors.CYAN_GLOW, bg=Colors.BG_PANEL).pack(pady=(12, 5))
        
        self.ai_core = AICore(inner, size=55)
        self.ai_core.pack()
        self.animated.append(self.ai_core)
    
    def _build_center_panel(self, parent):
        """Build center data core panel."""
        center = tk.Frame(parent, bg=Colors.BG_DEEP)
        center.grid(row=1, column=1, sticky="nsew", padx=5)
        
        # Flight Data Recorder
        self.fdr = FlightDataRecorder(center)
        self.fdr.pack(fill="both", expand=True)
        
        # Waveform visualizer
        tk.Label(center, text="◆ VOICE COMMS ◆",
                font=("Consolas", 8, "bold"),
                fg=Colors.CYAN_GLOW, bg=Colors.BG_DEEP).pack(pady=(8, 2))
        
        self.waveform = WaveformVisualizer(center)
        self.waveform.pack(fill="x")
        self.animated.append(self.waveform)
    
    def _build_right_panel(self, parent):
        """Build right auxiliary panel."""
        right = tk.Frame(parent, bg=Colors.BG_PANEL, width=self.RIGHT_WIDTH)
        right.grid(row=1, column=2, sticky="nsew", padx=(5, 0))
        right.grid_propagate(False)
        
        inner = tk.Frame(right, bg=Colors.BG_PANEL)
        inner.pack(fill="both", expand=True, padx=10, pady=8)
        
        # Power bar
        tk.Label(inner, text="◆ POWER ◆",
                font=("Consolas", 8, "bold"),
                fg=Colors.CYAN_GLOW, bg=Colors.BG_PANEL).pack(pady=(0, 3))
        
        self.power_bar = PowerBar(inner)
        self.power_bar.pack()
        self.animated.append(self.power_bar)
        
        # Weapons bay
        tk.Label(inner, text="◆ WEAPONS BAY ◆",
                font=("Consolas", 8, "bold"),
                fg=Colors.CYAN_GLOW, bg=Colors.BG_PANEL).pack(pady=(15, 5))
        
        weapons = [
            ("DEPLOY: SPOTIFY", "Play music on Spotify"),
            ("DEPLOY: BROWSER", "Open YouTube"),
            ("DEPLOY: NOTEPAD", "Open Notepad"),
            ("SYSTEM CHECK", "Status report"),
        ]
        
        for label, cmd in weapons:
            btn = WeaponButton(inner, label, command=lambda c=cmd: self._quick_action(c), width=180, height=36)
            btn.pack(pady=2)
        
        # Spacer
        tk.Label(inner, text="", bg=Colors.BG_PANEL).pack(fill="y", expand=True)
        
        # Abort button
        abort = WeaponButton(inner, "■ MISSION ABORT", command=self._on_close, width=180, height=36)
        abort.pack(pady=(5, 0))
    
    def _build_telemetry(self, parent):
        """Build bottom telemetry bar."""
        self.telemetry = TelemetryBar(parent, height=self.TELEMETRY_HEIGHT)
        self.telemetry.grid(row=2, column=0, columnspan=3, sticky="ew", pady=(5, 0))
        self.animated.append(self.telemetry)
    
    def _update_clock(self):
        """Update clock display."""
        self.clock.config(text=datetime.now().strftime("%H:%M:%S"))
        self.after(1000, self._update_clock)
    
    def _toggle_system(self):
        """Toggle system engage/disengage."""
        if not self.is_running:
            self._engage()
        else:
            self._disengage()
    
    def _engage(self):
        """Engage FOX-3 systems."""
        self.log("PILOT AUTHORIZATION RECEIVED")
        self.log("ENGAGING ALL SYSTEMS...")
        
        self.engine = NovaBotEngine(
            status_callback=self._on_status_change,
            log_callback=self._on_log
        )
        self.engine.start()
        
        self.is_running = True
        self.engage_btn.set_engaged(True)
        self._set_status("online")
        
        self.log("ALL SYSTEMS ONLINE - WEAPONS FREE")
    
    def _disengage(self):
        """Disengage systems."""
        self.log("DISENGAGING SYSTEMS...")
        
        if self.engine:
            self.engine.stop()
            self.engine = None
        
        self.is_running = False
        self.engage_btn.set_engaged(False)
        self._set_status("offline")
        
        self.log("FOX-3 RTB COMPLETE")
    
    def _set_status(self, status):
        """Update all status indicators."""
        self.radar.set_state(status)
        self.ai_core.set_state(status)
        self.waveform.set_active(status in ["listening", "processing", "executing"])
        
        colors = {
            "offline": (Colors.TEXT_DIM, "OFFLINE"),
            "online": (Colors.GREEN_OK, "ONLINE"),
            "listening": (Colors.CYAN_GLOW, "SCANNING"),
            "processing": (Colors.ORANGE_GLOW, "COMPUTING"),
            "executing": (Colors.RED_ALERT, "ENGAGED"),
        }
        
        color, text = colors.get(status, (Colors.TEXT_DIM, "UNKNOWN"))
        self.status_dot.delete("all")
        self.status_dot.create_oval(1, 1, 9, 9, fill=color, outline="")
        self.status_label.config(text=text, fg=color)
    
    def _on_status_change(self, status):
        """Handle status change from engine."""
        self.after(0, lambda: self._process_status(status))
    
    def _process_status(self, status):
        """Process status update."""
        s = status.lower()
        if "listening" in s:
            self._set_status("listening")
        elif "processing" in s or "planning" in s:
            self._set_status("processing")
        elif "executing" in s:
            self._set_status("executing")
        elif "ready" in s or "complete" in s:
            self._set_status("online")
        elif "stop" in s:
            self._set_status("offline")
    
    def _on_log(self, message):
        """Handle log message from engine."""
        self.after(0, lambda: self.log(message))
    
    def log(self, message):
        """Write to flight data recorder."""
        self.fdr.write(message)
    
    def _quick_action(self, command):
        """Execute quick action."""
        if not self.is_running:
            self.log("!! ENGAGE SYSTEMS FIRST")
            return
        
        self.log(f">> DEPLOYING: {command.upper()}")
        self.engine.execute_command(command)
    
    def _on_close(self):
        """Clean shutdown."""
        if self.is_running:
            self._disengage()
        
        for component in self.animated:
            if hasattr(component, 'stop'):
                component.stop()
        
        self.destroy()


def main():
    """Launch FOX-3 Combat Interface."""
    app = Fox3HUD()
    app.mainloop()


if __name__ == "__main__":
    main()
