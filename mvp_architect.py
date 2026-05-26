import json
import os
import re
import anthropic
from datetime import datetime

def analyze_mvp(lang="en"):
    """
    Reads startup_data.json, market_analysis.json, and finance_analysis.json.
    Calls Claude to generate an MVP architecture, timeline, complexity score, and tech stack recommendations.
    Saves the result to data/mvp_analysis.json.
    """
    data_dir = "data"
    startup_data_path = os.path.join(data_dir, "startup_data.json")
    market_data_path = os.path.join(data_dir, "market_analysis.json")
    finance_data_path = os.path.join(data_dir, "finance_analysis.json")
    
    if not os.path.exists(startup_data_path):
        err = "Mülakat verileri eksik. Lütfen mülakatı tamamlayın." if lang == "tr" else "Interview data is missing. Please complete the interview first."
        return {"error": err, "hata": err}
    
    with open(startup_data_path, "r", encoding="utf-8") as f:
        startup_data = f.read()
        
    market_data = "{}"
    if os.path.exists(market_data_path):
        with open(market_data_path, "r", encoding="utf-8") as f:
            market_data = f.read()
            
    finance_data = "{}"
    if os.path.exists(finance_data_path):
        with open(finance_data_path, "r", encoding="utf-8") as f:
            finance_data = f.read()

    lang_instruction = "Respond ENTIRELY in Turkish (Türkçe). All labels, notes, and values must be in Turkish." if lang == "tr" else "Respond ENTIRELY in English."

    current_date = datetime.now().strftime("%B %Y")
    
    system_prompt = f"""You are an expert Technical Cofounder and MVP Architect.
Your job is to analyze the startup data, market, and financials to generate a lean, actionable MVP execution plan.

The current date is {current_date}. Keep timeline and tech stack recommendations relevant to {datetime.now().year}.

REQUIREMENTS:
1. "Complexity_Score": Rate technical complexity on a scale of 1-10 (e.g. "7/10")
2. "Complexity_Reasoning": Explain why it got this score.
3. "Time_to_Market": Estimate the time to build the MVP (e.g., "4-6 Weeks").
4. "MVP_Focus_Features": Array of 2-3 core features to build on Day 1.
5. "MVP_Cut_Features": Array of 2-3 features to explicitly NOT build yet.
6. "Tech_Recommendations": Array of tools/frameworks to use.
7. "Build_vs_Buy_Decisions": For each tech recommendation, specify if they should build it or use an existing service (with cost estimate).
8. "Founder_Sprint_Plan": An array of exactly 4 sprint objects. Each object must have a "week" string and a "tasks" array of strings.
9. "Week_0_Validation_Task": One concrete no-code/low-code experiment the founder can run THIS WEEK to test the riskiest assumption.
10. "Pivot_Trigger": At what measurable metric failure point should the founder pivot vs. persist?

MANDATORY OUTPUT FORMAT:
Return ONLY a valid JSON object with the exact keys:
"Complexity_Score", "Complexity_Reasoning", "Time_to_Market", "MVP_Focus_Features", "MVP_Cut_Features", "Tech_Recommendations", "Build_vs_Buy_Decisions", "Founder_Sprint_Plan", "Week_0_Validation_Task", "Pivot_Trigger"

No markdown, no explanation text, no code fences. Pure JSON only.

{lang_instruction}"""

    user_prompt = f"""STARTUP DATA:
{startup_data[:2000]}

MARKET ANALYSIS:
{market_data[:1500]}

FINANCE ANALYSIS:
{finance_data[:1500]}

Produce the MVP Analysis JSON."""

    try:
        client = anthropic.Anthropic()
        message = client.messages.create(
            model="claude-opus-4-5",
            max_tokens=2000,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}]
        )
        raw = message.content[0].text.strip()
        if raw.startswith("```"):
            raw = re.sub(r"^```[a-z]*\n?", "", raw)
            raw = re.sub(r"\n?```$", "", raw)
        result = json.loads(raw)
        
        os.makedirs(data_dir, exist_ok=True)
        with open(os.path.join(data_dir, "mvp_analysis.json"), "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=4)
            
        return result
    except Exception as e:
        err = f"MVP analizi başarısız oldu: {str(e)}" if lang == "tr" else f"MVP analysis failed: {str(e)}"
        return {"error": err, "hata": err}

if __name__ == "__main__":
    result = analyze_mvp()
    print(json.dumps(result, indent=2, ensure_ascii=False))
