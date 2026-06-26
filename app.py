import streamlit as st
import pandas as pd
import plotly.express as px
from fpdf import FPDF
import requests
from bs4 import BeautifulSoup
import os

# 1. INICIALIZACIÓN DE VARIABLES GLOBALES EN SESIÓN
if "equipos" not in st.session_state:
    st.session_state["equipos"] = []
if "materiales" not in st.session_state:
    st.session_state["materiales"] = []
if "servicios_mo" not in st.session_state:
    st.session_state["servicios_mo"] = []

# Configuración de página e interfaz
st.set_page_config(page_title="Cotizador Inteligente - Alfa Security", layout="wide")

st.title("🛡️ Sistema de Cotizaciones Automáticas — Alfa Security")
st.markdown("---")

# Diccionario de Departamentos Oficiales proporcionados por el usuario
DEPARTAMENTOS_FREUND = {
    "🏗️ Tubería y Ductos (Cableado)": "https://www.freundferreteria.com/categoria/TUBERIA-Y-DUCTOS-CABLEADO-ELECTRICO/productos/NVL3-149",
    "🔌 Conductores Eléctricos": "https://www.freundferreteria.com/categoria/CONDUCTORES-ELECTRICOS/productos/NVL2-37",
    "🔩 Accesorios Conductores Eléctricos": "https://www.freundferreteria.com/categoria/ACCESORIOS-CONDUCTORES-ELECTRICOS/productos/NVL3-432",
    "⚡ Material Eléctrico": "https://www.freundferreteria.com/categoria/MATERIAL-ELECTRICO/productos/NVL2-38",
    "⛓️ Alambres y Mallas": "https://www.freundferreteria.com/categoria/ALAMBRES-Y-MALLAS/productos/NVL2-27"
}

# FUNCIÓN DE WEB SCRAPING PARA FREUND
def buscar_en_freund(url_departamento, termino_busqueda):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    resultados = []
    
    try:
        # Petición HTTP al departamento seleccionado
        respuesta = requests.get(url_departamento, headers=headers, timeout=7)
        if respuesta.status_code == 200:
            soup = BeautifulSoup(respuesta.text, "html.parser")
            
            # Buscamos las tarjetas de producto según la estructura común de su plataforma de e-commerce
            tarjetas = soup.find_all("div", class_="product-block") or soup.find_all("div", class_="item") or soup.find_all("div", class_="product-item")
            
            for t in tarjetas:
                # Intentamos extraer el título y el precio usando clases estándar
                titulo_elem = t.find("h3") or t.find("a", class_="product-item-link") or t.find("div", class_="name")
                precio_elem = t.find("span", class_="price") or t.find("div", class_="price")
                
                if titulo_elem and precio_elem:
                    nombre = titulo_elem.text.strip()
                    precio_texto = precio_elem.text.replace("$", "").replace(",", "").strip()
                    
                    try:
                        precio = float(precio_texto)
                    except:
                        precio = 0.0
                    
                    # Filtramos por el término de búsqueda ingresado
                    if not termino_busqueda or termino_busqueda.lower() in nombre.lower():
                        resultados.append({
                            "sku": "F-" + str(len(resultados) + 101),
                            "name": nombre.upper(),
                            "price": precio
                        })
    except Exception as e:
        pass # Si falla el scraping en vivo, pasará a usar el respaldo
        
    # RESPALDO AUTOMÁTICO INTEGRADO (Si el raspado no arroja datos debido al firewall de la tienda)
    if not resultados:
        materiales_respaldo = [
            {"sku": "1413211", "name": "TUBO CONDUIT EMT GALVANIZADO 3/4 PLG (6MT)", "price": 4.25, "dep": "🏗️ Tubería y Ductos (Cableado)"},
            {"sku": "24847137", "name": "UNION EMT PRESION 3/4 PLG", "price": 0.95, "dep": "🏗️ Tubería y Ductos (Cableado)"},
            {"sku": "2718137", "name": "UNION TUBO EMT 3/4 PLG", "price": 0.65, "dep": "🏗️ Tubería y Ductos (Cableado)"},
            {"sku": "522421", "name": "CONECTOR RECTO EMT A CAJA 1 PLG", "price": 0.85, "dep": "🔩 Accesorios Conductores Eléctricos"},
            {"sku": "643907", "name": "ABRAZADERA 4 A 5 PLG X 1/4X1 1/2 POSTE PAR", "price": 4.25, "dep": "🔩 Accesorios Conductores Eléctricos"},
            {"sku": "CABLE-14", "name": "CABLE ELECTRICO THHN NEGRO NO. 14 AWG COMULSA", "price": 0.45, "dep": "🔌 Conductores Eléctricos"},
            {"sku": "CABLE-12", "name": "CABLE THHN ROJO NO. 12 AWG INDUSAL", "price": 0.65, "dep": "🔌 Conductores Eléctricos"},
            {"sku": "TOMA-01", "name": "TOMACORRIENTE DOBLE CON TIERRA POLARIZADO EAGLE", "price": 2.85, "dep": "⚡ Material Eléctrico"},
            {"sku": "MALLA-02", "name": "MALLA CICLONICA GALVANIZADA 2X2 PULG (1.50X20MT)", "price": 85.00, "dep": "⛓️ Alambres y Mallas"}
        ]
        # Filtramos el respaldo local por departamento y por palabra clave
        for m in materiales_respaldo:
            url_seleccionada = DEPARTAMENTOS_FREUND.get(m["dep"])
            if url_seleccionada == url_departamento:
                if not termino_busqueda or termino_busqueda.lower() in m["name"].lower():
                    resultados.append({"sku": m["sku"], "name": m["name"], "price": m["price"]})
                    
    return resultados

# 2. PANEL IZQUIERDO: LOGO Y DATOS DEL PROYECTO
ruta_logo = "LOGO_ALFA-02.png"
if os.path.exists(ruta_logo):
    st.sidebar.image(ruta_logo, use_container_width=True)
else:
    ruta_logo_min = "logo_alfa-02.png"
    if os.path.exists(ruta_logo_min):
        st.sidebar.image(ruta_logo_min, use_container_width=True)

st.sidebar.header("📋 Datos del Proyecto")
proyecto = st.sidebar.text_input("Nombre del Proyecto", "Proyecto Procaps El Salvador")
empresa = st.sidebar.text_input("Empresa", "Alfa Security")
atencion = st.sidebar.text_input("Atención a:", "Ing. Miguel Melendez")
validez = st.sidebar.text_input("Validez de la Oferta", "15 Días")
pago = st.sidebar.text_input("Condiciones de Pago", "60% Anticipo / 40% Contraentrega")

tab1, tab2, tab3, tab4 = st.tabs([
    "📦 Equipos Principales", 
    "🔍 Buscador Freund (Materiales)", 
    "🛠️ Mano de Obra", 
    "📊 Resumen Comercial"
])

# ==========================================
# --- PESTAÑA 1: EQUIPOS PRINCIPALES ---
# ==========================================
with tab1:
    st.subheader("Componentes y Equipos de Seguridad Electrónica")
    st.info("Ingresa los equipos principales. Podrás ajustar la rentabilidad directamente en la tabla de abajo.")
    
    with st.form("form_equipos"):
        col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
        desc_eq = col1.text_input("Descripción del Equipo", placeholder="Ej. Panel de Incendio Honeywell 1 SLC")
        cant_eq = col2.number_input("Cantidad", min_value=1, value=1, step=1)
        costo_eq = col3.number_input("Costo Unitario ($)", min_value=0.0, value=0.0, step=10.0)
        rent_inicial = col4.number_input("Rentabilidad Inicial (%)", min_value=0.0, max_value=99.0, value=40.0, step=5.0)
        
        btn_eq = st.form_submit_button("Agregar Equipo")
        
        if btn_eq and desc_eq:
            margen_decimal = rent_inicial / 100.0
            precio_venta_u = costo_
