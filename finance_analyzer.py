import json
import os
import re

def get_system_prompt(lang="en"):
    """
    Returns the system prompt for the LLM based on the selected language.
    Note: Currently not injected into an API call, but ready for future integration.
    """
    if lang == "tr":
        return "Sen uzman bir finansal analistsin. Startup verilerini ve pazar analizini inceleyerek finansal metrikleri hesapla ve JSON döndür."
    return "You are an expert financial analyst. Review the startup and market data to calculate financial metrics and return JSON."

def analyze_finance(lang="en"):
    """
    Reads startup_data.json and market_analysis.json to estimate:
    - LTV/CAC Prediction
    - Capital Intensity
    - Investability Score
    - Red Flags
    Saves the results to finance_analysis.json.
    """
    startup_data_path = "data/startup_data.json"
    market_data_path = "data/market_analysis.json"
    
    if not os.path.exists(startup_data_path) or not os.path.exists(market_data_path):
        err = "Veriler eksik. Lütfen mülakatı ve pazar analizini tamamlayın." if lang == "tr" else "Missing data. Please complete the interview and market analysis first."
        return {"error": err, "hata": err}
        
    with open(startup_data_path, "r", encoding="utf-8") as f:
        startup_data = json.load(f)
        
    with open(market_data_path, "r", encoding="utf-8") as f:
        market_data = json.load(f)
        
    # Extract needed variables
    business_model = startup_data.get("q4", {}).get("answer", "").lower()
    mvp_approach = startup_data.get("q5", {}).get("answer", "").lower()
    
    tam_val = market_data.get("TAM_Total_Addressable_Market", "")
    market_density = market_data.get("Market_Density", market_data.get("Market_Density_Pazar_Yogunlugu", ""))
    
    # 1. LTV/CAC Öngörüsü
    ltv_cac_ratio = 2.5
    if lang == "tr":
        ltv_cac_comment = "Sektör standartlarına yakın (2.5x - 3x). İyileştirme gerekebilir."
    else:
        ltv_cac_comment = "Close to industry standards (2.5x - 3x). May require improvement."
    
    if "saas" in business_model or "abonelik" in business_model or "subscription" in business_model:
        ltv_cac_ratio = 4.2
        ltv_cac_comment = "SaaS ve abonelik modellerinde LTV yüksek olma eğilimindedir (Tahmini 4x+). Çok olumlu." if lang == "tr" else "SaaS and subscription models tend to have high LTV (Estimated 4x+). Very positive."
    elif "komisyon" in business_model or "pazaryeri" in business_model or "marketplace" in business_model or "commission" in business_model:
        ltv_cac_ratio = 1.8
        ltv_cac_comment = "Pazaryeri modellerinde iki tarafı da edinmek zor olduğundan CAC yüksektir (Tahmini < 2x). Dikkat!" if lang == "tr" else "High CAC in marketplace models as both sides must be acquired (Estimated < 2x). Caution!"
    elif "reklam" in business_model or "ads" in business_model:
        ltv_cac_ratio = 2.0
        ltv_cac_comment = "Reklam modellerinde hacim önemlidir, ilk etapta LTV/CAC düşük kalabilir." if lang == "tr" else "Volume is key in ad models, LTV/CAC might be low initially."

    if "kırmızı" in market_density.lower() or "red" in market_density.lower():
        ltv_cac_ratio -= 0.5
        ltv_cac_comment += " Kırmızı okyanusta müşteri edinmek pahalıdır, CAC baskısı oluşacak." if lang == "tr" else " Customer acquisition is expensive in red oceans, creating CAC pressure."
        
    # 2. Sermaye Yoğunluğu (Capital Intensity)
    if lang == "tr":
        capital_intensity = "Orta (Medium)"
        if any(word in mvp_approach for word in ["no code", "no-code", "ai", "yapay zeka", "bot", "manuel", "hızlı"]):
            capital_intensity = "Düşük (Low) - Lean Startup yaklaşımına çok uygun, dış sermaye bağımlılığı az."
        elif any(word in mvp_approach for word in ["donanım", "hardware", "fabrika", "üretim", "arge"]):
            capital_intensity = "Yüksek (High) - Ürünü test etmek bile ciddi bir ön yatırım gerektiriyor."
    else:
        capital_intensity = "Medium"
        if any(word in mvp_approach for word in ["no code", "no-code", "ai", "yapay zeka", "bot", "manuel", "hızlı", "fast"]):
            capital_intensity = "Low - Very suitable for Lean Startup, low external capital dependency."
        elif any(word in mvp_approach for word in ["donanım", "hardware", "fabrika", "üretim", "arge", "factory", "production", "r&d"]):
            capital_intensity = "High - Even testing the product requires serious upfront investment."
        
    # 3. Yatırım Alabilirlik Skoru
    score = 50
    
    # TAM Etkisi
    if "B" in tam_val or "Billion" in tam_val:
        score += 20 # Milyar dolarlık pazar
    elif "T" in tam_val or "Trillion" in tam_val:
        score += 25
    else:
        score += 5 # Daha küçük bir pazar
        
    # Density Etkisi
    if "mavi" in market_density.lower() or "blue" in market_density.lower():
        score += 15
    elif "kırmızı" in market_density.lower() or "red" in market_density.lower():
        score -= 10
        
    # Model Etkisi
    if "saas" in business_model:
        score += 10
    if "Düşük" in capital_intensity or "Low" in capital_intensity:
        score += 10
    elif "Yüksek" in capital_intensity or "High" in capital_intensity:
        score -= 5
        
    # Sınırlandırma
    score = max(0, min(100, int(score)))
    
    # 4. Kırmızı Bayraklar (Red Flags)
    red_flags = []
    if lang == "tr":
        if "kırmızı" in market_density.lower() or "red" in market_density.lower():
            red_flags.append("🚨 Pazar çok dar veya aşırı rekabetçi. Pazar payı kapmak CAC (Müşteri Edinme) maliyetlerini patlatabilir.")
        if ltv_cac_ratio < 3.0:
            red_flags.append(f"⚠️ Tahmini LTV/CAC oranı ({ltv_cac_ratio:.1f}x) VC'lerin ideal gördüğü 3x'in altında. Birim ekonomisi (Unit Economics) zorlayıcı olabilir.")
        if "pazaryeri" in business_model or "komisyon" in business_model or "marketplace" in business_model:
            red_flags.append("⚠️ Pazaryeri iş modeli. 'Tavuk-yumurta' problemi nedeniyle her iki tarafı da sisteme katmak ciddi sermaye yakmayı (burn rate) gerektirecektir.")
        if "Yüksek" in capital_intensity or "High" in capital_intensity:
            red_flags.append("🚨 Donanım veya ağır Ar-Ge içeren süreç. Ürün-Pazar uyumunu test etmeden önce çok fazla para yakma riski var.")
        if score < 60:
            red_flags.append("🚨 Genel Yatırım Skoru düşük. VC turuna çıkmadan önce bootstrapping (öz sermaye ile büyüme) tavsiye edilir.")
            
        if not red_flags:
            red_flags.append("✅ Belirgin bir kırmızı bayrak saptanmadı. Finansal temeller umut verici.")
    else:
        if "kırmızı" in market_density.lower() or "red" in market_density.lower():
            red_flags.append("🚨 Market is too narrow or highly competitive. Gaining market share will skyrocket CAC.")
        if ltv_cac_ratio < 3.0:
            red_flags.append(f"⚠️ Estimated LTV/CAC ratio ({ltv_cac_ratio:.1f}x) is below the VC ideal of 3x. Unit economics might be challenging.")
        if "pazaryeri" in business_model or "komisyon" in business_model or "marketplace" in business_model:
            red_flags.append("⚠️ Marketplace business model. The 'chicken-egg' problem of acquiring both sides will require significant burn rate.")
        if "Yüksek" in capital_intensity or "High" in capital_intensity:
            red_flags.append("🚨 Process involves hardware or heavy R&D. High risk of burning too much cash before testing Product-Market Fit.")
        if score < 60:
            red_flags.append("🚨 Overall Investment Score is low. Bootstrapping is recommended before seeking VC funding.")
            
        if not red_flags:
            red_flags.append("✅ No obvious red flags detected. Financial fundamentals are promising.")

    analysis = {
        "LTV_CAC_Estimate": f"{ltv_cac_ratio:.1f}x",
        "LTV_CAC_Comment": ltv_cac_comment,
        "Capital_Intensity": capital_intensity,
        "Investment_Score": score,
        "Red_Flags": red_flags
    }
    
    os.makedirs("data", exist_ok=True)
    with open("data/finance_analysis.json", "w", encoding="utf-8") as f:
        json.dump(analysis, f, ensure_ascii=False, indent=4)
        
    return analysis

if __name__ == "__main__":
    result = analyze_finance()
    print(json.dumps(result, indent=2, ensure_ascii=False))
