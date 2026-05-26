import streamlit as st
import plotly.graph_objects as go
import re as _re
from ui_text import UI_TEXT
from datetime import datetime

def _extract_val(s):
    nums = _re.findall(r'\d+(?:\.\d+)?', str(s).replace(',', ''))
    if nums:
        v = float(nums[0])
        if any(x in str(s) for x in ('B', 'Milyar', 'Billion', 'T', 'Trillion')):
            v *= 1000
        return v
    return 10

def render_market_dashboard(lang, m_data):
    t = UI_TEXT[lang]
    st.markdown("---")
    st.subheader(t["market_dashboard"])

    if "hata" in m_data or "error" in m_data:
        st.error(m_data.get("hata", m_data.get("error")))
        return

    # Extract sections
    metrics = m_data.get("Market_Metrics")
    comp_flaws = m_data.get("Competitor_Flaws", [])
    reg_risks = m_data.get("Regulatory_Risks", [])
    unit_economics = m_data.get("Unit_Economics")
    moat_analysis = m_data.get("Moat_Analysis")
    choke_points = m_data.get("Choke_Points", [])

    if metrics:
        tam_obj = metrics.get("TAM", {})
        sam_obj = metrics.get("SAM", {})
        som_obj = metrics.get("SOM", {})
        cagr_obj = metrics.get("CAGR", {})
        density = metrics.get("Market_Density", "")

        tam = tam_obj.get("value", t["market_unknown"])
        sam = sam_obj.get("value", t["market_unknown"])
        som = som_obj.get("value", t["market_unknown"])
        cagr = cagr_obj.get("value", t["market_unknown"])

        st.markdown(t["market_metrics_hdr"])
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("TAM", tam.split()[0] if tam else "-")
        c2.metric("SAM", sam.split()[0] if sam else "-")
        c3.metric("SOM", som.split()[0] if som else "-")
        c4.metric("CAGR", cagr.split()[0] if cagr else "-", delta=t["market_uptrend"])

        with st.expander(t["market_source"]):
            for label, obj in [("TAM", tam_obj), ("SAM", sam_obj), ("SOM", som_obj), ("CAGR", cagr_obj)]:
                scope = obj.get("scope", obj.get("period", ""))
                src = obj.get("source_assumption", "")
                st.markdown(f"**{label}** — _{scope}_  \n`{src}`")

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

        if comp_flaws:
            st.markdown(t["market_comp_hdr"])
            for cf in comp_flaws:
                name = cf.get("competitor", "Unknown")
                with st.expander(f"🎯 {name}"):
                    st.markdown(f"{t['market_comp_weakness']} {cf.get('known_weakness', '-')}")
                    st.markdown(f"{t['market_comp_window']} {cf.get('exploit_window', '-')}")

        if reg_risks:
            st.markdown(t["market_reg_hdr"])
            for rr in reg_risks:
                reg_name = rr.get("regulation", "Unknown regulation")
                with st.expander(f"⚖️ {reg_name}"):
                    st.warning(f"{t['market_reg_impact']} {rr.get('impact', '-')}")
                    st.info(f"{t['market_reg_mitigation']} {rr.get('mitigation', '-')}")

        # Unit Economics
        ue = m_data.get("Unit_Economics")
        if ue:
            st.markdown("### 💰 Unit Economics")
            col_ue1, col_ue2 = st.columns(2)
            with col_ue1:
                st.info(f"**Model type:** {ue.get('model_type', '-')}")
            with col_ue2:
                st.markdown(ue.get('metrics_breakdown', '-'))

        # Moat Analysis
        moat = m_data.get("Moat_Analysis")
        if moat:
            st.markdown("### 🏰 Moat Analysis")
            moat_score = moat.get('replication_difficulty_score', '?')
            st.metric("Replication difficulty (1–10)", moat_score)
            st.warning(moat.get('defensibility', '-'))

        # 18-Month Kill Scenarios
        choke = m_data.get("Choke_Points")
        if choke:
            st.markdown("### ⚠️ 18-Month kill scenarios")
            for i, cp in enumerate(choke, 1):
                st.error(f"**Kill scenario #{i}:** {cp.get('lethal_scenario', '-')}")

    else:
        # Legacy format fallback
        tam = m_data.get("TAM_Total_Addressable_Market", t["market_unknown"])
        sam = m_data.get("SAM_Serviceable_Addressable_Market", t["market_unknown"])
        som = m_data.get("SOM_Serviceable_Obtainable_Market", t["market_unknown"])
        cagr = m_data.get("CAGR_Market_Growth_Rate", m_data.get("CAGR_Pazar_Buyume_Orani", t["market_unknown"]))
        density = m_data.get("Market_Density", m_data.get("Market_Density_Pazar_Yogunlugu", ""))
        note = m_data.get("Summary_Research_Note", m_data.get("Ozet_Arastirma_Notu", ""))

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("TAM", tam.split()[0] if tam else "-")
        c2.metric("SAM", sam.split()[0] if sam else "-")
        c3.metric("SOM", som.split()[0] if som else "-")
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
            
    # --- Data Source Transparency Panel ---
    with st.expander(t["data_sources"]):
        meta = m_data.get("_meta", {})
        corpus_len = meta.get("corpus_length_chars", 0)
        query_count = len(meta.get("search_queries_used", []))
        st.info(t["market_sources"].format(corpus_len, query_count))
        if corpus_len < 500:
            st.warning(t["market_sources_warn"])

def render_finance_dashboard(lang, f_data):
    t = UI_TEXT[lang]
    st.subheader(t["finance_dashboard"])

    if "hata" in f_data or "error" in f_data:
        st.error(f_data.get("hata", f_data.get("error")))
        return

    score = f_data.get("Investment_Score", f_data.get("Yatirim_Skoru", 0))

    m1, m2, m3 = st.columns(3)
    m1.metric(t["finance_score"], f"{score}/100")
    m2.metric(t["finance_ltv_cac"], f_data.get("LTV_CAC_Estimate", f_data.get("LTV_CAC_Tahmini", "-")))
    m3.metric(t["finance_capital"], str(f_data.get("Capital_Intensity", f_data.get("Sermaye_Yogunlugu", "-"))).split()[0])

    ltv_comment = f_data.get('LTV_CAC_Comment', f_data.get('LTV_CAC_Yorumu', ''))
    cap_detail = f_data.get('Capital_Intensity', f_data.get('Sermaye_Yogunlugu', ''))
    st.info(t["finance_ltv_comment"].format(ltv_comment))
    st.info(t["finance_capital_detail"].format(cap_detail))

    st.markdown(t["finance_red_flags"])
    red_flags = f_data.get("Red_Flags", f_data.get("Kirmizi_Bayraklar", []))
    for flag in red_flags:
        if "🚨" in flag or "CRITICAL" in flag:
            st.error(flag)
        elif "⚠️" in flag or "HIGH" in flag or "MEDIUM" in flag:
            st.warning(flag)
        else:
            st.success(flag)
            
    # New fields from Claude-powered engine
    payback = f_data.get("Payback_Period_Months")
    if payback:
        st.metric("CAC Payback Period", f"{payback} months")

    gross_margin = f_data.get("Gross_Margin_Estimate")
    burn_rate = f_data.get("Burn_Rate_Estimate")
    death = f_data.get("Death_Scenario")
    funding_rec = f_data.get("Funding_Recommendation")
    score_just = f_data.get("Score_Justification")

    if gross_margin:
        st.info(f"**Gross margin estimate:** {gross_margin}")
    if burn_rate:
        st.info(f"**Monthly burn estimate:** {burn_rate}")
    if score_just:
        st.markdown("#### Score justification")
        st.markdown(score_just)
    if death:
        st.markdown("#### ☠️ Most likely death scenario")
        st.error(death)
    if funding_rec:
        st.markdown("#### Funding recommendation")
        st.success(f"**{funding_rec}**")

    # --- Data Source Transparency Panel ---
    with st.expander(t["data_sources"]):
        st.info(t["finance_sources"].format(datetime.now().strftime('%B %Y')))
        # Show benchmark database indicator
        st.markdown("**Benchmark Data:** 2024-2025 VC Industry Standards (SaaS/Hardware/Marketplace)")

def render_mvp_dashboard(lang, m_data):
    t = UI_TEXT[lang]
    st.markdown("---")
    st.subheader(t["mvp_dashboard"])

    if "hata" in m_data or "error" in m_data:
        st.error(m_data.get("hata", m_data.get("error")))
        return

    complexity_score = m_data.get('Complexity_Score', m_data.get('Karmasiklik_Skoru', ''))
    complexity_reason = m_data.get('Complexity_Reasoning', m_data.get('Karmasiklik_Gerekcesi', ''))
    ttm = m_data.get('Time_to_Market', m_data.get('Pazara_Cikis_Suresi', ''))

    st.markdown(t["mvp_complexity"].format(complexity_score))
    st.info(complexity_reason)

    st.markdown(t["mvp_time_to_market"].format(ttm))
    
    # Week 0 validation
    week_0 = m_data.get("Week_0_Validation_Task")
    if week_0:
        st.markdown(t["mvp_week0"])
        st.warning(week_0)

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
        
    build_buy = m_data.get("Build_vs_Buy_Decisions")
    if build_buy:
        st.markdown(t["mvp_build_buy"])
        for bb in build_buy:
            st.markdown(f"- {bb}")
            
    pivot_trigger = m_data.get("Pivot_Trigger")
    if pivot_trigger:
        st.markdown(t["mvp_pivot"])
        st.error(pivot_trigger)

    st.markdown(t["mvp_sprint"])
    sprint_plan = m_data.get("Founder_Sprint_Plan", m_data.get("Kurucu_Sprint_Plani", []))
    for i, sprint in enumerate(sprint_plan):
        with st.expander(sprint["week"], expanded=True):
            for j, task in enumerate(sprint["tasks"]):
                st.checkbox(task, key=f"sprint_{i}_task_{j}")
