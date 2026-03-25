"""
styles/css.py
Todo o CSS customizado da aplicação em um único lugar.
Para alterar o tema, edite apenas este arquivo.
"""

import streamlit as st

# ── Paleta de cores (referência para manutenção) ────────────────────────────
# bg_primary:   #0a0e27
# accent:       #a78bfa  (violet-400)
# accent_dark:  #7c3aed  (violet-600)
# accent_light: #c4b5fd  (violet-300)
# text_primary: #f0f4ff
# text_muted:   #7b8ba8
# text_dim:     #4a5568

_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap');

*, *::before, *::after { box-sizing: border-box; }

html, body, .main, [data-testid="stAppViewContainer"] {
    background-color: #0a0e27 !important;
}

[data-testid="stAppViewContainer"] {
    background-image:
        radial-gradient(ellipse 80% 50% at 50% -10%, rgba(139,92,246,0.12) 0%, transparent 60%),
        radial-gradient(ellipse 40% 30% at 80% 60%, rgba(59,130,246,0.08) 0%, transparent 50%);
}

[data-testid="stHeader"] { background: transparent !important; }

.main h1, .main h2, .main h3, .main h4,
.main p, .main a, .main li,
[data-testid="stAppViewContainer"] div:not([data-testid="stSidebar"]) {
    font-family: 'DM Sans', sans-serif !important;
}

[data-testid="stMarkdownContainer"] { width: 100% !important; }
.block-container {
    max-width: 100% !important;
    padding-left: 4rem !important;
    padding-right: 4rem !important;
}

/* ── SIDEBAR ── */
[data-testid="stSidebar"] {
    background: rgba(10, 14, 39, 0.95) !important;
    border-right: 1px solid rgba(167,139,250,0.15) !important;
}
[data-testid="stSidebar"] * {
    font-family: 'DM Sans', sans-serif !important;
    color: #e2e8f0 !important;
}
[data-testid="stSidebar"] .stSelectbox > div > div {
    background: rgba(255,255,255,0.03) !important;
    border: 1px solid rgba(167,139,250,0.2) !important;
    color: #e2e8f0 !important;
    border-radius: 12px !important;
}
[data-testid="stSidebar"] .stSlider > div > div > div {
    background: #a78bfa !important;
}

/* ── HERO ── */
.hero-wrapper {
    text-align: center;
    padding: 72px 20px 48px;
    width: 100%;
    display: flex;
    flex-direction: column;
    align-items: center;
}
.hero-badge {
    display: inline-block;
    font-family: 'Syne', sans-serif !important;
    font-size: 0.70rem;
    font-weight: 700;
    letter-spacing: 3px;
    text-transform: uppercase;
    color: #a78bfa;
    border: 1px solid rgba(167,139,250,0.35);
    background: rgba(167,139,250,0.07);
    padding: 6px 18px;
    border-radius: 100px;
    margin-bottom: 26px;
}
.hero-title {
    font-family: 'Syne', sans-serif !important;
    font-size: clamp(2.2rem, 4.5vw, 3.6rem);
    font-weight: 800;
    line-height: 1.08;
    letter-spacing: -1.5px;
    color: #f0f4ff;
    margin: 0 auto 18px;
    max-width: 760px;
    text-align: center;
}
.hero-title .accent {
    background: linear-gradient(135deg, #a78bfa 0%, #7c3aed 50%, #c4b5fd 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.hero-subtitle {
    font-size: 1rem;
    font-weight: 300;
    color: #7b8ba8;
    max-width: 520px;
    margin: 0 auto 44px;
    line-height: 1.75;
    text-align: center;
}
.hero-stats {
    display: flex;
    justify-content: center;
    gap: 48px;
    flex-wrap: wrap;
    margin-bottom: 52px;
}
.hero-stat { text-align: center; }
.hero-stat-number {
    font-family: 'Syne', sans-serif !important;
    font-size: 2rem;
    font-weight: 800;
    color: #a78bfa;
    display: block;
    line-height: 1;
}
.hero-stat-label {
    font-size: 0.72rem;
    color: #4a5568;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    margin-top: 6px;
    display: block;
}
.hero-divider {
    width: 100%;
    max-width: 860px;
    margin: 0 auto 52px;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(167,139,250,0.3), transparent);
}

/* ── SECTION HEADERS ── */
.section-header {
    font-family: 'Syne', sans-serif !important;
    font-size: 1.4rem;
    font-weight: 800;
    color: #f0f4ff;
    margin: 44px 0 24px;
    padding-bottom: 14px;
    border-bottom: 1px solid rgba(167,139,250,0.2);
    letter-spacing: -0.5px;
    position: relative;
}
.section-header::after {
    content: '';
    position: absolute;
    bottom: -1px;
    left: 0;
    width: 48px;
    height: 2px;
    background: #a78bfa;
}
.section-header-plain {
    font-family: 'Syne', sans-serif !important;
    font-size: 1.4rem;
    font-weight: 800;
    color: #f0f4ff;
    margin: 44px 0 24px;
    padding-bottom: 0;
    border-bottom: none;
    letter-spacing: -0.5px;
}

/* ── STAT CARDS ── */
.stat-card {
    background: linear-gradient(145deg, rgba(255,255,255,0.03) 0%, rgba(0,0,0,0.2) 100%);
    border: 1px solid rgba(167,139,250,0.2);
    border-radius: 18px;
    padding: 28px 22px;
    text-align: center;
    position: relative;
    overflow: hidden;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}
.stat-card:hover {
    transform: translateY(-4px);
    border-color: rgba(167,139,250,0.4);
    box-shadow: 0 20px 40px rgba(0,0,0,0.4);
}
.stat-card-icon { font-size: 1.8rem; margin-bottom: 10px; display: block; }
.stat-number {
    font-family: 'Syne', sans-serif !important;
    font-size: 1.4rem;
    font-weight: 800;
    color: #a78bfa;
    margin-bottom: 6px;
    line-height: 1;
    display: block;
    white-space: nowrap;
}
.stat-label {
    font-family: 'Syne', sans-serif !important;
    font-size: 0.72rem;
    font-weight: 700;
    color: #e2e8f0;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    display: block;
}
.stat-sublabel {
    font-size: 0.78rem;
    color: #4a5568;
    margin-top: 6px;
    font-weight: 300;
    display: block;
}

/* ── SECTOR CARDS (flip 3D) ── */
.sector-grid {
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 12px;
    margin: 20px 0;
}
.flip-wrapper {
    perspective: 800px;
    height: 120px;
    cursor: default;
}
.flip-inner {
    position: relative;
    width: 100%;
    height: 100%;
    transform-style: preserve-3d;
    transition: transform 0.55s cubic-bezier(0.4, 0, 0.2, 1);
}
.flip-wrapper:hover .flip-inner { transform: rotateY(180deg); }
.flip-front, .flip-back {
    position: absolute;
    inset: 0;
    border-radius: 14px;
    backface-visibility: hidden;
    -webkit-backface-visibility: hidden;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 14px 12px;
    text-align: center;
}
.flip-front {
    background: linear-gradient(145deg, rgba(255,255,255,0.03) 0%, rgba(0,0,0,0.2) 100%);
    border: 1px solid rgba(167,139,250,0.18);
    transition: border-color 0.3s;
}
.flip-wrapper:hover .flip-front { border-color: rgba(167,139,250,0.0); }
.flip-back {
    background: linear-gradient(145deg, rgba(167,139,250,0.18) 0%, rgba(124,58,237,0.12) 100%);
    border: 1px solid rgba(167,139,250,0.45);
    transform: rotateY(180deg);
}
.sector-card-icon { font-size: 1.6rem; display: block; margin-bottom: 8px; line-height: 1; }
.sector-card-name {
    font-family: 'Syne', sans-serif !important;
    font-size: 0.8rem;
    font-weight: 700;
    color: #e2e8f0;
}
.flip-back-title {
    font-family: 'Syne', sans-serif !important;
    font-size: 0.76rem;
    font-weight: 700;
    color: #c4b5fd;
    margin-bottom: 7px;
    letter-spacing: 0.2px;
}
.flip-back-desc { font-size: 0.72rem; color: #a78bfa; line-height: 1.55; font-weight: 300; }

/* ── STEPS ── */
.steps-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 16px;
    margin: 20px 0;
}
.step-card {
    background: linear-gradient(145deg, rgba(255,255,255,0.03) 0%, rgba(0,0,0,0.2) 100%);
    border: 1px solid rgba(167,139,250,0.18);
    border-radius: 16px;
    padding: 24px 20px;
    text-align: center;
    transition: all 0.3s ease;
}
.step-card:hover {
    border-color: rgba(167,139,250,0.4);
    box-shadow: 0 12px 32px rgba(0,0,0,0.3);
}
.step-num {
    font-family: 'Syne', sans-serif !important;
    font-size: 0.65rem;
    font-weight: 700;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: #a78bfa;
    background: rgba(167,139,250,0.1);
    border: 1px solid rgba(167,139,250,0.2);
    border-radius: 100px;
    padding: 3px 12px;
    display: inline-block;
    margin-bottom: 14px;
}
.step-icon { font-size: 1.8rem; display: block; margin-bottom: 10px; }
.step-title {
    font-family: 'Syne', sans-serif !important;
    font-size: 0.9rem;
    font-weight: 700;
    color: #f0f4ff;
    margin-bottom: 8px;
}
.step-text { font-size: 0.78rem; color: #7b8ba8; line-height: 1.6; font-weight: 300; }

/* ── INFO / SUCCESS BOXES ── */
.info-box {
    background: linear-gradient(145deg, rgba(167,139,250,0.08) 0%, rgba(124,58,237,0.05) 100%);
    border: 1px solid rgba(167,139,250,0.25);
    border-radius: 14px;
    padding: 18px 22px;
    margin: 20px 0;
    font-size: 0.88rem;
    color: #c4b5fd;
    line-height: 1.7;
}
.info-box strong { color: #a78bfa; }
.success-box {
    background: linear-gradient(145deg, rgba(34,197,94,0.08) 0%, rgba(34,197,94,0.04) 100%);
    border: 1px solid rgba(34,197,94,0.25);
    border-radius: 14px;
    padding: 16px 20px;
    font-size: 0.9rem;
    color: #86efac;
    margin: 16px 0;
}

/* ── INPUTS ── */
.stSelectbox > div > div {
    background: rgba(255,255,255,0.03) !important;
    border: 1px solid rgba(167,139,250,0.2) !important;
    color: #e2e8f0 !important;
    border-radius: 12px !important;
}
.stDateInput > div > div {
    background: rgba(255,255,255,0.03) !important;
    border: 1px solid rgba(167,139,250,0.2) !important;
    border-radius: 12px !important;
}
hr {
    border: none !important;
    border-top: 1px solid rgba(167,139,250,0.1) !important;
    margin: 36px 0 !important;
}

/* ── TABS ── */
.stTabs [data-baseweb="tab-list"] {
    background: transparent !important;
    border-bottom: 1px solid rgba(167,139,250,0.2) !important;
    gap: 4px;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: #7b8ba8 !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.82rem !important;
    letter-spacing: 0.5px;
    border-radius: 8px 8px 0 0 !important;
    padding: 10px 20px !important;
    transition: color 0.2s, background 0.2s;
}
.stTabs [aria-selected="true"] {
    background: rgba(167,139,250,0.1) !important;
    color: #a78bfa !important;
    border-bottom: 2px solid #a78bfa !important;
}

/* ── DATAFRAME ── */
.stDataFrame {
    border: 1px solid rgba(167,139,250,0.2) !important;
    border-radius: 12px !important;
}

/* ── BOTÃO COLAPSAR SIDEBAR ── */
@import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@24,400,0,0');
span[data-testid="stIconMaterial"] {
    font-size: 0 !important; line-height: 0 !important;
    display: inline-block !important; width: 24px !important; height: 24px !important;
    position: relative !important;
}
span[data-testid="stIconMaterial"]::before {
    font-family: 'Material Symbols Rounded' !important;
    font-size: 24px !important; line-height: 24px !important;
    color: #a78bfa !important; position: absolute !important;
    top: 0; left: 0 !important; content: "\\eac3" !important;
}
[data-testid="stSidebarCollapsedControl"] span[data-testid="stIconMaterial"]::before,
[data-testid="stHeader"] span[data-testid="stIconMaterial"]::before {
    content: "\\eac9" !important;
}
button[data-testid="stBaseButton-headerNoPadding"],
[data-testid="stSidebarCollapsedControl"] button {
    background: rgba(167,139,250,0.08) !important;
    border: 1px solid rgba(167,139,250,0.2) !important;
    border-radius: 8px !important;
}
button[data-testid="stBaseButton-headerNoPadding"]:hover,
[data-testid="stSidebarCollapsedControl"] button:hover {
    background: rgba(167,139,250,0.18) !important;
    border-color: rgba(167,139,250,0.4) !important;
}

/* ── SLIDER — esconde input numérico e tickbar ── */
[data-testid="stSidebar"] [data-testid="stSlider"] input[type="number"],
[data-testid="stSliderTickBar"] { display: none !important; }

/* ── Remove borda superior nativa dos blocos de coluna ── */
[data-testid="stVerticalBlockBorderWrapper"],
[data-testid="stVerticalBlockBorderWrapper"] > div,
[data-testid="column"] > div:first-child {
    border-top: none !important;
    box-shadow: none !important;
    outline: none !important;
}

/* ── SCROLLBAR ── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: #0a0e27; }
::-webkit-scrollbar-thumb { background: rgba(167,139,250,0.2); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: rgba(167,139,250,0.4); }

/* ── BUTTONS ── */
.stButton > button {
    background: linear-gradient(135deg, #7c3aed, #a78bfa) !important;
    color: #fff !important; border: none !important; border-radius: 12px !important;
    font-family: 'Syne', sans-serif !important; font-weight: 700 !important;
    font-size: 0.88rem !important; padding: 10px 22px !important;
    transition: transform 0.2s, box-shadow 0.2s !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 24px rgba(124,58,237,0.4) !important;
}
.stDownloadButton > button {
    background: linear-gradient(135deg, #7c3aed, #a78bfa) !important;
    color: #fff !important; border: none !important; border-radius: 12px !important;
    font-family: 'Syne', sans-serif !important; font-weight: 700 !important;
    font-size: 0.9rem !important; margin-top: 8px !important;
    transition: transform 0.2s, box-shadow 0.2s !important;
}
.stDownloadButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 28px rgba(124,58,237,0.45) !important;
}
</style>
"""


def inject_css() -> None:
    """Injeta o CSS customizado na página Streamlit."""
    st.markdown(_CSS, unsafe_allow_html=True)
