import os
import re
import unicodedata
import time
import requests
import concurrent.futures
import streamlit as st
import pandas as pd
from deep_translator import GoogleTranslator
from textblob import TextBlob

os.system("python -m textblob.download_corpora quiet 2>/dev/null")

# ─────────────────────────────────────────────
#  Página
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="MedSearch Architect — Universidade de Vassouras",
    page_icon="assets/logo.png" if os.path.exists("assets/logo.png") else None,
    layout="wide",
)

# ─────────────────────────────────────────────
#  CSS — estética "Digital Library"
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=Georgia&display=swap');

/* ── BASE ── */
html, body, [class*="css"] {
    font-family: 'Inter', 'Segoe UI', sans-serif;
    font-size: 15px;
    color: #000000;
    line-height: 1.6;
}
.stApp { background: #F8FAFC; }

/* ── SIDEBAR — texto branco puro em todos os elementos ── */
[data-testid="stSidebar"] { background: #0A1628 !important; }
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] div,
[data-testid="stSidebar"] li,
[data-testid="stSidebar"] a { color: #FFFFFF !important; }

.sb-institution {
    padding: 1.6rem 1rem 1.2rem;
    border-bottom: 1px solid #2a4a6a;
    margin-bottom: 1.4rem;
}
.sb-inst-name {
    font-family: Georgia, 'Times New Roman', serif;
    font-size: 1rem;
    font-weight: 700;
    color: #FFFFFF !important;
    line-height: 1.4;
    letter-spacing: 0.2px;
}
.sb-inst-sub {
    font-size: 0.75rem;
    color: #E2E8F0 !important;
    letter-spacing: 0.3px;
    margin-top: 0.35rem;
    line-height: 1.6;
}
.sb-section-label {
    font-size: 0.65rem;
    letter-spacing: 1.8px;
    text-transform: uppercase;
    color: #E2E8F0 !important;
    font-weight: 600;
    margin: 1.4rem 0 0.6rem;
    display: block;
}
.sb-body {
    font-size: 0.84rem;
    color: #FFFFFF !important;
    line-height: 1.7;
}
.sb-divider {
    border: none;
    border-top: 1px solid #2a4a6a;
    margin: 1.2rem 0;
}
.sb-pipeline-item {
    font-size: 0.82rem;
    color: #FFFFFF !important;
    padding: 0.3rem 0;
    display: flex;
    align-items: baseline;
    gap: 0.6rem;
    line-height: 1.6;
}
.sb-pipeline-num {
    font-size: 0.65rem;
    font-weight: 700;
    color: #E2E8F0 !important;
    min-width: 20px;
}
.sb-credit-block {
    margin-top: 1.4rem;
    padding: 0.9rem 1rem;
    border-top: 1px solid #2a4a6a;
}
.sb-credit-name {
    font-size: 0.84rem;
    font-weight: 700;
    color: #FFFFFF !important;
    margin-bottom: 0.2rem;
}
.sb-credit-role {
    font-size: 0.75rem;
    color: #E2E8F0 !important;
    line-height: 1.6;
}

/* ── HEADER PRINCIPAL ── */
.page-header {
    padding: 2rem 0 1.5rem;
    border-bottom: 1px solid #E2E8F0;
    margin-bottom: 1.8rem;
}
.page-header-eyebrow {
    font-size: 0.7rem;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: #475569;
    font-weight: 600;
    margin-bottom: 0.5rem;
}
.page-header-title {
    font-family: Georgia, 'Times New Roman', serif;
    font-size: 1.85rem;
    font-weight: 700;
    color: #0A1628;
    letter-spacing: -0.3px;
    line-height: 1.2;
    margin-bottom: 0.4rem;
}
.page-header-sub {
    font-size: 0.9rem;
    color: #475569;
    font-weight: 400;
    line-height: 1.6;
}

/* ── CARDS — sombra leve, sem borda pesada ── */
.card {
    background: #FFFFFF;
    border: none;
    border-radius: 6px;
    padding: 1.5rem 1.6rem;
    margin-bottom: 1rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.10), 0 1px 2px rgba(0,0,0,0.06);
}
.card-title {
    font-family: Georgia, 'Times New Roman', serif;
    font-size: 1rem;
    font-weight: 600;
    color: #0A1628;
    margin-bottom: 0.25rem;
    letter-spacing: 0.1px;
}
.card-sub {
    font-size: 0.84rem;
    color: #475569;
    margin-bottom: 1rem;
    line-height: 1.6;
}

/* ── INPUT — fundo branco, texto preto absoluto ── */
.stTextArea textarea {
    font-family: 'Inter', 'Segoe UI', sans-serif !important;
    font-size: 16px !important;
    color: #000000 !important;
    background: #FFFFFF !important;
    border: 1px solid #CBD5E0 !important;
    border-radius: 4px !important;
    line-height: 1.6 !important;
    resize: none !important;
    padding: 0.75rem 0.9rem !important;
}
.stTextArea textarea:focus {
    border-color: #0A1628 !important;
    box-shadow: 0 0 0 2px rgba(10,22,40,0.10) !important;
}
.stTextArea textarea::placeholder {
    color: #94a3b8 !important;
    font-style: italic !important;
}

/* ── BOTOES ── */
.stButton > button {
    background: #0A1628 !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 4px !important;
    padding: 0.6rem 1.6rem !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.88rem !important;
    letter-spacing: 0.3px !important;
    width: 100% !important;
    transition: background 0.15s !important;
    box-shadow: none !important;
}
.stButton > button:hover { background: #162540 !important; }

/* ── CAIXAS DE TRADUÇÃO — fundo branco, texto preto absoluto ── */
.trans-section { margin-bottom: 0.25rem; }
.trans-label {
    display: block !important;
    font-size: 0.68rem !important;
    font-weight: 700 !important;
    letter-spacing: 1.4px !important;
    text-transform: uppercase !important;
    color: #475569 !important;
    margin-bottom: 0.35rem !important;
}
.trans-box {
    border-radius: 4px !important;
    padding: 0.85rem 1rem !important;
    font-size: 0.92rem !important;
    font-weight: 400 !important;
    line-height: 1.65 !important;
    color: #000000 !important;
    border: 1px solid #CBD5E0 !important;
    background: #FFFFFF !important;
}
.trans-box-pt { background: #FFFFFF !important; }
.trans-box-en { background: #FFFFFF !important; border-left: 3px solid #0A1628 !important; }

/* ── CURADORIA — lista vertical ── */
.curation-term {
    font-family: 'Source Code Pro', 'Courier New', monospace;
    font-size: 0.9rem;
    font-weight: 600;
    color: #000000;
    flex: 1;
}
/* Status MeSH: texto em negrito, sem fundo colorido */
.curation-status {
    font-size: 0.75rem;
    font-weight: 500;
    letter-spacing: 0.2px;
    color: #475569;
    white-space: nowrap;
    align-self: center;
}
.curation-status-mesh {
    font-weight: 700;
    color: #166534; /* verde escuro — contraste WCAG AA garantido sobre branco */
}

/* ── RESULTADO ── */
.result-card {
    background: #FFFFFF;
    border: none;
    border-radius: 6px;
    padding: 1.5rem 1.6rem;
    margin-bottom: 1rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.10), 0 1px 2px rgba(0,0,0,0.06);
}
.explain-card {
    background: #FFFFFF;
    border: none;
    border-left: 3px solid #0A1628;
    border-radius: 6px;
    padding: 1.5rem 1.6rem;
    margin-bottom: 1rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.10), 0 1px 2px rgba(0,0,0,0.06);
}

/* ── AVISO ── */
.notice-box {
    background: #FFFFFF;
    border: 1px solid #CBD5E0;
    border-left: 3px solid #475569;
    border-radius: 4px;
    padding: 0.75rem 1rem;
    font-size: 0.85rem;
    color: #000000;
    line-height: 1.6;
    margin-top: 0.8rem;
}
.notice-box a { color: #2563EB; font-weight: 600; }

/* ── PIPELINE (estado inicial) ── */
.pipeline-flow {
    display: flex;
    align-items: stretch;
    flex-wrap: wrap;
    gap: 0;
    margin-top: 1.2rem;
}
.pipeline-step {
    background: #F8FAFC;
    border: 1px solid #E2E8F0;
    border-radius: 4px;
    padding: 0.75rem 0.9rem;
    flex: 1;
    min-width: 100px;
    box-shadow: 0 1px 2px rgba(0,0,0,0.05);
}
.pipeline-step-num {
    font-size: 0.62rem;
    font-weight: 700;
    letter-spacing: 1.2px;
    color: #475569;
    text-transform: uppercase;
    margin-bottom: 0.2rem;
}
.pipeline-step-label {
    font-size: 0.82rem;
    font-weight: 600;
    color: #000000;
    line-height: 1.3;
}
.pipeline-step-desc {
    font-size: 0.72rem;
    color: #475569;
    margin-top: 0.15rem;
    line-height: 1.5;
}
.pipeline-arrow {
    color: #94a3b8;
    font-size: 1rem;
    padding: 0 0.3rem;
    flex-shrink: 0;
    align-self: center;
}

/* ── GLOSSÁRIO ── */
.gloss-item {
    padding: 0.8rem 0;
    border-bottom: 1px solid #E2E8F0;
}
.gloss-item:last-child { border-bottom: none; }
.gloss-term {
    font-family: 'Source Code Pro', 'Courier New', monospace;
    font-size: 0.88rem;
    font-weight: 700;
    color: #000000;
}
.gloss-def {
    font-size: 0.84rem;
    color: #475569;
    margin-top: 0.2rem;
    line-height: 1.6;
}

/* ── STEPS ── */
.step-row {
    display: flex;
    gap: 0.9rem;
    align-items: flex-start;
    padding: 0.75rem 0;
    border-bottom: 1px solid #E2E8F0;
}
.step-row:last-child { border-bottom: none; }
.step-n {
    font-size: 0.72rem;
    font-weight: 700;
    color: #FFFFFF;
    background: #0A1628;
    border-radius: 50%;
    min-width: 24px;
    height: 24px;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    margin-top: 0.15rem;
}
.step-body { font-size: 0.88rem; color: #000000; line-height: 1.65; }
.step-body strong { color: #0A1628; font-weight: 600; }
.step-body a { color: #2563EB; font-weight: 600; }

/* ── TABS ── */
.stTabs [data-baseweb="tab-list"] {
    background: transparent;
    border-bottom: 1px solid #E2E8F0;
    border-radius: 0;
    padding: 0;
    gap: 0;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 0 !important;
    font-weight: 500 !important;
    color: #475569 !important;
    padding: 0.6rem 1.3rem !important;
    font-size: 0.88rem !important;
    border-bottom: 2px solid transparent !important;
    background: transparent !important;
}
.stTabs [aria-selected="true"] {
    color: #000000 !important;
    border-bottom: 2px solid #0A1628 !important;
    font-weight: 600 !important;
    background: transparent !important;
    box-shadow: none !important;
}

/* ── CHECKBOX ── */
.stCheckbox label {
    font-size: 0.88rem !important;
    color: #000000 !important;
    font-weight: 400 !important;
    line-height: 1.6 !important;
}

/* ── DATAFRAME — largura total, cabeçalhos nítidos ── */
[data-testid="stDataFrame"] {
    border: 1px solid #E2E8F0;
    border-radius: 4px;
    width: 100% !important;
}
[data-testid="stDataFrame"] th {
    background: #F8FAFC !important;
    color: #000000 !important;
    font-weight: 600 !important;
    font-size: 0.84rem !important;
    border-bottom: 2px solid #CBD5E0 !important;
}
[data-testid="stDataFrame"] td {
    color: #000000 !important;
    font-size: 0.84rem !important;
    line-height: 1.6 !important;
}

/* ── OCULTAR chrome Streamlit ── */
[data-testid="stToolbar"] { display: none !important; }
#MainMenu { display: none !important; }
footer { display: none !important; }

/* ── STATUS BOXES (st.status) ────────────────────────────────────────────────
   Estrutura real (bundle JS src.BnXM6qiK.js, componente nE / Expandable):
     <div class="stExpander" data-testid="stExpander">
       <details class="eqw31fm1">
         <summary class="eqw31fm4">  ← summary NÃO define color; herda do tema
           <span class="eqw31fm2">
             <div class="eqw31fm3">…label…</div>
           </span>
         </summary>
         <div data-testid="stExpanderDetails" class="eqw31fm5">…</div>
       </details>
     </div>

   Problema: Emotion injeta CSS APÓS o <style> do app, mesmo com !important igual
   a ordem de aparecimento no DOM decide — Emotion ganha por vir depois.
   Solução definitiva: prefixo "html body" adiciona dois elementos à especificidade
   → [0,0,2] + resto, impossível de ser igualado por um seletor Emotion de classe única. ── */

html body [data-testid="stExpander"] summary {
    color: #0A1628 !important;
}
html body [data-testid="stExpander"] summary * {
    color: #0A1628 !important;
}
html body [data-testid="stExpander"] .eqw31fm4 {
    color: #0A1628 !important;
}
html body [data-testid="stExpander"] .eqw31fm4 * {
    color: #0A1628 !important;
}
html body [data-testid="stExpander"] .eqw31fm2,
html body [data-testid="stExpander"] .eqw31fm2 *,
html body [data-testid="stExpander"] .eqw31fm3,
html body [data-testid="stExpander"] .eqw31fm3 * {
    color: #0A1628 !important;
}
html body [data-testid="stExpanderDetails"],
html body [data-testid="stExpanderDetails"] * {
    color: #0A1628 !important;
}

/* ── WARNING BOX (st.warning) — texto escuro sobre fundo amarelo pastel ── */
[data-testid="stAlert"][kind="warning"],
div[data-testid="stAlert"] {
    background: #FEFCE8 !important;
    border: 1px solid #ca8a04 !important;
    border-radius: 6px !important;
}
[data-testid="stAlert"] p,
[data-testid="stAlert"] span,
[data-testid="stAlert"] div,
[data-testid="stAlert"] a,
[data-testid="stAlert"] li,
[data-testid="stAlert"] * {
    color: #713f12 !important;
}
[data-testid="stAlert"] a {
    color: #1d4ed8 !important;
    font-weight: 600 !important;
    text-decoration: underline !important;
}
/* Ícone do alerta */
[data-testid="stAlert"] svg {
    fill: #ca8a04 !important;
    color: #ca8a04 !important;
}
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════
#  LÓGICA — IDÊNTICA À VERSÃO ANTERIOR, SEM ALTERAÇÕES
# ══════════════════════════════════════════════════════

VERBS_TO_REMOVE = {
    "want","see","find","search","analyze","analyse","show","look","get",
    "make","use","know","check","review","investigate","explore","study",
    "examine","assess","evaluate","understand","determine","identify",
    "compare","describe","measure","calculate","need","try","help","provide",
}
ALLOWED_POS = {"NN","NNS","NNP","NNPS","JJ","VBN","VBG"}
STOPWORDS_RESIDUAL = {
    "a","an","the","of","in","on","at","to","for","with","by","from",
    "and","or","is","are","was","were","be","been","being","this","that",
    "these","those","it","its","among","between","during","after","before",
    "through","into","over","under","patients","patient","people","person",
    "individuals","population","group","sample","adults","children",
    "elderly","women","men","study","studies","article","articles",
    "paper","papers","research","data","result","results","method",
    "methods","analysis","assessment","evaluation","report","evidence",
    "impact","effect","effects","level","levels","rate","rates","type",
    "types","factor","factors","relationship","association","number",
    "case","cases","index","measure","measures","also","however",
    "therefore","thus","while","because","due","such","than","more",
    "less","new","old","different","various","several","many","large",
    "small","important","significant","common","current","recent",
    "previous","possible","general","main","major","potential",
    "non","anti","pre","post","per","vs","versus",
}
LOCALITY_TERMS = [
    "vassouras","resende","volta redonda","barra mansa","petropolis",
    "petrópolis","teresópolis","teresopolis","nova friburgo",
    "rio de janeiro","são paulo","sao paulo","brasil","brazil",
    "minas gerais","espirito santo","espírito santo","rio","rj","sp","mg","es",
]
PUBMED_ESEARCH = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"

# ─────────────────────────────────────────────
#  Dicionário coloquial PT → termo MeSH em inglês
# ─────────────────────────────────────────────
COLOQUIAL_DICT = {
    # Cardiovascular
    "pressao alta":             "Hypertension",
    "hipertensao":              "Hypertension",
    "pressao baixa":            "Hypotension",
    "hipotensao":               "Hypotension",
    "infarto":                  "Myocardial Infarction",
    "ataque cardiaco":          "Myocardial Infarction",
    "derrame":                  "Stroke",
    "avc":                      "Stroke",
    "acidente vascular cerebral": "Stroke",
    "insuficiencia cardiaca":   "Heart Failure",
    "arritmia":                 "Arrhythmias, Cardiac",
    "colesterol alto":          "Hypercholesterolemia",
    "triglicerides alto":       "Hypertriglyceridemia",
    "triglicerideos alto":      "Hypertriglyceridemia",
    "varizes":                  "Varicose Veins",
    # Metabólico / Endócrino
    "diabetes":                 "Diabetes Mellitus",
    "diabetes tipo 1":          "Diabetes Mellitus, Type 1",
    "diabetes tipo 2":          "Diabetes Mellitus, Type 2",
    "acucar alto":              "Hyperglycemia",
    "acucar no sangue":         "Blood Glucose",
    "gordura no figado":        "Fatty Liver",
    "esteatose hepatica":       "Fatty Liver",
    "tireoide":                 "Thyroid Diseases",
    "hipotireoidismo":          "Hypothyroidism",
    "hipertireoidismo":         "Hyperthyroidism",
    "obesidade":                "Obesity",
    "sobrepeso":                "Overweight",
    # Respiratório
    "asma":                     "Asthma",
    "bronquite":                "Bronchitis",
    "dpoc":                     "Pulmonary Disease, Chronic Obstructive",
    "enfisema":                 "Pulmonary Emphysema",
    "pneumonia":                "Pneumonia",
    "tuberculose":              "Tuberculosis",
    "apneia do sono":           "Sleep Apnea Syndromes",
    "ronco":                    "Snoring",
    # Digestivo
    "refluxo":                  "Gastroesophageal Reflux",
    "azia":                     "Heartburn",
    "ulcera":                   "Peptic Ulcer",
    "gastrite":                 "Gastritis",
    "intestino preso":          "Constipation",
    "prisao de ventre":         "Constipation",
    "constipacao":              "Constipation",
    "diarreia":                 "Diarrhea",
    "hemorroida":               "Hemorrhoids",
    # Neurológico / Mental
    "depressao":                "Depression",
    "ansiedade":                "Anxiety Disorders",
    "esquizofrenia":            "Schizophrenia",
    "alzheimer":                "Alzheimer Disease",
    "parkinson":                "Parkinson Disease",
    "epilepsia":                "Epilepsy",
    "convulsao":                "Seizures",
    "enxaqueca":                "Migraine Disorders",
    "cefaleia":                 "Headache",
    "insonia":                  "Sleep Initiation and Maintenance Disorders",
    "deficit de atencao":       "Attention Deficit Disorder with Hyperactivity",
    "tdah":                     "Attention Deficit Disorder with Hyperactivity",
    "autismo":                  "Autistic Disorder",
    "toc":                      "Obsessive-Compulsive Disorder",
    "burnout":                  "Burnout, Professional",
    # Músculo-esquelético
    "artrite":                  "Arthritis",
    "artrose":                  "Osteoarthritis",
    "reumatismo":               "Rheumatic Diseases",
    "lupus":                    "Lupus Erythematosus, Systemic",
    "osteoporose":              "Osteoporosis",
    "dor nas costas":           "Back Pain",
    "lombalgia":                "Low Back Pain",
    "fibromialgia":             "Fibromyalgia",
    "tendinite":                "Tendinopathy",
    # Renal / Urológico
    "pedra nos rins":           "Kidney Calculi",
    "calculo renal":            "Kidney Calculi",
    "insuficiencia renal":      "Renal Insufficiency",
    "infeccao urinaria":        "Urinary Tract Infections",
    "incontinencia urinaria":   "Urinary Incontinence",
    # Oncológico
    "cancer":                   "Neoplasms",
    "cancro":                   "Neoplasms",
    "tumor":                    "Neoplasms",
    "leucemia":                 "Leukemia",
    "linfoma":                  "Lymphoma",
    "melanoma":                 "Melanoma",
    # Infeccioso
    "dengue":                   "Dengue",
    "zika":                     "Zika Virus Infection",
    "chikungunya":              "Chikungunya Fever",
    "hiv":                      "HIV Infections",
    "aids":                     "Acquired Immunodeficiency Syndrome",
    "hepatite":                 "Hepatitis",
    "covid":                    "COVID-19",
    "coronavirus":              "COVID-19",
    # Álcool / Substâncias
    "alcoolismo":               "Alcoholism",
    "alcool":                   "Alcohol Drinking",
    "beber":                    "Alcohol Drinking",
    "vinho":                    "Wine",
    "tabagismo":                "Smoking",
    "cigarro":                  "Smoking",
    "fumo":                     "Smoking",
    "drogas":                   "Substance-Related Disorders",
    # Saúde da mulher
    "gravidez":                 "Pregnancy",
    "gestacao":                 "Pregnancy",
    "menopausa":                "Menopause",
    "endometriose":             "Endometriosis",
    "sindrome dos ovarios policisticos": "Polycystic Ovary Syndrome",
    "sop":                      "Polycystic Ovary Syndrome",
    "cancer de mama":           "Breast Neoplasms",
    "cancer de colo":           "Uterine Cervical Neoplasms",
    # Pediatria
    "febre":                    "Fever",
    "desnutricao":              "Malnutrition",
    # Outros
    "anemia":                   "Anemia",
    "alergia":                  "Hypersensitivity",
    "rinite":                   "Rhinitis, Allergic",
    "sinusite":                 "Sinusitis",
    "acne":                     "Acne Vulgaris",
    "psoriase":                 "Psoriasis",
    "eczema":                   "Eczema",
    "queda de cabelo":          "Alopecia",
    "calvicie":                 "Alopecia",
    "disfuncao eretil":         "Erectile Dysfunction",
    "impotencia":               "Erectile Dysfunction",
    "fertilidade":              "Fertility",
    "infertilidade":            "Infertility",
    "sedentarismo":             "Sedentary Behavior",
    "exercicio fisico":         "Exercise",
    "atividade fisica":         "Exercise",
    "vacina":                   "Vaccines",
    "vacinacao":                "Vaccination",
}


def normalize_str(text):
    nfkd = unicodedata.normalize("NFKD", text.lower())
    return "".join(c for c in nfkd if not unicodedata.combining(c))


def apply_coloquial_dict(text_pt: str) -> tuple:
    """
    Varre o texto PT e substitui expressões coloquiais pelos descritores MeSH.
    Retorna (texto_modificado, lista_de_substituicoes).
    Ordena por comprimento decrescente para que frases longas tenham prioridade.
    """
    text_norm = normalize_str(text_pt)
    substituicoes = []
    resultado = text_pt

    for chave in sorted(COLOQUIAL_DICT.keys(), key=len, reverse=True):
        chave_norm = normalize_str(chave)
        if chave_norm in text_norm:
            mesh_term = COLOQUIAL_DICT[chave]
            text_norm = text_norm.replace(chave_norm, normalize_str(mesh_term))
            resultado = re.sub(re.escape(chave), mesh_term, resultado, flags=re.IGNORECASE)
            substituicoes.append((chave.title(), mesh_term))

    return resultado, substituicoes

def translate_to_english(text):
    return GoogleTranslator(source="auto", target="en").translate(text)

def detect_localities(text_pt):
    text_n = normalize_str(text_pt)
    found = []
    for loc in LOCALITY_TERMS:
        if normalize_str(loc) in text_n:
            found.append(loc.title())
    return list(dict.fromkeys(found))

def remove_localities(text_en, localities):
    for loc in localities:
        text_en = re.sub(re.escape(loc), " ", text_en, flags=re.IGNORECASE)
    return re.sub(r"\s{2,}", " ", text_en).strip()

def extract_concepts_nlp(text_en):
    blob = TextBlob(text_en)
    protected = set()
    concepts = []
    for phrase in blob.noun_phrases:
        phrase_clean = phrase.strip().lower()
        if len(phrase_clean) < 3:
            continue
        words = phrase_clean.split()
        if all(w in STOPWORDS_RESIDUAL for w in words):
            continue
        if words[0] in VERBS_TO_REMOVE:
            continue
        canonical = phrase.strip().title()
        concepts.append(canonical)
        for w in words:
            protected.add(w)
    for word, pos in blob.tags:
        word_l = word.lower()
        if word_l in protected or pos not in ALLOWED_POS:
            continue
        if word_l in STOPWORDS_RESIDUAL or word_l in VERBS_TO_REMOVE:
            continue
        if len(word_l) < 3:
            continue
        concepts.append(word.capitalize())
    seen = set()
    final = []
    for c in concepts:
        key = c.lower()
        if key not in seen:
            seen.add(key)
            final.append(c)
    return final

def validar_mesh(termo):
    try:
        resp = requests.get(
            PUBMED_ESEARCH,
            params={"db": "mesh", "term": termo, "retmode": "json", "retmax": "1"},
            timeout=6,
        )
        count = int(resp.json().get("esearchresult", {}).get("count", 0))
        return {"termo": termo, "is_mesh": count > 0}
    except Exception:
        return {"termo": termo, "is_mesh": False}

def validar_mesh_paralelo(conceitos):
    resultados = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as ex:
        futures = {ex.submit(validar_mesh, c): c for c in conceitos}
        for f in concurrent.futures.as_completed(futures):
            r = f.result()
            resultados[r["termo"]] = r["is_mesh"]
    return resultados

def quote_if_needed(term):
    return f'"{term}"' if " " in term else term

def build_boolean_string(concepts):
    blocks = []
    for c in concepts:
        q = quote_if_needed(c)
        blocks.append(f"({q}[MeSH Terms] OR {q}[tiab])")
    return "\nAND\n".join(blocks)

def build_explanation_rows(concepts, mesh_status):
    rows = []
    for i, c in enumerate(concepts):
        q = quote_if_needed(c)
        is_mesh = mesh_status.get(c, False)
        rows.append({
            "Conceito": c,
            "Status": "Descritor MeSH" if is_mesh else "Termo livre",
            "Bloco na String": f"({q}[MeSH Terms] OR {q}[tiab])",
        })
        if i < len(concepts) - 1:
            rows.append({"Conceito": "—", "Status": "", "Bloco na String": "AND"})
    return rows


# ─────────────────────────────────────────────
#  SESSION STATE
# ─────────────────────────────────────────────
defaults = {
    "pipeline_done": False,
    "query_used": "",
    "translated": "",
    "localities": [],
    "concepts_raw": [],
    "mesh_status": {},
    "selected": {},
    "show_result": False,
    "boolean_str": "",
    "concepts_final": [],
    "substituicoes_dict": [],
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ─────────────────────────────────────────────
#  SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="sb-institution">
        <div class="sb-inst-name">Universidade de Vassouras</div>
        <div class="sb-inst-sub">
            Monitoria de Iniciação Científica<br>
            Matheus Degani
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<span class="sb-section-label">Sobre</span>', unsafe_allow_html=True)
    st.markdown("""
    <div class="sb-body">
        O MedSearch Architect converte descrições em português
        em <em>Boolean Searches</em> estruturadas para o PubMed,
        com validação via API oficial da NLM.
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<hr class="sb-divider">', unsafe_allow_html=True)
    st.markdown('<span class="sb-section-label">Pipeline de Processamento</span>', unsafe_allow_html=True)

    for num, label in [
        ("01", "Tradução automática PT → EN"),
        ("02", "Extração NLP (TextBlob)"),
        ("03", "Filtragem por POS Tagging"),
        ("04", "Validação via API NLM/PubMed"),
        ("05", "Curadoria pelo pesquisador"),
        ("06", "Geração da Boolean String"),
    ]:
        st.markdown(
            f'<div class="sb-pipeline-item">'
            f'<span class="sb-pipeline-num">{num}</span>'
            f'<span>{label}</span>'
            f'</div>',
            unsafe_allow_html=True,
        )


# ─────────────────────────────────────────────
#  HEADER PRINCIPAL
# ─────────────────────────────────────────────
st.markdown("""
<div class="page-header">
    <div class="page-header-eyebrow">Ferramenta de Apoio à Pesquisa Científica</div>
    <div class="page-header-title">MedSearch Architect</div>
    <div class="page-header-sub">
        Descreva sua pergunta de pesquisa em português.<br>
        O sistema traduz, analisa a sintaxe médica e valida cada conceito no vocabulário MeSH.
    </div>
</div>
""", unsafe_allow_html=True)

tab_builder, tab_help = st.tabs(["Construtor de Busca", "Ajuda e Tutorial"])


# ════════════════════════════════════════════
#  TAB 1 — Construtor
# ════════════════════════════════════════════
with tab_builder:

    # ── Entrada ──────────────────────────────────────────
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">Descrição da Pesquisa</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="card-sub">'
        'Escreva como falaria com seu orientador, em português corrente. '
        'Evite abreviações e termos muito coloquiais.'
        '</div>',
        unsafe_allow_html=True,
    )

    query = st.text_area(
        label="query",
        label_visibility="collapsed",
        placeholder=(
            "Ex.: prevalência de asma em crianças em Vassouras\n"
            "Ex.: mortalidade por insuficiência cardíaca em idosos\n"
            "Ex.: ventilação mecânica em pacientes com DPOC"
        ),
        height=110,
        key="query_input",
    )

    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        btn_analisar = st.button("Analisar e Gerar String", use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # ── Pipeline ─────────────────────────────────────────
    if btn_analisar:
        if not query.strip():
            st.warning("Descreva sua pesquisa antes de continuar.")
        else:
            st.session_state.pipeline_done = False
            st.session_state.show_result   = False
            st.session_state.boolean_str   = ""

            localities = detect_localities(query)

            # ── Pré-processamento: substitui termos coloquiais PT → MeSH ──
            query_preprocessed, substituicoes_dict = apply_coloquial_dict(query)

            with st.status("Traduzindo para inglês...", expanded=True) as status:
                try:
                    translated = translate_to_english(query_preprocessed)
                    translated_clean = remove_localities(translated, localities)
                    status.update(label="Traducao concluida.", state="complete")
                except Exception as e:
                    st.error(f"Erro na tradução: {e}")
                    st.stop()

            with st.status("Analisando sintaxe médica...", expanded=True) as status:
                time.sleep(0.2)
                concepts_raw = extract_concepts_nlp(translated_clean)
                if not concepts_raw:
                    status.update(label="Nenhum conceito identificado.", state="error")
                    st.error("Não foi possível extrair conceitos. Tente uma descrição mais específica.")
                    st.stop()
                status.update(
                    label=f"{len(concepts_raw)} conceito(s) identificado(s).",
                    state="complete",
                )

            with st.status("Consultando base de dados — NLM, Bethesda, Maryland...", expanded=True) as status:
                mesh_status = validar_mesh_paralelo(concepts_raw)
                n_mesh = sum(1 for v in mesh_status.values() if v)
                status.update(
                    label=f"Validacao concluida. {n_mesh} descritor(es) MeSH confirmado(s).",
                    state="complete",
                )

            st.session_state.pipeline_done = True
            st.session_state.query_used    = query
            st.session_state.translated    = translated
            st.session_state.localities    = localities
            st.session_state.concepts_raw  = concepts_raw
            st.session_state.mesh_status   = mesh_status
            st.session_state.selected      = {c: True for c in concepts_raw}
            st.session_state.substituicoes_dict = substituicoes_dict

    # ── Resultados persistidos ────────────────────────────
    if st.session_state.pipeline_done:

        if st.session_state.substituicoes_dict:
            subs = st.session_state.substituicoes_dict
            linhas = "  \n".join(f"**{pt}** → `{mesh}`" for pt, mesh in subs)
            st.info(
                f"🔤 **Dicionário coloquial aplicado** — "
                f"{len(subs)} termo(s) substituído(s) antes da tradução:  \n{linhas}"
            )

        if st.session_state.localities:
            st.warning(
                f"Dado local detectado: {', '.join(st.session_state.localities)}. "
                "Localidades foram removidas da string — o PubMed opera em escala global e "
                "cidades pequenas raramente possuem descritores MeSH. "
                "Para dados locais, consulte também o [Google Acadêmico](https://scholar.google.com.br) "
                "e o [BVS](https://bvsalud.org)."
            )

        # Tradução
        with st.expander("Tradução automática — PT / EN", expanded=False):
            col_a, col_b = st.columns(2)
            with col_a:
                st.markdown(
                    '<div class="trans-section">'
                    '<span class="trans-label">Texto original — Português</span>'
                    f'<div class="trans-box trans-box-pt">{st.session_state.query_used}</div>'
                    '</div>',
                    unsafe_allow_html=True,
                )
            with col_b:
                st.markdown(
                    '<div class="trans-section">'
                    '<span class="trans-label">Texto traduzido — Inglês</span>'
                    f'<div class="trans-box trans-box-en">{st.session_state.translated}</div>'
                    '</div>',
                    unsafe_allow_html=True,
                )

        # ── Curadoria — lista vertical ────────────────────
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">Curadoria dos Conceitos</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="card-sub">'
            'Revise os conceitos extraídos. '
            'Termos marcados como "Descritor MeSH" foram confirmados na base da NLM. '
            'Desmarque qualquer item que represente ruído antes de gerar a string.'
            '</div>',
            unsafe_allow_html=True,
        )

        concepts_raw = st.session_state.concepts_raw
        mesh_status  = st.session_state.mesh_status

        for i, concept in enumerate(concepts_raw):
            is_mesh    = mesh_status.get(concept, False)
            status_cls = "curation-status curation-status-mesh" if is_mesh else "curation-status"
            status_txt = "Descritor MeSH" if is_mesh else "Termo livre"

            col_chk, col_term, col_status = st.columns([0.5, 3.5, 2])
            with col_chk:
                checked = st.checkbox(
                    label=" ",
                    value=st.session_state.selected.get(concept, True),
                    key=f"cb_{concept}",
                )
                st.session_state.selected[concept] = checked
            with col_term:
                st.markdown(
                    f'<div class="curation-term" style="padding-top:0.3rem;">{concept}</div>',
                    unsafe_allow_html=True,
                )
            with col_status:
                st.markdown(
                    f'<div style="padding-top:0.3rem;">'
                    f'<span class="{status_cls}">{status_txt}</span>'
                    f'</div>',
                    unsafe_allow_html=True,
                )

        st.markdown('</div>', unsafe_allow_html=True)

        concepts_final = [c for c in concepts_raw if st.session_state.selected.get(c, True)]

        if not concepts_final:
            st.error("Selecione ao menos um conceito para gerar a string.")
        else:
            c1b, c2b, c3b = st.columns([1, 2, 1])
            with c2b:
                btn_final = st.button(
                    f"Gerar Boolean String  ({len(concepts_final)} conceito(s) selecionado(s))",
                    use_container_width=True,
                    key="btn_final",
                )

            if btn_final:
                st.session_state.boolean_str   = build_boolean_string(concepts_final)
                st.session_state.show_result   = True
                st.session_state.concepts_final = concepts_final

            # ── Saída ─────────────────────────────────────
            if st.session_state.show_result and st.session_state.boolean_str:
                concepts_final = st.session_state.get("concepts_final", concepts_final)
                mesh_final     = {c: mesh_status.get(c, False) for c in concepts_final}

                st.markdown('<div class="result-card">', unsafe_allow_html=True)
                st.markdown('<div class="card-title">Boolean String — PubMed</div>', unsafe_allow_html=True)
                st.markdown(
                    '<div class="card-sub">'
                    'Copie o bloco abaixo e cole em '
                    '<a href="https://pubmed.ncbi.nlm.nih.gov/advanced/" target="_blank">'
                    'PubMed Advanced Search</a>.'
                    '</div>',
                    unsafe_allow_html=True,
                )
                st.code(st.session_state.boolean_str, language="text")
                st.markdown(
                    '<div class="notice-box">'
                    'Muitos resultados: adicione conceitos (mais blocos AND). '
                    'Poucos resultados: remova um bloco ou revise os termos.'
                    '</div>',
                    unsafe_allow_html=True,
                )
                st.markdown('</div>', unsafe_allow_html=True)

                # Tabela explicativa
                st.markdown('<div class="explain-card">', unsafe_allow_html=True)
                st.markdown('<div class="card-title">Mapa da Boolean String</div>', unsafe_allow_html=True)
                st.markdown(
                    '<div class="card-sub">Cada linha corresponde a um conceito e seu bloco na string final.</div>',
                    unsafe_allow_html=True,
                )
                df = pd.DataFrame(build_explanation_rows(concepts_final, mesh_final))
                st.dataframe(
                    df, use_container_width=True, hide_index=True,
                    column_config={
                        "Conceito": st.column_config.TextColumn("Conceito",        width="medium"),
                        "Status":   st.column_config.TextColumn("Status",          width="small"),
                        "Bloco na String": st.column_config.TextColumn("Bloco na String", width="large"),
                    },
                )
                st.markdown('</div>', unsafe_allow_html=True)

    # ── Estado inicial ────────────────────────────────────
    if not st.session_state.pipeline_done and not btn_analisar:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">Pipeline de Processamento</div>', unsafe_allow_html=True)
        st.markdown('<div class="card-sub">Sequência de operações executadas ao submeter uma descrição.</div>', unsafe_allow_html=True)
        st.markdown("""
        <div class="pipeline-flow">
            <div class="pipeline-step">
                <div class="pipeline-step-num">Etapa 01</div>
                <div class="pipeline-step-label">Entrada</div>
                <div class="pipeline-step-desc">Texto livre em português</div>
            </div>
            <div class="pipeline-arrow">›</div>
            <div class="pipeline-step">
                <div class="pipeline-step-num">Etapa 02</div>
                <div class="pipeline-step-label">Tradução</div>
                <div class="pipeline-step-desc">PT para EN (automático)</div>
            </div>
            <div class="pipeline-arrow">›</div>
            <div class="pipeline-step">
                <div class="pipeline-step-num">Etapa 03</div>
                <div class="pipeline-step-label">NLP</div>
                <div class="pipeline-step-desc">noun_phrases + POS Tagging</div>
            </div>
            <div class="pipeline-arrow">›</div>
            <div class="pipeline-step">
                <div class="pipeline-step-num">Etapa 04</div>
                <div class="pipeline-step-label">Validação MeSH</div>
                <div class="pipeline-step-desc">API NLM — Bethesda, MD</div>
            </div>
            <div class="pipeline-arrow">›</div>
            <div class="pipeline-step">
                <div class="pipeline-step-num">Etapa 05</div>
                <div class="pipeline-step-label">Curadoria</div>
                <div class="pipeline-step-desc">Revisão pelo pesquisador</div>
            </div>
            <div class="pipeline-arrow">›</div>
            <div class="pipeline-step">
                <div class="pipeline-step-num">Etapa 06</div>
                <div class="pipeline-step-label">Boolean String</div>
                <div class="pipeline-step-desc">MeSH Terms + tiab + AND/OR</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)


# ════════════════════════════════════════════
#  TAB 2 — Ajuda e Tutorial
# ════════════════════════════════════════════
with tab_help:
    col_left, col_right = st.columns([1, 1], gap="large")

    with col_left:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">Como usar</div>', unsafe_allow_html=True)

        for num, title, body in [
            ("1", "Descreva em português",
             'Escreva sua pergunta de pesquisa como falaria com seu orientador. '
             'Ex.: <em>"prevalência de depressão na doença de Parkinson"</em>'),
            ("2", "Aguarde o pipeline",
             "O sistema traduz automaticamente, extrai os conceitos via NLP "
             "e consulta a API da NLM para validar cada descritor no vocabulário MeSH."),
            ("3", "Revise os conceitos",
             "Descritores confirmados no MeSH aparecem marcados como tal. "
             "Desmarque qualquer termo que represente ruído antes de gerar a string."),
            ("4", "Use no PubMed",
             'Cole a string em <a href="https://pubmed.ncbi.nlm.nih.gov/advanced/" target="_blank">'
             "pubmed.ncbi.nlm.nih.gov/advanced</a> e clique em <em>Search</em>."),
        ]:
            st.markdown(
                f'<div class="step-row">'
                f'<div class="step-n">{num}</div>'
                f'<div class="step-body"><strong>{title}</strong><br>{body}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">Exemplos de Entrada</div>', unsafe_allow_html=True)
        for area, ex in [
            ("Cardiologia",    "mortalidade por insuficiência cardíaca em idosos"),
            ("Pneumologia",    "ventilação mecânica em pacientes com DPOC"),
            ("Neurologia",     "prevalência de depressão na doença de Parkinson"),
            ("Endocrinologia", "resistência à insulina em diabéticos tipo 2"),
            ("Saúde Local",    "prevalência de hipertensão em adultos em Vassouras"),
        ]:
            st.markdown(
                f'<div style="padding:0.65rem 0;border-bottom:1px solid #EDF2F7;">'
                f'<div style="font-size:0.68rem;font-weight:600;letter-spacing:1px;'
                f'text-transform:uppercase;color:#718096;margin-bottom:0.2rem;">{area}</div>'
                f'<div style="font-size:0.88rem;color:#1a202c;font-style:italic;">"{ex}"</div>'
                f'</div>',
                unsafe_allow_html=True,
            )
        st.markdown('</div>', unsafe_allow_html=True)

    with col_right:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">Glossário</div>', unsafe_allow_html=True)
        for term, defn in [
            ("[MeSH Terms]",
             "Medical Subject Headings — vocabulário controlado da NLM/NIH. "
             "Todo artigo do PubMed recebe descritores MeSH independentemente do idioma de publicação."),
            ("[tiab]",
             "Title/Abstract — busca o termo no título e no resumo. "
             "Captura artigos recentes ainda não indexados pelo MeSH."),
            ("AND",
             "Interseção booleana. O artigo deve abordar todos os conceitos simultaneamente. "
             "Define o escopo e aumenta a especificidade da busca."),
            ("OR",
             "União booleana. Aceita qualquer forma de indexação do mesmo conceito. "
             "Aumenta a cobertura sem excluir artigos relevantes."),
            ("noun_phrases",
             "Frases nominais detectadas pelo TextBlob. "
             "Preservam termos compostos como 'Mechanical Ventilation' como uma unidade única."),
            ("POS Tagging",
             "Classificação morfossintática. Apenas substantivos (NN), adjetivos (JJ) "
             "e particípios qualificadores (VBN) são aceitos na string final."),
            ("Curadoria",
             "Etapa de revisão humana. O pesquisador valida ou descarta os conceitos "
             "extraídos antes da geração da string definitiva."),
        ]:
            st.markdown(
                f'<div class="gloss-item">'
                f'<div class="gloss-term">{term}</div>'
                f'<div class="gloss-def">{defn}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">Sensibilidade e Especificidade</div>', unsafe_allow_html=True)
        st.markdown("""
        <table style="width:100%;border-collapse:collapse;font-size:0.85rem;">
            <thead>
                <tr style="border-bottom:2px solid #E2E8F0;">
                    <th style="padding:0.5rem 0.6rem;text-align:left;color:#0A1628;font-weight:600;">Estratégia</th>
                    <th style="padding:0.5rem 0.6rem;text-align:center;color:#0A1628;font-weight:600;">Volume</th>
                    <th style="padding:0.5rem 0.6rem;text-align:left;color:#0A1628;font-weight:600;">Indicação</th>
                </tr>
            </thead>
            <tbody>
                <tr style="border-bottom:1px solid #EDF2F7;">
                    <td style="padding:0.55rem 0.6rem;"><code style="font-size:0.8rem;background:#F7FAFC;padding:0.1rem 0.3rem;border-radius:3px;border:1px solid #E2E8F0;">Apenas [MeSH]</code></td>
                    <td style="padding:0.55rem 0.6rem;text-align:center;color:#4a5568;">Menor</td>
                    <td style="padding:0.55rem 0.6rem;color:#4a5568;">Alta precisão</td>
                </tr>
                <tr style="border-bottom:1px solid #EDF2F7;background:#FAFAFA;">
                    <td style="padding:0.55rem 0.6rem;"><code style="font-size:0.8rem;background:#F7FAFC;padding:0.1rem 0.3rem;border-radius:3px;border:1px solid #E2E8F0;">[MeSH] OR [tiab]</code></td>
                    <td style="padding:0.55rem 0.6rem;text-align:center;color:#4a5568;">Equilibrado</td>
                    <td style="padding:0.55rem 0.6rem;color:#4a5568;">Uso geral</td>
                </tr>
                <tr>
                    <td style="padding:0.55rem 0.6rem;"><code style="font-size:0.8rem;background:#F7FAFC;padding:0.1rem 0.3rem;border-radius:3px;border:1px solid #E2E8F0;">Apenas [tiab]</code></td>
                    <td style="padding:0.55rem 0.6rem;text-align:center;color:#4a5568;">Maior</td>
                    <td style="padding:0.55rem 0.6rem;color:#4a5568;">Revisão sistemática</td>
                </tr>
            </tbody>
        </table>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
[data-testid="stSidebar"] div,
[data-testid="stSidebar"] li,
[data-testid="stSidebar"] a { color: #FFFFFF !important; }

.sb-institution {
    padding: 1.6rem 1rem 1.2rem;
    border-bottom: 1px solid #2a4a6a;
    margin-bottom: 1.4rem;
}
.sb-inst-name {
    font-family: Georgia, 'Times New Roman', serif;
    font-size: 1rem;
    font-weight: 700;
    color: #FFFFFF !important;
    line-height: 1.4;
    letter-spacing: 0.2px;
}
.sb-inst-sub {
    font-size: 0.75rem;
    color: #E2E8F0 !important;
    letter-spacing: 0.3px;
    margin-top: 0.35rem;
    line-height: 1.6;
}
.sb-section-label {
    font-size: 0.65rem;
    letter-spacing: 1.8px;
    text-transform: uppercase;
    color: #E2E8F0 !important;
    font-weight: 600;
    margin: 1.4rem 0 0.6rem;
    display: block;
}
.sb-body {
    font-size: 0.84rem;
    color: #FFFFFF !important;
    line-height: 1.7;
}
.sb-divider {
    border: none;
    border-top: 1px solid #2a4a6a;
    margin: 1.2rem 0;
}
.sb-pipeline-item {
    font-size: 0.82rem;
    color: #FFFFFF !important;
    padding: 0.3rem 0;
    display: flex;
    align-items: baseline;
    gap: 0.6rem;
    line-height: 1.6;
}
.sb-pipeline-num {
    font-size: 0.65rem;
    font-weight: 700;
    color: #E2E8F0 !important;
    min-width: 20px;
}
.sb-credit-block {
    margin-top: 1.4rem;
    padding: 0.9rem 1rem;
    border-top: 1px solid #2a4a6a;
}
.sb-credit-name {
    font-size: 0.84rem;
    font-weight: 700;
    color: #FFFFFF !important;
    margin-bottom: 0.2rem;
}
.sb-credit-role {
    font-size: 0.75rem;
    color: #E2E8F0 !important;
    line-height: 1.6;
}

/* ── HEADER PRINCIPAL ── */
.page-header {
    padding: 2rem 0 1.5rem;
    border-bottom: 1px solid #E2E8F0;
    margin-bottom: 1.8rem;
}
.page-header-eyebrow {
    font-size: 0.7rem;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: #475569;
    font-weight: 600;
    margin-bottom: 0.5rem;
}
.page-header-title {
    font-family: Georgia, 'Times New Roman', serif;
    font-size: 1.85rem;
    font-weight: 700;
    color: #0A1628;
    letter-spacing: -0.3px;
    line-height: 1.2;
    margin-bottom: 0.4rem;
}
.page-header-sub {
    font-size: 0.9rem;
    color: #475569;
    font-weight: 400;
    line-height: 1.6;
}

/* ── CARDS — sombra leve, sem borda pesada ── */
.card {
    background: #FFFFFF;
    border: none;
    border-radius: 6px;
    padding: 1.5rem 1.6rem;
    margin-bottom: 1rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.10), 0 1px 2px rgba(0,0,0,0.06);
}
.card-title {
    font-family: Georgia, 'Times New Roman', serif;
    font-size: 1rem;
    font-weight: 600;
    color: #0A1628;
    margin-bottom: 0.25rem;
    letter-spacing: 0.1px;
}
.card-sub {
    font-size: 0.84rem;
    color: #475569;
    margin-bottom: 1rem;
    line-height: 1.6;
}

/* ── INPUT — fundo branco, texto preto absoluto ── */
.stTextArea textarea {
    font-family: 'Inter', 'Segoe UI', sans-serif !important;
    font-size: 16px !important;
    color: #000000 !important;
    background: #FFFFFF !important;
    border: 1px solid #CBD5E0 !important;
    border-radius: 4px !important;
    line-height: 1.6 !important;
    resize: none !important;
    padding: 0.75rem 0.9rem !important;
}
.stTextArea textarea:focus {
    border-color: #0A1628 !important;
    box-shadow: 0 0 0 2px rgba(10,22,40,0.10) !important;
}
.stTextArea textarea::placeholder {
    color: #94a3b8 !important;
    font-style: italic !important;
}

/* ── BOTOES ── */
.stButton > button {
    background: #0A1628 !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 4px !important;
    padding: 0.6rem 1.6rem !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.88rem !important;
    letter-spacing: 0.3px !important;
    width: 100% !important;
    transition: background 0.15s !important;
    box-shadow: none !important;
}
.stButton > button:hover { background: #162540 !important; }

/* ── CAIXAS DE TRADUÇÃO — fundo branco, texto preto absoluto ── */
.trans-section { margin-bottom: 0.25rem; }
.trans-label {
    display: block !important;
    font-size: 0.68rem !important;
    font-weight: 700 !important;
    letter-spacing: 1.4px !important;
    text-transform: uppercase !important;
    color: #475569 !important;
    margin-bottom: 0.35rem !important;
}
.trans-box {
    border-radius: 4px !important;
    padding: 0.85rem 1rem !important;
    font-size: 0.92rem !important;
    font-weight: 400 !important;
    line-height: 1.65 !important;
    color: #000000 !important;
    border: 1px solid #CBD5E0 !important;
    background: #FFFFFF !important;
}
.trans-box-pt { background: #FFFFFF !important; }
.trans-box-en { background: #FFFFFF !important; border-left: 3px solid #0A1628 !important; }

/* ── CURADORIA — lista vertical ── */
.curation-term {
    font-family: 'Source Code Pro', 'Courier New', monospace;
    font-size: 0.9rem;
    font-weight: 600;
    color: #000000;
    flex: 1;
}
/* Status MeSH: texto em negrito, sem fundo colorido */
.curation-status {
    font-size: 0.75rem;
    font-weight: 500;
    letter-spacing: 0.2px;
    color: #475569;
    white-space: nowrap;
    align-self: center;
}
.curation-status-mesh {
    font-weight: 700;
    color: #166534; /* verde escuro — contraste WCAG AA garantido sobre branco */
}

/* ── RESULTADO ── */
.result-card {
    background: #FFFFFF;
    border: none;
    border-radius: 6px;
    padding: 1.5rem 1.6rem;
    margin-bottom: 1rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.10), 0 1px 2px rgba(0,0,0,0.06);
}
.explain-card {
    background: #FFFFFF;
    border: none;
    border-left: 3px solid #0A1628;
    border-radius: 6px;
    padding: 1.5rem 1.6rem;
    margin-bottom: 1rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.10), 0 1px 2px rgba(0,0,0,0.06);
}

/* ── AVISO ── */
.notice-box {
    background: #FFFFFF;
    border: 1px solid #CBD5E0;
    border-left: 3px solid #475569;
    border-radius: 4px;
    padding: 0.75rem 1rem;
    font-size: 0.85rem;
    color: #000000;
    line-height: 1.6;
    margin-top: 0.8rem;
}
.notice-box a { color: #2563EB; font-weight: 600; }

/* ── PIPELINE (estado inicial) ── */
.pipeline-flow {
    display: flex;
    align-items: stretch;
    flex-wrap: wrap;
    gap: 0;
    margin-top: 1.2rem;
}
.pipeline-step {
    background: #F8FAFC;
    border: 1px solid #E2E8F0;
    border-radius: 4px;
    padding: 0.75rem 0.9rem;
    flex: 1;
    min-width: 100px;
    box-shadow: 0 1px 2px rgba(0,0,0,0.05);
}
.pipeline-step-num {
    font-size: 0.62rem;
    font-weight: 700;
    letter-spacing: 1.2px;
    color: #475569;
    text-transform: uppercase;
    margin-bottom: 0.2rem;
}
.pipeline-step-label {
    font-size: 0.82rem;
    font-weight: 600;
    color: #000000;
    line-height: 1.3;
}
.pipeline-step-desc {
    font-size: 0.72rem;
    color: #475569;
    margin-top: 0.15rem;
    line-height: 1.5;
}
.pipeline-arrow {
    color: #94a3b8;
    font-size: 1rem;
    padding: 0 0.3rem;
    flex-shrink: 0;
    align-self: center;
}

/* ── GLOSSÁRIO ── */
.gloss-item {
    padding: 0.8rem 0;
    border-bottom: 1px solid #E2E8F0;
}
.gloss-item:last-child { border-bottom: none; }
.gloss-term {
    font-family: 'Source Code Pro', 'Courier New', monospace;
    font-size: 0.88rem;
    font-weight: 700;
    color: #000000;
}
.gloss-def {
    font-size: 0.84rem;
    color: #475569;
    margin-top: 0.2rem;
    line-height: 1.6;
}

/* ── STEPS ── */
.step-row {
    display: flex;
    gap: 0.9rem;
    align-items: flex-start;
    padding: 0.75rem 0;
    border-bottom: 1px solid #E2E8F0;
}
.step-row:last-child { border-bottom: none; }
.step-n {
    font-size: 0.72rem;
    font-weight: 700;
    color: #FFFFFF;
    background: #0A1628;
    border-radius: 50%;
    min-width: 24px;
    height: 24px;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    margin-top: 0.15rem;
}
.step-body { font-size: 0.88rem; color: #000000; line-height: 1.65; }
.step-body strong { color: #0A1628; font-weight: 600; }
.step-body a { color: #2563EB; font-weight: 600; }

/* ── TABS ── */
.stTabs [data-baseweb="tab-list"] {
    background: transparent;
    border-bottom: 1px solid #E2E8F0;
    border-radius: 0;
    padding: 0;
    gap: 0;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 0 !important;
    font-weight: 500 !important;
    color: #475569 !important;
    padding: 0.6rem 1.3rem !important;
    font-size: 0.88rem !important;
    border-bottom: 2px solid transparent !important;
    background: transparent !important;
}
.stTabs [aria-selected="true"] {
    color: #000000 !important;
    border-bottom: 2px solid #0A1628 !important;
    font-weight: 600 !important;
    background: transparent !important;
    box-shadow: none !important;
}

/* ── CHECKBOX ── */
.stCheckbox label {
    font-size: 0.88rem !important;
    color: #000000 !important;
    font-weight: 400 !important;
    line-height: 1.6 !important;
}

/* ── DATAFRAME — largura total, cabeçalhos nítidos ── */
[data-testid="stDataFrame"] {
    border: 1px solid #E2E8F0;
    border-radius: 4px;
    width: 100% !important;
}
[data-testid="stDataFrame"] th {
    background: #F8FAFC !important;
    color: #000000 !important;
    font-weight: 600 !important;
    font-size: 0.84rem !important;
    border-bottom: 2px solid #CBD5E0 !important;
}
[data-testid="stDataFrame"] td {
    color: #000000 !important;
    font-size: 0.84rem !important;
    line-height: 1.6 !important;
}

/* ── OCULTAR chrome Streamlit ── */
[data-testid="stToolbar"] { display: none !important; }
#MainMenu { display: none !important; }
footer { display: none !important; }

/* ── STATUS BOXES (st.status) ────────────────────────────────────────────────
   O st.status é renderizado pelo componente Expander do Streamlit:
     <div data-testid="stExpander">
       <details class="eqw31fm1">          ← WT  (fundo transparente quando fechado)
         <summary class="eqw31fm4">        ← qT  (summary clicável)
           <span class="eqw31fm2">…</span> ← GT  (ícone + label)
         </summary>
         <div data-testid="stExpanderDetails">…</div>
       </details>
     </div>
   O problema: o summary tem background 'transparent' quando fechado,
   e o tema do Streamlit define bodyText como uma cor clara — então texto
   fica invisível sobre fundo branco.
   Solução: forçar cor de texto escura em TODOS os elementos do stExpander,
   usando o seletor de classe Emotion gerado (.eqw31fm*) E o data-testid. ── */

/* Wrapper externo */
[data-testid="stExpander"] {
    color: #0A1628 !important;
}
/* O elemento <details> e tudo dentro dele */
[data-testid="stExpander"] details,
[data-testid="stExpander"] details * {
    color: #0A1628 !important;
}
/* O <summary> (cabeçalho clicável) — fechado E aberto */
[data-testid="stExpander"] summary {
    color: #0A1628 !important;
    background-color: #F0F4F8 !important;
}
[data-testid="stExpander"] summary * {
    color: #0A1628 !important;
}
/* Conteúdo interno (stExpanderDetails) */
[data-testid="stExpanderDetails"],
[data-testid="stExpanderDetails"] * {
    color: #0A1628 !important;
}
/* Ícones SVG dentro do expander */
[data-testid="stExpander"] svg {
    fill: #0A1628 !important;
    color: #0A1628 !important;
}
/* Fallback via classe Emotion gerada pelo Streamlit para o summary */
.eqw31fm4,
.eqw31fm4 * {
    color: #0A1628 !important;
    background-color: #F0F4F8 !important;
}
.eqw31fm1 summary,
.eqw31fm1 summary * {
    color: #0A1628 !important;
    background-color: #F0F4F8 !important;
}

/* ── WARNING BOX (st.warning) — texto escuro sobre fundo amarelo pastel ── */
[data-testid="stAlert"][kind="warning"],
div[data-testid="stAlert"] {
    background: #FEFCE8 !important;
    border: 1px solid #ca8a04 !important;
    border-radius: 6px !important;
}
[data-testid="stAlert"] p,
[data-testid="stAlert"] span,
[data-testid="stAlert"] div,
[data-testid="stAlert"] a,
[data-testid="stAlert"] li,
[data-testid="stAlert"] * {
    color: #713f12 !important;
}
[data-testid="stAlert"] a {
    color: #1d4ed8 !important;
    font-weight: 600 !important;
    text-decoration: underline !important;
}
/* Ícone do alerta */
[data-testid="stAlert"] svg {
    fill: #ca8a04 !important;
    color: #ca8a04 !important;
}
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════
#  LÓGICA — IDÊNTICA À VERSÃO ANTERIOR, SEM ALTERAÇÕES
# ══════════════════════════════════════════════════════

VERBS_TO_REMOVE = {
    "want","see","find","search","analyze","analyse","show","look","get",
    "make","use","know","check","review","investigate","explore","study",
    "examine","assess","evaluate","understand","determine","identify",
    "compare","describe","measure","calculate","need","try","help","provide",
}
ALLOWED_POS = {"NN","NNS","NNP","NNPS","JJ","VBN","VBG"}
STOPWORDS_RESIDUAL = {
    "a","an","the","of","in","on","at","to","for","with","by","from",
    "and","or","is","are","was","were","be","been","being","this","that",
    "these","those","it","its","among","between","during","after","before",
    "through","into","over","under","patients","patient","people","person",
    "individuals","population","group","sample","adults","children",
    "elderly","women","men","study","studies","article","articles",
    "paper","papers","research","data","result","results","method",
    "methods","analysis","assessment","evaluation","report","evidence",
    "impact","effect","effects","level","levels","rate","rates","type",
    "types","factor","factors","relationship","association","number",
    "case","cases","index","measure","measures","also","however",
    "therefore","thus","while","because","due","such","than","more",
    "less","new","old","different","various","several","many","large",
    "small","important","significant","common","current","recent",
    "previous","possible","general","main","major","potential",
    "non","anti","pre","post","per","vs","versus",
}
LOCALITY_TERMS = [
    "vassouras","resende","volta redonda","barra mansa","petropolis",
    "petrópolis","teresópolis","teresopolis","nova friburgo",
    "rio de janeiro","são paulo","sao paulo","brasil","brazil",
    "minas gerais","espirito santo","espírito santo","rio","rj","sp","mg","es",
]
PUBMED_ESEARCH = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"


def normalize_str(text):
    nfkd = unicodedata.normalize("NFKD", text.lower())
    return "".join(c for c in nfkd if not unicodedata.combining(c))

def translate_to_english(text):
    return GoogleTranslator(source="auto", target="en").translate(text)

def detect_localities(text_pt):
    text_n = normalize_str(text_pt)
    found = []
    for loc in LOCALITY_TERMS:
        if normalize_str(loc) in text_n:
            found.append(loc.title())
    return list(dict.fromkeys(found))

def remove_localities(text_en, localities):
    for loc in localities:
        text_en = re.sub(re.escape(loc), " ", text_en, flags=re.IGNORECASE)
    return re.sub(r"\s{2,}", " ", text_en).strip()

def extract_concepts_nlp(text_en):
    blob = TextBlob(text_en)
    protected = set()
    concepts = []
    for phrase in blob.noun_phrases:
        phrase_clean = phrase.strip().lower()
        if len(phrase_clean) < 3:
            continue
        words = phrase_clean.split()
        if all(w in STOPWORDS_RESIDUAL for w in words):
            continue
        if words[0] in VERBS_TO_REMOVE:
            continue
        canonical = phrase.strip().title()
        concepts.append(canonical)
        for w in words:
            protected.add(w)
    for word, pos in blob.tags:
        word_l = word.lower()
        if word_l in protected or pos not in ALLOWED_POS:
            continue
        if word_l in STOPWORDS_RESIDUAL or word_l in VERBS_TO_REMOVE:
            continue
        if len(word_l) < 3:
            continue
        concepts.append(word.capitalize())
    seen = set()
    final = []
    for c in concepts:
        key = c.lower()
        if key not in seen:
            seen.add(key)
            final.append(c)
    return final

def validar_mesh(termo):
    try:
        resp = requests.get(
            PUBMED_ESEARCH,
            params={"db": "mesh", "term": termo, "retmode": "json", "retmax": "1"},
            timeout=6,
        )
        count = int(resp.json().get("esearchresult", {}).get("count", 0))
        return {"termo": termo, "is_mesh": count > 0}
    except Exception:
        return {"termo": termo, "is_mesh": False}

def validar_mesh_paralelo(conceitos):
    resultados = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as ex:
        futures = {ex.submit(validar_mesh, c): c for c in conceitos}
        for f in concurrent.futures.as_completed(futures):
            r = f.result()
            resultados[r["termo"]] = r["is_mesh"]
    return resultados

def quote_if_needed(term):
    return f'"{term}"' if " " in term else term

def build_boolean_string(concepts):
    blocks = []
    for c in concepts:
        q = quote_if_needed(c)
        blocks.append(f"({q}[MeSH Terms] OR {q}[tiab])")
    return "\nAND\n".join(blocks)

def build_explanation_rows(concepts, mesh_status):
    rows = []
    for i, c in enumerate(concepts):
        q = quote_if_needed(c)
        is_mesh = mesh_status.get(c, False)
        rows.append({
            "Conceito": c,
            "Status": "Descritor MeSH" if is_mesh else "Termo livre",
            "Bloco na String": f"({q}[MeSH Terms] OR {q}[tiab])",
        })
        if i < len(concepts) - 1:
            rows.append({"Conceito": "—", "Status": "", "Bloco na String": "AND"})
    return rows


# ─────────────────────────────────────────────
#  SESSION STATE
# ─────────────────────────────────────────────
defaults = {
    "pipeline_done": False,
    "query_used": "",
    "translated": "",
    "localities": [],
    "concepts_raw": [],
    "mesh_status": {},
    "selected": {},
    "show_result": False,
    "boolean_str": "",
    "concepts_final": [],
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ─────────────────────────────────────────────
#  SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="sb-institution">
        <div class="sb-inst-name">Universidade de Vassouras</div>
        <div class="sb-inst-sub">
            Monitoria de Iniciação Científica<br>
            Matheus Degani
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<span class="sb-section-label">Sobre</span>', unsafe_allow_html=True)
    st.markdown("""
    <div class="sb-body">
        O MedSearch Architect converte descrições em português
        em <em>Boolean Searches</em> estruturadas para o PubMed,
        com validação via API oficial da NLM.
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<hr class="sb-divider">', unsafe_allow_html=True)
    st.markdown('<span class="sb-section-label">Pipeline de Processamento</span>', unsafe_allow_html=True)

    for num, label in [
        ("01", "Tradução automática PT → EN"),
        ("02", "Extração NLP (TextBlob)"),
        ("03", "Filtragem por POS Tagging"),
        ("04", "Validação via API NLM/PubMed"),
        ("05", "Curadoria pelo pesquisador"),
        ("06", "Geração da Boolean String"),
    ]:
        st.markdown(
            f'<div class="sb-pipeline-item">'
            f'<span class="sb-pipeline-num">{num}</span>'
            f'<span>{label}</span>'
            f'</div>',
            unsafe_allow_html=True,
        )


# ─────────────────────────────────────────────
#  HEADER PRINCIPAL
# ─────────────────────────────────────────────
st.markdown("""
<div class="page-header">
    <div class="page-header-eyebrow">Ferramenta de Apoio à Pesquisa Científica</div>
    <div class="page-header-title">MedSearch Architect</div>
    <div class="page-header-sub">
        Descreva sua pergunta de pesquisa em português.<br>
        O sistema traduz, analisa a sintaxe médica e valida cada conceito no vocabulário MeSH.
    </div>
</div>
""", unsafe_allow_html=True)

tab_builder, tab_help = st.tabs(["Construtor de Busca", "Ajuda e Tutorial"])


# ════════════════════════════════════════════
#  TAB 1 — Construtor
# ════════════════════════════════════════════
with tab_builder:

    # ── Entrada ──────────────────────────────────────────
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">Descrição da Pesquisa</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="card-sub">'
        'Escreva como falaria com seu orientador, em português corrente. '
        'Evite abreviações e termos muito coloquiais.'
        '</div>',
        unsafe_allow_html=True,
    )

    query = st.text_area(
        label="query",
        label_visibility="collapsed",
        placeholder=(
            "Ex.: prevalência de asma em crianças em Vassouras\n"
            "Ex.: mortalidade por insuficiência cardíaca em idosos\n"
            "Ex.: ventilação mecânica em pacientes com DPOC"
        ),
        height=110,
        key="query_input",
    )

    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        btn_analisar = st.button("Analisar e Gerar String", use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # ── Pipeline ─────────────────────────────────────────
    if btn_analisar:
        if not query.strip():
            st.warning("Descreva sua pesquisa antes de continuar.")
        else:
            st.session_state.pipeline_done = False
            st.session_state.show_result   = False
            st.session_state.boolean_str   = ""

            localities = detect_localities(query)

            with st.status("Traduzindo para inglês...", expanded=True) as status:
                try:
                    translated = translate_to_english(query)
                    translated_clean = remove_localities(translated, localities)
                    status.update(label="Traducao concluida.", state="complete")
                except Exception as e:
                    st.error(f"Erro na tradução: {e}")
                    st.stop()

            with st.status("Analisando sintaxe médica...", expanded=True) as status:
                time.sleep(0.2)
                concepts_raw = extract_concepts_nlp(translated_clean)
                if not concepts_raw:
                    status.update(label="Nenhum conceito identificado.", state="error")
                    st.error("Não foi possível extrair conceitos. Tente uma descrição mais específica.")
                    st.stop()
                status.update(
                    label=f"{len(concepts_raw)} conceito(s) identificado(s).",
                    state="complete",
                )

            with st.status("Consultando base de dados — NLM, Bethesda, Maryland...", expanded=True) as status:
                mesh_status = validar_mesh_paralelo(concepts_raw)
                n_mesh = sum(1 for v in mesh_status.values() if v)
                status.update(
                    label=f"Validacao concluida. {n_mesh} descritor(es) MeSH confirmado(s).",
                    state="complete",
                )

            st.session_state.pipeline_done = True
            st.session_state.query_used    = query
            st.session_state.translated    = translated
            st.session_state.localities    = localities
            st.session_state.concepts_raw  = concepts_raw
            st.session_state.mesh_status   = mesh_status
            st.session_state.selected      = {c: True for c in concepts_raw}

    # ── Resultados persistidos ────────────────────────────
    if st.session_state.pipeline_done:

        if st.session_state.localities:
            st.warning(
                f"Dado local detectado: {', '.join(st.session_state.localities)}. "
                "Localidades foram removidas da string — o PubMed opera em escala global e "
                "cidades pequenas raramente possuem descritores MeSH. "
                "Para dados locais, consulte também o [Google Acadêmico](https://scholar.google.com.br) "
                "e o [BVS](https://bvsalud.org)."
            )

        # Tradução
        with st.expander("Tradução automática — PT / EN", expanded=False):
            col_a, col_b = st.columns(2)
            with col_a:
                st.markdown(
                    '<div class="trans-section">'
                    '<span class="trans-label">Texto original — Português</span>'
                    f'<div class="trans-box trans-box-pt">{st.session_state.query_used}</div>'
                    '</div>',
                    unsafe_allow_html=True,
                )
            with col_b:
                st.markdown(
                    '<div class="trans-section">'
                    '<span class="trans-label">Texto traduzido — Inglês</span>'
                    f'<div class="trans-box trans-box-en">{st.session_state.translated}</div>'
                    '</div>',
                    unsafe_allow_html=True,
                )

        # ── Curadoria — lista vertical ────────────────────
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">Curadoria dos Conceitos</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="card-sub">'
            'Revise os conceitos extraídos. '
            'Termos marcados como "Descritor MeSH" foram confirmados na base da NLM. '
            'Desmarque qualquer item que represente ruído antes de gerar a string.'
            '</div>',
            unsafe_allow_html=True,
        )

        concepts_raw = st.session_state.concepts_raw
        mesh_status  = st.session_state.mesh_status

        for i, concept in enumerate(concepts_raw):
            is_mesh    = mesh_status.get(concept, False)
            status_cls = "curation-status curation-status-mesh" if is_mesh else "curation-status"
            status_txt = "Descritor MeSH" if is_mesh else "Termo livre"

            col_chk, col_term, col_status = st.columns([0.5, 3.5, 2])
            with col_chk:
                checked = st.checkbox(
                    label=" ",
                    value=st.session_state.selected.get(concept, True),
                    key=f"cb_{concept}",
                )
                st.session_state.selected[concept] = checked
            with col_term:
                st.markdown(
                    f'<div class="curation-term" style="padding-top:0.3rem;">{concept}</div>',
                    unsafe_allow_html=True,
                )
            with col_status:
                st.markdown(
                    f'<div style="padding-top:0.3rem;">'
                    f'<span class="{status_cls}">{status_txt}</span>'
                    f'</div>',
                    unsafe_allow_html=True,
                )

        st.markdown('</div>', unsafe_allow_html=True)

        concepts_final = [c for c in concepts_raw if st.session_state.selected.get(c, True)]

        if not concepts_final:
            st.error("Selecione ao menos um conceito para gerar a string.")
        else:
            c1b, c2b, c3b = st.columns([1, 2, 1])
            with c2b:
                btn_final = st.button(
                    f"Gerar Boolean String  ({len(concepts_final)} conceito(s) selecionado(s))",
                    use_container_width=True,
                    key="btn_final",
                )

            if btn_final:
                st.session_state.boolean_str   = build_boolean_string(concepts_final)
                st.session_state.show_result   = True
                st.session_state.concepts_final = concepts_final

            # ── Saída ─────────────────────────────────────
            if st.session_state.show_result and st.session_state.boolean_str:
                concepts_final = st.session_state.get("concepts_final", concepts_final)
                mesh_final     = {c: mesh_status.get(c, False) for c in concepts_final}

                st.markdown('<div class="result-card">', unsafe_allow_html=True)
                st.markdown('<div class="card-title">Boolean String — PubMed</div>', unsafe_allow_html=True)
                st.markdown(
                    '<div class="card-sub">'
                    'Copie o bloco abaixo e cole em '
                    '<a href="https://pubmed.ncbi.nlm.nih.gov/advanced/" target="_blank">'
                    'PubMed Advanced Search</a>.'
                    '</div>',
                    unsafe_allow_html=True,
                )
                st.code(st.session_state.boolean_str, language="text")
                st.markdown(
                    '<div class="notice-box">'
                    'Muitos resultados: adicione conceitos (mais blocos AND). '
                    'Poucos resultados: remova um bloco ou revise os termos.'
                    '</div>',
                    unsafe_allow_html=True,
                )
                st.markdown('</div>', unsafe_allow_html=True)

                # Tabela explicativa
                st.markdown('<div class="explain-card">', unsafe_allow_html=True)
                st.markdown('<div class="card-title">Mapa da Boolean String</div>', unsafe_allow_html=True)
                st.markdown(
                    '<div class="card-sub">Cada linha corresponde a um conceito e seu bloco na string final.</div>',
                    unsafe_allow_html=True,
                )
                df = pd.DataFrame(build_explanation_rows(concepts_final, mesh_final))
                st.dataframe(
                    df, use_container_width=True, hide_index=True,
                    column_config={
                        "Conceito": st.column_config.TextColumn("Conceito",        width="medium"),
                        "Status":   st.column_config.TextColumn("Status",          width="small"),
                        "Bloco na String": st.column_config.TextColumn("Bloco na String", width="large"),
                    },
                )
                st.markdown('</div>', unsafe_allow_html=True)

    # ── Estado inicial ────────────────────────────────────
    if not st.session_state.pipeline_done and not btn_analisar:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">Pipeline de Processamento</div>', unsafe_allow_html=True)
        st.markdown('<div class="card-sub">Sequência de operações executadas ao submeter uma descrição.</div>', unsafe_allow_html=True)
        st.markdown("""
        <div class="pipeline-flow">
            <div class="pipeline-step">
                <div class="pipeline-step-num">Etapa 01</div>
                <div class="pipeline-step-label">Entrada</div>
                <div class="pipeline-step-desc">Texto livre em português</div>
            </div>
            <div class="pipeline-arrow">›</div>
            <div class="pipeline-step">
                <div class="pipeline-step-num">Etapa 02</div>
                <div class="pipeline-step-label">Tradução</div>
                <div class="pipeline-step-desc">PT para EN (automático)</div>
            </div>
            <div class="pipeline-arrow">›</div>
            <div class="pipeline-step">
                <div class="pipeline-step-num">Etapa 03</div>
                <div class="pipeline-step-label">NLP</div>
                <div class="pipeline-step-desc">noun_phrases + POS Tagging</div>
            </div>
            <div class="pipeline-arrow">›</div>
            <div class="pipeline-step">
                <div class="pipeline-step-num">Etapa 04</div>
                <div class="pipeline-step-label">Validação MeSH</div>
                <div class="pipeline-step-desc">API NLM — Bethesda, MD</div>
            </div>
            <div class="pipeline-arrow">›</div>
            <div class="pipeline-step">
                <div class="pipeline-step-num">Etapa 05</div>
                <div class="pipeline-step-label">Curadoria</div>
                <div class="pipeline-step-desc">Revisão pelo pesquisador</div>
            </div>
            <div class="pipeline-arrow">›</div>
            <div class="pipeline-step">
                <div class="pipeline-step-num">Etapa 06</div>
                <div class="pipeline-step-label">Boolean String</div>
                <div class="pipeline-step-desc">MeSH Terms + tiab + AND/OR</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)


# ════════════════════════════════════════════
#  TAB 2 — Ajuda e Tutorial
# ════════════════════════════════════════════
with tab_help:
    col_left, col_right = st.columns([1, 1], gap="large")

    with col_left:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">Como usar</div>', unsafe_allow_html=True)

        for num, title, body in [
            ("1", "Descreva em português",
             'Escreva sua pergunta de pesquisa como falaria com seu orientador. '
             'Ex.: <em>"prevalência de depressão na doença de Parkinson"</em>'),
            ("2", "Aguarde o pipeline",
             "O sistema traduz automaticamente, extrai os conceitos via NLP "
             "e consulta a API da NLM para validar cada descritor no vocabulário MeSH."),
            ("3", "Revise os conceitos",
             "Descritores confirmados no MeSH aparecem marcados como tal. "
             "Desmarque qualquer termo que represente ruído antes de gerar a string."),
            ("4", "Use no PubMed",
             'Cole a string em <a href="https://pubmed.ncbi.nlm.nih.gov/advanced/" target="_blank">'
             "pubmed.ncbi.nlm.nih.gov/advanced</a> e clique em <em>Search</em>."),
        ]:
            st.markdown(
                f'<div class="step-row">'
                f'<div class="step-n">{num}</div>'
                f'<div class="step-body"><strong>{title}</strong><br>{body}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">Exemplos de Entrada</div>', unsafe_allow_html=True)
        for area, ex in [
            ("Cardiologia",    "mortalidade por insuficiência cardíaca em idosos"),
            ("Pneumologia",    "ventilação mecânica em pacientes com DPOC"),
            ("Neurologia",     "prevalência de depressão na doença de Parkinson"),
            ("Endocrinologia", "resistência à insulina em diabéticos tipo 2"),
            ("Saúde Local",    "prevalência de hipertensão em adultos em Vassouras"),
        ]:
            st.markdown(
                f'<div style="padding:0.65rem 0;border-bottom:1px solid #EDF2F7;">'
                f'<div style="font-size:0.68rem;font-weight:600;letter-spacing:1px;'
                f'text-transform:uppercase;color:#718096;margin-bottom:0.2rem;">{area}</div>'
                f'<div style="font-size:0.88rem;color:#1a202c;font-style:italic;">"{ex}"</div>'
                f'</div>',
                unsafe_allow_html=True,
            )
        st.markdown('</div>', unsafe_allow_html=True)

    with col_right:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">Glossário</div>', unsafe_allow_html=True)
        for term, defn in [
            ("[MeSH Terms]",
             "Medical Subject Headings — vocabulário controlado da NLM/NIH. "
             "Todo artigo do PubMed recebe descritores MeSH independentemente do idioma de publicação."),
            ("[tiab]",
             "Title/Abstract — busca o termo no título e no resumo. "
             "Captura artigos recentes ainda não indexados pelo MeSH."),
            ("AND",
             "Interseção booleana. O artigo deve abordar todos os conceitos simultaneamente. "
             "Define o escopo e aumenta a especificidade da busca."),
            ("OR",
             "União booleana. Aceita qualquer forma de indexação do mesmo conceito. "
             "Aumenta a cobertura sem excluir artigos relevantes."),
            ("noun_phrases",
             "Frases nominais detectadas pelo TextBlob. "
             "Preservam termos compostos como 'Mechanical Ventilation' como uma unidade única."),
            ("POS Tagging",
             "Classificação morfossintática. Apenas substantivos (NN), adjetivos (JJ) "
             "e particípios qualificadores (VBN) são aceitos na string final."),
            ("Curadoria",
             "Etapa de revisão humana. O pesquisador valida ou descarta os conceitos "
             "extraídos antes da geração da string definitiva."),
        ]:
            st.markdown(
                f'<div class="gloss-item">'
                f'<div class="gloss-term">{term}</div>'
                f'<div class="gloss-def">{defn}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">Sensibilidade e Especificidade</div>', unsafe_allow_html=True)
        st.markdown("""
        <table style="width:100%;border-collapse:collapse;font-size:0.85rem;">
            <thead>
                <tr style="border-bottom:2px solid #E2E8F0;">
                    <th style="padding:0.5rem 0.6rem;text-align:left;color:#0A1628;font-weight:600;">Estratégia</th>
                    <th style="padding:0.5rem 0.6rem;text-align:center;color:#0A1628;font-weight:600;">Volume</th>
                    <th style="padding:0.5rem 0.6rem;text-align:left;color:#0A1628;font-weight:600;">Indicação</th>
                </tr>
            </thead>
            <tbody>
                <tr style="border-bottom:1px solid #EDF2F7;">
                    <td style="padding:0.55rem 0.6rem;"><code style="font-size:0.8rem;background:#F7FAFC;padding:0.1rem 0.3rem;border-radius:3px;border:1px solid #E2E8F0;">Apenas [MeSH]</code></td>
                    <td style="padding:0.55rem 0.6rem;text-align:center;color:#4a5568;">Menor</td>
                    <td style="padding:0.55rem 0.6rem;color:#4a5568;">Alta precisão</td>
                </tr>
                <tr style="border-bottom:1px solid #EDF2F7;background:#FAFAFA;">
                    <td style="padding:0.55rem 0.6rem;"><code style="font-size:0.8rem;background:#F7FAFC;padding:0.1rem 0.3rem;border-radius:3px;border:1px solid #E2E8F0;">[MeSH] OR [tiab]</code></td>
                    <td style="padding:0.55rem 0.6rem;text-align:center;color:#4a5568;">Equilibrado</td>
                    <td style="padding:0.55rem 0.6rem;color:#4a5568;">Uso geral</td>
                </tr>
                <tr>
                    <td style="padding:0.55rem 0.6rem;"><code style="font-size:0.8rem;background:#F7FAFC;padding:0.1rem 0.3rem;border-radius:3px;border:1px solid #E2E8F0;">Apenas [tiab]</code></td>
                    <td style="padding:0.55rem 0.6rem;text-align:center;color:#4a5568;">Maior</td>
                    <td style="padding:0.55rem 0.6rem;color:#4a5568;">Revisão sistemática</td>
                </tr>
            </tbody>
        </table>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
