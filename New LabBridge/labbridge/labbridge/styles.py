import reflex as rx

# =============================================================================
# GLOBAL VIBE CODING - DESIGN SYSTEM (THE ARCHITECT APPROVED)
# =============================================================================
# Principles:
# 1. Aesthetics First: Modern Fintech/Health Vibe (Emerald/Teal + Glass)
# 2. KISS: Flatter structures, less nested dictionaries
# 3. YAGNI: Only what we use. No "Future Proofing".
# =============================================================================

class Color:
    # =============================================================================
    # LABBRIDGE DESIGN SYSTEM - Cores Semânticas
    # Baseado em: UI_UX_STRUCTURE_LABBRIDGE.md
    # - Azul → ações principais, confiança
    # - Verde → sucesso, estabilidade
    # - Amarelo-esverdeado → atenção / destaque
    # - Cinzas neutros para layout
    # =============================================================================

    # --- Primary Brand (Blue - Ações Principais, Confiança) ---
    PRIMARY = "#2563EB"          # Blue 600 - Principal
    PRIMARY_HOVER = "#1D4ED8"    # Blue 700 - Hover
    PRIMARY_LIGHT = "#EFF6FF"    # Blue 50 - Backgrounds, Badges
    PRIMARY_DARK = "#1E40AF"     # Blue 800 - Deep

    # --- Deep & Contrast (Text & Headers) ---
    DEEP = "#1E3A5F"             # Navy Blue - Headers, Premium feel
    SECONDARY = "#3B82F6"        # Blue 500 - Accents

    # --- Neutrals (Clean Slate) ---
    BACKGROUND = "#F8FAFC"       # Slate 50 - Cool Gray Background
    SURFACE = "#FFFFFF"          # Pure White
    TEXT_PRIMARY = "#0F172A"     # Slate 900 - Sharper text
    TEXT_SECONDARY = "#64748B"   # Slate 500 - Soft text
    TEXT_MUTED = "#64748B"       # Slate 500 - Muted text (was #94A3B8, improved for WCAG AA contrast)
    BORDER = "#E2E8F0"           # Slate 200 - Subtle borders
    BORDER_DARK = "#CBD5E1"      # Slate 300 - Stronger borders

    # --- Status (Semantic) ---
    ERROR = "#DC2626"            # Red 600
    ERROR_BG = "#FEF2F2"         # Red 50
    ERROR_LIGHT = "#FECACA"      # Red 200

    SUCCESS = "#16A34A"          # Green 600 - Sucesso, Estabilidade
    SUCCESS_BG = "#F0FDF4"       # Green 50
    SUCCESS_LIGHT = "#BBF7D0"    # Green 200

    WARNING = "#84CC16"          # Lime 500 - Amarelo-esverdeado para atenção
    WARNING_HOVER = "#65A30D"    # Lime 600
    WARNING_BG = "#F7FEE7"       # Lime 50
    WARNING_LIGHT = "#D9F99D"    # Lime 200

    INFO = "#0EA5E9"             # Sky 500 - Informativo
    INFO_BG = "#F0F9FF"          # Sky 50

    # --- Extended Variants (for deep_analysis and other components) ---
    ERROR_DARK = "#991B1B"       # Red 800 - Texto em contexto de erro
    SUCCESS_DARK = "#166534"     # Green 800 - Texto em contexto de sucesso
    WARNING_DARK = "#92400E"     # Amber 800 - Texto em contexto de warning
    PRIMARY_BORDER = "#BFDBFE"   # Blue 200 - Borders em contexto primary

    # --- Vibe Gradients ---
    GRADIENT_PRIMARY = "linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%)"
    GRADIENT_SUCCESS = "linear-gradient(135deg, #16A34A 0%, #15803D 100%)"
    GRADIENT_SURFACE = "radial-gradient(circle at top left, #F8FAFC 0%, #E2E8F0 100%)"
    GRADIENT_GLASS = "linear-gradient(180deg, rgba(255,255,255,0.95) 0%, rgba(255,255,255,0.85) 100%)"
    GRADIENT_HERO = "linear-gradient(135deg, #1E3A5F 0%, #2563EB 100%)"

class Design:
    # --- Layout ---
    MAX_WIDTH_CONTENT = "1200px"
    MAX_WIDTH_WIDE = "1400px"
    
    # --- Radius (Curvier = Friendlier) ---
    RADIUS_MD = "10px"
    RADIUS_LG = "16px"
    RADIUS_XL = "24px" 
    
    # --- Shadows (Soft & floating) ---
    SHADOW_SM = "0 1px 2px 0 rgba(0, 0, 0, 0.05)"
    SHADOW_DEFAULT = "0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03)"
    SHADOW_MD = "0 10px 15px -3px rgba(0, 0, 0, 0.05), 0 4px 6px -2px rgba(0, 0, 0, 0.025)"
    SHADOW_LG = "0 20px 25px -5px rgba(0, 0, 0, 0.05), 0 10px 10px -5px rgba(0, 0, 0, 0.02)"

class Typography:
    # --- Headings ---
    H1 = {"font_size": "2.5rem", "font_weight": "800", "line_height": "1.2", "color": Color.DEEP}
    H2 = {"font_size": "2rem", "font_weight": "700", "line_height": "1.3", "color": Color.DEEP}
    H3 = {"font_size": "1.5rem", "font_weight": "600", "line_height": "1.4", "color": Color.DEEP}
    H4 = {"font_size": "1.25rem", "font_weight": "600", "color": Color.TEXT_PRIMARY}
    H5 = {"font_size": "1rem", "font_weight": "600", "color": Color.TEXT_PRIMARY}
    
    # --- Body ---
    BODY = {"font_size": "1rem", "font_weight": "400", "line_height": "1.6", "color": Color.TEXT_PRIMARY}
    BODY_LARGE = {"font_size": "1.125rem", "font_weight": "400", "color": Color.TEXT_PRIMARY}
    BODY_SECONDARY = {"font_size": "1rem", "color": Color.TEXT_SECONDARY}
    SMALL = {"font_size": "0.875rem", "color": Color.TEXT_SECONDARY}
    CAPTION = {"font_size": "0.75rem", "color": Color.TEXT_SECONDARY}
    
    # --- UI Elements ---
    LABEL = {"font_size": "0.875rem", "font_weight": "500", "color": Color.TEXT_PRIMARY, "margin_bottom": "4px"}
    LABEL_LARGE = {"font_size": "1rem", "font_weight": "500", "color": Color.TEXT_PRIMARY}

class TextSize:
    """
    Typography size tokens - USE THESE instead of inline font_size values.
    
    Examples:
        ❌ font_size="0.875rem"  
        ✅ font_size=TextSize.SMALL
        
        ❌ font_size="0.75rem"
        ✅ font_size=TextSize.CAPTION
    """
    H1 = "2.5rem"      # 40px - Page titles
    H2 = "2rem"        # 32px - Section titles
    H3 = "1.5rem"      # 24px - Card titles
    H4 = "1.25rem"     # 20px - Subsection titles
    H5 = "1rem"        # 16px - Small titles
    BODY = "1rem"      # 16px - Body text
    BODY_LARGE = "1.125rem"  # 18px - Large body
    SMALL = "0.875rem" # 14px - Secondary text, labels
    CAPTION = "0.75rem" # 12px - Captions, meta info
    XS = "0.625rem"    # 10px - Micro text (badges)

class Spacing:
    # --- Consistent Rhythm (4px base) ---
    XS = "4px"
    SM = "8px"
    MD = "16px"
    LG = "24px"
    XL = "32px"
    XXL = "48px"

class Animation:
    FADE_IN_UP = {
        "0%": {"opacity": "0", "transform": "translateY(20px)"},
        "100%": {"opacity": "1", "transform": "translateY(0)"},
    }

# =============================================================================
# TYPOGRAPHY (KISS: Default to Reflex Text props, define only specifics)
# =============================================================================
# We use standard Reflex rx.text(size="...") but provide helpers here if needed.
# For now, we trust the defaults + Inter font.

# =============================================================================
# ANIMATIONS (Vibe Motion)
# =============================================================================
STYLES = {
    "font_family": "'Inter', 'Outfit', sans-serif",
    "background_color": Color.BACKGROUND,
    
    # Keyframes
    "@keyframes fadeIn": {
        "from": {"opacity": "0"},
        "to": {"opacity": "1"},
    },
    "@keyframes slideUp": {
        "from": {"opacity": "0", "transform": "translateY(10px)"},
        "to": {"opacity": "1", "transform": "translateY(0)"},
    },
    
    # Global Classes
    ".animate-fade-in": {"animation": "fadeIn 0.4s ease-out"},
    ".animate-slide-up": {"animation": "slideUp 0.5s cubic-bezier(0.2, 0.8, 0.2, 1)"},
}

# =============================================================================
# COMPONENT STYLES (Refactored for Reusability)
# =============================================================================

# --- Input Fields ---
INPUT_STYLE = {
    "border": f"1px solid {Color.BORDER}",
    "border_radius": Design.RADIUS_LG,
    "padding": f"{Spacing.SM} {Spacing.MD}",
    "min_height": "48px", # Touch target accessible
    "bg": Color.SURFACE,
    "color": Color.TEXT_PRIMARY,
    "transition": "all 0.2s cubic-bezier(0.4, 0, 0.2, 1)",
    "_focus": {
        "border_color": Color.PRIMARY,
        "box_shadow": f"0 0 0 4px {Color.PRIMARY_LIGHT}",
        "outline": "none"
    },
    "_hover": {"border_color": Color.SECONDARY}
}

# --- Large Input (Matching Button XL) ---
INPUT_XL_STYLE = {
    "border": f"1px solid {Color.BORDER}",
    "border_radius": Design.RADIUS_LG,
    "padding": f"{Spacing.MD} {Spacing.XL}", # More breathing room
    "height": "56px", # Matching Button XL
    "width": "100%",  # Explicit Full Width
    "bg": Color.SURFACE,
    "color": Color.TEXT_PRIMARY,
    "font_size": "1rem",
    "transition": "all 0.2s cubic-bezier(0.4, 0, 0.2, 1)",
    "_focus": {
        "border_color": Color.PRIMARY,
        "box_shadow": f"0 0 0 4px {Color.PRIMARY_LIGHT}",
        "outline": "none"
    },
    "_hover": {"border_color": Color.SECONDARY}
}

# --- Primary Button ---
BUTTON_PRIMARY_STYLE = {
    "bg": Color.PRIMARY,
    "color": "white",
    "padding_x": Spacing.LG,
    "min_height": "48px",
    "border_radius": Design.RADIUS_LG,
    "font_weight": "600",
    "transition": "all 0.2s cubic-bezier(0.4, 0, 0.2, 1)",
    "box_shadow": Design.SHADOW_DEFAULT,
    "_hover": {
        "bg": Color.PRIMARY_HOVER,
        "transform": "translateY(-2px)",
        "box_shadow": Design.SHADOW_MD,
    },
    "_active": {
        "transform": "scale(0.98)",
        "box_shadow": "none",
    }
}

# --- Large/XL Button (Impact) ---
BUTTON_XL_STYLE = {
    "bg": Color.PRIMARY,
    "color": "white",
    "padding_x": Spacing.XL,
    "height": "56px", # Taller for impact
    "width": "100%",  # Usually full width
    "border_radius": Design.RADIUS_LG,
    "font_weight": "700", # Bolder
    "font_size": "1.125rem", # Larger Frame
    "transition": "all 0.2s cubic-bezier(0.4, 0, 0.2, 1)",
    "box_shadow": Design.SHADOW_MD,
    "_hover": {
        "bg": Color.PRIMARY_HOVER,
        "transform": "translateY(-2px)",
        "box_shadow": Design.SHADOW_LG,
    },
    "_active": {
        "transform": "scale(0.99)",
        "box_shadow": "none",
    }
}

# --- Glass Card ( The Crown Jewel) ---
CARD_STYLE = {
    "bg": Color.SURFACE,
    "border": f"1px solid {Color.BORDER}",
    "border_radius": Design.RADIUS_XL,
    "padding": Spacing.LG,
    "box_shadow": Design.SHADOW_DEFAULT,
    "transition": "all 0.3s ease",
    "_hover": {
        "box_shadow": Design.SHADOW_MD,
        "border_color": Color.PRIMARY_LIGHT, # Subtle glow
    }
}

# Botão Secundário / Outline
BUTTON_SECONDARY_STYLE = {
    "bg": "transparent",
    "color": Color.DEEP,
    "border": f"2px solid {Color.BORDER}",
    "padding_y": Spacing.SM,
    "padding_x": Spacing.LG,
    "min_height": "48px",
    "min_width": "120px",
    "border_radius": Design.RADIUS_LG,
    "font_weight": "600",
    "font_size": "1rem",
    "cursor": "pointer",
    "transition": "all 0.2s ease",
    "_hover": {
        "bg": Color.PRIMARY_LIGHT,
        "border_color": Color.PRIMARY,
        "transform": "translateY(-1px)",
        "box_shadow": Design.SHADOW_SM,
    },
    "_active": { "transform": "translateY(0)" },
    "_focus": {
        "outline": f"2px solid {Color.PRIMARY}",
        "outline_offset": "2px",
    },
    "_disabled": {
        "opacity": 0.5,
        "cursor": "not-allowed",
        "transform": "none",
    }
}

# Glassmorphism Style
GLASS_STYLE = {
    "background_color": "rgba(255, 255, 255, 0.7)",
    "backdrop_filter": "blur(12px) saturate(180%)",
    "-webkit-backdrop-filter": "blur(12px) saturate(180%)",
    "border": "1px solid rgba(255, 255, 255, 0.3)",
}

# Estilo para Tabelas
TABLE_STYLE = {
    "width": "100%",
    "border_collapse": "separate",
    "border_spacing": "0",
    "border": f"1px solid {Color.BORDER}",
    "border_radius": Design.RADIUS_LG,
    "overflow": "hidden",
}

TABLE_HEADER_STYLE = {
    "bg": Color.PRIMARY_LIGHT,
    "color": Color.DEEP,
    "font_weight": "600",
    "font_size": "0.875rem",
    "text_transform": "uppercase",
    "letter_spacing": "0.05em",
    "padding": f"{Spacing.MD} {Spacing.MD}",
    "text_align": "left",
    "border_bottom": f"2px solid {Color.PRIMARY}",
}

TABLE_CELL_STYLE = {
    "padding": f"{Spacing.SM} {Spacing.MD}",  
    "border_bottom": f"1px solid {Color.BORDER}",
    "color": Color.TEXT_PRIMARY,
    "font_size": "0.875rem",
}

TABLE_ROW_STYLE = {
    "transition": "background-color 0.15s ease",
    "_hover": {"bg": Color.PRIMARY_LIGHT + "40"}
}

TABLE_ROW_EVEN_STYLE = {
    "bg": "#F9FAFB",
}
