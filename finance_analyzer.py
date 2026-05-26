"""
finance_analyzer.py — Claude-Powered VC Financial Analysis Engine
==================================================================
Previous version used hardcoded if/else rules with zero AI calls.
This version calls Claude API with institutional-grade benchmarks.
"""

import json
import os
import re
import anthropic
from datetime import datetime


def _extract_tam(market_data: dict) -> str:
    """Handles both new nested Market_Metrics format and old flat format."""
    metrics = market_data.get("Market_Metrics", {})
    if metrics:
        return metrics.get("TAM", {}).get("value", "Unknown")
    return market_data.get("TAM_Total_Addressable_Market",
           market_data.get("TAM", "Unknown"))


def _extract_density(market_data: dict) -> str:
    """Handles both new nested Market_Metrics format and old flat format."""
    metrics = market_data.get("Market_Metrics", {})
    if metrics:
        return metrics.get("Market_Density", "")
    return market_data.get("Market_Density",
           market_data.get("Market_Density_Pazar_Yogunlugu", ""))


def _extract_cagr(market_data: dict) -> str:
    """Extracts CAGR from either format."""
    metrics = market_data.get("Market_Metrics", {})
    if metrics:
        return metrics.get("CAGR", {}).get("value", "Unknown")
    return market_data.get("CAGR_Market_Growth_Rate",
           market_data.get("CAGR_Pazar_Buyume_Orani", "Unknown"))


def analyze_finance(lang: str = "en") -> dict:
    """
    Calls Claude API with startup data + market analysis to produce
    institutional-grade financial projections.
    Replaces the old hardcoded rule-based engine entirely.
    """
    startup_data_path = "data/startup_data.json"
    market_data_path = "data/market_analysis.json"

    if not os.path.exists(startup_data_path):
        err = "Veri eksik. Lütfen mülakatı tamamlayın." if lang == "tr" else "Missing data. Please complete the interview first."
        return {"error": err, "hata": err}

    with open(startup_data_path, "r", encoding="utf-8") as f:
        startup_data = json.load(f)

    market_data = {}
    if os.path.exists(market_data_path):
        with open(market_data_path, "r", encoding="utf-8") as f:
            market_data = json.load(f)

    current_date = datetime.now().strftime("%B %Y")
    current_year = datetime.now().year

    tam = _extract_tam(market_data)
    density = _extract_density(market_data)
    cagr = _extract_cagr(market_data)
    choke_points = market_data.get("Choke_Points", [])
    moat = market_data.get("Moat_Analysis", {})

    lang_instruction = (
        "Respond ENTIRELY in Turkish. All keys, labels, values, and explanations must be in Turkish."
        if lang == "tr"
        else "Respond ENTIRELY in English."
    )

    system_prompt = f"""You are a senior VC financial analyst conducting institutional due diligence in {current_year}.
Today's date is {current_date}.

BENCHMARK DATABASE ({current_year} standards — cite these explicitly):
- B2B SaaS median LTV:CAC = 3.5:1 (top quartile = 5:1+, bottom quartile = 1.8:1)
- Marketplace median LTV:CAC = 1.5:1 (two-sided acquisition doubles CAC)
- B2C Consumer App median LTV:CAC = 1.8:1
- Hardware startup gross margin target = 40-60% (commodity = 20-35%)
- SaaS gross margin benchmark = 70-80%
- Series A median revenue multiple ({current_year}) = 5-7x ARR (compressed from 2021 highs)
- Average SaaS CAC payback period = 12-18 months (best-in-class = <12 months)
- Seed-stage monthly burn benchmark = $30K-$80K (lean) / $80K-$200K (team-heavy)
- Turkey-specific: CAC typically 40-60% lower than US for same vertical
- Turkey-specific: LTV also lower due to purchasing power (~25-35% of US equivalent)
- Turkey-specific: SaaS pricing power significantly lower, churn higher in SMB segment

BANNED PHRASES (automatic failure if used):
"potentially profitable", "promising", "could be successful", "has potential",
"growing market", "exciting opportunity", "strong foundation"

CRITICAL RULES:
- Every numeric claim MUST cite the benchmark or formula used
- LTV:CAC must be a specific ratio with reasoning, not a range
- Investment score must have a 3-sentence mathematical justification
- Red flags must be severity-ranked: CRITICAL / HIGH / MEDIUM
- Death scenario must be the single most statistically likely failure mode

{lang_instruction}

Return ONLY valid JSON. No markdown, no explanation text, no code fences."""

    user_prompt = f"""ANALYSIS DATE: {current_date}

STARTUP DATA:
{json.dumps(startup_data, ensure_ascii=False, indent=2)}

MARKET CONTEXT (from market analysis):
- TAM: {tam}
- Market Density: {density}
- CAGR: {cagr}
- Moat Analysis: {json.dumps(moat, ensure_ascii=False)}
- Known Kill Scenarios: {json.dumps(choke_points, ensure_ascii=False)}

Produce financial analysis as this exact JSON structure:
{{
  "Investment_Score": <integer 0-100>,
  "Score_Justification": "<3 sentences with mathematical reasoning citing benchmarks>",
  "LTV_CAC_Estimate": "<specific ratio like '3.2:1'>",
  "LTV_CAC_Comment": "<cite the benchmark used, explain why this startup hits above/below>",
  "Payback_Period_Months": "<estimated months as integer>",
  "Gross_Margin_Estimate": "<percentage range with reasoning>",
  "Burn_Rate_Estimate": "<monthly USD estimate for seed stage with breakdown>",
  "Capital_Intensity": "<Low / Medium / High with 18-month runway cost estimate in USD>",
  "Red_Flags": [
    "CRITICAL: <specific kill scenario with financial mechanism>",
    "HIGH: <second risk with quantified impact>",
    "MEDIUM: <third risk with mitigation cost estimate>"
  ],
  "Death_Scenario": "<single most statistically likely financial cause of failure within 12 months, be specific>",
  "Funding_Recommendation": "<Bootstrap / Pre-seed / Seed / Series A — with reasoning>"
}}"""

    try:
        client = anthropic.Anthropic()
        message = client.messages.create(
            model="claude-opus-4-5",
            max_tokens=1500,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}]
        )
        raw = message.content[0].text.strip()
        if raw.startswith("```"):
            raw = re.sub(r"^```[a-z]*\n?", "", raw)
            raw = re.sub(r"\n?```$", "", raw)
        result = json.loads(raw)
    except json.JSONDecodeError:
        result = _fallback_finance(startup_data, market_data, lang)
    except Exception as e:
        result = {"error": str(e), "hata": str(e)}

    os.makedirs("data", exist_ok=True)
    with open("data/finance_analysis.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=4)

    return result


def _fallback_finance(startup_data: dict, market_data: dict, lang: str) -> dict:
    """Rule-based fallback only used when Claude API call fails."""
    business_model = startup_data.get("q4", {}).get("answer", "").lower()
    density = _extract_density(market_data)

    if "saas" in business_model or "subscription" in business_model:
        ltv_cac = "3.5:1"
        score = 58
    elif "marketplace" in business_model or "commission" in business_model:
        ltv_cac = "1.5:1"
        score = 42
    else:
        ltv_cac = "2.5:1"
        score = 50

    if "red" in density.lower() or "kırmızı" in density.lower():
        score -= 10

    if lang == "tr":
        return {
            "Investment_Score": score,
            "Score_Justification": "API çağrısı başarısız oldu — kural tabanlı yedek sistem kullanıldı. Gerçek analiz için tekrar deneyin.",
            "LTV_CAC_Estimate": ltv_cac,
            "LTV_CAC_Comment": "Yedek sistem tahmini — Claude API ile doğrulanmadı.",
            "Payback_Period_Months": 18,
            "Gross_Margin_Estimate": "Bilinmiyor — API çağrısı gerekli",
            "Burn_Rate_Estimate": "Bilinmiyor — API çağrısı gerekli",
            "Capital_Intensity": "Orta (Medium)",
            "Red_Flags": ["CRITICAL: API çağrısı başarısız — analiz eksik"],
            "Death_Scenario": "Belirsiz — Claude API bağlantısını kontrol edin.",
            "Funding_Recommendation": "Belirsiz"
        }
    return {
        "Investment_Score": score,
        "Score_Justification": "API call failed — rule-based fallback used. Retry for real analysis.",
        "LTV_CAC_Estimate": ltv_cac,
        "LTV_CAC_Comment": "Fallback estimate — not validated by Claude API.",
        "Payback_Period_Months": 18,
        "Gross_Margin_Estimate": "Unknown — API call required",
        "Burn_Rate_Estimate": "Unknown — API call required",
        "Capital_Intensity": "Medium",
        "Red_Flags": ["CRITICAL: API call failed — analysis incomplete"],
        "Death_Scenario": "Uncertain — check Claude API connection.",
        "Funding_Recommendation": "Uncertain"
    }


if __name__ == "__main__":
    result = analyze_finance()
    print(json.dumps(result, indent=2, ensure_ascii=False))
