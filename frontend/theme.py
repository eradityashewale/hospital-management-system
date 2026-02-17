"""
MediFlow - Modern UI Theme System
Premium medical-tech aesthetic: Dark mode, glassmorphism, gradient accents
"""
from __future__ import annotations

# =============================================================================
# THEME: DARK MODE - Premium Medical-Tech
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
