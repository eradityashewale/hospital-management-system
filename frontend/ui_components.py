"""
MediFlow - Modern Reusable UI Components
Glassmorphism cards, sidebar navigation, pill buttons, animated elements
"""
import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional, Tuple
from frontend.theme import (
    BG_BASE, BG_CARD, BG_ELEVATED, ACCENT_BLUE, ACCENT_TEAL, ACCENT_PURPLE,
    ACCENT_PINK, ACCENT_GREEN, GRADIENT_BLUE, GRADIENT_PURPLE, GRADIENT_TEAL,
    GRADIENT_PINK, GRADIENT_GREEN, GRADIENT_ORANGE, GRADIENT_RED,
    TEXT_PRIMARY, TEXT_SECONDARY, SIDEBAR_ACTIVE, SIDEBAR_HOVER, SIDEBAR_BG,
    SIDEBAR_TEXT, SIDEBAR_TEXT_ACTIVE, FILTER_ACTIVE, FILTER_INACTIVE,
    FILTER_INACTIVE_TEXT, RADIUS_CARD, RADIUS_LG, RADIUS_MD,
    FONT_FAMILY, FONT_UI, FONT_SIZE_SM, FONT_SIZE_BASE, FONT_SIZE_LG,
    FONT_SIZE_2XL, FONT_SIZE_3XL, BTN_PRIMARY_BG, BTN_PRIMARY_HOVER,
    SIDEBAR_WIDTH, SIDEBAR_ACTIVE_GLOW,
)


def _create_rounded_rect(canvas: tk.Canvas, x1: int, y1: int, x2: int, y2: int, 
                        r: int, fill: str, outline: str = "", width: int = 0) -> list:
    """Draw rounded rectangle on canvas. Returns list of created item ids."""
    r = min(r, (x2 - x1) // 2, (y2 - y1) // 2)
    items = []
    # Corners
    items.append(canvas.create_arc(x1, y1, x1 + 2*r, y1 + 2*r, start=90, extent=90, fill=fill, outline=outline, width=width))
    items.append(canvas.create_arc(x2 - 2*r, y1, x2, y1 + 2*r, start=0, extent=90, fill=fill, outline=outline, width=width))
    items.append(canvas.create_arc(x1, y2 - 2*r, x1 + 2*r, y2, start=180, extent=90, fill=fill, outline=outline, width=width))
    items.append(canvas.create_arc(x2 - 2*r, y2 - 2*r, x2, y2, start=270, extent=90, fill=fill, outline=outline, width=width))
    # Rectangles
    items.append(canvas.create_rectangle(x1 + r, y1, x2 - r, y2, fill=fill, outline=outline, width=width))
    items.append(canvas.create_rectangle(x1, y1 + r, x2, y2 - r, fill=fill, outline=outline, width=width))
    return items


class ModernCard(tk.Frame):
    """Glass-effect dashboard card with gradient accent and hover animation."""
    
    CARD_COLORS = [
        ("#3b82f6", "#4f8ff7"),   # Blue + hover
        ("#8b5cf6", "#9d6ef7"),   # Purple
        ("#ec4899", "#ef6ba8"),   # Pink
        ("#f59e0b", "#f7b02e"),   # Orange
        ("#ef4444", "#f15959"),   # Red
        ("#06b6d4", "#22c4dc"),   # Teal
        ("#10b981", "#34d399"),   # Green
    ]
    
    def __init__(self, parent, icon: str, label: str, value: str, trend: str = "",
                 color_index: int = 0, **kwargs):
        super().__init__(parent, **kwargs)
        self.configure(bg=BG_BASE, highlightthickness=0)
        self.color_index = color_index
        self.card_color, self.card_color_hover = self.CARD_COLORS[color_index % len(self.CARD_COLORS)]
        
        # Card container - elevated with subtle border for glass feel
        content = tk.Frame(self, bg=self.card_color, highlightbackground=self.card_color,
                          highlightthickness=1, highlightcolor=self.card_color)
        content.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        # Top: Icon + Label
        top_frame = tk.Frame(content, bg=self.card_color)
        top_frame.pack(fill=tk.X, padx=20, pady=(20, 8))
        
        icon_lbl = tk.Label(top_frame, text=icon, font=(FONT_UI, 22), 
                           bg=self.card_color, fg='white')
        icon_lbl.pack(side=tk.LEFT, padx=(0, 12))
        
        label_frame = tk.Frame(top_frame, bg=self.card_color)
        label_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        tk.Label(label_frame, text=label, font=(FONT_UI, FONT_SIZE_SM, 'bold'),
                bg=self.card_color, fg='white').pack(anchor='w')
        if trend:
            tk.Label(label_frame, text=f"↑ {trend}", font=(FONT_UI, 9),
                    bg=self.card_color, fg='white').pack(anchor='w')
        
        # Value - large number
        self.value_label = tk.Label(content, text=str(value), font=(FONT_UI, FONT_SIZE_3XL, 'bold'),
                                   bg=self.card_color, fg='white')
        self.value_label.pack(pady=(0, 20))
        
        # Hover: slight brighten
        def on_enter(e):
            content.config(bg=self.card_color_hover)
            for w in content.winfo_children():
                w.config(bg=self.card_color_hover)
                for c in w.winfo_children():
                    c.config(bg=self.card_color_hover)
        
        def on_leave(e):
            content.config(bg=self.card_color)
            for w in content.winfo_children():
                w.config(bg=self.card_color)
                for c in w.winfo_children():
                    c.config(bg=self.card_color)
        
        for w in [content, top_frame, icon_lbl, label_frame, self.value_label]:
            w.bind('<Enter>', on_enter)
            w.bind('<Leave>', on_leave)
            if hasattr(w, 'winfo_children'):
                for c in w.winfo_children():
                    c.bind('<Enter>', on_enter)
                    c.bind('<Leave>', on_leave)
        
        self.content_frame = content
    
    def set_value(self, value: str):
        self.value_label.config(text=str(value))


class ModernSidebar(tk.Frame):
    """Vertical sidebar with icon+text items, active indicator, collapsible."""
    
    def __init__(self, parent, width: int = SIDEBAR_WIDTH, on_nav: Optional[Callable] = None, **kwargs):
        super().__init__(parent, width=width, **kwargs)
        self.configure(bg=SIDEBAR_BG, highlightthickness=0)
        self.pack_propagate(False)
        self.on_nav = on_nav
        self.buttons: list[Tuple[str, tk.Frame, Callable]] = []
        self.active_key: Optional[str] = None
        self._collapsed = False
        self._width_expanded = width
    
    def add_item(self, key: str, icon: str, label: str, command: Callable):
        frame = tk.Frame(self, bg=SIDEBAR_BG, cursor='hand2', height=48)
        frame.pack_propagate(False)
        frame.pack(fill=tk.X, padx=8, pady=2)
        
        # Inner clickable area
        inner = tk.Frame(frame, bg=SIDEBAR_BG, cursor='hand2')
        inner.pack(fill=tk.BOTH, expand=True)
        
        icon_lbl = tk.Label(inner, text=icon, font=(FONT_UI, 14), bg=SIDEBAR_BG, fg=SIDEBAR_TEXT)
        icon_lbl.pack(side=tk.LEFT, padx=(16, 12), pady=12)
        
        text_lbl = tk.Label(inner, text=label, font=(FONT_UI, FONT_SIZE_BASE, 'bold'),
                           bg=SIDEBAR_BG, fg=SIDEBAR_TEXT)
        text_lbl.pack(side=tk.LEFT, fill=tk.X, expand=True, anchor='w')
        
        def on_click(e=None):
            self.set_active(key)
            command()
        
        for w in [frame, inner, icon_lbl, text_lbl]:
            w.bind('<Button-1>', on_click)
            w.bind('<Enter>', lambda e, f=frame, i=inner, ic=icon_lbl, t=text_lbl: self._hover(f, i, ic, t, True))
            w.bind('<Leave>', lambda e, f=frame, i=inner, ic=icon_lbl, t=text_lbl: self._hover(f, i, ic, t, False))
        
        self.buttons.append((key, frame, command))
    
    def _hover(self, frame, inner, icon_lbl, text_lbl, enter: bool):
        if self.active_key and frame in [b[1] for b in self.buttons if b[0] == self.active_key]:
            return
        bg = SIDEBAR_HOVER if enter else SIDEBAR_BG
        for w in [frame, inner, icon_lbl, text_lbl]:
            w.config(bg=bg)
    
    def set_active(self, key: str):
        self.active_key = key
        for k, frame, _ in self.buttons:
            inner = frame.winfo_children()[0]
            icon_lbl = inner.winfo_children()[0]
            text_lbl = inner.winfo_children()[1]
            if k == key:
                frame.config(bg=SIDEBAR_ACTIVE)
                inner.config(bg=SIDEBAR_ACTIVE)
                icon_lbl.config(bg=SIDEBAR_ACTIVE, fg=SIDEBAR_TEXT_ACTIVE)
                text_lbl.config(bg=SIDEBAR_ACTIVE, fg=SIDEBAR_TEXT_ACTIVE)
            else:
                frame.config(bg=SIDEBAR_BG)
                inner.config(bg=SIDEBAR_BG)
                icon_lbl.config(bg=SIDEBAR_BG, fg=SIDEBAR_TEXT)
                text_lbl.config(bg=SIDEBAR_BG, fg=SIDEBAR_TEXT)


class ModernPillButton(tk.Button):
    """Pill-shaped button with gradient feel and hover glow."""
    
    def __init__(self, parent, text: str, command: Optional[Callable] = None, 
                 active: bool = False, **kwargs):
        super().__init__(parent, text=text, command=command, **kwargs)
        self._active = active
        self.configure(
            font=(FONT_UI, FONT_SIZE_SM, 'bold'),
            bg=FILTER_ACTIVE if active else FILTER_INACTIVE,
            fg='white' if active else FILTER_INACTIVE_TEXT,
            activebackground=FILTER_ACTIVE if active else '#2d3748',
            activeforeground='white',
            relief=tk.FLAT,
            bd=0,
            padx=20,
            pady=8,
            cursor='hand2',
            highlightthickness=0,
        )
        self.bind('<Enter>', self._on_enter)
        self.bind('<Leave>', self._on_leave)
    
    def _on_enter(self, e):
        if not self._active:
            self.config(bg='#2d3748', fg=TEXT_SECONDARY)
    
    def _on_leave(self, e):
        self.config(bg=FILTER_ACTIVE if self._active else FILTER_INACTIVE,
                   fg='white' if self._active else FILTER_INACTIVE_TEXT)
    
    def set_active(self, active: bool):
        self._active = active
        self.config(bg=FILTER_ACTIVE if active else FILTER_INACTIVE,
                   fg='white' if active else FILTER_INACTIVE_TEXT)


def create_modern_button(parent, text: str, command: Callable = None, 
                         style: str = 'primary', **kwargs) -> tk.Button:
    """Create a modern gradient-style button."""
    styles = {
        'primary': (BTN_PRIMARY_BG, BTN_PRIMARY_HOVER),
        'success': (ACCENT_GREEN, '#059669'),
        'danger': ('#ef4444', '#dc2626'),
        'secondary': (BG_ELEVATED, '#2d3748'),
    }
    bg, abg = styles.get(style, styles['primary'])
    btn = tk.Button(parent, text=text, command=command,
                    font=(FONT_UI, FONT_SIZE_BASE, 'bold'),
                    bg=bg, fg='white', activebackground=abg, activeforeground='white',
                    relief=tk.FLAT, bd=0, padx=20, pady=10, cursor='hand2',
                    highlightthickness=0, **kwargs)
    return btn
