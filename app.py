import streamlit as st
import pandas as pd
import plotly.express as px
import folium
from streamlit_folium import st_folium

from backend.data_processing import load_data, clean_data, normalize_data
from backend.index_calculation import calculate_priority_index
from backend.clustering import apply_clustering
from backend.recommendation import generate_recommendation


# ═══════════════════════════════════════════════════
# PAGE CONFIG
# ═══════════════════════════════════════════════════
st.set_page_config(
    page_title="CiviRank ⭐",
    page_icon="🏙️",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# ═══════════════════════════════════════════════════
# CSS INJECTION (shared)
# ═══════════════════════════════════════════════════
def load_css():
    try:
        with open("assets/style.css", "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        pass

load_css()


# ═══════════════════════════════════════════════════
# SESSION STATE
# ═══════════════════════════════════════════════════
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "username" not in st.session_state:
    st.session_state["username"] = ""
if "users" not in st.session_state:
    st.session_state["users"] = {}
if "dark_mode" not in st.session_state:
    st.session_state["dark_mode"] = False


# ═══════════════════════════════════════════════════
# LOGIN STYLES (injected only when needed)
# ═══════════════════════════════════════════════════
def inject_login_styles():
    st.markdown("""
    <style>
    .stApp { background: #020617 !important; color: #f8fafc; }
    header, footer, [data-testid="stToolbar"] { display: none !important; }
    .block-container { padding-top: 5vh !important; padding-bottom: 4vh !important; }

    /* Typography */
    .auth-brand { text-align: center; margin-bottom: 36px; }
    .auth-brand-icon { font-size: 52px; line-height: 1; margin-bottom: 12px; display: inline-block; animation: iconPulse 3s ease-in-out infinite; }
    @keyframes iconPulse { 0%,100% { transform: scale(1); } 50% { transform: scale(1.08); } }
    .auth-brand-title { font-size: 28px; font-weight: 800; color: #f8fafc; letter-spacing: -1px; margin-bottom: 6px; white-space: nowrap; }
    .auth-brand-sub { font-size: 15px; color: #94a3b8; font-weight: 400; }

    /* Pill Tabs */
    .stTabs [data-baseweb="tab-list"] {
        background: rgba(255,255,255,0.06); border-radius: 14px; padding: 5px; gap: 4px;
        border-bottom: none !important; margin-bottom: 36px; display: flex; width: 100%; min-width: 100%;
    }
    .stTabs [data-baseweb="tab"] {
        background: transparent; border-radius: 10px; color: #94a3b8;
        font-weight: 600; font-size: 14px; padding: 10px 0; box-shadow: none;
        border: none; flex: 1 1 auto; justify-content: center; transition: all 0.3s ease;
        min-width: unset; white-space: nowrap; overflow: visible;
    }
    .stTabs [data-baseweb="tab"]:hover { color: #f8fafc; background: rgba(255,255,255,0.03); }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #1f6f8b, #14b8a6) !important;
        color: white !important; box-shadow: 0 4px 16px rgba(20,184,166,0.3) !important;
    }
    /* Hide tab arrows */
    .stTabs [data-testid="stBaseButton-secondary"] { display: none !important; }

    /* Inputs */
    .stTextInput > div > div > input {
        background: rgba(255,255,255,0.06) !important; border: 1px solid rgba(255,255,255,0.1) !important;
        color: #f1f5f9 !important; border-radius: 12px !important; padding: 14px 16px !important;
        font-size: 15px !important; transition: all 0.3s ease; font-family: 'Inter', sans-serif !important;
    }
    .stTextInput > div > div > input:focus {
        border-color: #14b8a6 !important; box-shadow: 0 0 0 4px rgba(20,184,166,0.15) !important;
        background: rgba(255,255,255,0.08) !important;
    }
    .stTextInput > label {
        color: #94a3b8 !important; font-size: 13px !important; font-weight: 600 !important;
        text-transform: uppercase; letter-spacing: 0.6px; margin-bottom: 6px !important;
    }

    /* Checkbox */
    .stCheckbox > label { color: #94a3b8 !important; font-size: 13px !important; white-space: nowrap !important; }
    .stCheckbox > div > div { align-items: center !important; }

    /* Buttons */
    .stButton > button {
        width: 100%; background: linear-gradient(135deg, #1f6f8b, #14b8a6) !important;
        color: white !important; border: none !important; border-radius: 14px !important;
        padding: 14px !important; font-size: 16px !important; font-weight: 700 !important;
        box-shadow: 0 8px 24px rgba(20,184,166,0.25) !important; transition: all 0.3s ease !important;
        margin-top: 10px; font-family: 'Inter', sans-serif !important;
    }
    .stButton > button:hover {
        transform: translateY(-2px) !important; box-shadow: 0 12px 32px rgba(20,184,166,0.35) !important;
        filter: brightness(1.08);
    }
    .stButton > button:active { transform: scale(0.98) !important; }

    /* Form shell */
    [data-testid="stForm"] { background: transparent !important; border: none !important; box-shadow: none !important; padding: 0 !important; }

    /* Alerts */
    .stAlert { border-radius: 12px !important; border: none !important; padding: 14px 16px !important; }

    /* Hint box */
    .auth-hint {
        background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.08);
        border-radius: 12px; padding: 14px; color: #64748b; font-size: 13px;
        text-align: center; margin-top: 28px; line-height: 1.6;
    }

    /* Social buttons (visual) */
    .social-btn {
        flex: 1; background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1);
        border-radius: 12px; padding: 10px; color: #e2e8f0; font-size: 13px;
        cursor: pointer; transition: all 0.3s; text-align: center; font-weight: 600;
    }
    .social-btn:hover { background: rgba(255,255,255,0.1); border-color: rgba(255,255,255,0.2); transform: translateY(-1px); }

    /* Divider */
    .auth-divider {
        display: flex; align-items: center; gap: 16px; margin: 24px 0;
        color: #475569; font-size: 13px; font-weight: 500;
    }
    .auth-divider-line { flex: 1; height: 1px; background: rgba(255,255,255,0.08); }

    /* Links */
    .auth-link { color: #94a3b8; text-decoration: none; font-size: 13px; transition: color 0.3s; white-space: nowrap; }
    .auth-link:hover { color: #14b8a6; }

    /* Password strength bar */
    .strength-bar { height: 4px; border-radius: 4px; margin-top: 6px; transition: all 0.3s; background: rgba(255,255,255,0.06); }
    .strength-fill { height: 100%; border-radius: 4px; transition: all 0.3s; }

    /* Column layout helpers */
    .auth-card { width: 100%; max-width: 420px; margin: 0 auto; }
    </style>

    <div style="position: fixed; top:0; left:0; right:0; bottom:0; z-index:-1; background: #020617;
                background-image: linear-gradient(rgba(255,255,255,0.03) 1px, transparent 1px),
                                  linear-gradient(90deg, rgba(255,255,255,0.03) 1px, transparent 1px);
                background-size: 44px 44px; overflow: hidden;">
        <div style="position: absolute; width: 520px; height: 520px; border-radius: 50%; background: rgba(31,111,139,0.22); filter: blur(120px); top: -160px; left: -140px; animation: orb1 24s infinite ease-in-out;"></div>
        <div style="position: absolute; width: 420px; height: 420px; border-radius: 50%; background: rgba(20,184,166,0.18); filter: blur(100px); bottom: -120px; right: -120px; animation: orb2 28s infinite ease-in-out;"></div>
        <div style="position: absolute; width: 380px; height: 380px; border-radius: 50%; background: rgba(99,102,241,0.14); filter: blur(100px); top: 45%; left: 55%; animation: orb3 20s infinite ease-in-out;"></div>
    </div>

    <style>
    @keyframes orb1 { 0%,100% { transform: translate(0,0) scale(1); } 50% { transform: translate(60px, 40px) scale(1.1); } }
    @keyframes orb2 { 0%,100% { transform: translate(0,0) scale(1); } 50% { transform: translate(-50px, -60px) scale(1.15); } }
    @keyframes orb3 { 0%,100% { transform: translate(0,0) scale(1); } 50% { transform: translate(30px, -40px) scale(0.95); } }
    </style>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════
# CHART THEME HELPERS
# ═══════════════════════════════════════════════════
def chart_theme():
    if st.session_state.get("dark_mode", False):
        return {
            "paper_bgcolor": "rgba(0,0,0,0)",
            "plot_bgcolor": "rgba(0,0,0,0)",
            "font_color": "#f8fafc",
            "title_font_color": "#f8fafc",
            "gridcolor": "#334155",
            "legend_font_color": "#f8fafc",
        }
    return {
        "paper_bgcolor": "rgba(0,0,0,0)",
        "plot_bgcolor": "rgba(0,0,0,0)",
        "font_color": "#334155",
        "title_font_color": "#0f172a",
        "gridcolor": "#e2e8f0",
        "legend_font_color": "#334155",
    }


def apply_chart_layout(fig, theme):
    fig.update_layout(
        template="plotly_white",
        paper_bgcolor=theme["paper_bgcolor"],
        plot_bgcolor=theme["plot_bgcolor"],
        font=dict(size=13, color=theme["font_color"]),
        title_font=dict(size=20, color=theme["title_font_color"]),
        margin=dict(l=20, r=20, t=50, b=20),
        legend=dict(font=dict(color=theme["legend_font_color"]),
                    orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    fig.update_xaxes(gridcolor=theme["gridcolor"], gridwidth=0.5, zerolinecolor=theme["gridcolor"])
    fig.update_yaxes(gridcolor=theme["gridcolor"], gridwidth=0.5, zerolinecolor=theme["gridcolor"])
    return fig


# ═══════════════════════════════════════════════════
# DASHBOARD THEME INJECTION
# ═══════════════════════════════════════════════════
def inject_dashboard_theme():
    is_dark = st.session_state.get("dark_mode", False)
    if is_dark:
        st.markdown("""
        <style>
        .stApp {
            background: linear-gradient(120deg, #020617 0%, #0f172a 40%, #1e293b 100%) !important;
            color: #f8fafc !important;
        }
        .metric-card { background: rgba(15,23,42,0.92) !important; border-color: rgba(255,255,255,0.06) !important; box-shadow: 0 10px 30px rgba(0,0,0,0.35) !important; }
        .metric-value { color: #f8fafc !important; }
        .metric-label { color: #94a3b8 !important; }
        .header-box { background: linear-gradient(135deg, rgba(15,23,42,0.98), rgba(31,111,139,0.92), rgba(20,184,166,0.88)) !important; border-color: rgba(255,255,255,0.12) !important; }
        [data-testid="stForm"] { background: transparent !important; border-color: rgba(255,255,255,0.08) !important; }
        input, textarea { background: rgba(30,41,59,0.6) !important; color: #f8fafc !important; border-color: #334155 !important; }
        div[data-testid="stMetric"] { background: rgba(15,23,42,0.92) !important; border-color: rgba(255,255,255,0.06) !important; }
        div[data-testid="stMetricValue"] { color: #f8fafc !important; }
        div[data-testid="stMetricLabel"] { color: #94a3b8 !important; }
        section[data-testid="stFileUploader"] { background: rgba(30,41,59,0.6) !important; border-color: #334155 !important; }
        [data-testid="stExpander"] { background: rgba(30,41,59,0.6) !important; border-color: rgba(255,255,255,0.06) !important; }
        .stDataFrame { background: rgba(30,41,59,0.6) !important; }
        .stTabs [data-baseweb="tab-list"] { border-bottom-color: #334155 !important; }
        .stTabs [data-baseweb="tab"] { background: rgba(30,41,59,0.6) !important; color: #94a3b8 !important; box-shadow: 0 4px 14px rgba(0,0,0,0.2) !important; }
        .stTabs [aria-selected="true"] { color: white !important; }
        hr { background: linear-gradient(90deg, transparent, #334155, transparent) !important; }
        .footer { border-color: #1e293b !important; color: #94a3b8 !important; }
        .control-info { background: rgba(30,41,59,0.6) !important; border-color: #334155 !important; color: #94a3b8 !important; }
        .app-bar { border-bottom-color: #1e293b !important; }
        </style>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <style>
        .stApp { background: linear-gradient(120deg, #e0f2fe 0%, #f0f9ff 40%, #ffffff 100%) !important; color: #0f172a !important; }
        </style>
        """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════
# LOGIN / REGISTER PAGE
# ═══════════════════════════════════════════════════
def login_page():
    inject_login_styles()

    # Use a wide center column so the card is spacious on desktop
    _, center, _ = st.columns([1, 2, 1])
    with center:
        st.markdown("""
        <div class="auth-card">
            <div class="auth-brand">
                <div class="auth-brand-icon">🏙️</div>
                <div class="auth-brand-title">CiviRank</div>
                <div class="auth-brand-sub">A Platform designed for Better India!</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        login_tab, register_tab = st.tabs(["Sign In", "Create Account"])

        with login_tab:
            with st.form("login_form", clear_on_submit=False):
                username = st.text_input("Username", placeholder="Enter your username")
                password = st.text_input("Password", type="password", placeholder="••••••••")

                c1, c2 = st.columns([1, 1])
                with c1:
                    st.checkbox("Remember me", key="remember_login")
                with c2:
                    st.markdown("<div style='text-align: right; padding-top: 4px;'><a href='#' class='auth-link'>Forgot password?</a></div>", unsafe_allow_html=True)

                submitted = st.form_submit_button("Sign In")
                if submitted:
                    users = st.session_state.get("users", {})
                    if (username == "admin" and password == "admin123") or (username in users and users[username] == password):
                        st.session_state["logged_in"] = True
                        st.session_state["username"] = username
                        st.toast(f"✅ Welcome back, {username}!", icon="🎉")
                        st.rerun()
                    else:
                        st.error("Invalid username or password. Please try again.")

            st.markdown("""
            <div class="auth-card">
                <div class="auth-divider">
                    <div class="auth-divider-line"></div>
                    <span>or continue with</span>
                    <div class="auth-divider-line"></div>
                </div>
                <div style="display: flex; gap: 12px;">
                    <div class="social-btn">Google</div>
                    <div class="social-btn">GitHub</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        with register_tab:
            with st.form("register_form", clear_on_submit=False):
                new_name = st.text_input("Full Name", placeholder="Your full name")
                new_user = st.text_input("Username", placeholder="Choose a username")
                new_pass = st.text_input("Password", type="password", placeholder="Create a password")
                confirm_pass = st.text_input("Confirm Password", type="password", placeholder="Repeat password")

                # Password strength visualization
                strength = 0
                if new_pass:
                    strength = min(len(new_pass) * 10, 100)
                strength_color = "#ef4444" if strength < 40 else "#f59e0b" if strength < 80 else "#10b981"
                st.markdown(f"""
                <div style="margin-top: -8px; margin-bottom: 12px;">
                    <div style="font-size: 11px; color: #64748b; text-transform: uppercase; letter-spacing: 0.5px; font-weight: 600; margin-bottom: 4px;">Password Strength</div>
                    <div class="strength-bar"><div class="strength-fill" style="width: {strength}%; background: {strength_color};"></div></div>
                </div>
                """, unsafe_allow_html=True)

                st.checkbox("I agree to the Terms and Privacy Policy", key="terms_register")
                reg_submitted = st.form_submit_button("Get Started")

                if reg_submitted:
                    if not new_user or not new_pass:
                        st.error("Username and password are required.")
                    elif new_pass != confirm_pass:
                        st.error("Passwords do not match.")
                    elif new_user in st.session_state.get("users", {}):
                        st.error("Username already exists. Please choose another.")
                    else:
                        st.session_state["users"][new_user] = new_pass
                        st.success("✅ Account created! You can now sign in.")

        st.markdown("""
        <div class="auth-card">
            <div class="auth-hint">
                🔓 Demo Access — Username: <b>admin</b> &nbsp;•&nbsp; Password: <b>admin123</b>
            </div>
        </div>
        """, unsafe_allow_html=True)


if not st.session_state["logged_in"]:
    login_page()
    st.stop()


# ═══════════════════════════════════════════════════
# DASHBOARD — INTEGRATED CONTROL PANEL
# ═══════════════════════════════════════════════════
inject_dashboard_theme()

# Top App Bar
bar1, bar2, bar3 = st.columns([1, 2, 1])
with bar1:
    st.markdown('<div style="font-size: 24px; font-weight: 800; color: var(--text); letter-spacing: -0.5px;">🏙️ CiviRank</div>', unsafe_allow_html=True)
with bar3:
    st.markdown(f'<div style="text-align: right; font-size: 20px; color: var(--muted); font-weight: 900;">👤 <span style="color: var(--text); font-weight: 900;">{st.session_state["username"]}</span></div>', unsafe_allow_html=True)

st.markdown("<div class='app-bar' style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)

# Control Panel
st.markdown("""
<div style="margin-bottom: 8px; font-size: 12px; font-weight: 700; color: var(--muted); text-transform: uppercase; letter-spacing: 1px;">
    ⚙️ Control Panel
</div>
""", unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns([2, 2, 1, 1])
with c1:
    uploaded_file = st.file_uploader(
        "📤 Upload Slum Dataset (CSV)",
        type=["csv"],
        help="Upload your dataset or use the default sample data.",
        label_visibility="collapsed"
    )
with c2:
    st.markdown(
        '<div class="control-info">ℹ️ <b>Tip:</b> Upload your CSV or continue with the built-in sample dataset.</div>',
        unsafe_allow_html=True
    )
with c3:
    dark_mode = st.toggle(
        "🌙 Dark",
        value=st.session_state.get("dark_mode", False),
        key="dark_mode_toggle"
    )
    if dark_mode != st.session_state.dark_mode:
        st.session_state.dark_mode = dark_mode
        st.rerun()
with c4:
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state["logged_in"] = False
        st.session_state["username"] = ""
        st.rerun()

inject_dashboard_theme()


# ═══════════════════════════════════════════════════
# DATA LOADING & PROCESSING
# ═══════════════════════════════════════════════════
try:
    with st.spinner("🧠 Processing urban intelligence data…"):
        df = load_data(uploaded_file)
        df = clean_data(df)
        original_df = df.copy()
        df = normalize_data(df)
        df = calculate_priority_index(df)
        df = apply_clustering(df)
        df["Recommendation"] = df.apply(generate_recommendation, axis=1)
except Exception as e:
    st.error("🚨 Something went wrong while processing the dataset.")
    st.caption(f"Traceback: {e}")
    st.stop()


# ═══════════════════════════════════════════════════
# HERO HEADER
# ═══════════════════════════════════════════════════
st.markdown(f"""
<div class="header-box">
    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 20px;">
        <div>
            <h1 style="color:white; margin:0; font-size: 42px; font-weight: 800;">🏙️ CiviRank</h1>
            <p style="color: rgba(255,255,255,0.9); margin: 8px 0 0 0; font-size: 18px; font-weight: 400;">
                AI-powered urban intelligence for sustainable slum development planning.
            </p>
            <p style="color: rgba(255,255,255,0.7); margin: 6px 0 0 0; font-size: 14px; font-weight: 400;">
                Smart Priority Index • Risk Analysis • ML Clustering • Map Intelligence
            </p>
        </div>
        <div style="text-align: right;">
            <div style="background: rgba(255,255,255,0.15); border-radius: 16px; padding: 12px 20px; display: inline-block; backdrop-filter: blur(10px); border: 1px solid rgba(255,255,255,0.2);">
                <div style="font-size: 12px; color: rgba(255,255,255,0.8); text-transform: uppercase; letter-spacing: 1px; font-weight: 600;">Dataset Status</div>
                <div style="font-size: 16px; color: white; font-weight: 700;">{len(df):,} Records Loaded</div>
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════
# METRICS
# ═══════════════════════════════════════════════════
st.markdown("""
<div style="margin-bottom: 8px; font-size: 14px; font-weight: 700; color: var(--muted); text-transform: uppercase; letter-spacing: 1px;">
    📊 Urban Development Intelligence Overview
</div>
""", unsafe_allow_html=True)
st.markdown(
    '<div style="font-size: 14px; color: var(--muted); margin-bottom: 16px;">Real-time insights generated from uploaded slum development data.</div>',
    unsafe_allow_html=True
)

m1, m2, m3, m4 = st.columns(4)
with m1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-icon" style="background: linear-gradient(135deg, #3b82f6, #1d4ed8);">🏘️</div>
        <div class="metric-label">Total Areas</div>
        <div class="metric-value">{len(df):,}</div>
        <div class="metric-delta" style="color: #10b981;">▲ Active Regions</div>
    </div>
    """, unsafe_allow_html=True)

with m2:
    high_risk = len(df[df["Risk_Level"] == "High Risk"])
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-icon" style="background: linear-gradient(135deg, #ef4444, #b91c1c);">⚠️</div>
        <div class="metric-label">High Risk Areas</div>
        <div class="metric-value">{high_risk:,}</div>
        <div class="metric-delta" style="color: #ef4444;">Requires Immediate Action</div>
    </div>
    """, unsafe_allow_html=True)

with m3:
    avg_score = round(df["Priority_Score"].mean(), 2)
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-icon" style="background: linear-gradient(135deg, #f59e0b, #d97706);">📉</div>
        <div class="metric-label">Avg Priority Score</div>
        <div class="metric-value">{avg_score}</div>
        <div class="metric-delta" style="color: #f59e0b;">Composite Index</div>
    </div>
    """, unsafe_allow_html=True)

with m4:
    max_score = df["Priority_Score"].max()
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-icon" style="background: linear-gradient(135deg, #14b8a6, #0f766e);">🏆</div>
        <div class="metric-label">Highest Score</div>
        <div class="metric-value">{max_score}</div>
        <div class="metric-delta" style="color: #14b8a6;">Top Priority Region</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")


# ═══════════════════════════════════════════════════
# TABS
# ═══════════════════════════════════════════════════
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🏠 Priority Dashboard",
    "📈 Advanced Analytics",
    "🧠 ML Clustering",
    "🗺️ Geo-Spatial Map",
    "📄 AI Recommendations"
])

theme = chart_theme()

with tab1:
    st.markdown(
        '<div style="font-size: 20px; font-weight: 700; color: var(--text); margin-bottom: 16px;">🏆 Area Priority Ranking</div>',
        unsafe_allow_html=True
    )
    search_area = st.text_input(
        "🔍 Search Area",
        placeholder="Type area name to filter…",
        label_visibility="collapsed"
    )
    display_df = df.copy()
    if search_area:
        display_df = display_df[display_df["Area"].str.contains(search_area, case=False, na=False)]
    st.dataframe(
        display_df[["Rank", "Area", "Population", "Priority_Score", "Risk_Level", "Cluster"]],
        use_container_width=True,
        height=450,
        hide_index=True,
        column_config={
            "Rank": st.column_config.NumberColumn("Rank", width="small"),
            "Area": st.column_config.TextColumn("Area Name", width="medium"),
            "Population": st.column_config.NumberColumn("Population", width="medium"),
            "Priority_Score": st.column_config.NumberColumn(
                "Priority Score",
                format="%.2f",
                width="medium"
            ),
            "Risk_Level": st.column_config.TextColumn("Risk Level", width="medium"),
            "Cluster": st.column_config.NumberColumn("Cluster", width="small"),
        }
    )
    csv = display_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="⬇️ Download Processed Report",
        data=csv,
        file_name="civirank_processed_report.csv",
        mime="text/csv",
        use_container_width=False
    )

with tab2:
    st.markdown(
        '<div style="font-size: 20px; font-weight: 700; color: var(--text); margin-bottom: 16px;">📈 Priority Score Analysis</div>',
        unsafe_allow_html=True
    )
    a1, a2 = st.columns([2, 1])
    with a1:
        fig_bar = px.bar(
            df, x="Area", y="Priority_Score", color="Risk_Level",
            title="Priority Score by Area", text="Priority_Score",
            color_discrete_map={"High Risk": "#ef4444", "Medium Risk": "#f59e0b", "Low Risk": "#10b981"}
        )
        fig_bar.update_traces(textposition="outside", texttemplate="%{text:.2f}")
        fig_bar = apply_chart_layout(fig_bar, theme)
        st.plotly_chart(fig_bar, use_container_width=True, config={"displayModeBar": False})
    with a2:
        fig_pie = px.pie(
            df, names="Risk_Level", title="Risk Distribution", hole=0.45,
            color_discrete_map={"High Risk": "#ef4444", "Medium Risk": "#f59e0b", "Low Risk": "#10b981"}
        )
        fig_pie.update_traces(textposition="inside", textinfo="percent+label", pull=[0.02, 0.02, 0.02])
        fig_pie = apply_chart_layout(fig_pie, theme)
        st.plotly_chart(fig_pie, use_container_width=True, config={"displayModeBar": False})
    fig_scatter = px.scatter(
        df, x="Population", y="Priority_Score", color="Risk_Level",
        size="Priority_Score", hover_name="Area",
        title="Population vs Priority Score Correlation",
        color_discrete_map={"High Risk": "#ef4444", "Medium Risk": "#f59e0b", "Low Risk": "#10b981"}
    )
    fig_scatter = apply_chart_layout(fig_scatter, theme)
    st.plotly_chart(fig_scatter, use_container_width=True, config={"displayModeBar": False})

with tab3:
    st.markdown(
        '<div style="font-size: 20px; font-weight: 700; color: var(--text); margin-bottom: 16px;">🧠 KMeans Cluster Analysis</div>',
        unsafe_allow_html=True
    )
    fig_cluster = px.scatter(
        df, x="Sanitation", y="Healthcare", color=df["Cluster"].astype(str),
        size="Priority_Score", hover_name="Area",
        title="Development Cluster Visualization",
        color_discrete_sequence=px.colors.qualitative.Bold
    )
    fig_cluster = apply_chart_layout(fig_cluster, theme)
    st.plotly_chart(fig_cluster, use_container_width=True, config={"displayModeBar": False})
    st.markdown("""
    <div style="background: var(--border); border-radius: 14px; padding: 20px; border-left: 5px solid var(--secondary); margin-top: 16px;">
        <div style="font-weight: 700; color: var(--text); margin-bottom: 6px;">💡 Insight</div>
        <div style="color: var(--muted); font-size: 14px;">
            Cluster groups help identify similar areas based on development conditions. Areas within the same cluster share comparable sanitation and healthcare profiles, enabling targeted intervention strategies.
        </div>
    </div>
    """, unsafe_allow_html=True)

with tab4:
    st.markdown(
        '<div style="font-size: 20px; font-weight: 700; color: var(--text); margin-bottom: 16px;">🗺️ Geo-Spatial Intelligence Map</div>',
        unsafe_allow_html=True
    )
    if "Latitude" in original_df.columns and "Longitude" in original_df.columns:
        map_data = original_df.copy()
        map_data = map_data.dropna(subset=["Latitude", "Longitude"])
        if map_data.empty:
            st.warning("⚠️ Latitude and Longitude values are empty after dropping missing coordinates.")
        else:
            center_lat = map_data["Latitude"].mean()
            center_lon = map_data["Longitude"].mean()
            google_map = folium.Map(
                location=[center_lat, center_lon],
                zoom_start=12,
                tiles="https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}",
                attr="Google Maps"
            )
            for _, row in map_data.iterrows():
                area_name = row["Area"] if "Area" in row else "Unknown Area"
                matched_row = df[df["Area"] == area_name]
                if not matched_row.empty:
                    risk_level = matched_row["Risk_Level"].values[0]
                    priority_score = matched_row["Priority_Score"].values[0]
                else:
                    risk_level = "Unknown"
                    priority_score = "N/A"
                marker_color = (
                    "red" if risk_level == "High Risk"
                    else "orange" if risk_level == "Medium Risk"
                    else "green"
                )
                popup_html = f"""
                <div style="font-family: 'Inter', sans-serif; min-width: 200px;">
                    <div style="background: linear-gradient(135deg, #0f172a, #1f6f8b); color: white; padding: 10px 14px; border-radius: 10px 10px 0 0; font-weight: 700; font-size: 16px;">
                        {area_name}
                    </div>
                    <div style="background: white; padding: 14px; border-radius: 0 0 10px 10px; border: 1px solid #e2e8f0; border-top: none;">
                        <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                            <span style="color: #64748b; font-size: 13px;">Priority Score</span>
                            <span style="font-weight: 700; color: #0f172a; font-size: 13px;">{priority_score}</span>
                        </div>
                        <div style="display: flex; justify-content: space-between;">
                            <span style="color: #64748b; font-size: 13px;">Risk Level</span>
                            <span style="font-weight: 700; color: {marker_color}; font-size: 13px;">{risk_level}</span>
                        </div>
                    </div>
                </div>
                """
                folium.Marker(
                    location=[row["Latitude"], row["Longitude"]],
                    popup=folium.Popup(popup_html, max_width=300),
                    tooltip=area_name,
                    icon=folium.Icon(color=marker_color, icon="home", prefix="fa")
                ).add_to(google_map)
            st_folium(google_map, width=None, height=650)
    else:
        st.warning("🗺️ Latitude and Longitude columns are required for map visualization. Please upload a dataset containing coordinate data.")

with tab5:
    st.markdown(
        '<div style="font-size: 20px; font-weight: 700; color: var(--text); margin-bottom: 16px;">📄 Smart Development Recommendations</div>',
        unsafe_allow_html=True
    )
    for _, row in df.iterrows():
        risk_color = (
            "#ef4444" if row["Risk_Level"] == "High Risk"
            else "#f59e0b" if row["Risk_Level"] == "Medium Risk"
            else "#10b981"
        )
        with st.expander(f"🏘️ {row['Area']} | Score: {row['Priority_Score']} | {row['Risk_Level']}"):
            c1, c2 = st.columns([1, 3])
            with c1:
                st.markdown(f"""
                <div style="text-align: center; padding: 20px; background: var(--border); border-radius: 16px; border: 1px solid var(--border);">
                    <div style="font-size: 32px; font-weight: 800; color: var(--text);">{row['Rank']}</div>
                    <div style="font-size: 12px; color: var(--muted); text-transform: uppercase; letter-spacing: 1px; margin-top: 4px;">Rank</div>
                    <div style="margin-top: 16px; font-size: 14px; font-weight: 700; color: {risk_color}; background: {risk_color}15; padding: 6px 12px; border-radius: 20px; display: inline-block;">
                        {row['Risk_Level']}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            with c2:
                st.markdown(f"""
                <div style="margin-bottom: 8px;">
                    <span style="font-size: 12px; color: var(--muted); text-transform: uppercase; letter-spacing: 1px; font-weight: 700;">Population</span>
                    <div style="font-size: 18px; font-weight: 700; color: var(--text);">{row['Population']:,}</div>
                </div>
                <div style="margin-bottom: 8px;">
                    <span style="font-size: 12px; color: var(--muted); text-transform: uppercase; letter-spacing: 1px; font-weight: 700;">Priority Score</span>
                    <div style="font-size: 18px; font-weight: 700; color: var(--text);">{row['Priority_Score']}</div>
                </div>
                <div>
                    <span style="font-size: 12px; color: var(--muted); text-transform: uppercase; letter-spacing: 1px; font-weight: 700;">AI Recommendation</span>
                    <div style="font-size: 15px; color: var(--muted); line-height: 1.6; margin-top: 6px; background: var(--border); padding: 14px; border-radius: 12px; border-left: 4px solid var(--secondary);">
                        {row['Recommendation']}
                    </div>
                </div>
                """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════
# FOOTER
# ═══════════════════════════════════════════════════
st.markdown("""
<div class="footer">
    <div style="font-weight: 700; color: var(--text); margin-bottom: 4px;">CiviRank</div>
    <div style="font-size: 13px; color: var(--muted);">Smart Slum Development Priority Index © 2026</div>
    <div style="font-size: 12px; color: var(--muted); margin-top: 8px;">Powered by AI • ML Clustering • Geo-Spatial Analytics</div>
</div>
""", unsafe_allow_html=True)
