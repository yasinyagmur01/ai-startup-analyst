# 🚀 Start-Up AI-R: Institutional VC-Grade Due Diligence & Market Intelligence Engine

![Version](https://img.shields.io/badge/version-2.0.0-blueviolet?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![Framework](https://img.shields.io/badge/Agentic-Framework-orange?style=for-the-badge)

**Start-Up AI-R** is an AI-driven Venture Capital (VC) screening and market intelligence engine designed to move far beyond generic business summaries. It breaks away from boilerplate SaaS cliches to conduct institutional-grade due diligence across diverse startup verticals, including DeepTech, robotics, hardware, and e-commerce.

---

## 🌟 Core Features (v2.0)

### 1. 🎤 Dynamic Interview Framework & Input Boundary
* **On-the-Fly Question Generation:** Replaces static, boring intake forms. The core engine analyzes the initial startup thesis and dynamically generates **3 rigorous, vertical-specific interview questions** on the fly.
* **UI Validation Boundary:** Prevents superficial responses like "yes," "no," or "we will handle it." The interface enforces a strict minimum character threshold, locking the submission until the founder provides concrete operational strategies.

### 2. 📊 Institutional VC-Grade Market Intelligence
* **Strict Metric Enforcement:** Vague phrases like "rapidly growing market" are strictly banned. The engine calculates data-backed **TAM (Total Addressable Market)**, **SAM (Serviceable Addressable Market)**, and **SOM (Serviceable Obtainable Market)** metrics, citing mathematical assumptions or historical data sources for every figure.
* **Geographic & Regulatory Deep-Dive:** Extracts critical legal and macroeconomic bottlenecks tailored to the selected country of operation (e.g., KVKK/monetary volatility for Turkey, GDPR/CE/MDR compliance for the EU).

### 3. 🛡️ Defensibility & Moat Architecture
* Evaluates structural barriers to entry. The engine rigorously scores the startup’s defensibility and maps out how quickly an incumbent with $10M in venture backing could copy the core value proposition based on IP, algorithms, or supply chain locking.

### 4. 📉 Unit Economics & Lethal Choke Points
* **Cost Architecture:** Outlines **COGS (Cost of Goods Sold)** and **BOM (Bill of Materials) risks** for hardware/robotics projects, or **LTV:CAC and Payback Period benchmarks** for digital products.
* **The Red Flag Directory:** Synthesizes exactly **3 brutal, vertical-specific kill-scenarios** where the startup faces high bankruptcy risk within the first 18 months.

### 5. 💯 Investment Readiness Index (Scoring Engine)
* Scores the venture across four distinct pillars (Market Fit, Tech Defensibility, Regulatory Safety, etc.) out of 100, outputting a weighted **VC Investment Index** with a 1-sentence analytical justification for every metric.

---

## 🏗️ System Architecture & Tech Stack

* **Frontend:** Streamlit (Bilingual UI, dynamic reactive input validation)
* **Agentic Backend:** LangChain / CrewAI / Anthropic Claude API (Vertical-specific routing logic)
* **Data Layer:** State persistence via `startup_data.json`
