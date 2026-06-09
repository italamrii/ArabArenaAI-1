"""Production-grade CSS for ArabArena simple chat."""

from __future__ import annotations

from workspace.ui.theme import ARABARENA_COLORS, ARABARENA_FONT, ARABARENA_GRADIENTS, ARABARENA_RADIUS


def simple_chat_css(*, show_uploads: bool = False) -> str:
    c = ARABARENA_COLORS
    g = ARABARENA_GRADIENTS
    r = ARABARENA_RADIUS
    upload_rules = ""
    if not show_uploads:
        upload_rules = """
    .aa-upload-hidden, .aa-simple-upload-overlay,
    .aa-simple-chip, .aa-simple-note, .aa-simple-attach-icon {
        display: none !important;
    }
"""
    return f"""
    <style>
    @keyframes aa-fade-up {{
        from {{ opacity: 0; transform: translateY(10px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}
    @keyframes aa-pulse-glow {{
        0%, 100% {{ opacity: 0.55; transform: scale(1); }}
        50% {{ opacity: 1; transform: scale(1.04); }}
    }}
    @keyframes aa-shimmer {{
        0% {{ background-position: 200% center; }}
        100% {{ background-position: -200% center; }}
    }}
    @keyframes aa-thinking-dots {{
        0%, 80%, 100% {{ opacity: 0.25; }}
        40% {{ opacity: 1; }}
    }}

    #MainMenu, footer, header {{ visibility: hidden; height: 0; }}
    [data-testid="stSidebar"], section[data-testid="stSidebar"] {{ display: none !important; }}
    [data-testid="collapsedControl"] {{ display: none !important; }}

    .stApp {{
        background: {c["bg_primary"]};
        font-family: {ARABARENA_FONT};
    }}
    [data-testid="stAppViewContainer"] > .main {{
        background:
            radial-gradient(ellipse 90% 60% at 50% 18%, rgba(16,163,127,0.14) 0%, transparent 62%),
            radial-gradient(ellipse 70% 45% at 50% 85%, rgba(201,162,39,0.05) 0%, transparent 55%),
            {c["bg_primary"]};
    }}
    .block-container {{
        padding-top: 1.75rem;
        padding-bottom: 0.75rem;
        max-width: 960px;
    }}
    [data-testid="stVerticalBlock"] {{ gap: 0.45rem; }}

    .aa-hero {{
        position: relative;
        margin: 0 auto 0.85rem;
        padding: 0.35rem 0 0.15rem;
        animation: aa-fade-up 0.55s ease-out;
    }}
    .aa-hero-compact {{
        margin-bottom: 0.55rem;
        padding-top: 0.1rem;
    }}
    .aa-hero-glow {{
        position: absolute;
        inset: -24px 8% auto;
        height: 110px;
        background: radial-gradient(ellipse at center, rgba(16,163,127,0.16) 0%, transparent 70%);
        pointer-events: none;
        z-index: 0;
    }}
    .aa-hero-brand-row {{
        position: relative;
        z-index: 1;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 0.85rem;
        direction: rtl;
    }}
    .aa-brand-avatar {{
        flex-shrink: 0;
        width: 3.1rem;
        height: 3.1rem;
        border-radius: 16px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.45rem;
        background: linear-gradient(145deg, rgba(16,163,127,0.22) 0%, rgba(201,162,39,0.12) 100%);
        border: 1px solid {c["accent_border"]};
        box-shadow: 0 0 24px rgba(16,163,127,0.18);
    }}
    .aa-hero-compact .aa-brand-avatar {{
        width: 2.35rem;
        height: 2.35rem;
        font-size: 1.05rem;
        border-radius: 12px;
    }}
    .aa-hero-brand-text {{
        text-align: right;
    }}
    .aa-hero-title {{
        margin: 0;
        font-size: clamp(1.85rem, 4.5vw, 2.55rem);
        font-weight: 700;
        letter-spacing: -0.02em;
        color: {c["text_primary"]};
        line-height: 1.12;
    }}
    .aa-hero-compact .aa-hero-title {{
        font-size: clamp(1.25rem, 3vw, 1.5rem);
    }}
    .aa-hero-gold {{ color: {c["gold"]}; }}
    .aa-hero-tagline {{
        margin: 0.35rem 0 0;
        max-width: 420px;
        font-size: 0.92rem;
        line-height: 1.5;
        color: {c["text_muted"]};
    }}
    .aa-hero-compact .aa-hero-tagline {{ display: none; }}
    .aa-hero-badge {{
        display: inline-block;
        margin-top: 0.45rem;
        padding: 0.14rem 0.55rem;
        border-radius: {r["pill"]};
        font-size: 0.62rem;
        font-weight: 600;
        letter-spacing: 0.06em;
        text-transform: uppercase;
        color: {c["gold"]};
        background: {c["gold_soft"]};
        border: 1px solid rgba(201,162,39,0.35);
    }}
    .aa-hero-compact .aa-hero-badge {{
        margin-top: 0.2rem;
        font-size: 0.55rem;
    }}

    .aa-search-shell {{
        width: min(78%, 680px);
        min-width: min(94vw, 300px);
        margin: 0 auto 0.65rem;
        animation: aa-fade-up 0.55s ease-out 0.05s both;
    }}
    .aa-search-bar {{
        padding: 1px;
        border-radius: 16px;
        background: linear-gradient(135deg, rgba(16,163,127,0.35), rgba(16,163,127,0.08));
        box-shadow: 0 0 18px rgba(16,163,127,0.08);
    }}
    .aa-search-bar [data-testid="stTextInput"] > div > div {{
        direction: rtl;
        background: {c["bg_elevated"]} !important;
        border: none !important;
        border-radius: 15px !important;
        min-height: 2.65rem !important;
        box-shadow: inset 0 1px 0 rgba(255,255,255,0.03) !important;
    }}
    .aa-search-bar input {{
        direction: rtl;
        color: {c["text_primary"]} !important;
        font-size: 0.88rem !important;
    }}
    .aa-search-bar input::placeholder {{
        color: {c["text_dim"]} !important;
    }}
    .aa-search-results {{
        margin-top: 0.45rem;
        display: flex;
        flex-direction: column;
        gap: 0.35rem;
    }}
    .aa-search-result-card {{
        direction: rtl;
        text-align: right;
        padding: 0.55rem 0.75rem;
        border-radius: 12px;
        background: rgba(255,255,255,0.03);
        border: 1px solid {c["border_strong"]};
        animation: aa-fade-up 0.3s ease-out;
    }}
    .aa-search-result-meta {{
        font-size: 0.68rem;
        color: {c["accent"]};
        margin-bottom: 0.2rem;
        font-weight: 600;
    }}
    .aa-search-result-snippet {{
        font-size: 0.82rem;
        color: {c["text_muted"]};
        line-height: 1.55;
    }}
    .aa-search-empty {{
        direction: rtl;
        text-align: center;
        font-size: 0.78rem;
        color: {c["text_dim"]};
        padding: 0.35rem 0;
    }}

    .aa-empty-state {{
        text-align: center;
        margin: 0.15rem auto 0.45rem;
        animation: aa-fade-up 0.55s ease-out 0.08s both;
    }}
    .aa-empty-greeting {{
        margin: 0;
        font-size: clamp(1.1rem, 2.8vw, 1.45rem);
        font-weight: 600;
        color: {c["text_primary"]};
        line-height: 1.35;
    }}

    .aa-quick-chips {{
        width: min(78%, 720px);
        min-width: min(94vw, 300px);
        margin: 0.45rem auto 0.25rem;
        animation: aa-fade-up 0.5s ease-out 0.12s both;
    }}
    .aa-quick-chips .stButton > button {{
        width: 100%;
        font-size: 0.72rem !important;
        padding: 0.32rem 0.55rem !important;
        min-height: 1.9rem !important;
        border-radius: {r["pill"]} !important;
        border: 1px solid {c["border_strong"]} !important;
        background: rgba(255,255,255,0.025) !important;
        color: {c["text_muted"]} !important;
    }}
    .aa-quick-chips .stButton > button:hover {{
        border-color: {c["accent_border"]} !important;
        background: {c["accent_soft"]} !important;
        color: {c["text_primary"]} !important;
    }}

    .aa-chat-shell {{
        max-width: 900px;
        margin: 0 auto;
        width: 100%;
    }}
    .aa-composer-wrap {{
        width: min(78%, 760px);
        min-width: min(94vw, 320px);
        margin: 0.35rem auto 0;
        animation: aa-fade-up 0.55s ease-out 0.08s both;
    }}
    .aa-composer-wrap-hero {{
        margin-top: 0.1rem;
    }}

    .aa-simple-thread {{
        direction: rtl;
        margin: 0.15rem auto 0.45rem;
        max-height: calc(100vh - 280px);
        overflow-y: auto;
        padding: 0 0.1rem;
    }}

    .aa-msg-user {{
        direction: rtl;
        text-align: right;
        margin: 0.45rem 0 0.75rem;
        padding: 0.75rem 1rem;
        border-radius: 18px;
        background: linear-gradient(135deg, rgba(16,163,127,0.16) 0%, rgba(16,163,127,0.08) 100%);
        border: 1px solid {c["accent_border"]};
        color: {c["text_primary"]};
        font-size: 0.98rem;
        line-height: 1.65;
        max-width: 78%;
        margin-right: 0;
        margin-left: auto;
        box-shadow: 0 8px 24px rgba(0,0,0,0.18);
        animation: aa-fade-up 0.35s ease-out;
        white-space: pre-wrap;
    }}

    .aa-msg-assistant-card {{
        direction: rtl;
        text-align: right;
        margin: 0 0 1rem;
        padding: 1rem 1.15rem;
        border-radius: 20px;
        background: linear-gradient(180deg, rgba(255,255,255,0.045) 0%, rgba(255,255,255,0.025) 100%);
        border: 1px solid {c["border_strong"]};
        box-shadow:
            0 1px 0 rgba(255,255,255,0.04) inset,
            0 12px 32px rgba(0,0,0,0.22),
            0 0 0 1px rgba(16,163,127,0.06);
        animation: aa-fade-up 0.45s ease-out;
    }}
    .aa-msg-assistant-card .stMarkdown {{
        color: {c["text_primary"]};
        font-size: 1.02rem;
        line-height: 1.9;
    }}
    .aa-msg-assistant-card .stMarkdown p {{
        margin: 0 0 0.9rem;
    }}
    .aa-msg-assistant-card .stMarkdown p:last-child {{ margin-bottom: 0; }}
    .aa-msg-assistant-card .stMarkdown ul,
    .aa-msg-assistant-card .stMarkdown ol {{
        margin: 0.4rem 0 0.95rem;
        padding-right: 1.45rem;
        padding-left: 0;
    }}
    .aa-msg-assistant-card .stMarkdown li {{
        margin-bottom: 0.45rem;
        line-height: 1.8;
    }}
    .aa-msg-assistant-card .stMarkdown li::marker {{ color: {c["accent"]}; }}
    .aa-msg-assistant-card .stMarkdown h1,
    .aa-msg-assistant-card .stMarkdown h2,
    .aa-msg-assistant-card .stMarkdown h3 {{
        margin: 0.85rem 0 0.55rem;
        line-height: 1.35;
        font-weight: 600;
    }}
    .aa-msg-assistant-card .stMarkdown strong {{ color: {c["text_primary"]}; }}
    .aa-msg-assistant-card .stMarkdown code {{
        background: rgba(16,163,127,0.1);
        border: 1px solid rgba(16,163,127,0.18);
        padding: 0.12rem 0.4rem;
        border-radius: {r["sm"]};
        font-size: 0.88em;
    }}
    .aa-msg-assistant-card .stMarkdown pre {{
        background: rgba(0,0,0,0.35);
        border: 1px solid {c["border_strong"]};
        border-radius: 14px;
        padding: 0.9rem 1rem;
        overflow-x: auto;
        margin: 0.55rem 0 0.95rem;
        box-shadow: inset 0 1px 0 rgba(255,255,255,0.04);
    }}
    .aa-msg-assistant-card .stMarkdown pre code {{
        background: transparent;
        border: none;
        padding: 0;
    }}

    .aa-glow-composer {{
        width: 100%;
        padding: 2px;
        border-radius: 22px;
        background: {g["composer_border"]};
        box-shadow:
            0 0 0 1px rgba(16,163,127,0.14),
            0 4px 24px rgba(0,0,0,0.28),
            0 0 40px rgba(16,163,127,0.16),
            0 0 64px rgba(201,162,39,0.05);
        transition: box-shadow 0.25s ease;
    }}
    .aa-glow-composer:focus-within {{
        box-shadow:
            0 0 0 1px rgba(16,163,127,0.32),
            0 6px 28px rgba(0,0,0,0.32),
            0 0 52px rgba(16,163,127,0.26),
            0 0 72px rgba(201,162,39,0.08);
    }}
    .aa-glow-composer-body {{
        border-radius: 20px;
        background: linear-gradient(165deg, {c["bg_elevated"]} 0%, {c["bg_secondary"]} 100%);
        padding: 0.85rem 0.9rem 0.75rem;
    }}
    .aa-glow-composer-body [data-testid="stForm"] {{
        border: none;
        padding: 0;
        margin: 0;
    }}
    .aa-glow-composer-body textarea {{
        direction: rtl;
        border: none !important;
        background: transparent !important;
        box-shadow: none !important;
        color: {c["text_primary"]} !important;
        font-size: 1.06rem !important;
        min-height: 90px !important;
        max-height: 200px !important;
        padding: 0.35rem 0.4rem !important;
        resize: none !important;
        line-height: 1.65 !important;
    }}
    .aa-glow-composer-body textarea:focus {{
        outline: none !important;
        box-shadow: none !important;
    }}
    .aa-glow-composer-body textarea::placeholder {{ color: {c["text_dim"]} !important; }}
    .aa-send-row {{
        display: flex;
        justify-content: flex-start;
        direction: rtl;
        margin-top: 0.55rem;
    }}
    .aa-glow-composer-body .aa-send-row .stButton {{
        width: auto;
    }}
    .aa-glow-composer-body .aa-send-row .stButton > button {{
        background: {g["accent_button"]} !important;
        border: 1px solid rgba(16,163,127,0.45) !important;
        color: #fff !important;
        border-radius: 14px !important;
        min-height: 2.65rem !important;
        padding: 0.45rem 1.15rem !important;
        font-size: 0.88rem !important;
        font-weight: 600 !important;
        box-shadow: 0 0 18px rgba(16,163,127,0.28) !important;
        transition: all 0.2s ease !important;
    }}
    .aa-glow-composer-body .aa-send-row .stButton > button:hover {{
        box-shadow: 0 0 26px rgba(16,163,127,0.38) !important;
        transform: translateY(-1px);
    }}
    .aa-glow-composer-body .aa-send-row .stButton > button:disabled {{
        opacity: 0.55 !important;
        transform: none !important;
    }}
    .aa-glow-composer-dock {{
        position: sticky;
        bottom: 0.35rem;
        z-index: 40;
    }}

    .aa-thinking-card {{
        direction: rtl;
        display: inline-flex;
        align-items: center;
        gap: 0.45rem;
        margin: 0.15rem 0 0.65rem;
        padding: 0.55rem 0.9rem;
        border-radius: {r["pill"]};
        background: {c["accent_soft"]};
        border: 1px solid {c["accent_border"]};
        color: {c["accent"]};
        font-size: 0.88rem;
        animation: aa-fade-up 0.3s ease-out;
    }}
    .aa-thinking-dot {{
        display: inline-block;
        width: 5px;
        height: 5px;
        border-radius: 50%;
        background: {c["accent"]};
        animation: aa-thinking-dots 1.2s infinite ease-in-out;
    }}
    .aa-thinking-dot:nth-child(2) {{ animation-delay: 0.15s; }}
    .aa-thinking-dot:nth-child(3) {{ animation-delay: 0.3s; }}

    .aa-footer {{
        text-align: center;
        margin-top: 0.65rem;
        padding-top: 0.55rem;
        border-top: 1px solid {c["border"]};
        animation: aa-fade-up 0.5s ease-out 0.2s both;
    }}
    .aa-footer-brand {{
        font-size: 0.72rem;
        font-weight: 600;
        color: {c["text_muted"]};
        letter-spacing: 0.04em;
    }}
    .aa-footer-powered {{
        margin-top: 0.18rem;
        font-size: 0.62rem;
        color: {c["text_dim"]};
    }}
    .aa-footer-disclaimer {{
        margin-top: 0.35rem;
        font-size: 0.58rem;
        color: {c["text_dim"]};
        line-height: 1.4;
        max-width: 520px;
        margin-left: auto;
        margin-right: auto;
    }}
    .aa-inline-warning {{
        text-align: center;
        font-size: 0.75rem;
        color: {c["gold"]};
        margin: 0.15rem 0;
    }}
    {upload_rules}
    </style>
    """
