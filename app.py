import streamlit as st
import json
import os
import anthropic

UI_TEXT = {
    "en": {
        "title": "AI Startup Analyst - Interview Phase",
        "questions": [
            "What is your startup idea and what specific problem does it solve?",
            "Who is your exact target niche market and user base initially?",
            "Who are your 2-3 biggest competitors currently trying to solve this problem, and how will you differentiate?",
            "How do you plan to make money from this startup? (SaaS, commission, marketplace, etc.)",
            "If you wanted to test this product as quickly and cheaply as possible (without coding or with minimal code), what would be the first core feature you'd offer?"
        ],
        "success_saved": "Thank you! Your data has been saved. Analysis agents are ready to run.",
        "btn_market": "📊 Start Market Analysis",
        "btn_finance": "💰 Start Financial Analysis",
        "btn_mvp": "🚀 Generate MVP Roadmap",
        "spin_market": "Conducting market research on the internet...",
        "spin_finance": "Modeling financial data...",
        "spin_mvp": "Creating MVP strategy...",
        "market_dashboard": "📊 Market Analysis Dashboard",
        "market_unknown": "Unknown",
        "market_uptrend": "Uptrend",
        "market_density_red": "**WARNING:** This market is quite congested and highly competitive (Red Ocean). You must carefully define your entry strategy.\n\n_Detail: {}_",
        "market_density_blue": "**OPPORTUNITY:** This market has low competition (Blue Ocean). You can leverage the first-mover advantage.\n\n_Detail: {}_",
        "market_density_info": "**Market Density:** {}",
        "market_funnel_title": "Market Size Funnel Analysis",
        "market_note": "### 📝 Analyst Note",
        "market_metrics_hdr": "### 📐 Market Metrics",
        "market_source": "🔍 Source / Assumption",
        "market_comp_hdr": "### ⚔️ Competitor Intelligence",
        "market_comp_weakness": "**Structural Weakness:**",
        "market_comp_window": "**Exploit Window:**",
        "market_reg_hdr": "### ⚖️ Regulatory Risks",
        "market_reg_impact": "**Impact:**",
        "market_reg_mitigation": "**Mitigation:**",
        "finance_dashboard": "💰 Financial Analysis Results",
        "finance_score": "Investment Score",
        "finance_ltv_cac": "LTV/CAC Estimate",
        "finance_capital": "Capital Intensity",
        "finance_ltv_comment": "**LTV/CAC Comment:** {}",
        "finance_capital_detail": "**Capital Requirement Detail:** {}",
        "finance_red_flags": "### 🚩 Red Flags & Risks",
        "mvp_dashboard": "🚀 MVP Roadmap & Founder Sprint",
        "mvp_complexity": "**Complexity Score:** `{}`",
        "mvp_time_to_market": "**⏳ Estimated Time-to-Market:** `{}`",
        "mvp_focus": "### ✅ Focus Features (Day-1)",
        "mvp_cut": "### ❌ Cut Features (For Now)",
        "mvp_tech": "### 🛠️ Tech & Tool Recommendations",
        "mvp_sprint": "### 📅 Founder Sprint (To-Do List)",
        "chat_placeholder": "Type your answer here...",
        "answer_too_short": "This answer is too brief for a proper VC-grade analysis. Please provide more concrete strategy details.",
        "analysis_locked": "Complete the interview with substantive answers to unlock analysis.",
        "submit_answers": "Submit Answers",
        "run_analysis": "Run Analysis"
    },
    "tr": {
        "title": "AI Startup Analisti - Mülakat Aşaması",
        "questions": [
            "Startup fikriniz nedir ve hangi spesifik problemi çözüyor?",
            "İlk etapta hedeflediğiniz niş pazar ve kullanıcı kitlesi tam olarak kimler?",
            "Şu an bu problemi çözmeye çalışan en büyük 2-3 rakibiniz kim ve siz onlardan nasıl farklılaşacaksınız?",
            "Bu girişimden nasıl para kazanmayı planlıyorsunuz? (SaaS, komisyon, pazaryeri vb.)",
            "Bu ürünü en hızlı ve en ucuz şekilde (kodlamadan veya minimal kodla) test etmek isteseniz, sunacağınız ilk temel özellik ne olurdu?"
        ],
        "success_saved": "Teşekkürler! Verileriniz kaydedildi. Analiz ajanları çalışmaya hazır.",
        "btn_market": "📊 Pazar Analizini Başlat",
        "btn_finance": "💰 Finansal Analizi Başlat",
        "btn_mvp": "🚀 MVP Yol Haritasını Çıkar",
        "spin_market": "İnternette pazar araştırması yapılıyor...",
        "spin_finance": "Finansal veriler modelleniyor...",
        "spin_mvp": "MVP stratejisi oluşturuluyor...",
        "market_dashboard": "📊 Pazar Analizi Dashboard",
        "market_unknown": "Bilinmiyor",
        "market_uptrend": "Yükseliş Trendi",
        "market_density_red": "**DİKKAT:** Bu pazar oldukça sıkışık ve rekabet yüksek (Kırmızı Okyanus). Giriş stratejinizi çok iyi belirlemelisiniz.\n\n_Detay: {}_",
        "market_density_blue": "**FIRSAT:** Bu pazar düşük rekabet barındırıyor (Mavi Okyanus). İlk hamle avantajını kullanabilirsiniz.\n\n_Detay: {}_",
        "market_density_info": "**Pazar Yoğunluğu:** {}",
        "market_funnel_title": "Pazar Büyüklüğü Huni (Funnel) Analizi",
        "market_note": "### 📝 Analist Notu",
        "market_metrics_hdr": "### 📐 Pazar Metrikleri",
        "market_source": "🔍 Kaynak / Varsayım",
        "market_comp_hdr": "### ⚔️ Rakip İstihbarat Analizi",
        "market_comp_weakness": "**Yapısal Zayıflık:**",
        "market_comp_window": "**Fırsat Penceresi:**",
        "market_reg_hdr": "### ⚖️ Düzenleyici Riskler",
        "market_reg_impact": "**Etki:**",
        "market_reg_mitigation": "**Azaltma Stratejisi:**",
        "finance_dashboard": "💰 Finansal Analiz Sonuçları",
        "finance_score": "Yatırım Skoru",
        "finance_ltv_cac": "LTV/CAC Tahmini",
        "finance_capital": "Sermaye Yoğunluğu",
        "finance_ltv_comment": "**LTV/CAC Yorumu:** {}",
        "finance_capital_detail": "**Sermaye İhtiyacı Detayı:** {}",
        "finance_red_flags": "### 🚩 Kırmızı Bayraklar & Riskler",
        "mvp_dashboard": "🚀 MVP Yol Haritası & Kurucu Sprinti",
        "mvp_complexity": "**Karmaşıklık Skoru:** `{}`",
        "mvp_time_to_market": "**⏳ Tahmini Pazara Çıkış Süresi:** `{}`",
        "mvp_focus": "### ✅ Odaklanılacak Özellikler (Day-1)",
        "mvp_cut": "### ❌ Elenen Özellikler (Şimdilik)",
        "mvp_tech": "### 🛠️ Teknoloji & Araç Önerileri",
        "mvp_sprint": "### 📅 Kurucu Sprinti (To-Do List)",
        "chat_placeholder": "Cevabınızı buraya yazın...",
        "answer_too_short": "Bu cevap profesyonel bir analiz için çok yüzeysel. Lütfen stratejiniz hakkında daha somut detaylar verin.",
        "analysis_locked": "Analizi açmak için tüm soruları yeterli detayla yanıtlayın.",
        "submit_answers": "Cevapları Gönder",
        "run_analysis": "Analizi Başlat"
    }
}

def get_lang():
    return st.session_state.get("lang_code", "en")


def generate_interview_questions(pitch: str, lang: str = "en") -> list[str]:
    """
    Calls Claude to classify the pitch domain and generate 3 brutal,
    deep-dive, industry-specific interview questions.

    Domain rules:
      - deep-tech / hardware / robotics  → R&D bottlenecks & technical feasibility
      - e-commerce / physical products   → unit economics, margins, supply chain
      - SaaS                             → churn, integration, retention
      - other                            → go-to-market, moat, traction
    """
    if lang == "tr":
        language_instruction = "Soruları Türkçe yaz."
        fallback_intro = "Startup fikriniz için 3 sert mülakat sorusu:"
    else:
        language_instruction = "Write the questions in English."
        fallback_intro = "3 brutal interview questions for your startup idea:"

    system_prompt = (
        "You are a world-class venture capital partner conducting a brutal, high-stakes startup interview. "
        "Your job is to stress-test every assumption the founder makes. "
        "You classify the startup domain from the one-sentence pitch and ask domain-specific deep-dive questions.\n\n"
        "Domain classification rules:\n"
        "  - deep-tech / hardware / robotics / biotech / defense → focus on R&D bottlenecks, IP moat, technical feasibility, regulatory path\n"
        "  - e-commerce / physical products / retail / marketplace → focus on unit economics, gross margins, supply chain resilience, CAC vs LTV\n"
        "  - SaaS / B2B software / platform → focus on churn drivers, integration complexity, switching costs, expansion revenue\n"
        "  - other (consumer app, media, fintech, etc.) → focus on go-to-market moat, network effects, regulatory risk, monetization defensibility\n\n"
        f"{language_instruction}\n\n"
        "Output ONLY a JSON array of exactly 3 strings, no keys, no markdown, no explanation. Example:\n"
        '["Question 1?", "Question 2?", "Question 3?"]'
    )

    user_message = (
        f"Startup pitch: \"{pitch.strip()}\"\n\n"
        "Classify this startup's domain and generate exactly 3 brutal, specific, deep-dive interview questions "
        "that target the most critical failure points for this domain. "
        "Make them uncomfortable. Each question must be answerable with concrete data, not vague ideas. "
        "Return ONLY a JSON array of 3 question strings."
    )

    try:
        client = anthropic.Anthropic()
        message = client.messages.create(
            model="claude-opus-4-5",
            max_tokens=600,
            system=system_prompt,
            messages=[{"role": "user", "content": user_message}]
        )
        raw = message.content[0].text.strip()
        # Strip any accidental markdown code fences
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        questions = json.loads(raw)
        if isinstance(questions, list) and len(questions) == 3:
            return questions
    except Exception:
        pass  # Fall through to fallback

    # Fallback: return static questions for the language
    return UI_TEXT[lang]["questions"][:3]

def init_session_state():
    if "lang_code" not in st.session_state:
        st.session_state.lang_code = "en"
    # Phase flags
    if "pitch_submitted" not in st.session_state:
        st.session_state.pitch_submitted = False
    if "dynamic_questions" not in st.session_state:
        st.session_state.dynamic_questions = []
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
            f"q{i+1}": {"question": questions_used[i], "answer": answers[i]}
            for i in range(min(len(questions_used), len(answers)))
        }
    }
    with open("data/startup_data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def main():
    # Sidebar language toggle
    lang_choice = st.sidebar.selectbox("Language / Dil", ["English", "Türkçe"], index=0)
    new_lang_code = "en" if lang_choice == "English" else "tr"
    
    if "lang_code" in st.session_state and st.session_state.lang_code != new_lang_code:
        st.session_state.lang_code = new_lang_code
        # Optionally, update the last question in the chat history to match the new language
        if len(st.session_state.chat_history) > 0 and st.session_state.chat_history[-1]["role"] == "assistant":
            idx = st.session_state.current_question_idx
            if idx < len(UI_TEXT[new_lang_code]["questions"]):
                st.session_state.chat_history[-1]["content"] = UI_TEXT[new_lang_code]["questions"][idx]

    st.session_state.lang_code = new_lang_code
    init_session_state()
    
    lang = get_lang()
    t = UI_TEXT[lang]

    st.title(t["title"])

    # ──────────────────────────────────────────────────────────
    # PHASE 0 — Pitch input (runs before the interview starts)
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
                    questions = generate_interview_questions(pitch_input.strip(), lang)
                st.session_state.dynamic_questions = questions
                st.session_state.pitch_submitted = True
                # Seed the chat history with the first dynamic question
                st.session_state.chat_history = [
                    {"role": "assistant", "content": questions[0]}
                ]
                st.rerun()
        return  # Don't render the rest until pitch is done

    # ──────────────────────────────────────────────────────────
    # PHASE 1 — Interview using dynamic questions (form layout)
    # ──────────────────────────────────────────────────────────
    active_questions = st.session_state.dynamic_questions
    MIN_ANSWER_LEN = 40

    if not st.session_state.interview_complete:
        st.markdown("---")
        # Collect live draft answers from text areas
        draft_answers = []
        all_valid = True

        for i, question in enumerate(active_questions):
            st.markdown(f"**Q{i+1}. {question}**")
            ans = st.text_area(
                label=f"answer_{i+1}",
                label_visibility="collapsed",
                key=f"draft_answer_{i}",
                height=120,
                placeholder=t["chat_placeholder"]
            )
            draft_answers.append(ans)
            # Per-field validation warning
            if ans.strip() and len(ans.strip()) < MIN_ANSWER_LEN:
                st.warning(t["answer_too_short"])
                all_valid = False
            elif not ans.strip():
                all_valid = False
            st.markdown("")

        # Submit button — disabled when any answer is too short or empty
        if st.button(t["submit_answers"], disabled=not all_valid, type="primary"):
            st.session_state.answers = [a.strip() for a in draft_answers]
            save_data(st.session_state.answers)
            st.session_state.interview_complete = True
            st.rerun()
        return

    # ── All answers submitted — show analysis section ──────────
    analyses_unlocked = len(st.session_state.answers) >= len(active_questions)

    st.success(t["success_saved"])

    if not analyses_unlocked:
        st.info(t["analysis_locked"])
        
    col1, col2, col3 = st.columns(3)
        
    with col1:
        if st.button(t["btn_market"], use_container_width=True, disabled=not analyses_unlocked):
            with st.spinner(t["spin_market"]):
                from market_analyzer import analyze_market
                st.session_state.market_analysis = analyze_market(lang=lang)

    with col2:
        if st.button(t["btn_finance"], use_container_width=True, disabled=not analyses_unlocked):
            with st.spinner(t["spin_finance"]):
                from finance_analyzer import analyze_finance
                st.session_state.finance_analysis = analyze_finance(lang=lang)

    with col3:
        if st.button(t["btn_mvp"], use_container_width=True, disabled=not analyses_unlocked):
            with st.spinner(t["spin_mvp"]):
                from mvp_architect import analyze_mvp
                st.session_state.mvp_analysis = analyze_mvp(lang=lang)
            
    if "market_analysis" in st.session_state:
        st.markdown("---")
        st.subheader(t["market_dashboard"])
        m_data = st.session_state.market_analysis

        if "hata" in m_data or "error" in m_data:
            st.error(m_data.get("hata", m_data.get("error")))
        else:
            import plotly.graph_objects as go
            import re as _re

            def _extract_val(s):
                nums = _re.findall(r'\d+(?:\.\d+)?', str(s).replace(',', ''))
                if nums:
                    v = float(nums[0])
                    if any(x in str(s) for x in ('B', 'Milyar', 'Billion', 'T', 'Trillion')):
                        v *= 1000
                    return v
                return 10

            # ── Detect new 3-layer vs. legacy flat structure ──────────────
            metrics    = m_data.get("Market_Metrics")
            comp_flaws = m_data.get("Competitor_Flaws", [])
            reg_risks  = m_data.get("Regulatory_Risks", [])

            if metrics:  # ── NEW institutional format ──────────────────────
                tam_obj  = metrics.get("TAM", {})
                sam_obj  = metrics.get("SAM", {})
                som_obj  = metrics.get("SOM", {})
                cagr_obj = metrics.get("CAGR", {})
                density  = metrics.get("Market_Density", "")

                tam  = tam_obj.get("value",  t["market_unknown"])
                sam  = sam_obj.get("value",  t["market_unknown"])
                som  = som_obj.get("value",  t["market_unknown"])
                cagr = cagr_obj.get("value", t["market_unknown"])

                # 1. KPI Cards
                st.markdown(t["market_metrics_hdr"])
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("TAM",  tam.split()[0]  if tam  else "-")
                c2.metric("SAM",  sam.split()[0]  if sam  else "-")
                c3.metric("SOM",  som.split()[0]  if som  else "-")
                c4.metric("CAGR", cagr.split()[0] if cagr else "-", delta=t["market_uptrend"])

                # Source notes
                with st.expander(t["market_source"]):
                    for label, obj in [("TAM", tam_obj), ("SAM", sam_obj), ("SOM", som_obj), ("CAGR", cagr_obj)]:
                        scope = obj.get("scope", obj.get("period", ""))
                        src   = obj.get("source_assumption", "")
                        st.markdown(f"**{label}** — _{scope}_  \n`{src}`")

                # 2. Market Density
                d_lower = density.lower()
                if "red" in d_lower or "kırmızı" in d_lower:
                    st.error(t["market_density_red"].format(density))
                elif "blue" in d_lower or "mavi" in d_lower:
                    st.success(t["market_density_blue"].format(density))
                else:
                    st.info(t["market_density_info"].format(density))

                # 3. Funnel Chart
                fig = go.Figure(go.Funnel(
                    y=["TAM", "SAM", "SOM"],
                    x=[_extract_val(tam), _extract_val(sam), _extract_val(som)],
                    text=[tam, sam, som],
                    textinfo="text",
                    marker={"color": ["#004c6d", "#00839a", "#00c0a3"]}
                ))
                fig.update_layout(title=t["market_funnel_title"], margin=dict(t=40, l=20, r=20, b=20))
                st.plotly_chart(fig, use_container_width=True)

                # 4. Competitor Flaws
                if comp_flaws:
                    st.markdown(t["market_comp_hdr"])
                    for cf in comp_flaws:
                        name = cf.get("competitor", "Unknown")
                        with st.expander(f"🎯 {name}"):
                            st.markdown(f"{t['market_comp_weakness']} {cf.get('known_weakness', '-')}")
                            st.markdown(f"{t['market_comp_window']} {cf.get('exploit_window', '-')}")

                # 5. Regulatory Risks
                if reg_risks:
                    st.markdown(t["market_reg_hdr"])
                    for rr in reg_risks:
                        reg_name = rr.get("regulation", "Unknown regulation")
                        with st.expander(f"⚖️ {reg_name}"):
                            st.warning(f"{t['market_reg_impact']} {rr.get('impact', '-')}")
                            st.info(f"{t['market_reg_mitigation']} {rr.get('mitigation', '-')}")

            else:  # ── Legacy flat format (backward compat) ─────────────────
                tam  = m_data.get("TAM_Total_Addressable_Market",      t["market_unknown"])
                sam  = m_data.get("SAM_Serviceable_Addressable_Market", t["market_unknown"])
                som  = m_data.get("SOM_Serviceable_Obtainable_Market",  t["market_unknown"])
                cagr = m_data.get("CAGR_Market_Growth_Rate", m_data.get("CAGR_Pazar_Buyume_Orani", t["market_unknown"]))
                density = m_data.get("Market_Density", m_data.get("Market_Density_Pazar_Yogunlugu", ""))
                note    = m_data.get("Summary_Research_Note", m_data.get("Ozet_Arastirma_Notu", ""))

                c1, c2, c3, c4 = st.columns(4)
                c1.metric("TAM",  tam.split()[0]  if tam  else "-")
                c2.metric("SAM",  sam.split()[0]  if sam  else "-")
                c3.metric("SOM",  som.split()[0]  if som  else "-")
                c4.metric("CAGR", cagr.split()[0] if cagr else "-", delta=t["market_uptrend"])

                d_lower = density.lower()
                if "red" in d_lower or "kırmızı" in d_lower:
                    st.error(t["market_density_red"].format(density))
                elif "blue" in d_lower or "mavi" in d_lower:
                    st.success(t["market_density_blue"].format(density))
                else:
                    st.info(t["market_density_info"].format(density))

                fig = go.Figure(go.Funnel(
                    y=["TAM", "SAM", "SOM"],
                    x=[_extract_val(tam), _extract_val(sam), _extract_val(som)],
                    text=[tam, sam, som],
                    textinfo="text",
                    marker={"color": ["#004c6d", "#00839a", "#00c0a3"]}
                ))
                fig.update_layout(title=t["market_funnel_title"], margin=dict(t=40, l=20, r=20, b=20))
                st.plotly_chart(fig, use_container_width=True)

                if note:
                    st.markdown(t["market_note"])
                    st.info(note)

    if "finance_analysis" in st.session_state:
        st.subheader(t["finance_dashboard"])
        f_data = st.session_state.finance_analysis

        if "hata" in f_data or "error" in f_data:
            st.error(f_data.get("hata", f_data.get("error")))
        else:
            score = f_data.get("Investment_Score", f_data.get("Yatirim_Skoru", 0))

            # Metric cols
            m1, m2, m3 = st.columns(3)
            m1.metric(t["finance_score"], f"{score}/100")
            m2.metric(t["finance_ltv_cac"], f_data.get("LTV_CAC_Estimate", f_data.get("LTV_CAC_Tahmini", "-")))
            m3.metric(t["finance_capital"], f_data.get("Capital_Intensity", f_data.get("Sermaye_Yogunlugu", "-")).split()[0])

            ltv_comment = f_data.get('LTV_CAC_Comment', f_data.get('LTV_CAC_Yorumu', ''))
            cap_detail = f_data.get('Capital_Intensity', f_data.get('Sermaye_Yogunlugu', ''))
            st.info(t["finance_ltv_comment"].format(ltv_comment))
            st.info(t["finance_capital_detail"].format(cap_detail))

            st.markdown(t["finance_red_flags"])
            red_flags = f_data.get("Red_Flags", f_data.get("Kirmizi_Bayraklar", []))
            for flag in red_flags:
                if "🚨" in flag:
                    st.error(flag)
                elif "⚠️" in flag:
                    st.warning(flag)
                else:
                    st.success(flag)

    if "mvp_analysis" in st.session_state:
        st.markdown("---")
        st.subheader(t["mvp_dashboard"])
        m_data = st.session_state.mvp_analysis

        if "hata" in m_data or "error" in m_data:
            st.error(m_data.get("hata", m_data.get("error")))
        else:
            complexity_score = m_data.get('Complexity_Score', m_data.get('Karmasiklik_Skoru', ''))
            complexity_reason = m_data.get('Complexity_Reasoning', m_data.get('Karmasiklik_Gerekcesi', ''))
            ttm = m_data.get('Time_to_Market', m_data.get('Pazara_Cikis_Suresi', ''))

            st.markdown(t["mvp_complexity"].format(complexity_score))
            st.info(complexity_reason)

            st.markdown(t["mvp_time_to_market"].format(ttm))

            col_a, col_b = st.columns(2)
            with col_a:
                st.markdown(t["mvp_focus"])
                focus_feats = m_data.get("MVP_Focus_Features", m_data.get("MVP_Odak_Ozellikler", []))
                for feat in focus_feats:
                    st.markdown(f"- {feat}")
            with col_b:
                st.markdown(t["mvp_cut"])
                cut_feats = m_data.get("MVP_Cut_Features", m_data.get("MVP_Elenen_Ozellikler", []))
                for feat in cut_feats:
                    st.markdown(f"- {feat}")

            st.markdown(t["mvp_tech"])
            techs = m_data.get("Tech_Recommendations", m_data.get("Teknoloji_Onerileri", []))
            for tech in techs:
                st.markdown(f"- {tech}")

            st.markdown(t["mvp_sprint"])
            sprint_plan = m_data.get("Founder_Sprint_Plan", m_data.get("Kurucu_Sprint_Plani", []))
            for i, sprint in enumerate(sprint_plan):
                with st.expander(sprint["week"], expanded=True):
                    for j, task in enumerate(sprint["tasks"]):
                        st.checkbox(task, key=f"sprint_{i}_task_{j}")

if __name__ == "__main__":
    main()
