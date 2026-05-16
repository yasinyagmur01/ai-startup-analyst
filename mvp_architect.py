import json
import os

def get_system_prompt(lang="en"):
    """
    Returns the system prompt for the LLM based on the selected language.
    Note: Currently not injected into an API call, but ready for future integration.
    """
    if lang == "tr":
        return "Sen uzman bir MVP mimarısın. Girişim verilerini analiz ederek MVP kapsamını ve kurucu sprint planını JSON formatında oluştur."
    return "You are an expert MVP architect. Analyze the startup data to generate the MVP scope and founder sprint plan in JSON format."

def analyze_mvp(lang="en"):
    """
    Reads startup_data.json, market_analysis.json, and finance_analysis.json.
    Generates an MVP architecture, timeline, complexity score, and tech stack recommendations.
    Saves the result to data/mvp_analysis.json.
    """
    data_dir = "data"
    startup_data_path = os.path.join(data_dir, "startup_data.json")
    market_data_path = os.path.join(data_dir, "market_analysis.json")
    finance_data_path = os.path.join(data_dir, "finance_analysis.json")
    
    # Check if files exist
    if not os.path.exists(startup_data_path):
        err = "Mülakat verileri eksik. Lütfen mülakatı tamamlayın." if lang == "tr" else "Interview data is missing. Please complete the interview first."
        return {"error": err, "hata": err}
    
    # Read files with default fallbacks if market/finance are missing
    with open(startup_data_path, "r", encoding="utf-8") as f:
        startup_data = json.load(f)
        
    market_data = {}
    if os.path.exists(market_data_path):
        with open(market_data_path, "r", encoding="utf-8") as f:
            market_data = json.load(f)
            
    finance_data = {}
    if os.path.exists(finance_data_path):
        with open(finance_data_path, "r", encoding="utf-8") as f:
            finance_data = json.load(f)
            
    # Extract needed variables
    problem = startup_data.get("q1", {}).get("answer", "").lower()
    target_audience = startup_data.get("q2", {}).get("answer", "").lower()
    competitors = startup_data.get("q3", {}).get("answer", "").lower()
    business_model = startup_data.get("q4", {}).get("answer", "").lower()
    mvp_idea = startup_data.get("q5", {}).get("answer", "").lower()
    
    capital_intensity = finance_data.get("Capital_Intensity", finance_data.get("Sermaye_Yogunlugu", "Orta"))
    
    # 1. Karmaşıklık Skoru (Complexity Index)
    complexity = 5
    if lang == "tr":
        complexity_reasoning = "Ortalama bir yazılım projesi zorluğu."
        
        if any(keyword in problem + mvp_idea for keyword in ["yapay zeka", "ai", "makine öğrenmesi", "llm", "agent", "bot", "deep learning"]):
            complexity += 3
            complexity_reasoning = "Yapay zeka/LLM entegrasyonu gerektirdiği için teknik karmaşıklık yüksek (API bağımlılıkları, prompt engineering, context yönetimi)."
        elif any(keyword in problem + mvp_idea for keyword in ["donanım", "hardware", "iot", "sensör"]):
            complexity += 4
            complexity_reasoning = "Donanım bileşeni barındırıyor. Prototipleme, tedarik zinciri ve üretim süreçleri karmaşıklığı ciddi oranda artırıyor."
        elif any(keyword in business_model for keyword in ["pazaryeri", "marketplace"]):
            complexity += 2
            complexity_reasoning = "Pazaryeri modeli. Teknik olarak çok zor olmasa da, iki farklı kullanıcı tipini (alıcı/satıcı) eş zamanlı yönetmek operasyonel karmaşıklık yaratır."
        
        if any(keyword in mvp_idea for keyword in ["no-code", "no code", "manuel", "form", "excel", "whatsapp"]):
            complexity -= 3
            complexity_reasoning = "MVP için no-code/manuel süreçler planlanmış, bu sayede ilk lansman teknik olarak çok kolaylaştırılmış."
    else:
        complexity_reasoning = "Average software project difficulty."
        
        if any(keyword in problem + mvp_idea for keyword in ["yapay zeka", "ai", "makine öğrenmesi", "llm", "agent", "bot", "deep learning"]):
            complexity += 3
            complexity_reasoning = "High technical complexity due to AI/LLM integration (API dependencies, prompt engineering, context management)."
        elif any(keyword in problem + mvp_idea for keyword in ["donanım", "hardware", "iot", "sensör", "sensor"]):
            complexity += 4
            complexity_reasoning = "Involves hardware components. Prototyping, supply chain, and manufacturing significantly increase complexity."
        elif any(keyword in business_model for keyword in ["pazaryeri", "marketplace"]):
            complexity += 2
            complexity_reasoning = "Marketplace model. While not technically hard, managing two user types simultaneously creates operational complexity."
        
        if any(keyword in mvp_idea for keyword in ["no-code", "no code", "manuel", "manual", "form", "excel", "whatsapp"]):
            complexity -= 3
            complexity_reasoning = "No-code/manual processes planned for MVP, greatly easing the technical aspect of the initial launch."
            
    complexity = max(1, min(10, complexity))
    
    # 2. Pazara Çıkış Süresi (Time-to-Market)
    if lang == "tr":
        if complexity <= 3:
            time_to_market = "1-2 Hafta"
        elif complexity <= 6:
            time_to_market = "3-6 Hafta"
        elif complexity <= 8:
            time_to_market = "2-3 Ay"
        else:
            time_to_market = "4-6 Ay+"
    else:
        if complexity <= 3:
            time_to_market = "1-2 Weeks"
        elif complexity <= 6:
            time_to_market = "3-6 Weeks"
        elif complexity <= 8:
            time_to_market = "2-3 Months"
        else:
            time_to_market = "4-6 Months+"

    # 3. MVP Kapsamı (Core Feature Set)
    core_features = []
    cut_features = []
    
    if lang == "tr":
        if "ai" in problem + mvp_idea or "yapay zeka" in problem + mvp_idea:
            core_features.append("Kullanıcıdan girdi alan ve basit bir LLM (Örn: OpenAI API) çağrısı ile çıktı dönen tek sayfalık arayüz.")
            cut_features.append("Kullanıcı yetkilendirmesi (Login/Signup - ilk etapta şifresiz test edin).")
            cut_features.append("Geçmiş sohbetleri veritabanına kaydetme (Kısa vadede session state yeterli).")
            cut_features.append("Özel model eğitimi (Fine-tuning yerine ilk başta prompt engineering kullanın).")
        elif "pazaryeri" in business_model or "marketplace" in business_model:
            core_features.append("Alıcılar için basit bir listeleme sayfası.")
            core_features.append("Satıcılar için WhatsApp veya Typeform üzerinden manuel talep toplama akışı.")
            cut_features.append("Otomatik ödeme sistemi (Ödemeleri ilk 10 müşteri için manuel/EFT alın).")
            cut_features.append("Gelişmiş filtreleme ve arama algoritmaları.")
        elif "saas" in business_model:
            core_features.append("Çözdüğünüz ana problemi gösteren interaktif bir demo veya 'tek tıkla sonuç' butonu.")
            core_features.append("Erken erişim (Waitlist) veya basit bir Stripe/Iyzico ödeme linki.")
            cut_features.append("Kullanıcı profilleri, ayarlar sayfası ve dashboard.")
            cut_features.append("Otomatik faturalandırma ve ekip yönetimi modülleri.")
        else:
            core_features.append(f"Belirttiğiniz şu özelliği manuel veya çok basit bir arayüzle sunmak: '{mvp_idea[:50]}...'")
            cut_features.append("Mobil uygulama (Önce mobil uyumlu web sitesi ile test edin).")
            cut_features.append("Otomatik onboarding e-postaları.")
    else:
        if "ai" in problem + mvp_idea or "yapay zeka" in problem + mvp_idea:
            core_features.append("Single-page interface taking user input and returning an output via a simple LLM call (e.g., OpenAI API).")
            cut_features.append("User authentication (Login/Signup - test without passwords initially).")
            cut_features.append("Saving chat history to database (Session state is enough for now).")
            cut_features.append("Custom model training (Use prompt engineering first instead of fine-tuning).")
        elif "pazaryeri" in business_model or "marketplace" in business_model:
            core_features.append("Simple listing page for buyers.")
            core_features.append("Manual lead generation flow for sellers via WhatsApp or Typeform.")
            cut_features.append("Automated payment system (Take payments manually for the first 10 customers).")
            cut_features.append("Advanced filtering and search algorithms.")
        elif "saas" in business_model:
            core_features.append("Interactive demo or a 'one-click result' button showcasing the main problem you solve.")
            core_features.append("Early access (Waitlist) or a simple Stripe payment link.")
            cut_features.append("User profiles, settings page, and dashboard.")
            cut_features.append("Automated billing and team management modules.")
        else:
            core_features.append(f"Offering the feature you mentioned manually or via a very simple interface: '{mvp_idea[:50]}...'")
            cut_features.append("Mobile application (Test with a mobile-responsive website first).")
            cut_features.append("Automated onboarding emails.")

    # 4. Teknoloji ve Araç Önerileri
    tech_stack = []
    if lang == "tr":
        if complexity <= 4 or "no-code" in mvp_idea:
            tech_stack.append("🌐 **Arayüz/Frontend**: Softr veya Bubble (Hızlı web uygulaması için)")
            tech_stack.append("⚙️ **Arka Plan/Otomasyon**: Make.com veya Zapier")
            tech_stack.append("🗄️ **Veritabanı**: Airtable veya Google Sheets")
        elif "yapay zeka" in problem + mvp_idea or "ai" in problem + mvp_idea:
            tech_stack.append("🐍 **Backend/Core**: Python (FastAPI veya Streamlit)")
            tech_stack.append("🧠 **AI Entegrasyonu**: LangChain veya doğrudan OpenAI/Anthropic API")
            tech_stack.append("🌐 **Arayüz**: Streamlit (Sıfır frontend eforu için) veya Vercel + Next.js (Daha iyi UX için)")
            tech_stack.append("🗄️ **Veritabanı**: Supabase (PostgreSQL) veya Firebase")
        else:
            tech_stack.append("🌐 **Web Çerçevesi**: Next.js (React) veya Django/Flask (Python)")
            tech_stack.append("🎨 **Tasarım**: TailwindCSS veya hazır UI kütüphaneleri (shadcn/ui)")
            tech_stack.append("🗄️ **Veritabanı**: Supabase veya MongoDB Atlas")
            
        if "mobil" in mvp_idea or "uygulama" in mvp_idea or "app" in mvp_idea:
            tech_stack.append("📱 **Mobil (Eğer zorunluysa)**: Flutterflow (No-code) veya React Native (Expo)")
    else:
        if complexity <= 4 or "no-code" in mvp_idea:
            tech_stack.append("🌐 **Frontend**: Softr or Bubble (For quick web apps)")
            tech_stack.append("⚙️ **Backend/Automation**: Make.com or Zapier")
            tech_stack.append("🗄️ **Database**: Airtable or Google Sheets")
        elif "yapay zeka" in problem + mvp_idea or "ai" in problem + mvp_idea:
            tech_stack.append("🐍 **Backend/Core**: Python (FastAPI or Streamlit)")
            tech_stack.append("🧠 **AI Integration**: LangChain or direct OpenAI/Anthropic API")
            tech_stack.append("🌐 **Frontend**: Streamlit (Zero frontend effort) or Vercel + Next.js (Better UX)")
            tech_stack.append("🗄️ **Database**: Supabase (PostgreSQL) or Firebase")
        else:
            tech_stack.append("🌐 **Web Framework**: Next.js (React) or Django/Flask (Python)")
            tech_stack.append("🎨 **Design**: TailwindCSS or ready UI libraries (shadcn/ui)")
            tech_stack.append("🗄️ **Database**: Supabase or MongoDB Atlas")
            
        if "mobil" in mvp_idea or "uygulama" in mvp_idea or "app" in mvp_idea:
            tech_stack.append("📱 **Mobile (If strictly necessary)**: Flutterflow (No-code) or React Native (Expo)")

    # 5. Sprint (To-Do List) Format
    if lang == "tr":
        sprint_plan = [
            {"week": "1. Hafta (Hazırlık ve Temel Kurgu)", "tasks": [
                "Hedef kitleyle (min 5 kişi) ürün fikri üzerine kısa görüşmeler yapın.",
                f"Önerilen araçlardan birini ({tech_stack[0].split(':')[1].strip()}) seçip hesapları açın.",
                "Domain (alan adı) satın alın ve basit bir açılış (landing) sayfası kurun."
            ]},
            {"week": "2. Hafta (Core MVP Geliştirme)", "tasks": [
                f"Odaklanılacak özellik: {core_features[0]}",
                "Tüm elediğimiz özellikleri ('nice-to-have') kesinlikle geliştirmeye dahil etmeyin.",
                "Tasarımda mükemmellik aramayın, sadece fonksiyonun çalışmasına odaklanın."
            ]},
            {"week": "3. Hafta (Test ve Erken Doğrulama)", "tasks": [
                "Ürünü kendi başınıza ve çevrenizden 2-3 kişiye test ettirin.",
                "Kritik hataları (bug) giderin, arayüzü sadece anlaşılır hale getirin.",
                "Manuel bir ödeme veya 'talep toplama' adımı ekleyin."
            ]},
            {"week": "4. Hafta (Canlıya Alma ve Lansman)", "tasks": [
                "Reddit, Product Hunt, X veya sektörel LinkedIn gruplarında MVP'nizi paylaşın.",
                "İlk kullanıcılardan anında geri bildirim almak için bir iletişim kanalı (Discord/WhatsApp) kurun.",
                "Gelen tepkilere göre pivot etme veya devam etme kararını verin."
            ]}
        ]
    else:
        sprint_plan = [
            {"week": "Week 1 (Prep & Basic Setup)", "tasks": [
                "Conduct short interviews with your target audience (min 5 people) about the product idea.",
                f"Choose one of the recommended tools ({tech_stack[0].split(':')[1].strip()}) and create an account.",
                "Buy a domain and set up a simple landing page."
            ]},
            {"week": "Week 2 (Core MVP Development)", "tasks": [
                f"Focus feature: {core_features[0]}",
                "Absolutely exclude all features we cut ('nice-to-have') from development.",
                "Don't aim for design perfection, focus solely on functionality."
            ]},
            {"week": "Week 3 (Testing & Early Validation)", "tasks": [
                "Test the product yourself and with 2-3 people from your circle.",
                "Fix critical bugs, just make the interface understandable.",
                "Add a manual payment or 'lead collection' step."
            ]},
            {"week": "Week 4 (Go-Live & Launch)", "tasks": [
                "Share your MVP on Reddit, Product Hunt, X, or industry LinkedIn groups.",
                "Set up a communication channel (Discord/WhatsApp) for instant feedback from early users.",
                "Decide whether to pivot or persevere based on reactions."
            ]}
        ]

    analysis = {
        "Complexity_Score": f"{complexity}/10",
        "Complexity_Reasoning": complexity_reasoning,
        "Time_to_Market": time_to_market,
        "MVP_Focus_Features": core_features,
        "MVP_Cut_Features": cut_features,
        "Tech_Recommendations": tech_stack,
        "Founder_Sprint_Plan": sprint_plan
    }
    
    os.makedirs(data_dir, exist_ok=True)
    with open(os.path.join(data_dir, "mvp_analysis.json"), "w", encoding="utf-8") as f:
        json.dump(analysis, f, ensure_ascii=False, indent=4)
        
    return analysis

if __name__ == "__main__":
    result = analyze_mvp()
    print(json.dumps(result, indent=2, ensure_ascii=False))
