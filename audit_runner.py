import json
import os
import time

# Import modules from the project
import app
import market_analyzer
import mvp_architect
import finance_analyzer

scenarios = [
    {"name": "Pure Hardware / Toy", "pitch": "A mechanical, non-electronic premium wooden educational puzzle toy for kids."},
    {"name": "DeepTech / Robotics", "pitch": "Autonomous Underwater Vehicles (AUVs) utilizing ROS2 and DDS for deep-sea pipeline maintenance."},
    {"name": "Crypto / Cyber-Physical", "pitch": "Edge-AI biometric hardware tokens sealing data transmission via Physical Unclonable Functions (PUF)."},
    {"name": "Pure SaaS / B2B", "pitch": "Multi-tenant automated tax reconciliation engine for cross-border e-commerce vendors."},
    {"name": "Consumer IoT / Hardware", "pitch": "Smart botanic workspace humidifiers checking soil moisture via BLE and automated watering lines."},
    {"name": "BioTech / MedTech", "pitch": "Microfluidic chip hardware utilizing AI for real-time pathogen screening in dairy farms."},
    {"name": "AgriTech / Drone", "pitch": "Autonomous drone fleet tracking soil nitrogen levels with multispectral sensors."},
    {"name": "FinTech / Compliance", "pitch": "Real-time AI-driven anti-money laundering (AML) graph database analyzer."},
    {"name": "SpaceTech / Hardware", "pitch": "Low-Earth orbit satellite communications cubesat antenna arrays."},
    {"name": "E-Commerce / Hybrid", "pitch": "Customized mechanical keyboard dynamic hot-swap switch marketplaces utilizing generative 3D modeling tools."},
    {"name": "CleanTech / Hardware", "pitch": "Residential-scale micro-wind turbine hardware with integrated power grid software."},
    {"name": "EdTech / SaaS", "pitch": "AI-generated personalized gamified curriculum engines for neurodivergent children."}
]

audit_results = []

def run_audit():
    print("Starting Automated Stress-Test...")
    
    # Optional: We will mock the Streamlit session state for `save_data` if needed.
    # However, app.py's `save_data` expects st.session_state. We can just write the JSON directly!
    
    for idx, sc in enumerate(scenarios):
        print(f"\n[{idx+1}/{len(scenarios)}] Processing: {sc['name']}")
        
        pitch = sc["pitch"]
        
        # 1. Generate Interview Questions
        print("  -> Generating interview questions...")
        q_result = app.generate_interview_questions(pitch, lang="en")
        
        questions = []
        if isinstance(q_result, dict):
            questions = q_result.get("questions", [])
            warning = q_result.get("buzzword_warning")
        else:
            questions = q_result # Fallback is just list if it somehow failed
            warning = None
            
        print(f"  -> Found {len(questions)} questions. Warning: {warning}")
        
        # 2. Mock Answers and Save to Data
        answers = []
        for i, q in enumerate(questions):
            q_text = q.get("question", str(q)) if isinstance(q, dict) else q
            # Generate a somewhat plausible but generic answer based on vertical
            answers.append(f"We plan to address this by focusing heavily on our core demographic and optimizing our supply chain in {sc['name'].split('/')[0].strip()} sectors.")
            
        # Add MVP specific answer for Q5 if it exists
        if len(answers) >= 5:
            answers[4] = "We will launch a simple MVP website to collect pre-orders."
            
        data = {
            "pitch": pitch,
        }
        for i in range(min(len(questions), len(answers))):
            q_text = questions[i].get("question", str(questions[i])) if isinstance(questions[i], dict) else questions[i]
            data[f"q{i+1}"] = {"question": q_text, "answer": answers[i]}
            
        os.makedirs("data", exist_ok=True)
        with open("data/startup_data.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
            
        # 3. Analyze Market
        print("  -> Running Market Analysis...")
        market_res = market_analyzer.analyze_market(lang="en")
        
        # 4. Analyze MVP
        print("  -> Running MVP Architecture...")
        mvp_res = mvp_architect.analyze_mvp(lang="en")
        
        # 5. Analyze Finance
        print("  -> Running Finance Analysis...")
        fin_res = finance_analyzer.analyze_finance(lang="en")
        
        # 6. Store in audit logs
        audit_results.append({
            "scenario": sc["name"],
            "pitch": sc["pitch"],
            "buzzword_warning": warning,
            "questions_generated": questions,
            "market_analysis": market_res,
            "mvp_analysis": mvp_res,
            "finance_analysis": fin_res
        })
        
        time.sleep(2) # Prevent extreme API rate limiting
        
    with open("audit_logs.json", "w", encoding="utf-8") as f:
        json.dump(audit_results, f, ensure_ascii=False, indent=4)
        
    print("\n✅ Audit complete! Results saved to audit_logs.json")

if __name__ == "__main__":
    run_audit()
