"""
███████╗ ██████╗ ██╗  ██╗      ██████╗ 
██╔════╝██╔═══██╗╚██╗██╔╝      ╚════██╗
█████╗  ██║   ██║ ╚███╔╝  █████╗ █████╔╝
██╔══╝  ██║   ██║ ██╔██╗  ╚════╝ ╚═══██╗
██║     ╚██████╔╝██╔╝ ██╗      ██████╔╝
╚═╝      ╚═════╝ ╚═╝  ╚═╝      ╚═════╝ 

FOX-3 TACTICAL COMBAT INTERFACE
Advanced Holographic HUD System
Featuring: Rotating F-16 Wireframe Model
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
    """Tactical HUD Color Scheme"""
    BG_DEEP = "#000000"           # Pure black background
    BG_PANEL = "#0a0a0a"          # Slightly lighter panel
    CYAN_GLOW = "#00E5FF"         # Primary neon cyan
    CYAN_BRIGHT = "#00FFFF"       # Bright cyan
    CYAN_DIM = "#004455"          # Dimmed cyan
    CYAN_DARK = "#002233"         # Very dim cyan
    BLUE_ELECTRIC = "#0066FF"     # Electric blue
    ORANGE_GLOW = "#FF6600"       # Alert orange
    RED_ALERT = "#FF0033"         # Critical red
    GREEN_OK = "#00FF66"          # Success green
    WHITE = "#FFFFFF"             # Pure white
    TEXT_DIM = "#336677"          # Dimmed text
    GRID_LINE = "#0a2530"         # Grid lines


# ==================== F-16 WIREFRAME MODEL ====================
class F16Model:
    """3D wireframe data for F-16 Fighting Falcon"""
    
    # Simplified F-16 vertices (x, y, z) - scaled model
    VERTICES = [
        # Nose cone
        (0, 0, 50),           # 0 - nose tip
        (-5, -3, 35),         # 1 - nose left top
        (5, -3, 35),          # 2 - nose right top
        (-5, 3, 35),          # 3 - nose left bottom
        (5, 3, 35),           # 4 - nose right bottom
        
        # Cockpit
        (-6, -8, 25),         # 5 - cockpit left top
        (6, -8, 25),          # 6 - cockpit right top
        (-6, 2, 25),          # 7 - cockpit left bottom
        (6, 2, 25),           # 8 - cockpit right bottom
        
        # Fuselage front
        (-8, -5, 10),         # 9 - fuse front left top
        (8, -5, 10),          # 10 - fuse front right top
        (-8, 5, 10),          # 11 - fuse front left bottom
        (8, 5, 10),           # 12 - fuse front right bottom
        
        # Fuselage mid
        (-10, -6, -15),       # 13 - fuse mid left top
        (10, -6, -15),        # 14 - fuse mid right top
        (-10, 6, -15),        # 15 - fuse mid left bottom
        (10, 6, -15),         # 16 - fuse mid right bottom
        
        # Fuselage rear
        (-8, -5, -40),        # 17 - fuse rear left top
        (8, -5, -40),         # 18 - fuse rear right top
        (-8, 5, -40),         # 19 - fuse rear left bottom
        (8, 5, -40),          # 20 - fuse rear right bottom
        
        # Engine nozzle
        (-6, 0, -50),         # 21 - nozzle left
        (6, 0, -50),          # 22 - nozzle right
        (0, -5, -50),         # 23 - nozzle top
        (0, 5, -50),          # 24 - nozzle bottom
        
        # Wings
        (-45, 0, -10),        # 25 - left wing tip
        (45, 0, -10),         # 26 - right wing tip
        (-35, 0, -25),        # 27 - left wing rear
        (35, 0, -25),         # 28 - right wing rear
        
        # Horizontal stabilizers
        (-20, 0, -45),        # 29 - left stab tip
        (20, 0, -45),         # 30 - right stab tip
        (-15, 0, -38),        # 31 - left stab front
        (15, 0, -38),         # 32 - right stab front
        
        # Vertical tail
        (0, -25, -35),        # 33 - tail top
        (0, -20, -25),        # 34 - tail front
        (0, -8, -45),         # 35 - tail rear
        
        # Air intake (bottom)
        (-7, 8, 15),          # 36 - intake left
        (7, 8, 15),           # 37 - intake right
        (-5, 12, -5),         # 38 - intake rear left
        (5, 12, -5),          # 39 - intake rear right
    ]
    
    # Edges connecting vertices
    EDGES = [
        # Nose
        (0, 1), (0, 2), (0, 3), (0, 4),
        (1, 2), (3, 4), (1, 3), (2, 4),
        
        # Nose to cockpit
        (1, 5), (2, 6), (3, 7), (4, 8),
        (5, 6), (7, 8), (5, 7), (6, 8),
        
        # Cockpit to fuselage front
        (5, 9), (6, 10), (7, 11), (8, 12),
        (9, 10), (11, 12), (9, 11), (10, 12),
        
        # Fuselage front to mid
        (9, 13), (10, 14), (11, 15), (12, 16),
        (13, 14), (15, 16), (13, 15), (14, 16),
        
        # Fuselage mid to rear
        (13, 17), (14, 18), (15, 19), (16, 20),
        (17, 18), (19, 20), (17, 19), (18, 20),
        
        # Rear to nozzle
        (17, 21), (18, 22), (17, 23), (18, 23),
        (19, 21), (20, 22), (19, 24), (20, 24),
        (21, 23), (22, 23), (21, 24), (22, 24),
        
        # Wings
        (11, 25), (12, 26),   # Wing root front
        (15, 27), (16, 28),   # Wing root rear
        (25, 27), (26, 28),   # Wing trailing edge
        (11, 27), (12, 28),   # Wing leading edge inner
        
        # Horizontal stabilizers
        (19, 29), (20, 30),   # Stab root
        (31, 29), (32, 30),   # Stab leading
        (29, 35), (30, 35),   # Stab trailing
        (17, 31), (18, 32),
        
        # Vertical tail
        (17, 34), (18, 34),
        (34, 33), (33, 35),
        (17, 35), (18, 35),
        
        # Air intake
        (36, 37), (36, 38), (37, 39),
        (38, 39), (11, 36), (12, 37),
        (15, 38), (16, 39),
    ]


class RotatingF16(tk.Canvas):
    """Rotating wireframe F-16 hologram display"""
    
    def __init__(self, parent, size=280, **kwargs):
        super().__init__(parent, width=size, height=size+60, 
                        bg=Colors.BG_DEEP, highlightthickness=0, **kwargs)
        self.size = size
        self.center_x = size // 2
        self.center_y = size // 2 + 20
        self.scale = 2.2
        
        # Rotation angles
        self.angle_x = 0.3  # Slight pitch
        self.angle_y = 0
        self.angle_z = 0.1  # Slight roll
        
        self.state = "offline"
        self._animating = True
        self._animate()
    
    def set_state(self, state):
        self.state = state
    
    def _rotate_point(self, x, y, z):
        """Apply 3D rotation to a point"""
        # Rotate around Y axis (main rotation)
        cos_y, sin_y = math.cos(self.angle_y), math.sin(self.angle_y)
        x, z = x * cos_y - z * sin_y, x * sin_y + z * cos_y
        
        # Rotate around X axis (pitch)
        cos_x, sin_x = math.cos(self.angle_x), math.sin(self.angle_x)
        y, z = y * cos_x - z * sin_x, y * sin_x + z * cos_x
        
        # Rotate around Z axis (roll)
        cos_z, sin_z = math.cos(self.angle_z), math.sin(self.angle_z)
        x, y = x * cos_z - y * sin_z, x * sin_z + y * cos_z
        
        return x, y, z
    
    def _project(self, x, y, z):
        """Project 3D point to 2D with perspective"""
        # Simple perspective projection
        fov = 200
        z_offset = 100
        
        scale = fov / (z + z_offset) if (z + z_offset) > 0 else fov / 0.1
        screen_x = self.center_x + x * scale * self.scale
        screen_y = self.center_y - y * scale * self.scale  # Invert Y
        
        return screen_x, screen_y, z
    
    def _draw_scan_lines(self):
        """Draw horizontal scan lines effect"""
        for i in range(0, self.size + 60, 4):
            alpha = 0.03 + 0.02 * math.sin(i * 0.1 + self.angle_y * 2)
            if random.random() < 0.3:
                self.create_line(0, i, self.size, i, 
                               fill=Colors.CYAN_DARK, width=1, tags="scanline")
    
    def _draw_hologram_base(self):
        """Draw holographic projection base"""
        base_y = self.size + 30
        
        # Base glow ellipse
        for i in range(5, 0, -1):
            glow_color = Colors.CYAN_DARK if i > 2 else Colors.CYAN_DIM
            self.create_oval(
                30 - i*3, base_y - 15 - i*2,
                self.size - 30 + i*3, base_y + 15 + i*2,
                outline=glow_color, width=1, tags="base"
            )
        
        # Base platform
        self.create_oval(40, base_y - 10, self.size - 40, base_y + 10,
                        outline=Colors.CYAN_GLOW, width=2, tags="base")
    
    def _animate(self):
        if not self._animating:
            return
        
        self.delete("all")
        
        # Draw scan lines
        self._draw_scan_lines()
        
        # Draw hologram base
        self._draw_hologram_base()
        
        # Calculate and store projected vertices with depth
        projected = []
        for vx, vy, vz in F16Model.VERTICES:
            rx, ry, rz = self._rotate_point(vx, vy, vz)
            px, py, pz = self._project(rx, ry, rz)
            projected.append((px, py, pz))
        
        # Choose color based on state
        if self.state == "offline":
            edge_color = Colors.CYAN_DIM
            glow_color = Colors.CYAN_DARK
        elif self.state == "listening":
            edge_color = Colors.CYAN_BRIGHT
            glow_color = Colors.CYAN_GLOW
        elif self.state == "processing":
            edge_color = Colors.ORANGE_GLOW
            glow_color = "#FF9933"
        elif self.state == "executing":
            edge_color = Colors.RED_ALERT
            glow_color = "#FF6666"
        else:
            edge_color = Colors.CYAN_GLOW
            glow_color = Colors.CYAN_DIM
        
        # Sort edges by average depth for painter's algorithm
        edge_depths = []
        for v1, v2 in F16Model.EDGES:
            avg_z = (projected[v1][2] + projected[v2][2]) / 2
            edge_depths.append((avg_z, v1, v2))
        edge_depths.sort(reverse=True)  # Draw far edges first
        
        # Draw edges with glow effect
        for depth, v1, v2 in edge_depths:
            x1, y1, _ = projected[v1]
            x2, y2, _ = projected[v2]
            
            # Depth-based alpha (farther = dimmer)
            brightness = max(0.3, min(1.0, (depth + 50) / 100))
            
            # Glow layer
            self.create_line(x1, y1, x2, y2, fill=glow_color, width=3, tags="glow")
            # Main line
            self.create_line(x1, y1, x2, y2, fill=edge_color, width=1, tags="edge")
        
        # Draw vertices as glowing points
        for px, py, pz in projected:
            brightness = max(0.5, min(1.0, (pz + 50) / 100))
            size = 2 + brightness
            self.create_oval(px - size, py - size, px + size, py + size,
                           fill=edge_color, outline="", tags="vertex")
        
        # Draw label
        self.create_text(self.size // 2, 15, text="F-16 FIGHTING FALCON",
                        font=("Consolas", 9, "bold"), fill=Colors.CYAN_GLOW, tags="label")
        
        # Status text
        status_text = self.state.upper() if self.state != "offline" else "STANDBY"
        self.create_text(self.size // 2, self.size + 50, text=status_text,
                        font=("Consolas", 8), fill=edge_color, tags="status")
        
        # Rotate for next frame
        self.angle_y += 0.02  # Continuous Y rotation
        
        self.after(33, self._animate)  # ~30 FPS
    
    def stop(self):
        self._animating = False


# ==================== CENTRAL RUN BUTTON ====================
class CentralRunButton(tk.Canvas):
    """Central circular Run/Stop button with rotating rings"""
    
    def __init__(self, parent, command=None, size=220, **kwargs):
        super().__init__(parent, width=size, height=size, 
                        bg=Colors.BG_DEEP, highlightthickness=0, **kwargs)
        self.size = size
        self.center = size // 2
        self.command = command
        self.engaged = False
        self.hover = False
        self.ring_angle = 0
        self.pulse = 0
        self._animating = True
        
        self.bind("<Enter>", lambda e: self._set_hover(True))
        self.bind("<Leave>", lambda e: self._set_hover(False))
        self.bind("<Button-1>", self._on_click)
        
        self._animate()
    
    def _set_hover(self, hover):
        self.hover = hover
    
    def _on_click(self, event):
        # Check if click is within center button area
        dx = event.x - self.center
        dy = event.y - self.center
        if dx*dx + dy*dy < 35*35:  # Within inner button
            if self.command:
                self.command()
    
    def set_engaged(self, engaged):
        self.engaged = engaged
    
    def _draw_ring(self, radius, segments, gap, width, color, rotation=0):
        """Draw a segmented ring"""
        segment_angle = (2 * math.pi - gap * segments) / segments
        
        for i in range(segments):
            start = rotation + i * (segment_angle + gap)
            
            # Calculate arc points
            points = []
            steps = 20
            for j in range(steps + 1):
                angle = start + (segment_angle * j / steps)
                x = self.center + radius * math.cos(angle)
                y = self.center + radius * math.sin(angle)
                points.extend([x, y])
            
            if len(points) >= 4:
                self.create_line(points, fill=color, width=width, 
                               smooth=True, tags="ring")
    
    def _draw_tick_marks(self, radius, count, length, color):
        """Draw tick marks around a circle"""
        for i in range(count):
            angle = 2 * math.pi * i / count
            x1 = self.center + radius * math.cos(angle)
            y1 = self.center + radius * math.sin(angle)
            x2 = self.center + (radius + length) * math.cos(angle)
            y2 = self.center + (radius + length) * math.sin(angle)
            
            # Every 5th tick is longer
            if i % 5 == 0:
                self.create_line(x1, y1, x2 + length*0.5*math.cos(angle), 
                               y2 + length*0.5*math.sin(angle),
                               fill=color, width=2, tags="tick")
            else:
                self.create_line(x1, y1, x2, y2, fill=color, width=1, tags="tick")
    
    def _animate(self):
        if not self._animating:
            return
        
        self.delete("all")
        c = self.center
        
        self.pulse += 0.08
        pulse_val = (math.sin(self.pulse) + 1) / 2
        
        # Colors based on state
        if self.engaged:
            main_color = Colors.RED_ALERT
            glow_color = "#FF6666"
            btn_text = "Stop"
        else:
            main_color = Colors.CYAN_GLOW
            glow_color = Colors.CYAN_DIM
            btn_text = "Run"
        
        # Outer tick marks ring
        self._draw_tick_marks(95, 60, 8, Colors.CYAN_DIM)
        
        # Outer rotating ring (segmented)
        self._draw_ring(85, 8, 0.15, 2, Colors.CYAN_DIM, self.ring_angle)
        
        # Middle rotating ring (opposite direction)
        self._draw_ring(72, 12, 0.1, 3, main_color, -self.ring_angle * 1.5)
        
        # Inner static ring with gradient effect
        for i in range(3):
            self.create_oval(
                c - 58 + i, c - 58 + i, c + 58 - i, c + 58 - i,
                outline=glow_color if i == 0 else main_color, 
                width=2 - i*0.5, tags="inner_ring"
            )
        
        # Decorative inner elements
        self._draw_ring(50, 16, 0.08, 1, Colors.CYAN_DIM, self.ring_angle * 2)
        
        # Center button glow
        glow_radius = 38 + pulse_val * 3
        for i in range(5, 0, -1):
            self.create_oval(
                c - glow_radius - i*2, c - glow_radius - i*2,
                c + glow_radius + i*2, c + glow_radius + i*2,
                outline=glow_color, width=1, tags="btn_glow"
            )
        
        # Center button
        btn_fill = main_color if self.hover else Colors.BG_PANEL
        btn_outline = main_color
        self.create_oval(c - 35, c - 35, c + 35, c + 35,
                        fill=btn_fill, outline=btn_outline, width=3, tags="btn")
        
        # Button text
        text_color = Colors.BG_DEEP if self.hover else main_color
        self.create_text(c, c, text=btn_text, font=("Consolas", 16, "bold"),
                        fill=text_color, tags="btn_text")
        
        # Rotating elements
        self.ring_angle += 0.02
        
        self.after(33, self._animate)
    
    def stop(self):
        self._animating = False


# ==================== LOADING BAR ====================
class LoadingBar(tk.Canvas):
    """Animated loading/progress bar"""
    
    def __init__(self, parent, width=250, height=25, **kwargs):
        super().__init__(parent, width=width, height=height,
                        bg=Colors.BG_DEEP, highlightthickness=0, **kwargs)
        self.bar_width = width
        self.bar_height = height
        self.progress = 0
        self.target_progress = 100
        self.text = "INITIATING SYSTEM 1...."
        self.scan_pos = 0
        self._animating = True
        self._animate()
    
    def set_progress(self, value, text=None):
        self.target_progress = max(0, min(100, value))
        if text:
            self.text = text
    
    def _animate(self):
        if not self._animating:
            return
        
        self.delete("all")
        w, h = self.bar_width, self.bar_height
        
        # Animate progress
        if self.progress < self.target_progress:
            self.progress += 2
        elif self.progress > self.target_progress:
            self.progress -= 2
        
        # Draw text
        self.create_text(5, 3, text=self.text, anchor="nw",
                        font=("Consolas", 9, "bold"), fill=Colors.CYAN_GLOW)
        
        # Bar background
        bar_y = 18
        bar_h = 6
        self.create_rectangle(0, bar_y, w, bar_y + bar_h,
                            outline=Colors.CYAN_DIM, fill=Colors.BG_PANEL, width=1)
        
        # Progress fill with segments
        fill_width = (w - 4) * self.progress / 100
        segment_width = 8
        for x in range(2, int(fill_width), segment_width + 2):
            seg_w = min(segment_width, fill_width - x + 2)
            self.create_rectangle(x, bar_y + 1, x + seg_w, bar_y + bar_h - 1,
                                fill=Colors.CYAN_GLOW, outline="")
        
        # Scanning effect
        self.scan_pos = (self.scan_pos + 3) % w
        self.create_line(self.scan_pos, bar_y, self.scan_pos, bar_y + bar_h,
                        fill=Colors.WHITE, width=2)
        
        self.after(50, self._animate)
    
    def stop(self):
        self._animating = False


# ==================== CIRCULAR RADAR ====================
class CircularRadar(tk.Canvas):
    """Circular radar display with sweep animation"""
    
    def __init__(self, parent, size=120, **kwargs):
        super().__init__(parent, width=size, height=size,
                        bg=Colors.BG_DEEP, highlightthickness=0, **kwargs)
        self.size = size
        self.center = size // 2
        self.sweep_angle = 0
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
        r = c - 10
        
        # Outer circle
        self.create_oval(5, 5, self.size - 5, self.size - 5,
                        outline=Colors.CYAN_DIM, width=2)
        
        # Inner circles
        for i in range(1, 4):
            ri = r * i / 4
            self.create_oval(c - ri, c - ri, c + ri, c + ri,
                           outline=Colors.CYAN_DARK, width=1)
        
        # Cross lines
        self.create_line(c, 5, c, self.size - 5, fill=Colors.CYAN_DARK, width=1)
        self.create_line(5, c, self.size - 5, c, fill=Colors.CYAN_DARK, width=1)
        
        # Tick marks
        for i in range(36):
            angle = i * math.pi / 18
            inner = r - 5
            outer = r
            if i % 3 == 0:
                inner = r - 10
            x1 = c + inner * math.cos(angle)
            y1 = c + inner * math.sin(angle)
            x2 = c + outer * math.cos(angle)
            y2 = c + outer * math.sin(angle)
            self.create_line(x1, y1, x2, y2, fill=Colors.CYAN_DIM, width=1)
        
        # Sweep line (if active)
        if self.state != "offline":
            color = Colors.CYAN_GLOW if self.state == "online" else Colors.ORANGE_GLOW
            end_x = c + r * math.cos(self.sweep_angle)
            end_y = c - r * math.sin(self.sweep_angle)
            
            # Sweep trail
            for i in range(20):
                trail_angle = self.sweep_angle - i * 0.05
                tr = r * (1 - i * 0.02)
                tx = c + tr * math.cos(trail_angle)
                ty = c - tr * math.sin(trail_angle)
                self.create_line(c, c, tx, ty, fill=Colors.CYAN_DIM, width=1)
            
            self.create_line(c, c, end_x, end_y, fill=color, width=2)
            
            self.sweep_angle += 0.1
        
        # Center dot
        self.create_oval(c - 3, c - 3, c + 3, c + 3, fill=Colors.CYAN_GLOW, outline="")
        
        self.after(50, self._animate)
    
    def stop(self):
        self._animating = False


# ==================== CHEVRON INDICATOR ====================
class ChevronIndicator(tk.Canvas):
    """Animated chevron/arrow indicator"""
    
    def __init__(self, parent, width=80, height=60, **kwargs):
        super().__init__(parent, width=width, height=height,
                        bg=Colors.BG_DEEP, highlightthickness=0, **kwargs)
        self.w = width
        self.h = height
        self.pulse = 0
        self.state = "offline"
        self._animating = True
        self._animate()
    
    def set_state(self, state):
        self.state = state
    
    def _animate(self):
        if not self._animating:
            return
        
        self.delete("all")
        
        self.pulse += 0.15
        pulse_val = (math.sin(self.pulse) + 1) / 2
        
        color = Colors.CYAN_GLOW if self.state != "offline" else Colors.CYAN_DIM
        
        # Draw multiple chevrons with animation
        for i in range(3):
            offset = i * 20 - 20
            alpha = max(0.3, 1 - i * 0.3 - pulse_val * 0.3)
            
            # Chevron shape pointing right
            points = [
                5 + offset, 10,
                self.w - 30 + offset, self.h // 2,
                5 + offset, self.h - 10,
                15 + offset, self.h // 2
            ]
            
            chev_color = color if alpha > 0.5 else Colors.CYAN_DIM
            self.create_polygon(points, fill="", outline=chev_color, width=2)
        
        self.after(50, self._animate)
    
    def stop(self):
        self._animating = False


# ==================== STATUS DOTS ====================
class StatusDots(tk.Canvas):
    """Status indicator dots"""
    
    def __init__(self, parent, count=4, **kwargs):
        super().__init__(parent, width=count * 25, height=20,
                        bg=Colors.BG_DEEP, highlightthickness=0, **kwargs)
        self.count = count
        self.active = 0
        self.pulse = 0
        self._animating = True
        self._animate()
    
    def set_active(self, count):
        self.active = min(count, self.count)
    
    def _animate(self):
        if not self._animating:
            return
        
        self.delete("all")
        self.pulse += 0.1
        
        for i in range(self.count):
            x = 12 + i * 25
            y = 10
            
            if i < self.active:
                # Active dot with glow
                glow_size = 8 + math.sin(self.pulse + i) * 2
                self.create_oval(x - glow_size, y - glow_size, 
                               x + glow_size, y + glow_size,
                               fill=Colors.CYAN_DIM, outline="")
                self.create_oval(x - 5, y - 5, x + 5, y + 5,
                               fill=Colors.CYAN_GLOW, outline="")
            else:
                # Inactive dot
                self.create_oval(x - 5, y - 5, x + 5, y + 5,
                               fill=Colors.CYAN_DARK, outline=Colors.CYAN_DIM, width=1)
        
        self.after(50, self._animate)
    
    def stop(self):
        self._animating = False


# ==================== INFO PANEL ====================
class InfoPanel(tk.Canvas):
    """Sci-fi styled information panel with corner accents"""
    
    def __init__(self, parent, width=260, height=90, title="", **kwargs):
        super().__init__(parent, width=width, height=height,
                        bg=Colors.BG_DEEP, highlightthickness=0, **kwargs)
        self.panel_width = width
        self.panel_height = height
        self.title = title
        self.content_lines = []
        self._draw()
    
    def set_content(self, lines):
        self.content_lines = lines
        self._draw()
    
    def _draw(self):
        self.delete("all")
        w, h = self.panel_width, self.panel_height
        
        # Main border
        self.create_rectangle(8, 8, w - 8, h - 8,
                            outline=Colors.CYAN_DIM, width=2)
        
        # Corner accents
        corner_size = 15
        accent_color = Colors.CYAN_GLOW
        
        # Top-left
        self.create_line(3, 3, 3 + corner_size, 3, fill=accent_color, width=2)
        self.create_line(3, 3, 3, 3 + corner_size, fill=accent_color, width=2)
        
        # Top-right
        self.create_line(w - 3, 3, w - 3 - corner_size, 3, fill=accent_color, width=2)
        self.create_line(w - 3, 3, w - 3, 3 + corner_size, fill=accent_color, width=2)
        
        # Bottom-left
        self.create_line(3, h - 3, 3 + corner_size, h - 3, fill=accent_color, width=2)
        self.create_line(3, h - 3, 3, h - 3 - corner_size, fill=accent_color, width=2)
        
        # Bottom-right
        self.create_line(w - 3, h - 3, w - 3 - corner_size, h - 3, fill=accent_color, width=2)
        self.create_line(w - 3, h - 3, w - 3, h - 3 - corner_size, fill=accent_color, width=2)
        
        # Title
        if self.title:
            self.create_text(w // 2, 18, text=self.title,
                           font=("Consolas", 9, "bold"), fill=Colors.CYAN_GLOW)
        
        # Content
        y = 35
        for line in self.content_lines[:4]:
            self.create_text(15, y, text=line, anchor="w",
                           font=("Consolas", 8), fill=Colors.TEXT_DIM)
            y += 14


# ==================== HEXAGONAL BORDER ====================
class HexBorder(tk.Canvas):
    """Bottom hexagonal circuit border"""
    
    def __init__(self, parent, height=50, **kwargs):
        super().__init__(parent, height=height,
                        bg=Colors.BG_DEEP, highlightthickness=0, **kwargs)
        self.border_height = height
        self.pulse = 0
        self._animating = True
        self.bind("<Configure>", lambda e: self._draw())
        self._animate()
    
    def _animate(self):
        if not self._animating:
            return
        
        self.pulse += 0.05
        self._draw()
        self.after(100, self._animate)
    
    def _draw(self):
        self.delete("all")
        w = self.winfo_width() or 1130
        h = self.border_height
        
        # Hexagonal pattern points
        segments = 12
        seg_width = w / segments
        
        points = [0, h]  # Start bottom-left
        
        for i in range(segments + 1):
            x = i * seg_width
            # Alternate heights for hexagonal effect
            if i % 2 == 0:
                y = h - 15
            else:
                y = h - 30 - math.sin(self.pulse + i * 0.5) * 3
            points.extend([x, y])
        
        points.extend([w, h])  # End bottom-right
        
        # Draw glowing border
        for offset in range(3, 0, -1):
            glow_points = points.copy()
            self.create_line(glow_points, fill=Colors.CYAN_DIM if offset > 1 else Colors.CYAN_GLOW,
                           width=offset, smooth=False)
        
        # Add node points at vertices
        for i in range(segments + 1):
            x = i * seg_width
            y = h - 15 if i % 2 == 0 else h - 30
            
            # Glowing node
            node_size = 3 + math.sin(self.pulse + i) * 1
            self.create_oval(x - node_size, y - node_size, x + node_size, y + node_size,
                           fill=Colors.CYAN_GLOW, outline="")
    
    def stop(self):
        self._animating = False


# ==================== MISSION LOG ====================
class MissionLog(tk.Frame):
    """Mission log display panel"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=Colors.BG_DEEP, **kwargs)
        
        # Create text widget with custom styling
        self.log = tk.Text(self, bg=Colors.BG_DEEP, fg=Colors.CYAN_GLOW,
                          font=("Consolas", 9), wrap="word",
                          insertbackground=Colors.CYAN_GLOW,
                          relief="flat", padx=10, pady=10,
                          highlightthickness=1,
                          highlightbackground=Colors.CYAN_DIM)
        self.log.pack(fill="both", expand=True)
        self.log.config(state="disabled")
        
        # Configure tags
        self.log.tag_configure("time", foreground=Colors.TEXT_DIM)
        self.log.tag_configure("info", foreground=Colors.CYAN_GLOW)
        self.log.tag_configure("warn", foreground=Colors.ORANGE_GLOW)
        self.log.tag_configure("error", foreground=Colors.RED_ALERT)
        self.log.tag_configure("success", foreground=Colors.GREEN_OK)
        
        # Mouse wheel scrolling
        self.log.bind("<MouseWheel>", self._on_scroll)
    
    def _on_scroll(self, event):
        self.log.yview_scroll(int(-1 * (event.delta / 120)), "units")
        return "break"
    
    def write(self, message):
        self.log.config(state="normal")
        
        time_str = datetime.now().strftime("%H:%M:%S")
        
        msg_lower = message.lower()
        if "error" in msg_lower or "fault" in msg_lower:
            tag = "error"
        elif "warning" in msg_lower:
            tag = "warn"
        elif "success" in msg_lower or "complete" in msg_lower:
            tag = "success"
        else:
            tag = "info"
        
        # Clean emojis
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


# ==================== MAIN FOX-3 HUD ====================
class Fox3HUD(tk.Tk):
    """FOX-3 Tactical Combat Interface"""
    
    WINDOW_WIDTH = 1130
    WINDOW_HEIGHT = 600
    
    def __init__(self):
        super().__init__()
        
        self.title("FOX-3 // TACTICAL SYSTEMS")
        self.geometry(f"{self.WINDOW_WIDTH}x{self.WINDOW_HEIGHT}")
        self.resizable(False, False)
        self.configure(bg=Colors.BG_DEEP)
        
        self.engine = None
        self.is_running = False
        self.animated = []
        
        self._build_ui()
        
        self.log("FOX-3 TACTICAL SYSTEMS INITIALIZED")
        self.log("ALL SUBSYSTEMS: STANDBY")
        self.log("AWAITING PILOT AUTHORIZATION...")
        
        self.protocol("WM_DELETE_WINDOW", self._on_close)
    
    def _build_ui(self):
        """Build the tactical interface"""
        
        # Main container
        main = tk.Frame(self, bg=Colors.BG_DEEP)
        main.pack(fill="both", expand=True, padx=15, pady=10)
        
        # === TOP SECTION ===
        top = tk.Frame(main, bg=Colors.BG_DEEP)
        top.pack(fill="x", pady=(0, 10))
        
        # Left: Loading bar and status
        top_left = tk.Frame(top, bg=Colors.BG_DEEP)
        top_left.pack(side="left")
        
        self.loading_bar = LoadingBar(top_left, width=280, height=25)
        self.loading_bar.pack(anchor="w")
        self.animated.append(self.loading_bar)
        
        # Center: Status dots
        top_center = tk.Frame(top, bg=Colors.BG_DEEP)
        top_center.pack(side="left", expand=True)
        
        self.status_dots = StatusDots(top_center, count=4)
        self.status_dots.pack()
        self.status_dots.set_active(1)
        self.animated.append(self.status_dots)
        
        # Right: Input field placeholder
        top_right = tk.Frame(top, bg=Colors.BG_DEEP)
        top_right.pack(side="right")
        
        self.input_frame = tk.Frame(top_right, bg=Colors.CYAN_DIM, padx=2, pady=2)
        self.input_frame.pack()
        self.input_display = tk.Label(self.input_frame, text="", width=25,
                                      bg=Colors.BG_DEEP, fg=Colors.CYAN_GLOW,
                                      font=("Consolas", 10), anchor="w", padx=5)
        self.input_display.pack()
        
        # === MIDDLE SECTION ===
        middle = tk.Frame(main, bg=Colors.BG_DEEP)
        middle.pack(fill="both", expand=True)
        
        # Left panel
        left_panel = tk.Frame(middle, bg=Colors.BG_DEEP, width=280)
        left_panel.pack(side="left", fill="y", padx=(0, 15))
        left_panel.pack_propagate(False)
        
        # Chevron and Radar row
        top_row = tk.Frame(left_panel, bg=Colors.BG_DEEP)
        top_row.pack(fill="x", pady=(0, 10))
        
        self.chevron = ChevronIndicator(top_row, width=80, height=60)
        self.chevron.pack(side="left", padx=(0, 10))
        self.animated.append(self.chevron)
        
        self.radar = CircularRadar(top_row, size=120)
        self.radar.pack(side="left")
        self.animated.append(self.radar)
        
        # Info panels
        self.panel1 = InfoPanel(left_panel, width=260, height=90, title="SYSTEM STATUS")
        self.panel1.pack(pady=(0, 10))
        self.panel1.set_content(["MODE: STANDBY", "VOICE: READY", "AI: LOADED", "NET: CONNECTED"])
        
        self.panel2 = InfoPanel(left_panel, width=260, height=90, title="MISSION DATA")
        self.panel2.pack()
        self.panel2.set_content(["COMMANDS: 0", "SUCCESS: 0", "ERRORS: 0", "UPTIME: 00:00"])
        
        # Center panel - Run button
        center_panel = tk.Frame(middle, bg=Colors.BG_DEEP)
        center_panel.pack(side="left", fill="both", expand=True, padx=15)
        
        # Center the run button vertically
        center_spacer = tk.Frame(center_panel, bg=Colors.BG_DEEP)
        center_spacer.pack(expand=True)
        
        self.run_button = CentralRunButton(center_panel, command=self._toggle_system, size=220)
        self.run_button.pack()
        self.animated.append(self.run_button)
        
        center_spacer2 = tk.Frame(center_panel, bg=Colors.BG_DEEP)
        center_spacer2.pack(expand=True)
        
        # Right panel - F-16 and log
        right_panel = tk.Frame(middle, bg=Colors.BG_DEEP, width=320)
        right_panel.pack(side="right", fill="y", padx=(15, 0))
        right_panel.pack_propagate(False)
        
        self.f16 = RotatingF16(right_panel, size=280)
        self.f16.pack(pady=(0, 10))
        self.animated.append(self.f16)
        
        # Mini log
        log_label = tk.Label(right_panel, text="MISSION LOG", 
                            font=("Consolas", 9, "bold"),
                            fg=Colors.CYAN_GLOW, bg=Colors.BG_DEEP)
        log_label.pack(anchor="w")
        
        self.mission_log = MissionLog(right_panel)
        self.mission_log.pack(fill="both", expand=True)
        
        # === BOTTOM SECTION ===
        bottom = tk.Frame(main, bg=Colors.BG_DEEP)
        bottom.pack(fill="x", pady=(10, 0))
        
        self.hex_border = HexBorder(bottom, height=40)
        self.hex_border.pack(fill="x")
        self.animated.append(self.hex_border)
        
        # Logo
        logo = tk.Label(main, text="FOX-3", font=("Consolas", 14, "bold"),
                       fg=Colors.CYAN_GLOW, bg=Colors.BG_DEEP)
        logo.place(relx=1.0, rely=1.0, anchor="se", x=-10, y=-5)
        
        # Start uptime counter
        self.start_time = datetime.now()
        self.command_count = 0
        self.success_count = 0
        self.error_count = 0
        self._update_stats()
    
    def _update_stats(self):
        """Update statistics panels"""
        uptime = datetime.now() - self.start_time
        mins = int(uptime.total_seconds() // 60)
        secs = int(uptime.total_seconds() % 60)
        
        self.panel2.set_content([
            f"COMMANDS: {self.command_count}",
            f"SUCCESS: {self.success_count}",
            f"ERRORS: {self.error_count}",
            f"UPTIME: {mins:02d}:{secs:02d}"
        ])
        
        self.after(1000, self._update_stats)
    
    def _toggle_system(self):
        """Toggle system on/off"""
        if not self.is_running:
            self._engage()
        else:
            self._disengage()
    
    def _engage(self):
        """Engage systems"""
        self.log("PILOT AUTHORIZATION CONFIRMED")
        self.log("ENGAGING ALL SYSTEMS...")
        
        self.loading_bar.set_progress(100, "SYSTEMS ONLINE")
        self.status_dots.set_active(4)
        
        self.engine = NovaBotEngine(
            status_callback=self._on_status_change,
            log_callback=self._on_log
        )
        self.engine.start()
        
        self.is_running = True
        self.run_button.set_engaged(True)
        self._set_status("online")
        
        self.panel1.set_content(["MODE: ACTIVE", "VOICE: LISTENING", "AI: PROCESSING", "NET: CONNECTED"])
        
        self.log("ALL SYSTEMS ONLINE - WEAPONS HOT")
    
    def _disengage(self):
        """Disengage systems"""
        self.log("DISENGAGING SYSTEMS...")
        
        if self.engine:
            self.engine.stop()
            self.engine = None
        
        self.is_running = False
        self.run_button.set_engaged(False)
        self._set_status("offline")
        
        self.loading_bar.set_progress(0, "SYSTEMS OFFLINE")
        self.status_dots.set_active(1)
        self.panel1.set_content(["MODE: STANDBY", "VOICE: READY", "AI: LOADED", "NET: CONNECTED"])
        
        self.log("FOX-3 RTB COMPLETE")
    
    def _set_status(self, status):
        """Update all status indicators"""
        self.radar.set_state(status)
        self.f16.set_state(status)
        self.chevron.set_state(status)
    
    def _on_status_change(self, status):
        """Handle status change from engine"""
        self.after(0, lambda: self._process_status(status))
    
    def _process_status(self, status):
        """Process status update"""
        s = status.lower()
        if "listening" in s:
            self._set_status("listening")
            self.input_display.config(text="LISTENING...")
        elif "processing" in s or "planning" in s:
            self._set_status("processing")
            self.input_display.config(text="PROCESSING...")
        elif "executing" in s:
            self._set_status("executing")
        elif "ready" in s or "complete" in s:
            self._set_status("online")
            self.input_display.config(text="")
            self.command_count += 1
            self.success_count += 1
        elif "stop" in s:
            self._set_status("offline")
    
    def _on_log(self, message):
        """Handle log from engine"""
        self.after(0, lambda: self.log(message))
    
    def log(self, message):
        """Write to mission log"""
        self.mission_log.write(message)
    
    def _on_close(self):
        """Clean shutdown"""
        if self.is_running:
            self._disengage()
        
        for component in self.animated:
            if hasattr(component, 'stop'):
                component.stop()
        
        self.destroy()


def main():
    """Launch FOX-3 Tactical Interface"""
    app = Fox3HUD()
    app.mainloop()


if __name__ == "__main__":
    main()
