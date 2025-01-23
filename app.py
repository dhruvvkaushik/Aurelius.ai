import streamlit as st
from dotenv import load_dotenv
import os
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse, parse_qs
import time

# Load environment variables
load_dotenv()

# Configure Gemini AI
genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))

# =====================================
# Custom UI Styling
# =====================================
st.markdown("""
    <style>
    @keyframes gradientBG {
        0% {background-position: 0% 50%}
        50% {background-position: 100% 50%}
        100% {background-position: 0% 50%}
    }
    
    .main {
        background: linear-gradient(-45deg, #ee7752, #e73c7e, #23a6d5, #23d5ab);
        background-size: 400% 400%;
        animation: gradientBG 15s ease infinite;
        color: #ffffff;
    }
    
    .stTextInput>div>div>input {
        background: rgba(255, 255, 255, 0.9) !important;
        border-radius: 25px !important;
        padding: 15px 25px !important;
        font-size: 1.1rem !important;
    }
    
    .summary-card {
        background: rgba(255, 255, 255, 0.95) !important;
        border-radius: 20px;
        padding: 2rem;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        backdrop-filter: blur(10px);
        margin: 2rem 0;
        color: #2c3e50;
    }
    
    .pulse {
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0% {transform: scale(0.95)}
        50% {transform: scale(1.05)}
        100% {transform: scale(0.95)}
    }
    </style>
    """, unsafe_allow_html=True)

# =====================================
# App Header
# =====================================
st.markdown("""
    <div style="text-align: center; padding: 2rem 0;">
        <h1 style="font-size: 3.5rem; margin: 0;">🎥 Aurelius.ai</h1>
        <p style="font-size: 1.2rem; opacity: 0.9;">Transform YouTube Videos into Actionable Insights</p>
    </div>
""", unsafe_allow_html=True)

# =====================================
# Sidebar Configuration
# =====================================
with st.sidebar:
    st.markdown("""
        <style>
        .sidebar .sidebar-content {
            background: rgba(255, 255, 255, 0.85) !important;
            backdrop-filter: blur(5px);
        }
        </style>
    """, unsafe_allow_html=True)
    
    st.header("🚀 Quick Guide")
    st.markdown("""
    1. Paste YouTube URL
    2. Let AI analyze content
    3. Get instant video digest
    4. Save or share insights
    """)
    st.progress(100 if st.session_state.get('processed') else 0)
    st.markdown("---")
    st.markdown("**Powered by:**")
    st.markdown("- Google Gemini AI")
    st.markdown("- YouTube Transcript API")
    st.markdown("- Streamlit")

# =====================================
# AI Prompt Engineering
# =====================================
PROMPT_TEMPLATE = """**Create an engaging video digest with this structure:**

🌟 **Core Concept**: {core_concept}

📌 **Key Points** (5-7 bullet points):
{bullet_points}

💎 **Golden Nuggets** (3 unique insights):
{golden_nuggets}

🎬 **Best Moments**:
{best_moments}

🤔 **Discussion Questions**:
{questions}

**Formatting Rules:**
- Use relevant emojis for each section
- Keep language conversational but professional
- Highlight surprising facts in bold
- Maintain original context accuracy
- Total length: 300-400 words

**Video Transcript:** {transcript}"""

# =====================================
# Core Functions
# =====================================
def extract_video_id(url):
    """Extract YouTube video ID from various URL formats"""
    try:
        parsed = urlparse(url)
        if parsed.hostname == 'youtu.be':
            return parsed.path[1:]
        if parsed.hostname in ('www.youtube.com', 'youtube.com'):
            if parsed.path == '/watch':
                return parse_qs(parsed.query)['v'][0]
            if parsed.path.startswith('/embed/'):
                return parsed.path.split('/')[2]
            if parsed.path.startswith('/v/'):
                return parsed.path.split('/')[2]
        return url.split('v=')[-1].split('&')[0]
    except:
        st.error("🔍 Couldn't extract video ID. Please check the URL format.")
        return None

def generate_ai_insights(transcript):
    """Generate formatted insights using Gemini AI"""
    try:
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(
            PROMPT_TEMPLATE.format(
                transcript=transcript,
                core_concept="[One-sentence essence]",
                bullet_points="\n- ",
                golden_nuggets="\n- ",
                best_moments="\n- ",
                questions="\n- "
            ),
            generation_config={
                "temperature": 0.7,
                "top_p": 0.95,
                "max_output_tokens": 2000
            }
        )
        return response.text
    except Exception as e:
        st.error(f"🤖 AI Error: {str(e)}")
        return None

# =====================================
# Main App Logic
# =====================================
video_url = st.text_input(
    "**Paste YouTube Video URL** 🎬",
    placeholder="https://www.youtube.com/watch?v=...",
    help="Supports all YouTube URL formats"
)

if video_url:
    # Video Preview Section
    col1, col2 = st.columns([2, 1])
    with col1:
        st.video(video_url)
    with col2:
        video_id = extract_video_id(video_url)
        if video_id:
            st.image(
                f"http://img.youtube.com/vi/{video_id}/maxresdefault.jpg",
                caption="Video Thumbnail",
                use_column_width=True
            )

    # Analysis Trigger
    if st.button("🚀 Generate Video Digest", type="primary"):
        with st.spinner("🔍 Analyzing video content..."):
            try:
                # Get Transcript
                transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
                transcript = " ".join([t['text'] for t in transcript_list])
                
                # Show progress animation
                progress_bar = st.progress(0)
                for percent in range(100):
                    time.sleep(0.02)
                    progress_bar.progress(percent + 1)
                
                # Generate AI Insights
                with st.spinner("🧠 Crafting insights..."):
                    ai_output = generate_ai_insights(transcript)
                
                if ai_output:
                    # Display Results
                    st.balloons()
                    with st.container():
                        st.markdown(f"""
                        <div class="summary-card">
                            {ai_output}
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # Download Options
                    col1, col2 = st.columns(2)
                    with col1:
                        st.download_button(
                            "📥 Download Digest",
                            ai_output,
                            file_name="video_digest.md",
                            mime="text/markdown"
                        )
                    with col2:
                        if st.button("🔄 Analyze Another Video", type="secondary"):
                            st.session_state.clear()
                            st.rerun()
                    
                    st.session_state.processed = True
                    
            except Exception as e:
                st.error(f"🚨 Error: {str(e)}")
                st.session_state.processed = False

# =====================================
# Footer Section
# =====================================
st.markdown("---")
st.markdown("""
    <div style="text-align: center; padding: 2rem 0; opacity: 0.8;">
        Made with ❤️ using Streamlit | 
        <a href="https://github.com/dhruvvkaushik/Aurelius.ai.git" target="_blank" style="color: white;">View Source Code</a>
    </div>
""", unsafe_allow_html=True)