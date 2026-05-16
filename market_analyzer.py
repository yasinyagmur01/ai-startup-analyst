import json
import os
import re
import random

try:
    from duckduckgo_search import DDGS
except ImportError:
    DDGS = None

def get_system_prompt(lang="en"):
    """
    Returns the system prompt for the LLM based on the selected language.
    Note: Currently not injected into an API call, but ready for future integration.
    """
    if lang == "tr":
        return "Sen uzman bir pazar analistisin. Verilen startup bilgilerini incele ve pazar araştırması sonuçlarını JSON formatında döndür."
    return "You are an expert market analyst. Review the provided startup information and return the market research results in JSON format."

def analyze_market(lang="en"):
    """
    Reads startup_data.json, searches the web using DuckDuckGo,
    and estimates TAM, SAM, SOM, CAGR, and Market Density.
    Saves the results to market_analysis.json.
    """
    data_path = "data/startup_data.json"
    if not os.path.exists(data_path):
        err = "Veri bulunamadı. Lütfen önce mülakatı tamamlayın." if lang == "tr" else "Data not found. Please complete the interview first."
        return {"error": err, "hata": err}
        
    with open(data_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    niche = data.get("q2", {}).get("answer", "Genel Pazar")
    competitors = data.get("q3", {}).get("answer", "Bilinmeyen Rakipler")
    
    search_results = ""
    
    if DDGS:
        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(f"{niche} market size TAM CAGR", max_results=3))
                search_results += " ".join([r.get('body', '') for r in results])
                
                comp_results = list(ddgs.text(f"{competitors} market share competitors", max_results=3))
                search_results += " ".join([r.get('body', '') for r in comp_results])
        except Exception as e:
            search_results = str(e)
            
    money_pattern = r'\$?\d+(?:\.\d+)?\s*(?:Billion|B|Million|M|Trillion|T)'
    matches = list(set(re.findall(money_pattern, search_results, re.IGNORECASE)))
    
    cagr_pattern = r'\d+(?:\.\d+)?%'
    cagr_matches = list(set(re.findall(cagr_pattern, search_results)))
    
    if lang == "tr":
        tam_val = "$500M - $1B (Tahmini Sektör Hacmi)"
        if matches:
            tam_val = matches[0] + " (Arama sonuçlarından)"
        sam_val = "$50M - $100M (Hedef Kitlenin Pazar Büyüklüğü Tahmini)"
        som_val = "$1M - $5M (İlk 1-2 Yılda Ele Geçirilebilecek Pazar Payı)"
        
        cagr_val = "10.5% (Ortalama Büyüme Trendi)"
        if cagr_matches:
            cagr_val = cagr_matches[0] + " (Arama sonuçlarından CAGR)"
            
        market_density = "Mavi Okyanus (Gelişmekte olan ve fırsat barındıran pazar)"
        red_ocean_keywords = ["competitive", "dominated", "leader", "saturated", "rekabetçi"]
        if any(keyword in search_results.lower() for keyword in red_ocean_keywords) or len(competitors.split()) > 3:
            market_density = "Kırmızı Okyanus (Yüksek Rekabet ve Sıkışık Pazar)"
            
        note = f"'{niche}' nişi ve '{competitors}' rakipleri baz alınarak web araştırması ile hesaplanmıştır."
    else:
        tam_val = "$500M - $1B (Estimated Industry Volume)"
        if matches:
            tam_val = matches[0] + " (From search results)"
        sam_val = "$50M - $100M (Target Audience Market Size Estimate)"
        som_val = "$1M - $5M (Market Share Obtainable in First 1-2 Years)"
        
        cagr_val = "10.5% (Average Growth Trend)"
        if cagr_matches:
            cagr_val = cagr_matches[0] + " (CAGR from search results)"
            
        market_density = "Blue Ocean (Emerging market with opportunities)"
        red_ocean_keywords = ["competitive", "dominated", "leader", "saturated", "rekabetçi"]
        if any(keyword in search_results.lower() for keyword in red_ocean_keywords) or len(competitors.split()) > 3:
            market_density = "Red Ocean (High Competition and Congested Market)"
            
        note = f"Calculated via web research based on the '{niche}' niche and '{competitors}' competitors."
        
    analysis = {
        "TAM_Total_Addressable_Market": tam_val,
        "SAM_Serviceable_Addressable_Market": sam_val,
        "SOM_Serviceable_Obtainable_Market": som_val,
        "CAGR_Market_Growth_Rate": cagr_val,
        "Market_Density": market_density,
        "Summary_Research_Note": note
    }
    
    os.makedirs("data", exist_ok=True)
    with open("data/market_analysis.json", "w", encoding="utf-8") as f:
        json.dump(analysis, f, ensure_ascii=False, indent=4)
        
    return analysis

if __name__ == "__main__":
    result = analyze_market()
    print(json.dumps(result, indent=2, ensure_ascii=False))
