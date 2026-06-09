"""Premium chat-only CSS for ArabArena simple chat."""

from __future__ import annotations

from workspace.ui.theme import ARABARENA_COLORS, ARABARENA_FONT, ARABARENA_GRADIENTS, ARABARENA_RADIUS


def simple_chat_css(*, show_uploads: bool = False) -> str:
    c = ARABARENA_COLORS
    g = ARABARENA_GRADIENTS
    r = ARABARENA_RADIUS
    upload_rules = ""
    if not show_uploads:
        upload_rules = """
    [data-testid="stFileUploader"] { display: none !important; }
"""
    return f"""
    <style>
    @keyframes aa-rise {{
        from {{ opacity: 0; transform: translateY(8px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}
    @keyframes aa-glow-pulse {{
        0%, 100% {{ opacity: 0.55; }}
        50% {{ opacity: 0.85; }}
    }}
    @keyframes aa-thinking-dots {{
        0%, 80%, 100% {{ opacity: 0.2; }}
        40% {{ opacity: 1; }}
    }}

    #MainMenu, footer, header {{ visibility: hidden; height: 0; }}
    [data-testid="stSidebar"], section[data-testid="stSidebar"] {{ display: none !important; }}
    [data-testid="collapsedControl"] {{ display: none !important; }}

    .stApp {{
        background: {c["bg_primary"]};
        font-family: {ARABARENA_FONT};
        color: {c["text_primary"]};
    }}
    [data-testid="stAppViewContainer"] > .main {{
        background: {c["bg_primary"]};
    }}
    .block-container {{
        padding-top: max(0.5rem, env(safe-area-inset-top));
        padding-bottom: max(0.25rem, env(safe-area-inset-bottom));
        max-width: 820px;
    }}
    [data-testid="stVerticalBlock"] {{ gap: 0.12rem; }}
    [data-testid="stVerticalBlockBorderWrapper"] {{ gap: 0.12rem; }}
    hr {{ display: none; }}

    .stButton > button[kind="primary"],
    .stFormSubmitButton > button {{
        background: {g["accent_button"]} !important;
        border: none !important;
        color: #fff !important;
    }}
    div[data-testid="stAlert"] {{ display: none !important; }}

    /* ── Brand ── */
    .aa-brand {{
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 0.5rem;
        direction: rtl;
        animation: aa-rise 0.45s ease-out;
    }}
    .aa-brand-hero {{
        margin-bottom: 0.35rem;
    }}
    .aa-brand-compact {{
        margin-bottom: 0.25rem;
        opacity: 0.92;
    }}
    .aa-brand-mark {{
        width: 0.55rem;
        height: 0.55rem;
        border-radius: 50%;
        background: {c["accent"]};
        box-shadow: 0 0 12px rgba(16,163,127,0.55);
        flex-shrink: 0;
    }}
    .aa-brand-compact .aa-brand-mark {{
        width: 0.4rem;
        height: 0.4rem;
    }}
    .aa-brand-name {{
        font-weight: 650;
        letter-spacing: -0.025em;
        color: {c["text_primary"]};
        font-size: clamp(1.5rem, 3.8vw, 2rem);
    }}
    .aa-brand-compact .aa-brand-name {{
        font-size: 0.92rem;
        font-weight: 600;
        color: {c["text_muted"]};
    }}
    .aa-brand-spark {{
        color: {c["gold"]};
        font-size: 1em;
        line-height: 1;
    }}
    .aa-brand-compact .aa-brand-spark {{
        font-size: 0.85em;
    }}

    /* ── Conversation ── */
    .aa-chat-shell {{
        width: min(100%, 780px);
        margin: 0 auto;
    }}
    .aa-thread {{
        direction: rtl;
        width: min(100%, 780px);
        margin: 0.15rem auto 0.25rem;
        max-height: calc(100vh - 210px);
        overflow-y: auto;
        scroll-behavior: smooth;
        padding: 0.1rem 0.15rem 0.35rem;
    }}
    .aa-msg-user {{
        direction: rtl;
        text-align: right;
        margin: 0.35rem 0 0.65rem;
        margin-left: auto;
        margin-right: 0;
        max-width: 82%;
        padding: 0.7rem 0.95rem;
        border-radius: 18px 18px 4px 18px;
        background: linear-gradient(135deg, rgba(16,163,127,0.18), rgba(16,163,127,0.08));
        border: 1px solid {c["accent_border"]};
        color: {c["text_primary"]};
        font-size: 0.97rem;
        line-height: 1.62;
        white-space: pre-wrap;
        animation: aa-rise 0.35s ease-out;
    }}
    .aa-msg-assistant {{
        direction: rtl;
        text-align: right;
        margin: 0 0 0.85rem;
        padding: 0.15rem 0.05rem;
        animation: aa-rise 0.4s ease-out;
    }}
    .aa-msg-assistant .stMarkdown {{
        color: {c["text_primary"]};
        font-size: 1.02rem;
        line-height: 1.88;
        letter-spacing: 0.01em;
    }}
    .aa-msg-assistant .stMarkdown p {{ margin: 0 0 0.8rem; }}
    .aa-msg-assistant .stMarkdown p:last-child {{ margin-bottom: 0; }}
    .aa-msg-assistant .stMarkdown ul,
    .aa-msg-assistant .stMarkdown ol {{
        margin: 0.35rem 0 0.8rem;
        padding-right: 1.35rem;
    }}
    .aa-msg-assistant .stMarkdown li {{ margin-bottom: 0.35rem; }}
    .aa-msg-assistant .stMarkdown li::marker {{ color: {c["accent"]}; }}
    .aa-msg-assistant .stMarkdown strong {{ color: {c["text_primary"]}; font-weight: 600; }}
    .aa-msg-assistant .stMarkdown code {{
        background: rgba(16,163,127,0.12);
        border: 1px solid rgba(16,163,127,0.2);
        border-radius: {r["sm"]};
        padding: 0.12rem 0.38rem;
        font-size: 0.9em;
    }}
    .aa-msg-assistant .stMarkdown pre {{
        background: rgba(0,0,0,0.38);
        border: 1px solid {c["border_strong"]};
        border-radius: 14px;
        padding: 0.85rem 1rem;
        overflow-x: auto;
        margin: 0.5rem 0 0.85rem;
    }}
    .aa-msg-assistant .stMarkdown pre code {{
        background: transparent;
        border: none;
        padding: 0;
    }}

    /* ── Composer spotlight (empty state) ── */
    .aa-composer-spotlight {{
        width: min(100%, 780px);
        height: 140px;
        margin: -0.5rem auto -4.5rem;
        background: radial-gradient(
            ellipse 70% 80% at 50% 75%,
            rgba(16,163,127,0.16) 0%,
            rgba(201,162,39,0.04) 35%,
            transparent 70%
        );
        pointer-events: none;
        animation: aa-glow-pulse 4s ease-in-out infinite;
    }}

    .aa-composer-stage {{
        width: min(100%, 780px);
        margin: 0 auto;
        position: relative;
        z-index: 2;
    }}
    .aa-composer-hero {{
        margin-top: clamp(1rem, 10vh, 4.5rem);
    }}

    .aa-composer {{
        padding: 1.5px;
        border-radius: 26px;
        background: {g["composer_border"]};
        box-shadow:
            0 0 0 1px rgba(16,163,127,0.12),
            0 8px 32px rgba(0,0,0,0.35),
            0 0 48px rgba(16,163,127,0.14);
        transition: box-shadow 0.28s ease, transform 0.28s ease;
    }}
    .aa-composer-hero .aa-composer {{
        box-shadow:
            0 0 0 1px rgba(16,163,127,0.18),
            0 12px 40px rgba(0,0,0,0.4),
            0 0 64px rgba(16,163,127,0.22),
            0 0 96px rgba(201,162,39,0.06);
    }}
    .aa-composer:focus-within {{
        box-shadow:
            0 0 0 1px rgba(16,163,127,0.35),
            0 10px 36px rgba(0,0,0,0.38),
            0 0 56px rgba(16,163,127,0.28);
    }}

    .aa-composer-dock {{
        position: sticky;
        bottom: 0.15rem;
        z-index: 50;
        padding-top: 0.5rem;
        background: linear-gradient(180deg, transparent 0%, {c["bg_primary"]} 42%);
    }}

    .aa-composer-inner {{
        border-radius: 24px;
        background: linear-gradient(168deg, {c["bg_elevated"]} 0%, rgba(16,20,26,0.98) 100%);
        padding: 0.55rem 0.6rem 0.55rem 0.65rem;
        box-shadow: inset 0 1px 0 rgba(255,255,255,0.04);
    }}
    .aa-composer-inner [data-testid="stForm"] {{
        border: none !important;
        padding: 0 !important;
        margin: 0 !important;
        background: transparent !important;
    }}
    .aa-composer-inner [data-testid="column"] {{
        align-items: flex-end !important;
    }}
    .aa-composer-inner textarea {{
        direction: rtl;
        border: none !important;
        background: transparent !important;
        box-shadow: none !important;
        color: {c["text_primary"]} !important;
        font-size: 1.06rem !important;
        line-height: 1.65 !important;
        min-height: 88px !important;
        max-height: 180px !important;
        padding: 0.45rem 0.5rem 0.35rem !important;
        resize: none !important;
    }}
    .aa-composer-inner textarea:focus {{
        outline: none !important;
        box-shadow: none !important;
    }}
    .aa-composer-inner textarea::placeholder {{
        color: {c["text_dim"]} !important;
        opacity: 0.9;
    }}
    .aa-composer-inner .stFormSubmitButton > button {{
        width: 2.65rem !important;
        height: 2.65rem !important;
        min-width: 2.65rem !important;
        min-height: 2.65rem !important;
        padding: 0 !important;
        border-radius: 50% !important;
        font-size: 1.15rem !important;
        font-weight: 700 !important;
        line-height: 1 !important;
        box-shadow: 0 0 20px rgba(16,163,127,0.32) !important;
        transition: transform 0.18s ease, box-shadow 0.18s ease !important;
    }}
    .aa-composer-inner .stFormSubmitButton > button:hover:not(:disabled) {{
        transform: translateY(-1px) scale(1.03);
        box-shadow: 0 0 28px rgba(16,163,127,0.42) !important;
    }}
    .aa-composer-inner .stFormSubmitButton > button:disabled {{
        opacity: 0.45 !important;
    }}

    .aa-thinking {{
        direction: rtl;
        display: inline-flex;
        align-items: center;
        gap: 0.35rem;
        margin: 0.15rem 0 0.35rem;
        color: {c["accent"]};
        font-size: 0.86rem;
    }}
    .aa-thinking-dot {{
        width: 4px;
        height: 4px;
        border-radius: 50%;
        background: {c["accent"]};
        display: inline-block;
        animation: aa-thinking-dots 1.15s infinite ease-in-out;
    }}
    .aa-thinking-dot:nth-child(2) {{ animation-delay: 0.12s; }}
    .aa-thinking-dot:nth-child(3) {{ animation-delay: 0.24s; }}

    .aa-inline-notice {{
        direction: rtl;
        text-align: center;
        font-size: 0.72rem;
        color: {c["gold"]};
        margin: 0.05rem auto 0.15rem;
        max-width: 780px;
        opacity: 0.9;
    }}
    {upload_rules}
    </style>
    """
