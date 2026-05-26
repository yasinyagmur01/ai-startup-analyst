import streamlit as st
import os
import json
from ui_text import UI_TEXT

def init_session_state():
    if "lang_code" not in st.session_state:
        st.session_state.lang_code = "en"
    # Phase flags
    if "pitch_submitted" not in st.session_state:
        st.session_state.pitch_submitted = False
    if "dynamic_questions" not in st.session_state:
        st.session_state.dynamic_questions = []
    if "buzzword_warning" not in st.session_state:
        st.session_state.buzzword_warning = None
    if "answers" not in st.session_state:
        st.session_state.answers = []
    if "interview_complete" not in st.session_state:
        st.session_state.interview_complete = False

def save_data(answers):
    """Persist interview answers. Uses dynamic questions when available."""
    os.makedirs("data", exist_ok=True)
    # Prefer dynamic questions generated for this session
    questions_used = st.session_state.get("dynamic_questions") or UI_TEXT["en"]["questions"]
    pitch = st.session_state.get("pitch_text", "")
    data = {
        "pitch": pitch,
        **{
            f"q{i+1}": {"question": questions_used[i].get("question", str(questions_used[i])), "answer": answers[i]}
            for i in range(min(len(questions_used), len(answers)))
        }
    }
    with open("data/startup_data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
