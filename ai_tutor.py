import streamlit as st
from streamlit.components.v1 import html
import time
import os
import re
from dotenv import load_dotenv
import google.generativeai as genai
from pydantic import BaseModel

GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
if not GOOGLE_API_KEY:
    st.error("⚠️ Google GenAI API key is missing!.")
    st.stop()
    
model = genai.GenerativeModel(
    "gemini-1.5-pro",
    system_instruction="You're an expert AI tutor who ONLY answers questions related to AI, ML, DL, Python, and Data Science. "
                       "Always answer clearly and in details. You never answer anything outside this domain. "
                       "If asked an unrelated question, politely redirect to AI topics."
)


# ============ Chat History ============
if "history" not in st.session_state:
    st.session_state.history = []

# ============ Theme State ============
if "theme" not in st.session_state:
    st.session_state.theme = "dark"

# ============ Domain Validation ============
class Query(BaseModel):
    text: str

    def is_relevant(self) -> bool:
        keywords = [
            "data", "information", "data science", "machine learning", "deep learning", "neural network",
            "AI", "artificial intelligence", "python", "pandas", "numpy", "regression",
            "classification", "nlp", "natural language processing", "llm", "generative",
            "data analysis", "statistics", "EDA", "SQL", "big data", "analytics"
        ]
        return any(word in self.text.lower() for word in keywords)

# ============ UI Styles ============
st.markdown(
    f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@600&display=swap');

    html, body, .stApp {{
        background: {'linear-gradient(145deg, #0A1D37, #0F2745, #071829)' if st.session_state.theme == 'dark' else '#F0F0F0'};
        background-size: 400% 400%;
        animation: gradientShift 20s ease infinite;
        color: {'#EDEDED' if st.session_state.theme == 'dark' else '#000000'};
        font-family: 'Orbitron', sans-serif;
    }}

    @keyframes gradientShift {{
        0% {{background-position: 0% 50%;}}
        50% {{background-position: 100% 50%;}}
        100% {{background-position: 0% 50%;}}
    }}

    div.stButton > button {{
        background-color: #102542;
        color: #F5F5F5;
        padding: 0.6em 1.4em;
        font-size: 16px;
        border-radius: 12px;
        border: none;
        box-shadow: 0 0 10px #1C64F2;
        transition: all 0.3s ease;
    }}

    div.stButton > button:hover {{
        background-color: #1C4C8B;
        box-shadow: 0 0 20px #8AB6F9;
        transform: scale(1.05);
    }}

    .custom-response {{
        background-color: #0B3D91;
        padding: 20px;
        border-radius: 16px;
        color: #F5F5F5;
        font-size: 17px;
        line-height: 1.7;
        box-shadow: 0 0 20px rgba(0, 153, 255, 0.4);
        animation: float 3s ease-in-out infinite;
        text-shadow: 0 0 8px #8AB6F9;
        transition: all 0.3s ease-in-out;
    }}

    @keyframes float {{
        0%   {{ transform: translateY(0px); }}
        50%  {{ transform: translateY(-5px); }}
        100% {{ transform: translateY(0px); }}
    }}

    .custom-header {{
        color: #93F9B9;
        text-align: center;
        font-size: 42px;
        padding: 10px;
        margin-top: -30px;
        text-shadow: 0 0 10px #5FFFD9, 0 0 20px #5FFFD9;
        animation: glowPulse 3s infinite alternate;
    }}

    @keyframes glowPulse {{
        from {{ text-shadow: 0 0 10px #5FFFD9, 0 0 20px #5FFFD9; }}
        to {{ text-shadow: 0 0 20px #C3F5F5, 0 0 30px #8AB6F9; }}
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# ============ App Title ============
st.markdown("<h1 class='custom-header'>🤖 Your Own Data Science Tutor</h1>", unsafe_allow_html=True)

# ============ Theme Toggle ============
with st.sidebar:
    theme_option = st.radio("Choose Theme", ["dark", "light"], index=["dark", "light"].index(st.session_state.theme))
    if theme_option != st.session_state.theme:
        st.session_state.theme = theme_option
        st.rerun()  # Refresh to apply theme immediately without resetting chat

    if st.button("Reset Chat History"):
        st.session_state.history = []


# ============ User Input ============
user_input = st.text_area("Ask a data science question:", key="input")

if st.button("Ask the Tutor") and user_input:
    query = Query(text=user_input)
    with st.spinner("Summonning the DATA GODS 🧠✨"):
        if query.is_relevant():
            response = model.generate_content(user_input).text
        else:
            response = "I do respect and appreciate your curiosity but sorry it's not my expertise so I'm out."
    st.session_state.history.append((user_input, response))
    st.success("Here's what I think:")
    st.markdown(f"<div class='custom-response'>{response}</div>", unsafe_allow_html=True)

# ============ Chat History Display ============
st.markdown("\n---\n")
st.subheader("Previous Chats")
for user_q, ai_r in st.session_state.history:
    st.markdown(f"**You asked:** {user_q}")
    st.markdown(f"<div class='custom-response'>{ai_r}</div>", unsafe_allow_html=True)
    st.markdown("---")
