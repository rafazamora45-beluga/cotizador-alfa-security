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
proyecto = st.sidebar.text_input("Nombre del Proyecto", "Proyecto Procaps El Salvador")
empresa = st.sidebar.text_input("Empresa", "Alfa Security")
atencion = st.sidebar.text_input("Atención a:", "Ing. Miguel Melendez")
validez = st.sidebar.text_input("Validez de la Oferta", "15 Días")
pago = st.sidebar.text_input("Condiciones de Pago", "60% Anticipo / 40% Contraentrega")

# PESTAÑAS PRINCIPALES DE LA INTERFAZ
tab1, tab2, tab3, tab4 = st.tabs([
    "📦 Equipos Principales", 
    "🔍 Buscador Freund (Materiales)", 
    "🛠️ Mano de Obra", 
    "📊 Resumen Comercial y Liquidación"
])

# --- PESTAÑA 1: EQUIPOS PRINCIPALES (TABLA INTERACTIVA EDITABLE Y BORRABLE) ---
with tab1:
    st.subheader("Componentes y Equipos de Seguridad Electrónica")
    st.info("Ingresa los equipos principales. Podrás ajustar la rentabilidad directamente en la tabla de abajo.")
    
    with st.form("form_equipos"):
        col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
        desc_eq = col1.text_input("Descripción del Equipo", placeholder="Ej. Panel de Incendio Honeywell 1 SLC")
        cant_eq = col2.number_input("Cantidad", min_value=1, value=1, step=1)
        costo_eq = col3.number_input("Costo Unitario ($)", min_value=0.0, value=0.0, step=10.0)
        # Rentabilidad inicial sugerida (40%)
        rent_inicial = col4.number_input("Rentabilidad Inicial (%)", min_value=0.0, max_value=99.0, value=40.0, step=5.0)
        
        btn_eq = st.form_submit_button("Agregar Equipo")
        
        if btn_eq and desc_eq:
            margen_decimal = rent_inicial / 100.0
            precio_venta_u = costo_eq / (1 - margen_decimal) if margen_decimal < 1 else costo_eq
            
            st.session_state["equipos"].append({
                "Borrar": False,
                "Descripción": desc_eq,
                "Cantidad": cant_eq,
                "Costo Unitario ($)": float(costo_eq),
                "Costo Total ($)": float(costo_eq * cant_eq),
                "Rentabilidad (%)": float(rent_inicial),
                "Precio Venta U ($)": float(precio_venta_u),
                "Precio Venta Total ($)": float(precio_venta_u * cant_eq)
            })
            st.success(f"Agregado: {desc_eq}")

    # SECCIÓN DE LA TABLA COMPLETA
    if st.session_state["equipos"]:
        st.markdown("#### 📊 Lista de Equipos Cargados")
        st.caption("Tip: Puedes editar la 'Rentabilidad (%)' o la 'Cantidad' directamente en la celda. Marca 'Borrar' y presiona el botón inferior si deseas quitar un equipo.")
        
        # Convertimos la lista de memoria a un DataFrame de Pandas
        df_original = pd.DataFrame(st.session_state["equipos"])
        
        # Usamos st.data_editor para renderizar una tabla verdaderamente interactiva
        df_editado = st.data_editor(
            df_original,
            hide_index=True,
            use_container_width=True,
            disabled=["Descripción", "Costo Unitario ($)", "Costo Total ($)", "Precio Venta U ($)", "Precio Venta Total ($)"],
            column_config={
                "Borrar": st.column_config.CheckboxColumn("Seleccionar para Borrar", default=False),
                "Cantidad": st.column_config.NumberColumn("Cantidad", min_value=1, step=1),
                "Rentabilidad (%)": st.column_config.NumberColumn("Rentabilidad (%)", min_value=0, max_value=99, step=1),
                "Costo Unitario ($)": st.column_config.NumberColumn(format="$%.2f"),
                "Costo Total ($)": st.column_config.NumberColumn(format="$%.2f"),
                "Precio Venta U ($)": st.column_config.NumberColumn(format="$%.2f"),
                "Precio Venta Total ($)": st.column_config.NumberColumn(format="$%.2f"),
            }
        )
        
        # Recalcular automáticamente si el usuario editó cantidades o rentabilidades en la tabla
        for i in range(len(df_editado)):
            r_pct = df_editado.at[i, "Rentabilidad (%)"] / 100.0
            c_uni = df_editado.at[i, "Costo Unitario ($)"]
            cant = df_editado.at[i, "Cantidad"]
            
            # Re-calculamos fórmulas financieras sobre la marcha
            df_editado.at[i, "Costo Total ($)"] = c_uni * cant
            p_venta_u = c_uni / (1 - r_pct) if r_pct < 1 else c_uni
            df_editado.at[i, "Precio Venta U ($)"] = p_venta_u
            df_editado.at[i, "Precio Venta Total ($)"] = p_venta_u * cant

        # Sincronizamos los cambios de vuelta a la memoria interna de la sesión
        st.session_state["equipos"] = df_editado.to_dict(orient="records")
        
        # Acciones de limpieza de la tabla
        st.markdown(" ")
        col_btn1, col_btn2 = st.columns([3, 10])
        
        if col_btn1.button("🗑️ Aplicar Eliminación de Marcados"):
            # Filtramos dejando únicamente los equipos que NO tengan la casilla 'Borrar' activa
            equipos_restantes = [eq for eq in st.session_state["equipos"] if not eq["Borrar"]]
            if len(equipos_restantes) < len(st.session_state["equipos"]):
                st.session_state["equipos"] = equipos_restantes
                st.success("Los equipos seleccionados han sido removidos.")
                st.rerun()
            else:
                st.warning("No has marcado ninguna casilla en la columna 'Borrar'.")
                
        if col_btn2.button("Limpiar Toda la Lista", key="btn_clear_eq"):
            st.session_state["equipos"] = []
            st.rerun()
