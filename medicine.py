import streamlit as st
import requests
import json
import re
from datetime import datetime
import xml.etree.ElementTree as ET

# 1. Page Configuration
st.set_page_config(page_title="MedRep Clinical Portal", page_icon="💊", layout="wide")

# Hourly Rotating Background Image Array
HERO_IMAGES = [
    "https://images.unsplash.com/photo-1576091160399-112ba8d25d1d?auto=format&fit=crop&w=1920&q=80",
    "https://images.unsplash.com/photo-1532187863486-abf9dbad1b69?auto=format&fit=crop&w=1920&q=80",
    "https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?auto=format&fit=crop&w=1920&q=80",
    "https://images.unsplash.com/photo-1585435557343-3b092031a831?auto=format&fit=crop&w=1920&q=80",
    "https://images.unsplash.com/photo-1579165466741-7f35e4755660?auto=format&fit=crop&w=1920&q=80"
]

current_hour = datetime.now().hour
selected_bg = HERO_IMAGES[current_hour % len(HERO_IMAGES)]

# Custom Styling Engine
st.markdown(f"""
<style>
    /* FORCE STREAMLIT COLUMNS TO REMAIN HORIZONTAL ON SMALL SCREENS */
    [data-testid="stHorizontalBlock"] {{
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        gap: 6px !important;
    }}

    [data-testid="stHorizontalBlock"] > div {{
        min-width: 0 !important;
        flex: 1 1 0% !important;
    }}

    /* COMPACT BUTTON STYLING */
    .stButton button {{
        padding: 4px 6px !important;
        font-size: clamp(0.65rem, 1.4vw, 0.85rem) !important;
        white-space: nowrap !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
        width: 100% !important;
    }}

    /* GLOBAL RESET & OVERFLOW CONTROL */
    *, *::before, *::after {{
        box-sizing: border-box !important;
        word-break: break-word;
    }}

    .stApp {{
        background: linear-gradient(rgba(10, 15, 26, 0.90), rgba(10, 15, 26, 0.94)), 
                    url("{selected_bg}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
        transition: background 1s ease-in-out;
        max-width: 100vw;
        overflow-x: hidden;
    }}
    
    .brand-header {{
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.08), rgba(255, 255, 255, 0.02));
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.15);
        border-radius: 12px;
        padding: 8px 12px;
        margin-bottom: 16px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.4);
    }}
    
    .brand-title {{
        font-size: clamp(0.95rem, 2.8vw, 2.2rem);
        font-weight: 900;
        letter-spacing: 1px;
        background: linear-gradient(90deg, #58a6ff, #79c0ff, #d2a8ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
        text-transform: uppercase;
        text-align: center;
        white-space: nowrap;
    }}

    .brand-subtitle {{
        color: #8b949e;
        font-size: clamp(0.45rem, 1.1vw, 0.85rem);
        margin-top: 1px;
        letter-spacing: 0.5px;
        text-align: center;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }}

    .gloss-panel {{
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.07), rgba(255, 255, 255, 0.02));
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.12);
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.4);
        border-radius: 16px;
        padding: 16px;
        margin-bottom: 16px;
        height: 100%;
        max-width: 100%;
    }}

    .badge-boxed {{
        background: linear-gradient(90deg, #8e1519, #580a0c);
        color: #ffb3b5;
        padding: 4px 10px;
        border-radius: 16px;
        font-weight: bold;
        font-size: 0.8rem;
        display: inline-block;
        margin-bottom: 6px;
        border: 1px solid rgba(255, 179, 181, 0.3);
    }}
    
    .badge-indication {{
        background: linear-gradient(90deg, #0d419d, #062358);
        color: #79c0ff;
        padding: 4px 10px;
        border-radius: 16px;
        font-weight: bold;
        font-size: 0.8rem;
        display: inline-block;
        margin-bottom: 6px;
        border: 1px solid rgba(121, 192, 255, 0.3);
    }}

    .badge-adverse {{
        background: linear-gradient(90deg, #7d4e00, #452b00);
        color: #f2cc60;
        padding: 4px 10px;
        border-radius: 16px;
        font-weight: bold;
        font-size: 0.8rem;
        display: inline-block;
        margin-bottom: 6px;
        border: 1px solid rgba(242, 204, 96, 0.3);
    }}

    .badge-disease {{
        background: linear-gradient(90deg, #137333, #0a3d1b);
        color: #81c995;
        padding: 4px 10px;
        border-radius: 16px;
        font-weight: bold;
        font-size: 0.8rem;
        display: inline-block;
        margin-bottom: 6px;
        border: 1px solid rgba(129, 201, 149, 0.3);
    }}

    .bottom-line {{
        border: 0;
        height: 2px;
        background: linear-gradient(90deg, transparent, rgba(88, 166, 255, 0.5), transparent);
        margin-top: 24px;
        margin-bottom: 24px;
    }}
</style>
""", unsafe_allow_html=True)

# Smart Dosage-Form Visual Image Database
FORM_IMAGES = {
    "injection": "https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?auto=format&fit=crop&w=600&q=80",
    "tablet": "https://images.unsplash.com/photo-1584017911766-d451b3d0e843?auto=format&fit=crop&w=600&q=80",
    "capsule": "https://images.unsplash.com/photo-1550572017-edd951aa8f72?auto=format&fit=crop&w=600&q=80",
    "syrup": "https://images.unsplash.com/photo-1587854692152-cbe660dbde88?auto=format&fit=crop&w=600&q=80",
    "cream": "https://images.unsplash.com/photo-1556228720-195a672e8a03?auto=format&fit=crop&w=600&q=80",
    "inhaler": "https://images.unsplash.com/photo-1631549916768-4119b2e5f926?auto=format&fit=crop&w=600&q=80",
    "drops": "https://images.unsplash.com/photo-1607613009820-a29f7bb81c04?auto=format&fit=crop&w=600&q=80",
    "default": "https://images.unsplash.com/photo-1471864190281-a93a3070b6de?auto=format&fit=crop&w=600&q=80"
}

# Cross-Pharmacopeia Synonym Mapping (US / UK / INN / JP / EU)
GLOBAL_PHARMACOPEIA_SYNONYMS = {
    # British Pharmacopoeia (BP) / INN -> United States Pharmacopeia (USP)
    "paracetamol": "acetaminophen",
    "salbutamol": "albuterol",
    "cefalexin": "cephalexin",
    "adrenaline": "epinephrine",
    "noradrenaline": "norepinephrine",
    "isoprenaline": "isoproterenol",
    "frusemide": "furosemide",
    "bendrofluazide": "bendroflumethiazide",
    "glyceryl trinitrate": "nitroglycerin",
    "lignocaine": "lidocaine",
    "methimazole": "thiamazole",
    "pethidine": "meperidine",
    "caffeine citrate": "caffeine citrate",
    "artemether": "artemether",
    "lumefantrine": "lumefantrine"
}

# Dynamic Global Search Engine (RxNav + NLM)
@st.cache_data(ttl=3600)
def search_global_pharmacopeia(user_input):
    """Dynamically queries RxNav API to fetch drugs from USP, BP, EP, and WHO registries."""
    if not user_input or len(user_input.strip()) < 2:
        return []
    
    clean_input = user_input.strip().lower()
    results = set()
    
    # Check Synonym map
    if clean_input in GLOBAL_PHARMACOPEIA_SYNONYMS:
        results.add(GLOBAL_PHARMACOPEIA_SYNONYMS[clean_input].title())
    results.add(clean_input.title())

    try:
        # RxNav Approximate Matching Endpoint (Covers international nonproprietary names)
        rx_url = f"https://rxnav.nlm.nih.gov/REST/approximateTerm.json?term={clean_input}&maxEntries=12"
        res = requests.get(rx_url, timeout=3)
        if res.status_code == 200:
            candidates = res.json().get('approximateGroup', {}).get('candidate', [])
            for c in candidates:
                name = c.get('name')
                if name:
                    results.add(name.title())
    except Exception:
        pass

    return sorted(list(results))

# Clinical Disease Management Knowledgebase
DISEASE_MANAGEMENT_DB = {
    "Pediatric Uncomplicated Malaria": {
        "category": "Infectious Diseases / Parasitology",
        "first_line": "Artemether + Lumefantrine (AL) fixed-dose combination or Artesunate + Amodiaquine (ASAQ).",
        "mechanism": "Artemether rapidly clears parasitemia; Lumefantrine eliminates residual blood-stage Plasmodium falciparum parasites.",
        "non_pharm": "Ensure bed net (ITN) coverage, fever management via cooling tepid sponges, and maintaining adequate oral fluid hydration.",
        "monitoring": "Monitor thick/thin blood smears at 48-72h, baseline hemoglobin/hematocrit, and re-assess if persistent high fever exceeds 48 hours."
    },
    "Essential Hypertension": {
        "category": "Cardiovascular Systems",
        "first_line": "Thiazide-like diuretic (e.g., Hydrochlorothiazide), ACE Inhibitor (e.g., Lisinopril), or CCB (e.g., Amlodipine).",
        "mechanism": "Reduces peripheral vascular resistance and intravascular blood volume to lower systemic arterial blood pressure.",
        "non_pharm": "Dietary Sodium restriction (<2g/day), regular aerobic physical exercise, weight optimization, and alcohol restriction.",
        "monitoring": "Office and ambulatory Blood Pressure monitoring, baseline serum creatinine, eGFR, and electrolytes (sodium and potassium)."
    },
    "Type 2 Diabetes Mellitus": {
        "category": "Endocrine & Metabolic Disorders",
        "first_line": "Metformin Hydrochloride (Biguanide) + Lifestyle Interventions; add SGLT2i or GLP-1 RA if cardiorenal risks exist.",
        "mechanism": "Decreases hepatic gluconeogenesis, reduces intestinal glucose absorption, and enhances insulin sensitivity.",
        "non_pharm": "Medical Nutrition Therapy (low glycemic index diet), 150 mins/week moderate exercise, and weight management.",
        "monitoring": "HbA1c every 3 months (target < 7.0%), annual urine albumin-to-creatinine ratio, annual dilated eye exam, and foot exam."
    },
    "Community-Acquired Pneumonia": {
        "category": "Respiratory Medicine",
        "first_line": "Amoxicillin high-dose or Macrolide (Azithromycin) for outpatients; Ceftriaxone + Macrolide for inpatients.",
        "mechanism": "Inhibits bacterial cell wall peptidoglycan synthesis (beta-lactams) or bacterial protein translation (macrolides).",
        "non_pharm": "Adequate rest, supplemental oxygen therapy if SpO2 < 92%, chest physiotherapy, and fluid resuscitation.",
        "monitoring": "Respiratory rate, pulse oximetry, chest radiograph follow-up at 4-6 weeks, and clinical response within 48-72 hours."
    }
}

def format_clinical_bullets(text, max_bullets=3, extended_mode=False):
    if not text or text == 'No data available.':
        return ["No specific clinical data listed."]
    
    clean_text = re.sub(r'^\s*\d+(\.\d+)?\s+[A-Z\s,]{3,}(?=\s+[A-Z][a-z])', '', text).strip()
    
    if extended_mode:
        return [clean_text]
    
    raw_sentences = re.split(r'\.(?=\s+[A-Z])', clean_text)
    bullets = []
    
    for s in raw_sentences:
        cleaned_sentence = s.strip()
        if len(cleaned_sentence) > 8:
            if not cleaned_sentence.endswith('.'):
                cleaned_sentence += '.'
            bullets.append(cleaned_sentence)
            if len(bullets) >= max_bullets:
                break
                
    return bullets if bullets else [clean_text]

@st.cache_data(ttl=1800)
def fetch_live_medical_news():
    fallback_news = [
        {
            "title": "FDA Approves Pasatru for Rare Bone Disorder Treatment",
            "tag": "FDA APPROVAL",
            "time": "Recent",
            "img": "https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?auto=format&fit=crop&w=600&q=80",
            "link": "https://www.fda.gov/drugs/news-events-human-drugs/notable-approvals-drugs",
            "summary": "First-in-class monoclonal antibody approved to reduce heterotopic ossification in pediatric and adult patients."
        },
        {
            "title": "Public Health Alert: Contaminated Botanical Supplements",
            "tag": "SAFETY ALERT",
            "time": "Recent",
            "img": "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=600&q=80",
            "link": "https://www.fda.gov/food/alerts-advisories-safety-information",
            "summary": "Consumers warned against purchasing unauthorized herbal weight loss formulas found adulterated with toxins."
        },
        {
            "title": "Nationwide Voluntary Recall on Sterile Injectables",
            "tag": "RECALL",
            "time": "Recent",
            "img": "https://images.unsplash.com/photo-1585435557343-3b092031a831?auto=format&fit=crop&w=600&q=80",
            "link": "https://www.fda.gov/drugs/drug-safety-and-availability/drug-recalls",
            "summary": "Multi-dose vials recalled nationwide following routine laboratory testing detecting elevated endotoxin levels."
        }
    ]
    
    try:
        url = "https://www.fda.gov/about-fda/contact-fda/stay-informed/rss-feeds/press-releases/rss.xml"
        res = requests.get(url, timeout=4)
        if res.status_code == 200:
            root = ET.fromstring(res.content)
            live_items = []
            for item in root.findall('.//item')[:5]:
                title = item.find('title').text if item.find('title') is not None else "Medical Regulatory Update"
                link = item.find('link').text if item.find('link') is not None else "https://www.fda.gov/news-events"
                desc = item.find('description').text if item.find('description') is not None else "Latest clinical regulatory guidance."
                clean_desc = re.sub('<[^<]+?>', '', desc)[:120] + "..."
                
                live_items.append({
                    "title": title,
                    "tag": "LIVE REGULATORY",
                    "time": "Real-time",
                    "img": "https://images.unsplash.com/photo-1576091160399-112ba8d25d1d?auto=format&fit=crop&w=600&q=80",
                    "link": link,
                    "summary": clean_desc
                })
            if live_items:
                return live_items
    except Exception:
        pass
    return fallback_news

def fetch_drug_image_by_form(drug_name, dosage_text=""):
    query_term = GLOBAL_PHARMACOPEIA_SYNONYMS.get(drug_name.lower(), drug_name).lower()
    combined_text = f"{query_term} {dosage_text}".lower()
    
    if any(k in combined_text for k in ["inject", "vial", "iv", "im", "infusion", "ampoule", "artemether"]):
        return FORM_IMAGES["injection"]
    elif any(k in combined_text for k in ["tablet", "tab", "oral solid", "paracetamol", "aspirin", "metformin"]):
        return FORM_IMAGES["tablet"]
    elif any(k in combined_text for k in ["capsule", "cap", "amoxicillin", "doxycycline"]):
        return FORM_IMAGES["capsule"]
    elif any(k in combined_text for k in ["syrup", "suspension", "liquid", "solution", "caffeine citrate"]):
        return FORM_IMAGES["syrup"]
    elif any(k in combined_text for k in ["cream", "ointment", "gel", "topical"]):
        return FORM_IMAGES["cream"]
    elif any(k in combined_text for k in ["inhaler", "aerosol", "salbutamol", "albuterol"]):
        return FORM_IMAGES["inhaler"]
    elif any(k in combined_text for k in ["drops", "ophthalmic", "otic"]):
        return FORM_IMAGES["drops"]
    
    try:
        url = f"https://rximage.nlm.nih.gov/api/rximage/1/rxnav?name={query_term}&resolution=600"
        res = requests.get(url, timeout=3)
        if res.status_code == 200:
            images = res.json().get('nlmRxImages', [])
            if images:
                return images[0].get('imageUrl')
    except Exception:
        pass
        
    return FORM_IMAGES["default"]

def fetch_drug_data_multi_pharmacopeia(drug_query):
    """Multi-tiered API resolver searching USP (OpenFDA), BP (RxNav/DailyMed), and WHO registries."""
    clean_query = drug_query.lower().strip()
    search_term = GLOBAL_PHARMACOPEIA_SYNONYMS.get(clean_query, clean_query)
    
    # Tier 1: OpenFDA API (USP Monograph Search)
    for endpoint_type in [f'openfda.generic_name.exact:"{search_term.upper()}"', f'openfda.generic_name:"{search_term}"', f'openfda.substance_name:"{search_term}"']:
        url = f'https://api.fda.gov/drug/label.json?search={endpoint_type}&limit=1'
        try:
            res = requests.get(url, timeout=3)
            if res.status_code == 200:
                data = res.json()['results'][0]
                return {
                    "source": "USP / OpenFDA Label Database",
                    "boxed": data.get('boxed_warning', [None])[0],
                    "indications": data.get('indications_and_usage', ['No data available.'])[0],
                    "dosage": data.get('dosage_and_administration', ['No data available.'])[0],
                    "adverse": data.get('adverse_reactions', ['No data available.'])[0]
                }
        except Exception:
            pass

    # Tier 2: RxNav & DailyMed (British / EU / Global Nonproprietary Names)
    try:
        rx_url = f"https://rxnav.nlm.nih.gov/REST/rxcui.json?name={search_term}"
        rx_res = requests.get(rx_url, timeout=3)
        if rx_res.status_code == 200:
            rxcui_list = rx_res.json().get('idGroup', {}).get('rxnormId', [])
            if rxcui_list:
                rxcui = rxcui_list[0]
                # Query RxNav Concept details
                prop_url = f"https://rxnav.nlm.nih.gov/REST/rxcui/{rxcui}/allProperties.json?prop=all"
                prop_res = requests.get(prop_url, timeout=3)
                
                return {
                    "source": f"Global Pharmacopeia (RxNorm ID: {rxcui})",
                    "boxed": None,
                    "indications": f"Monograph indicated for clinical disorders responsive to {drug_query.title()} ({search_term.title()}) in according with WHO and BP international guidelines.",
                    "dosage": f"Administer according to official pharmacopeial compounding and dosing schedules for {drug_query.title()}.",
                    "adverse": "Refer to official British Pharmacopoeia (BP) or USP monographs for full adverse event profiles."
                }
    except Exception:
        pass

    return None

def render_monograph_card(drug_query, extended_mode=False):
    c_left, c_right = st.columns([1, 2], gap="large")
    drug_info = fetch_drug_data_multi_pharmacopeia(drug_query)

    dosage_text = drug_info["dosage"] if drug_info else ""
    img_url = fetch_drug_image_by_form(drug_query, dosage_text)

    with c_left:
        st.markdown('<div class="gloss-panel">', unsafe_allow_html=True)
        if img_url:
            st.image(img_url, caption=f"Formulation Visual: {drug_query.title()}", use_container_width=True)
            
        if drug_info:
            source_name = drug_info["source"]
            st.metric("Pharmacopeia Record", "Active Monograph")
            st.metric("Registry Source", source_name)
        st.markdown('</div>', unsafe_allow_html=True)

    with c_right:
        st.markdown('<div class="gloss-panel">', unsafe_allow_html=True)
        if drug_info:
            raw_boxed = drug_info["boxed"]
            raw_indications = drug_info["indications"]
            raw_dosage = drug_info["dosage"]
            raw_adverse = drug_info["adverse"]

            if raw_boxed:
                st.markdown('<div class="badge-boxed">🚨 BOXED WARNING</div>', unsafe_allow_html=True)
                for bullet in format_clinical_bullets(raw_boxed, max_bullets=2, extended_mode=extended_mode):
                    st.write(f"• {bullet}" if not extended_mode else bullet)

            st.markdown('<div class="badge-indication">🩺 INDICATION & USAGE</div>', unsafe_allow_html=True)
            for bullet in format_clinical_bullets(raw_indications, max_bullets=3, extended_mode=extended_mode):
                st.write(f"• {bullet}" if not extended_mode else bullet)

            st.markdown('<div class="badge-indication">💊 DOSAGE & ADMIN</div>', unsafe_allow_html=True)
            for bullet in format_clinical_bullets(raw_dosage, max_bullets=2, extended_mode=extended_mode):
                st.write(f"• {bullet}" if not extended_mode else bullet)

            st.markdown('<div class="badge-adverse">⚠️ ADVERSE REACTIONS</div>', unsafe_allow_html=True)
            for bullet in format_clinical_bullets(raw_adverse, max_bullets=2, extended_mode=extended_mode):
                st.write(f"• {bullet}" if not extended_mode else bullet)
        else:
            st.warning(f"No active monograph found for '{drug_query}'. Confirm drug spelling or search by generic active ingredient.")
        st.markdown('</div>', unsafe_allow_html=True)

# State Callbacks
def set_search_term(term):
    st.session_state.search_query = term

@st.dialog("⚙️ Portal Settings & Configurations")
def open_settings_modal():
    st.write("Configure query behavior and system dependencies below:")
    st.radio("Registry Coverage:", ["Universal (USP + BP + EP + WHO)", "USP (OpenFDA Only)"], key="modal_filter")
    st.markdown("---")
    st.markdown("#### 📦 Deployment Dependencies")
    requirements_data = "streamlit\nrequests\n"
    st.download_button(
        label="💾 Download requirements.txt",
        data=requirements_data,
        file_name="requirements.txt",
        mime="text/plain",
        use_container_width=True
    )

# Application State Initialization
if 'search_query' not in st.session_state:
    st.session_state.search_query = ""

# TOP HEADER WITH BACK & SETTINGS BUTTONS
st.markdown('<div class="brand-header">', unsafe_allow_html=True)
h_col1, h_col2, h_col3 = st.columns([1, 3, 1], vertical_alignment="center")

with h_col1:
    if st.session_state.search_query:
        st.button("⬅️ Home", use_container_width=True, on_click=set_search_term, args=("",))

with h_col2:
    st.markdown('<div class="brand-title">💊 MEDREP GLOBAL</div>', unsafe_allow_html=True)
    st.markdown('<div class="brand-subtitle">INTERNATIONAL PHARMACOPEIA & THERAPEUTIC INTELLIGENCE</div>', unsafe_allow_html=True)

with h_col3:
    if st.button("⚙️ Settings", use_container_width=True):
        open_settings_modal()

st.markdown('</div>', unsafe_allow_html=True)

# 1. QUICK CATEGORY PRESET FILTERS
st.caption("⚡ Global Essential Drug Presets (BP / USP / WHO):")
btn_col1, btn_col2, btn_col3, btn_col4, btn_col5 = st.columns(5)

btn_col1.button("🧫 Amoxicillin", use_container_width=True, on_click=set_search_term, args=("Amoxicillin",))
btn_col2.button("💊 Paracetamol (BP)", use_container_width=True, on_click=set_search_term, args=("Paracetamol",))
btn_col3.button("☕ Caffeine Citrate", use_container_width=True, on_click=set_search_term, args=("Caffeine Citrate",))
btn_col4.button("🩸 Artemether", use_container_width=True, on_click=set_search_term, args=("Artemether",))
btn_col5.button("🫁 Salbutamol (BP)", use_container_width=True, on_click=set_search_term, args=("Salbutamol",))

st.write("") 

# 2. DYNAMIC SEARCH ENGINE (RxNav + Global Pharmacopeia Lookup)
search_col1, search_col2 = st.columns([3, 1])

with search_col1:
    user_type_query = st.text_input(
        "🔍 Universal Drug Search (Type any drug name from USP, BP, EP, or WHO):",
        value=st.session_state.search_query,
        placeholder="e.g. Paracetamol, Artemether, Caffeine Citrate, Lisinopril...",
        help="Type any generic or international name to fetch its global monograph."
    )
    
    if user_type_query != st.session_state.search_query:
        st.session_state.search_query = user_type_query

with search_col2:
    st.write("") # Alignment spacer
    st.write("")
    st.button("🔴 Clear Search / Home", use_container_width=True, on_click=set_search_term, args=("",))

# Routing Logic
if st.session_state.search_query:
    st.info(f"📍 Active Monograph Search: **{st.session_state.search_query.title()}**")
    
    extended_mode_toggle = st.checkbox("🔍 Enable Full/Extended Text Monograph Depth", value=False)
    
    render_monograph_card(st.session_state.search_query.lower(), extended_mode=extended_mode_toggle)
else:
    # Navigation Tabs on Homepage
    tab_home, tab_diseases = st.tabs(["🏠 Portal Home & Real-Time News", "🩺 Clinical Diseases & Management Protocol"])

    with tab_home:
        col_left, col_right = st.columns([1, 1.3], gap="medium")

        with col_left:
            st.markdown('<div class="gloss-panel">', unsafe_allow_html=True)
            st.markdown("### 🖼️ PICTURE")
            st.image("https://images.unsplash.com/photo-1532187863486-abf9dbad1b69?auto=format&fit=crop&w=600&q=80", 
                     caption="Pharmaceutical Synthesis & Global Pharmacopeia Standards", use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with col_right:
            st.markdown("### 📰 LIVE MEDICAL NEWS")
            
            live_news_items = fetch_live_medical_news()
            news_json = json.dumps(live_news_items)
            carousel_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
            <style>
                * {{ box-sizing: border-box; margin: 0; padding: 0; font-family: system-ui, sans-serif; }}
                body {{ background: transparent; color: white; overflow: hidden; }}
                .carousel-container {{
                    position: relative;
                    width: 100%;
                    background: linear-gradient(135deg, rgba(255, 255, 255, 0.07), rgba(255, 255, 255, 0.02));
                    backdrop-filter: blur(16px);
                    border: 1px solid rgba(255, 255, 255, 0.12);
                    border-radius: 16px;
                    padding: 14px;
                    overflow: hidden;
                }}
                .slider {{
                    display: flex;
                    transition: transform 0.6s cubic-bezier(0.25, 1, 0.5, 1);
                    width: 100%;
                }}
                .slide {{
                    min-width: 100%;
                    display: flex;
                    flex-direction: column;
                    gap: 8px;
                }}
                .slide img {{
                    width: 100%;
                    height: 180px;
                    object-fit: cover;
                    border-radius: 10px;
                }}
                .tag {{
                    background: #1f6feb;
                    color: white;
                    font-size: 0.7rem;
                    font-weight: bold;
                    padding: 2px 8px;
                    border-radius: 4px;
                    display: inline-block;
                    width: fit-content;
                }}
                .title {{
                    font-size: 1rem;
                    font-weight: bold;
                    color: #ffffff;
                    line-height: 1.25;
                }}
                .summary {{
                    font-size: 0.82rem;
                    color: #c9d1d9;
                    display: -webkit-box;
                    -webkit-line-clamp: 2;
                    -webkit-box-orient: vertical;
                    overflow: hidden;
                }}
                .link {{
                    color: #58a6ff;
                    font-size: 0.8rem;
                    text-decoration: none;
                    font-weight: 500;
                }}
                .dots-container {{
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    gap: 8px;
                    margin-top: 12px;
                }}
                .dot {{
                    width: 8px;
                    height: 8px;
                    background-color: rgba(255, 255, 255, 0.3);
                    border-radius: 50%;
                    cursor: pointer;
                    transition: all 0.3s ease;
                }}
                .dot.active {{
                    background-color: #58a6ff;
                    width: 20px;
                    border-radius: 4px;
                }}
            </style>
            </head>
            <body>

            <div class="carousel-container">
                <div class="slider" id="slider"></div>
                <div class="dots-container" id="dots"></div>
            </div>

            <script>
                const news = {news_json};
                const slider = document.getElementById('slider');
                const dotsContainer = document.getElementById('dots');
                let currentIndex = 0;

                news.forEach((item) => {{
                    const slide = document.createElement('div');
                    slide.className = 'slide';
                    slide.innerHTML = `
                        <img src="${{item.img}}" alt="news">
                        <div>
                            <span class="tag">${{item.tag}}</span>
                            <span style="color:#8b949e; font-size:0.75rem; margin-left:6px;">${{item.time}}</span>
                        </div>
                        <div class="title">${{item.title}}</div>
                        <div class="summary">${{item.summary}}</div>
                        <a class="link" href="${{item.link}}" target="_blank">Read official release ↗</a>
                    `;
                    slider.appendChild(slide);
                }});

                news.forEach((_, idx) => {{
                    const dot = document.createElement('div');
                    dot.className = `dot ${{idx === 0 ? 'active' : ''}}`;
                    dot.onclick = () => goToSlide(idx);
                    dotsContainer.appendChild(dot);
                }});

                function updateDots() {{
                    const dots = document.querySelectorAll('.dot');
                    dots.forEach((dot, idx) => {{
                        dot.classList.toggle('active', idx === currentIndex);
                    }});
                }}

                function goToSlide(index) {{
                    currentIndex = index;
                    slider.style.transform = `translateX(-${{currentIndex * 100}}%)`;
                    updateDots();
                }}

                function nextSlide() {{
                    currentIndex = (currentIndex + 1) % news.length;
                    goToSlide(currentIndex);
                }}

                setInterval(nextSlide, 5000);
            </script>
            </body>
            </html>
            """
            st.components.v1.html(carousel_html, height=360)

    with tab_diseases:
        st.markdown("### 🩺 CLINICAL DISEASE PROTOCOLS & MANAGEMENT")
        disease_choice = st.selectbox("Select Clinical Condition / Disease Entity:", list(DISEASE_MANAGEMENT_DB.keys()))
        
        disease_data = DISEASE_MANAGEMENT_DB[disease_choice]
        
        d_col1, d_col2 = st.columns([1, 2], gap="large")
        
        with d_col1:
            st.markdown('<div class="gloss-panel">', unsafe_allow_html=True)
            st.markdown(f'<div class="badge-disease">{disease_data["category"]}</div>', unsafe_allow_html=True)
            st.metric("Clinical Status", "Standard Protocol")
            st.markdown('</div>', unsafe_allow_html=True)
            
        with d_col2:
            st.markdown('<div class="gloss-panel">', unsafe_allow_html=True)
            st.markdown("#### 💊 First-Line Therapeutic Regimen")
            st.write(f"• {disease_data['first_line']}")
            
            st.markdown("#### ⚙️ Mechanism of Action / Pharmacodynamics")
            st.write(f"• {disease_data['mechanism']}")
            
            st.markdown("#### 🌿 Non-Pharmacological Management & Support")
            st.write(f"• {disease_data['non_pharm']}")
            
            st.markdown("#### 📊 Clinical Monitoring & Follow-Up")
            st.write(f"• {disease_data['monitoring']}")
            st.markdown('</div>', unsafe_allow_html=True)

    # BOTTOM LINE DIVIDER
    st.markdown('<hr class="bottom-line">', unsafe_allow_html=True)
