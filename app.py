import streamlit as st
import json
import os
import plotly.graph_objects as go
import anthropic
import re as _re

from ui_text import UI_TEXT
from session_manager import init_session_state, save_data
from dashboard_renderers import render_market_dashboard, render_finance_dashboard, render_mvp_dashboard
from synthesis_agent import synthesize_analysis
from pdf_generator import generate_pdf_report

def get_lang():
    return st.session_state.get("lang_code", "en")

def generate_interview_questions(pitch: str, lang: str = "en") -> dict:
    """
    Calls Claude to classify the pitch domain and generate 3 brutal,
    deep-dive, industry-specific interview questions.
    """
    if lang == "tr":
        language_instruction = "Soruları ve Blueprint Guide örneklerini Türkçe yaz."
    else:
        language_instruction = "Write the questions and Blueprint Guides in English."

    system_prompt = (
        "You are a world-class venture capital partner conducting a brutal, high-stakes startup interview. "
        "Your job is to stress-test every assumption the founder makes. "
        "You classify the startup domain from the one-sentence pitch and ask domain-specific deep-dive questions.\n\n"
        "The Guided Adversarial Framework:\n"
        "When generating a question, you MUST generate a 2-part block:\n"
        "1. The Squeeze Question: A sharp, analytical question targeting the core technical/operational bottleneck.\n"
        "2. The Blueprint Guide: A highly contextual, technical guide showing the user exactly how a robust answer should look, filled with placeholders based on their vertical.\n\n"
        "Dynamic Vertical Forking Examples:\n"
        "- Hardware/IoT/Embedded: Focus on MCU choice, power management. Guide Output: \"Example: 'We are using STM32 MCUs communicating via SPI with a LoRaWAN module, utilizing a 3000mAh LiPo battery with sleep-mode optimization...'\"\n"
        "- Pure SaaS/Software: Focus on data pipeline scalability, API dependency. Guide Output: \"Example: 'The backend is built on FastAPI with PostgreSQL, caching hot data via Redis, and using AWS Lambda for serverless computation...'\"\n"
        "- Mechanical/Physical Toy: Focus on BOM, injection molding, wear-and-tear. Guide Output: \"Example: 'The outer shell will be manufactured via ABS injection molding, using high-torque brushless DC motors to prevent gear stripping...'\"\n\n"
        "The Anti-Bullshit Radar Boundary:\n"
        "If the user types buzzwords in their pitch (e.g. 'advanced AI', 'smart cloud', 'blockchain'), gracefully intercept by including a `buzzword_warning` in your JSON response.\n\n"
        f"{language_instruction}\n\n"
        "Output ONLY a JSON object containing a `buzzword_warning` (or null) and a `questions` array. Example:\n"
        '{\n'
        '  "buzzword_warning": "You used a generic phrase. To help our VC Engine give you a high score, replace \'advanced AI\' with the specific model or algorithm framework you intend to deploy.",\n'
        '  "questions": [\n'
        '    {\n'
        '      "question": "Data pipeline scalability question...",\n'
        '      "guide": "Example: \'The backend is built on FastAPI with PostgreSQL...\'"\n'
        '    }\n'
        '  ]\n'
        '}'
    )

    user_message = (
        f"Startup pitch: \"{pitch.strip()}\"\n\n"
        "Classify this startup's domain and generate exactly 3 brutal, specific, deep-dive interview questions (each with a Blueprint Guide). "
        "Return ONLY the requested JSON object."
    )

    try:
        client = anthropic.Anthropic()
        message = client.messages.create(
            model="claude-opus-4-5",
            max_tokens=1000,
            system=system_prompt,
            messages=[{"role": "user", "content": user_message}]
        )
        raw = message.content[0].text.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        result = json.loads(raw)
        if isinstance(result, dict) and "questions" in result:
            return result
    except Exception as e:
        print("Fallback Exception:", e)
        pass

    return {
        "buzzword_warning": None,
        "questions": UI_TEXT[lang]["questions"][:3]
    }

def extract_numeric(val, default=10):
    try:
        # Convert "8/10" to 8
        if isinstance(val, str) and "/" in val:
            val = val.split("/")[0]
        return float(val)
    except:
        return default

def main():
    lang_choice = st.sidebar.selectbox("Language / Dil", ["English", "Türkçe"], index=0)
    new_lang_code = "en" if lang_choice == "English" else "tr"
    
    if "lang_code" in st.session_state and st.session_state.lang_code != new_lang_code:
        st.session_state.lang_code = new_lang_code

    st.session_state.lang_code = new_lang_code
    init_session_state()
    
    lang = get_lang()
    t = UI_TEXT[lang]

    st.title(t["title"])

    # ──────────────────────────────────────────────────────────
    # PHASE 0 — Pitch input
    # ──────────────────────────────────────────────────────────
    if not st.session_state.pitch_submitted:
        if lang == "tr":
            pitch_label = "🚀 Startup fikrinizi tek cümleyle anlatın:"
            pitch_placeholder = "Örneğin: 'KOBİ'ler için otonom muhasebe SaaS'ı'..."
            pitch_btn = "Devam Et →"
            pitch_warning = "Lütfen startup fikrinizi giriniz."
            generating_msg = "🤖 Mülakat soruları oluşturuluyor..."
        else:
            pitch_label = "🚀 Describe your startup idea in one sentence:"
            pitch_placeholder = "e.g. 'An autonomous accounting SaaS for SMBs'..."
            pitch_btn = "Continue →"
            pitch_warning = "Please enter your startup pitch."
            generating_msg = "🤖 Generating your interview questions..."

        with st.form("pitch_form"):
            pitch_input = st.text_input(pitch_label, placeholder=pitch_placeholder)
            submitted = st.form_submit_button(pitch_btn)

        if submitted:
            if not pitch_input.strip():
                st.warning(pitch_warning)
            else:
                st.session_state.pitch_text = pitch_input.strip()
                with st.spinner(generating_msg):
                    result = generate_interview_questions(pitch_input.strip(), lang)
                st.session_state.dynamic_questions = result.get("questions", t["questions"][:3])
                st.session_state.buzzword_warning = result.get("buzzword_warning", None)
                st.session_state.pitch_submitted = True
                st.rerun()
        return

    # ──────────────────────────────────────────────────────────
    # PHASE 1 — Interview
    # ──────────────────────────────────────────────────────────
    active_questions = st.session_state.dynamic_questions
    MIN_ANSWER_LEN = 40

    if not st.session_state.interview_complete:
        st.markdown("---")
        
        if st.session_state.buzzword_warning:
            st.warning(f"🚨 **Anti-Bullshit Radar:** {st.session_state.buzzword_warning}")
            
        draft_answers = []
        all_valid = True

        for i, q_obj in enumerate(active_questions):
            question_text = q_obj.get("question", str(q_obj))
            guide_text = q_obj.get("guide", "")
            
            st.markdown(f"**Q{i+1}. {question_text}**")
            ans = st.text_area(
                label=f"answer_{i+1}",
                label_visibility="collapsed",
                key=f"draft_answer_{i}",
                height=120,
                placeholder=t["chat_placeholder"]
            )
            draft_answers.append(ans)
            
            if guide_text:
                st.info(f"💡 {guide_text}")
                
            if ans.strip() and len(ans.strip()) < MIN_ANSWER_LEN:
                st.warning(t["answer_too_short"])
                all_valid = False
            elif not ans.strip():
                all_valid = False
            st.markdown("")

        if st.button(t["submit_answers"], disabled=not all_valid, type="primary"):
            st.session_state.answers = [a.strip() for a in draft_answers]
            save_data(st.session_state.answers)
            st.session_state.interview_complete = True
            st.rerun()
        return

    # ──────────────────────────────────────────────────────────
    # PHASE 2 — Analysis
    # ──────────────────────────────────────────────────────────
    analyses_unlocked = len(st.session_state.answers) >= len(active_questions)
    st.success(t["success_saved"])

    if not analyses_unlocked:
        st.info(t["analysis_locked"])
        
    c1, c2, c3, c4 = st.columns(4)
        
    with c1:
        if st.button(t["btn_market"], use_container_width=True, disabled=not analyses_unlocked):
            with st.spinner(t["spin_market"]):
                from market_analyzer import analyze_market
                st.session_state.market_analysis = analyze_market(lang=lang)

    with c2:
        if st.button(t["btn_finance"], use_container_width=True, disabled=not analyses_unlocked):
            with st.spinner(t["spin_finance"]):
                from finance_analyzer import analyze_finance
                st.session_state.finance_analysis = analyze_finance(lang=lang)

    with c3:
        if st.button(t["btn_mvp"], use_container_width=True, disabled=not analyses_unlocked):
            with st.spinner(t["spin_mvp"]):
                from mvp_architect import analyze_mvp
                st.session_state.mvp_analysis = analyze_mvp(lang=lang)

    all_done = ("market_analysis" in st.session_state and 
                "finance_analysis" in st.session_state and 
                "mvp_analysis" in st.session_state)

    with c4:
        if st.button(t["btn_synthesis"], use_container_width=True, disabled=not all_done):
            with st.spinner(t["spin_synthesis"]):
                st.session_state.synthesis_analysis = synthesize_analysis(lang=lang)
            
    if "market_analysis" in st.session_state:
        render_market_dashboard(lang, st.session_state.market_analysis)

    if "finance_analysis" in st.session_state:
        render_finance_dashboard(lang, st.session_state.finance_analysis)

    if "mvp_analysis" in st.session_state:
        render_mvp_dashboard(lang, st.session_state.mvp_analysis)

    if "synthesis_analysis" in st.session_state:
        syn = st.session_state.synthesis_analysis
        st.markdown("---")
        st.subheader(t["synthesis_dashboard"])
        
        if "hata" in syn or "error" in syn:
            st.error(syn.get("hata", syn.get("error")))
        else:
            st.error(t["synthesis_contradiction"].format(syn.get("biggest_contradiction", "")))
            st.success(t["synthesis_signal"].format(syn.get("strongest_signal", "")))
            
            st.markdown(t["synthesis_critical_path"])
            for i, p in enumerate(syn.get("critical_path", []), 1):
                st.markdown(f"{i}. {p}")

    # ──────────────────────────────────────────────────────────
    # PHASE 3 — VC Summary (Radar Chart) & PDF Export
    # ──────────────────────────────────────────────────────────
    if all_done:
        st.markdown("---")
        st.subheader(t["vc_summary"])
        
        m_data = st.session_state.market_analysis
        f_data = st.session_state.finance_analysis
        mvp_data = st.session_state.mvp_analysis
        
        if not ("error" in m_data or "error" in f_data or "error" in mvp_data):
            # Calculate Scores (0-100 scale)
            # Market Opportunity: Give 80 baseline + up to 20 depending on density
            mo_score = 80
            density = m_data.get("Market_Metrics", {}).get("Market_Density", "").lower()
            if "blue" in density or "mavi" in density: mo_score = 95
            elif "red" in density or "kırmızı" in density: mo_score = 65
            
            # Competitive Moat: (0-10) -> (0-100)
            moat_score = extract_numeric(m_data.get("Moat_Analysis", {}).get("replication_difficulty_score", 5)) * 10
            
            # Financial Viability: already 0-100
            fin_score = extract_numeric(f_data.get("Investment_Score", 50))
            
            # Execution Speed: (10 - complexity) * 10
            comp = extract_numeric(mvp_data.get("Complexity_Score", 5))
            exec_score = max(0, (10 - comp)) * 10
            
            # Regulatory Safety: 100 - (count of risks * 20)
            reg_risks = m_data.get("Regulatory_Risks", [])
            reg_score = max(0, 100 - (len(reg_risks) * 20))
            
            categories = ['Market Opportunity', 'Competitive Moat', 'Financial Viability', 'Execution Speed', 'Regulatory Safety']
            scores = [mo_score, moat_score, fin_score, exec_score, reg_score]
            
            fig = go.Figure()
            fig.add_trace(go.Scatterpolar(
                r=scores + [scores[0]],
                theta=categories + [categories[0]],
                fill='toself',
                name='VC Intelligence'
            ))
            fig.update_layout(
                polar=dict(
                    radialaxis=dict(visible=True, range=[0, 100])
                ),
                showlegend=False
            )
            st.plotly_chart(fig, use_container_width=True)
            
            avg_score = sum(scores) / len(scores)
            st.metric("Overall VC Score", f"{avg_score:.1f}/100")
            
            if avg_score >= 75:
                st.success(t["vc_verdict_strong"])
            elif avg_score >= 50:
                st.warning(t["vc_verdict_conditional"])
            else:
                st.error(t["vc_verdict_weak"])

        # PDF Export Button
        if st.button(t["btn_pdf"], type="primary"):
            pitch = st.session_state.get("pitch_text", "")
            synthesis = st.session_state.get("synthesis_analysis", {})
            pdf_buffer = generate_pdf_report(pitch, m_data, f_data, mvp_data, synthesis)
            st.download_button(
                label="⬇️ Download PDF",
                data=pdf_buffer,
                file_name="vc_due_diligence_report.pdf",
                mime="application/pdf"
            )
            st.success(t["pdf_success"])

if __name__ == "__main__":
    main()
