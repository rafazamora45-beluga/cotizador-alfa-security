import streamlit as st
import pandas as pd
import plotly.express as px
from fpdf import FPDF
import requests
from bs4 import BeautifulSoup
import os

# Configuración de página e interfaz inicial
st.set_page_config(page_title="Cotizador Inteligente - Alfa Security", layout="wide")

# 1. INICIALIZACIÓN DE VARIABLES GLOBALES EN SESIÓN
if "equipos" not in st.session_state:
    st.session_state["equipos"] = []
if "materiales" not in st.session_state:
    st.session_state["materiales"] = []
if "servicios_mo" not in st.session_state:
    st.session_state["servicios_mo"] = []
if "coincidencias_busqueda" not in st.session_state:
    st.session_state["coincidencias_busqueda"] = []

st.title("🛡️ Sistema de Cotizaciones Automáticas — Alfa Security")
st.markdown("---")

# Diccionario de Departamentos Oficiales de Freund
DEPARTAMENTOS_FREUND = {
    "🏗️ Tubería y Ductos (Cableado)": "https://www.freundferreteria.com/categoria/TUBERIA-Y-DUCTOS-CABLEADO-ELECTRICO/productos/NVL3-149",
    "🔌 Conductores Eléctricos": "https://www.freundferreteria.com/categoria/CONDUCTORES-ELECTRICOS/productos/NVL2-37",
    "🔩 Accesorios Conductores Eléctricos": "https://www.freundferreteria.com/categoria/ACCESORIOS-CONDUCTORES-ELECTRICOS/productos/NVL3-432",
    "⚡ Material Eléctrico": "https://www.freundferreteria.com/categoria/MATERIAL-ELECTRICOS/productos/NVL2-38"
}

# =========================================================================
# CLASE PDF PARA LOGÍSTICA DE REPORTES
# =========================================================================
class PDF_Cotizacion(FPDF):
    def header(self):
        if os.path.exists("LOGO_ALFA-02.png"):
            self.image("LOGO_ALFA-02.png", 10, 8, 33)
        self.set_font("Arial", "B", 14)
        self.cell(80)
        self.cell(110, 10, "ALFA SECURITY S.A. DE C.V.", 0, 0, "R")
        self.ln(5)
        self.set_font("Arial", "", 9)
        self.cell(80)
        self.cell(110, 10, "Seguridad Electrónica e Ingeniería de Incendio", 0, 0, "R")
        self.ln(12)
        self.set_draw_color(180, 180, 180)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.set_text_color(120, 120, 120)
        self.cell(0, 10, f"Página {self.page_no()} de {{nb}} — Oferta Técnico-Comercial Alfa Security", 0, 0, "C")

# =========================================================================
# MOTOR DE EXTRACCIÓN EN TIEMPO REAL
# =========================================================================
def obtener_datos_reales_producto(url_producto):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "es-SV,es;q=0.9,en;q=0.8"
    }
    try:
        respuesta = requests.get(url_producto, headers=headers, timeout=7)
        if respuesta.status_code == 200:
            soup = BeautifulSoup(respuesta.text, "html.parser")
            
            meta_img = soup.find("meta", property="og:image")
            url_imagen = meta_img["content"] if meta_img else None
            
            meta_title = soup.find("meta", property="og:title")
            nombre_real = meta_title["content"].strip().upper() if meta_title else None
            
            precio = None
            selectores_precio = [
                ".product-info-price .price", 
                ".price-box .price",
                "[data-price-type='finalPrice'] .price",
                ".current-price",
                "span.price",
                ".product-price"
            ]
            
            for selector in selectores_precio:
                elem = soup.select_one(selector)
                if elem and elem.text:
                    texto_precio = elem.text.replace("$", "").replace(",", "").strip()
                    try:
                        precio = float(texto_precio)
                        if precio > 0:
                            break
                    except ValueError:
                        continue
            return {"name": nombre_real, "image": url_imagen, "price": precio}
    except Exception:
        pass
    return None

def buscar_en_freund(url_departamento, termino_busqueda):
    resultados = []
    materiales_verificados = [
        {"sku": "24847137", "name": "UNION CONDUIT TUBERIA 19 mm (3/4 in) ACERO GALVANIZADO EMT PRESION", "price_default": 0.95, "dep": "🏗️ Tubería y Ductos (Cableado)", "link": "https://www.freundferreteria.com/producto/UNION-EMT-PRESION-3-4-PLG/24847137", "img_default": None},
        {"sku": "1413211", "name": "TUBO CONDUIT EMT GALVANIZADO 19 mm (3/4 PLG) LONGITUD 3 METROS", "price_default": 4.25, "dep": "🏗️ Tubería y Ductos (Cableado)", "link": "https://www.freundferreteria.com/producto/TUBO-CONDUIT-EMT-GALVANIZADO-3-4-PLG--6MT-/1413211", "img_default": None},
        {"sku": "1413212", "name": "TUBO CONDUIT EMT GALVANIZADO 13 mm (1/2 PLG) LONGITUD 3 METROS", "price_default": 3.15, "dep": "🏗️ Tubería y Ductos (Cableado)", "link": "https://www.freundferreteria.com/producto/TUBO-CONDUIT-EMT-GALVANIZADO-1-2-PLG--6MT-/1413212", "img_default": None},
        {"sku": "2718137", "name": "UNION CONDUIT TUBERIA 19 MM (3/4 IN) GALVANIZADO ZINC EMT CON TORNILLO", "price_default": 0.65, "dep": "🏗️ Tubería y Ductos (Cableado)", "link": "https://www.freundferreteria.com/producto/UNION-TUBO-EMT-3-4-PLG/2718137", "img_default": None},
        {"sku": "748392", "name": "TECNO-DUCTO 19 MM (3/4 IN) CORRUGADO CABLEADO ELECTRICO PVC GRIS", "price_default": 0.85, "dep": "🏗️ Tubería y Ductos (Cableado)", "link": "https://www.freundferreteria.com/buscar?text=TECNO-DUCTO%2019", "img_default": None},
        {"sku": "748393", "name": "TECNO-DUCTO 13 MM (1/2 IN) CORRUGADO CABLEADO ELECTRICO PVC GRIS", "price_default": 0.60, "dep": "🏗️ Tubería y Ductos (Cableado)", "link": "https://www.freundferreteria.com/buscar?text=TECNO-DUCTO%2013", "img_default": None}
    ]
    
    termino = termino_busqueda.lower().strip() if termino_busqueda else ""
    for item in materiales_verificados:
        if DEPARTAMENTOS_FREUND.get(item["dep"]) == url_departamento:
            if not termino or termino in item["name"].lower() or termino in item["sku"].lower():
                datos_vivos = obtener_datos_reales_producto(item["link"])
                if datos_vivos:
                    item_final = {
                        "sku": item["sku"],
                        "name": datos_vivos["name"] if datos_vivos["name"] else item["name"],
                        "price": datos_vivos["price"] if datos_vivos["price"] else item["price_default"],
                        "link": item["link"],
                        "img": datos_vivos["image"] if datos_vivos["image"] else item["img_default"]
                    }
                else:
                    item_final = {
                        "sku": item["sku"],
                        "name": item["name"],
                        "price": item["price_default"],
                        "link": item["link"],
                        "img": item["img_default"]
                    }
                resultados.append(item_final)
    return resultados

# PANEL IZQUIERDO (SIDEBAR)
ruta_logo = "LOGO_ALFA-02.png"
if os.path.exists(ruta_logo):
    st.sidebar.image(ruta_logo, use_container_width=True)

st.sidebar.header("📋 Datos del Proyecto")
proyecto = st.sidebar.text_input("Nombre del Proyecto", "Instalación sistema de detección de incendios")
empresa = st.sidebar.text_input("Empresa", "Del Sur")
atencion = st.sidebar.text_input("Atención a:", "Rafael Zamora")
validez = st.sidebar.text_input("Validez de la Oferta", "20 días")
pago = st.sidebar.text_input("Condiciones de Pago", "60% Anticipo / 40% Contraentrega")

# Pestañas principales de Navegación
tab1, tab2, tab3, tab4 = st.tabs([
    "📦 Equipos Principales", 
    "🏗️ Materiales", 
    "🛠️ Mano de Obra", 
    "📊 Resumen Comercial"
])

# ==========================================
# --- PESTAÑA 1: EQUIPOS PRINCIPALES ---
# ==========================================
with tab1:
    st.subheader("Componentes y Equipos de Seguridad Electrónica")
    with st.form("form_equipos"):
        col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
        desc_eq = col1.text_input("Descripción del Equipo", placeholder="Ej. Panel de incendio Honeywell")
        cant_eq = col2.number_input("Cantidad", min_value=1, value=1, step=1)
        costo_eq = col3.number_input("Costo Unitario ($)", min_value=0.0, value=0.0, step=10.0)
        rent_inicial = col4.number_input("Rentabilidad Inicial (%)", min_value=0.0, max_value=99.0, value=40.0, step=5.0)
        
        btn_eq = st.form_submit_button("Agregar Equipo")
        if btn_eq and desc_eq:
            margen_decimal = rent_inicial / 100.0
            precio_venta_u = costo_eq / (1 - margen_decimal) if margen_decimal < 1 else costo_eq
            st.session_state["equipos"].append({
                "Borrar": False, "Descripción": desc_eq.upper(), "Cantidad": int(cant_eq),
                "Costo Unitario ($)": float(costo_eq), "Costo Total ($)": float(costo_eq * cant_eq),
                "Rentabilidad (%)": float(rent_inicial), "Precio Venta U ($)": float(precio_venta_u),
                "Precio Venta Total ($)": float(precio_venta_u * cant_eq)
            })
            st.toast(f"Agregado: {desc_eq.upper()}")

    if st.session_state["equipos"]:
        df_original = pd.DataFrame(st.session_state["equipos"])
        df_editado = st.data_editor(
            df_original, hide_index=True, use_container_width=True,
            disabled=["Descripción", "Costo Unitario ($)", "Costo Total ($)", "Precio Venta U ($)", "Precio Venta Total ($)"],
            column_config={
                "Borrar": st.column_config.CheckboxColumn("Seleccionar para Borrar", default=False),
                "Cantidad": st.column_config.NumberColumn("Cantidad", min_value=1, step=1),
                "Rentabilidad (%)": st.column_config.NumberColumn("Rentabilidad (%)", min_value=0, max_value=99, step=1),
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
        
        col_btn1, col_btn2 = st.columns([3, 10])
        if col_btn1.button("🗑️ Aplicar Eliminación de Marcados", key="del_eq"):
            st.session_state["equipos"] = [eq for eq in st.session_state["equipos"] if not eq["Borrar"]]
            st.rerun()
        if col_btn2.button("Limpiar Toda la Lista", key="btn_clear_eq"):
            st.session_state["equipos"] = []
            st.rerun()

# ==========================================
# --- PESTAÑA 2: MATERIALES ---
# ==========================================
with tab2:
    st.subheader("🔍 Extractor de Catálogo — Ferreterías Freund El Salvador")
    col_busc, col_manu = st.columns([5, 4])
    
    with col_busc:
        st.markdown("##### 🔍 Buscador de Catálogo")
        col_dep, col_text = st.columns([2, 3])
        dept_seleccionado = col_dep.selectbox("Seleccionar Departamento Técnico", list(DEPARTAMENTOS_FREUND.keys()))
        buscar_termino = col_text.text_input("¿Qué buscas?", placeholder="Ej. union conduit, emt, tecno-ducto...")
        
        url_final = DEPARTAMENTOS_FREUND[dept_seleccionado]
        if st.button("🚀 Buscar Insumos en Freund"):
            with st.spinner("Conectando en tiempo real con Freund..."):
                st.session_state["coincidencias_busqueda"] = buscar_en_freund(url_final, buscar_termino)
            if not st.session_state["coincidencias_busqueda"]:
                st.warning("No se encontraron coincidencias para esa palabra clave en este departamento.")

    with col_manu:
        st.markdown("##### ➕ Agregar Material Manual")
        with st.form("form_material_manual"):
            m_desc = st.text_input("Descripción del Material")
            mc1, mc2 = st.columns(2)
            m_cant = mc1.number_input("Cantidad", min_value=1, value=1)
            m_costo = mc2.number_input("Costo Unitario ($)", min_value=0.00, value=0.00, step=0.10)
            btn_manual = st.form_submit_button("Agregar Material Manual (Al 40%)")
            
            if btn_manual and m_desc:
                p_v = m_costo / (1 - 0.40)
                st.session_state["materiales"].append({
                    "Borrar": False, "Descripción": m_desc.upper(), "Cantidad": int(m_cant),
                    "Costo Unitario ($)": float(m_costo), "Costo Total ($)": float(m_costo * m_cant),
                    "Rentabilidad (%)": 40.0, "Precio Venta U ($)": float(p_v), "Precio Venta Total ($)": float(p_v * m_cant)
                })
                st.toast(f"✅ Material manual cargado: {m_desc.upper()}")

    coincidencias = st.session_state.get("coincidencias_busqueda", [])
    if coincidencias:
        st.markdown(f"### 📊 Materiales encontrados ({len(coincidencias)})")
        for i, m in enumerate(coincidencias):
            with st.container():
                c_img, c_desc, c_precio, c_accion = st.columns([1.5, 3.2, 1, 2.3])
                with c_img:
                    if m.get("img"):
                        st.image(m["img"], use_container_width=True)
                    else:
                        st.markdown(f'<div style="background-color: #1e222b; border: 1px dashed #4e5565; border-radius: 5px; height: 90px; display: flex; align-items: center; justify-content: center; text-align: center;"><span style="color: #8a92a6; font-size: 11px;">ALFA PREVIEW</span></div>', unsafe_allow_html=True)
                with c_desc:
                    st.markdown(f"**{m['name']}**")
                    st.markdown(f"`SKU Real: {m['sku']}`")
                    st.markdown(f"[🔗 Ver producto en tienda Freund]({m['link']})")
                with c_precio:
                    st.markdown(f"#### ${m['price']:.2f}")
                with c_accion:
                    cant_m = st.number_input("Cant.", min_value=1, value=1, step=1, key=f"f_cant_{i}")
                    if st.button("📥 Agregar al Costeo", key=f"f_btn_{i}"):
                        p_v = m['price'] / (1 - 0.40)
                        st.session_state["materiales"].append({
                            "Borrar": False, "Descripción": m['name'], "Cantidad": int(cant_m),
                            "Costo Unitario ($)": float(m['price']), "Costo Total ($)": float(m['price'] * cant_m),
                            "Rentabilidad (%)": 40.0, "Precio Venta U ($)": float(p_v), "Precio Venta Total ($)": float(p_v * cant_m)
                        })
                        st.toast(f"✅ Suministro cargado: {m['name']}")
                st.markdown("<div style='margin-top: 12px; margin-bottom: 12px; border-bottom: 1px solid #2d3139;'></div>", unsafe_allow_html=True)

    if st.session_state["materiales"]:
        st.markdown("### 🛒 Materiales y Suministros Cargados")
        df_mat_orig = pd.DataFrame(st.session_state["materiales"])
        df_mat_edit = st.data_editor(
            df_mat_orig, hide_index=True, use_container_width=True,
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
    st.subheader("🛠️ Presupuesto de Mano de Obra y Logística")
    col_izq, col_der = st.columns([1, 1])
    with col_izq:
        st.markdown("#### ⚙️ 1. Personal Técnico y Cargas")
        rent_mo = st.number_input("Rentabilidad Comercial MO (%)", min_value=0.0, max_value=99.0, value=20.0, step=5.0)
        with st.form("form_mano_obra_completo"):
            c1, c2 = st.columns(2)
            cant_conf = c1.number_input("Cantidad Configuradores", min_value=0, value=0)
            dias_conf = c2.number_input("Días Configurador", min_value=0, value=0)
            tarifa_conf = st.number_input("Costo Diario Configurador ($)", min_value=0.0, value=50.0)
            st.markdown("---")
            c3, c4 = st.columns(2)
            cant_inst = c3.number_input("Cantidad Instaladores", min_value=0, value=0)
            dias_inst = c4.number_input("Días Instalador", min_value=0, value=0)
            tarifa_inst = st.number_input("Costo Diario Instalador ($)", min_value=0.0, value=25.0)
            st.markdown("---")
            c5, c6 = st.columns(2)
            dias_estadia = c5.number_input("Días Estadía fuera de SS", min_value=0, value=0)
            costo_estadia = c6.number_input("Costo Diario Estadía ($)", min_value=0.0, value=0.0)
            c7, c8 = st.columns(2)
            dias_viaticos = c7.number_input("Días de Viáticos", min_value=0, value=0)
            costo_viaticos = c8.number_input("Costo Diario Viáticos ($)", min_value=0.0, value=0.0)
            st.markdown("---")
            col_km1, col_km2 = st.columns(2)
            kms_proyecto = col_km1.number_input("Kilómetros totales (KM)", min_value=0.0, value=0.0)
            costo_por_km = col_km2.number_input("Costo por Kilómetro ($)", min_value=0.0, value=0.36, step=0.05)
            btn_guardar_mo = st.form_submit_button("Agregar al Balance Operativo")

            if btn_guardar_mo:
                servicios_nuevos = [
                    ("Servicio de Configuración Especializada", cant_conf * dias_conf, tarifa_conf),
                    ("Servicio de Técnico Instalador", cant_inst * dias_inst, tarifa_inst),
                    ("Logística de Estadía fuera de San Salvador", dias_estadia, costo_estadia),
                    ("Viáticos de Alimentación y Campo", dias_viaticos, costo_viaticos),
                    ("Movilización y Combustible del Proyecto", kms_proyecto, costo_por_km)
                ]
                for nombre, cant, costo_u in servicios_nuevos:
                    if cant > 0 and costo_u > 0:
                        costo_tot = float(cant * costo_u)
                        margen = rent_mo / 100.0
                        precio_v_u = costo_u / (1 - margen) if margen < 1 else costo_u
                        st.session_state["servicios_mo"].append({
                            "Borrar": False, "Descripción": nombre, "Cantidad": float(cant),
                            "Costo Unitario ($)": float(costo_u), "Costo Interno ($)": float(costo_tot),
                            "Rentabilidad (%)": float(rent_mo), "Costo del Cliente U ($)": float(precio_v_u),
                            "Precio Venta Total ($)": float(precio_v_u * cant)
                        })
                st.rerun()

    with col_der:
        st.markdown("#### 🔧 2. Certificaciones y Equipos Especiales")
        with st.form("form_herramientas"):
            c_desc = st.text_input("Descripción del Item", placeholder="Ej. Alquiler de Andamios")
            c_monto = st.number_input("Costo Total ($)", min_value=0.0, value=0.0)
            btn_add_h = st.form_submit_button("Agregar Herramienta")
            if btn_add_h and c_desc:
                st.session_state["servicios_mo"].append({
                    "Borrar": False, "Descripción": f"[HERRAMIENTA] {c_desc.upper()}", "Cantidad": 1.0,
                    "Costo Unitario ($)": float(c_monto), "Costo Interno ($)": float(c_monto),
                    "Rentabilidad (%)": 0.0, "Costo del Cliente U ($)": float(c_monto),
                    "Precio Venta Total ($)": float(c_monto)
                })
                st.rerun()

    st.markdown("---")
    if st.session_state["servicios_mo"]:
        df_mo_original = pd.DataFrame(st.session_state["servicios_mo"])
        df_mo_editado = st.data_editor(
            df_mo_original, hide_index=True, use_container_width=True,
            disabled=["Descripción", "Costo Unitario ($)", "Costo Interno ($)", "Costo del Cliente U ($)", "Precio Venta Total ($)"],
            column_config={
                "Borrar": st.column_config.CheckboxColumn("Borrar", default=False),
                "Cantidad": st.column_config.NumberColumn("Cantidad", min_value=0.0, format="%.2f"),
                "Rentabilidad (%)": st.column_config.NumberColumn("Rentabilidad (%)", min_value=0, max_value=99),
            }
        )
        for i in range(len(df_mo_editado)):
            r_pct = df_mo_editado.at[i, "Rentabilidad (%)"] / 100.0
            c_uni = df_mo_editado.at[i, "Costo Unitario ($)"]
            cant = df_mo_editado.at[i, "Cantidad"]
            df_mo_editado.at[i, "Costo Interno ($)"] = c_uni * cant
            p_venta_u = c_uni / (1 - r_pct) if r_pct < 1 else c_uni
            df_mo_editado.at[i, "Costo del Cliente U ($)"] = p_venta_u
            df_mo_editado.at[i, "Precio Venta Total ($)"] = p_venta_u * cant
        st.session_state["servicios_mo"] = df_mo_editado.to_dict(orient="records")
        if st.button("🗑️ Eliminar Servicios Seleccionados", key="del_mo_sel"):
            st.session_state["servicios_mo"] = [s for s in st.session_state["servicios_mo"] if not s["Borrar"]]
            st.rerun()

# ==========================================
# --- PESTAÑA 4: RESUMEN COMERCIAL (COMPLETA Y EN MARCHA) ---
# ==========================================
with tab4:
    st.subheader("📊 Análisis y Estructura Financiera")
    
    lista_eq = st.session_state.get("equipos", [])
    lista_mat = st.session_state.get("materiales", [])
    lista_mo = st.session_state.get("servicios_mo", [])
    
    # Cálculos Financieros Consolidados
    costo_equipos = sum(float(x.get("Costo Total ($)", 0.0)) for x in lista_eq)
    venta_equipos = sum(float(x.get("Precio Venta Total ($)", 0.0)) for x in lista_eq)
    
    costo_materiales = sum(float(x.get("Costo Total ($)", 0.0)) for x in lista_mat)
    venta_materiales = sum(float(x.get("Precio Venta Total ($)", 0.0)) for x in lista_mat)
    
    costo_mo_tot = sum(float(x.get("Costo Interno ($)", 0.0)) for x in lista_mo)
    venta_mo_tot = sum(float(x.get("Precio Venta Total ($)", 0.0)) for x in lista_mo)
    
    costo_total_proyecto = costo_equipos + costo_materiales + costo_mo_tot
    subtotal_venta_proyecto = venta_equipos + venta_materiales + venta_mo_tot
    utilidad_total = subtotal_venta_proyecto - costo_total_proyecto
    rentabilidad_real_pct = (utilidad_total / subtotal_venta_proyecto * 100) if subtotal_venta_proyecto > 0 else 0.0

    # Panel de control de Impuestos y Rentabilidad Objetivo
    c_ctr1, c_ctr2 = st.columns(2)
    rent_objetivo = c_ctr1.number_input("🎯 Rentabilidad Comercial Objetivo (%)", min_value=1.0, max_value=99.0, value=40.0, step=1.0)
    aplicar_iva = c_ctr2.checkbox("⚠️ Aplicar IVA de Ley (13%) a la Oferta", value=True)
    
    iva_calc = subtotal_venta_proyecto * 0.13 if aplicar_iva else 0.0
    total_general_cliente = subtotal_venta_proyecto + iva_calc

    st.markdown("---")
    
    # KPIs Principales
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    kpi1.metric("Costo Interno Global", f"${costo_total_proyecto:,.2f}")
    kpi2.metric("Precio Venta Subtotal", f"${subtotal_venta_proyecto:,.2f}")
    
    # Indicador dinámico de Rentabilidad Real
    if rentabilidad_real_pct >= rent_objetivo:
        kpi3.metric("Rentabilidad Real", f"{rentabilidad_real_pct:.2f}%", f"▲ Cumple objetivo ({rent_objetivo}%)")
    else:
        kpi3.metric("Rentabilidad Real", f"{rentabilidad_real_pct:.2f}%", f"▼ Abajo del objetivo", delta_color="inverse")
        
    kpi4.metric("Utilidad Bruta Alfa", f"${utilidad_total:,.2f}")

    # Distribución Operativa (Pie Chart) y Detalles
    st.markdown("### 📊 Composición del Presupuesto Comercial")
    col_chart, col_table = st.columns([4, 6])
    
    df_chart = pd.DataFrame([
        {"Rubro": "📦 Equipos Principales", "Monto ($)": venta_equipos},
        {"🏗️ Materiales y Canalización", "Monto ($)": venta_materiales},
        {"🛠️ Mano de Obra e Ingeniería", "Monto ($)": venta_mo_tot}
    ])
    
    with col_chart:
        if subtotal_venta_proyecto > 0:
            fig = px.pie(df_chart, values="Monto ($)", names="Rubro", hole=0.4,
                         color_discrete_sequence=px.colors.qualitative.Pastel)
            fig.update_layout(margin=dict(t=10, b=10, l=10, r=10), height=260, showlegend=True)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Sin datos financieros para graficar.")

    with col_table:
        tabla_resumen = []
        for eq in lista_eq:
            tabla_resumen.append({"Tipo": "Equipo", "Detalle del Ítem": eq['Descripción'], "Cantidad": eq['Cantidad'], "Venta Total ($)": eq['Precio Venta Total ($)']})
        for mat in lista_mat:
            tabla_resumen.append({"Tipo": "Material", "Detalle del Ítem": mat['Descripción'], "Cantidad": mat['Cantidad'], "Venta Total ($)": mat['Precio Venta Total ($)']})
        for mo in lista_mo:
            tabla_resumen.append({"Tipo": "Mano de Obra", "Detalle del Ítem": mo['Descripción'], "Cantidad": mo['Cantidad'], "Venta Total ($)": mo['Precio Venta Total ($)']})
            
        if tabla_resumen:
            st.dataframe(pd.DataFrame(tabla_resumen), hide_index=True, use_container_width=True)
        else:
            st.warning("No hay elementos cargados en la cotización.")

    # Caja de Cierre y Botón de Reporte PDF
    if subtotal_venta_proyecto > 0:
        st.markdown(
            f"""
            <div style="background-color: #1e222b; padding: 20px; border-radius: 8px; border: 1px solid #2d3139; margin-top: 15px;">
                <h4 style="margin: 0; color: #ffffff;">🧾 CIERRE DE COTIZACIÓN COMERCIAL</h4>
                <p style="margin: 8px 0 0 0; font-size: 15px;"><b>SUBTOTAL NETO DE VENTA:</b> ${subtotal_venta_proyecto:,.2f}</p>
                <p style="margin: 4px 0 0 0; font-size: 15px;"><b>IVA REPERCUTIDO (13%):</b> ${iva_calc:,.2f}</p>
                <hr style="border-color: #2d3139; margin: 10px 0;">
                <h2 style="margin: 0; color: #58a6ff;">VALOR TOTAL DE LA OFERTA: ${total_general_cliente:,.2f}</h2>
            </div>
            """, unsafe_allow_html=True
        )
        
        # Lógica de Construcción de PDF en Memoria
        pdf = PDF_Cotizacion()
        pdf.alias_nb_pages()
        pdf.add_page()
        
        pdf.set_font("Arial", "B", 11)
        pdf.cell(0, 7, f"PROYECTO: {proyecto.upper()}", 0, 1)
        pdf.set_font("Arial", "", 10)
        pdf.cell(100, 6, f"Cliente: {empresa}", 0, 0)
        pdf.cell(90, 6, f"Validez: {validez}", 0, 1)
        pdf.cell(100, 6, f"Atención: {atencion}", 0, 0)
        pdf.cell(90, 6, f"Pago: {pago}", 0, 1)
        pdf.ln(5)
        
        pdf.set_fill_color(30, 41, 59)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("Arial", "B", 9)
        pdf.cell(110, 7, " DESCRIPCION DEL RUBRO / ITEM", 1, 0, "L", True)
        pdf.cell(25, 7, "CANTIDAD", 1, 0, "C", True)
        pdf.cell(25, 7, "P. UNITARIO", 1, 0, "R", True)
        pdf.cell(30, 7, "TOTAL", 1, 1, "R", True)
        
        pdf.set_text_color(0, 0, 0)
        pdf.set_font("Arial", "", 8.5)
        
        for item in tabla_resumen:
            p_u = item["Venta Total ($)"] / item["Cantidad"]
            pdf.cell(110, 6, f" [{item['Tipo'].upper()}] {item['Detalle del Ítem'][:55]}", 1, 0, "L")
            pdf.cell(25, 6, f"{item['Cantidad']}", 1, 0, "C")
            pdf.cell(25, 6, f"${p_u:,.2f}", 1, 0, "R")
            pdf.cell(30, 6, f"${item['Venta Total ($)']:,.2f}", 1, 1, "R")
            
        pdf.ln(4)
        pdf.set_font("Arial", "B", 10)
        pdf.cell(140, 6, "SUBTOTAL NETO:", 0, 0, "R")
        pdf.cell(50, 6, f"${subtotal_venta_proyecto:,.2f}", 0, 1, "R")
        pdf.cell(140, 6, "IVA (13%):", 0, 0, "R")
        pdf.cell(50, 6, f"${iva_calc:,.2f}", 0, 1, "R")
        pdf.set_font("Arial", "B", 11)
        pdf.cell(140, 6, "TOTAL DE LA OFERTA:", 0, 0, "R")
        pdf.cell(50, 6, f"${total_general_cliente:,.2f}", 0, 1, "R")
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.download_button(
            label="📥 Descargar Propuesta Comercial en PDF",
            data=pdf.output(dest='S').encode('latin-1'),
            file_name=f"Oferta_{empresa.replace(' ', '_')}.pdf",
            mime="application/pdf"
        )
