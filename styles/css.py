"""styles/css.py — Estilos CSS e tema da aplicação."""

import streamlit as st


def inject_css() -> None:
    """Aplica os estilos CSS personalizados à aplicação."""
    st.markdown("""
<style>
    /* ==================== RESET E CONFIGURAÇÕES GLOBAIS ==================== */
    .stApp {
        background: linear-gradient(135deg, #f8fafc 0%, #eff6ff 100%);
    }
    
    /* ==================== HERO SECTION ==================== */
    .hero-wrapper {
        text-align: center;
        padding: 2rem 1rem 1rem 1rem;
        max-width: 900px;
        margin: 0 auto;
    }
    
    /* Título principal */
    .hero-title {
        font-size: 3.8rem;
        font-weight: 800;
        color: #0f172a;
        text-align: center;
        margin-bottom: 1.25rem;
        line-height: 1.2;
        letter-spacing: -0.03em;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    /* Subtítulo */
    .hero-subtitle {
        font-size: 1.3rem;
        font-weight: 400;
        color: #475569;
        text-align: center;
        margin-bottom: 2rem;
        max-width: 550px;
        margin-left: auto;
        margin-right: auto;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        line-height: 1.5;
    }
    
    /* Divisória decorativa */
    .hero-divider {
        width: 100px;
        height: 4px;
        background: linear-gradient(90deg, #3b82f6, #8b5cf6, #ec4899);
        margin: 1.5rem auto 0;
        border-radius: 4px;
        animation: shimmer 2s infinite;
    }
    
    @keyframes shimmer {
        0% { background-position: -200% 0; }
        100% { background-position: 200% 0; }
    }
    
    /* ==================== BADGE (opcional, mantido para compatibilidade) ==================== */
    .hero-badge {
        display: inline-block;
        background: rgba(59, 130, 246, 0.1);
        backdrop-filter: blur(4px);
        padding: 0.5rem 1.25rem;
        border-radius: 40px;
        font-size: 0.85rem;
        font-weight: 500;
        color: #3b82f6;
        margin-bottom: 1.5rem;
        border: 1px solid rgba(59, 130, 246, 0.2);
        font-family: monospace;
    }
    
    /* ==================== STATS (mantido para compatibilidade) ==================== */
    .hero-stats {
        display: flex;
        justify-content: center;
        gap: 2.5rem;
        flex-wrap: wrap;
        margin: 2rem 0 1rem;
    }
    
    .hero-stat {
        text-align: center;
    }
    
    .hero-stat-number {
        display: block;
        font-size: 2rem;
        font-weight: 800;
        color: #0f172a;
        line-height: 1.2;
    }
    
    .hero-stat-label {
        display: block;
        font-size: 0.85rem;
        color: #64748b;
        font-weight: 500;
    }
    
    /* ==================== COR DE DESTAQUE (accent) ==================== */
    .accent {
        background: linear-gradient(135deg, #3b82f6, #8b5cf6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-weight: inherit;
    }
    
    /* ==================== RESPONSIVIDADE ==================== */
    @media (max-width: 768px) {
        .hero-title {
            font-size: 2.2rem;
        }
        
        .hero-subtitle {
            font-size: 1rem;
        }
        
        .hero-stats {
            gap: 1.5rem;
        }
        
        .hero-stat-number {
            font-size: 1.5rem;
        }
    }
    
    /* ==================== CARDS E OUTROS ELEMENTOS ==================== */
    .stCard {
        border-radius: 1rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    
    /* Botões personalizados */
    .stButton > button {
        border-radius: 0.75rem;
        font-weight: 600;
        transition: all 0.2s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
    }
</style>
""", unsafe_allow_html=True)
