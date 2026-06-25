import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
from fpdf import FPDF

# Configuración y Estados
if "equipos" not in st.session_state: st.session_state["equipos"] = []
if "materiales" not in st.session_state: st.session_state["materiales"] = []
if "mano_obra" not in st.session_state: st.session_state["mano_obra"] = []

st.set_page_config(page_title="Alfa Security - Cotizador", layout="wide")
st.title("🛡️ Sistema Alfa Security")
MARGEN = 0.40

tab1, tab2, tab3, tab4 = st.tabs(["📦 Equipos", "🔍 Materiales", "🛠️ Mano de Obra", "📊 Liquidación Interna / PDF"])

# --- PESTAÑAS 1, 2 Y 3 ---
# (Mantén la lógica de ingreso que ya tenías para equipos y materiales)

with tab3:
    st.subheader("Mano de Obra y Viáticos")
    col1, col2 = st.columns(2)
    with col1:
        with st.form("form_obra"):
            rol = st.selectbox("Técnico", ["Instalador", "Configurador"])
            tarifa = st.number_input("Tarifa Diaria ($)", value=50.0)
            dias = st.number_input("Días", value=1)
            btn = st.form_submit_button("Agregar")
            if btn:
                st.session_state["mano_obra"].append({"Rol": rol, "Costo": tarifa * dias})
    with col2:
        kms = st.number_input("Kilómetros totales (Ida y vuelta)", value=0)
        costo_combustible = kms * 0.36
        st.metric("Costo Combustible", f"${costo_combustible:,.2f}")

# --- PESTAÑA 4: DIVISIÓN ---
with tab4:
    # CÁLCULOS
    c_equipos = sum(x["Costo Total"] for x in st.session_state["equipos"])
    c_mat = sum(x["Costo Total"] for x in st.session_state["materiales"])
    c_mo = sum(x["Costo"] for x in st.session_state["mano_obra"]) + costo_combustible
    
    v_equipos = sum(x["Precio Venta Total"] for x in st.session_state["equipos"])
    v_mat = sum(x["Precio Venta Total"] for x in st.session_state["materiales"])
    v_mo = (c_mo / (1 - MARGEN))

    st.subheader("📊 Panel de Liquidación Interna (Tú ves esto)")
    col_a, col_b, col_c = st.columns(3)
    col_a.metric("Costo Total", f"${(c_equipos + c_mat + c_mo):,.2f}")
    col_b.metric("Venta Total", f"${(v_equipos + v_mat + v_mo):,.2f}")
    col_c.metric("Utilidad Bruta", f"${(v_equipos + v_mat + v_mo) - (c_equipos + c_mat + c_mo):,.2f}")

    st.markdown("---")
    st.subheader("📄 Generación de PDF (Cliente ve esto)")
    
    def generar_pdf():
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(0, 10, "Cotización Alfa Security", 0, 1, 'C')
        pdf.set_font("Arial", '', 12)
        pdf.cell(0, 10, f"Suministro Equipos: ${v_equipos:,.2f}", 0, 1)
        pdf.cell(0, 10, f"Materiales e Instalación: ${v_mat + v_mo:,.2f}", 0, 1)
        pdf.ln(10)
        pdf.cell(0, 10, f"TOTAL: ${((v_equipos + v_mat + v_mo) * 1.13):,.2f}", 0, 1)
        return pdf.output(dest='S').encode('latin-1')

    if st.button("Descargar PDF para Cliente"):
        st.download_button("Descargar", data=generar_pdf(), file_name="cotizacion.pdf")
