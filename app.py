import streamlit as st
import json
import os

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
        "chat_placeholder": "Type your answer here..."
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
        "chat_placeholder": "Cevabınızı buraya yazın..."
    }
}

def get_lang():
    return st.session_state.get("lang_code", "en")

def init_session_state():
    if "lang_code" not in st.session_state:
        st.session_state.lang_code = "en"
    if "current_question_idx" not in st.session_state:
        st.session_state.current_question_idx = 0
    if "answers" not in st.session_state:
        st.session_state.answers = []
    if "chat_history" not in st.session_state:
        lang = st.session_state.lang_code
        st.session_state.chat_history = [{"role": "assistant", "content": UI_TEXT[lang]["questions"][0]}]

def save_data(answers):
    os.makedirs("data", exist_ok=True)
    lang = get_lang()
    data = {
        f"q{i+1}": {"question": UI_TEXT["en"]["questions"][i], "answer": answers[i]}
        for i in range(len(UI_TEXT["en"]["questions"]))
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

    # Display chat history
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # If all questions are answered
    if st.session_state.current_question_idx >= len(t["questions"]):
        st.success(t["success_saved"])
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button(t["btn_market"], use_container_width=True):
                with st.spinner(t["spin_market"]):
                    from market_analyzer import analyze_market
                    st.session_state.market_analysis = analyze_market(lang=lang)
                    
        with col2:
            if st.button(t["btn_finance"], use_container_width=True):
                with st.spinner(t["spin_finance"]):
                    from finance_analyzer import analyze_finance
                    st.session_state.finance_analysis = analyze_finance(lang=lang)
                    
        with col3:
            if st.button(t["btn_mvp"], use_container_width=True):
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
                tam = m_data.get("TAM_Total_Addressable_Market", t["market_unknown"])
                sam = m_data.get("SAM_Serviceable_Addressable_Market", t["market_unknown"])
                som = m_data.get("SOM_Serviceable_Obtainable_Market", t["market_unknown"])
                cagr = m_data.get("CAGR_Market_Growth_Rate", m_data.get("CAGR_Pazar_Buyume_Orani", t["market_unknown"]))
                density = m_data.get("Market_Density", m_data.get("Market_Density_Pazar_Yogunlugu", ""))
                note = m_data.get("Summary_Research_Note", m_data.get("Ozet_Arastirma_Notu", ""))
                
                # 1. KPI Cards
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("TAM", tam.split()[0] if tam else "-")
                c2.metric("SAM", sam.split()[0] if sam else "-")
                c3.metric("SOM", som.split()[0] if som else "-")
                
                cagr_val = cagr.split()[0] if cagr else "-"
                c4.metric("CAGR", cagr_val, delta=t["market_uptrend"])
                
                # 2. Market Density Warning
                density_lower = density.lower()
                if "red" in density_lower or "kırmızı" in density_lower:
                    st.error(t["market_density_red"].format(density))
                elif "blue" in density_lower or "mavi" in density_lower:
                    st.success(t["market_density_blue"].format(density))
                else:
                    st.info(t["market_density_info"].format(density))
                
                # 3. Funnel Chart
                import plotly.graph_objects as go
                import re
                
                def extract_val(s):
                    matches = re.findall(r'\d+(?:\.\d+)?', str(s).replace(',', ''))
                    if matches:
                        val = float(matches[0])
                        if 'B' in str(s) or 'Milyar' in str(s) or 'Billion' in str(s): 
                            val *= 1000
                        return val
                    return 10
                
                t_val, s_val, so_val = extract_val(tam), extract_val(sam), extract_val(som)
                
                fig = go.Figure(go.Funnel(
                    y=["TAM", "SAM", "SOM"],
                    x=[t_val, s_val, so_val],
                    text=[tam, sam, som],
                    textinfo="text",
                    marker={"color": ["#004c6d", "#00839a", "#00c0a3"]}
                ))
                fig.update_layout(title=t["market_funnel_title"], margin=dict(t=40, l=20, r=20, b=20))
                st.plotly_chart(fig, use_container_width=True)
                
                # 4. Summary Note
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
                            
        return

    # Chat input
    if prompt := st.chat_input(t["chat_placeholder"]):
        # Add user answer to chat history
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        # Save answer
        st.session_state.answers.append(prompt)
        
        # Move to next question
        st.session_state.current_question_idx += 1
        
        if st.session_state.current_question_idx < len(t["questions"]):
            next_q = t["questions"][st.session_state.current_question_idx]
            st.session_state.chat_history.append({"role": "assistant", "content": next_q})
        else:
            # Finished
            save_data(st.session_state.answers)
            
        st.rerun()

if __name__ == "__main__":
    main()
