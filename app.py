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
# CORREGIDO: Se mantiene el Nombre del Proyecto y se reincorpora la Empresa
proyecto = st.sidebar.text_input("Nombre del Proyecto", "Proyecto Procaps El Salvador")
empresa = st.sidebar.text_input("Empresa", "Alfa Security")
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

# --- PESTAÑA 1: EQUIPOS PRINCIPALES (INGRESO MANUAL Y ELIMINACIÓN) ---
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

    # SECCIÓN NUEVA: Visualización y eliminación selectiva
    if st.session_state["equipos"]:
        st.markdown("#### Lista de Equipos Cargados")
        st.write("Si te equivocaste, marca la casilla del equipo y presiona 'Eliminar Equipos Seleccionados'.")
        
        # Creamos una lista temporal para guardar cuáles quiere borrar el usuario
        equipos_a_eliminar = []
        
        # Encabezados de la tabla manual con columnas de acción
        col_check, col_info = st.columns([1, 12])
        
        for i, eq in enumerate(st.session_state["equipos"]):
            col_sel, col_det = st.columns([1, 12])
            # Casilla de verificación individual para cada equipo usando su índice
            marcado = col_sel.checkbox("", key=f"del_eq_{i}")
            if marcado:
                equipos_a_eliminar.append(i)
                
            # Mostramos los datos de manera ordenada en formato de texto formateado
            col_det.markdown(
                f"**{eq['Descripción']}** | Cantidad: {eq['Cantidad']} | "
                f"Costo U: ${eq['Costo Unitario']:.2f} | Costo Total: ${eq['Costo Total']:.2f} | "
                f"Precio Venta U: ${eq['Precio Venta U']:.2f} | Venta Total: ${eq['Precio Venta Total']:.2f}"
            )
        
        st.markdown(" ")
        col_btn1, col_btn2 = st.columns([3, 10])
        
        # Botón para borrar selectivamente los marcados
        if col_btn1.button("🗑️ Eliminar Equipos Seleccionados", type="secondary"):
            if equipos_a_eliminar:
                # Borramos de atrás hacia adelante para no arruinar los índices de la lista original
                for indice in sorted(equipos_a_eliminar, reverse=True):
                    st.session_state["equipos"].pop(indice)
                st.success("Equipos seleccionados eliminados correctamente.")
                st.rerun()
            else:
                st.warning("Por favor, selecciona al menos una casilla para eliminar.")
                
        # Botón original para limpiar todo de un solo click
        if col_btn2.button("Limpiar Toda la Lista", key="btn_clear_eq"):
            st.session_state["equipos"] = []
            st.rerun()
