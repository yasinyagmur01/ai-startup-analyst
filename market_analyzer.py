"""
market_analyzer.py — Institutional-Grade VC Market Intelligence Engine
=======================================================================
Role  : Lead VC Market Intelligence & Data Scientist
Output: 3-layer JSON → Market_Metrics | Competitor_Flaws | Regulatory_Risks

Banned phrases (never produced):
  "The market is growing rapidly", "High potential", "Fast-growing", "Promising sector"

Every metric MUST cite a data source or explicit mathematical assumption.
"""

import json
import os
import re
import anthropic

try:
    from duckduckgo_search import DDGS
except ImportError:
    DDGS = None

# ─────────────────────────────────────────────────────────────────────────────
# REGULATORY KNOWLEDGE BASE  (country → known bottlenecks)
# ─────────────────────────────────────────────────────────────────────────────
REGULATORY_DB = {
    "turkey": [
        "KVKK (Kişisel Verilerin Korunması Kanunu) — mandatory data localisation and explicit consent flows required before any B2C data processing.",
        "BDDK/SPK licencing — fintech and payment solutions require explicit regulatory approval; typical timeline 6-18 months.",
        "Import tariffs & ÖTV — hardware/IoT devices face up to 25% import duties, compressing unit economics severely.",
        "EPDK energy sector regulation — energy-tech startups must obtain separate EPDK permits.",
        "Turkish Competition Authority (Rekabet Kurumu) — dominant-platform acquisition restrictions tightening since 2022."
    ],
    "türkiye": [
        "KVKK (Kişisel Verilerin Korunması Kanunu) — zorunlu veri yerelleştirme ve açık rıza akışları, B2C veri işleme başlamadan önce tamamlanmalıdır.",
        "BDDK/SPK lisanslama — fintech ve ödeme çözümleri için düzenleyici onay gereklidir; tipik süreç 6-18 ay.",
        "İthalat tarifeleri & ÖTV — donanım/IoT cihazları %25'e varan ithalat vergisiyle karşılaşır, birim ekonomisini ciddi ölçüde baskılar.",
        "EPDK enerji sektörü düzenlemesi — enerji-tech girişimleri ayrıca EPDK izni almak zorundadır.",
        "Rekabet Kurumu — 2022'den itibaren baskın platform satın alma kısıtlamaları sıkılaşıyor."
    ],
    "eu": [
        "GDPR (General Data Protection Regulation) — Art. 17 right-to-erasure and Art. 20 data portability require significant engineering investment; fines up to 4% global annual turnover.",
        "AI Act (2024) — high-risk AI systems (HR-tech, credit scoring, biometrics) require conformity assessments before market entry.",
        "MDR (EU Medical Device Regulation) — health-tech hardware requires CE/MDR certification; notified body queues are 18-36 months.",
        "DSA/DMA — digital gatekeeping rules impose interoperability mandates on platforms above 45M EU users.",
        "State-aid rules — public funding (Horizon Europe, EIC) comes with IP ownership constraints."
    ],
    "usa": [
        "SEC/FINRA registration — fintech platforms offering securities-adjacent products face federal registration; broker-dealer licence costs $50K-$200K upfront.",
        "State-level money-transmitter licences — payments startups need licences in all 50 states; typical cost $500K+ cumulative.",
        "FDA 510(k) clearance — health-tech hardware/software as medical device (SaMD) requires FDA clearance; median timeline 12 months.",
        "FTC data privacy enforcement — COPPA (under-13 data), CCPA/CPRA (California) and 20+ state-level laws create patchwork compliance burden.",
        "FAA Part 135/107 — drone/robotics operations require FAA waivers; commercial Beyond Visual Line of Sight (BVLOS) approvals take 12-24 months."
    ],
    "uk": [
        "UK GDPR & ICO — post-Brexit data adequacy rules; transfers to non-adequate countries need Standard Contractual Clauses.",
        "FCA authorisation — fintech and crypto firms need FCA authorisation (Financial Services and Markets Act 2023); typical timeline 6-12 months.",
        "CMA merger control — acquisitions above £70M turnover threshold scrutinised; digital market investigations increasing.",
        "MHRA — medical device approvals now diverged from EU MDR post-Brexit; separate UKCA marking required.",
        "Online Safety Act (2023) — platforms with user-generated content face mandatory age verification and content moderation duties."
    ],
    "germany": [
        "BDSG (Federal Data Protection Act) — stricter national supplement to GDPR; works council co-determination rights affect HR-tech deployments.",
        "BaFin licencing — fintech, crypto custody, and payment institutions require BaFin licence; AML/KYC obligations are extensive.",
        "Betriebsverfassungsgesetz — software affecting employee monitoring requires works council agreement, slowing B2B enterprise sales.",
        "BSI IT-Grundschutz — critical infrastructure software must comply with BSI cybersecurity baseline; mandatory for public sector clients."
    ]
}

def _detect_country(text: str) -> str:
    """Heuristic country detection from free text."""
    text_l = text.lower()
    for key in REGULATORY_DB:
        if key in text_l:
            return key
    # secondary keyword mapping
    country_map = {
        "tr": "turkey", "türkiye": "türkiye", "istanbul": "turkey", "ankara": "turkey",
        "europe": "eu", "european": "eu", "germany": "germany", "deutschland": "germany",
        "uk": "uk", "united kingdom": "uk", "britain": "uk", "london": "uk",
        "usa": "usa", "united states": "usa", "america": "usa", "us ": "usa",
    }
    for kw, country in country_map.items():
        if kw in text_l:
            return country
    return "global"


def _build_search_queries(vertical: str, niche: str, country: str) -> list[str]:
    """
    Construct institutional-grade search queries per VC research standards.
    Prioritises PDF reports and authoritative databases.
    """
    base = f"{vertical} {niche}"
    queries = [
        f"{base} market size report 2025 2026 filetype:pdf",
        f"site:statista.com {base} {country} market revenue",
        f"{base} TAM SAM SOM market research 2025 site:grandviewresearch.com OR site:mordorintelligence.com",
        f"{base} CAGR compound annual growth rate 2024 2030 market forecast",
        f"{base} competitor market share analysis {country} 2024",
        f"{vertical} regulatory compliance {country} legal requirements 2024 2025",
    ]
    return queries


def _run_searches(queries: list[str], max_per_query: int = 4) -> str:
    """Execute DuckDuckGo searches and return concatenated snippet corpus."""
    if not DDGS:
        return ""
    corpus = []
    for q in queries:
        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(q, max_results=max_per_query))
                for r in results:
                    snippet = r.get("body", "")
                    if snippet:
                        corpus.append(snippet)
        except Exception:
            continue
    return " ".join(corpus)


def _extract_money_figures(text: str) -> list[str]:
    pattern = r'\$\s?\d+(?:\.\d+)?\s*(?:Trillion|Billion|Million|B|M|T)\b'
    return list(set(re.findall(pattern, text, re.IGNORECASE)))


def _extract_cagr(text: str) -> list[str]:
    pattern = r'\b\d+(?:\.\d+)?%\s*(?:CAGR|compound annual|growth rate)\b'
    return list(set(re.findall(pattern, text, re.IGNORECASE)))


def _call_llm_analysis(startup_data: dict, search_corpus: str, country: str, lang: str) -> dict:
    """
    Call Claude with a strict VC-grade prompt enforcing concrete financial templates
    and the 3-layer output structure.
    """
    pitch       = startup_data.get("pitch", "")
    niche       = startup_data.get("q2", {}).get("answer", "")
    competitors = startup_data.get("q3", {}).get("answer", "")
    revenue_model = startup_data.get("q4", {}).get("answer", "")
    mvp_answer  = startup_data.get("q5", {}).get("answer", "")

    money_snippets = _extract_money_figures(search_corpus)[:6]
    cagr_snippets  = _extract_cagr(search_corpus)[:4]
    reg_risks      = REGULATORY_DB.get(country, REGULATORY_DB.get("global", [
        "No specific regulatory database entry for detected geography. Apply GDPR baseline for data handling and local company law for incorporation."
    ]))

    lang_instruction = "Respond ENTIRELY in Turkish (Türkçe). All labels, notes, and values must be in Turkish." if lang == "tr" else "Respond ENTIRELY in English."

    system_prompt = f"""You are a Lead VC Market Intelligence Partner conducting institutional-grade due diligence for a Series A investment decision.

Strict Metrics: The model MUST explicitly calculate and output Market_Metrics containing TAM, SAM, and SOM with absolute mathematical assumptions or data sources based on the target country inside startup_data.json.

Regulatory Barrier: The model MUST identify at least one brutal country-specific regulation (e.g., KVKK for Turkey, GDPR/CE for Germany) under Regulatory_Risks.

Unit_Economics Layer: The model must demand and break down COGS vs. Gross Margins (for hardware/deep-tech like robotics) or LTV:CAC and Payback Period targets (for SaaS/Software) tailored to the operations country in startup_data.json.

Moat_Analysis Layer: The model must evaluate replication difficulty. It must brutally score the startup's defensibility against a competitor with $10M in VC backing, focusing on IP, proprietary algorithms, or supply chain locking.

Choke_Points Layer: The model must output exactly 3 lethal kill-scenarios where this specific startup faces high bankruptcy risk within 18 months (e.g., operational, regulatory, or technical bottlenecks).

Banned Words: You are banned from using cliché phrases like 'high potential', 'rapidly growing', or 'promising sector'. If you use them, the evaluation fails.

MANDATORY OUTPUT FORMAT:
Return ONLY a valid JSON object with exactly these six top-level keys:
  "Market_Metrics", "Competitor_Flaws", "Regulatory_Risks", "Unit_Economics", "Moat_Analysis", "Choke_Points"

No markdown, no explanation text, no code fences. Pure JSON only.

{lang_instruction}"""

    user_prompt = f"""STARTUP BRIEF:
Pitch: {pitch}
Target Niche & Geography: {niche}
Competitors Mentioned: {competitors}
Revenue Model: {revenue_model}
MVP Plan: {mvp_answer}

WEB RESEARCH CORPUS (raw snippets — use as evidence base):
{search_corpus[:3000] if search_corpus else "[No live search data available — derive from first principles and state assumption clearly]"}

EXTRACTED MONEY FIGURES FROM SEARCH: {money_snippets}
EXTRACTED CAGR FIGURES FROM SEARCH:  {cagr_snippets}

KNOWN REGULATORY RISKS FOR '{country.upper()}':
{json.dumps(reg_risks, ensure_ascii=False)}

YOUR TASK — produce the following JSON exactly:

{{
  "Market_Metrics": {{
    "TAM": {{
      "value": "<absolute dollar figure e.g. $4.2B>",
      "scope": "<Global / Regional — define exactly>",
      "source_assumption": "<cite the report, database, or the mathematical formula used>"
    }},
    "SAM": {{
      "value": "<dollar figure>",
      "scope": "<Target country's realistic addressable share>",
      "source_assumption": "<cite the geographic penetration rate or formula applied>"
    }},
    "SOM": {{
      "value": "<dollar figure>",
      "scope": "<Year 1 obtainable based on this startup's stated MVP and capability>",
      "source_assumption": "<cite the conversion funnel math or benchmark used>"
    }},
    "CAGR": {{
      "value": "<percentage>",
      "period": "<e.g. 2024–2030>",
      "source_assumption": "<cite source or derivation>"
    }},
    "Market_Density": "<Red Ocean / Blue Ocean — with specific justification referencing named competitors>"
  }},
  "Competitor_Flaws": [
    {{
      "competitor": "<name>",
      "known_weakness": "<specific structural flaw: pricing, UX gap, geography blind spot, tech debt, etc.>",
      "exploit_window": "<how and when this startup can exploit it>"
    }}
  ],
  "Regulatory_Risks": [
    {{
      "regulation": "<exact law/regulation name>",
      "impact": "<concrete operational or financial impact on this startup>",
      "mitigation": "<specific recommended action with timeline>"
    }}
  ],
  "Unit_Economics": {{
    "model_type": "<e.g. SaaS, Hardware, Marketplace>",
    "metrics_breakdown": "<Provide COGS vs. Gross Margins (for hardware/deep-tech) or LTV:CAC and Payback Period targets (for SaaS/Software) tailored to the operations country>"
  }},
  "Moat_Analysis": {{
    "replication_difficulty_score": "<1-10 scale>",
    "defensibility": "<Brutal evaluation of defensibility against a competitor with $10M in VC backing, focusing on IP, proprietary algorithms, or supply chain locking>"
  }},
  "Choke_Points": [
    {{
      "lethal_scenario": "<Specific operational, regulatory, or technical kill-scenario #1 leading to bankruptcy within 18 months>"
    }},
    {{
      "lethal_scenario": "<Lethal kill-scenario #2>"
    }},
    {{
      "lethal_scenario": "<Lethal kill-scenario #3>"
    }}
  ]
}}

Be brutal, specific, and data-driven. Every field must contain concrete information."""

    try:
        client = anthropic.Anthropic()
        message = client.messages.create(
            model="claude-opus-4-5",
            max_tokens=2000,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}]
        )
        raw = message.content[0].text.strip()
        # Strip accidental markdown fences
        if raw.startswith("```"):
            raw = re.sub(r"^```[a-z]*\n?", "", raw)
            raw = re.sub(r"\n?```$", "", raw)
        return json.loads(raw)
    except json.JSONDecodeError:
        return None
    except Exception as e:
        return {"error": str(e)}


def _fallback_analysis(startup_data: dict, search_corpus: str, country: str, lang: str) -> dict:
    """
    Rule-based fallback when the LLM call fails.
    Still enforces the 3-layer structure with honest uncertainty flags.
    """
    money  = _extract_money_figures(search_corpus)
    cagrs  = _extract_cagr(search_corpus)
    niche  = startup_data.get("q2", {}).get("answer", "N/A")
    comps  = startup_data.get("q3", {}).get("answer", "N/A")
    reg    = REGULATORY_DB.get(country, ["No specific regulatory data for this geography. Defaulting to GDPR baseline."])

    if lang == "tr":
        tam_v = money[0] if money else "$500M – $2B"
        cagr_v = cagrs[0] if cagrs else "12% (sektör ortalaması varsayımı)"
        density = "Kırmızı Okyanus (Yüksek Rekabet)" if len(comps.split()) > 8 else "Mavi Okyanus (Gelişmekte)"
        return {
            "Market_Metrics": {
                "TAM": {"value": tam_v, "scope": "Global sektör tavanı", "source_assumption": "DuckDuckGo arama korpusundan regex ile çıkarıldı — LLM doğrulaması yapılamadı"},
                "SAM": {"value": "TAM'ın %5-15'i (coğrafi nüfus ve internet penetrasyonu baz alınarak)", "scope": niche, "source_assumption": "Nüfus oranı varsayımı: hedef ülke payı"},
                "SOM": {"value": "SAM'ın %0,5-2'si", "scope": "1. Yıl MVP lansmanı", "source_assumption": "Standart SaaS/marketplace kıyaslama dönüşüm hunisi: 0,5% – 2%"},
                "CAGR": {"value": cagr_v, "period": "2024–2030", "source_assumption": "Arama korpusundan regex ile çıkarıldı"},
                "Market_Density": density
            },
            "Competitor_Flaws": [
                {"competitor": comps[:80], "known_weakness": "Detaylı rekabet analizi için LLM çağrısı başarısız oldu — veriler yetersiz", "exploit_window": "Manuel araştırma gerekli"}
            ],
            "Regulatory_Risks": [
                {"regulation": r, "impact": "Operasyonel veya finansal etki tespiti için hukuki danışmanlık gereklidir", "mitigation": "Kuruluş öncesi hukuki görüş alın"}
                for r in reg[:3]
            ]
        }
    else:
        tam_v = money[0] if money else "$500M – $2B"
        cagr_v = cagrs[0] if cagrs else "12% (industry average assumption)"
        density = "Red Ocean (High Competition)" if len(comps.split()) > 8 else "Blue Ocean (Emerging)"
        return {
            "Market_Metrics": {
                "TAM": {"value": tam_v, "scope": "Global sector ceiling", "source_assumption": "Regex-extracted from DuckDuckGo search corpus — LLM validation unavailable"},
                "SAM": {"value": "5–15% of TAM (based on geographic population and internet penetration)", "scope": niche, "source_assumption": "Population-ratio assumption: target country's share of global addressable market"},
                "SOM": {"value": "0.5–2% of SAM", "scope": "Year 1 MVP launch", "source_assumption": "Standard SaaS/marketplace benchmark conversion funnel: 0.5% – 2%"},
                "CAGR": {"value": cagr_v, "period": "2024–2030", "source_assumption": "Regex-extracted from search corpus"},
                "Market_Density": density
            },
            "Competitor_Flaws": [
                {"competitor": comps[:80], "known_weakness": "LLM call failed — insufficient data for detailed competitor weakness analysis", "exploit_window": "Manual research required"}
            ],
            "Regulatory_Risks": [
                {"regulation": r, "impact": "Legal/financial impact assessment requires qualified legal counsel", "mitigation": "Obtain legal opinion prior to incorporation and product launch"}
                for r in reg[:3]
            ]
        }


def analyze_market(lang: str = "en") -> dict:
    """
    Institutional-grade market analysis entry point.

    Pipeline:
      1. Load startup_data.json
      2. Detect target country from niche/pitch text
      3. Build institutional search queries (PDF reports + authoritative domains)
      4. Run DuckDuckGo searches
      5. Call Claude with strict VC prompt → 3-layer JSON
      6. Fallback to rule-based if LLM fails
      7. Persist to data/market_analysis.json and return
    """
    data_path = "data/startup_data.json"
    if not os.path.exists(data_path):
        err = "Veri bulunamadı. Lütfen önce mülakatı tamamlayın." if lang == "tr" else "Data not found. Please complete the interview first."
        return {"error": err, "hata": err}

    with open(data_path, "r", encoding="utf-8") as f:
        startup_data = json.load(f)

    pitch  = startup_data.get("pitch", "")
    niche  = startup_data.get("q2", {}).get("answer", "general market")
    comps  = startup_data.get("q3", {}).get("answer", "")

    # ── 1. Country detection ──────────────────────────────────────────────────
    combined_text = f"{pitch} {niche} {comps}"
    country = _detect_country(combined_text)

    # ── 2. Vertical classification (simple keyword heuristic) ─────────────────
    vertical_map = {
        ("saas", "software", "b2b", "platform", "api"): "SaaS B2B software",
        ("ecommerce", "e-commerce", "marketplace", "retail", "shop"): "e-commerce marketplace",
        ("hardware", "iot", "robotics", "device", "sensor"): "hardware IoT robotics",
        ("health", "medtech", "medical", "biotech", "pharma"): "health medtech biotech",
        ("fintech", "payment", "banking", "insurance", "lending"): "fintech payments",
        ("deep tech", "ai", "ml", "nlp", "computer vision"): "deep tech AI ML",
    }
    vertical = "technology startup"
    for keywords, label in vertical_map.items():
        if any(kw in combined_text.lower() for kw in keywords):
            vertical = label
            break

    # ── 3. Institutional search queries ───────────────────────────────────────
    queries = _build_search_queries(vertical, niche[:60], country)

    # ── 4. Web search ─────────────────────────────────────────────────────────
    search_corpus = _run_searches(queries, max_per_query=4)

    # ── 5. LLM deep-dive analysis ─────────────────────────────────────────────
    result = _call_llm_analysis(startup_data, search_corpus, country, lang)

    # ── 6. Fallback if LLM failed ─────────────────────────────────────────────
    if result is None or "error" in result:
        result = _fallback_analysis(startup_data, search_corpus, country, lang)

    # Attach metadata
    result["_meta"] = {
        "country_detected": country,
        "vertical_classified": vertical,
        "search_queries_used": queries,
        "corpus_length_chars": len(search_corpus),
        "lang": lang
    }

    # ── 7. Persist ────────────────────────────────────────────────────────────
    os.makedirs("data", exist_ok=True)
    with open("data/market_analysis.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=4)

    return result


if __name__ == "__main__":
    result = analyze_market(lang="en")
    print(json.dumps(result, indent=2, ensure_ascii=False))
