import json
import os
import re
import anthropic

def synthesize_analysis(lang="en"):
    """
    Reads all three analysis JSON files: market_analysis.json, finance_analysis.json, mvp_analysis.json
    Calls Claude to produce a Synthesis Report as JSON.
    """
    data_dir = "data"
    market_path = os.path.join(data_dir, "market_analysis.json")
    finance_path = os.path.join(data_dir, "finance_analysis.json")
    mvp_path = os.path.join(data_dir, "mvp_analysis.json")
    
    if not (os.path.exists(market_path) and os.path.exists(finance_path) and os.path.exists(mvp_path)):
        err = "Tüm analizler (Pazar, Finans, MVP) tamamlanmadan sentez yapılamaz." if lang == "tr" else "Cannot synthesize until all analyses (Market, Finance, MVP) are complete."
        return {"error": err, "hata": err}
        
    with open(market_path, "r", encoding="utf-8") as f:
        market_data = f.read()
    with open(finance_path, "r", encoding="utf-8") as f:
        finance_data = f.read()
    with open(mvp_path, "r", encoding="utf-8") as f:
        mvp_data = f.read()

    lang_instruction = "Respond ENTIRELY in Turkish (Türkçe). All content must be in Turkish." if lang == "tr" else "Respond ENTIRELY in English."

    system_prompt = f"""You are a Lead VC Partner synthesizing multiple due diligence reports (Market, Finance, MVP) into a final executive summary.

Your task is to analyze the three provided JSON reports and produce a Synthesis Report as a JSON object with EXACTLY these three keys:
1. "biggest_contradiction": The most critical misalignment between the reports (e.g., 'Market analysis shows high CAGR but Finance shows 24-month payback — misaligned'). Be highly critical and analytical.
2. "strongest_signal": The single most positive data point across all analyses that validates the investment.
3. "critical_path": An array of exactly 3 concrete next actions for the founder to take immediately.

MANDATORY OUTPUT FORMAT:
Return ONLY a valid JSON object with the exact keys: "biggest_contradiction", "strongest_signal", "critical_path".
No markdown, no explanation text, no code fences. Pure JSON only.

{lang_instruction}"""

    user_prompt = f"""MARKET ANALYSIS:
{market_data[:3000]}

FINANCE ANALYSIS:
{finance_data[:2000]}

MVP ANALYSIS:
{mvp_data[:2000]}

Produce the Synthesis Report JSON."""

    try:
        client = anthropic.Anthropic()
        message = client.messages.create(
            model="claude-opus-4-5",
            max_tokens=1000,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}]
        )
        raw = message.content[0].text.strip()
        if raw.startswith("```"):
            raw = re.sub(r"^```[a-z]*\n?", "", raw)
            raw = re.sub(r"\n?```$", "", raw)
        result = json.loads(raw)
        
        # Persist
        with open(os.path.join(data_dir, "synthesis_analysis.json"), "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=4)
            
        return result
    except Exception as e:
        err = f"Sentez işlemi başarısız oldu: {str(e)}" if lang == "tr" else f"Synthesis failed: {str(e)}"
        return {"error": err, "hata": err}

if __name__ == "__main__":
    res = synthesize_analysis()
    print(json.dumps(res, indent=2, ensure_ascii=False))
