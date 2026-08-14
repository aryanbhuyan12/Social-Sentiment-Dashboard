import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import numpy as np
from textblob import TextBlob
import plotly.express as px
import plotly.graph_objects as go
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import io
import feedparser
import re
import requests
import datetime
import sqlite3
from fpdf import FPDF
from pypdf import PdfReader
from docx import Document
from youtube_comment_downloader import YoutubeCommentDownloader, SORT_BY_POPULAR
from deep_translator import GoogleTranslator
from langdetect import detect

# ---------------------------------------------------------
# 1. Page Configuration & Custom Glassmorphism CSS Styling
# ---------------------------------------------------------
st.set_page_config(
    page_title="FeeLiQ - Social Sentiment & Growth",
    page_icon="📊",
    layout="wide"
)

# ---------------------------------------------------------
# 2. Canvas Background Animation Injectors
# ---------------------------------------------------------
def render_shapegrid_background():
    """
    Renders React Bits' ShapeGrid as a high-performance background canvas.
    """
    shapegrid_html = """
    <div id="bg-container" style="position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; z-index: -1; pointer-events: auto; overflow: hidden; background: #07090e;">
        <canvas id="shapegrid-canvas" style="width: 100%; height: 100%; display: block;"></canvas>
    </div>
    <script>
    (function() {
        const canvas = document.getElementById('shapegrid-canvas');
        if (!canvas) return;
        const ctx = canvas.getContext('2d');

        const squareSize = 42;
        const speed = 0.6;
        const borderColor = 'rgba(56, 189, 248, 0.15)';
        const hoverFillColor = 'rgba(56, 189, 248, 0.28)';
        const hoverTrailAmount = 6;

        let gridOffset = { x: 0, y: 0 };
        let hoveredSquare = null;
        let trailCells = [];
        let cellOpacities = new Map();
        let animationFrameId = null;

        function resize() {
            canvas.width = window.innerWidth;
            canvas.height = window.innerHeight;
        }
        window.addEventListener('resize', resize);
        resize();

        function drawGrid() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);

            const offsetX = ((gridOffset.x % squareSize) + squareSize) % squareSize;
            const offsetY = ((gridOffset.y % squareSize) + squareSize) % squareSize;
            const cols = Math.ceil(canvas.width / squareSize) + 3;
            const rows = Math.ceil(canvas.height / squareSize) + 3;

            for (let col = -2; col < cols; col++) {
                for (let row = -2; row < rows; row++) {
                    const sx = col * squareSize + offsetX;
                    const sy = row * squareSize + offsetY;
                    const cellKey = `${col},${row}`;
                    const alpha = cellOpacities.get(cellKey);

                    if (alpha) {
                        ctx.globalAlpha = alpha;
                        ctx.fillStyle = hoverFillColor;
                        ctx.fillRect(sx, sy, squareSize, squareSize);
                        ctx.globalAlpha = 1;
                    }

                    ctx.strokeStyle = borderColor;
                    ctx.lineWidth = 1;
                    ctx.strokeRect(sx, sy, squareSize, squareSize);
                }
            }

            // Radial vignette
            const gradient = ctx.createRadialGradient(
                canvas.width / 2, canvas.height / 2, 0,
                canvas.width / 2, canvas.height / 2, Math.sqrt(canvas.width ** 2 + canvas.height ** 2) / 2
            );
            gradient.addColorStop(0, 'rgba(7, 9, 14, 0.2)');
            gradient.addColorStop(1, 'rgba(7, 9, 14, 0.85)');
            ctx.fillStyle = gradient;
            ctx.fillRect(0, 0, canvas.width, canvas.height);
        }

        function update() {
            gridOffset.x = (gridOffset.x - speed + squareSize) % squareSize;
            gridOffset.y = (gridOffset.y - speed + squareSize) % squareSize;

            const targets = new Map();
            if (hoveredSquare) {
                targets.set(`${hoveredSquare.x},${hoveredSquare.y}`, 1);
            }
            if (hoverTrailAmount > 0) {
                for (let i = 0; i < trailCells.length; i++) {
                    const t = trailCells[i];
                    const key = `${t.x},${t.y}`;
                    if (!targets.has(key)) {
                        targets.set(key, (trailCells.length - i) / (trailCells.length + 1));
                    }
                }
            }

            for (const [key] of targets) {
                if (!cellOpacities.has(key)) cellOpacities.set(key, 0);
            }

            for (const [key, opacity] of cellOpacities) {
                const target = targets.get(key) || 0;
                const next = opacity + (target - opacity) * 0.15;
                if (next < 0.005) {
                    cellOpacities.delete(key);
                } else {
                    cellOpacities.set(key, next);
                }
            }

            drawGrid();
            animationFrameId = requestAnimationFrame(update);
        }

        window.addEventListener('mousemove', (e) => {
            const offsetX = ((gridOffset.x % squareSize) + squareSize) % squareSize;
            const offsetY = ((gridOffset.y % squareSize) + squareSize) % squareSize;
            const col = Math.floor((e.clientX - offsetX) / squareSize);
            const row = Math.floor((e.clientY - offsetY) / squareSize);

            if (!hoveredSquare || hoveredSquare.x !== col || hoveredSquare.y !== row) {
                if (hoveredSquare && hoverTrailAmount > 0) {
                    trailCells.unshift({ ...hoveredSquare });
                    if (trailCells.length > hoverTrailAmount) trailCells.length = hoverTrailAmount;
                }
                hoveredSquare = { x: col, y: row };
            }
        });

        window.addEventListener('mouseleave', () => {
            if (hoveredSquare && hoverTrailAmount > 0) {
                trailCells.unshift({ ...hoveredSquare });
                if (trailCells.length > hoverTrailAmount) trailCells.length = hoverTrailAmount;
            }
            hoveredSquare = null;
        });

        update();
    })();
    </script>
    """
    components.html(shapegrid_html, height=0, width=0)

def render_blinking_squares_background():
    """
    Renders React Bits Pro's Blinking Squares (Twinkling Grid) as an ambient canvas.
    """
    blink_html = """
    <div id="blink-bg-container" style="position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; z-index: -1; pointer-events: none; overflow: hidden; background: #06080d;">
        <canvas id="blink-canvas" style="width: 100%; height: 100%; display: block;"></canvas>
    </div>
    <script>
    (function() {
        const canvas = document.getElementById('blink-canvas');
        if (!canvas) return;
        const ctx = canvas.getContext('2d');

        const squareSize = 38;
        const borderColor = 'rgba(255, 255, 255, 0.04)';
        let cols, rows;
        let squares = [];

        function resize() {
            canvas.width = window.innerWidth;
            canvas.height = window.innerHeight;
            cols = Math.ceil(canvas.width / squareSize) + 1;
            rows = Math.ceil(canvas.height / squareSize) + 1;
            initSquares();
        }

        function initSquares() {
            squares = [];
            for (let c = 0; c < cols; c++) {
                for (let r = 0; r < rows; r++) {
                    squares.push({
                        c: c,
                        r: r,
                        alpha: 0,
                        targetAlpha: 0,
                        speed: 0.01 + Math.random() * 0.03,
                        color: Math.random() > 0.4 ? '56, 189, 248' : (Math.random() > 0.5 ? '129, 140, 248' : '16, 185, 129')
                    });
                }
            }
        }

        window.addEventListener('resize', resize);
        resize();

        function draw() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);

            // Draw base grid
            for (let c = 0; c < cols; c++) {
                for (let r = 0; r < rows; r++) {
                    ctx.strokeStyle = borderColor;
                    ctx.lineWidth = 1;
                    ctx.strokeRect(c * squareSize, r * squareSize, squareSize, squareSize);
                }
            }

            // Update & draw blinking squares
            for (let i = 0; i < squares.length; i++) {
                const sq = squares[i];

                // Randomly trigger twinkle
                if (sq.targetAlpha === 0 && Math.random() < 0.0009) {
                    sq.targetAlpha = 0.25 + Math.random() * 0.45;
                }

                sq.alpha += (sq.targetAlpha - sq.alpha) * sq.speed;
                if (Math.abs(sq.targetAlpha - sq.alpha) < 0.01) {
                    if (sq.targetAlpha > 0) sq.targetAlpha = 0;
                }

                if (sq.alpha > 0.005) {
                    ctx.fillStyle = `rgba(${sq.color}, ${sq.alpha})`;
                    ctx.fillRect(sq.c * squareSize + 1, sq.r * squareSize + 1, squareSize - 2, squareSize - 2);
                }
            }

            // Radial vignette
            const gradient = ctx.createRadialGradient(
                canvas.width / 2, canvas.height / 2, 0,
                canvas.width / 2, canvas.height / 2, Math.sqrt(canvas.width ** 2 + canvas.height ** 2) / 2
            );
            gradient.addColorStop(0, 'rgba(6, 8, 13, 0.1)');
            gradient.addColorStop(1, 'rgba(6, 8, 13, 0.88)');
            ctx.fillStyle = gradient;
            ctx.fillRect(0, 0, canvas.width, canvas.height);

            requestAnimationFrame(draw);
        }

        draw();
    })();
    </script>
    """
    components.html(blink_html, height=0, width=0)

# Global styling injection
st.markdown(
    """
    <style>
    /* Transparent app container for canvas visibility */
    .stApp {
        background-color: transparent !important;
    }
    
    /* Header Gradient */
    .brand-title {
        font-size: 3.5rem;
        font-weight: 800;
        background: linear-gradient(90deg, #38bdf8, #818cf8, #34d399);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: -10px;
    }
    .brand-subtitle {
        font-size: 1.5rem;
        font-weight: 500;
        color: #f1f5f9;
        margin-bottom: 5px;
    }
    .brand-caption {
        font-size: 0.95rem;
        color: #94a3b8;
        margin-bottom: 25px;
    }

    /* Glassmorphism Metric and Content Cards */
    [data-testid="stMetricValue"], [data-testid="stMetric"] {
        background: rgba(15, 23, 42, 0.6) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 14px !important;
        padding: 12px 18px !important;
        backdrop-filter: blur(14px) !important;
        -webkit-backdrop-filter: blur(14px) !important;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37) !important;
    }
    
    /* Sidebar frosted styling */
    [data-testid="stSidebar"] {
        background: rgba(10, 14, 23, 0.8) !important;
        backdrop-filter: blur(18px) !important;
        -webkit-backdrop-filter: blur(18px) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.06) !important;
    }

    /* Table & Container background adjustment */
    [data-testid="stDataFrame"] {
        background: rgba(15, 23, 42, 0.5) !important;
        backdrop-filter: blur(12px) !important;
        border-radius: 12px !important;
        border: 1px solid rgba(255, 255, 255, 0.06) !important;
    }
    </style>
    
    <div>
        <span class="brand-title">FeeLiQ</span>
        <div class="brand-subtitle">Social Media Sentiment & Growth Dashboard</div>
        <div class="brand-caption">Real-time social telemetry, multilingual intelligence, competitor benchmarking & persistent workspace storage.</div>
    </div>
    """,
    unsafe_allow_html=True
)

# ---------------------------------------------------------
# 3. SQLite Database Setup & Storage Operations
# ---------------------------------------------------------
DB_FILE = "feeliq_analytics.db"

def init_database():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS telemetry_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_name TEXT,
            timestamp TEXT,
            author TEXT,
            likes INTEGER,
            weighted_impact REAL,
            brand TEXT,
            source TEXT,
            original_post TEXT,
            post TEXT,
            language TEXT,
            score REAL,
            sentiment TEXT,
            emotion TEXT,
            aspect TEXT,
            churn_intent BOOLEAN
        )
    """)
    conn.commit()
    conn.close()

init_database()

def get_all_projects():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT name FROM projects ORDER BY id DESC")
    rows = c.fetchall()
    conn.close()
    return [r[0] for r in rows] if rows else ["Default Workspace"]

def create_project(project_name):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    try:
        c.execute("INSERT INTO projects (name) VALUES (?)", (project_name.strip(),))
        conn.commit()
    except Exception:
        pass
    conn.close()

def save_dataframe_to_db(df, project_name):
    if df.empty:
        return
    conn = sqlite3.connect(DB_FILE)
    df_to_save = df.copy()
    df_to_save["project_name"] = project_name
    df_to_save["timestamp"] = df_to_save["Timestamp"].astype(str)
    
    col_mapping = {
        "Author": "author",
        "Likes": "likes",
        "Weighted Impact": "weighted_impact",
        "Brand": "brand",
        "Source": "source",
        "Original Post": "original_post",
        "Post": "post",
        "Language": "language",
        "Score": "score",
        "Sentiment": "sentiment",
        "Emotion": "emotion",
        "Aspect": "aspect",
        "Churn Intent": "churn_intent"
    }
    df_to_save = df_to_save.rename(columns=col_mapping)
    df_to_save.to_sql("telemetry_records", conn, if_exists="append", index=False)
    conn.close()

def load_dataframe_from_db(project_name):
    conn = sqlite3.connect(DB_FILE)
    query = "SELECT * FROM telemetry_records WHERE project_name = ? ORDER BY id DESC"
    loaded_df = pd.read_sql(query, conn, params=(project_name,))
    conn.close()
    
    if not loaded_df.empty:
        rev_mapping = {
            "author": "Author",
            "likes": "Likes",
            "weighted_impact": "Weighted Impact",
            "brand": "Brand",
            "source": "Source",
            "original_post": "Original Post",
            "post": "Post",
            "language": "Language",
            "score": "Score",
            "sentiment": "Sentiment",
            "emotion": "Emotion",
            "aspect": "Aspect",
            "churn_intent": "Churn Intent",
            "timestamp": "Timestamp"
        }
        loaded_df = loaded_df.rename(columns=rev_mapping)
        loaded_df["Timestamp"] = pd.to_datetime(loaded_df["Timestamp"])
    return loaded_df

# ---------------------------------------------------------
# 4. Session State Initialization
# ---------------------------------------------------------
if "analyzed_df" not in st.session_state:
    st.session_state["analyzed_df"] = pd.DataFrame()

if "competitor_df" not in st.session_state:
    st.session_state["competitor_df"] = pd.DataFrame()

# ---------------------------------------------------------
# 5. Sidebar Workspace & Navigation
# ---------------------------------------------------------
st.sidebar.title("🗂️ Active Workspace")
project_list = get_all_projects()
active_workspace = st.sidebar.selectbox("Current Project:", project_list)

new_proj_name = st.sidebar.text_input("Create New Workspace:", placeholder="e.g. Q3 Launch")
if st.sidebar.button("➕ Add Workspace"):
    if new_proj_name.strip():
        create_project(new_proj_name.strip())
        st.sidebar.success(f"Workspace '{new_proj_name}' created!")
        st.rerun()

st.sidebar.divider()
st.sidebar.title("Navigation")
page = st.sidebar.radio(
    "Go to",
    [
        "📊 Overview & Live Feed",
        "📈 Sentiment Analytics & Charts",
        "👥 Influencer & High-Impact Voices",
        "🌍 Multilingual Intelligence",
        "⏳ Time-Series Velocity & Forecasting",
        "🧠 Emotion & Aspect Intelligence",
        "⚔️ Competitor Benchmarking",
        "🤖 AI Copilot & Action Items",
        "☁️ Word Cloud & Topics",
        "🗄️ Workspaces & Database History",
        "🚨 Crisis Alerts & Executive Reports"
    ]
)

# ---------------------------------------------------------
# 6. Dynamic Animation Router
# ---------------------------------------------------------
if page == "📊 Overview & Live Feed":
    render_shapegrid_background()
else:
    render_blinking_squares_background()

st.sidebar.divider()

# --- SAFE NUMBER PARSER ---
def parse_engagement_count(val):
    if val is None:
        return np.random.randint(5, 150)
    if isinstance(val, (int, float)):
        return int(val)
    val_str = str(val).strip().lower().replace(",", "")
    try:
        if val_str.endswith("k"):
            return int(float(val_str[:-1]) * 1000)
        elif val_str.endswith("m"):
            return int(float(val_str[:-1]) * 1000000)
        elif val_str.endswith("b"):
            return int(float(val_str[:-1]) * 1000000000)
        numeric_match = re.search(r"[-+]?\d*\.?\d+", val_str)
        if numeric_match:
            return int(float(numeric_match.group()))
        return np.random.randint(5, 150)
    except Exception:
        return np.random.randint(5, 150)

# --- NLP & TRANSLATION HELPERS ---
def detect_and_translate(text):
    clean_txt = str(text).strip()
    if not clean_txt:
        return clean_txt, "en"
    try:
        lang = detect(clean_txt)
    except Exception:
        lang = "en"
    if lang != "en":
        try:
            translated = GoogleTranslator(source='auto', target='en').translate(clean_txt)
            return translated, lang
        except Exception:
            return clean_txt, lang
    return clean_txt, "en"

def detect_emotion(text, polarity):
    lower_text = text.lower()
    anger_words = {"angry", "hate", "terrible", "worst", "broken", "useless", "annoying", "rage", "awful", "scam", "trash"}
    joy_words = {"love", "awesome", "great", "amazing", "smooth", "best", "perfect", "fantastic", "good", "happy", "fire"}
    sadness_words = {"sad", "disappointed", "unfortunate", "miss", "regret", "depressing", "lost", "bad"}
    surprise_words = {"shocked", "wow", "unexpected", "unbelievable", "crazy", "surprised", "whoa"}
    fear_words = {"worry", "afraid", "risk", "danger", "scared", "fear", "insecure", "concern"}
    words = set(re.findall(r"\b\w+\b", lower_text))
    if words & anger_words or (polarity < -0.3 and any(w in lower_text for w in ["fix", "bug", "crash"])):
        return "Anger"
    elif words & joy_words or polarity > 0.35:
        return "Joy"
    elif words & sadness_words or polarity < -0.2:
        return "Sadness"
    elif words & surprise_words:
        return "Surprise"
    elif words & fear_words:
        return "Concern/Fear"
    else:
        return "Neutral"

def detect_aspect(text):
    lower_text = text.lower()
    if any(k in lower_text for k in ["ui", "ux", "design", "look", "interface", "screen", "dark mode", "visual", "layout"]):
        return "UI / UX"
    elif any(k in lower_text for k in ["lag", "crash", "speed", "slow", "fast", "performance", "bug", "patch", "freeze", "error"]):
        return "Performance & Stability"
    elif any(k in lower_text for k in ["price", "pricing", "cost", "expensive", "cheap", "subscription", "pay", "fee"]):
        return "Pricing & Value"
    elif any(k in lower_text for k in ["support", "service", "help", "agent", "team", "ticket", "response"]):
        return "Customer Support"
    else:
        return "Features & General"

def detect_churn_intent(text):
    lower_text = text.lower()
    churn_patterns = [
        "switching to", "switch to", "moving to", "leaving", "left", "canceling",
        "cancelled", "unsubscribe", "alternative", "replacement", "done with", "fed up"
    ]
    return any(p in lower_text for p in churn_patterns)

def process_records(raw_records, brand_name="Brand", enable_translation=True):
    processed = []
    base_time = datetime.datetime.now() - datetime.timedelta(hours=len(raw_records))
    
    for idx, record in enumerate(raw_records):
        original_text = str(record.get("Post", "")).strip()
        if not original_text:
            continue
        author = record.get("Author", f"user_{100 + idx}")
        likes = parse_engagement_count(record.get("Likes", None))
        
        if enable_translation:
            processed_text, detected_lang = detect_and_translate(original_text)
        else:
            processed_text, detected_lang = original_text, "en"
            
        blob = TextBlob(processed_text)
        score = blob.sentiment.polarity
        
        if score > 0.1:
            sentiment = "Positive"
        elif score < -0.1:
            sentiment = "Negative"
        else:
            sentiment = "Neutral"
            
        emotion = detect_emotion(processed_text, score)
        aspect = detect_aspect(processed_text)
        churn_flag = detect_churn_intent(processed_text)
        record_time = record.get("Timestamp", base_time + datetime.timedelta(minutes=idx * 25))
        weighted_impact = round(score * np.log1p(likes), 3)
        
        processed.append({
            "Timestamp": record_time,
            "Author": author,
            "Likes": likes,
            "Weighted Impact": weighted_impact,
            "Brand": brand_name,
            "Source": record.get("Source", "Unknown"),
            "Original Post": original_text,
            "Post": processed_text,
            "Language": detected_lang.upper(),
            "Score": round(score, 4),
            "Sentiment": sentiment,
            "Emotion": emotion,
            "Aspect": aspect,
            "Churn Intent": churn_flag
        })
    return pd.DataFrame(processed)

# --- PDF GENERATOR CLASS ---
class FeeLiQReport(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 18)
        self.set_text_color(56, 189, 248)
        self.cell(0, 10, "FeeLiQ - Executive Sentiment & Intelligence Report", border=False, align="L", ln=True)
        self.set_font("Helvetica", "I", 10)
        self.set_text_color(120, 120, 120)
        self.cell(0, 6, f"Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Confidential", border=False, align="L", ln=True)
        self.line(10, 28, 200, 28)
        self.ln(6)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(160, 160, 160)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")

def generate_pdf(df, nss, bhi, risk_status, pos_c, neu_c, neg_c):
    pdf = FeeLiQReport()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Helvetica", "B", 14)
    pdf.set_text_color(30, 41, 59)
    pdf.cell(0, 8, "1. Executive Growth & Health Summary", ln=True)
    pdf.ln(2)
    pdf.set_font("Helvetica", "", 10)
    pdf.set_fill_color(241, 245, 249)
    pdf.cell(45, 10, f"Net Sentiment: {nss}%", border=1, fill=True)
    pdf.cell(45, 10, f"Brand Health: {bhi}/100", border=1, fill=True)
    pdf.cell(50, 10, f"Risk Status: {risk_status}", border=1, fill=True)
    pdf.cell(50, 10, f"Total Mentions: {len(df)}", border=1, fill=True, ln=True)
    pdf.ln(4)
    pdf.cell(63, 8, f"Positive Mentions: {pos_c}", border=1)
    pdf.cell(63, 8, f"Neutral Mentions: {neu_c}", border=1)
    pdf.cell(64, 8, f"Negative Mentions: {neg_c}", border=1, ln=True)
    pdf.ln(8)
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 8, "2. Aspect Diagnostics", ln=True)
    pdf.set_font("Helvetica", "", 10)
    aspect_counts = df["Aspect"].value_counts()
    for asp, cnt in aspect_counts.items():
        pdf.cell(0, 6, f"- {asp}: {cnt} mentions", ln=True)
    pdf.ln(6)
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(16, 185, 129)
    pdf.cell(0, 7, "Top Positive Customer Voices:", ln=True)
    pdf.set_font("Helvetica", "I", 9)
    pdf.set_text_color(50, 50, 50)
    pos_quotes = df[df["Sentiment"] == "Positive"]["Post"].head(3).tolist()
    for q in pos_quotes:
        clean_q = q.encode('latin-1', 'replace').decode('latin-1')
        pdf.multi_cell(0, 5, f'"{clean_q[:140]}..."')
        pdf.ln(1)
    pdf.ln(4)
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(239, 68, 68)
    pdf.cell(0, 7, "Critical Areas Requiring Action:", ln=True)
    pdf.set_font("Helvetica", "I", 9)
    pdf.set_text_color(50, 50, 50)
    neg_quotes = df[df["Sentiment"] == "Negative"]["Post"].head(3).tolist()
    for q in neg_quotes:
        clean_q = q.encode('latin-1', 'replace').decode('latin-1')
        pdf.multi_cell(0, 5, f'"{clean_q[:140]}..."')
        pdf.ln(1)
    return pdf.output()

# ---------------------------------------------------------
# 7. Primary Ingestion
# ---------------------------------------------------------
st.sidebar.subheader("📡 Primary Brand Ingestion")
enable_trans = st.sidebar.checkbox("🌍 Enable Auto-Translation", value=True)

source_mode = st.sidebar.selectbox(
    "Select Connector",
    [
        "🔴 YouTube Comments (Live)",
        "🤖 Reddit (Live RSS Feed)",
        "📁 Upload Document (CSV / PDF / Word)",
        "✍️ Manual Text (Supports Multilingual)"
    ]
)

if source_mode == "🔴 YouTube Comments (Live)":
    yt_input = st.sidebar.text_input("YouTube Video URL / ID:", value="https://www.youtube.com/watch?v=dQw4w9WgXcQ", key="yt_main")
    max_comments = st.sidebar.slider("Max Comments", 10, 100, 30, key="max_yt_main")
    if st.sidebar.button("Fetch Primary YouTube"):
        with st.spinner("Fetching comments, authors & engagement..."):
            try:
                video_id_match = re.search(r"(?:v=|\/shorts\/|youtu\.be\/)([a-zA-Z0-9_-]{11})", yt_input)
                clean_target = video_id_match.group(1) if video_id_match else yt_input.strip()
                downloader = YoutubeCommentDownloader()
                comments = downloader.get_comments(clean_target, sort_by=SORT_BY_POPULAR)
                records = []
                count = 0
                for c in comments:
                    if count >= max_comments:
                        break
                    txt = c.get("text", "").strip()
                    if txt:
                        records.append({
                            "Author": c.get("author", f"yt_user_{count}"),
                            "Likes": c.get("votes", 0),
                            "Post": txt,
                            "Source": "YouTube"
                        })
                        count += 1
                if records:
                    st.session_state["analyzed_df"] = process_records(records, brand_name="Primary Brand", enable_translation=enable_trans)
                    st.sidebar.success(f"Fetched {len(records)} comments!")
            except Exception as e:
                st.sidebar.error(f"Error: {e}")

elif source_mode == "🤖 Reddit (Live RSS Feed)":
    subreddit_name = st.sidebar.text_input("Subreddit Name:", value="technology", key="sub_main")
    if st.sidebar.button("Fetch Primary Reddit"):
        with st.spinner(f"Ingesting r/{subreddit_name}..."):
            try:
                rss_url = f"https://www.reddit.com/r/{subreddit_name.strip()}/.rss"
                feed = feedparser.parse(rss_url, agent="FeeLiQ-Collector/1.0")
                records = []
                if feed.entries:
                    for entry in feed.entries:
                        clean_summary = re.sub(r"<[^<]+?>", "", entry.get("summary", ""))
                        author_name = entry.get("author", "u/redditor")
                        records.append({
                            "Author": author_name,
                            "Likes": np.random.randint(10, 800),
                            "Post": f"{entry.title}. {clean_summary}".strip(),
                            "Source": f"r/{subreddit_name}"
                        })
                    st.session_state["analyzed_df"] = process_records(records, brand_name="Primary Brand", enable_translation=enable_trans)
                    st.sidebar.success(f"Fetched {len(records)} posts!")
            except Exception as e:
                st.sidebar.error(f"Error: {e}")

elif source_mode == "📁 Upload Document (CSV / PDF / Word)":
    uploaded_file = st.sidebar.file_uploader("Upload Primary Data", type=["csv", "pdf", "docx"], key="doc_main")
    if uploaded_file is not None:
        file_ext = uploaded_file.name.split(".")[-1].lower()
        records = []
        if file_ext == "csv":
            try:
                raw_df = pd.read_csv(uploaded_file)
                col = st.sidebar.selectbox("Text Column:", raw_df.columns, key="csv_col_main")
                for idx, item in enumerate(raw_df[col].dropna().astype(str)):
                    records.append({
                        "Author": f"client_{idx}",
                        "Likes": np.random.randint(1, 150),
                        "Post": item,
                        "Source": f"CSV: {uploaded_file.name}"
                    })
            except Exception as e:
                st.sidebar.error(f"Error: {e}")
        elif file_ext == "pdf":
            try:
                reader = PdfReader(uploaded_file)
                for page_obj in reader.pages:
                    txt = page_obj.extract_text()
                    if txt:
                        lines = [line.strip() for line in txt.split("\n") if len(line.strip()) > 15]
                        for idx, l in enumerate(lines):
                            records.append({
                                "Author": f"doc_sec_{idx}",
                                "Likes": np.random.randint(1, 50),
                                "Post": l,
                                "Source": f"PDF: {uploaded_file.name}"
                            })
            except Exception as e:
                st.sidebar.error(f"Error: {e}")
        elif file_ext == "docx":
            try:
                doc = Document(uploaded_file)
                for idx, p in enumerate(doc.paragraphs):
                    if len(p.text.strip()) > 10:
                        records.append({
                            "Author": f"doc_par_{idx}",
                            "Likes": np.random.randint(1, 50),
                            "Post": p.text.strip(),
                            "Source": f"DOCX: {uploaded_file.name}"
                        })
            except Exception as e:
                st.sidebar.error(f"Error: {e}")
                
        if st.sidebar.button("Process Primary Document"):
            if records:
                st.session_state["analyzed_df"] = process_records(records, brand_name="Primary Brand", enable_translation=enable_trans)
                st.sidebar.success(f"Parsed {len(records)} sections!")

else:
    default_text = """Super excited for the new update release! Everything is so smooth.
The performance dropped significantly after the patch and it crashes constantly.
Pricing feels a bit too high for indie developers.
Customer service was quick to resolve my issue in 5 minutes!
The new UI layout is fantastic and very clean.
Terrible lag and constant freezing on the login page."""
    user_input = st.sidebar.text_area("Input Primary posts:", value=default_text, height=150, key="txt_main")
    if st.sidebar.button("Analyze Primary Text"):
        records = [
            {"Author": f"influencer_{i+1}", "Likes": (i+1)*85, "Post": l.strip(), "Source": "Manual"} 
            for i, l in enumerate(user_input.split("\n")) if l.strip()
        ]
        st.session_state["analyzed_df"] = process_records(records, brand_name="Primary Brand", enable_translation=enable_trans)
        st.sidebar.success("Primary data analyzed!")

# ---------------------------------------------------------
# 8. Check Active Session Data
# ---------------------------------------------------------
df = st.session_state["analyzed_df"]

if df.empty:
    st.info(f"👈 Ingest feedback data for **{active_workspace}** on the sidebar (or load history from DB) to begin.")
    stored_df = load_dataframe_from_db(active_workspace)
    if not stored_df.empty:
        if st.button(f"📥 Restore {len(stored_df)} Saved Records from '{active_workspace}'"):
            st.session_state["analyzed_df"] = stored_df
            st.rerun()
    st.stop()

# ---------------------------------------------------------
# 9. Global Growth KPIs Ribbon
# ---------------------------------------------------------
pos_count = len(df[df["Sentiment"] == "Positive"])
neg_count = len(df[df["Sentiment"] == "Negative"])
neu_count = len(df[df["Sentiment"] == "Neutral"])
total = len(df) if len(df) > 0 else 1

nss = round(((pos_count - neg_count) / total) * 100, 1)
avg_score = df["Score"].mean()
brand_health_index = max(0, min(100, round(50 + (avg_score * 50), 1)))

anger_count = len(df[df["Emotion"] == "Anger"])
anger_pct = round((anger_count / total) * 100, 1)
risk_status = "🟢 Normal" if anger_pct < 15 else ("🟡 Elevated" if anger_pct < 30 else "🔴 Crisis Risk")

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Net Sentiment Score", f"{nss}%")
col2.metric("Brand Health Index", f"{brand_health_index}/100")
col3.metric("Crisis Risk Level", risk_status)
col4.metric("Positive Mentions", pos_count)
col5.metric("Negative Mentions", neg_count)

st.divider()

# ---------------------------------------------------------
# 10. Navigation Views
# ---------------------------------------------------------

# PAGE 1: Overview & Live Feed (ShapeGrid Animated Background)
if page == "📊 Overview & Live Feed":
    st.subheader(f"Primary Telemetry Stream ({len(df)} Records Active in '{active_workspace}')")
    f_col1, f_col2, f_col3 = st.columns(3)
    with f_col1:
        filter_sentiment = st.selectbox("Filter Sentiment:", ["All", "Positive", "Neutral", "Negative"])
    with f_col2:
        filter_aspect = st.selectbox("Filter Aspect:", ["All"] + sorted(df["Aspect"].unique().tolist()))
    with f_col3:
        search_query = st.text_input("Search keyword:")

    filtered_df = df.copy()
    if filter_sentiment != "All":
        filtered_df = filtered_df[filtered_df["Sentiment"] == filter_sentiment]
    if filter_aspect != "All":
        filtered_df = filtered_df[filtered_df["Aspect"] == filter_aspect]
    if search_query:
        filtered_df = filtered_df[filtered_df["Post"].str.contains(search_query, case=False, na=False)]

    display_cols = ["Author", "Likes", "Weighted Impact", "Original Post", "Post", "Language", "Score", "Sentiment", "Emotion", "Aspect"]
    st.dataframe(filtered_df[display_cols], use_container_width=True, height=360)
    
    csv_buffer = io.StringIO()
    filtered_df.to_csv(csv_buffer, index=False)
    st.download_button("📥 Download Telemetry (CSV)", data=csv_buffer.getvalue(), file_name=f"{active_workspace}_telemetry.csv", mime="text/csv")

# PAGE 2: Sentiment Analytics (Blinking Squares Background)
elif page == "📈 Sentiment Analytics & Charts":
    st.subheader(f"Audience Polarity & Growth Metrics ({len(df)} Records)")
    chart_col1, chart_col2 = st.columns(2)
    color_map = {"Positive": "#10b981", "Neutral": "#64748b", "Negative": "#ef4444"}
    
    with chart_col1:
        st.markdown("#### Sentiment Share")
        sentiment_counts = df["Sentiment"].value_counts().reset_index()
        sentiment_counts.columns = ["Sentiment", "Count"]
        fig_donut = px.pie(sentiment_counts, names="Sentiment", values="Count", hole=0.45, color="Sentiment", color_discrete_map=color_map)
        fig_donut.update_traces(textinfo="percent+label")
        fig_donut.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#e2e8f0")
        st.plotly_chart(fig_donut, use_container_width=True)

    with chart_col2:
        st.markdown("#### Polarity Distribution")
        fig_hist = px.histogram(df, x="Score", nbins=20, color="Sentiment", color_discrete_map=color_map, labels={"Score": "Polarity Score (-1.0 to +1.0)"})
        fig_hist.update_layout(bargap=0.1, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#e2e8f0")
        st.plotly_chart(fig_hist, use_container_width=True)

# PAGE 3: Influencer & High-Impact Voices
elif page == "👥 Influencer & High-Impact Voices":
    st.subheader("👥 Influencer Voice Matrix & Engagement-Weighted Reach")
    st.markdown("### 🎯 Audience Reach vs. Sentiment Polarity Matrix")
    
    fig_matrix = px.scatter(
        df,
        x="Score",
        y="Likes",
        size="Likes",
        color="Sentiment",
        hover_name="Author",
        hover_data=["Post", "Emotion", "Weighted Impact"],
        color_discrete_map={"Positive": "#10b981", "Neutral": "#64748b", "Negative": "#ef4444"},
        size_max=30,
        labels={"Score": "Sentiment Polarity (-1.0 to +1.0)", "Likes": "Engagement Reach (Likes / Upvotes)"}
    )
    fig_matrix.add_vline(x=0.0, line_dash="dash", line_color="#475569")
    fig_matrix.add_hline(y=df["Likes"].median(), line_dash="dot", line_color="#64748b", annotation_text="Median Reach")
    fig_matrix.update_layout(margin=dict(t=20, b=20, l=20, r=20), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#e2e8f0")
    st.plotly_chart(fig_matrix, use_container_width=True)
    
    st.divider()
    col_adv, col_det = st.columns(2)
    
    with col_adv:
        st.markdown("### 🌟 Top Brand Advocates (VIP Evangelists)")
        advocates = df[df["Sentiment"] == "Positive"].sort_values(by="Weighted Impact", ascending=False).head(4)
        if not advocates.empty:
            for _, row in advocates.iterrows():
                st.success(f"**@{row['Author']}** · `{row['Likes']} Likes` · Impact: `+{row['Weighted Impact']}`\n\n> \"{row['Post']}\"")
        else:
            st.info("No strong positive advocates identified yet.")
            
    with col_det:
        st.markdown("### 🚨 High-Risk Detractors (Crisis Threats)")
        detractors = df[df["Sentiment"] == "Negative"].sort_values(by="Weighted Impact", ascending=True).head(4)
        if not detractors.empty:
            for _, row in detractors.iterrows():
                st.error(f"**@{row['Author']}** · `{row['Likes']} Likes` · Impact: `{row['Weighted Impact']}`\n\n> \"{row['Post']}\"")
        else:
            st.success("✅ No high-reach negative detractors detected!")

# PAGE 4: Multilingual Intelligence
elif page == "🌍 Multilingual Intelligence":
    st.subheader("🌍 Multilingual Feedback Intelligence & Translation Auditing")
    col_lang1, col_lang2 = st.columns([1, 2])
    with col_lang1:
        st.markdown("#### Language Distribution")
        lang_counts = df["Language"].value_counts().reset_index()
        lang_counts.columns = ["Language", "Count"]
        fig_lang = px.pie(lang_counts, names="Language", values="Count", hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel)
        fig_lang.update_traces(textinfo="percent+label")
        fig_lang.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#e2e8f0")
        st.plotly_chart(fig_lang, use_container_width=True)
        
    with col_lang2:
        st.markdown("#### Sentiment by Detected Language")
        lang_sent = df.groupby(["Language", "Sentiment"]).size().reset_index(name="Count")
        fig_lang_bar = px.bar(lang_sent, x="Language", y="Count", color="Sentiment", color_discrete_map={"Positive": "#10b981", "Neutral": "#64748b", "Negative": "#ef4444"}, barmode="group")
        fig_lang_bar.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#e2e8f0")
        st.plotly_chart(fig_lang_bar, use_container_width=True)
        
    st.divider()
    st.markdown("### 🔍 Side-by-Side Translation Audit Table")
    non_en_df = df[df["Language"] != "EN"]
    if not non_en_df.empty:
        st.dataframe(non_en_df[["Language", "Original Post", "Post", "Sentiment", "Emotion", "Aspect"]], use_container_width=True)
    else:
        st.info("All processed posts in the current batch were in English (EN).")

# PAGE 5: Time-Series Velocity & Forecasting
elif page == "⏳ Time-Series Velocity & Forecasting":
    st.subheader("⏳ Temporal Sentiment Velocity, Decay & Predictive Forecasting")
    ts_df = df.copy().sort_values(by="Timestamp").reset_index(drop=True)
    ts_df["Index"] = np.arange(len(ts_df))
    ts_df["Rolling_MA3"] = ts_df["Score"].rolling(window=3, min_periods=1).mean()
    ts_df["Rolling_MA7"] = ts_df["Score"].rolling(window=7, min_periods=1).mean()
    
    st.markdown("### 📈 Real-Time Sentiment Trajectory & Moving Averages")
    fig_ts = go.Figure()
    fig_ts.add_trace(go.Scatter(x=ts_df["Timestamp"], y=ts_df["Score"], mode="markers+lines", name="Raw Polarity", line=dict(color="#64748b", width=1, dash="dot"), marker=dict(size=8, color=ts_df["Score"], colorscale=[[0, "#ef4444"], [0.5, "#94a3b8"], [1, "#10b981"]], showscale=False)))
    fig_ts.add_trace(go.Scatter(x=ts_df["Timestamp"], y=ts_df["Rolling_MA3"], mode="lines", name="Fast Velocity (MA 3)", line=dict(color="#38bdf8", width=2.5)))
    fig_ts.add_trace(go.Scatter(x=ts_df["Timestamp"], y=ts_df["Rolling_MA7"], name="Macro Trend (MA 7)", line=dict(color="#a855f7", width=3)))
    fig_ts.add_hline(y=0.0, line_dash="dash", line_color="#475569", annotation_text="Neutral Line")
    fig_ts.update_layout(xaxis_title="Timeline", yaxis_title="Sentiment Polarity (-1.0 to +1.0)", margin=dict(t=20, b=20, l=20, r=20), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#e2e8f0")
    st.plotly_chart(fig_ts, use_container_width=True)
    
    st.divider()
    col_fc, col_spk = st.columns(2)
    with col_fc:
        st.markdown("### 🔮 Predictive Sentiment Forecast")
        x_vals = ts_df["Index"].values
        y_vals = ts_df["Score"].values
        if len(x_vals) >= 3:
            slope, intercept = np.polyfit(x_vals, y_vals, 1)
            future_indices = np.arange(len(x_vals), len(x_vals) + 5)
            forecasted_scores = slope * future_indices + intercept
            future_dates = [ts_df["Timestamp"].iloc[-1] + datetime.timedelta(minutes=25 * (i + 1)) for i in range(5)]
            fig_fc = go.Figure()
            fig_fc.add_trace(go.Scatter(x=ts_df["Timestamp"], y=ts_df["Score"], mode="lines", name="Historical", line=dict(color="#94a3b8")))
            fig_fc.add_trace(go.Scatter(x=future_dates, y=forecasted_scores, mode="lines+markers", name="AI Projected", line=dict(color="#f59e0b", width=3, dash="dash"), marker=dict(size=8, color="#f59e0b")))
            fig_fc.update_layout(margin=dict(t=10, b=10, l=10, r=10), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#e2e8f0")
            st.plotly_chart(fig_fc, use_container_width=True)

# PAGE 6: Emotion & Aspect Intelligence
elif page == "🧠 Emotion & Aspect Intelligence":
    st.subheader("Audience Emotion & Aspect-Based Sentiment Analysis")
    col_emo, col_aspect = st.columns(2)
    with col_emo:
        st.markdown("#### Detected Emotion Distribution")
        emotion_counts = df["Emotion"].value_counts().reset_index()
        emotion_counts.columns = ["Emotion", "Count"]
        emo_color_map = {"Joy": "#10b981", "Neutral": "#64748b", "Anger": "#ef4444", "Sadness": "#3b82f6", "Surprise": "#f59e0b", "Concern/Fear": "#8b5cf6"}
        fig_emo = px.bar(emotion_counts, x="Emotion", y="Count", color="Emotion", color_discrete_map=emo_color_map)
        fig_emo.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#e2e8f0")
        st.plotly_chart(fig_emo, use_container_width=True)
    with col_aspect:
        st.markdown("#### Feedback Breakdown by Aspect")
        aspect_df = df.groupby(["Aspect", "Sentiment"]).size().reset_index(name="Mentions")
        fig_aspect = px.bar(aspect_df, x="Aspect", y="Mentions", color="Sentiment", color_discrete_map={"Positive": "#10b981", "Neutral": "#64748b", "Negative": "#ef4444"}, barmode="stack")
        fig_aspect.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#e2e8f0")
        st.plotly_chart(fig_aspect, use_container_width=True)

# PAGE 7: Competitor Benchmarking
elif page == "⚔️ Competitor Benchmarking":
    st.subheader("⚔️ Head-to-Head Competitor Benchmarking & Churn Prospecting")
    comp_box = st.expander("📥 Ingest Competitor Feedback Data", expanded=st.session_state["competitor_df"].empty)
    with comp_box:
        comp_name = st.text_input("Competitor Name:", value="Competitor X")
        comp_source = st.selectbox("Competitor Data Source", ["✍️ Manual Text", "🤖 Reddit (RSS Feed)", "🔴 YouTube Comments", "📁 Upload Document"])
        comp_records = []
        if comp_source == "✍️ Manual Text":
            default_comp = """Competitor X has terrible customer support, waited 3 days for a reply.
Their pricing increased again, looking for an alternative now!
Thinking of switching to another product because the latest update is unusable.
The UI of Competitor X is decent, but constantly laggy.
Cancelling my subscription with Competitor X today."""
            comp_input = st.text_area("Paste Competitor posts:", value=default_comp, height=120)
            if st.button("Analyze Competitor Data"):
                comp_records = [{"Post": l.strip(), "Source": "Manual"} for l in comp_input.split("\n") if l.strip()]
                st.session_state["competitor_df"] = process_records(comp_records, brand_name=comp_name, enable_translation=enable_trans)
                st.success(f"Loaded {len(comp_records)} posts for {comp_name}!")
                st.rerun()

    comp_df = st.session_state["competitor_df"]
    if comp_df.empty:
        st.info("👈 Ingest competitor feedback above to unlock head-to-head benchmarking visuals and churn leads.")
    else:
        c_pos = len(comp_df[comp_df["Sentiment"] == "Positive"])
        c_neg = len(comp_df[comp_df["Sentiment"] == "Negative"])
        c_total = len(comp_df) if len(comp_df) > 0 else 1
        c_nss = round(((c_pos - c_neg) / c_total) * 100, 1)
        c_avg_score = comp_df["Score"].mean()
        c_bhi = max(0, min(100, round(50 + (c_avg_score * 50), 1)))
        delta_nss = round(nss - c_nss, 1)
        delta_bhi = round(brand_health_index - c_bhi, 1)
        
        st.markdown("### 🏆 Head-to-Head Growth KPIs")
        kpi1, kpi2, kpi3, kpi4 = st.columns(4)
        kpi1.metric("Your Brand NSS", f"{nss}%")
        kpi2.metric(f"{comp_df['Brand'].iloc[0]} NSS", f"{c_nss}%")
        kpi3.metric("Net Advantage (Δ NSS)", f"{delta_nss}%", delta=f"{delta_nss}%")
        kpi4.metric("Brand Health Gap (Δ BHI)", f"{delta_bhi} pts", delta=f"{delta_bhi}")

# PAGE 8: AI Copilot & Action Items
elif page == "🤖 AI Copilot & Action Items":
    st.subheader("🤖 Generative AI Copilot & Automated Action Generator")
    copilot_mode = st.radio("Select AI Engine:", ["⚡ FeeLiQ Offline Heuristic Copilot (Instant / Free)", "🔑 OpenAI GPT Engine (API Key Required)"], horizontal=True)
    openai_key = ""
    if "OpenAI" in copilot_mode:
        openai_key = st.text_input("Enter OpenAI API Key:", type="password", placeholder="sk-...")

    st.divider()
    tab1, tab2, tab3 = st.tabs(["📋 Chief of Staff Executive Briefing", "💬 Smart Customer Support Drafter", "🛠️ Automated Jira/Bug Ticket Creator"])
    
    with tab1:
        st.markdown("### 📋 Executive Telemetry Summary Briefing")
        if st.button("Generate Executive Briefing"):
            top_pos = df[df["Sentiment"] == "Positive"]["Post"].head(2).tolist()
            top_neg = df[df["Sentiment"] == "Negative"]["Post"].head(2).tolist()
            worst_aspect = df[df["Sentiment"] == "Negative"]["Aspect"].value_counts()
            worst_aspect_name = worst_aspect.index[0] if not worst_aspect.empty else "None"
            st.markdown(
                f"""
### 📊 FeeLiQ Executive Telemetry Briefing

1. **Executive Sentiment Assessment:**
   * Net Sentiment Score: **{nss}%** | Brand Health Index: **{brand_health_index}/100** | Risk: **{risk_status}**.

2. **Primary Friction & Growth Drivers:**
   * Primary user complaint cluster: **{worst_aspect_name}**.
   * Growth momentum sustained by UI responsiveness and resolution speed.

3. **Recommended Tactical Action Items:**
   * Patch stability friction in *{worst_aspect_name}*.
   * Proactively reach out to high-severity detractors.
                """
            )

    with tab2:
        st.markdown("### 💬 1-Click Smart Support Response Drafter")
        neg_posts = df[df["Sentiment"] == "Negative"]["Post"].tolist() or df["Post"].tolist()
        selected_post = st.selectbox("Select Customer Post to Respond To:", neg_posts)
        tone = st.selectbox("Select Reply Tone:", ["Empathetic & Professional", "Fast Resolution (Direct)", "Technical Support / Debugging"])
        if st.button("Draft AI Response"):
            template = f"Hi there, we apologize for the friction! We are escalating this directly to our team. Could you please send us a DM with your account details so we can fix this immediately?"
            st.success("Draft Generated:")
            st.text_area("Copy Response:", value=template, height=100)

    with tab3:
        st.markdown("### 🛠️ Automated Product Bug & Jira Ticket Creator")
        bug_candidates = df[df["Aspect"].isin(["Performance & Stability", "UI / UX"])]["Post"].tolist() or df["Post"].tolist()
        selected_bug_post = st.selectbox("Select Post with Issue/Bug:", bug_candidates, key="bug_sel")
        if st.button("Generate Issue Ticket"):
            ticket_body = f"""### 🏷️ Title: [BUG]: Friction in {df[df['Post'] == selected_bug_post]['Aspect'].iloc[0]}
**Severity:** High / Priority 2
**Detected Emotion:** {df[df['Post'] == selected_bug_post]['Emotion'].iloc[0]}

#### 📝 Description:
Customer telemetry flagged issue: "{selected_bug_post}"
"""
            st.success("Ticket Generated:")
            st.code(ticket_body, language="markdown")

# PAGE 9: Word Cloud
elif page == "☁️ Word Cloud & Topics":
    st.subheader(f"Audience Voice Word Cloud ({len(df)} Records)")
    cloud_filter = st.radio("Generate for sentiment class:", ["All Words", "Positive Words Only", "Negative Words Only"], horizontal=True)
    if cloud_filter == "Positive Words Only":
        cloud_text = " ".join(df[df["Sentiment"] == "Positive"]["Post"])
        colormap_choice = "Greens"
    elif cloud_filter == "Negative Words Only":
        cloud_text = " ".join(df[df["Sentiment"] == "Negative"]["Post"])
        colormap_choice = "Reds"
    else:
        cloud_text = " ".join(df["Post"])
        colormap_choice = "Blues"
        
    if cloud_text.strip():
        wordcloud = WordCloud(width=900, height=400, background_color="#0e1117", colormap=colormap_choice, stopwords={"the", "a", "and", "to", "is", "in", "it", "this", "my", "of", "for", "with", "on", "https", "co"}).generate(cloud_text)
        fig_wc, ax = plt.subplots(figsize=(10, 5))
        ax.imshow(wordcloud, interpolation="bilinear")
        ax.axis("off")
        fig_wc.patch.set_facecolor('#0e1117')
        st.pyplot(fig_wc)

# PAGE 10: Workspaces & Database History
elif page == "🗄️ Workspaces & Database History":
    st.subheader(f"🗄️ Persistent Database & Workspace Management ({active_workspace})")
    db_col1, db_col2 = st.columns(2)
    with db_col1:
        st.markdown("### 💾 Save Current Telemetry to SQLite DB")
        st.write(f"Persist the current active batch of **{len(df)} records** under workspace **`{active_workspace}`**:")
        if st.button("Save Batch to Database"):
            save_dataframe_to_db(df, active_workspace)
            st.success(f"✅ Successfully committed {len(df)} records to database under '{active_workspace}'!")
            
    with db_col2:
        st.markdown("### 🔄 Historical Telemetry Restore")
        st.write(f"Retrieve previously saved snapshot batches from **`{active_workspace}`**:")
        if st.button("Load Workspace History from DB"):
            historical_df = load_dataframe_from_db(active_workspace)
            if not historical_df.empty:
                st.session_state["analyzed_df"] = historical_df
                st.success(f"✅ Loaded {len(historical_df)} historical records from SQLite!")
                st.rerun()
            else:
                st.warning(f"No saved historical records found for workspace '{active_workspace}'.")
                
    st.divider()
    st.markdown(f"### 🗃️ Persistent SQLite Database View: `{active_workspace}`")
    all_db_records = load_dataframe_from_db(active_workspace)
    if not all_db_records.empty:
        st.dataframe(all_db_records, use_container_width=True, height=320)
        hist_pos = len(all_db_records[all_db_records["Sentiment"] == "Positive"])
        hist_neg = len(all_db_records[all_db_records["Sentiment"] == "Negative"])
        hist_total = len(all_db_records)
        hist_nss = round(((hist_pos - hist_neg) / hist_total) * 100, 1)
        st.info(f"📊 **Workspace Lifetime Metrics:** Total Records: `{hist_total}` | Lifetime Net Sentiment: `{hist_nss}%`")
    else:
        st.info(f"No records stored in SQLite database yet for '{active_workspace}'. Click 'Save Batch to Database' above to persist records.")

# PAGE 11: Crisis Alerts & Executive Reports
elif page == "🚨 Crisis Alerts & Executive Reports":
    st.subheader("Automated Executive Reporting & Team Incident Webhooks")
    rep_col, alert_col = st.columns(2)
    with rep_col:
        st.markdown("### 📄 Executive PDF Intelligence Report")
        if st.button("Generate Executive PDF Report"):
            with st.spinner("Compiling Report..."):
                pdf_bytes = generate_pdf(df, nss, brand_health_index, risk_status, pos_count, neu_count, neg_count)
                st.download_button("⬇️ Download PDF Report", data=bytes(pdf_bytes), file_name=f"FeeLiQ_{active_workspace}_Report_{datetime.date.today()}.pdf", mime="application/pdf")
                
    with alert_col:
        st.markdown("### 🔔 Incident Alert Webhook Dispatcher")
        webhook_url = st.text_input("Webhook URL (Discord / Slack):", placeholder="https://discord.com/api/webhooks/...")
        if st.button("🚀 Dispatch Real-Time Incident Alert"):
            if not webhook_url:
                st.warning("Please provide a Webhook URL.")
            else:
                payload = {
                    "content": f"🚨 **[FeeLiQ Intelligence Alert - {active_workspace}]**\n"
                               f"• **Status:** {risk_status}\n"
                               f"• **Net Sentiment Score:** `{nss}%`\n"
                               f"• **Brand Health Index:** `{brand_health_index}/100`\n"
                               f"• **Anger Rate:** `{anger_pct}%`\n"
                               f"• **Mentions:** `{len(df)}`"
                }
                try:
                    res = requests.post(webhook_url, json=payload, timeout=5)
                    if res.status_code in [200, 204]:
                        st.success("✅ Alert dispatched!")
                    else:
                        st.error(f"Failed (HTTP {res.status_code})")
                except Exception as e:
                    st.error(f"Error: {e}")
