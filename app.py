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

# Diccionario de Departamentos Oficiales de Freund
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
        respuesta = requests.get(url_departamento, headers=headers, timeout=7)
        if respuesta.status_code == 200:
            soup = BeautifulSoup(respuesta.text, "html.parser")
            tarjetas = soup.find_all("div", class_="product-block") or soup.find_all("div", class_="item") or soup.find_all("div", class_="product-item")
            
            for t in tarjetas:
                titulo_elem = t.find("h3") or t.find("a", class_="product-item-link") or t.find("div", class_="name")
                precio_elem = t.find("span", class_="price") or t.find("div", class_="price")
                
                if titulo_elem and precio_elem:
                    nombre = titulo_elem.text.strip()
                    precio_texto = precio_elem.text.replace("$", "").replace(",", "").strip()
                    
                    try:
                        precio = float(precio_texto)
                    except:
                        precio = 0.0
                    
                    if not termino_busqueda or termino_busqueda.lower() in nombre.lower():
                        resultados.append({
                            "sku": "F-" + str(len(resultados) + 101),
                            "name": nombre.upper(),
                            "price": precio
                        })
    except:
        pass
        
    # RESPALDO AUTOMÁTICO INTEGRADO (Por si el firewall bloquea la IP de Streamlit)
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
            precio_venta_u = costo_eq / (1 - margen_decimal) if margen_decimal < 1 else costo_eq
            
            st.session_state["equipos"].append({
                "Borrar": False,
                "Descripción": desc_eq,
                "Cantidad": int(cant_eq),
                "Costo Unitario ($)": float(costo_eq),
                "Costo Total ($)": float(costo_eq * cant_eq),
                "Rentabilidad (%)": float(rent_inicial),
                "Precio Venta U ($)": float(precio_venta_u),
                "Precio Venta Total ($)": float(precio_venta_u * cant_eq)
            })
            st.success(f"Agregado: {desc_eq}")

    if st.session_state["equipos"]:
        st.markdown("#### 📊 Lista de Equipos Cargados")
        df_original = pd.DataFrame(st.session_state["equipos"])
        
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
        
        for i in range(len(df_editado)):
            r_pct = df_editado.at[i, "Rentabilidad (%)"] / 100.0
            c_uni = df_editado.at[i, "Costo Unitario ($)"]
            cant = df_editado.at[i, "Cantidad"]
            
            df_editado.at[i, "Costo Total ($)"] = c_uni * cant
            p_venta_u = c_uni / (1 - r_pct) if r_pct < 1 else c_uni
            df_editado.at[i, "Precio Venta U ($)"] = p_venta_u
            df_editado.at[i, "Precio Venta Total ($)"] = p_venta_u * cant

        st.session_state["equipos"] = df_editado.to_dict(orient="records")
        
        total_costo_interno_eq = sum(x["Costo Total ($)"] for x in st.session_state["equipos"])
        total_venta_eq = sum(x["Precio Venta Total ($)"] for x in st.session_state["equipos"])
        
        st.markdown(" ")
        ceq1, ceq2 = st.columns(2)
        ceq1.metric("Costo Interno Total (Equipos)", f"${total_costo_interno_eq:,.2f}")
        ceq2.metric("Precio de Venta Total (Equipos)", f"${total_venta_eq:,.2f}")
        
        st.markdown("---")
        col_btn1, col_btn2 = st.columns([3, 10])
        
        if col_btn1.button("🗑️ Aplicar Eliminación de Marcados", key="del_eq"):
            st.session_state["equipos"] = [eq for eq in st.session_state["equipos"] if not eq["Borrar"]]
            st.success("Equipos eliminados correctamente.")
            st.rerun()
                
        if col_btn2.button("Limpiar Toda la Lista", key="btn_clear_eq"):
            st.session_state["equipos"] = []
            st.rerun()

# ==========================================
# --- PESTAÑA 2: BUSCADOR FREUND ---
# ==========================================
with tab2:
    st.subheader("🔍 Extractor de Catálogo en Vivo — Ferretería Freund El Salvador")
    st.caption("Selecciona un departamento de canalización o materiales eléctricos para realizar la búsqueda dirigida.")
    
    col_dep, col_text = st.columns([2, 3])
    dept_seleccionado = col_dep.selectbox("Seleccionar Departamento Técnico", list(DEPARTAMENTOS_FREUND.keys()))
    buscar_termino = col_text.text_input("¿Qué material o palabra clave buscas? (O déjalo vacío para ver todo)", placeholder="Ej. tuberia emt, union, cable...")
    
    url_final = DEPARTAMENTOS_FREUND[dept_seleccionado]
    
    if st.button("🚀 Buscar Insumos en Freund"):
        with st.spinner("Conectando con el servidor de Freund..."):
            coincidencias = buscar_en_freund(url_final, buscar_termino)
            
            if coincidencias:
                st.markdown(f"#### 📊 Materiales encontrados en el pasillo ({len(coincidencias)})")
                for i, m in enumerate(coincidencias):
                    with st.container():
                        c_card1, c_card2, c_card3 = st.columns([4, 1, 2])
                        c_card1.markdown(f"**{m['name']}** \n`SKU: {m['sku']}`")
                        c_card2.markdown(f"#### ${m['price']:.2f}")
                        cant_m = c_card3.number_input("Cant.", min_value=1, value=1, step=1, key=f"f_cant_{i}")
                        
                        if c_card3.button("📥 Agregar al Costeo", key=f"f_btn_{i}"):
                            p_v = m['price'] / (1 - 0.40)
                            st.session_state["materiales"].append({
                                "Borrar": False,
                                "Descripción": m['name'],
                                "Cantidad": int(cant_m),
                                "Costo Unitario ($)": float(m['price']),
                                "Costo Total ($)": float(m['price'] * cant_m),
                                "Rentabilidad (%)": 40.0,
                                "Precio Venta U ($)": float(p_v),
                                "Precio Venta Total ($)": float(p_v * cant_m)
                            })
                            st.toast(f"Agregado: {m['name']}")
                        st.markdown("---")
            else:
                st.warning("No se encontraron coincidencias para esa palabra clave en este departamento.")

    if st.session_state["materiales"]:
        st.markdown("### 🛒 Materiales y Suministros Cargados en esta Cotización")
        df_mat_orig = pd.DataFrame(st.session_state["materiales"])
        df_mat_edit = st.data_editor(
            df_mat_orig,
            hide_index=True,
            use_container_width=True,
            disabled=["Descripción", "Costo Unitario ($)", "Costo Total ($)", "Precio Venta U ($)", "Precio Venta Total ($)"],
            column_config={
                "Borrar": st.column_config.CheckboxColumn("Borrar", default=False),
                "Cantidad": st.column_config.NumberColumn("Cantidad", min_value=1, step=1),
                "Rentabilidad (%)": st.column_config.NumberColumn("Rentabilidad (%)", min_value=0, max_value=99, step=1),
            }
        )
        for i in range(len(df_mat_edit)):
            r_pct = df_mat_edit.at[i, "Rentabilidad (%)"] / 100.0
            c_uni = df_mat_edit.at[i, "Costo Unitario ($)"]
            cant = df_mat_edit.at[i, "Cantidad"]
            
            df_mat_edit.at[i, "Costo Total ($)"] = c_uni * cant
            p_venta_u = c_uni / (1 - r_pct) if r_pct < 1 else c_uni
            df_mat_edit.at[i, "Precio Venta U ($)"] = p_venta_u
            df_mat_edit.at[i, "Precio Venta Total ($)"] = p_venta_u * cant
            
        st.session_state["materiales"] = df_mat_edit.to_dict(orient="records")
        
        if st.button("🗑️ Eliminar Materiales Seleccionados", key="del_mat"):
            st.session_state["materiales"] = [m for m in st.session_state["materiales"] if not m["Borrar"]]
            st.rerun()

# ==========================================
# --- PESTAÑA 3: MANO DE OBRA ---
# ==========================================
with tab3:
    st.subheader("🛠️ Presupuesto de Mano de Obra, Viáticos y Herramientas")
    col_izq, col_der = st.columns([1, 1])

    with col_izq:
        st.markdown("#### ⚙️ 1. Personal Técnico y Logística")
        rent_mo = st.number_input("Rentabilidad Comercial por Defecto (%)", min_value=0.0, max_value=99.0, value=20.0, step=5.0, key="rent_mo_p3")

        with st.form("form_mano_obra_completo"):
            st.markdown("**Carga de Personal:**")
            c1, c2 = st.columns(2)
            cant_conf = c1.number_input("Cantidad Configuradores", min_value=0, value=0)
            dias_conf = c2.number_input("Días Configurador", min_value=0, value=0)
            tarifa_conf = st.number_input("Costo Diario Configurador ($)", min_value=0.0, value=50.0)
            
            st.markdown("---")
            c3, c4 = st.columns(2)
            cant_inst = c3.number_input("Cantidad Instaladores", min_value=0, value=0)
            dias_inst = c4.number_input("Días Instalador", min_value=0, value=0)
            tarifa
