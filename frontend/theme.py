"""
MediFlow - Modern UI Theme System
Premium medical-tech aesthetic: Dark (Night) / Light (Day) mode, glassmorphism, gradient accents
"""
from __future__ import annotations
import os

# =============================================================================
# THEME: DARK MODE (NIGHT) - Premium Medical-Tech
# =============================================================================

# Background layers (depth)
BG_DEEP = "#0f1419"           # Deep charcoal - main background
BG_BASE = "#151c24"           # Slightly lighter - content areas
BG_CARD = "#1a222d"           # Card/panel background
BG_ELEVATED = "#1e2732"      # Elevated surfaces (sidebar hover, dropdowns)
BG_GLASS = "#252d3a"         # Frosted glass effect (semi-opaque panels)

# Sidebar
SIDEBAR_BG = "#0d1117"
SIDEBAR_WIDTH = 260
SIDEBAR_COLLAPSED = 72
SIDEBAR_ACTIVE = "#1e3a5f"   # Active item background - soft blue
SIDEBAR_ACTIVE_GLOW = "#2563eb"
SIDEBAR_HOVER = "#1a252f"
SIDEBAR_TEXT = "#94a3b8"
SIDEBAR_TEXT_ACTIVE = "#ffffff"
SIDEBAR_ICON = "#64748b"

# Accent gradient (Blue → Purple → Teal)
ACCENT_BLUE = "#3b82f6"
ACCENT_PURPLE = "#8b5cf6"
ACCENT_TEAL = "#06b6d4"
ACCENT_CYAN = "#22d3ee"
ACCENT_PINK = "#ec4899"
ACCENT_GREEN = "#10b981"

# Gradient combinations for cards
GRADIENT_BLUE = (ACCENT_BLUE, "#2563eb")
GRADIENT_PURPLE = (ACCENT_PURPLE, "#7c3aed")
GRADIENT_TEAL = (ACCENT_TEAL, "#0891b2")
GRADIENT_PINK = (ACCENT_PINK, "#db2777")
GRADIENT_GREEN = (ACCENT_GREEN, "#059669")
GRADIENT_ORANGE = ("#f59e0b", "#d97706")
GRADIENT_RED = ("#ef4444", "#dc2626")

# Text
TEXT_PRIMARY = "#f1f5f9"
TEXT_SECONDARY = "#94a3b8"
TEXT_MUTED = "#64748b"
TEXT_DISABLED = "#475569"

# Borders & dividers
BORDER_SUBTLE = "#2d3748"
BORDER_DEFAULT = "#374151"
BORDER_GLOW = "rgba(59, 130, 246, 0.5)"  # CSS-style, use for Canvas

# Shadows (for Canvas - simulated)
SHADOW_COLOR = "#000000"
GLOW_BLUE = "#3b82f6"
GLOW_PURPLE = "#8b5cf6"
GLOW_TEAL = "#06b6d4"

# Status colors
SUCCESS = "#10b981"
WARNING = "#f59e0b"
ERROR = "#ef4444"
INFO = "#3b82f6"

# Buttons
BTN_PRIMARY_BG = ACCENT_BLUE
BTN_PRIMARY_HOVER = "#2563eb"
BTN_SECONDARY_BG = BG_ELEVATED
BTN_SECONDARY_HOVER = "#2d3748"
BTN_DANGER_BG = "#ef4444"
BTN_DANGER_HOVER = "#dc2626"
BTN_SUCCESS_BG = ACCENT_GREEN
BTN_SUCCESS_HOVER = "#059669"

# Filter/Pill buttons
FILTER_ACTIVE = ACCENT_TEAL
FILTER_INACTIVE = BG_ELEVATED
FILTER_INACTIVE_TEXT = TEXT_SECONDARY

# Tables
TABLE_HEADER_BG = BG_ELEVATED
TABLE_ROW_HOVER = "#1e2732"
TABLE_BORDER = BORDER_SUBTLE

# Radius (pixels - for Canvas rounded rects)
RADIUS_SM = 6
RADIUS_MD = 10
RADIUS_LG = 16
RADIUS_XL = 20
RADIUS_CARD = 20

# Fonts (Segoe UI Variable / fallback Inter)
FONT_FAMILY = "Segoe UI Variable"
FONT_FALLBACK = "Segoe UI"
FONT_SIZE_XS = 9
FONT_SIZE_SM = 10
FONT_SIZE_BASE = 11
FONT_SIZE_LG = 12
FONT_SIZE_XL = 14
FONT_SIZE_2XL = 18
FONT_SIZE_3XL = 24
FONT_SIZE_4XL = 28

# Spacing
SPACING_XS = 4
SPACING_SM = 8
SPACING_MD = 16
SPACING_LG = 24
SPACING_XL = 32

# =============================================================================
# DAY / NIGHT MODE - Theme switching
# =============================================================================

THEME_DARK = {
    "BG_DEEP": BG_DEEP,
    "BG_BASE": BG_BASE,
    "BG_CARD": BG_CARD,
    "BG_ELEVATED": BG_ELEVATED,
    "BG_GLASS": BG_GLASS,
    "TABLE_HEADER_BG": TABLE_HEADER_BG,
    "SIDEBAR_BG": SIDEBAR_BG,
    "SIDEBAR_ACTIVE": SIDEBAR_ACTIVE,
    "SIDEBAR_HOVER": SIDEBAR_HOVER,
    "SIDEBAR_TEXT": SIDEBAR_TEXT,
    "SIDEBAR_TEXT_ACTIVE": SIDEBAR_TEXT_ACTIVE,
    "SIDEBAR_ICON": SIDEBAR_ICON,
    "TEXT_PRIMARY": TEXT_PRIMARY,
    "TEXT_SECONDARY": TEXT_SECONDARY,
    "TEXT_MUTED": TEXT_MUTED,
    "TEXT_DISABLED": TEXT_DISABLED,
    "BORDER_SUBTLE": BORDER_SUBTLE,
    "BORDER_DEFAULT": BORDER_DEFAULT,
    "ACCENT_BLUE": ACCENT_BLUE,
    "ACCENT_TEAL": ACCENT_TEAL,
}

# Light (Day) theme
THEME_LIGHT = {
    "BG_DEEP": "#f1f5f9",
    "BG_BASE": "#ffffff",
    "BG_CARD": "#ffffff",
    "BG_ELEVATED": "#f8fafc",
    "BG_GLASS": "#e2e8f0",
    "TABLE_HEADER_BG": "#e2e8f0",
    "SIDEBAR_BG": "#0f172a",
    "SIDEBAR_ACTIVE": "#1e3a5f",
    "SIDEBAR_HOVER": "#1e293b",
    "SIDEBAR_TEXT": "#94a3b8",
    "SIDEBAR_TEXT_ACTIVE": "#ffffff",
    "SIDEBAR_ICON": "#64748b",
    "TEXT_PRIMARY": "#0f172a",
    "TEXT_SECONDARY": "#475569",
    "TEXT_MUTED": "#64748b",
    "TEXT_DISABLED": "#94a3b8",
    "BORDER_SUBTLE": "#e2e8f0",
    "BORDER_DEFAULT": "#cbd5e1",
    "ACCENT_BLUE": "#2563eb",
    "ACCENT_TEAL": "#0891b2",
}

_THEME_FILE = None

def _get_theme_file():
    global _THEME_FILE
    if _THEME_FILE is not None:
        return _THEME_FILE
    try:
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        _THEME_FILE = os.path.join(base, "config", "theme.txt")
        os.makedirs(os.path.dirname(_THEME_FILE), exist_ok=True)
    except Exception:
        _THEME_FILE = os.path.join(os.path.expanduser("~"), ".mediflow_theme.txt")
    return _THEME_FILE

_current_mode = "night"  # "night" | "day"

def _load_saved_theme():
    global _current_mode
    try:
        path = _get_theme_file()
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                mode = f.read().strip().lower()
                if mode in ("day", "night"):
                    _current_mode = mode
    except Exception:
        pass

def get_theme():
    """Return the current theme dict (for day or night mode)."""
    return THEME_LIGHT if _current_mode == "day" else THEME_DARK

def get_theme_mode():
    """Return current mode: 'day' or 'night'."""
    return _current_mode

def set_theme(mode: str):
    """Set theme to 'day' or 'night' and persist preference."""
    global _current_mode
    mode = mode.lower()
    if mode not in ("day", "night"):
        return
    _current_mode = mode
    try:
        with open(_get_theme_file(), "w", encoding="utf-8") as f:
            f.write(_current_mode)
    except Exception:
        pass

# Load saved preference on import
_load_saved_theme()
