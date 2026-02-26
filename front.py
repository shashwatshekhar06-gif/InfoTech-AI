import streamlit as st

# CRITICAL: FIRST COMMAND - Must be before ANY other streamlit command
st.set_page_config(
    page_title="InfoFetch AI - Intelligent Research Assistant",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Imports AFTER set_page_config
import json
import time
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import custom modules
from serp import run_research_agent, get_chat_response, OPENAI_AVAILABLE, SERPAPI_AVAILABLE, display_company_results
from db_utils import *
from razorpay_handler import create_razorpay_order, RAZORPAY_AVAILABLE, PLAN_PRICING

# ============================================================================
# PREMIUM PROFESSIONAL CSS - BOARD-READY DESIGN
# ============================================================================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=Space+Grotesk:wght@400;500;600;700&display=swap');

/* ============================================================================
   STREAMLIT LAYOUT OVERRIDES
   ============================================================================ */
.main > div {
    padding-top: 0rem !important;
}

.main .block-container {
    padding-top: 0rem !important;
    padding-bottom: 0rem !important;
}

section[data-testid="stVerticalBlock"] > div {
    gap: 0rem !important;
}

/* ============================================================================
   GLOBAL PREMIUM THEME
   ============================================================================ */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

html, body, .stApp {
    background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0f172a 100%) !important;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    color: #f1f5f9;
}

/* Remove Streamlit branding */
#MainMenu, footer, header, .stDeployButton, 
[data-testid="stToolbar"], [data-testid="stDecoration"] {
    display: none !important;
}

.stApp > header {
    background-color: transparent !important;
}

/* ============================================================================
   PROFESSIONAL NAVIGATION
   ============================================================================ */
.logo-text {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.75rem;
    font-weight: 700;
    background: linear-gradient(135deg, #3b82f6 0%, #06b6d4 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    letter-spacing: -0.5px;
}

/* ============================================================================
   HERO SECTION WITH BACKGROUND IMAGE
   ============================================================================ */
.hero-with-image {
    position: relative;
    min-height: 600px;
    display: flex;
    align-items: center;
    justify-content: center;
    overflow: hidden;
    margin-bottom: 4rem;
}

.hero-background {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: linear-gradient(135deg, rgba(15, 23, 42, 0.50) 0%, rgba(30, 41, 59, 0.55) 100%),
                url('https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=1920&q=80') center/cover;
    z-index: 1;
    filter: brightness(0.9);
}

.hero-background::after {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: radial-gradient(ellipse at center, transparent 0%, rgba(15, 23, 42, 0.4) 100%);
    z-index: 2;
}

.hero-content-overlay {
    position: relative;
    z-index: 10;
    text-align: center;
    padding: 4rem 2rem;
    max-width: 1000px;
}

.badge-professional {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.6rem 1.2rem;
    background: rgba(59, 130, 246, 0.15);
    border: 1px solid rgba(59, 130, 246, 0.3);
    border-radius: 50px;
    color: #93c5fd;
    font-size: 0.875rem;
    font-weight: 600;
    margin-bottom: 2rem;
    letter-spacing: 0.5px;
}

.hero-title-pro {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 3.5rem;
    font-weight: 700;
    line-height: 1.15;
    margin-bottom: 1.5rem;
    background: linear-gradient(135deg, #ffffff 0%, #93c5fd 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    letter-spacing: -1.5px;
}

.hero-subtitle-pro {
    font-size: 1.15rem;
    color: #cbd5e1;
    line-height: 1.7;
    max-width: 600px;
    margin: 0 auto 2.5rem;
    font-weight: 400;
    text-align: center;
}

/* ============================================================================
   MODERN FEATURE CARDS
   ============================================================================ */
.features-container-pro {
    max-width: 1200px;
    margin: 4rem auto;
    padding: 0 2rem;
}

.section-title-pro {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 2.25rem;
    font-weight: 700;
    text-align: center;
    margin-bottom: 1rem;
    background: linear-gradient(135deg, #ffffff 0%, #93c5fd 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.section-desc-pro {
    text-align: center;
    color: #94a3b8;
    font-size: 1rem;
    margin-bottom: 3rem;
}

.feature-grid-pro {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 1.5rem;
    margin-top: 2rem;
}

.feature-card-pro {
    background: rgba(30, 41, 59, 0.6);
    border: 1px solid rgba(59, 130, 246, 0.15);
    border-radius: 16px;
    padding: 2rem;
    transition: all 0.3s ease;
    backdrop-filter: blur(10px);
}

.feature-card-pro:hover {
    transform: translateY(-5px);
    border-color: rgba(59, 130, 246, 0.4);
    box-shadow: 0 12px 48px rgba(59, 130, 246, 0.15);
}

.feature-icon-pro {
    font-size: 2.5rem;
    margin-bottom: 1rem;
    display: block;
}

.feature-title-pro {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.25rem;
    font-weight: 600;
    color: #f1f5f9;
    margin-bottom: 0.75rem;
}

.feature-desc-pro {
    color: #cbd5e1;
    line-height: 1.6;
    font-size: 0.95rem;
}

/* ============================================================================
   PROFESSIONAL STATS SECTION
   ============================================================================ */
.stats-container-pro {
    max-width: 1000px;
    margin: 4rem auto;
    padding: 3rem 2rem;
    background: rgba(30, 41, 59, 0.4);
    border-radius: 20px;
    border: 1px solid rgba(59, 130, 246, 0.1);
}

.stats-grid-pro {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 2rem;
    text-align: center;
}

.stat-number-pro {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 2.5rem;
    font-weight: 700;
    color: #3b82f6;
    margin-bottom: 0.5rem;
}

.stat-label-pro {
    color: #94a3b8;
    font-size: 0.95rem;
    font-weight: 500;
}

/* ============================================================================
   REVIEWS SECTION - LANDING PAGE
   ============================================================================ */
.reviews-section {
    max-width: 1200px;
    margin: 5rem auto 3rem;
    padding: 0 2rem;
}

.review-card-landing {
    background: rgba(15, 23, 42, 0.8);
    border: 1px solid rgba(59, 130, 246, 0.2);
    border-radius: 20px;
    padding: 2rem;
    height: 100%;
    min-height: 260px;
    position: relative;
    transition: all 0.35s ease;
    backdrop-filter: blur(12px);
    overflow: hidden;
}

.review-card-landing::before {
    content: '"';
    position: absolute;
    top: -10px;
    left: 20px;
    font-size: 7rem;
    color: rgba(59, 130, 246, 0.08);
    font-family: Georgia, serif;
    line-height: 1;
    pointer-events: none;
}

.review-card-landing:hover {
    transform: translateY(-6px);
    border-color: rgba(59, 130, 246, 0.45);
    box-shadow: 0 16px 48px rgba(59, 130, 246, 0.18);
}

.review-avatar {
    width: 48px;
    height: 48px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.4rem;
    font-weight: 700;
    margin-bottom: 1rem;
    flex-shrink: 0;
}

.review-header-row {
    display: flex;
    align-items: center;
    gap: 1rem;
    margin-bottom: 1rem;
}

.review-meta {
    flex: 1;
}

.review-name {
    font-family: 'Space Grotesk', sans-serif;
    font-weight: 600;
    font-size: 1rem;
    color: #f1f5f9;
    margin-bottom: 0.15rem;
}

.review-role {
    font-size: 0.78rem;
    color: #64748b;
    font-weight: 400;
}

.review-stars {
    font-size: 0.9rem;
    letter-spacing: 1px;
    margin-bottom: 0.85rem;
}

.review-text-landing {
    color: #cbd5e1;
    line-height: 1.7;
    font-size: 0.93rem;
    font-style: italic;
}

.review-date-badge {
    display: inline-block;
    margin-top: 1rem;
    padding: 0.2rem 0.75rem;
    background: rgba(59, 130, 246, 0.1);
    border-radius: 20px;
    font-size: 0.75rem;
    color: #3b82f6;
    font-weight: 500;
}

/* ============================================================================
   FEEDBACK PAGE STYLES
   ============================================================================ */
.feedback-hero {
    background: linear-gradient(135deg, rgba(59, 130, 246, 0.15) 0%, rgba(6, 182, 212, 0.1) 100%);
    border: 1px solid rgba(59, 130, 246, 0.2);
    border-radius: 24px;
    padding: 3rem 2rem;
    text-align: center;
    margin-bottom: 2.5rem;
}

.feedback-section-card {
    background: rgba(30, 41, 59, 0.5);
    border: 1px solid rgba(59, 130, 246, 0.12);
    border-radius: 18px;
    padding: 2rem;
    margin-bottom: 1.5rem;
    backdrop-filter: blur(8px);
}

.feedback-section-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.1rem;
    font-weight: 600;
    color: #93c5fd;
    margin-bottom: 1.25rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.emoji-rating-container {
    display: flex;
    gap: 1rem;
    justify-content: center;
    flex-wrap: wrap;
    padding: 0.5rem;
}

.emoji-rating-btn {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 1rem 1.25rem;
    background: rgba(30, 41, 59, 0.8);
    border: 2px solid rgba(59, 130, 246, 0.15);
    border-radius: 16px;
    cursor: pointer;
    transition: all 0.2s ease;
    min-width: 80px;
}

.emoji-rating-btn:hover {
    border-color: rgba(59, 130, 246, 0.5);
    background: rgba(59, 130, 246, 0.1);
    transform: scale(1.08);
}

.emoji-rating-btn.selected {
    border-color: #3b82f6;
    background: rgba(59, 130, 246, 0.2);
    box-shadow: 0 0 20px rgba(59, 130, 246, 0.3);
}

.pulse-dot {
    display: inline-block;
    width: 10px;
    height: 10px;
    border-radius: 50%;
    background: #22c55e;
    animation: pulse 2s infinite;
    margin-right: 8px;
}

@keyframes pulse {
    0% { box-shadow: 0 0 0 0 rgba(34, 197, 94, 0.4); }
    70% { box-shadow: 0 0 0 8px rgba(34, 197, 94, 0); }
    100% { box-shadow: 0 0 0 0 rgba(34, 197, 94, 0); }
}

.progress-bar-container {
    background: rgba(30, 41, 59, 0.8);
    border-radius: 10px;
    height: 8px;
    overflow: hidden;
    margin-top: 0.5rem;
}

.progress-bar-fill {
    height: 100%;
    border-radius: 10px;
    background: linear-gradient(90deg, #3b82f6, #06b6d4);
    transition: width 0.5s ease;
}

.tag-chip {
    display: inline-block;
    padding: 0.35rem 0.85rem;
    border-radius: 20px;
    font-size: 0.82rem;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s;
    border: 1px solid transparent;
    margin: 0.2rem;
}

.tag-chip-default {
    background: rgba(30, 41, 59, 0.9);
    border-color: rgba(59, 130, 246, 0.2);
    color: #94a3b8;
}

.tag-chip-selected {
    background: rgba(59, 130, 246, 0.2);
    border-color: #3b82f6;
    color: #93c5fd;
}

.submit-feedback-btn {
    background: linear-gradient(135deg, #3b82f6, #06b6d4) !important;
    color: white !important;
    border: none !important;
    padding: 1rem 3rem !important;
    border-radius: 14px !important;
    font-size: 1.1rem !important;
    font-weight: 700 !important;
    width: 100%;
    cursor: pointer;
    box-shadow: 0 8px 24px rgba(59, 130, 246, 0.35) !important;
    transition: all 0.3s ease !important;
}

.success-feedback-banner {
    background: linear-gradient(135deg, rgba(34, 197, 94, 0.2), rgba(16, 185, 129, 0.15));
    border: 1px solid rgba(34, 197, 94, 0.4);
    border-radius: 20px;
    padding: 3rem 2rem;
    text-align: center;
}

/* ============================================================================
   PROFESSIONAL BUTTONS
   ============================================================================ */
.stButton > button {
    background: linear-gradient(135deg, #3b82f6, #2563eb) !important;
    color: #fff !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-family: 'Inter', sans-serif !important;
    border: none !important;
    padding: 0.6rem 0.5rem !important;
    transition: all 0.7s cubic-bezier(0.25, 0.46, 0.45, 0.94) !important;
    box-shadow: 0 4px 14px rgba(59, 130, 246, 0.25) !important;
    font-size: 0.85rem !important;
    white-space: nowrap !important;
    cursor: pointer !important;
    will-change: transform, box-shadow !important;
}

.stButton > button:hover {
    transform: translateY(-3px) scale(1.05) !important;
    box-shadow: 0 10px 32px rgba(59, 130, 246, 0.55), 
                0 5px 15px rgba(59, 130, 246, 0.3) !important;
    background: linear-gradient(135deg, #4a8ef6, #2d6beb) !important;
    filter: brightness(1.06) saturate(1.1) !important;
}

.stButton > button:active {
    transform: translateY(-1px) scale(1.02) !important;
    transition: all 0.1s ease !important;
}
            
/* ============================================================================
   PROFESSIONAL INPUTS
   ============================================================================ */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea {
    background: rgba(30, 41, 59, 0.7) !important;
    border: 1px solid rgba(59, 130, 246, 0.2) !important;
    border-radius: 10px !important;
    color: #f1f5f9 !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.85rem !important;
    white-space: nowrap !important;
    padding: 0.875rem 1rem !important;
}

.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: #3b82f6 !important;
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.15) !important;
}

/* Slider styling */
.stSlider > div > div > div {
    color: #3b82f6 !important;
}

/* Radio and checkbox */
.stRadio > div {
    gap: 0.5rem !important;
}

.stRadio label, .stCheckbox label {
    color: #cbd5e1 !important;
    font-size: 0.85rem !important;
    white-space: nowrap !important;
}

/* Select box */
.stSelectbox > div > div {
    background: rgba(30, 41, 59, 0.7) !important;
    border: 1px solid rgba(59, 130, 246, 0.2) !important;
    border-radius: 10px !important;
    color: #f1f5f9 !important;
}

/* ============================================================================
   PROFESSIONAL ALERTS
   ============================================================================ */
.stSuccess {
    background: rgba(34, 197, 94, 0.1) !important;
    border-left: 4px solid #22c55e !important;
    border-radius: 10px !important;
    color: #86efac !important;
}

.stError {
    background: rgba(239, 68, 68, 0.1) !important;
    border-left: 4px solid #ef4444 !important;
    border-radius: 10px !important;
    color: #fca5a5 !important;
}

.stWarning {
    background: rgba(245, 158, 11, 0.1) !important;
    border-left: 4px solid #f59e0b !important;
    border-radius: 10px !important;
    color: #fcd34d !important;
}

.stInfo {
    background: rgba(59, 130, 246, 0.1) !important;
    border-left: 4px solid #3b82f6 !important;
    border-radius: 10px !important;
    color: #93c5fd !important;
}

/* ============================================================================
   PROFESSIONAL METRICS
   ============================================================================ */
[data-testid="stMetricValue"] {
    font-family: 'Space Grotesk', sans-serif !important;
    font-size: 2rem !important;
    color: #3b82f6 !important;
    font-weight: 700;
}

[data-testid="stMetricLabel"] {
    font-family: 'Inter', sans-serif !important;
    color: #94a3b8 !important;
    font-weight: 500;
    font-size: 0.875rem;
}

/* ============================================================================
   PROFESSIONAL CONTAINERS
   ============================================================================ */
.professional-card {
    background: rgba(30, 41, 59, 0.6);
    border: 1px solid rgba(59, 130, 246, 0.15);
    border-radius: 16px;
    padding: 2rem;
    margin: 1.5rem 0;
    box-shadow: 0 4px 24px rgba(0, 0, 0, 0.2);
    backdrop-filter: blur(10px);
}

.main-content-pro {
    max-width: 1400px;
    margin: 2rem auto;
    padding: 0 2rem;
}

.page-title-pro {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 2.5rem;
    font-weight: 700;
    text-align: center;
    margin-bottom: 1rem;
    background: linear-gradient(135deg, #3b82f6, #06b6d4);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.page-subtitle-pro {
    text-align: center;
    color: #94a3b8;
    font-size: 1rem;
    margin-bottom: 2.5rem;
}

/* ============================================================================
   PAYMENT MODAL STYLES
   ============================================================================ */
.payment-modal {
    background: rgba(15, 23, 42, 0.98);
    border: 2px solid rgba(59, 130, 246, 0.3);
    border-radius: 20px;
    padding: 2.5rem;
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
    max-width: 500px;
    margin: 2rem auto;
}

.payment-header {
    text-align: center;
    margin-bottom: 2rem;
}

.payment-amount {
    font-size: 3rem;
    font-weight: 700;
    color: #3b82f6;
    font-family: 'Space Grotesk', sans-serif;
}

.payment-plan-name {
    font-size: 1.5rem;
    color: #93c5fd;
    margin-top: 0.5rem;
}

.payment-features {
    background: rgba(59, 130, 246, 0.1);
    border-radius: 12px;
    padding: 1.5rem;
    margin: 1.5rem 0;
}

.payment-feature {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    margin: 0.75rem 0;
    color: #cbd5e1;
}

/* ============================================================================
   FOOTER
   ============================================================================ */
.footer-pro {
    text-align: center;
    padding: 3rem 2rem 2rem;
    margin-top: 5rem;
    border-top: 1px solid rgba(59, 130, 246, 0.15);
    color: #64748b;
    font-size: 0.875rem;
}

/* ============================================================================
   RESPONSIVE DESIGN
   ============================================================================ */
@media (max-width: 768px) {
    .hero-title-pro {
        font-size: 2.25rem;
    }
    
    .hero-subtitle-pro {
        font-size: 1rem;
    }
    
    .feature-grid-pro {
        grid-template-columns: 1fr;
    }
}

/* ============================================================================
   SCROLLBAR
   ============================================================================ */
::-webkit-scrollbar {
    width: 10px;
}

::-webkit-scrollbar-track {
    background: #1e293b;
}

::-webkit-scrollbar-thumb {
    background: linear-gradient(180deg, #3b82f6, #2563eb);
    border-radius: 5px;
}

::-webkit-scrollbar-thumb:hover {
    background: linear-gradient(180deg, #2563eb, #1d4ed8);
}
</style>
""", unsafe_allow_html=True)

# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================

if 'loggedin' not in st.session_state:
    st.session_state.loggedin = False
if 'userid' not in st.session_state:
    st.session_state.userid = None
if 'username' not in st.session_state:
    st.session_state.username = 'Guest'
if 'user_plan' not in st.session_state:
    st.session_state.user_plan = 'Free'
if 'page' not in st.session_state:
    st.session_state.page = 'Home'
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'research_results' not in st.session_state:
    st.session_state.research_results = None
if 'show_login_modal' not in st.session_state:
    st.session_state.show_login_modal = False
if 'show_payment_modal' not in st.session_state:
    st.session_state.show_payment_modal = False
if 'selected_plan' not in st.session_state:
    st.session_state.selected_plan = None
if 'payment_order' not in st.session_state:
    st.session_state.payment_order = None
if 'feedback_submitted' not in st.session_state:
    st.session_state.feedback_submitted = False

# Sync user plan from database on login
if st.session_state.loggedin and st.session_state.userid:
    current_plan = get_user_plan(st.session_state.userid)
    if current_plan != st.session_state.user_plan:
        st.session_state.user_plan = current_plan

# ============================================================================
# PROFESSIONAL LANDING PAGE COMPONENTS
# ============================================================================

def render_professional_navbar():
    """Render professional navigation bar"""
    st.markdown('<div style="margin-top: -2rem;"></div>', unsafe_allow_html=True)
    
    col_logo, col_space, col_signin = st.columns([3, 6, 1.2])
    
    with col_logo:
        st.markdown('<div style="padding: 0.5rem 0;"><span style="font-size: 1.75rem;">🔍</span> <span class="logo-text">InfoFetch AI</span></div>', unsafe_allow_html=True)
    
    with col_signin:
        if st.button("Sign In", key="landing_signin", use_container_width=True):
            st.session_state.show_login_modal = True
            st.rerun()


def render_professional_hero():
    """Render professional hero section with background image"""
    st.markdown("""
    <div class="hero-with-image">
        <div class="hero-background"></div>
        <div class="hero-content-overlay">
            <div class="badge-professional">
                <span>✨</span>
                <span>AI-Powered Research Platform</span>
            </div>
            <h1 class="hero-title-pro">
                Research Smarter,<br>Decide Faster
            </h1>
            <p class="hero-subtitle-pro" style="text-align: center; color: #e2e8f0; margin-bottom: 3rem;">
                Empower your team with AI-driven company insights, competitive intelligence, 
                and market research. Built for professionals who demand excellence.
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3, col4, col5 = st.columns([2, 1.5, 0.5, 1.5, 2])
    
    with col2:
        if st.button("🚀 Start Free Trial", key="hero_cta_start", use_container_width=True, type="primary"):
            st.session_state.show_login_modal = True
            st.rerun()
    
    with col4:
        if st.button("📊 View Demo", key="hero_cta_demo", use_container_width=True):
            st.info("Demo credentials: admin / secure123")


def render_professional_features():
    """Render professional features section"""
    st.markdown("""
    <div class="features-container-pro">
        <h2 class="section-title-pro">Enterprise-Grade Research Tools</h2>
        <p class="section-desc-pro">
            Trusted by leading organizations for strategic decision-making
        </p>
        <div class="feature-grid-pro">
            <div class="feature-card-pro">
                <span class="feature-icon-pro">🏢</span>
                <h3 class="feature-title-pro">Company Intelligence</h3>
                <p class="feature-desc-pro">
                    Deep market analysis, competitive positioning, financial health, 
                    and talent acquisition insights.
                </p>
            </div>
            <div class="feature-card-pro">
                <span class="feature-icon-pro">⚡</span>
                <h3 class="feature-title-pro">Real-Time Data</h3>
                <p class="feature-desc-pro">
                    Access to 50+ premium sources with sub-second response times. 
                    Always current, always accurate.
                </p>
            </div>
            <div class="feature-card-pro">
                <span class="feature-icon-pro">🔒</span>
                <h3 class="feature-title-pro">Enterprise Security</h3>
                <p class="feature-desc-pro">
                    SOC 2 compliant, end-to-end encryption, and role-based access 
                    control for your sensitive data.
                </p>
            </div>
            <div class="feature-card-pro">
                <span class="feature-icon-pro">📊</span>
                <h3 class="feature-title-pro">Advanced Analytics</h3>
                <p class="feature-desc-pro">
                    AI-powered insights with customizable dashboards, automated 
                    reporting, and export capabilities.
                </p>
            </div>
            <div class="feature-card-pro">
                <span class="feature-icon-pro">🤝</span>
                <h3 class="feature-title-pro">Team Collaboration</h3>
                <p class="feature-desc-pro">
                    Share research, annotate findings, and collaborate seamlessly 
                    across departments.
                </p>
            </div>
            <div class="feature-card-pro">
                <span class="feature-icon-pro">🎯</span>
                <h3 class="feature-title-pro">API Integration</h3>
                <p class="feature-desc-pro">
                    RESTful API for seamless integration with your existing 
                    workflow and business intelligence tools.
                </p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_professional_stats():
    """Render professional statistics section"""
    st.markdown("""
    <div class="stats-container-pro">
        <div class="stats-grid-pro">
            <div>
                <div class="stat-number-pro">500+</div>
                <div class="stat-label-pro">Enterprise Clients</div>
            </div>
            <div>
                <div class="stat-number-pro">10M+</div>
                <div class="stat-label-pro">Searches Completed</div>
            </div>
            <div>
                <div class="stat-number-pro">99.9%</div>
                <div class="stat-label-pro">Uptime SLA</div>
            </div>
            <div>
                <div class="stat-number-pro">24/7</div>
                <div class="stat-label-pro">Support Available</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_customer_reviews():
    """Render beautiful customer reviews section on the landing page"""

    # Fetch from DB, fallback to curated defaults
    db_reviews = get_public_feedback(6)

    default_reviews = [
        {
            'username': 'Sarah Chen',
            'role': 'Product Manager · Fintech',
            'avatar': 'SC',
            'avatar_color': 'linear-gradient(135deg,#3b82f6,#06b6d4)',
            'rating': 5,
            'text': 'InfoFetch AI completely transformed how our team conducts market research. The AI-powered insights are strikingly accurate and save us 6+ hours every week. Absolute game-changer.',
            'date': 'Feb 15, 2026',
        },
        {
            'username': 'Michael Roberts',
            'role': 'Business Analyst · Consulting',
            'avatar': 'MR',
            'avatar_color': 'linear-gradient(135deg,#8b5cf6,#ec4899)',
            'rating': 5,
            'text': 'The dual research modes are brilliant. Company research gives me contacts, salaries, culture — all in one place. I used to cobble this together from 5 different tools.',
            'date': 'Feb 14, 2026',
        },
        {
            'username': 'Priya Sharma',
            'role': 'Senior Recruiter · Tech',
            'avatar': 'PS',
            'avatar_color': 'linear-gradient(135deg,#f59e0b,#ef4444)',
            'rating': 5,
            'text': 'As a recruiter this tool is invaluable. I can research companies, find live hiring trends, and get salary benchmarks in minutes. Worth every rupee of the Premium plan.',
            'date': 'Feb 13, 2026',
        },
        {
            'username': 'David Kim',
            'role': 'Venture Analyst · VC Firm',
            'avatar': 'DK',
            'avatar_color': 'linear-gradient(135deg,#10b981,#3b82f6)',
            'rating': 5,
            'text': "Impressed by both speed and accuracy. The AI chatbot handles quick questions instantly, and the deep-research mode gives me institutional-quality company profiles.",
            'date': 'Feb 12, 2026',
        },
        {
            'username': 'Emma Williams',
            'role': 'Data Scientist · E-commerce',
            'avatar': 'EW',
            'avatar_color': 'linear-gradient(135deg,#06b6d4,#8b5cf6)',
            'rating': 5,
            'text': 'The structured JSON output is a data-scientist\'s dream. No messy HTML scraping — everything is clean, typed, and ready to pipe into my analytics pipeline.',
            'date': 'Feb 11, 2026',
        },
        {
            'username': 'Alex Johnson',
            'role': 'Strategy Lead · SaaS',
            'avatar': 'AJ',
            'avatar_color': 'linear-gradient(135deg,#ec4899,#f59e0b)',
            'rating': 5,
            'text': 'The confidence scoring helps me calibrate trust in results instantly. Persistent history means I never lose important research mid-project. Highly recommend.',
            'date': 'Feb 10, 2026',
        },
    ]

    # Merge DB reviews with defaults (DB reviews take priority)
    if db_reviews:
        merged = []
        for r in db_reviews:
            merged.append({
                'username': r['username'],
                'role': 'Verified User',
                'avatar': r['username'][:2].upper(),
                'avatar_color': 'linear-gradient(135deg,#3b82f6,#06b6d4)',
                'rating': r['rating'],
                'text': r['text'],
                'date': r['date'][:10] if r.get('date') else 'Recently',
            })
        # Pad with defaults if fewer than 6
        for d in default_reviews:
            if len(merged) >= 6:
                break
            merged.append(d)
        reviews_to_show = merged[:6]
    else:
        reviews_to_show = default_reviews

    # Section header
    st.markdown("""
    <div class="reviews-section">
        <h2 class="section-title-pro" style="margin-bottom:0.5rem;">Loved by Professionals</h2>
        <p class="section-desc-pro" style="margin-bottom:2.5rem;">
            Real stories from people who research smarter every day
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Row 1 — 3 cards
    cols1 = st.columns(3, gap="medium")
    for idx in range(3):
        r = reviews_to_show[idx]
        stars_html = "⭐" * r['rating']
        with cols1[idx]:
            st.markdown(f"""
            <div class="review-card-landing">
                <div class="review-header-row">
                    <div class="review-avatar" style="background:{r['avatar_color']};color:#fff;">
                        {r['avatar']}
                    </div>
                    <div class="review-meta">
                        <div class="review-name">{r['username']}</div>
                        <div class="review-role">{r['role']}</div>
                    </div>
                </div>
                <div class="review-stars">{stars_html}</div>
                <p class="review-text-landing">"{r['text']}"</p>
                <span class="review-date-badge">{r['date']}</span>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<div style='margin:1.5rem 0;'></div>", unsafe_allow_html=True)

    # Row 2 — 3 cards
    if len(reviews_to_show) > 3:
        cols2 = st.columns(3, gap="medium")
        for idx in range(3, min(6, len(reviews_to_show))):
            r = reviews_to_show[idx]
            stars_html = "⭐" * r['rating']
            with cols2[idx - 3]:
                st.markdown(f"""
                <div class="review-card-landing">
                    <div class="review-header-row">
                        <div class="review-avatar" style="background:{r['avatar_color']};color:#fff;">
                            {r['avatar']}
                        </div>
                        <div class="review-meta">
                            <div class="review-name">{r['username']}</div>
                            <div class="review-role">{r['role']}</div>
                        </div>
                    </div>
                    <div class="review-stars">{stars_html}</div>
                    <p class="review-text-landing">"{r['text']}"</p>
                    <span class="review-date-badge">{r['date']}</span>
                </div>
                """, unsafe_allow_html=True)

    st.markdown("<div style='margin:2rem 0;'></div>", unsafe_allow_html=True)


def render_login_modal():
    """Render professional login modal"""
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("<h2 style='text-align: center; font-family: Space Grotesk; color: #f1f5f9; margin-bottom: 0.5rem;'>Welcome Back</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #94a3b8; margin-bottom: 2rem;'>Sign in to access your research dashboard</p>", unsafe_allow_html=True)
        
        with st.form("login_form", clear_on_submit=False):
            username = st.text_input("Username", placeholder="Enter your username", key="login_username")
            password = st.text_input("Password", type="password", placeholder="Enter your password", key="login_password")
            
            col_btn1, col_btn2 = st.columns(2)
            
            with col_btn1:
                submit = st.form_submit_button("Sign In", use_container_width=True, type="primary")
            
            with col_btn2:
                cancel = st.form_submit_button("Cancel", use_container_width=True)
            
            if cancel:
                st.session_state.show_login_modal = False
                st.rerun()
            
            if submit:
                if not username or not password:
                    st.error("Please enter both username and password")
                else:
                    user_id = verify_user(username, password)
                    if user_id:
                        st.session_state.loggedin = True
                        st.session_state.userid = user_id
                        st.session_state.username = username
                        st.session_state.user_plan = get_user_plan(user_id)
                        st.session_state.show_login_modal = False
                        st.session_state.chat_history = get_chat_history(user_id)
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("Invalid credentials. Try: admin / secure123")
        
        st.info("""💡 **Demo Accounts**

**Account 1:** admin / secure123
**Account 2:** researcher / research2024
**Account 3:** analyst / analyst2024
**Account 4:** manager / manager2024
**Account 5:** executive / exec2024""")

# ============================================================================
# APP NAVIGATION (LOGGED IN)
# ============================================================================

def render_app_navbar():
    """Render app navigation when logged in — includes Feedback tab"""
    st.markdown('<div style="margin-top: -2rem;"></div>', unsafe_allow_html=True)
    
    col1, col2, col3, col4, col5, col6, col7, col8, col9 = st.columns([2.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.2])
    
    with col1:
        st.markdown('<div style="padding: 1rem 0;"><span style="font-size: 1.9rem;">🔍</span> <span class="logo-text" style="font-size:1.8rem;">InfoFetch AI</span></div>', unsafe_allow_html=True)    
    with col2:
        if st.button("Research", key="nav_home", use_container_width=True):
            st.session_state.page = "Home"
            st.rerun()
    
    with col3:
        if st.button("Chatbot", key="nav_chat", use_container_width=True):
            st.session_state.page = "Chat"
            st.rerun()
    
    with col4:
        if st.button("History", key="nav_history", use_container_width=True):
            st.session_state.page = "History"
            st.rerun()
    
    with col5:
        if st.button("Plans", key="nav_upgrade", use_container_width=True):
            st.session_state.page = "Upgrade"
            st.rerun()

    with col6:
        if st.button("Feedback", key="nav_feedback", use_container_width=True):
            st.session_state.page = "Feedback"
            st.session_state.feedback_submitted = False
            st.rerun()
    
    with col7:
        if st.button("About", key="nav_about", use_container_width=True):
            st.session_state.page = "About"
            st.rerun()

    with col8:
        if st.button("Logout", key="nav_logout", use_container_width=True):
            st.session_state.clear()
            st.rerun()
    
    with col9:
        plan_badge_color = {
            'Free': 'rgba(100, 116, 139, 0.3)',
            'Plus': 'rgba(245, 158, 11, 0.3)',
            'Premium': 'rgba(168, 85, 247, 0.3)'
        }
        plan_text_color = {
            'Free': '#94a3b8',
            'Plus': '#fbbf24',
            'Premium': '#c084fc'
        }
        current_plan = st.session_state.user_plan
        st.markdown(f'<div style="padding: 0.75rem 1rem; background: {plan_badge_color.get(current_plan, "rgba(59, 130, 246, 0.15)")}; border: 1px solid rgba(59, 130, 246, 0.3); border-radius: 8px; color: {plan_text_color.get(current_plan, "#93c5fd")}; font-weight: 500; text-align: center;">👤 {st.session_state.username} ({current_plan})</div>', unsafe_allow_html=True)

# ============================================================================
# APP PAGES (LOGGED IN STATE)
# ============================================================================

def home_page():
    """Research page"""
    st.markdown('<div class="main-content-pro">', unsafe_allow_html=True)
    st.markdown('<h1 class="page-title-pro">Research Hub</h1>', unsafe_allow_html=True)
    
    if st.session_state.userid:
        stats = get_user_stats(st.session_state.userid)
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("🔍 Total Searches", stats['total_searches'])
        with col2:
            st.metric("💬 Chat Messages", stats['total_chats'])
        with col3:
            st.metric("⭐ Avg Confidence", stats['avg_confidence'])
        st.markdown("<div style='margin: 2rem 0;'></div>", unsafe_allow_html=True)
    
    daily_limits = {'Free': 10, 'Plus': 100, 'Premium': 999999}
    current_limit = daily_limits[st.session_state.user_plan]
    
    if st.session_state.userid and st.session_state.user_plan == 'Free':
        searches_today = get_user_stats(st.session_state.userid)['total_searches'] % current_limit
        st.warning(f"⚠️ Free Plan: {searches_today}/{current_limit} searches used today.")
    
    st.markdown("### 🔎 Intelligent Research Engine")
    st.info("💡 **Try**: Paytm careers for freshers •")
    
    query = st.text_input(
        "Enter your research question",
        placeholder="E.g., Amazon jobs for freshers, Tesla 2026 updates...",
        label_visibility="collapsed",
        key="research_query"
    )
    
    col1, col2 = st.columns([4, 1])
    with col1:
        research_btn = st.button("🚀 Search", use_container_width=True, type="primary")
    with col2:
        clear_btn = st.button("🗑️ Clear", use_container_width=True)
    
    if clear_btn:
        st.session_state.research_results = None
        st.rerun()
    
    if research_btn and query:
        if st.session_state.userid:
            searches_today = get_user_stats(st.session_state.userid)['total_searches'] % current_limit
            if searches_today >= current_limit and st.session_state.user_plan != 'Premium':
                st.error(f"❌ Daily limit reached ({current_limit} searches). Please upgrade!")
            else:
                with st.spinner("🔬 Analyzing data sources..."):
                    result = run_research_agent(query)
                    if save_search_history(st.session_state.userid, query, result):
                        st.session_state.research_results = result
                        st.success("✅ Research completed!")
                    else:
                        st.warning("⚠️ Research completed but not saved")
                        st.session_state.research_results = result
    
    if st.session_state.research_results:
        result = st.session_state.research_results
        is_company_displayed = display_company_results(result, st)
        if not is_company_displayed:
            display_general_results(result)
    
    st.markdown('</div>', unsafe_allow_html=True)

def display_general_results(result):
    """Display general research results"""
    st.markdown('<div class="professional-card">', unsafe_allow_html=True)
    st.markdown("### 📊 RESEARCH RESULTS")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        confidence = result.get('confidence', 'medium').title()
        st.metric("Confidence", "✅ " + confidence if confidence == 'High' else ("⚠️ " + confidence if confidence == 'Medium' else "ℹ️ " + confidence))
    with col2:
        st.metric("Sources Found", len(result.get('sources', [])))
    with col3:
        st.metric("Key Points", len(result.get('key_points', [])))
    
    st.markdown("<div style='margin: 1.5rem 0;'></div>", unsafe_allow_html=True)
    st.markdown("### 💡 EXECUTIVE SUMMARY")
    st.info(result.get('summary', 'No summary available'))
    st.markdown("### 🔑 KEY FINDINGS")
    for i, point in enumerate(result.get('key_points', [])[:10], 1):
        st.write(f"**{i}.** {point}")
    
    if result.get('sources'):
        st.markdown("### 🔗 SOURCES")
        for i, source in enumerate(result.get('sources', [])[:10], 1):
            st.code(f"{i}. {source}", language="")
    
    if st.session_state.user_plan in ['Plus', 'Premium']:
        st.download_button(
            "📥 Download JSON Report",
            data=json.dumps(result, indent=2),
            file_name=f"research_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )
    st.markdown('</div>', unsafe_allow_html=True)

def chat_page():
    """Chatbot page"""
    st.markdown('<div class="main-content-pro">', unsafe_allow_html=True)
    st.markdown('<h1 class="page-title-pro">💬 AI Assistant</h1>', unsafe_allow_html=True)
    st.markdown('<p class="page-subtitle-pro">Ask me anything about companies, jobs, or research</p>', unsafe_allow_html=True)
    
    if st.session_state.chat_history:
        for msg in st.session_state.chat_history[-20:]:
            if msg['role'] == 'user':
                with st.chat_message("user", avatar="👤"):
                    st.markdown(msg["content"])
            else:
                with st.chat_message("assistant", avatar="🤖"):
                    st.markdown(msg["content"])
    else:
        st.info("👋 Start a conversation! Ask me about companies, jobs, or any topic.")
    
    user_input = st.chat_input("Type your message...")
    
    if user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        save_chat_message(st.session_state.userid, "user", user_input)
        with st.spinner("🤔 Thinking..."):
            response = get_chat_response(user_input, st.session_state.chat_history)
        st.session_state.chat_history.append({"role": "assistant", "content": response})
        save_chat_message(st.session_state.userid, "assistant", response)
        st.rerun()
    
    if st.button("🗑️ Clear Chat History"):
        if clear_chat_history(st.session_state.userid):
            st.session_state.chat_history = []
            st.success("Chat cleared!")
            time.sleep(0.5)
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

def history_page():
    """History page"""
    st.markdown('<div class="main-content-pro">', unsafe_allow_html=True)
    st.markdown('<h1 class="page-title-pro">📚 Research History</h1>', unsafe_allow_html=True)
    
    if st.session_state.userid:
        stats = get_user_stats(st.session_state.userid)
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Searches", stats['total_searches'])
        with col2:
            st.metric("Total Messages", stats['total_chats'])
        with col3:
            st.metric("Avg Confidence", stats['avg_confidence'])
        st.markdown("<div style='margin: 2rem 0;'></div>", unsafe_allow_html=True)
    
    searches = get_user_history(st.session_state.userid) if st.session_state.userid else []
    
    if searches:
        st.markdown("### 🔍 Recent Searches")
        for search in searches[:15]:
            query_type = search['result'].get('query_type', 'general')
            query_icon = "🏢" if query_type == 'company' else "🔍"
            with st.expander(f"{query_icon} {search['query'][:80]}... ({search['confidence'].title()})"):
                st.write(f"**📅 Date:** {search['timestamp']} | **⭐ Confidence:** {search['confidence'].title()}")
                if search['result'].get('summary'):
                    st.write(search['result']['summary'][:300] + "...")
                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button("👁️ View", key=f"view{search['id']}", use_container_width=True):
                        st.session_state.research_results = search['result']
                        st.session_state.page = "Home"
                        st.rerun()
                with col2:
                    if st.button("🔄 Re-search", key=f"re{search['id']}", use_container_width=True):
                        st.info("Copy the query to search again!")
                with col3:
                    if st.button("🗑️ Delete", key=f"del{search['id']}", use_container_width=True):
                        if delete_search_item(search['id']):
                            st.success("Deleted!")
                            st.rerun()
        if st.button("🧹 Clear All History"):
            if clear_user_history(st.session_state.userid):
                st.success("History cleared!")
                time.sleep(0.5)
                st.rerun()
    else:
        st.info("🚀 No search history yet! Try the Research feature.")
    
    st.markdown('</div>', unsafe_allow_html=True)


# ============================================================================
# ✨ FEEDBACK PAGE - NEW
# ============================================================================

def feedback_page():
    """
    Creative, interactive feedback page that collects structured signals
    the AI system can learn from. Short but comprehensive.
    """
    st.markdown('<div class="main-content-pro">', unsafe_allow_html=True)

    # ── Show success state after submission ──────────────────────────────────
    if st.session_state.get('feedback_submitted', False):
        st.markdown("""
        <div class="success-feedback-banner">
            <div style="font-size:4rem;margin-bottom:1rem;">🎉</div>
            <h2 style="font-family:'Space Grotesk',sans-serif;color:#22c55e;font-size:2rem;margin-bottom:0.75rem;">
                Thank you for your feedback!
            </h2>
            <p style="color:#86efac;font-size:1.05rem;max-width:500px;margin:0 auto 1.5rem;">
                Your insights help make InfoFetch AI smarter for everyone.
                We read every submission carefully.
            </p>
            <p style="color:#64748b;font-size:0.85rem;">— The InfoFetch AI Team</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<div style='margin:2rem 0;'></div>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([2, 1, 2])
        with col2:
            if st.button("✍️ Submit Another", use_container_width=True):
                st.session_state.feedback_submitted = False
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        return

    # ── Hero banner ───────────────────────────────────────────────────────────
    st.markdown("""
    <div class="feedback-hero">
        <div style="font-size:3rem;margin-bottom:0.75rem;">🧠</div>
        <h1 style="font-family:'Space Grotesk',sans-serif;font-size:2.2rem;font-weight:700;
            background:linear-gradient(135deg,#ffffff,#93c5fd);-webkit-background-clip:text;
            -webkit-text-fill-color:transparent;margin-bottom:0.75rem;">
            Help Us Improve
        </h1>
        <p style="color:#94a3b8;font-size:1rem;max-width:520px;margin:0 auto;">
            Your feedback trains the AI to understand you better.
            Takes less than 2 minutes.
        </p>
        <div style="margin-top:1.25rem;display:flex;justify-content:center;gap:2rem;flex-wrap:wrap;">
            <span style="color:#64748b;font-size:0.85rem;">
                <span class="pulse-dot"></span>Live feedback loop active
            </span>
            <span style="color:#64748b;font-size:0.85rem;">🔒 Responses are private by default</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── SECTION 1 · Overall Experience ───────────────────────────────────────
    st.markdown("""
    <div class="feedback-section-card">
        <div class="feedback-section-title">⭐ Overall Experience</div>
    </div>
    """, unsafe_allow_html=True)

    emoji_options = {
        1: ("😤", "Frustrated"),
        2: ("😕", "Disappointed"),
        3: ("😐", "It's OK"),
        4: ("😊", "Happy"),
        5: ("🤩", "Love it!"),
    }
    overall_rating = st.select_slider(
        "How do you feel about InfoFetch AI overall?",
        options=[1, 2, 3, 4, 5],
        value=4,
        format_func=lambda x: f"{emoji_options[x][0]}  {emoji_options[x][1]}",
        key="overall_rating_slider"
    )

    # Contextual colour feedback
    rating_colors = {1: "#ef4444", 2: "#f97316", 3: "#eab308", 4: "#22c55e", 5: "#3b82f6"}
    rating_msgs = {
        1: "We're really sorry. Tell us what went wrong — we want to fix it.",
        2: "That's honest feedback. Please share more below.",
        3: "Good start! We'd love to know what would make it great.",
        4: "Awesome! Tell us what you liked most.",
        5: "You made our day! 🎉 What's your favourite feature?"
    }
    st.markdown(f"""
    <div style="background:rgba(30,41,59,0.6);border-left:4px solid {rating_colors[overall_rating]};
        border-radius:8px;padding:0.85rem 1.25rem;margin:0.5rem 0 1.5rem;color:#cbd5e1;font-size:0.9rem;">
        {emoji_options[overall_rating][0]}&nbsp;&nbsp;{rating_msgs[overall_rating]}
    </div>
    """, unsafe_allow_html=True)

    # ── SECTION 2 · Which features did you use? ───────────────────────────────
    st.markdown("---")
    st.markdown("### 🧩 Feature Usage")
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        used_research = st.checkbox("🔍 Company / Topic Research", value=True)
        used_chat = st.checkbox("💬 AI Chatbot", value=True)
    with col_f2:
        used_history = st.checkbox("📚 Search History")
        used_upgrade = st.checkbox("⭐ Upgrade / Plans")

    # ── SECTION 3 · Dimension ratings ────────────────────────────────────────
    st.markdown("---")
    st.markdown("### 📊 Rate Specific Dimensions")
    st.caption("1 = Poor   •   5 = Excellent")

    dim_col1, dim_col2, dim_col3 = st.columns(3)
    with dim_col1:
        accuracy_score = st.slider("🎯 Result Accuracy", 1, 5, 4, key="accuracy_slider")
        st.markdown(f"""<div class="progress-bar-container">
            <div class="progress-bar-fill" style="width:{accuracy_score*20}%;"></div></div>""",
            unsafe_allow_html=True)
    with dim_col2:
        speed_score = st.slider("⚡ Response Speed", 1, 5, 4, key="speed_slider")
        st.markdown(f"""<div class="progress-bar-container">
            <div class="progress-bar-fill" style="width:{speed_score*20}%;background:linear-gradient(90deg,#f59e0b,#ef4444);"></div></div>""",
            unsafe_allow_html=True)
    with dim_col3:
        ui_score = st.slider("🎨 UI / Design", 1, 5, 4, key="ui_slider")
        st.markdown(f"""<div class="progress-bar-container">
            <div class="progress-bar-fill" style="width:{ui_score*20}%;background:linear-gradient(90deg,#8b5cf6,#ec4899);"></div></div>""",
            unsafe_allow_html=True)

    # ── SECTION 4 · Feedback category ────────────────────────────────────────
    st.markdown("---")
    st.markdown("### 🏷️ Feedback Type")
    category = st.radio(
        "What best describes your feedback?",
        options=["💡 Suggestion", "🐛 Bug Report", "🙏 Praise", "❓ Question", "🔧 Improvement"],
        horizontal=True,
        key="feedback_category_radio",
        label_visibility="collapsed"
    )
    # strip emoji prefix for storage
    category_clean = category.split(" ", 1)[1] if " " in category else category

    # ── SECTION 5 · How well does the AI understand you? ─────────────────────
    st.markdown("---")
    st.markdown("### 🤖 AI Understanding Check")
    ai_understanding = st.radio(
        "When you ask InfoFetch AI a question, how well does it understand your intent?",
        options=[
            "🎯 Always understands perfectly",
            "✅ Usually gets it right",
            "🔄 Sometimes misses the point",
            "❌ Often misunderstands me",
        ],
        key="ai_understanding_radio",
    )
    ai_understanding_clean = ai_understanding.split(" ", 1)[1] if " " in ai_understanding else ai_understanding

    # ── SECTION 6 · Wanted features ──────────────────────────────────────────
    st.markdown("---")
    st.markdown("### 🚀 What Would Make InfoFetch AI Better?")
    st.caption("Select all that apply")

    wish_options = [
        "📱 Mobile app",
        "📧 Email digest / alerts",
        "🔁 Bulk research mode",
        "📄 PDF export",
        "🌐 More languages",
        "🗂️ Folder / project organisation",
        "🔗 CRM integrations",
        "📊 Visual charts & graphs",
    ]

    wish_cols = st.columns(4)
    selected_wishes = []
    for i, wish in enumerate(wish_options):
        with wish_cols[i % 4]:
            if st.checkbox(wish, key=f"wish_{i}"):
                selected_wishes.append(wish)

    # ── SECTION 7 · Open text ─────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("### 💬 In Your Own Words")
    feedback_text = st.text_area(
        "Tell us anything — a story, a bug, an idea, or just how you feel.",
        placeholder="E.g. 'The company research is great but I wish salary data was more specific for India...'",
        height=130,
        key="feedback_open_text",
        label_visibility="collapsed"
    )

    # ── SECTION 8 · Privacy toggle ────────────────────────────────────────────
    st.markdown("---")
    is_public = st.toggle(
        "🌐 Allow my feedback (anonymised) to appear in the public testimonials section",
        value=False,
        key="feedback_public_toggle"
    )

    # ── SUBMIT ────────────────────────────────────────────────────────────────
    st.markdown("<div style='margin:1.5rem 0 0.5rem;'></div>", unsafe_allow_html=True)

    col_s1, col_s2, col_s3 = st.columns([1, 2, 1])
    with col_s2:
        submit_feedback = st.button(
            "🚀 Submit Feedback",
            use_container_width=True,
            type="primary",
            key="submit_feedback_btn"
        )

    if submit_feedback:
        # Build feature-usage string for storage
        features_used = []
        if used_research: features_used.append("Research")
        if used_chat:     features_used.append("Chatbot")
        if used_history:  features_used.append("History")
        if used_upgrade:  features_used.append("Upgrade")

        feature_requests_str = "; ".join(selected_wishes) if selected_wishes else "None selected"
        combined_text = feedback_text.strip() if feedback_text.strip() else "No open-ended comment."

        success = save_feedback(
            user_id=st.session_state.userid,
            username=st.session_state.username,
            rating=overall_rating,
            category=category_clean,
            feedback_text=combined_text,
            ai_understanding=ai_understanding_clean,
            accuracy=accuracy_score,
            speed=speed_score,
            ui=ui_score,
            feature_requests=feature_requests_str,
            is_public=is_public
        )

        if success:
            st.session_state.feedback_submitted = True
            st.rerun()
        else:
            st.error("❌ Something went wrong saving your feedback. Please try again.")

    st.markdown('</div>', unsafe_allow_html=True)


# ============================================================================
# PAYMENT PAGES (unchanged)
# ============================================================================

def render_payment_modal(plan_name: str, amount: int, display_amount: str):
    plan_features = {
        'Plus': ['✓ 100 searches per day','✓ Advanced AI insights','✓ Priority response time','✓ Export to PDF/Excel','✓ Email support'],
        'Premium': ['✓ Unlimited searches','✓ API access','✓ Team collaboration','✓ Custom integrations','✓ 24/7 priority support','✓ Dedicated account manager']
    }
    st.markdown(f"""
    <div class="payment-modal">
        <div class="payment-header">
            <div class="payment-amount">{display_amount}</div>
            <div class="payment-plan-name">{plan_name} Plan</div>
        </div>
        <div class="payment-features">
            <h3 style="color: #3b82f6; margin-bottom: 1rem;">What's Included:</h3>
    """, unsafe_allow_html=True)
    for feature in plan_features.get(plan_name, []):
        st.markdown(f'<div class="payment-feature"><span style="color:#22c55e;font-size:1.2rem;">✓</span><span>{feature}</span></div>', unsafe_allow_html=True)
    st.markdown("</div></div>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("💳 Proceed to Payment", key="proceed_payment", use_container_width=True, type="primary"):
            order = create_razorpay_order(plan_name, st.session_state.userid, st.session_state.username)
            if order:
                st.session_state.payment_order = order
                create_payment_order(st.session_state.userid, plan_name, amount, order['order_id'])
                st.rerun()
            else:
                st.error("❌ Payment system unavailable. Please contact support.")
        if st.button("← Back to Plans", key="back_to_plans", use_container_width=True):
            st.session_state.show_payment_modal = False
            st.session_state.selected_plan = None
            st.rerun()

def render_razorpay_checkout():
    order = st.session_state.payment_order
    st.markdown(f"""
    <div class="payment-modal">
        <h2 style="text-align:center;color:#3b82f6;margin-bottom:1.5rem;">Complete Your Payment</h2>
        <p style="text-align:center;color:#94a3b8;margin-bottom:2rem;">
            You're upgrading to <strong>{order['plan_name']}</strong> plan
        </p>
    </div>""", unsafe_allow_html=True)
    st.components.v1.html(f"""
    <script src="https://checkout.razorpay.com/v1/checkout.js"></script>
    <script>
    var options = {{
        "key": "{order['key_id']}","amount": "{order['amount']}","currency": "{order['currency']}",
        "name": "InfoFetch AI","description": "{order['plan_name']} Plan Subscription",
        "image": "https://cdn-icons-png.flaticon.com/512/2920/2920277.png","order_id": "{order['order_id']}",
        "handler": function(response){{
            window.parent.postMessage({{type:'PAYMENT_SUCCESS',payment_id:response.razorpay_payment_id,
            order_id:response.razorpay_order_id,signature:response.razorpay_signature}},'*');
        }},
        "prefill":{{"name":"{st.session_state.username}","email":"{st.session_state.username}@infofetch.ai"}},
        "theme":{{"color":"#3b82f6"}},"modal":{{"ondismiss":function(){{window.parent.postMessage({{type:'PAYMENT_CANCELLED'}},'*');}}}}
    }};
    var rzp1 = new Razorpay(options);
    document.addEventListener('DOMContentLoaded',function(){{rzp1.open();}});
    </script>
    <div style="text-align:center;padding:3rem;">
        <button onclick="rzp1.open()" style="background:linear-gradient(135deg,#3b82f6,#2563eb);color:white;
        border:none;padding:1rem 3rem;border-radius:10px;font-size:1.1rem;font-weight:600;cursor:pointer;
        box-shadow:0 4px 14px rgba(59,130,246,0.4);">🔒 Pay {order['display_amount']} Securely</button>
        <p style="margin-top:1.5rem;color:#64748b;font-size:0.9rem;">🔐 Secured by Razorpay • 256-bit SSL Encryption</p>
    </div>""", height=400)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("✅ I've Completed Payment", key="payment_completed", use_container_width=True, type="primary"):
            complete_payment(order['order_id'], 'simulated_payment_id', 'simulated_signature')
            update_user_plan(st.session_state.userid, order['plan_name'])
            st.session_state.user_plan = order['plan_name']
            st.session_state.show_payment_modal = False
            st.session_state.payment_order = None
            st.success(f"🎉 Successfully upgraded to {order['plan_name']}!")
            time.sleep(2)
            st.rerun()
        if st.button("❌ Cancel Payment", key="cancel_payment", use_container_width=True):
            st.session_state.show_payment_modal = False
            st.session_state.payment_order = None
            st.rerun()

def upgrade_page():
    st.markdown('<div class="main-content-pro">', unsafe_allow_html=True)
    st.markdown('<h1 class="page-title-pro">⭐ Choose Your Plan</h1>', unsafe_allow_html=True)
    st.markdown('<p class="page-subtitle-pro">Select the perfect plan for your research needs</p>', unsafe_allow_html=True)
    if st.session_state.show_payment_modal and st.session_state.selected_plan:
        if st.session_state.payment_order:
            render_razorpay_checkout()
        else:
            plan_info = PLAN_PRICING[st.session_state.selected_plan]
            render_payment_modal(st.session_state.selected_plan, plan_info['amount'], plan_info['display'])
        st.markdown('</div>', unsafe_allow_html=True)
        return
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        current_plan = st.session_state.user_plan
        plan_emoji = {'Free':'🆓','Plus':'⭐','Premium':'👑'}
        st.info(f"{plan_emoji.get(current_plan,'🎯')} Current Plan: **{current_plan}**")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("### Free"); st.markdown("#### $0"); st.markdown("_Forever Free_")
        st.markdown("✓ 10 searches per day\n✓ Basic company research\n✓ Standard response time\n✓ Community support")
        if st.session_state.user_plan == 'Free':
            st.button("✓ Current Plan", key="free_current", use_container_width=True, disabled=True)
        else:
            if st.button("Switch to Free", key="free_btn", use_container_width=True):
                update_user_plan(st.session_state.userid, 'Free')
                st.session_state.user_plan = 'Free'
                st.success("✅ Switched to Free plan!")
                time.sleep(0.5); st.rerun()
    with col2:
        st.markdown("### ⭐ Plus"); st.markdown("#### ₹19/mo"); st.markdown("_Most Popular_")
        st.markdown("✓ 100 searches per day\n✓ Advanced insights\n✓ Priority response\n✓ Export to PDF/Excel")
        if st.session_state.user_plan == 'Plus':
            st.button("✓ Current Plan", key="plus_current", use_container_width=True, disabled=True)
        else:
            if RAZORPAY_AVAILABLE:
                if st.button("💳 Upgrade to Plus", key="plus_btn", use_container_width=True, type="primary"):
                    st.session_state.selected_plan = 'Plus'; st.session_state.show_payment_modal = True; st.rerun()
            else:
                st.warning("⚠️ Payment system unavailable"); st.info("Contact: support@infofetch.ai")
    with col3:
        st.markdown("### 👑 Premium"); st.markdown("#### ₹49/mo"); st.markdown("_Enterprise_")
        st.markdown("✓ Unlimited searches\n✓ API access\n✓ Team collaboration\n✓ 24/7 priority support")
        if st.session_state.user_plan == 'Premium':
            st.button("✓ Current Plan", key="premium_current", use_container_width=True, disabled=True)
        else:
            if RAZORPAY_AVAILABLE:
                if st.button("💳 Upgrade to Premium", key="premium_btn", use_container_width=True, type="primary"):
                    st.session_state.selected_plan = 'Premium'; st.session_state.show_payment_modal = True; st.rerun()
            else:
                st.warning("⚠️ Payment system unavailable"); st.info("Contact: support@infofetch.ai")
    st.success("💯 **30-Day Money-Back Guarantee** • Cancel anytime • Secure Payment via Razorpay")
    if st.session_state.user_plan in ['Plus', 'Premium']:
        st.markdown("---"); st.markdown("### 📜 Payment History")
        payments = get_user_payments(st.session_state.userid)
        if payments:
            for payment in payments:
                status_emoji = '✅' if payment['status'] == 'completed' else '⏳'
                st.markdown(f"{status_emoji} **{payment['plan']}** - {payment['currency']} {payment['amount']/100:.2f} - {payment['created']}")
        else:
            st.info("No payment history yet")
    st.markdown('</div>', unsafe_allow_html=True)

def about_page():
    st.markdown('<div class="main-content-pro">', unsafe_allow_html=True)
    st.markdown('<h1 class="page-title-pro">ℹ️ About InfoFetch AI</h1>', unsafe_allow_html=True)
    st.markdown("""
    ## 🎯 Enterprise Research Platform
    
    InfoFetch AI is a next-generation research platform designed for professionals 
    who demand accurate, timely, and actionable business intelligence.
    
    ### 🏢 Key Capabilities
    - **Company Intelligence** - Comprehensive company profiles, hiring trends, salary data
    - **Market Research** - Real-time market insights and competitive analysis
    - **AI Assistant** - Contextual Q&A powered by GPT-3.5-turbo
    - **Secure & Compliant** - Enterprise-grade security and data protection
    
    ### 🛠️ Technology Stack
    - **AI Models**: OpenAI GPT-3.5-turbo
    - **Search**: SerpAPI with 50+ premium sources
    - **Framework**: Streamlit, LangChain
    - **Database**: SQLite with encryption
    - **Payments**: Razorpay secure payment gateway
    
    ---
    **Version:** 3.0 Professional Edition | **Last Updated:** February 2026
    *Built for decision-makers, analysts, and research professionals*
    """)
    st.markdown('</div>', unsafe_allow_html=True)

# ============================================================================
# MAIN APPLICATION LOGIC
# ============================================================================

if st.session_state.show_login_modal:
    render_login_modal()

elif st.session_state.loggedin:
    st.markdown('<style>div.block-container{padding-top:0rem;}</style>', unsafe_allow_html=True)
    render_app_navbar()
    st.markdown("<div style='margin-top: -3rem;'></div>", unsafe_allow_html=True)

    if st.session_state.page == "Chat":
        chat_page()
    elif st.session_state.page == "History":
        history_page()
    elif st.session_state.page == "Upgrade":
        upgrade_page()
    elif st.session_state.page == "About":
        about_page()
    elif st.session_state.page == "Feedback":
        feedback_page()
    else:
        home_page()

else:
    st.markdown('<style>div.block-container{padding-top:0rem;}</style>', unsafe_allow_html=True)
    render_professional_navbar()
    st.markdown('<div style="margin-top: -3rem;"></div>', unsafe_allow_html=True)
    render_professional_hero()
    render_professional_features()
    render_professional_stats()
    render_customer_reviews()

    st.markdown("""
    <div class="footer-pro">
        <div style="margin-bottom: 1rem;">
            <span style="font-size: 1.5rem;">🔍</span>
            <span class="logo-text">InfoFetch AI</span>
        </div>
        <p>© 2026 InfoFetch AI. Enterprise Research Platform.</p>
        <p style="margin-top: 0.5rem; color: #475569;">
            Powered by OpenAI • SerpAPI • Streamlit • Razorpay
        </p>
    </div>
    """, unsafe_allow_html=True)
