"""
███████╗███████╗███╗   ██╗████████╗██╗███╗   ██╗███████╗██╗     
██╔════╝██╔════╝████╗  ██║╚══██╔══╝██║████╗  ██║██╔════╝██║     
███████╗█████╗  ██╔██╗ ██║   ██║   ██║██╔██╗ ██║█████╗  ██║     
╚════██║██╔══╝  ██║╚██╗██║   ██║   ██║██║╚██╗██║██╔══╝  ██║     
███████║███████╗██║ ╚████║   ██║   ██║██║ ╚████║███████╗███████╗
╚══════╝╚══════╝╚═╝  ╚═══╝   ╚═╝   ╚═╝╚═╝  ╚═══╝╚══════╝╚══════╝

SENTINEL-X // ADVANCED AI INTERFACE
Inspired by J.A.R.V.I.S - Living Orb Interface
"""

import tkinter as tk
from tkinter import ttk
import math
import random
from datetime import datetime

# Import the bot engine
from app.main import NovaBotEngine


# ==================== DESIGN SYSTEM ====================
class Theme:
    """Professional Dark Theme - JARVIS Inspired"""
    
    # Core Background
    BG_PRIMARY = "#05080f"        # Deep space black
    BG_SECONDARY = "#0c1018"      # Card background
    BG_TERTIARY = "#141c28"       # Elevated surfaces
    BG_HOVER = "#1a2535"          # Hover state
    
    # Accent Colors - Electric Blue Core
    ACCENT_PRIMARY = "#00d4ff"    # Bright cyan - main accent
    ACCENT_SECONDARY = "#0099cc"  # Medium cyan
    ACCENT_TERTIARY = "#006080"   # Muted cyan
    ACCENT_GLOW = "#00ffff"       # Glow effect
    
    # State Colors
    SUCCESS = "#00ff88"           # Bright green
    WARNING = "#ffaa00"           # Amber
    ERROR = "#ff3366"             # Red-pink
    
    # Text Hierarchy
    TEXT_PRIMARY = "#ffffff"      # Headers
    TEXT_SECONDARY = "#a8b4c4"    # Body text
    TEXT_MUTED = "#5a6878"        # Subtle text
    TEXT_ACCENT = "#00d4ff"       # Highlighted text
    
    # Orb Colors
    ORB_IDLE = ["#00b8d4", "#0088a8", "#005568"]
    ORB_ACTIVE = ["#00e676", "#00c853", "#009624"]
    ORB_LISTENING = ["#ffab00", "#ff8f00", "#ff6f00"]
    ORB_PROCESSING = ["#7c4dff", "#651fff", "#6200ea"]
    
    # Fonts - Clean Modern Stack
    FONT_DISPLAY = ("Segoe UI", 32, "bold")
    FONT_HEADER = ("Segoe UI Semibold", 14)
    FONT_BODY = ("Segoe UI", 11)
    FONT_SMALL = ("Segoe UI", 9)
    FONT_MONO = ("Consolas", 10)
    FONT_MONO_SMALL = ("Consolas", 9)
    FONT_STATUS = ("Segoe UI Light", 18)


# ==================== ANIMATED BACKGROUND ====================
class AnimatedBackground(tk.Canvas):
    """Subtle animated grid background"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=Theme.BG_PRIMARY, highlightthickness=0, **kwargs)
        self.time = 0
        self.grid_lines = []
        self._animating = True
        self._animate()
    
    def _animate(self):
        if not self._animating:
            return
        
        self.delete("grid")
        self.time += 0.02
        
        w = self.winfo_width()
        h = self.winfo_height()
        
        if w > 1 and h > 1:
            # Horizontal grid lines
            spacing = 60
            for i in range(0, h + spacing, spacing):
                y = i
                alpha = 0.1 + 0.05 * math.sin(self.time + i * 0.01)
                color = self._alpha_color(Theme.ACCENT_TERTIARY, alpha)
                self.create_line(0, y, w, y, fill=color, tags="grid")
            
            # Vertical grid lines
            for i in range(0, w + spacing, spacing):
                x = i
                alpha = 0.1 + 0.05 * math.sin(self.time + i * 0.01)
                color = self._alpha_color(Theme.ACCENT_TERTIARY, alpha)
                self.create_line(x, 0, x, h, fill=color, tags="grid")
        
        self.after(50, self._animate)
    
    def _alpha_color(self, hex_color, alpha):
        """Simulate alpha by darkening color"""
        hex_color = hex_color.lstrip('#')
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        r = int(r * alpha)
        g = int(g * alpha)
        b = int(b * alpha)
        return f'#{r:02x}{g:02x}{b:02x}'
    
    def stop(self):
        self._animating = False


# ==================== LIVING ORB - JARVIS CORE ====================
class LivingOrb(tk.Canvas):
    """
    Dynamic JARVIS-style orb that responds to system state.
    Features: Pulsing core, orbiting particles, reactive waves, glow effects
    """
    
    def __init__(self, parent, size=400, **kwargs):
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
        self.init_particles(60)
        
        # Ring particles
        self.ring_particles = []
        self.init_ring_particles(80)
        
        # Wave system
        self.waves = []
        
        # Audio reactive simulation
        self.audio_level = 0
        self.target_audio = 0.1
        
        # Click handling
        self.on_click = None
        self.bind("<Button-1>", self._handle_click)
        self.bind("<Enter>", lambda e: self.config(cursor="hand2"))
        self.bind("<Leave>", lambda e: self.config(cursor=""))
        
        self._animate()
    
    def init_particles(self, count):
        """Initialize orbiting particles"""
        self.particles = []
        for i in range(count):
            particle = {
                'angle': random.uniform(0, 2 * math.pi),
                'radius': random.uniform(70, 160),
                'speed': random.uniform(0.003, 0.015),
                'size': random.uniform(1.5, 4),
                'offset': random.uniform(0, 2 * math.pi),
                'layer': random.randint(0, 2),
                'brightness': random.uniform(0.4, 1.0)
            }
            self.particles.append(particle)
    
    def init_ring_particles(self, count):
        """Initialize ring particles"""
        self.ring_particles = []
        for i in range(count):
            angle = (2 * math.pi * i) / count
            particle = {
                'base_angle': angle,
                'radius': random.uniform(85, 95),
                'size': random.uniform(1, 2),
                'speed': random.uniform(0.5, 1.5)
            }
            self.ring_particles.append(particle)
    
    def _handle_click(self, event):
        """Handle click on orb"""
        dx = event.x - self.cx
        dy = event.y - self.cy
        dist = math.sqrt(dx*dx + dy*dy)
        
        if dist < 120:
            if self.on_click:
                self.on_click()
            for _ in range(3):
                self.waves.append({'radius': 60, 'alpha': 1.0, 'width': 3})
    
    def set_state(self, state):
        """Update orb visual state"""
        self.state = state
        if state == "listening":
            self.target_audio = 0.6
        elif state == "processing":
            self.target_audio = 0.4
        elif state == "speaking":
            self.target_audio = 0.8
        elif state == "active":
            self.target_audio = 0.3
        else:
            self.target_audio = 0.15
    
    def _get_colors(self):
        """Get current color scheme based on state"""
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
        
        # Smooth audio level transition
        self.audio_level += (self.target_audio - self.audio_level) * 0.08
        
        colors = self._get_colors()
        
        # Layer 1: Outer glow
        self._draw_outer_glow(colors)
        
        # Layer 2: Orbiting particles
        self._draw_particles(colors)
        
        # Layer 3: Ring particles
        self._draw_ring_particles(colors)
        
        # Layer 4: Main rings
        self._draw_main_rings(colors)
        
        # Layer 5: Core
        self._draw_core(colors)
        
        # Layer 6: Inner detail rings
        self._draw_inner_rings(colors)
        
        # Layer 7: Waves
        self._draw_waves(colors)
        
        # Layer 8: Center bright spot
        self._draw_center(colors)
        
        self.after(16, self._animate)
    
    def _draw_outer_glow(self, colors):
        """Draw soft outer glow"""
        pulse = (math.sin(self.time * 1.5) + 1) / 2
        
        for i in range(5, 0, -1):
            radius = 140 + i * 15 + pulse * 10 + self.audio_level * 25
            alpha = 0.08 * (6 - i) / 5
            color = self._lerp_color(Theme.BG_PRIMARY, colors[0], alpha)
            
            self.create_oval(
                self.cx - radius, self.cy - radius,
                self.cx + radius, self.cy + radius,
                fill=color, outline=''
            )
    
    def _draw_particles(self, colors):
        """Draw orbiting particles"""
        for p in self.particles:
            p['angle'] += p['speed'] * (1 + self.audio_level * 2)
            
            wobble = math.sin(self.time * 2 + p['offset']) * 15
            radius = p['radius'] + wobble + self.audio_level * 40
            
            x = self.cx + radius * math.cos(p['angle'])
            y = self.cy + radius * math.sin(p['angle'])
            
            pulse = (math.sin(self.time * 3 + p['offset']) + 1) / 2
            size = p['size'] * (0.8 + 0.4 * pulse)
            
            # Color with brightness variation
            base_color = colors[p['layer']]
            color = self._lerp_color(Theme.BG_PRIMARY, base_color, p['brightness'] * (0.6 + 0.4 * pulse))
            
            # Glow
            self.create_oval(x - size*2, y - size*2, x + size*2, y + size*2,
                           fill=color, outline='')
            # Core
            self.create_oval(x - size, y - size, x + size, y + size,
                           fill=colors[0], outline='')
    
    def _draw_ring_particles(self, colors):
        """Draw particles along the main ring"""
        base_radius = 90 + self.audio_level * 20
        
        for p in self.ring_particles:
            angle = p['base_angle'] + self.time * p['speed'] * 0.3
            wobble = math.sin(self.time * 4 + p['base_angle'] * 5) * 5
            radius = base_radius + wobble
            
            x = self.cx + radius * math.cos(angle)
            y = self.cy + radius * math.sin(angle)
            
            brightness = 0.4 + 0.6 * ((math.sin(angle * 3 + self.time * 2) + 1) / 2)
            color = self._lerp_color(Theme.BG_PRIMARY, colors[0], brightness)
            
            size = p['size'] * (1 + self.audio_level)
            self.create_oval(x - size, y - size, x + size, y + size,
                           fill=color, outline='')
    
    def _draw_main_rings(self, colors):
        """Draw the main orbital rings"""
        base_radius = 90 + self.audio_level * 20
        
        # Main ring
        self.create_oval(
            self.cx - base_radius, self.cy - base_radius,
            self.cx + base_radius, self.cy + base_radius,
            fill='', outline=colors[1], width=2
        )
        
        # Secondary rings
        for offset in [-12, 12]:
            r = base_radius + offset
            alpha = 0.5
            color = self._lerp_color(Theme.BG_PRIMARY, colors[2], alpha)
            self.create_oval(
                self.cx - r, self.cy - r,
                self.cx + r, self.cy + r,
                fill='', outline=color, width=1
            )
    
    def _draw_core(self, colors):
        """Draw the main orb core"""
        pulse = math.sin(self.time * 1.5) * 5 + self.audio_level * 15
        base_radius = 65 + pulse
        
        # Gradient layers
        layers = 12
        for i in range(layers, 0, -1):
            r = base_radius * i / layers
            t = (i / layers) ** 0.7
            color = self._lerp_color(Theme.BG_PRIMARY, colors[0], t * 0.85)
            
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
        """Draw rotating inner rings"""
        ring_configs = [
            {'radius': 50, 'segments': 6, 'speed': 0.8, 'width': 2, 'gap': 0.25},
            {'radius': 38, 'segments': 8, 'speed': -1.2, 'width': 1.5, 'gap': 0.2},
            {'radius': 26, 'segments': 4, 'speed': 1.5, 'width': 2, 'gap': 0.3},
        ]
        
        for idx, ring in enumerate(ring_configs):
            rotation = self.time * ring['speed']
            segment_angle = (2 * math.pi - ring['gap'] * ring['segments']) / ring['segments']
            
            for i in range(ring['segments']):
                start = rotation + i * (segment_angle + ring['gap'])
                
                points = []
                steps = 20
                for j in range(steps + 1):
                    angle = start + segment_angle * j / steps
                    # Add wobble
                    wobble = math.sin(self.time * 3 + angle * 2) * 2 * self.audio_level
                    r = ring['radius'] + wobble
                    x = self.cx + r * math.cos(angle)
                    y = self.cy + r * math.sin(angle)
                    points.extend([x, y])
                
                if len(points) >= 4:
                    color = colors[0] if i % 2 == 0 else colors[1]
                    self.create_line(points, fill=color, width=ring['width'], smooth=True)
    
    def _draw_waves(self, colors):
        """Draw expanding wave ripples"""
        new_waves = []
        for wave in self.waves:
            wave['radius'] += 4
            wave['alpha'] -= 0.025
            wave['width'] = max(1, wave['width'] - 0.05)
            
            if wave['alpha'] > 0:
                new_waves.append(wave)
                color = self._lerp_color(Theme.BG_PRIMARY, colors[0], wave['alpha'] * 0.8)
                
                self.create_oval(
                    self.cx - wave['radius'], self.cy - wave['radius'],
                    self.cx + wave['radius'], self.cy + wave['radius'],
                    fill='', outline=color, width=int(wave['width'])
                )
        
        self.waves = new_waves
        
        # Ambient waves
        if random.random() < 0.01 + self.audio_level * 0.02:
            self.waves.append({'radius': 65, 'alpha': 0.4, 'width': 2})
    
    def _draw_center(self, colors):
        """Draw bright center point"""
        pulse = (math.sin(self.time * 2.5) + 1) / 2
        radius = 12 + pulse * 5 + self.audio_level * 8
        
        # Outer glow
        for i in range(3, 0, -1):
            r = radius + i * 4
            alpha = 0.3 * (4 - i) / 3
            color = self._lerp_color(Theme.BG_PRIMARY, colors[0], alpha)
            self.create_oval(
                self.cx - r, self.cy - r,
                self.cx + r, self.cy + r,
                fill=color, outline=''
            )
        
        # Bright center
        self.create_oval(
            self.cx - radius, self.cy - radius,
            self.cx + radius, self.cy + radius,
            fill=Theme.TEXT_PRIMARY, outline=''
        )
        
        # Inner color
        inner_r = radius * 0.5
        self.create_oval(
            self.cx - inner_r, self.cy - inner_r,
            self.cx + inner_r, self.cy + inner_r,
            fill=colors[0], outline=''
        )
    
    def stop(self):
        self._animating = False


# ==================== STATUS DISPLAY ====================
class StatusDisplay(tk.Frame):
    """Clean status display with animation"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=Theme.BG_PRIMARY, **kwargs)
        
        self.main_label = tk.Label(
            self,
            text="SENTINEL-X",
            font=Theme.FONT_STATUS,
            bg=Theme.BG_PRIMARY,
            fg=Theme.ACCENT_PRIMARY
        )
        self.main_label.pack()
        
        self.sub_label = tk.Label(
            self,
            text="System Online",
            font=Theme.FONT_SMALL,
            bg=Theme.BG_PRIMARY,
            fg=Theme.TEXT_MUTED
        )
        self.sub_label.pack(pady=(5, 0))
    
    def set_status(self, main_text, sub_text=""):
        """Update status text"""
        self.main_label.config(text=main_text.upper())
        self.sub_label.config(text=sub_text)


# ==================== LOG PANEL ====================
class LogPanel(tk.Frame):
    """Professional log output panel"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=Theme.BG_SECONDARY, **kwargs)
        
        # Header
        header = tk.Frame(self, bg=Theme.BG_TERTIARY)
        header.pack(fill="x")
        
        tk.Label(
            header,
            text="SYSTEM LOG",
            font=Theme.FONT_SMALL,
            bg=Theme.BG_TERTIARY,
            fg=Theme.TEXT_MUTED,
            padx=15,
            pady=10
        ).pack(side="left")
        
        self.time_label = tk.Label(
            header,
            font=Theme.FONT_MONO_SMALL,
            bg=Theme.BG_TERTIARY,
            fg=Theme.TEXT_MUTED,
            padx=15
        )
        self.time_label.pack(side="right")
        self._update_time()
        
        # Text area
        text_frame = tk.Frame(self, bg=Theme.BG_SECONDARY)
        text_frame.pack(fill="both", expand=True, padx=2, pady=2)
        
        self.text = tk.Text(
            text_frame,
            font=Theme.FONT_MONO,
            bg=Theme.BG_PRIMARY,
            fg=Theme.TEXT_SECONDARY,
            insertbackground=Theme.ACCENT_PRIMARY,
            selectbackground=Theme.ACCENT_TERTIARY,
            relief="flat",
            padx=15,
            pady=12,
            wrap="word",
            state="disabled",
            cursor="arrow",
            borderwidth=0
        )
        
        scrollbar = ttk.Scrollbar(text_frame, command=self.text.yview)
        self.text.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side="right", fill="y")
        self.text.pack(side="left", fill="both", expand=True)
        
        # Tags
        self.text.tag_configure("system", foreground=Theme.TEXT_MUTED)
        self.text.tag_configure("info", foreground=Theme.TEXT_SECONDARY)
        self.text.tag_configure("success", foreground=Theme.SUCCESS)
        self.text.tag_configure("warning", foreground=Theme.WARNING)
        self.text.tag_configure("error", foreground=Theme.ERROR)
        self.text.tag_configure("accent", foreground=Theme.ACCENT_PRIMARY)
    
    def _update_time(self):
        self.time_label.config(text=datetime.now().strftime("%H:%M:%S"))
        self.after(1000, self._update_time)
    
    def log(self, message, tag="info"):
        # Safety check - don't log if widget destroyed
        try:
            if not self.winfo_exists():
                return
        except:
            return
        self.text.configure(state="normal")
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        if "[FAST]" in message or "[OK]" in message or "Done" in message:
            tag = "success"
        elif "[LLM]" in message or "[WARN]" in message or "WARN" in message:
            tag = "warning"
        elif "[ERROR]" in message or "Error" in message:
            tag = "error"
        elif "Heard:" in message:
            tag = "warning"
        elif "FOX-3:" in message or "SENTINEL:" in message:
            tag = "accent"
        
        self.text.insert("end", f"[{timestamp}] {message}\n", tag)
        self.text.see("end")
        self.text.configure(state="disabled")
    
    def clear(self):
        self.text.configure(state="normal")
        self.text.delete("1.0", "end")
        self.text.configure(state="disabled")


# ==================== QUICK ACTIONS ====================
class QuickActions(tk.Frame):
    """Quick action buttons"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=Theme.BG_SECONDARY, **kwargs)
        
        # Header
        header = tk.Frame(self, bg=Theme.BG_TERTIARY)
        header.pack(fill="x")
        
        tk.Label(
            header,
            text="QUICK ACTIONS",
            font=Theme.FONT_SMALL,
            bg=Theme.BG_TERTIARY,
            fg=Theme.TEXT_MUTED,
            padx=15,
            pady=10
        ).pack(side="left")
        
        # Buttons container
        self.btn_frame = tk.Frame(self, bg=Theme.BG_SECONDARY)
        self.btn_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.buttons = {}
        
        actions = [
            ("BROWSER", "browser", "Open Google"),
            ("MUSIC", "music", "Play music"),
            ("SCREENSHOT", "screenshot", "Capture screen"),
            ("STATUS", "status", "System check"),
            ("MINIMIZE", "minimize", "Show desktop"),
        ]
        
        for label, action_id, tooltip in actions:
            btn = self._create_button(label, tooltip)
            btn.pack(fill="x", pady=4)
            self.buttons[action_id] = btn
    
    def _create_button(self, text, tooltip):
        btn = tk.Label(
            self.btn_frame,
            text=text,
            font=Theme.FONT_SMALL,
            bg=Theme.BG_TERTIARY,
            fg=Theme.TEXT_SECONDARY,
            padx=20,
            pady=12,
            cursor="hand2"
        )
        
        btn.bind("<Enter>", lambda e, b=btn: b.configure(bg=Theme.BG_HOVER, fg=Theme.TEXT_PRIMARY))
        btn.bind("<Leave>", lambda e, b=btn: b.configure(bg=Theme.BG_TERTIARY, fg=Theme.TEXT_SECONDARY))
        
        return btn
    
    def bind_action(self, action_id, callback):
        if action_id in self.buttons:
            self.buttons[action_id].bind("<Button-1>", lambda e: callback())


# ==================== MAIN APPLICATION ====================
class SentinelXApp:
    """Main application - Full screen JARVIS interface"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("SENTINEL-X")
        self.root.configure(bg=Theme.BG_PRIMARY)
        
        # Full screen
        self.root.attributes('-fullscreen', True)
        self.root.bind('<Escape>', lambda e: self.root.destroy())
        self.root.bind('<F11>', lambda e: self._toggle_fullscreen())
        
        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()
        
        # Styles
        self._configure_styles()
        
        # Bot engine
        self.bot = NovaBotEngine()
        self.bot.log_callback = self._on_log
        self.bot.status_callback = self._on_status
        
        # Build UI
        self._build_ui()
        
        # Welcome
        self.log_panel.log("SENTINEL-X initialized", "system")
        self.log_panel.log("Lightning TTS engine ready", "system")
        self.log_panel.log("Click the orb to activate voice control", "info")
    
    def _toggle_fullscreen(self):
        current = self.root.attributes('-fullscreen')
        self.root.attributes('-fullscreen', not current)
    
    def _configure_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure(
            "Vertical.TScrollbar",
            background=Theme.BG_TERTIARY,
            troughcolor=Theme.BG_PRIMARY,
            bordercolor=Theme.BG_PRIMARY,
            arrowcolor=Theme.TEXT_MUTED
        )
    
    def _build_ui(self):
        # Main container
        main = tk.Frame(self.root, bg=Theme.BG_PRIMARY)
        main.pack(fill="both", expand=True)
        
        # Header
        self._build_header(main)
        
        # Content
        content = tk.Frame(main, bg=Theme.BG_PRIMARY)
        content.pack(fill="both", expand=True, padx=30, pady=20)
        
        # Left panel
        left = tk.Frame(content, bg=Theme.BG_SECONDARY, width=220)
        left.pack(side="left", fill="y", padx=(0, 20))
        left.pack_propagate(False)
        
        self.quick_actions = QuickActions(left)
        self.quick_actions.pack(fill="both", expand=True)
        self._bind_actions()
        
        # Center - Orb
        center = tk.Frame(content, bg=Theme.BG_PRIMARY)
        center.pack(side="left", fill="both", expand=True)
        
        orb_frame = tk.Frame(center, bg=Theme.BG_PRIMARY)
        orb_frame.pack(expand=True)
        
        self.status_display = StatusDisplay(orb_frame)
        self.status_display.pack(pady=(0, 30))
        
        orb_size = min(420, self.screen_height - 300)
        self.orb = LivingOrb(orb_frame, size=orb_size)
        self.orb.pack()
        self.orb.on_click = self._toggle_bot
        
        # Instructions
        tk.Label(
            orb_frame,
            text="CLICK ORB TO ACTIVATE  /  SPACE  /  ESC TO EXIT",
            font=Theme.FONT_SMALL,
            bg=Theme.BG_PRIMARY,
            fg=Theme.TEXT_MUTED
        ).pack(pady=(30, 0))
        
        # Right panel - Log
        right = tk.Frame(content, bg=Theme.BG_SECONDARY, width=380)
        right.pack(side="right", fill="y", padx=(20, 0))
        right.pack_propagate(False)
        
        self.log_panel = LogPanel(right)
        self.log_panel.pack(fill="both", expand=True)
        
        # Keyboard
        self.root.bind('<space>', lambda e: self._toggle_bot())
    
    def _build_header(self, parent):
        header = tk.Frame(parent, bg=Theme.BG_PRIMARY)
        header.pack(fill="x", padx=30, pady=(20, 0))
        
        # Title
        title_frame = tk.Frame(header, bg=Theme.BG_PRIMARY)
        title_frame.pack(side="left")
        
        tk.Label(
            title_frame,
            text="SENTINEL",
            font=Theme.FONT_DISPLAY,
            bg=Theme.BG_PRIMARY,
            fg=Theme.TEXT_PRIMARY
        ).pack(side="left")
        
        tk.Label(
            title_frame,
            text="-X",
            font=Theme.FONT_DISPLAY,
            bg=Theme.BG_PRIMARY,
            fg=Theme.ACCENT_PRIMARY
        ).pack(side="left")
        
        tk.Label(
            title_frame,
            text="ADVANCED AI INTERFACE",
            font=Theme.FONT_BODY,
            bg=Theme.BG_PRIMARY,
            fg=Theme.TEXT_MUTED
        ).pack(side="left", padx=(25, 0), pady=(15, 0))
        
        # Clock
        time_frame = tk.Frame(header, bg=Theme.BG_PRIMARY)
        time_frame.pack(side="right")
        
        self.clock = tk.Label(
            time_frame,
            font=("Segoe UI Light", 28),
            bg=Theme.BG_PRIMARY,
            fg=Theme.TEXT_SECONDARY
        )
        self.clock.pack()
        
        self.date = tk.Label(
            time_frame,
            font=Theme.FONT_SMALL,
            bg=Theme.BG_PRIMARY,
            fg=Theme.TEXT_MUTED
        )
        self.date.pack()
        
        self._update_clock()
        
        # Separator
        sep = tk.Frame(parent, bg=Theme.ACCENT_TERTIARY, height=1)
        sep.pack(fill="x", padx=30, pady=(15, 0))
    
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
            self.quick_actions.bind_action(action_id, cb)
    
    def _toggle_bot(self):
        if self.bot.is_running():
            self.bot.stop()
            self.orb.set_state("idle")
            self.status_display.set_status("STANDING BY", "Click orb to activate")
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
            self.status_display.set_status("STANDING BY", "Click orb to activate")
        elif "error" in s:
            self.orb.set_state("idle")
            self.status_display.set_status("ERROR", "Check log")
        elif "starting" in s:
            self.orb.set_state("active")
            self.status_display.set_status("INITIALIZING", "Starting...")
    
    def run(self):
        self.root.mainloop()
    
    def cleanup(self):
        # Disable logging before cleanup to prevent Tkinter errors
        self.bot.log_callback = lambda m: None
        self.bot.status_callback = lambda s: None
        self.orb.stop()
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
