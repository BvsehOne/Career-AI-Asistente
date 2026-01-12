import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup
from pypdf import PdfReader
from docx import Document

# --- 1. CONFIGURACIÓN Y ESTILO AGRESIVO ---
load_dotenv()
st.set_page_config(page_title="Career AI - Camilo Godoy", layout="wide", page_icon="💼")

# --- CSS PROFESIONAL FORZADO ---
st.markdown("""
<style>
    /* 1. Fondo principal con imagen de oficina desenfocada */
    .stApp {
        background-image: url("https://images.unsplash.com/photo-1497215728101-856f4ea42174?q=80&w=2070&auto=format&fit=crop");
        background-size: cover;
        background-attachment: fixed;
    }
    
    /* 2. Capa blanca semitransparente sobre el fondo para leer bien */
    .stApp::before {
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-color: rgba(255, 255, 255, 0.85); /* 85% blanco */
        z-index: -1;
    }

    /* 3. Contenedores de inputs con sombra suave */
    div[data-testid="stVerticalBlock"] > div {
        background-color: rgba(255, 255, 255, 0.8);
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        backdrop-filter: blur(5px);
    }
    
    /* 4. Títulos color azul corporativo */
    h1, h2, h3 {
        color: #0f172a !important;
        text-shadow: 2px 2px 4px rgba(255,255,255,1);
    }
    
    /* 5. Botones con gradiente */
    div.stButton > button {
        background: linear-gradient(90deg, #2563EB 0%, #1D4ED8 100%);
        color: white;
        border: none;
        padding: 15px 32px;
        font-size: 18px;
        border-radius: 10px;
        transition: transform 0.2s;
    }
    div.stButton > button:hover {
        transform: scale(1.05);
    }
</style>
""", unsafe_allow_html=True)

# Configurar API
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    st.error("⚠️ Error: Falta la API KEY.")
    st.stop()

genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-2.5-flash')

# --- 2. FUNCIONES DE LECTURA ---
def leer_pdf(archivo):
    try:
        reader = PdfReader(archivo)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text
    except:
        return "Error leyendo PDF."

def leer_docx(archivo):
    try:
        doc = Document(archivo)
        return "\n".join([para.text for para in doc.paragraphs])
    except:
        return "Error leyendo Word."

def leer_web(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        for tag in soup(["script", "style", "nav", "footer", "header"]):
            tag.decompose()
        return soup.get_text(separator=' ', strip=True)
    except Exception as e:
        return f"Error leyendo web: {str(e)}"

# --- 3. INTERFAZ DE USUARIO ---

st.title("💼 Career AI: Tu Asistente de Contratación")
st.markdown("### Prepara tu postulación y entrevista con Inteligencia Artificial")

# SECCIÓN DE DATOS (Arriba para que sirva a ambas pestañas)
with st.container():
    col1, col2 = st.columns(2)
    with col1:
        st.info("🔗 Paso 1: La Oferta de Trabajo")
        url_oferta = st.text_input("Pega el enlace (URL) del empleo aquí:")
    
    with col2:
        st.info("📄 Paso 2: Tu Currículum")
        archivo_cv = st.file_uploader("Sube tu CV (PDF/Word)", type=["pdf", "docx"])

# Procesar los datos una sola vez
texto_oferta = ""
texto_cv = ""

if url_oferta:
    with st.spinner("Leyendo sitio web..."):
        texto_oferta = leer_web(url_oferta)

if archivo_cv:
    if archivo_cv.name.endswith(".pdf"):
        texto_cv = leer_pdf(archivo_cv)
    elif archivo_cv.name.endswith(".docx"):
        texto_cv = leer_docx(archivo_cv)

st.divider()

# --- 4. SISTEMA DE PESTAÑAS (La Innovación) ---
tab1, tab2 = st.tabs(["🕵️ Analizar Compatibilidad (ATS)", "🎤 Simulador de Entrevista"])

# --- PESTAÑA 1: ANALIZADOR ---
with tab1:
    st.header("Análisis de Brechas y CV")
    if st.button("🚀 Analizar mi Perfil", type="primary"):
        if texto_oferta and texto_cv and "Error" not in texto_oferta:
            prompt_ats = f"""
            Actúa como un reclutador experto. Analiza:
            OFERTA: "{texto_oferta[:30000]}"
            CANDIDATO: "{texto_cv[:30000]}"
            
            Dame un reporte en Markdown:
            1. % de Compatibilidad.
            2. Habilidades que faltan (Crucial).
            3. Consejos para mejorar el CV para ESTA oferta específica.
            """
            with st.spinner("Analizando compatibilidad..."):
                response = model.generate_content(prompt_ats)
                st.markdown(response.text)
        else:
            st.warning("⚠️ Faltan datos: Asegúrate de poner un link válido y subir tu CV.")

# --- PESTAÑA 2: SIMULADOR DE ENTREVISTA (NUEVO) ---
with tab2:
    st.header("Preparación para la Entrevista")
    st.write("La IA leerá la oferta y te hará las preguntas difíciles que haría el reclutador real.")
    
    if st.button("🎙️ Generar Preguntas de Entrevista"):
        if texto_oferta and "Error" not in texto_oferta:
            prompt_entrevista = f"""
            Actúa como el Gerente de Contratación para este puesto.
            
            Basado ÚNICAMENTE en esta descripción de empleo:
            "{texto_oferta[:30000]}"
            
            Genera una guía de preparación para el candidato que incluya:
            1. **3 Preguntas Técnicas Difíciles** relacionadas con las herramientas mencionadas en la oferta.
            2. **2 Preguntas Situacionales** (tipo "Cuéntame de una vez que...").
            3. **1 Pregunta Trampa** (para ver su honestidad o manejo de estrés).
            4. Para cada pregunta, dame un "Tip Pro" de qué es lo que TÚ como reclutador quieres escuchar en la respuesta.
            """
            with st.spinner("El reclutador está leyendo tu perfil..."):
                response = model.generate_content(prompt_entrevista)
                st.markdown(response.text)
        else:
            st.warning("⚠️ Necesito el Link de la oferta para saber qué preguntar.")

# Pie de página
st.markdown("---")
st.caption("Desarrollado por Angelo Olivares - Versión Prototipo v3.0")