"""ArabArena visual identity — HumanAI-inspired app shell CSS."""

from __future__ import annotations

ARABARENA_COLORS = {
    "bg_primary": "#0B0F14",
    "bg_secondary": "#10161D",
    "bg_elevated": "#171E27",
    "bg_input": "#0F1419",
    "accent": "#10A37F",
    "accent_soft": "rgba(16, 163, 127, 0.14)",
    "accent_border": "rgba(16, 163, 127, 0.40)",
    "gold": "#C9A227",
    "gold_soft": "rgba(201, 162, 39, 0.15)",
    "text_primary": "#ECECF1",
    "text_muted": "#9CA3AF",
    "text_dim": "#6B7280",
    "border": "rgba(255, 255, 255, 0.07)",
    "border_strong": "rgba(255, 255, 255, 0.12)",
    "assistant_bubble": "rgba(255, 255, 255, 0.035)",
    "user_bubble": "rgba(16, 163, 127, 0.12)",
    "sidebar_bg": "#0C1117",
}

ARABARENA_GRADIENTS = {
    "accent_button": "linear-gradient(135deg, #0D9488 0%, #10A37F 100%)",
    "shell_glow": "radial-gradient(ellipse 80% 55% at 50% 20%, rgba(16,163,127,0.06) 0%, transparent 70%)",
    "composer_border": "linear-gradient(135deg, rgba(16,163,127,0.55), rgba(201,162,39,0.35))",
    "sidebar_top": "linear-gradient(180deg, rgba(16,163,127,0.06) 0%, transparent 100%)",
}

ARABARENA_RADIUS = {
    "sm": "8px",
    "md": "12px",
    "lg": "16px",
    "xl": "24px",
    "pill": "999px",
}

ARABARENA_FONT = '"Segoe UI", Tahoma, "Noto Sans Arabic", "IBM Plex Sans Arabic", sans-serif'
SIDEBAR_WIDTH = "250px"


def dashboard_css() -> str:
    c = ARABARENA_COLORS
    g = ARABARENA_GRADIENTS
    r = ARABARENA_RADIUS
    return f"""
    <style>
    #MainMenu, footer, header {{ visibility: hidden; height: 0; }}
    .stApp {{
        background: {c["bg_primary"]};
        font-family: {ARABARENA_FONT};
    }}
    [data-testid="stAppViewContainer"] {{
        background: {c["bg_primary"]};
    }}
    [data-testid="stSidebar"] {{
        width: {SIDEBAR_WIDTH} !important;
        min-width: {SIDEBAR_WIDTH} !important;
        max-width: {SIDEBAR_WIDTH} !important;
        background: {c["sidebar_bg"]};
        border-right: 1px solid {c["border"]};
        direction: rtl;
    }}
    [data-testid="stSidebar"] > div:first-child {{
        background: {g["sidebar_top"]};
    }}
    [data-testid="stSidebar"] .block-container {{
        padding: 1rem 0.85rem 1.25rem;
    }}
    [data-testid="stSidebar"] [data-testid="stVerticalBlock"] {{
        gap: 0.35rem;
    }}
    section.main {{
        direction: rtl;
        background: {g["shell_glow"]}, {c["bg_primary"]};
    }}
    section.main .block-container {{
        padding-top: 0.75rem;
        padding-bottom: 1.5rem;
        max-width: 780px;
    }}

    .aa-sidebar-brand {{
        font-size: 1rem;
        font-weight: 700;
        color: {c["text_primary"]};
        margin-bottom: 0.75rem;
        padding-bottom: 0.65rem;
        border-bottom: 1px solid {c["border"]};
    }}
    .aa-sidebar-section {{
        font-size: 0.68rem;
        color: {c["text_dim"]};
        letter-spacing: 0.03em;
        margin: 0.65rem 0 0.35rem;
    }}
    .aa-sidebar-list {{
        max-height: 42vh;
        overflow-y: auto;
        padding-left: 2px;
    }}
    .aa-sidebar-footer {{
        margin-top: auto;
        padding-top: 0.75rem;
        border-top: 1px solid {c["border"]};
        font-size: 0.75rem;
        color: {c["text_dim"]};
    }}
    .aa-powered-badge {{
        display: inline-block;
        padding: 0.18rem 0.5rem;
        border-radius: {r["pill"]};
        background: {c["accent_soft"]};
        border: 1px solid {c["accent_border"]};
        color: {c["text_muted"]};
        font-size: 0.65rem;
    }}
    [data-testid="stSidebar"] .stButton > button {{
        text-align: right;
        font-size: 0.78rem;
        padding: 0.45rem 0.65rem;
        min-height: 2.2rem;
    }}
    .aa-sidebar-conv-btn > button {{
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }}

    .aa-welcome-compact {{
        text-align: center;
        font-size: 0.95rem;
        color: {c["text_muted"]};
        margin: 0.5rem auto 0.75rem;
    }}
    .aa-canvas-empty {{
        min-height: auto;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        text-align: center;
        padding: 1rem;
    }}
    .aa-welcome {{
        font-size: 1.35rem;
        font-weight: 600;
        color: {c["text_primary"]};
        margin: 0 0 0.75rem;
    }}
    .aa-quick-chips-wrap {{
        display: flex;
        flex-wrap: wrap;
        gap: 0.35rem;
        justify-content: center;
        margin: 0 auto 0.85rem;
        max-width: 640px;
    }}
    .aa-quick-chips-wrap .stButton > button {{
        font-size: 0.72rem !important;
        padding: 0.22rem 0.65rem !important;
        min-height: 1.75rem !important;
        border-radius: {r["pill"]} !important;
        background: rgba(255,255,255,0.02) !important;
    }}

    .aa-composer-shell {{
        width: 100%;
        max-width: 700px;
        margin: 0 auto;
        padding: 1px;
        border-radius: {r["xl"]};
        background: {g["composer_border"]};
        box-shadow: 0 0 28px rgba(16,163,127,0.07);
    }}
    .aa-composer-inner {{
        position: relative;
        border-radius: calc({r["xl"]} - 1px);
        background: {c["bg_elevated"]};
        padding: 0.65rem 0.85rem 0.55rem;
    }}
    .aa-composer-chips {{
        display: flex;
        flex-wrap: wrap;
        gap: 0.25rem;
        margin-bottom: 0.35rem;
    }}
    .aa-composer-inner textarea {{
        direction: rtl;
        border: none !important;
        background: transparent !important;
        box-shadow: none !important;
        color: {c["text_primary"]} !important;
        font-size: 0.95rem !important;
        min-height: 48px !important;
        padding: 0 !important;
        resize: none !important;
    }}
    .aa-composer-inner textarea:focus {{
        outline: none !important;
        box-shadow: none !important;
    }}
    .aa-composer-inner [data-testid="stForm"] {{
        border: none;
        padding: 0;
        margin: 0;
    }}
    .aa-composer-inner [data-testid="column"] {{
        align-items: center;
    }}
    .aa-composer-plus {{
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 1.75rem;
        height: 1.75rem;
        border-radius: {r["pill"]};
        border: 1px solid {c["border_strong"]};
        color: {c["accent"]};
        font-size: 1rem;
        line-height: 1;
    }}
    .aa-composer-meta {{
        font-size: 0.68rem;
        color: {c["text_dim"]};
        text-align: left;
        direction: ltr;
    }}
    .aa-composer-dock {{
        position: sticky;
        bottom: 0.5rem;
        z-index: 50;
        margin-top: 0.75rem;
    }}
    .aa-upload-overlay {{
        position: absolute;
        left: 3.1rem;
        bottom: 0.55rem;
        width: 2rem;
        height: 2rem;
        overflow: hidden;
        opacity: 0.001;
        z-index: 20;
        pointer-events: auto;
    }}
    .aa-upload-overlay [data-testid="stFileUploader"] {{
        border: none !important;
        background: transparent !important;
        padding: 0 !important;
        min-height: 0 !important;
        width: 2rem !important;
        height: 2rem !important;
    }}
    .aa-upload-overlay [data-testid="stFileUploader"] section {{
        padding: 0 !important;
        min-height: 0 !important;
    }}
    .aa-upload-overlay [data-testid="stFileUploader"] small,
    .aa-upload-overlay [data-testid="stFileUploader"] label {{
        display: none !important;
    }}

    .aa-sidebar-chat-item {{
        padding: 0.45rem 0.55rem;
        border-radius: {r["md"]};
        border: 1px solid transparent;
        margin-bottom: 0.2rem;
        background: rgba(255,255,255,0.02);
    }}
    .aa-sidebar-chat-title {{
        font-size: 0.78rem;
        font-weight: 600;
        color: {c["text_primary"]};
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }}
    .aa-sidebar-chat-preview {{
        font-size: 0.68rem;
        color: {c["text_muted"]};
        margin-top: 0.1rem;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }}
    .aa-sidebar-chat-time {{
        font-size: 0.62rem;
        color: {c["text_dim"]};
        margin-top: 0.08rem;
    }}

    .aa-attachment-chip {{
        display: inline-flex;
        align-items: center;
        padding: 0.14rem 0.45rem;
        border-radius: {r["pill"]};
        background: {c["accent_soft"]};
        border: 1px solid {c["accent_border"]};
        font-size: 0.68rem;
        color: {c["text_muted"]};
    }}
    .aa-inline-note {{
        font-size: 0.68rem;
        color: {c["text_muted"]};
        margin: 0.15rem 0 0.35rem;
    }}

    .aa-chat-thread {{
        padding: 0.25rem 0 0.75rem;
        max-height: calc(100vh - 260px);
        overflow-y: auto;
    }}
    .aa-msg-row {{ margin-bottom: 0.85rem; }}
    div[data-testid="stChatMessage"] {{
        background: transparent;
        direction: rtl;
        gap: 0.55rem;
    }}
    .aa-msg-user div[data-testid="stChatMessage"] {{
        margin-right: auto;
        margin-left: 0;
        max-width: 70%;
    }}
    .aa-msg-assistant div[data-testid="stChatMessage"] {{
        margin-right: 0;
        margin-left: auto;
        max-width: 92%;
    }}
    div[data-testid="stChatMessageContent"] {{
        border-radius: {r["lg"]};
        border: none;
        background: {c["assistant_bubble"]};
        line-height: 1.65;
        padding: 0.65rem 0.85rem;
    }}
    .aa-msg-user div[data-testid="stChatMessageContent"] {{
        background: {c["user_bubble"]};
    }}
    .aa-msg-assistant div[data-testid="stChatMessageContent"] {{
        border: 1px solid {c["border"]};
    }}

    .aa-thinking {{ color: {c["accent"]}; font-size: 0.82rem; padding: 0.25rem 0; }}
    .aa-disclaimer-footer {{
        text-align: center;
        font-size: 0.62rem;
        color: {c["text_dim"]};
        margin-top: 0.55rem;
        line-height: 1.4;
    }}

    .stButton > button {{
        border-radius: {r["md"]};
        border: 1px solid {c["border_strong"]};
        background: rgba(255,255,255,0.03);
        color: {c["text_primary"]};
        transition: all 0.15s ease;
    }}
    .stButton > button:hover {{
        border-color: {c["accent_border"]};
        background: {c["accent_soft"]};
    }}
    .stButton > button[kind="primary"] {{
        background: {g["accent_button"]};
        border: none;
        color: #fff;
        min-width: 2.25rem;
        min-height: 2.25rem;
        border-radius: {r["pill"]};
    }}
    div[data-testid="stChatInput"] {{ display: none; }}
    </style>
    """