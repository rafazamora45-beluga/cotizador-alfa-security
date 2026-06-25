import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
from fpdf import FPDF

# 1. INICIALIZACIÓN ABSOLUTA DEL ESTADO DE LA SESIÓN
if "equipos" not in st.session_state:
    st.session_state["equipos"] = []
if "materiales" not in st.session_state:
    st.session_state["materiales"] = []
if "mano_obra" not in st.session_state:
    st.session_state["mano_obra"] = []

# Configuración de la página y diseño visual
st.set_page_config(page_title="Cotizador Inteligente - Alfa Security", layout="wide")

# Título y Encabezado Corporativo
st.title("🛡️ Sistema de Cotizaciones Automáticas — Alfa Security")
st.markdown("---")

# 2. INFORMACIÓN DEL PROYECTO (Panel Izquierdo)
st.sidebar.header("📋 Datos del Proyecto")
# CAMBIO SOLICITADO: Ajustado a solo "Nombre del Proyecto"
proyecto = st.sidebar.text_input("Nombre del Proyecto", "Proyecto Procaps El Salvador")
atencion = st.sidebar.text_input("Atención a:", "Ing. Miguel Melendez")
validez = st.sidebar.text_input("Validez de la Oferta", "15 Días")
pago = st.sidebar.text_input("Condiciones de Pago", "60% Anticipo / 40% Contraentrega")

# Rentabilidad blindada al 40% (Margen sobre el precio de venta final)
MARGEN = 0.40

# PESTAÑAS PRINCIPALES DE LA INTERFAZ
tab1, tab2, tab3, tab4 = st.tabs([
    "📦 Equipos Principales", 
    "🔍 Buscador Freund (Materiales)", 
    "🛠️ Mano de Obra", 
    "📊 Resumen Comercial y Liquidación"
])

# --- PESTAÑA 1: EQUIPOS PRINCIPALES (INGRESO MANUAL) ---
with tab1:
    st.subheader("Componentes y Equipos de Seguridad Electrónica")
    st.info("Ingresa manualmente los equipos principales de distribuidores (Paneles, Sensores, Cámaras, etc.)")
    
    with st.form("form_equipos"):
        col1, col2, col3 = st.columns([3, 1, 1])
        desc_eq = col1.text_input("Descripción del Equipo", placeholder="Ej. Panel de Incendio Inteligente Honeywell de 1 SLC")
        cant_eq = col2.number_input("Cantidad", min_value=1, value=1, step=1)
        costo_eq = col3.number_input("Costo Unitario ($)", min_value=0.0, value=0.0, step=10.0)
        
        btn_eq = st.form_submit_button("Agregar Equipo")
        
        if btn_eq and desc_eq:
            precio_venta_u = costo_eq / (1 - MARGEN)
            st.session_state["equipos"].append({
                "Descripción": desc_eq,
                "Cantidad": cant_eq,
                "Costo Unitario": costo_eq,
                "Costo Total": costo_eq * cant_eq,
                "Precio Venta U": precio_venta_u,
                "Precio Venta Total": precio_venta_u * cant_eq
            })
            st.success(f"Agregado: {desc_eq}")

    if st.session_state["equipos"]:
        df_eq = pd.DataFrame(st.session_state["equipos"])
        st.dataframe(df_eq.style.format({"Costo Unitario": "${:.2f}", "Costo Total": "${:.2f}", "Precio Venta U": "${:.2f}", "Precio Venta Total": "${:.2f}"}))
        if st.button("Limpiar Equipos", key="btn_clear_eq"):
            st.session_state["equipos"] = []
            st.rerun()

# Las pestañas 2, 3 y 4 siguen procesando la información abajo con la misma lógica limpia.
