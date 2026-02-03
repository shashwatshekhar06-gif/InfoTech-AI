import streamlit as st

# CRITICAL: FIRST COMMAND - Must be before ANY other streamlit command
st.set_page_config(page_title="InfoFetch AI 🚀", page_icon="🔍", layout="wide")

# Imports AFTER set_page_config
import json
import time
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import custom modules
from serp import run_research_agent, get_chat_response, OPENAI_AVAILABLE, SERPAPI_AVAILABLE
from db_utils import *

# Futuristic Cyberpunk CSS
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@300;400;600;700&display=swap');

/* Global theme */
.stApp {
    background: linear-gradient(135deg, #0a0a1a 0%, #1a0033 50%, #0f0f2f 100%);
    font-family: 'Rajdhani', sans-serif;
}

/* Animated background stars */
.stApp::before {
    content: '';
    position: fixed;
    width: 100%;
    height: 100%;
    background-image: 
        radial-gradient(2px 2px at 20px 30px, rgba(255, 255, 255, 0.15), transparent),
        radial-gradient(1px 1px at 90px 40px, rgba(0, 245, 255, 0.4), transparent);
    background-size: 200px 100px;
    animation: sparkle 20s linear infinite;
    pointer-events: none;
    z-index: 0;
}

@keyframes sparkle {
    0% { transform: translateY(0); }
    100% { transform: translateY(-100px); }
}

/* Main header */
.main-header {
    font-family: 'Orbitron', monospace !important;
    font-size: 3.5rem !important;
    font-weight: 900 !important;
    text-align: center;
    background: linear-gradient(45deg, #00f5ff, #ff00ff, #00ff88, #00f5ff);
    background-size: 300% 300%;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    animation: textGlow 3s ease-in-out infinite;
    margin-bottom: 1rem;
    text-shadow: 0 0 30px rgba(0, 255, 255, 0.5);
}

@keyframes textGlow {
    0%, 100% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
}

/* Glass card effect */
.glass-card {
    background: rgba(20, 20, 50, 0.85);
    backdrop-filter: blur(25px);
    border: 1px solid rgba(0, 255, 255, 0.3);
    border-radius: 20px;
    padding: 2rem;
    margin: 1rem 0;
    box-shadow: 0 8px 32px rgba(0, 245, 255, 0.15);
    position: relative;
}

.glass-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    border-radius: 20px;
    padding: 2px;
    background: linear-gradient(45deg, transparent, #00f5ff, transparent, #ff00ff, transparent);
    background-size: 300% 300%;
    animation: borderGlow 4s ease infinite;
    -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
    -webkit-mask-composite: xor;
    mask-composite: exclude;
    z-index: -1;
}

@keyframes borderGlow {
    0%, 100% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
}

/* Chat message styling */
.chat-user {
    background: rgba(0, 245, 255, 0.1);
    border-left: 4px solid #00f5ff !important;
    padding: 1rem;
    border-radius: 12px;
    margin: 0.5rem 0;
    animation: slideInLeft 0.3s ease;
}

.chat-ai {
    background: rgba(255, 0, 255, 0.1);
    border-left: 4px solid #ff00ff !important;
    padding: 1rem;
    border-radius: 12px;
    margin: 0.5rem 0;
    animation: slideInRight 0.3s ease;
}

@keyframes slideInLeft {
    from { opacity: 0; transform: translateX(-20px); }
    to { opacity: 1; transform: translateX(0); }
}

@keyframes slideInRight {
    from { opacity: 0; transform: translateX(20px); }
    to { opacity: 1; transform: translateX(0); }
}

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, #00f5ff, #ff00ff) !important;
    color: #000 !important;
    border-radius: 15px !important;
    font-weight: 700 !important;
    font-family: 'Orbitron', monospace !important;
    border: none !important;
    padding: 0.75rem 2rem !important;
    text-transform: uppercase;
    letter-spacing: 1px;
    transition: all 0.3s ease !important;
    box-shadow: 0 0 20px rgba(0, 245, 255, 0.4) !important;
}

.stButton > button:hover {
    transform: translateY(-3px) !important;
    box-shadow: 0 0 30px rgba(255, 0, 255, 0.6) !important;
}

/* Input fields */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea {
    background: rgba(0, 0, 0, 0.4) !important;
    border: 2px solid rgba(0, 245, 255, 0.3) !important;
    border-radius: 12px !important;
    color: white !important;
    font-family: 'Rajdhani', sans-serif !important;
    font-size: 1.1rem !important;
    padding: 1rem !important;
}

.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: #00f5ff !important;
    box-shadow: 0 0 20px rgba(0, 245, 255, 0.4) !important;
}

/* Chat input special styling */
.stChatInput > div > div > input {
    background: rgba(0, 0, 0, 0.6) !important;
    border: 2px solid rgba(0, 245, 255, 0.4) !important;
    border-radius: 15px !important;
    color: white !important;
    font-size: 1.1rem !important;
}

/* Metrics */
[data-testid="stMetricValue"] {
    font-family: 'Orbitron', monospace !important;
    font-size: 2rem !important;
    background: linear-gradient(135deg, #00f5ff, #ff00ff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, rgba(10, 10, 26, 0.98) 0%, rgba(26, 0, 51, 0.98) 100%);
    border-right: 1px solid rgba(0, 245, 255, 0.3);
}

/* Expander */
.streamlit-expanderHeader {
    background: rgba(0, 0, 0, 0.4);
    border: 1px solid rgba(0, 245, 255, 0.3);
    border-radius: 12px;
    color: white !important;
    font-family: 'Rajdhani', sans-serif;
}

/* Success/Error/Info */
.stSuccess, .stError, .stWarning, .stInfo {
    background: rgba(0, 0, 0, 0.4) !important;
    border-radius: 12px !important;
    backdrop-filter: blur(10px);
}

/* Tabs */
.stTabs [data-baseweb="tab"] {
    background: rgba(0, 0, 0, 0.3);
    border-radius: 10px;
    color: #00f5ff !important;
    font-family: 'Orbitron', monospace;
}

.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, rgba(0, 245, 255, 0.3), rgba(255, 0, 255, 0.3));
}

/* Scrollbar */
::-webkit-scrollbar {
    width: 10px;
}

::-webkit-scrollbar-track {
    background: rgba(0, 0, 0, 0.3);
}

::-webkit-scrollbar-thumb {
    background: linear-gradient(135deg, #00f5ff, #ff00ff);
    border-radius: 10px;
}
</style>
""", unsafe_allow_html=True)

# Session state initialization
if 'loggedin' not in st.session_state:
    st.session_state.loggedin = False
if 'userid' not in st.session_state:
    st.session_state.userid = None
if 'username' not in st.session_state:
    st.session_state.username = None
if 'page' not in st.session_state:
    st.session_state.page = 'Home'
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'research_results' not in st.session_state:
    st.session_state.research_results = None

# ============================================================================
# LOGIN PAGE
# ============================================================================

def login_page():
    st.markdown('<h1 class="main-header">🔍 InfoFetch AI</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align:center;color:#00f5ff;font-size:1.5rem;letter-spacing:3px;font-family:Orbitron;">SECURE ACCESS PORTAL</p>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        
        # API Status indicators
        col_a, col_b = st.columns(2)
        with col_a:
            if OPENAI_AVAILABLE:
                st.success("✅ OpenAI Connected")
            else:
                st.error("❌ OpenAI Key Missing")
        with col_b:
            if SERPAPI_AVAILABLE:
                st.success("✅ SerpAPI Connected")
            else:
                st.error("❌ SerpAPI Key Missing")
        
        st.markdown("---")
        
        with st.form("login_form"):
            st.markdown("#### 🔐 ENTER CREDENTIALS")
            username = st.text_input("👤 Username", placeholder="admin")
            password = st.text_input("🔒 Password", type="password", placeholder="secure123")
            
            submit = st.form_submit_button("🚀 ACCESS SYSTEM", use_container_width=True)
            
            if submit:
                if not username or not password:
                    st.error("❌ Please enter credentials")
                else:
                    user_id = verify_user(username, password)
                    if user_id:
                        st.session_state.loggedin = True
                        st.session_state.userid = user_id
                        st.session_state.username = username
                        # Load chat history
                        st.session_state.chat_history = get_chat_history(user_id)
                        st.success("✅ ACCESS GRANTED!")
                        st.balloons()
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("❌ INVALID CREDENTIALS")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Demo accounts
        with st.expander("💾 DEMO ACCOUNTS", expanded=True):
            st.markdown("""
            <div style="background:rgba(0,245,255,0.1);padding:1rem;border-radius:10px;">
                <p style="color:#00f5ff;font-family:Orbitron;"><strong>Test Logins:</strong></p>
                <code style="background:rgba(0,0,0,0.5);padding:0.3rem;border-radius:5px;">admin / secure123</code><br>
                <code style="background:rgba(0,0,0,0.5);padding:0.3rem;border-radius:5px;">user1 / pass123</code><br>
                <code style="background:rgba(0,0,0,0.5);padding:0.3rem;border-radius:5px;">test / demo456</code>
            </div>
            """, unsafe_allow_html=True)

# ============================================================================
# HOME PAGE - RESEARCH
# ============================================================================

def home_page():
    st.markdown('<h1 class="main-header">🚀 RESEARCH HUB</h1>', unsafe_allow_html=True)
    
    # User stats
    if st.session_state.userid:
        stats = get_user_stats(st.session_state.userid)
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("🔍 Total Searches", stats['total_searches'])
        with col2:
            st.metric("💬 Chat Messages", stats['total_chats'])
        with col3:
            st.metric("⭐ Avg Confidence", stats['avg_confidence'])
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Research input
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("### 🔎 DEEP WEB RESEARCH")
    
    query = st.text_input(
        "Enter your research question",
        placeholder="E.g., Latest AI trends, Virat Kohli stats, Tesla 2026 plans...",
        label_visibility="collapsed",
        key="research_query"
    )
    
    col1, col2 = st.columns([4, 1])
    with col1:
        research_btn = st.button("🚀 RESEARCH NOW", use_container_width=True, type="primary")
    with col2:
        clear_btn = st.button("🗑️ Clear", use_container_width=True)
    
    if clear_btn:
        st.session_state.research_results = None
        st.rerun()
    
    if research_btn and query:
        with st.spinner("🔬 Analyzing 50+ web sources..."):
            result = run_research_agent(query)
            
            # Save to database
            if save_search_history(st.session_state.userid, query, result):
                st.session_state.research_results = result
                st.success("✅ Research completed & saved!")
            else:
                st.warning("⚠️ Research completed but not saved")
                st.session_state.research_results = result
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Display results
    if st.session_state.research_results:
        result = st.session_state.research_results
        
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("### 📊 RESEARCH RESULTS")
        
        # Metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            confidence = result.get('confidence', 'medium').title()
            if confidence == 'High':
                st.metric("Confidence", "✅ " + confidence)
            elif confidence == 'Medium':
                st.metric("Confidence", "⚠️ " + confidence)
            else:
                st.metric("Confidence", "ℹ️ " + confidence)
        
        with col2:
            st.metric("Sources Found", len(result.get('sources', [])))
        
        with col3:
            st.metric("Key Points", len(result.get('key_points', [])))
        
        st.markdown("---")
        
        # Summary
        st.markdown("### 💡 EXECUTIVE SUMMARY")
        st.info(result.get('summary', 'No summary available'))
        
        # Key Points
        st.markdown("### 🔑 KEY FINDINGS")
        for i, point in enumerate(result.get('key_points', [])[:10], 1):
            st.markdown(f"**{i}.** {point}")
        
        # Sources
        if result.get('sources'):
            st.markdown("### 🔗 SOURCES")
            for i, source in enumerate(result.get('sources', [])[:10], 1):
                st.code(f"{i}. {source}", language="")
        
        # Download
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            st.download_button(
                "📥 DOWNLOAD JSON",
                data=json.dumps(result, indent=2),
                file_name=f"research_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                use_container_width=True
            )
        
        st.markdown('</div>', unsafe_allow_html=True)

# ============================================================================
# CHATBOT PAGE - WITH REAL GPT-3.5
# ============================================================================

def chat_page():
    st.markdown('<h1 class="main-header">💬 AI CHATBOT</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align:center;color:#00f5ff;font-size:1.2rem;">Powered by GPT-3.5-turbo</p>', unsafe_allow_html=True)
    
    # Chat container
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    
    # Display chat history
    chat_container = st.container()
    with chat_container:
        if st.session_state.chat_history:
            for msg in st.session_state.chat_history[-20:]:  # Show last 20 messages
                if msg['role'] == 'user':
                    with st.chat_message("user", avatar="👤"):
                        st.markdown(f'<div class="chat-user">{msg["content"]}</div>', unsafe_allow_html=True)
                else:
                    with st.chat_message("assistant", avatar="🤖"):
                        st.markdown(f'<div class="chat-ai">{msg["content"]}</div>', unsafe_allow_html=True)
        else:
            st.info("👋 Start a conversation! Ask me anything.")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Chat input
    user_input = st.chat_input("💭 Type your message here...")
    
    if user_input:
        # Add user message to history
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        save_chat_message(st.session_state.userid, "user", user_input)
        
        # Get AI response
        with st.spinner("🤔 Thinking..."):
            response = get_chat_response(user_input, st.session_state.chat_history)
        
        # Add AI response to history
        st.session_state.chat_history.append({"role": "assistant", "content": response})
        save_chat_message(st.session_state.userid, "assistant", response)
        
        st.rerun()
    
    # Clear chat button
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("🗑️ CLEAR CHAT", use_container_width=True):
            if clear_chat_history(st.session_state.userid):
                st.session_state.chat_history = []
                st.success("Chat cleared!")
                st.rerun()

# ============================================================================
# HISTORY PAGE
# ============================================================================

def history_page():
    st.markdown('<h1 class="main-header">📚 HISTORY</h1>', unsafe_allow_html=True)
    
    # Stats
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    stats = get_user_stats(st.session_state.userid)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Searches", stats['total_searches'])
    with col2:
        st.metric("Total Messages", stats['total_chats'])
    with col3:
        st.metric("Avg Confidence", stats['avg_confidence'])
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Search history
    searches = get_user_history(st.session_state.userid)
    
    if searches:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("### 🔍 SEARCH HISTORY")
        
        for search in searches[:15]:
            with st.expander(f"🔍 {search['query'][:80]}... ({search['confidence'].title()})"):
                st.markdown(f"**📅 {search['timestamp']}** | **⭐ {search['confidence'].title()}**")
                
                if search['result'].get('summary'):
                    st.write(search['result']['summary'][:300] + "...")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button("👁️ View Full", key=f"view{search['id']}", use_container_width=True):
                        st.session_state.research_results = search['result']
                        st.session_state.page = "Home"
                        st.rerun()
                with col2:
                    if st.button("🗑️ Delete", key=f"del{search['id']}", use_container_width=True):
                        if delete_search_item(search['id']):
                            st.success("Deleted!")
                            st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Clear all history
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("🧹 CLEAR ALL HISTORY", use_container_width=True):
                if clear_user_history(st.session_state.userid):
                    st.success("History cleared!")
                    st.rerun()
    else:
        st.info("🚀 No search history yet! Try the Research feature.")

# ============================================================================
# ABOUT PAGE
# ============================================================================

def about_page():
    st.markdown('<h1 class="main-header">ℹ️ ABOUT</h1>', unsafe_allow_html=True)
    
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("""
    ## 🎯 What is InfoFetch AI?
    
    InfoFetch AI is a **next-generation research assistant** powered by:
    
    - 🔍 **SerpAPI** - Real-time web search
    - 🤖 **GPT-3.5-turbo** - Advanced AI analysis
    - 💬 **Intelligent Chatbot** - Conversational AI
    - 📊 **Confidence Scoring** - Source quality ratings
    - 📚 **History Tracking** - All interactions saved
    
    ## 🛠️ Features
    
    ✨ **Deep Research** - Analyze 50+ web sources instantly  
    💬 **AI Chatbot** - Conversational interface with memory  
    📊 **Structured Results** - Summaries, key points, and sources  
    🎯 **Confidence Scores** - Know the reliability of information  
    📚 **Full History** - Track all searches and chats  
    💾 **Export Data** - Download results as JSON  
    
    ## 🚀 How to Use
    
    1. **Login** with demo account (admin/secure123)
    2. **Research**: Enter questions for deep analysis
    3. **Chatbot**: Ask conversational queries
    4. **History**: Review all past interactions
    
    ## 💡 Pro Tips
    
    - Use **Research** for comprehensive web analysis
    - Use **Chatbot** for quick questions and conversations
    - Check **History** to revisit past searches
    - Download results for offline reference
    
    ---
    
    **Made with ❤️ using Streamlit, LangChain, and OpenAI**
    """)
    st.markdown('</div>', unsafe_allow_html=True)

# ============================================================================
# MAIN APP LOGIC
# ============================================================================

if st.session_state.loggedin:
    # Sidebar navigation
    with st.sidebar:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("### 🌌 **InfoFetch AI**")
        st.success(f"👋 {st.session_state.username}")
        st.markdown("---")
        
        if st.button("🏠 Research", use_container_width=True):
            st.session_state.page = "Home"
            st.rerun()
        
        if st.button("💬 Chatbot", use_container_width=True):
            st.session_state.page = "Chat"
            st.rerun()
        
        if st.button("📚 History", use_container_width=True):
            st.session_state.page = "History"
            st.rerun()
        
        if st.button("ℹ️ About", use_container_width=True):
            st.session_state.page = "About"
            st.rerun()
        
        st.markdown("---")
        
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.clear()
            st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Page routing
    if st.session_state.page == "Chat":
        chat_page()
    elif st.session_state.page == "History":
        history_page()
    elif st.session_state.page == "About":
        about_page()
    else:
        home_page()

else:
    login_page()