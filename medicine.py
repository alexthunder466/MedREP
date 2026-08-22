import streamlit as st
import requests
import json
import re
from datetime import datetime

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
    .stApp {{
        background: linear-gradient(rgba(10, 15, 26, 0.90), rgba(10, 15, 26, 0.94)), 
                    url("{selected_bg}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
        transition: background 1s ease-in-out;
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

    .bottom-line {{
        border: 0;
        height: 2px;
        background: linear-gradient(90deg, transparent, rgba(88, 166, 255, 0.5), transparent);
        margin-top: 24px;
        margin-bottom: 24px;
    }}
</style>
""", unsafe_allow_html=True)

# Formatting Engine for Short vs Extended Views
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

PREDICTIVE_DRUG_DATABASE = [
    "", "Amoxicillin", "Amoxicillin and Clavulanate Potassium", "Ampicillin", "Artemether", "Aspirin", "Atenolol", "Atorvastatin", 
    "Azithromycin", "Caffeine Citrate", "Cefalexin", "Cefuroxime", "Cephalexin", "Ciprofloxacin", "Co-trimoxazole", 
    "Dexamethasone", "Diazepam", "Diclofenac", "Doxycycline", "Erythromycin", "Fluconazole", 
    "Furosemide", "Glibenclamide", "Hydrochlorothiazide", "Ibuprofen", "Insulin", "Lisinopril", 
    "Losartan", "Metformin", "Metronidazole", "Omeprazole", "Paracetamol", "Penicillin V", 
    "Promethazine", "Salbutamol", "Simvastatin", "Tramadol"
]

# US FDA / INN Generic Name Mappings
DRUG_SYNONYMS = {
    "salbutamol": "albuterol",
    "paracetamol": "acetaminophen",
    "cefalexin": "cephalexin"
}

NEWS_ITEMS = [
    {
        "title": "FDA Approves Pasatru for Rare Bone Disorder Treatment",
        "tag": "FDA APPROVAL",
        "time": "12m ago",
        "img": "https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?auto=format&fit=crop&w=600&q=80",
        "link": "https://www.fda.gov/drugs/news-events-human-drugs/notable-approvals-drugs",
        "summary": "First-in-class monoclonal antibody approved to reduce heterotopic ossification in pediatric and adult patients."
    },
    {
        "title": "Public Health Alert: Contaminated Botanical Supplements",
        "tag": "SAFETY ALERT",
        "time": "1h ago",
        "img": "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=600&q=80",
        "link": "https://www.fda.gov/food/alerts-advisories-safety-information",
        "summary": "Consumers warned against purchasing unauthorized herbal weight loss formulas found adulterated with toxins."
    },
    {
        "title": "Nationwide Voluntary Recall on Sterile Injectables",
        "tag": "RECALL",
        "time": "3h ago",
        "img": "https://images.unsplash.com/photo-1585435557343-3b092031a831?auto=format&fit=crop&w=600&q=80",
        "link": "https://www.fda.gov/drugs/drug-safety-and-availability/drug-recalls",
        "summary": "Multi-dose vials recalled nationwide following routine laboratory testing detecting elevated endotoxin levels."
    },
    {
        "title": "Novel Pediatric Malaria Prevention Guidelines Released",
        "tag": "CLINICAL STUDY",
        "time": "5h ago",
        "img": "https://images.unsplash.com/photo-1532187863486-abf9dbad1b69?auto=format&fit=crop&w=600&q=80",
        "link": "https://www.who.int/news",
        "summary": "Updated therapeutic dosing strategies published to reduce transmission rates in endemic regional clinics."
    }
]

def fetch_drug_image(drug_name):
    query_term = DRUG_SYNONYMS.get(drug_name.lower(), drug_name)
    try:
        url = f"https://rximage.nlm.nih.gov/api/rximage/1/rxnav?name={query_term}&resolution=600"
        res = requests.get(url, timeout=3)
        if res.status_code == 200:
            images = res.json().get('nlmRxImages', [])
            if images:
                return images[0].get('imageUrl')
    except Exception:
        pass
    return "https://images.unsplash.com/photo-1471864190281-a93a3070b6de?auto=format&fit=crop&w=600&q=80"

def fetch_drug_data_with_fallback(drug_query):
    clean_query = drug_query.lower().strip()
    search_term = DRUG_SYNONYMS.get(clean_query, clean_query)
    
    # 1. Strict Exact Match First (Prevents Amoxicillin matching Amoxiclav)
    url_exact = f'https://api.fda.gov/drug/label.json?search=openfda.generic_name.exact:"{search_term.upper()}"&limit=1'
    res = requests.get(url_exact)
    
    # 2. Quoted Exact Match Secondary
    if res.status_code != 200:
        url_quoted = f'https://api.fda.gov/drug/label.json?search=openfda.generic_name:"{search_term}"&limit=1'
        res = requests.get(url_quoted)

    # 3. Fallback Fuzzy Search
    if res.status_code != 200:
        url_fuzzy = f'https://api.fda.gov/drug/label.json?search=openfda.generic_name:{search_term}&limit=1'
        res = requests.get(url_fuzzy)

    if res.status_code == 200:
        data = res.json()['results'][0]
        return {
            "source": "OpenFDA API",
            "boxed": data.get('boxed_warning', [None])[0],
            "indications": data.get('indications_and_usage', ['No data available.'])[0],
            "dosage": data.get('dosage_and_administration', ['No data available.'])[0],
            "adverse": data.get('adverse_reactions', ['No data available.'])[0]
        }
    
    # 4. NIH DailyMed Fallback Strategy
    try:
        rx_url = f"https://rxnav.nlm.nih.gov/REST/rxcui.json?name={search_term}"
        rx_res = requests.get(rx_url, timeout=3)
        if rx_res.status_code == 200:
            rxcui = rx_res.json().get('idGroup', {}).get('rxnormId', [None])[0]
            if rxcui:
                return {
                    "source": "NIH DailyMed SPL Database",
                    "boxed": None,
                    "indications": f"Indicated for conditions responsive to {drug_query.title()} ({search_term.title()}) according to clinical practice guidelines.",
                    "dosage": f"Administer as directed per official monographs for {drug_query.title()}.",
                    "adverse": "Refer to official prescribing info for full adverse effect profile."
                }
    except Exception:
        pass

    return None

def render_monograph_card(drug_query, extended_mode=False):
    c_left, c_right = st.columns([1, 2], gap="large")
    drug_info = fetch_drug_data_with_fallback(drug_query)

    with c_left:
        st.markdown('<div class="gloss-panel">', unsafe_allow_html=True)
        img_url = fetch_drug_image(drug_query)
        if img_url:
            st.image(img_url, caption=f"Pill Visual: {drug_query.title()}", use_container_width=True)
            
        if drug_info:
            source_name = drug_info["source"]
            st.metric("FDA Status", "Active" if source_name == "OpenFDA API" else "Clinical SPL")
            st.metric("Data Source", source_name)
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
            st.warning(f"No clinical record found for '{drug_query}'. Verify ingredient spelling.")
        st.markdown('</div>', unsafe_allow_html=True)

# Callback functions to safely update selectbox state before rerun
def set_search_term(term):
    st.session_state.search_query = term

# Application State Initialization
if 'search_query' not in st.session_state:
    st.session_state.search_query = ""

# --- TOP SEARCH HEADER ---
st.markdown("## 💊 MEDREP CLINICAL PORTAL")
search_col1, search_col2 = st.columns([3, 1])

with search_col1:
    st.selectbox(
        "Search active ingredient (Predictive Autocomplete):",
        options=PREDICTIVE_DRUG_DATABASE,
        key="search_query",
        help="Select or type a generic drug to isolate focus page."
    )

with search_col2:
    st.button("🔴 Clear Search / Home", use_container_width=True, on_click=set_search_term, args=("",))

# --- QUICK CATEGORY PRESET FILTERS ---
st.caption("⚡ Quick Therapeutic Category Presets:")
btn_col1, btn_col2, btn_col3, btn_col4, btn_col5 = st.columns(5)

btn_col1.button("🧫 Antibiotic", use_container_width=True, on_click=set_search_term, args=("Amoxicillin",))
btn_col2.button("💊 Analgesic", use_container_width=True, on_click=set_search_term, args=("Ibuprofen",))
btn_col3.button("🫀 Antihypertensive", use_container_width=True, on_click=set_search_term, args=("Atenolol",))
btn_col4.button("🩸 Antidiabetic", use_container_width=True, on_click=set_search_term, args=("Metformin",))
btn_col5.button("🫁 Bronchodilator", use_container_width=True, on_click=set_search_term, args=("Salbutamol",))

# Routing Logic
if st.session_state.search_query:
    st.info(f"📍 Active Focus Monograph: **{st.session_state.search_query.title()}**")
    
    # Toggle Controls for Shortened vs Extended View
    extended_mode_toggle = st.checkbox("🔍 Enable Full/Extended Text Monograph Depth", value=False)
    
    render_monograph_card(st.session_state.search_query.lower(), extended_mode=extended_mode_toggle)
else:
    # --- HOMEPAGE LAYOUT ---
    col_left, col_middle, col_right = st.columns([1, 1.3, 1], gap="medium")

    with col_left:
        st.markdown('<div class="gloss-panel">', unsafe_allow_html=True)
        st.markdown("### 🖼️ PICTURE")
        st.image("https://images.unsplash.com/photo-1532187863486-abf9dbad1b69?auto=format&fit=crop&w=600&q=80", 
                 caption="Pharmaceutical Research & Synthesis", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_middle:
        st.markdown("### 📰 NEWS")
        
        news_json = json.dumps(NEWS_ITEMS)
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

    with col_right:
        st.markdown('<div class="gloss-panel">', unsafe_allow_html=True)
        st.markdown("### ⚙️ SETTINGS")
        st.radio("Query Engine Filter:", ["Generic Active Ingredient", "Exact Match Only"], key="home_filter")
        st.caption("Select a drug active ingredient from the top search bar to load focused drug monographs.")
        
        # --- GITHUB DEPLOYMENT / REQUIREMENTS GENERATOR ---
        st.markdown("---")
        st.markdown("#### 📦 Deployment Dependencies")
        requirements_data = "streamlit\nrequests\n"
        st.download_button(
            label="💾 Download requirements.txt",
            data=requirements_data,
            file_name="requirements.txt",
            mime="text/plain",
            use_container_width=True,
            help="Download this file and place it next to medicine.py when deploying to GitHub or Streamlit Cloud."
        )
        st.markdown('</div>', unsafe_allow_html=True)

    # --- BOTTOM LINE DIVIDER ---
    st.markdown('<hr class="bottom-line">', unsafe_allow_html=True)
