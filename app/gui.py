"""
███████╗███████╗███╗   ██╗████████╗██╗███╗   ██╗███████╗██╗     
██╔════╝██╔════╝████╗  ██║╚══██╔══╝██║████╗  ██║██╔════╝██║     
███████╗█████╗  ██╔██╗ ██║   ██║   ██║██╔██╗ ██║█████╗  ██║     
╚════██║██╔══╝  ██║╚██╗██║   ██║   ██║██║╚██╗██║██╔══╝  ██║     
███████║███████╗██║ ╚████║   ██║   ██║██║ ╚████║███████╗███████╗
╚══════╝╚══════╝╚═╝  ╚═══╝   ╚═╝   ╚═╝╚═╝  ╚═══╝╚══════╝╚══════╝

SENTINEL-X // TACTICAL AI INTERFACE
Military HUD-Inspired Design System
"""

import tkinter as tk
from tkinter import ttk
import math
import random
import psutil
from datetime import datetime

# Import the bot engine
from app.main import NovaBotEngine


# ==================== TACTICAL DESIGN SYSTEM ====================
class Theme:
    """Military HUD Dark Theme - Tactical & Purpose-Built"""
    
    # Core Background - Deep Navy/Charcoal (NOT pure black)
    BG_DEEP = "#050508"           # Deepest layer
    BG_PRIMARY = "#0B0F19"        # Main background
    BG_SECONDARY = "#101620"      # Panel backgrounds
    BG_TERTIARY = "#161D2A"       # Elevated surfaces
    BG_GLASS = "#1A2332"          # Glass panel base
    BG_HOVER = "#243040"          # Hover states
    
    # Accent Colors - Tactical Cyan
    ACCENT_PRIMARY = "#00D4FF"    # Primary cyan
    ACCENT_SECONDARY = "#0099BB"  # Secondary cyan  
    ACCENT_TERTIARY = "#006680"   # Muted cyan
    ACCENT_GLOW = "#00E5FF"       # Glow effects
    ACCENT_DIM = "#004455"        # Very dim accent
    
    # State Colors
    SUCCESS = "#00E676"           # Green - success
    WARNING = "#FFB300"           # Amber - warning
    ERROR = "#FF5252"             # Red - error
    ACTIVE = "#FF8C00"            # Orange - listening/active
    
    # Text Hierarchy
    TEXT_PRIMARY = "#FFFFFF"      # Bright white
    TEXT_SECONDARY = "#8899AA"    # Muted blue-grey
    TEXT_MUTED = "#4A5568"        # Very muted
    TEXT_DIM = "#2D3748"          # Nearly invisible
    TEXT_ACCENT = "#00D4FF"       # Cyan text
    
    # Orb Colors by State
    ORB_IDLE = ["#00B8D4", "#0088A8", "#005568"]
    ORB_ACTIVE = ["#00E676", "#00C853", "#009624"]
    ORB_LISTENING = ["#FF8C00", "#FF6D00", "#E65100"]  # Orange for listening
    ORB_PROCESSING = ["#7C4DFF", "#651FFF", "#6200EA"]
    
    # Fonts - Tactical Stack
    FONT_TITLE = ("Segoe UI", 28, "bold")
    FONT_TITLE_ACCENT = ("Segoe UI", 28, "bold")
    FONT_SUBTITLE = ("Segoe UI", 10)
    FONT_STATUS = ("Segoe UI Semibold", 14)
    FONT_STATUS_SUB = ("Segoe UI", 9)
    FONT_ICON = ("Segoe UI Symbol", 16)
    FONT_ICON_LABEL = ("Segoe UI", 8)
    FONT_MONO = ("Consolas", 9)
    FONT_MONO_SMALL = ("Consolas", 8)
    FONT_LOG_TIME = ("Consolas", 8)
    FONT_LOG_TEXT = ("Segoe UI", 9)
    FONT_STATS = ("Consolas", 8)
    FONT_CLOCK = ("Segoe UI Light", 32)
    FONT_DATE = ("Segoe UI", 9)


# ==================== HUD BACKGROUND WITH HEXGRID ====================
class HUDBackground(tk.Canvas):
    """Tactical background with hexagonal grid and vignette"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=Theme.BG_PRIMARY, highlightthickness=0, **kwargs)
        self.time = 0
        self._animating = True
        self.bind("<Configure>", self._on_resize)
        self._draw_static = True
        self.after(100, self._initial_draw)
    
    def _initial_draw(self):
        self._draw_background()
        self._animate_subtle()
    
    def _on_resize(self, event):
        self._draw_static = True
        self.after(50, self._draw_background)
    
    def _draw_background(self):
        self.delete("bg")
        w = self.winfo_width()
        h = self.winfo_height()
        
        if w < 10 or h < 10:
            return
        
        # Vignette - darker edges
        vignette_layers = 8
        for i in range(vignette_layers):
            inset = i * 80
            alpha = 0.03 * (vignette_layers - i) / vignette_layers
            color = self._darken(Theme.BG_PRIMARY, alpha)
            if inset < min(w, h) // 2:
                self.create_rectangle(inset, inset, w - inset, h - inset, 
                                     fill=color, outline='', tags="bg")
        
        # Hexagonal grid - very subtle
        self._draw_hex_grid(w, h)
        
        # Corner HUD elements
        self._draw_corner_hud(w, h)
    
    def _draw_hex_grid(self, w, h):
        """Draw subtle hexagonal grid pattern"""
        hex_size = 40
        row_height = hex_size * 1.5
        col_width = hex_size * math.sqrt(3)
        
        for row in range(-1, int(h / row_height) + 2):
            for col in range(-1, int(w / col_width) + 2):
                x = col * col_width + (row % 2) * (col_width / 2)
                y = row * row_height
                
                # Only draw if visible
                if -hex_size < x < w + hex_size and -hex_size < y < h + hex_size:
                    self._draw_hexagon(x, y, hex_size * 0.9)
    
    def _draw_hexagon(self, cx, cy, size):
        """Draw a single hexagon"""
        points = []
        for i in range(6):
            angle = math.pi / 6 + i * math.pi / 3
            x = cx + size * math.cos(angle)
            y = cy + size * math.sin(angle)
            points.extend([x, y])
        
        # Very subtle hex outline
        self.create_polygon(points, fill='', outline=Theme.BG_TERTIARY, 
                           width=1, tags="bg")
    
    def _draw_corner_hud(self, w, h):
        """Draw tactical corner brackets"""
        bracket_size = 30
        bracket_color = Theme.ACCENT_DIM
        
        # Top-left
        self.create_line(5, 5, 5, 5 + bracket_size, fill=bracket_color, width=1, tags="bg")
        self.create_line(5, 5, 5 + bracket_size, 5, fill=bracket_color, width=1, tags="bg")
        
        # Top-right  
        self.create_line(w-5, 5, w-5, 5 + bracket_size, fill=bracket_color, width=1, tags="bg")
        self.create_line(w-5, 5, w-5 - bracket_size, 5, fill=bracket_color, width=1, tags="bg")
        
        # Bottom-left
        self.create_line(5, h-5, 5, h-5 - bracket_size, fill=bracket_color, width=1, tags="bg")
        self.create_line(5, h-5, 5 + bracket_size, h-5, fill=bracket_color, width=1, tags="bg")
        
        # Bottom-right
        self.create_line(w-5, h-5, w-5, h-5 - bracket_size, fill=bracket_color, width=1, tags="bg")
        self.create_line(w-5, h-5, w-5 - bracket_size, h-5, fill=bracket_color, width=1, tags="bg")
    
    def _animate_subtle(self):
        """Very subtle ambient animation"""
        if not self._animating:
            return
        self.time += 0.01
        # Could add subtle pulse effects here
        self.after(100, self._animate_subtle)
    
    def _darken(self, hex_color, amount):
        hex_color = hex_color.lstrip('#')
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        r = int(r * (1 - amount))
        g = int(g * (1 - amount))
        b = int(b * (1 - amount))
        return f'#{r:02x}{g:02x}{b:02x}'
    
    def stop(self):
        self._animating = False


# ==================== AUDIO WAVEFORM VISUALIZER ====================
class WaveformVisualizer(tk.Canvas):
    """Audio waveform visualization below the orb"""
    
    def __init__(self, parent, width=300, height=40, **kwargs):
        super().__init__(parent, width=width, height=height,
                        bg=Theme.BG_PRIMARY, highlightthickness=0, **kwargs)
        self.width = width
        self.height = height
        self.bars = 40
        self.levels = [0.0] * self.bars
        self.target_levels = [0.0] * self.bars
        self._animating = True
        self._animate()
    
    def set_level(self, level):
        """Update audio level (0.0 to 1.0)"""
        # Create wave pattern from center
        center = self.bars // 2
        for i in range(self.bars):
            dist = abs(i - center)
            noise = random.uniform(0.8, 1.2)
            falloff = max(0, 1 - dist / center)
            self.target_levels[i] = level * falloff * noise
    
    def _animate(self):
        if not self._animating:
            return
        
        self.delete("all")
        
        bar_width = self.width / self.bars
        center_y = self.height / 2
        
        for i in range(self.bars):
            # Smooth interpolation
            self.levels[i] += (self.target_levels[i] - self.levels[i]) * 0.3
            
            # Natural decay
            self.target_levels[i] *= 0.85
            
            bar_height = max(2, self.levels[i] * self.height * 0.8)
            
            x = i * bar_width + bar_width / 2
            
            # Gradient effect - brighter in center
            dist = abs(i - self.bars // 2) / (self.bars // 2)
            brightness = 1 - dist * 0.5
            
            color = self._lerp_color(Theme.ACCENT_TERTIARY, Theme.ACCENT_PRIMARY, 
                                     self.levels[i] * brightness)
            
            # Draw symmetric bar
            self.create_line(x, center_y - bar_height/2, 
                           x, center_y + bar_height/2,
                           fill=color, width=max(2, bar_width * 0.6))
        
        self.after(30, self._animate)
    
    def _lerp_color(self, c1, c2, t):
        c1 = c1.lstrip('#')
        c2 = c2.lstrip('#')
        r1, g1, b1 = tuple(int(c1[i:i+2], 16) for i in (0, 2, 4))
        r2, g2, b2 = tuple(int(c2[i:i+2], 16) for i in (0, 2, 4))
        r = int(r1 + (r2 - r1) * t)
        g = int(g1 + (g2 - g1) * t)
        b = int(b1 + (b2 - b1) * t)
        return f'#{r:02x}{g:02x}{b:02x}'
    
    def stop(self):
        self._animating = False


# ==================== LIVING ORB - TACTICAL CORE ====================
class LivingOrb(tk.Canvas):
    """
    Tactical orb with Saturn-like rings and particle system.
    Responds dynamically to system state and audio input.
    """
    
    def __init__(self, parent, size=350, **kwargs):
        super().__init__(parent, width=size, height=size,
                        bg=Theme.BG_PRIMARY, highlightthickness=0, **kwargs)
        
        self.size = size
        self.cx = size // 2
        self.cy = size // 2
        
        # Animation state
        self.time = 0
        self.state = "idle"
        self._animating = True
        
        # Particle system
        self.particles = []
        self._init_particles(80)
        
        # Ring system
        self.ring_particles = []
        self._init_ring_particles(120)
        
        # Wave ripples
        self.waves = []
        
        # Audio levels
        self.audio_level = 0
        self.target_audio = 0.1
        self._voice_level = 0.0
        
        # Ring rotation
        self.ring_angle = 0
        
        # Click handling
        self.on_click = None
        self.bind("<Button-1>", self._handle_click)
        self.bind("<Enter>", lambda e: self.config(cursor="hand2"))
        self.bind("<Leave>", lambda e: self.config(cursor=""))
        
        self._animate()
    
    def _init_particles(self, count):
        """Initialize orbital particles"""
        self.particles = []
        for _ in range(count):
            self.particles.append({
                'angle': random.uniform(0, 2 * math.pi),
                'radius': random.uniform(80, 180),
                'speed': random.uniform(0.002, 0.012),
                'size': random.uniform(1, 3),
                'offset': random.uniform(0, 2 * math.pi),
                'layer': random.randint(0, 2),
                'brightness': random.uniform(0.3, 1.0)
            })
    
    def _init_ring_particles(self, count):
        """Initialize Saturn ring particles"""
        self.ring_particles = []
        for i in range(count):
            angle = (2 * math.pi * i) / count
            self.ring_particles.append({
                'base_angle': angle,
                'radius': random.uniform(100, 140),
                'size': random.uniform(0.5, 2),
                'speed': random.uniform(0.3, 0.8),
                'z': random.uniform(-0.3, 0.3)  # 3D depth
            })
    
    def _handle_click(self, event):
        dx = event.x - self.cx
        dy = event.y - self.cy
        if math.sqrt(dx*dx + dy*dy) < 100:
            if self.on_click:
                self.on_click()
            # Ripple effect
            for _ in range(3):
                self.waves.append({'radius': 60, 'alpha': 1.0, 'width': 2})
    
    def set_state(self, state):
        self.state = state
        if state == "listening":
            self.target_audio = 0.5
        elif state == "processing":
            self.target_audio = 0.3
        elif state == "speaking":
            self.target_audio = 0.6
        elif state == "active":
            self.target_audio = 0.2
        else:
            self.target_audio = 0.1
    
    def set_voice_level(self, level):
        self._voice_level = max(0.0, min(1.0, level))
    
    def _get_colors(self):
        if self.state == "active" or self.state == "speaking":
            return Theme.ORB_ACTIVE
        elif self.state == "listening":
            return Theme.ORB_LISTENING
        elif self.state == "processing":
            return Theme.ORB_PROCESSING
        return Theme.ORB_IDLE
    
    def _hex_to_rgb(self, hex_color):
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    def _rgb_to_hex(self, rgb):
        return '#{:02x}{:02x}{:02x}'.format(
            max(0, min(255, int(rgb[0]))),
            max(0, min(255, int(rgb[1]))),
            max(0, min(255, int(rgb[2])))
        )
    
    def _lerp_color(self, c1, c2, t):
        r1, g1, b1 = self._hex_to_rgb(c1)
        r2, g2, b2 = self._hex_to_rgb(c2)
        return self._rgb_to_hex((
            r1 + (r2 - r1) * t,
            g1 + (g2 - g1) * t,
            b1 + (b2 - b1) * t
        ))
    
    def _animate(self):
        if not self._animating:
            return
        
        self.delete("all")
        self.time += 0.016
        self.ring_angle += 0.005 + self.audio_level * 0.01
        
        # Smooth audio interpolation
        combined = self.target_audio + self._voice_level * 0.6
        self.audio_level += (combined - self.audio_level) * 0.12
        
        colors = self._get_colors()
        
        # Draw layers back to front
        self._draw_outer_glow(colors)
        self._draw_orbital_particles(colors)
        self._draw_saturn_rings_back(colors)
        self._draw_core(colors)
        self._draw_saturn_rings_front(colors)
        self._draw_inner_rings(colors)
        self._draw_waves(colors)
        self._draw_center_point(colors)
        
        self.after(16, self._animate)
    
    def _draw_outer_glow(self, colors):
        """Soft ambient glow"""
        pulse = (math.sin(self.time * 1.2) + 1) / 2
        
        for i in range(6, 0, -1):
            radius = 130 + i * 12 + pulse * 8 + self.audio_level * 20
            alpha = 0.06 * (7 - i) / 6
            color = self._lerp_color(Theme.BG_PRIMARY, colors[0], alpha)
            self.create_oval(
                self.cx - radius, self.cy - radius,
                self.cx + radius, self.cy + radius,
                fill=color, outline=''
            )
    
    def _draw_orbital_particles(self, colors):
        """Orbiting dust particles"""
        for p in self.particles:
            p['angle'] += p['speed'] * (1 + self.audio_level * 1.5)
            
            wobble = math.sin(self.time * 1.5 + p['offset']) * 12
            radius = p['radius'] + wobble + self.audio_level * 30
            
            x = self.cx + radius * math.cos(p['angle'])
            y = self.cy + radius * math.sin(p['angle'])
            
            pulse = (math.sin(self.time * 2 + p['offset']) + 1) / 2
            size = p['size'] * (0.7 + 0.5 * pulse)
            
            alpha = p['brightness'] * (0.5 + 0.5 * pulse)
            color = self._lerp_color(Theme.BG_PRIMARY, colors[p['layer']], alpha)
            
            self.create_oval(x - size, y - size, x + size, y + size,
                           fill=color, outline='')
    
    def _draw_saturn_rings_back(self, colors):
        """Back portion of Saturn-style rings (behind orb)"""
        ring_tilt = 0.3  # Tilt angle
        base_radius = 110 + self.audio_level * 15
        
        for p in self.ring_particles:
            if p['z'] < 0:  # Back particles only
                self._draw_ring_particle(p, colors, base_radius, ring_tilt)
    
    def _draw_saturn_rings_front(self, colors):
        """Front portion of Saturn-style rings (in front of orb)"""
        ring_tilt = 0.3
        base_radius = 110 + self.audio_level * 15
        
        for p in self.ring_particles:
            if p['z'] >= 0:  # Front particles only
                self._draw_ring_particle(p, colors, base_radius, ring_tilt)
    
    def _draw_ring_particle(self, p, colors, base_radius, tilt):
        """Draw a single ring particle with 3D projection"""
        angle = p['base_angle'] + self.ring_angle * p['speed']
        
        # 3D to 2D projection with tilt
        radius = base_radius + p['radius'] - 100
        x = self.cx + radius * math.cos(angle)
        y = self.cy + radius * math.sin(angle) * tilt
        
        # Depth-based brightness
        depth_factor = 0.5 + 0.5 * math.sin(angle)
        brightness = depth_factor * (0.4 + 0.6 * ((math.sin(angle + self.time) + 1) / 2))
        
        color = self._lerp_color(Theme.BG_PRIMARY, colors[1], brightness)
        size = p['size'] * (0.8 + depth_factor * 0.4)
        
        self.create_oval(x - size, y - size, x + size, y + size,
                        fill=color, outline='')
    
    def _draw_core(self, colors):
        """Main orb core with gradient"""
        pulse = math.sin(self.time * 1.2) * 4 + self.audio_level * 12
        base_radius = 55 + pulse
        
        # Gradient layers
        layers = 15
        for i in range(layers, 0, -1):
            r = base_radius * i / layers
            t = (i / layers) ** 0.6
            color = self._lerp_color(Theme.BG_PRIMARY, colors[0], t * 0.9)
            self.create_oval(
                self.cx - r, self.cy - r,
                self.cx + r, self.cy + r,
                fill=color, outline=''
            )
        
        # Core outline
        self.create_oval(
            self.cx - base_radius, self.cy - base_radius,
            self.cx + base_radius, self.cy + base_radius,
            fill='', outline=colors[0], width=2
        )
    
    def _draw_inner_rings(self, colors):
        """Rotating segmented inner rings"""
        configs = [
            {'radius': 42, 'segments': 6, 'speed': 0.6, 'width': 2, 'gap': 0.3},
            {'radius': 32, 'segments': 8, 'speed': -0.9, 'width': 1.5, 'gap': 0.25},
            {'radius': 22, 'segments': 4, 'speed': 1.2, 'width': 2, 'gap': 0.4},
        ]
        
        for ring in configs:
            rotation = self.time * ring['speed']
            segment_angle = (2 * math.pi - ring['gap'] * ring['segments']) / ring['segments']
            
            for i in range(ring['segments']):
                start = rotation + i * (segment_angle + ring['gap'])
                points = []
                
                for j in range(21):
                    angle = start + segment_angle * j / 20
                    wobble = math.sin(self.time * 2 + angle) * 2 * self.audio_level
                    r = ring['radius'] + wobble
                    x = self.cx + r * math.cos(angle)
                    y = self.cy + r * math.sin(angle)
                    points.extend([x, y])
                
                if len(points) >= 4:
                    color = colors[0] if i % 2 == 0 else colors[1]
                    self.create_line(points, fill=color, width=ring['width'], smooth=True)
    
    def _draw_waves(self, colors):
        """Expanding ripple waves"""
        new_waves = []
        for wave in self.waves:
            wave['radius'] += 3
            wave['alpha'] -= 0.02
            
            if wave['alpha'] > 0:
                new_waves.append(wave)
                color = self._lerp_color(Theme.BG_PRIMARY, colors[0], wave['alpha'] * 0.6)
                self.create_oval(
                    self.cx - wave['radius'], self.cy - wave['radius'],
                    self.cx + wave['radius'], self.cy + wave['radius'],
                    fill='', outline=color, width=max(1, int(wave['width']))
                )
        
        self.waves = new_waves
        
        # Ambient ripples
        if random.random() < 0.008 + self.audio_level * 0.02:
            self.waves.append({'radius': 55, 'alpha': 0.3, 'width': 1.5})
    
    def _draw_center_point(self, colors):
        """Bright center core"""
        pulse = (math.sin(self.time * 2) + 1) / 2
        radius = 10 + pulse * 4 + self.audio_level * 6
        
        # Glow layers
        for i in range(4, 0, -1):
            r = radius + i * 3
            alpha = 0.25 * (5 - i) / 4
            color = self._lerp_color(Theme.BG_PRIMARY, colors[0], alpha)
            self.create_oval(self.cx - r, self.cy - r, self.cx + r, self.cy + r,
                           fill=color, outline='')
        
        # White center
        self.create_oval(
            self.cx - radius, self.cy - radius,
            self.cx + radius, self.cy + radius,
            fill=Theme.TEXT_PRIMARY, outline=''
        )
        
        # Colored inner
        inner = radius * 0.4
        self.create_oval(
            self.cx - inner, self.cy - inner,
            self.cx + inner, self.cy + inner,
            fill=colors[0], outline=''
        )
    
    def stop(self):
        self._animating = False


# ==================== STATUS DISPLAY ====================
class StatusDisplay(tk.Frame):
    """Tactical status display above orb"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=Theme.BG_PRIMARY, **kwargs)
        
        self.main_label = tk.Label(
            self,
            text="STANDING BY",
            font=Theme.FONT_STATUS,
            bg=Theme.BG_PRIMARY,
            fg=Theme.ACCENT_PRIMARY
        )
        self.main_label.pack()
        
        self.sub_label = tk.Label(
            self,
            text="System ready",
            font=Theme.FONT_STATUS_SUB,
            bg=Theme.BG_PRIMARY,
            fg=Theme.TEXT_MUTED
        )
        self.sub_label.pack(pady=(3, 0))
    
    def set_status(self, main_text, sub_text=""):
        self.main_label.config(text=main_text.upper())
        self.sub_label.config(text=sub_text)
        
        # Color based on state
        if "LISTENING" in main_text.upper():
            self.main_label.config(fg=Theme.ACTIVE)
        elif "ERROR" in main_text.upper():
            self.main_label.config(fg=Theme.ERROR)
        elif "PROCESSING" in main_text.upper() or "PLANNING" in main_text.upper():
            self.main_label.config(fg="#7C4DFF")
        else:
            self.main_label.config(fg=Theme.ACCENT_PRIMARY)


# ==================== ICON SIDEBAR ====================
class IconSidebar(tk.Frame):
    """Narrow icon-only sidebar with glassmorphism effect"""
    
    # Unicode icons (cross-platform)
    ICONS = {
        'browser': '🌐',
        'music': '♪',
        'screenshot': '📷',
        'status': '⚙',
        'minimize': '⏻',
    }
    
    LABELS = {
        'browser': 'Browser',
        'music': 'Music', 
        'screenshot': 'Screenshot',
        'status': 'Status',
        'minimize': 'Minimize',
    }
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=Theme.BG_GLASS, **kwargs)
        
        self.buttons = {}
        self.labels = {}
        self.active_id = None
        
        # Glass effect border
        self.config(highlightbackground=Theme.ACCENT_DIM, highlightthickness=1)
        
        # Spacer at top
        tk.Frame(self, bg=Theme.BG_GLASS, height=20).pack()
        
        for action_id in ['browser', 'music', 'screenshot', 'status', 'minimize']:
            self._create_icon_button(action_id)
        
        # Spacer at bottom
        tk.Frame(self, bg=Theme.BG_GLASS, height=20).pack(side="bottom")
    
    def _create_icon_button(self, action_id):
        """Create an icon button with hover label"""
        container = tk.Frame(self, bg=Theme.BG_GLASS)
        container.pack(fill="x", pady=3)
        
        # Accent strip (shown on hover/active)
        accent = tk.Frame(container, bg=Theme.BG_GLASS, width=3)
        accent.pack(side="left", fill="y")
        
        # Icon button
        btn = tk.Label(
            container,
            text=self.ICONS.get(action_id, '●'),
            font=("Segoe UI Emoji", 18),
            bg=Theme.BG_GLASS,
            fg=Theme.TEXT_SECONDARY,
            width=3,
            height=2,
            cursor="hand2"
        )
        btn.pack(side="left", padx=(5, 0))
        
        # Hover label
        label = tk.Label(
            container,
            text=self.LABELS.get(action_id, ''),
            font=Theme.FONT_ICON_LABEL,
            bg=Theme.BG_GLASS,
            fg=Theme.TEXT_MUTED
        )
        
        # Hover effects
        def on_enter(e, b=btn, l=label, a=accent):
            b.config(fg=Theme.ACCENT_PRIMARY, bg=Theme.BG_HOVER)
            a.config(bg=Theme.ACCENT_PRIMARY)
            l.pack(side="left", padx=(5, 10))
        
        def on_leave(e, b=btn, l=label, a=accent, aid=action_id):
            if aid != self.active_id:
                b.config(fg=Theme.TEXT_SECONDARY, bg=Theme.BG_GLASS)
                a.config(bg=Theme.BG_GLASS)
            l.pack_forget()
        
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
        container.bind("<Enter>", on_enter)
        container.bind("<Leave>", on_leave)
        
        self.buttons[action_id] = btn
        self.labels[action_id] = label
    
    def bind_action(self, action_id, callback):
        if action_id in self.buttons:
            self.buttons[action_id].bind("<Button-1>", lambda e: callback())


# ==================== TACTICAL LOG PANEL ====================
class TacticalLogPanel(tk.Frame):
    """Military-style log panel with structured formatting"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=Theme.BG_GLASS, **kwargs)
        
        # Glass effect
        self.config(highlightbackground=Theme.ACCENT_DIM, highlightthickness=1)
        
        # Header
        header = tk.Frame(self, bg=Theme.BG_TERTIARY)
        header.pack(fill="x")
        
        tk.Label(
            header,
            text="SYSTEM LOG",
            font=("Segoe UI Semibold", 9),
            bg=Theme.BG_TERTIARY,
            fg=Theme.TEXT_SECONDARY,
            padx=15,
            pady=8
        ).pack(side="left")
        
        # Scrollable log area
        self.log_frame = tk.Frame(self, bg=Theme.BG_PRIMARY)
        self.log_frame.pack(fill="both", expand=True, padx=1, pady=1)
        
        # Canvas for custom scrolling
        self.canvas = tk.Canvas(self.log_frame, bg=Theme.BG_PRIMARY, 
                               highlightthickness=0)
        
        # Custom thin scrollbar
        self.scrollbar = tk.Frame(self.log_frame, bg=Theme.BG_TERTIARY, width=4)
        self.scroll_thumb = tk.Frame(self.scrollbar, bg=Theme.ACCENT_TERTIARY, width=4)
        
        self.scrollbar.pack(side="right", fill="y", padx=(0, 2), pady=5)
        self.canvas.pack(side="left", fill="both", expand=True)
        
        # Inner frame for log entries
        self.inner_frame = tk.Frame(self.canvas, bg=Theme.BG_PRIMARY)
        self.canvas_window = self.canvas.create_window((0, 0), window=self.inner_frame, 
                                                        anchor="nw")
        
        # Configure scrolling
        self.inner_frame.bind("<Configure>", self._on_frame_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        
        self.log_entries = []
        self.max_entries = 50
    
    def _on_frame_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        self._update_scrollbar()
    
    def _on_canvas_configure(self, event):
        self.canvas.itemconfig(self.canvas_window, width=event.width)
    
    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        self._update_scrollbar()
    
    def _update_scrollbar(self):
        """Update custom scrollbar thumb position"""
        try:
            # Get scroll position
            first, last = self.canvas.yview()
            
            # Calculate thumb size and position
            scrollbar_height = self.scrollbar.winfo_height()
            thumb_height = max(20, (last - first) * scrollbar_height)
            thumb_y = first * scrollbar_height
            
            self.scroll_thumb.place(x=0, y=thumb_y, width=4, height=thumb_height)
        except:
            pass
    
    def log(self, message, tag="info"):
        """Add a structured log entry"""
        try:
            if not self.winfo_exists():
                return
        except:
            return
        
        # Create entry frame
        entry = tk.Frame(self.inner_frame, bg=Theme.BG_PRIMARY)
        entry.pack(fill="x", padx=10, pady=3, anchor="w")
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Determine style based on content
        time_color = Theme.TEXT_DIM
        msg_color = Theme.TEXT_SECONDARY
        prefix = ""
        prefix_color = Theme.ACCENT_PRIMARY
        
        if "[OK]" in message or "[FAST]" in message or "Done" in message:
            prefix = "[OK]"
            prefix_color = Theme.SUCCESS
            message = message.replace("[OK]", "").replace("[FAST]", "").strip()
        elif "[ERROR]" in message or "Error" in message:
            prefix = "[ERR]"
            prefix_color = Theme.ERROR
            msg_color = Theme.ERROR
        elif "Heard:" in message:
            prefix = "USR"
            prefix_color = Theme.WARNING
            msg_color = Theme.TEXT_PRIMARY
        elif "FOX-3:" in message:
            prefix = "FOX-3"
            prefix_color = Theme.ACCENT_PRIMARY
            message = message.replace("FOX-3:", "").strip()
        elif "LISTENING" in message or "listening" in message.lower():
            msg_color = Theme.ACTIVE
        
        # Timestamp
        tk.Label(
            entry,
            text=timestamp,
            font=Theme.FONT_LOG_TIME,
            bg=Theme.BG_PRIMARY,
            fg=time_color
        ).pack(side="left", padx=(0, 8))
        
        # Prefix badge if present
        if prefix:
            badge = tk.Label(
                entry,
                text=prefix,
                font=("Segoe UI Semibold", 8),
                bg=Theme.BG_PRIMARY,
                fg=prefix_color
            )
            badge.pack(side="left", padx=(0, 8))
        
        # Message
        tk.Label(
            entry,
            text=message[:80] + "..." if len(message) > 80 else message,
            font=Theme.FONT_LOG_TEXT,
            bg=Theme.BG_PRIMARY,
            fg=msg_color,
            anchor="w"
        ).pack(side="left", fill="x")
        
        self.log_entries.append(entry)
        
        # Limit entries
        while len(self.log_entries) > self.max_entries:
            old = self.log_entries.pop(0)
            old.destroy()
        
        # Auto-scroll to bottom
        self.canvas.update_idletasks()
        self.canvas.yview_moveto(1.0)
        self._update_scrollbar()
    
    def clear(self):
        for entry in self.log_entries:
            entry.destroy()
        self.log_entries = []


# ==================== SYSTEM STATS WIDGET ====================
class SystemStats(tk.Frame):
    """Small system stats display (CPU, RAM, etc.)"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=Theme.BG_PRIMARY, **kwargs)
        
        self.stats = {}
        
        for label in ['CPU', 'RAM', 'PING']:
            frame = tk.Frame(self, bg=Theme.BG_PRIMARY)
            frame.pack(side="left", padx=(0, 15))
            
            tk.Label(
                frame,
                text=label,
                font=Theme.FONT_STATS,
                bg=Theme.BG_PRIMARY,
                fg=Theme.TEXT_DIM
            ).pack(side="left")
            
            # Indicator bar
            bar_bg = tk.Frame(frame, bg=Theme.BG_TERTIARY, width=30, height=3)
            bar_bg.pack(side="left", padx=(5, 3))
            bar_bg.pack_propagate(False)
            
            bar_fill = tk.Frame(bar_bg, bg=Theme.ACCENT_TERTIARY, height=3)
            bar_fill.place(x=0, y=0, relwidth=0.5, height=3)
            
            value = tk.Label(
                frame,
                text="--",
                font=Theme.FONT_STATS,
                bg=Theme.BG_PRIMARY,
                fg=Theme.TEXT_MUTED,
                width=4
            )
            value.pack(side="left")
            
            self.stats[label] = {'bar': bar_fill, 'value': value}
        
        self._update_stats()
    
    def _update_stats(self):
        try:
            # CPU
            cpu = psutil.cpu_percent(interval=0)
            self.stats['CPU']['value'].config(text=f"{cpu:.0f}%")
            self.stats['CPU']['bar'].place(x=0, y=0, relwidth=cpu/100, height=3)
            
            # RAM
            ram = psutil.virtual_memory().percent
            self.stats['RAM']['value'].config(text=f"{ram:.0f}%")
            self.stats['RAM']['bar'].place(x=0, y=0, relwidth=ram/100, height=3)
            
            # Ping (placeholder)
            self.stats['PING']['value'].config(text="--")
            self.stats['PING']['bar'].place(x=0, y=0, relwidth=0.3, height=3)
        except:
            pass
        
        self.after(2000, self._update_stats)


# ==================== MAIN APPLICATION ====================
class SentinelXApp:
    """Tactical AI Interface - Military HUD Design"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("SENTINEL-X")
        self.root.configure(bg=Theme.BG_PRIMARY)
        
        # Fullscreen
        self.root.attributes('-fullscreen', True)
        self.root.bind('<Escape>', lambda e: self.root.destroy())
        self.root.bind('<F11>', lambda e: self._toggle_fullscreen())
        
        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()
        
        # Bot engine
        self.bot = NovaBotEngine()
        self.bot.log_callback = self._on_log
        self.bot.status_callback = self._on_status
        self.bot.audio_level_callback = self._on_audio_level
        
        # Build UI
        self._build_ui()
        
        # Welcome logs
        self.log_panel.log("SENTINEL-X tactical interface online", "system")
        self.log_panel.log("Voice recognition standby", "system")
    
    def _toggle_fullscreen(self):
        current = self.root.attributes('-fullscreen')
        self.root.attributes('-fullscreen', not current)
    
    def _build_ui(self):
        # Background layer
        self.bg = HUDBackground(self.root)
        self.bg.place(relx=0, rely=0, relwidth=1, relheight=1)
        
        # Main container
        main = tk.Frame(self.root, bg=Theme.BG_PRIMARY)
        main.place(relx=0, rely=0, relwidth=1, relheight=1)
        
        # Header
        self._build_header(main)
        
        # Content area
        content = tk.Frame(main, bg=Theme.BG_PRIMARY)
        content.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Left sidebar - narrow icon panel
        self.sidebar = IconSidebar(content, width=70)
        self.sidebar.pack(side="left", fill="y", padx=(0, 15))
        self._bind_actions()
        
        # Center - Orb and waveform
        center = tk.Frame(content, bg=Theme.BG_PRIMARY)
        center.pack(side="left", fill="both", expand=True)
        
        orb_container = tk.Frame(center, bg=Theme.BG_PRIMARY)
        orb_container.pack(expand=True)
        
        # Status above orb
        self.status_display = StatusDisplay(orb_container)
        self.status_display.pack(pady=(0, 20))
        
        # Orb
        orb_size = min(350, self.screen_height - 350)
        self.orb = LivingOrb(orb_container, size=orb_size)
        self.orb.pack()
        self.orb.on_click = self._toggle_bot
        
        # Waveform below orb
        self.waveform = WaveformVisualizer(orb_container, width=280, height=35)
        self.waveform.pack(pady=(25, 0))
        
        # Right panel - Log
        right_container = tk.Frame(content, bg=Theme.BG_PRIMARY, width=340)
        right_container.pack(side="right", fill="y", padx=(15, 0))
        right_container.pack_propagate(False)
        
        self.log_panel = TacticalLogPanel(right_container)
        self.log_panel.pack(fill="both", expand=True)
        
        # Bottom stats
        self._build_footer(main)
        
        # Keyboard
        self.root.bind('<space>', lambda e: self._toggle_bot())
    
    def _build_header(self, parent):
        header = tk.Frame(parent, bg=Theme.BG_PRIMARY)
        header.pack(fill="x", padx=25, pady=(15, 0))
        
        # Title
        title_frame = tk.Frame(header, bg=Theme.BG_PRIMARY)
        title_frame.pack(side="left")
        
        tk.Label(
            title_frame,
            text="SENTINEL",
            font=Theme.FONT_TITLE,
            bg=Theme.BG_PRIMARY,
            fg=Theme.TEXT_PRIMARY
        ).pack(side="left")
        
        tk.Label(
            title_frame,
            text="-X",
            font=Theme.FONT_TITLE_ACCENT,
            bg=Theme.BG_PRIMARY,
            fg=Theme.ACCENT_PRIMARY
        ).pack(side="left")
        
        tk.Label(
            title_frame,
            text="ADVANCED AI INTERFACE",
            font=Theme.FONT_SUBTITLE,
            bg=Theme.BG_PRIMARY,
            fg=Theme.TEXT_SECONDARY
        ).pack(side="left", padx=(20, 0), pady=(12, 0))
        
        # Clock
        time_frame = tk.Frame(header, bg=Theme.BG_PRIMARY)
        time_frame.pack(side="right")
        
        self.clock = tk.Label(
            time_frame,
            font=Theme.FONT_CLOCK,
            bg=Theme.BG_PRIMARY,
            fg=Theme.TEXT_SECONDARY
        )
        self.clock.pack(anchor="e")
        
        self.date = tk.Label(
            time_frame,
            font=Theme.FONT_DATE,
            bg=Theme.BG_PRIMARY,
            fg=Theme.TEXT_MUTED
        )
        self.date.pack(anchor="e")
        
        self._update_clock()
    
    def _build_footer(self, parent):
        footer = tk.Frame(parent, bg=Theme.BG_PRIMARY)
        footer.pack(side="bottom", fill="x", padx=25, pady=(0, 12))
        
        # System stats on right
        self.sys_stats = SystemStats(footer)
        self.sys_stats.pack(side="right")
    
    def _update_clock(self):
        now = datetime.now()
        self.clock.config(text=now.strftime("%H:%M"))
        self.date.config(text=now.strftime("%A, %B %d"))
        self.root.after(1000, self._update_clock)
    
    def _bind_actions(self):
        actions = {
            "browser": lambda: self.bot.execute_command("open google"),
            "music": lambda: self.bot.execute_command("play music"),
            "screenshot": lambda: self.bot.execute_command("take screenshot"),
            "status": lambda: self.bot.execute_command("system status"),
            "minimize": lambda: self.bot.execute_command("minimize all"),
        }
        for action_id, cb in actions.items():
            self.sidebar.bind_action(action_id, cb)
    
    def _toggle_bot(self):
        if self.bot.is_running():
            self.bot.stop()
            self.orb.set_state("idle")
            self.status_display.set_status("STANDING BY", "System ready")
            self.waveform.set_level(0)
        else:
            self.bot.start()
            self.orb.set_state("active")
            self.status_display.set_status("ONLINE", "Voice control active")
    
    def _on_log(self, message):
        self.log_panel.log(message)
        
        msg = message.lower()
        if "listening" in msg:
            self.orb.set_state("listening")
        elif "processing" in msg:
            self.orb.set_state("processing")
        elif "fox-3:" in msg:
            self.orb.set_state("speaking")
    
    def _on_audio_level(self, level):
        try:
            self.orb.set_voice_level(level)
            self.waveform.set_level(level)
        except:
            pass
    
    def _on_status(self, status):
        s = status.lower()
        
        if "listening" in s:
            self.orb.set_state("listening")
            self.status_display.set_status("LISTENING", "Speak your command")
        elif "processing" in s:
            self.orb.set_state("processing")
            self.status_display.set_status("PROCESSING", "Analyzing...")
        elif "executing" in s:
            self.orb.set_state("active")
            self.status_display.set_status("EXECUTING", "Running command")
        elif "planning" in s:
            self.orb.set_state("processing")
            self.status_display.set_status("PLANNING", "Preparing...")
        elif "ready" in s:
            self.orb.set_state("active")
            self.status_display.set_status("READY", "Awaiting command")
        elif "stopped" in s:
            self.orb.set_state("idle")
            self.status_display.set_status("STANDING BY", "System ready")
        elif "error" in s:
            self.orb.set_state("idle")
            self.status_display.set_status("ERROR", "Check log")
        elif "starting" in s:
            self.orb.set_state("active")
            self.status_display.set_status("INITIALIZING", "Starting...")
    
    def run(self):
        self.root.mainloop()
    
    def cleanup(self):
        self.bot.log_callback = lambda m: None
        self.bot.status_callback = lambda s: None
        self.bot.audio_level_callback = lambda l: None
        self.orb.stop()
        self.waveform.stop()
        self.bg.stop()
        if self.bot.is_running():
            self.bot.stop()


def main():
    app = SentinelXApp()
    try:
        app.run()
    finally:
        app.cleanup()


if __name__ == "__main__":
    main()
