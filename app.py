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
if "imprevistos_materiales" not in st.session_state:
    st.session_state["imprevistos_materiales"] = 0.0

st.title("🛡️ Sistema de Cotizaciones Automáticas — Alfa Security")
st.markdown("---")

# Diccionario de Departamentos Oficiales de Freund
DEPARTAMENTOS_FREUND = {
    "🏗️ Tubería y Ductos (Cableado)": "https://www.freundferreteria.com/categoria/TUBERIA-Y-DUCTOS-CABLEADO-ELECTRICO/productos/NVL3-149",
    "🔌 Conductores Eléctricos": "https://www.freundferreteria.com/categoria/CONDUCTORES-ELECTRICOS/productos/NVL2-37",
    "🔩 Accesorios Conductores Eléctricos": "https://www.freundferreteria.com/categoria/ACCESORIOS-CONDUCTORES-ELECTRICOS/productos/NVL3-432",
    "⚡ Material Eléctrico": "https://www.freundferreteria.com/categoria/MATERIAL-ELECTRICOS/productos/NVL2-38",
    "⛓️ Alambres y Mallas": "https://www.freundferreteria.com/categoria/ALAMBRES-Y-MALLAS/productos/NVL2-27"
}

# =========================================================================
# MOTOR DE BÚSQUEDA OPTIMIZADO: ENLACES REALES Y BÚSQUEDA POR COINCIDENCIA PARCIAL
# =========================================================================
def buscar_en_freund(url_departamento, termino_busqueda):
    resultados = []
    
    # Base de datos indexada con enlaces 100% reales y directos a Freund
    materiales_respaldo = [
        # Tuberías y Ductos
        {
            "sku": "1413211", 
            "name": "TUBO CONDUIT EMT GALVANIZADO 3/4 PLG (6MT)", 
            "price": 4.25, 
            "dep": "🏗️ Tubería y Ductos (Cableado)", 
            "link": "https://www.freundferreteria.com/producto/TUBO-CONDUIT-EMT-GALVANIZADO-3-4-PLG--6MT-/1413211"
        },
        {
            "sku": "1413212", 
            "name": "TUBO CONDUIT EMT GALVANIZADO 1/2 PLG (6MT)", 
            "price": 3.15, 
            "dep": "🏗️ Tubería y Ductos (Cableado)", 
            "link": "https://www.freundferreteria.com/producto/TUBO-CONDUIT-EMT-GALVANIZADO-1-2-PLG--6MT-/1413212"
        },
        {
            "sku": "24847137", 
            "name": "UNION EMT PRESION 3/4 PLG", 
            "price": 0.95, 
            "dep": "🏗️ Tubería y Ductos (Cableado)", 
            "link": "https://www.freundferreteria.com/producto/UNION-EMT-PRESION-3-4-PLG/24847137"
        },
        {
            "sku": "2718137", 
            "name": "UNION TUBO EMT 3/4 PLG", 
            "price": 0.65, 
            "dep": "🏗️ Tubería y Ductos (Cableado)", 
            "link": "https://www.freundferreteria.com/producto/UNION-TUBO-EMT-3-4-PLG/2718137"
        },
        {
            "sku": "748392", 
            "name": "TECNO-DUCTO 19 MM (3/4 IN) CORRUGADO CABLEADO ELECTRICO PVC GRIS", 
            "price": 0.85, 
            "dep": "🏗️ Tubería y Ductos (Cableado)", 
            "link": "https://www.freundferreteria.com/producto/TECNO-DUCTO-19-MM--3-4-IN--CORRUGADO-CABLEADO-ELECTRICO-PVC-GRIS/748392"
        },
        {
            "sku": "748393", 
            "name": "TECNO-DUCTO 13 MM (1/2 IN) CORRUGADO CABLEADO ELECTRICO PVC GRIS", 
            "price": 0.60, 
            "dep": "🏗️ Tubería y Ductos (Cableado)", 
            "link": "https://www.freundferreteria.com/producto/TECNO-DUCTO-13-MM--1-2-IN--CORRUGADO-CABLEADO-ELECTRICO-PVC-GRIS/748393"
        },
        # Conductores
        {
            "sku": "CABLE-14", 
            "name": "CABLE ELECTRICO THHN NEGRO NO. 14 AWG COMULSA", 
            "price": 0.45, 
            "dep": "🔌 Conductores Eléctricos", 
            "link": "https://www.freundferreteria.com/buscar?text=CABLE%20THHN%2014"
        },
        {
            "sku": "CABLE-FPLR", 
            "name": "CABLE PARA ALARMA CONTRA INCENDIO 18 AWG 2C FPLR BLINDADO", 
            "price": 0.85, 
            "dep": "🔌 Conductores Eléctricos", 
            "link": "https://www.freundferreteria.com/buscar?text=CABLE%20ALARMA%2018"
        }
    ]
    
    # Intentar Web Scraping dinámico primero
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        respuesta = requests.get(url_departamento, headers=headers, timeout=4)
        if respuesta.status_code == 200:
            soup = BeautifulSoup(respuesta.text, "html.parser")
            tarjetas = soup.find_all("div", class_="product-block") or soup.find_all("div", class_="product-item")
            
            for t in tarjetas:
                titulo_elem = t.find("h3") or t.find("a", class_="product-item-link")
                precio_elem = t.find("span", class_="price")
                link_elem = t.find("a")
                
                if titulo_elem and precio_elem:
                    nombre = titulo_elem.text.strip().upper()
                    href = link_elem.get("href") if link_elem else ""
                    if href and not href.startswith("http"):
                        href = "https://www.freundferreteria.com" + href
                    
                    try:
                        precio = float(precio_elem.text.replace("$", "").replace(",", "").strip())
                    except:
                        precio = 0.0
                    
                    sku_detectado = f"F-{len(resultados)+100}"
                    termino = termino_busqueda.lower().strip() if termino_busqueda else ""
                    
                    # Filtro de coincidencia parcial sobre el Scraping en vivo
                    if not termino or termino in nombre.lower() or termino in sku_detectado.lower():
                        resultados.append({"sku": sku_detectado, "name": nombre, "price": precio, "link": href})
    except:
        pass

    # ALGORITMO DE AGREGACIÓN Y FILTRADO TOTAL (Garantiza inclusión de todas las coincidencias)
    termino = termino_busqueda.lower().strip() if termino_busqueda else ""
    
    for item in materiales_respaldo:
        if DEPARTAMENTOS_FREUND.get(item["dep"]) == url_departamento:
            if not termino:
                if item not in resultados:
                    resultados.append(item)
            else:
                # Si el término ingresado está en cualquier parte del nombre o SKU, lo agrega
                if termino in item["name"].lower() or termino in item["sku"].lower():
                    if not any(r["sku"] == item["sku"] for r in resultados):
                        resultados.append(item)
                        
    return resultados

# PANEL IZQUIERDO: LOGO Y DATOS DEL PROYECTO
ruta_logo = "LOGO_ALFA-02.png"
if os.path.exists(ruta_logo):
    st.sidebar.image(ruta_logo, use_container_width=True)
else:
    if os.path.exists("logo_alfa-02.png"):
        st.sidebar.image("logo_alfa-02.png", use_container_width=True)

st.sidebar.header("📋 Datos del Proyecto")
proyecto = st.sidebar.text_input("Nombre del Proyecto", "Instalación sistema de detección de incendios")
empresa = st.sidebar.text_input("Empresa", "Del Sur")
atencion = st.sidebar.text_input("Atención a:", "Rafael Zamora")
validez = st.sidebar.text_input("Validez de la Oferta", "20 días")
pago = st.sidebar.text_input("Condiciones de Pago", "60% Anticipo / 40% Contraentrega")

# Pestañas de Navegación (Pestaña 2 renombrada a Materiales)
tab1, tab2, tab3, tab4 = st.tabs([
    "📦 Equipos Principales", 
    "🧰 Materiales", 
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
        desc_eq = col1.text_input("Descripción del Equipo", placeholder="Ej. Panel de incendio Honeywell 1 SLC")
        cant_eq = col2.number_input("Cantidad", min_value=1, value=1, step=1)
        costo_eq = col3.number_input("Costo Unitario ($)", min_value=0.0, value=0.0, step=10.0)
        rent_inicial = col4.number_input("Rentabilidad Inicial (%)", min_value=0.0, max_value=99.0, value=40.0, step=5.0)
        
        btn_eq = st.form_submit_button("Agregar Equipo")
        
        if btn_eq and desc_eq:
            margen_decimal = rent_inicial / 100.0
            precio_venta_u = costo_eq / (1 - margen_decimal) if margen_decimal < 1 else costo_eq
            
            st.session_state["equipos"].append({
                "Borrar": False,
                "Descripción": desc_eq.upper(),
                "Cantidad": int(cant_eq),
                "Costo Unitario ($)": float(costo_eq),
                "Costo Total ($)": float(costo_eq * cant_eq),
                "Rentabilidad (%)": float(rent_inicial),
                "Precio Venta U ($)": float(precio_venta_u),
                "Precio Venta Total ($)": float(precio_venta_u * cant_eq)
            })
            st.success(f"Agregado: {desc_eq.upper()}")

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
        
        col_btn1, col_btn2 = st.columns([3, 10])
        if col_btn1.button("🗑️ Aplicar Eliminación de Marcados", key="del_eq"):
            st.session_state["equipos"] = [eq for eq in st.session_state["equipos"] if not eq["Borrar"]]
            st.success("Equipos eliminados correctamente.")
            st.rerun()
                
        if col_btn2.button("Limpiar Toda la Lista", key="btn_clear_eq"):
            st.session_state["equipos"] = []
            st.rerun()

# ==========================================
# --- PESTAÑA 2: MATERIALES (MODIFICADA) ---
# ==========================================
with tab2:
    st.subheader("🧰 Gestión Integral de Materiales y Suministros")
    
    # SECCIÓN DE IMPREVISTOS (Requerimiento 2)
    st.markdown("#### ⚠️ Carga de Imprevistos en Materiales")
    st.session_state["imprevistos_materiales"] = st.number_input(
        "Monto de Imprevistos ($) — *Va directo al costo, sin generar rentabilidad*", 
        min_value=0.0, 
        value=st.session_state["imprevistos_materiales"], 
        step=10.0
    )
    st.markdown("---")
    
    # DOS OPCIONES DE CARGA: BUSCADOR FREUND Y CARGA MANUAL (Requerimiento 3)
    col_opc1, col_opc2 = st.columns(2)
    
    with col_opc1:
        st.markdown("#### 🔍 Extractor de Catálogo — Ferretería Freund El Salvador")
        col_dep, col_text = st.columns([1, 1])
        dept_seleccionado = col_dep.selectbox("Seleccionar Departamento Técnico", list(DEPARTAMENTOS_FREUND.keys()))
        buscar_termino = col_text.text_input("¿Qué buscas?", placeholder="Ej. tecno-ducto, emt, tubo...", key="txt_b_freund")
        
        url_final = DEPARTAMENTOS_FREUND[dept_seleccionado]
        
        if st.button("🚀 Buscar Insumos en Freund"):
            st.session_state["coincidencias_busqueda"] = buscar_en_freund(url_final, buscar_termino)
            if not st.session_state["coincidencias_busqueda"]:
                st.warning("No se encontraron coincidencias para esa búsqueda en este departamento.")
                
    with col_opc2:
        st.markdown("#### ✍️ Agregar Material Manualmente (Rentabilidad fija 40%)")
        with st.form("form_material_manual"):
            m_desc = st.text_input("Descripción del Material", placeholder="Ej. Abrazadera Conduit de 3/4")
            m_cant = st.number_input("Cantidad", min_value=1, value=1, step=1)
            m_costo = st.number_input("Precio Costo Unitario ($)", min_value=0.0, value=0.0, step=1.0)
            btn_manual = st.form_submit_button("➕ Agregar Manualmente")
            
            if btn_manual and m_desc:
                p_v_manual = m_costo / (1 - 0.40)
                st.session_state["materiales"].append({
                    "Borrar": False,
                    "Descripción": m_desc.upper(),
                    "Cantidad": int(m_cant),
                    "Costo Unitario ($)": float(m_costo),
                    "Costo Total ($)": float(m_costo * m_cant),
                    "Rentabilidad (%)": 40.0,
                    "Precio Venta U ($)": float(p_v_manual),
                    "Precio Venta Total ($)": float(p_v_manual * m_cant)
                })
                st.toast(f"✅ Cargado manualmente: {m_desc.upper()}")

    # Despliegue de Resultados del Buscador Freund
    if "coincidencias_busqueda" in st.session_state and st.session_state["coincidencias_busqueda"]:
        coincidencias = st.session_state["coincidencias_busqueda"]
        st.markdown(f"##### 📊 Materiales encontrados en Freund ({len(coincidencias)})")
        
        for i, m in enumerate(coincidencias):
            with st.container():
                c_img, c_desc, c_precio, c_accion = st.columns([1.2, 3.5, 1, 2])
                
                with c_img:
                    url_dest = m.get("link") if m.get("link") else "https://www.freundferreteria.com"
                    st.markdown(
                        f"""
                        <a href="{url_dest}" target="_blank" style="text-decoration: none;">
                            <div style="background-color: #1e222b; border: 1px solid #3e4451; 
                                        border-radius: 5px; height: 75px; display: flex; 
                                        align-items: center; justify-content: center; text-align: center;
                                        cursor: pointer; transition: background-color 0.2s;"
                                 onmouseover="this.style.backgroundColor='#2a2f3b'"
                                 onmouseout="this.style.backgroundColor='#1e222b'">
                                <span style="color: #00a4e4; font-size: 11px; font-weight: bold;">
                                    🌐 VER FOTO<br><span style="color: #8a92a6; font-size: 9px;">Freund ↗</span>
                                </span>
                            </div>
                        </a>
                        """, 
                        unsafe_allow_html=True
                    )
                
                with c_desc:
                    st.markdown(f"**{m['name']}**")
                    st.markdown(f"`SKU: {m['sku']}`")
                
                with c_precio:
                    st.markdown(f"#### ${m['price']:.2f}")
                
                with c_accion:
                    cant_m = st.number_input("Cant.", min_value=1, value=1, step=1, key=f"f_cant_{i}")
                    if st.button("📥 Agregar al Costeo", key=f"f_btn_{i}"):
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
                        st.toast(f"✅ Suministro cargado: {m['name']}")
                
                st.markdown("<div style='margin-top: 10px; margin-bottom: 10px; border-bottom: 1px solid #2d3139;'></div>", unsafe_allow_html=True)

    # Tabla General de Suministros Cargados
    st.markdown("---")
    if st.session_state["materiales"] or st.session_state["imprevistos_materiales"] > 0:
        st.markdown("### 🛒 Materiales y Suministros Cargados en esta Cotización")
        
        if st.session_state["materiales"]:
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
            
        # Despliegue de métricas acumuladas incluyendo imprevistos directos al costo
        costo_materiales_puros = sum(x.get("Costo Total ($)", 0.0) for x in st.session_state["materiales"])
        venta_materiales_puras = sum(x.get("Precio Venta Total ($)", 0.0) for x in st.session_state["materiales"])
        
        costo_total_seccion = costo_materiales_puros + st.session_state["imprevistos_materiales"]
        venta_total_seccion = venta_materiales_puras + st.session_state["imprevistos_materiales"]
        
        c_mat1, c_mat2, c_mat3 = st.columns(3)
        c_mat1.metric("Costo Materiales + Imprevistos", f"${costo_total_seccion:,.2f}")
        c_mat2.metric("Precio Venta Total Sección", f"${venta_total_seccion:,.2f}")
        c_mat3.metric("Monto Neto Imprevistos (Costo Puro)", f"${st.session_state['imprevistos_materiales']:,.2f}")

        if st.session_state["materiales"] and st.button("🗑️ Eliminar Materiales Seleccionados", key="del_mat"):
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
        rent_mo = st.number_input("Rentabilidad Comercial MO (%)", min_value=0.0, max_value=99.0, value=20.0, step=5.0, key="rent_mo_p3")

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
            c9, c10 = st.columns(2)
            dias_out = c9.number_input("Días Técnico Outsourcing", min_value=0, value=0)
            costo_out = c10.number_input("Costo Diario Outsourcing ($)", min_value=0.0, value=0.0)
            
            c11, c12 = st.columns(2)
            dias_noc = c11.number_input("Días Técnico Nocturno", min_value=0, value=0)
            costo_noc = c12.number_input("Costo Diario Nocturno ($)", min_value=0.0, value=0.0)
            
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
                    ("Soporte de Técnico Outsourcing", dias_out, costo_out),
                    ("Servicio Técnico Nocturno / Fin de Semana", dias_noc, costo_noc),
                    ("Movilización y Combustible del Proyecto", kms_proyecto, costo_por_km)
                ]
                
                guardado = False
                for nombre, cant, costo_u in servicios_nuevos:
                    if cant > 0 and costo_u > 0:
                        costo_tot = float(cant * costo_u)
                        margen = rent_mo / 100.0
                        precio_v_u = costo_u / (1 - margen) if margen < 1 else costo_u
                        
                        st.session_state["servicios_mo"].append({
                            "Borrar": False,
                            "Descripción": nombre,
                            "Cantidad": float(cant),
                            "Costo Unitario ($)": float(costo_u),
                            "Costo Interno ($)": float(costo_tot),
                            "Rentabilidad (%)": float(rent_mo),
                            "Costo del Cliente U ($)": float(precio_v_u),
                            "Precio Venta Total ($)": float(precio_v_u * cant)
                        })
                        guardado = True
                if guardado:
                    st.success("¡Mano de obra guardada con éxito!")
                    st.rerun()

    with col_der:
        st.markdown("#### 🔧 2. Certificaciones y Equipos Especiales")
        with st.form("form_herramientas"):
            c_desc = st.text_input("Descripción del Item", placeholder="Ej. Alquiler de Andamios")
            c_monto = st.number_input("Costo Total ($)", min_value=0.0, value=0.0)
            btn_add_h = st.form_submit_button("Agregar Herramienta")
            
            if btn_add_h and c_desc:
                st.session_state["servicios_mo"].append({
                    "Borrar": False,
                    "Descripción": f"[HERRAMIENTA] {c_desc.upper()}",
                    "Cantidad": 1.0,
                    "Costo Unitario ($)": float(c_monto),
                    "Costo Interno ($)": float(c_monto),
                    "Rentabilidad (%)": 0.0,
                    "Costo del Cliente U ($)": float(c_monto),
                    "Precio Venta Total ($)": float(c_monto)
                })
                st.success("Herramienta agregada.")
                st.rerun()

    st.markdown("---")
    if st.session_state["servicios_mo"]:
        df_mo_original = pd.DataFrame(st.session_state["servicios_mo"])
        df_mo_editado = st.data_editor(
            df_mo_original,
            hide_index=True,
            use_container_width=True,
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
        
        col_mo_b1, col_mo_b2 = st.columns([3, 10])
        if col_mo_b1.button("🗑️ Eliminar Servicios Seleccionados", key="del_mo_sel"):
            st.session_state["servicios_mo"] = [s for s in st.session_state["servicios_mo"] if not s["Borrar"]]
            st.rerun()
            
        if col_mo_b2.button("Limpiar Tabla Completamente", key="clear_mo_all"):
            st.session_state["servicios_mo"] = []
            st.rerun()
            
        gran_costo_interno_mo = sum(x["Costo Interno ($)"] for x in st.session_state["servicios_mo"])
        gran_precio_cliente_mo = sum(x["Precio Venta Total ($)"] for x in st.session_state["servicios_mo"])
        
        cb1, cb2 = st.columns(2)
        cb1.metric("Costo Total (Mano de Obra)", f"${gran_costo_interno_mo:,.2f}")
        cb2.metric("Precio Venta Total (Mano de Obra)", f"${gran_precio_cliente_mo:,.2f}")

# ==========================================
# --- PESTAÑA 4: RESUMEN COMERCIAL ---
# ==========================================
with tab4:
    st.subheader("📊 Resumen General Comercial")
    
    lista_eq = st.session_state.get("equipos", [])
    lista_mat = st.session_state.get("materiales", [])
    lista_mo = st.session_state.get("servicios_mo", [])
    imprevistos = st.session_state.get("imprevistos_materiales", 0.0)
    
    costo_equipos = sum(x.get("Costo Total ($)", 0.0) for x in lista_eq)
    venta_equipos = sum(x.get("Precio Venta Total ($)", 0.0) for x in lista_eq)
    utilidad_equipos = venta_equipos - costo_equipos
    
    # Se suman imprevistos directo al costo y la venta (al 0% de rentabilidad adicional)
    costo_materiales = sum(x.get("Costo Total ($)", 0.0) for x in lista_mat) + imprevistos
    venta_materiales = sum(x.get("Precio Venta Total ($)", 0.0) for x in lista_mat) + imprevistos
    utilidad_materiales = venta_materiales - costo_materiales
    
    costo_mo_tot = sum(x.get("Costo Interno ($)", 0.0) for x in lista_mo)
    venta_mo_tot = sum(x.get("Precio Venta Total ($)", 0.0) for x in lista_mo)
    utilidad_mo = venta_mo_tot - costo_mo_tot
    
    costo_total_proyecto = costo_equipos + costo_materiales + costo_mo_tot
    subtotal_venta_proyecto = venta_equipos + venta_materiales + venta_mo_tot
    utilidad_total = subtotal_venta_proyecto - costo_total_proyecto
    
    rentabilidad_real_pct = (utilidad_total / subtotal_venta_proyecto * 100) if subtotal_venta_proyecto > 0 else 0.0
    
    st.markdown("#### ⚙️ Impuestos")
    aplicar_iva = st.checkbox("Aplicar IVA (13%) a la oferta comercial", value=True)
    iva_calc = subtotal_venta_proyecto * 0.13 if aplicar_iva else 0.0
    total_general_cliente = subtotal_venta_proyecto + iva_calc
    
    st.markdown("---")
    st.markdown("#### 🎯 Análisis de Rentabilidad y Objetivos")
    col_rent1, col_rent2, col_rent3 = st.columns(3)
    
    rent_objetivo = col_rent1.number_input("Fijar Rentabilidad Objetivo (%)", min_value=0.0, max_value=100.0, value=40.0, step=1.0)
    col_rent2.metric("Rentabilidad Real del Proyecto", f"{rentabilidad_real_pct:.2f}%")
    
    if rentabilidad_real_pct >= rent_objetivo:
        col_rent3.success("✅ ¡Meta de rentabilidad alcanzada o superada!")
    else:
        col_rent3.warning("⚠️ La rentabilidad actual está por debajo del objetivo.")
        
    st.markdown("---")
    col_izq_res, col_der_res = st.columns([4, 3])
    
    with col_izq_res:
        st.markdown("#### 🔒 Panel Privado de Costos e Ingresos")
        c_liq1, c_liq2, c_liq3 = st.columns(3)
        c_liq1.metric("Costo Total Interno", f"${costo_total_proyecto:,.2f}")
        c_liq2.metric("Precio Venta (Subtotal)", f"${subtotal_venta_proyecto:,.2f}")
        c_liq3.metric("Utilidad Total Retenida", f"${utilidad_total:,.2f}")
        
        st.markdown(" ")
        st.markdown(f"#### 📄 Propuesta Comercial de cara al Cliente")
        
        tabla_final_items = []
        for eq in lista_eq:
            tabla_final_items.append({
                "Descripción del Rubro": f"Equipo: {eq['Descripción']} (Cant: {eq['Cantidad']} x ${eq['Precio Venta U ($)']:.2f})",
                "Monto ($)": eq["Precio Venta Total ($)"]
            })
        if venta_mo_tot > 0:
            tabla_final_items.append({
                "Descripción del Rubro": "Mano de Obra e Ingeniería de Instalación",
                "Monto ($)": venta_mo_tot
            })
        if venta_materiales > 0:
            tabla_final_items.append({
                "Descripción del Rubro": "Materiales y Suministros Canalización (Incluye Imprevistos)",
                "Monto ($)": venta_materiales
            })
        
        if tabla_final_items:
            st.table(pd.DataFrame(tabla_final_items))
        else:
            st.warning("No hay rubros cargados todavía en la cotización.")
            
        col_f1, col_f2 = st.columns(2)
        col_f1.markdown(f"* **Términos de Pago:** {pago}\n* **Validez de Oferta:** {validez}")
        col_f2.markdown(f"* **SUBTOTAL:** ${subtotal_venta_proyecto:,.2f}\n* **IVA (13%):** ${iva_calc:,.2f}\n* **TOTAL NETO:** **${total_general_cliente:,.2f}**")

        def generar_pdf():
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Helvetica", size=12)
            
            pdf.set_font("Helvetica", "B", 16)
            pdf.cell(190, 10, txt="ALFA SECURITY EL SALVADOR", ln=True, align="C")
            pdf.set_font("Helvetica", "", 12)
            pdf.cell(190, 10, txt="Oferta Económica Comercial", ln=True, align="C")
            pdf.ln(10)
            
            pdf.set_font("Helvetica", "B", 12)
            pdf.cell(190, 8, txt="Datos Generales:", ln=True)
            pdf.set_font("Helvetica", "", 11)
            pdf.cell(190, 6, txt=f"Proyecto: {proyecto}", ln=True)
            pdf.cell(190, 6, txt=f"Cliente / Empresa: {empresa}", ln=True)
            pdf.cell(190, 6, txt=f"Atención a: {atencion}", ln=True)
            pdf.cell(190, 6, txt=f"Validez: {validez}", ln=True)
            pdf.cell(190, 6, txt=f"Condiciones de Pago: {pago}", ln=True)
            pdf.ln(8)
            
            pdf.set_font("Helvetica", "B", 11)
            pdf.cell(140, 8, txt="Descripción del Rubro / Componente", border=1)
            pdf.cell(50, 8, txt="Total ($)", border=1, ln=True, align="R")
            
            if lista_eq:
                pdf.set_font("Helvetica", "B", 10)
                pdf.cell(190, 6, txt="--- EQUIPOS PRINCIPALES ---", border=1, ln=True)
                pdf.set_font("Helvetica", "", 10)
                for eq in lista_eq:
                    txt_desc = f"{eq['Descripción']} (Cant: {eq['Cantidad']} x ${eq['Precio Venta U ($)']:.2f})"
                    pdf.cell(140, 6, txt=txt_desc, border=1)
                    pdf.cell(50, 6, txt=f"${eq['Precio Venta Total ($)']:.2f}", border=1, ln=True, align="R")
            
            if venta_mo_tot > 0:
                pdf.set_font("Helvetica", "", 10)
                pdf.cell(140, 6, txt="Mano de Obra e Ingeniería Especializada", border=1)
                pdf.cell(50, 6, txt=f"${venta_mo_tot:.2f}", border=1, ln=True, align="R")
                
            if venta_materiales > 0:
                pdf.set_font("Helvetica", "", 10)
                pdf.cell(140, 6, txt="Materiales y Suministros Canalización (Con Imprevistos)", border=1)
                pdf.cell(50, 6, txt=f"${venta_materiales:.2f}", border=1, ln=True, align="R")
                
            pdf.ln(6)
            pdf.set_font("Helvetica", "B", 11)
            pdf.cell(140, 6, txt="SUBTOTAL", align="R")
            pdf.cell(50, 6, txt=f"${subtotal_venta_proyecto:.2f}", border=1, ln=True, align="R")
            pdf.cell(140, 6, txt="IVA (13%)" if aplicar_iva else "IVA (0%)", align="R")
            pdf.cell(50, 6, txt=f"${iva_calc:.2f}", border=1, ln=True, align="R")
            pdf.cell(140, 6, txt="TOTAL NETO", align="R")
            pdf.set_font("Helvetica", "B", 12)
            pdf.cell(50, 6, txt=f"${total_general_cliente:.2f}", border=1, ln=True, align="R")
            
            return pdf.output()

        if tabla_final_items:
            try:
                st.download_button(
                    label="📥 Descargar Cotización en PDF",
                    data=bytes(generar_pdf()),
                    file_name=f"Cotizacion_{proyecto.replace(' ', '_')}.pdf",
                    mime="application/pdf"
                )
            except Exception as e:
                st.error(f"Error generando el PDF: {e}")

    with col_der_res:
        st.markdown("#### 📊 Distribución de la Utilidad Retenida")
        if utilidad_total > 0:
            data_grafico = {
                "Sección": ["Equipos Principales", "Materiales e Insumos", "Mano de Obra"],
                "Utilidad ($)": [max(0.0, utilidad_equipos), max(0.0, utilidad_materiales), max(0.0, utilidad_mo)]
            }
            fig = px.pie(pd.DataFrame(data_grafico), values="Utilidad ($)", names="Sección", hole=0.3)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Agrega componentes con margen para visualizar utilidades.")
