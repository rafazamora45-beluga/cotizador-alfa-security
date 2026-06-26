import streamlit as st
import pandas as pd
import plotly.express as px
from fpdf import FPDF
import requests
from bs4 import BeautifulSoup
import os

# Configuración de la interfaz
st.set_page_config(page_title="Cotizador Inteligente - Alfa Security", layout="wide")

# 1. INICIALIZACIÓN DE VARIABLES GLOBALES EN SESIÓN
if "equipos" not in st.session_state:
    st.session_state["equipos"] = []
if "materiales" not in st.session_state:
    st.session_state["materiales"] = []
if "servicios_mo" not in st.session_state:
    st.session_state["servicios_mo"] = []
if "resultados_scraping" not in st.session_state:
    st.session_state["resultados_scraping"] = []

st.title("🛡️ Sistema de Cotizaciones Automáticas — Alfa Security")
st.markdown("---")

# =========================================================================
# MOTOR DE SCRAPING PURO — DE CARA A LA WEB DE FREUND EN TIEMPO REAL
# =========================================================================
def raspado_puro_freund(termino_busqueda):
    """
    Realiza una búsqueda real en la web de Freund usando su buscador global,
    parsea los resultados dinámicamente y extrae foto, SKU, nombre y precio unitario.
    """
    if not termino_busqueda.strip():
        return []
        
    # Formateamos el término para la URL de la ferretería
    url_busqueda = f"https://www.freundferreteria.com/buscar?text={termino_busqueda.strip().replace(' ', '%20')}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "es-SV,es;q=0.9,en;q=0.8"
    }
    
    resultados = []
    
    try:
        respuesta = requests.get(url_busqueda, headers=headers, timeout=10)
        if respuesta.status_code == 200:
            soup = BeautifulSoup(respuesta.text, "html.parser")
            
            # Buscamos el contenedor de las tarjetas de producto en el HTML de Freund
            # (Clases típicas de su catálogo: 'product-item', 'item-inner' o selectores de grid)
            tarjetas = soup.select(".product-item, .item-product, .product-card")
            
            # Si no encuentra por clase específica, buscamos contenedores genéricos de links de productos
            if not tarjetas:
                tarjetas = soup.find_all("div", class_="product-info") # Fallback estructural básico
                
            for tarjeta in tarjetas:
                try:
                    # 1. Extracción de Nombre
                    tag_nombre = tarjeta.select_one(".product-name, .title, h2, h3")
                    nombre = tag_nombre.text.strip().upper() if tag_nombre else "PRODUCTO SIN NOMBRE"
                    
                    # 2. Extracción de Enlace Completo
                    tag_link = tarjeta.find("a", href=True)
                    link_final = tag_link["href"] if tag_link else "#"
                    if link_final.startswith("/"):
                        link_final = "https://www.freundferreteria.com" + link_final
                        
                    # 3. Extracción de SKU (Freund suele ponerlo en texto secundario o data-attributes)
                    sku = "N/A"
                    tag_sku = tarjeta.select_one(".sku, .code, [data-sku]")
                    if tag_sku:
                        sku = tag_sku.text.replace("SKU:", "").replace("Código:", "").strip()
                    else:
                        # Intento alternativo de extraer SKU desde el enlace si viene al final
                        partes_url = link_final.split("/")
                        if partes_url[-1].isdigit():
                            sku = partes_url[-1]

                    # 4. Extracción de Imagen
                    tag_img = tarjeta.find("img")
                    url_img = None
                    if tag_img:
                        url_img = tag_img.get("data-src") or tag_img.get("src")
                        if url_img and url_img.startswith("/"):
                            url_img = "https://www.freundferreteria.com" + url_img
                    
                    # 5. Extracción de Precio Unitario Puro de la Tarjeta
                    precio = 0.0
                    tag_precio = tarjeta.select_one(".price, .current-price, .special-price, span.price-amount")
                    if tag_precio:
                        texto_precio = tag_precio.text.replace("$", "").replace(",", "").strip()
                        try:
                            precio = float(texto_precio)
                        except ValueError:
                            pass
                            
                    # Agregamos solo si logramos capturar datos esenciales de comercio
                    if precio > 0 or nombre != "PRODUCTO SIN NOMBRE":
                        resultados.append({
                            "sku": sku,
                            "name": nombre,
                            "price": precio if precio > 0 else 0.0,
                            "link": link_final,
                            "img": url_img
                        })
                except Exception:
                    continue
    except Exception as e:
        print(f"Error crítico en el raspado web: {e}")
        
    return resultados


# PANEL IZQUIERDO: LOGO Y DATOS GENERALES DEL PROYECTO
ruta_logo = "LOGO_ALFA-02.png"
if os.path.exists(ruta_logo):
    st.sidebar.image(ruta_logo, use_container_width=True)

st.sidebar.header("📋 Datos del Proyecto")
proyecto = st.sidebar.text_input("Nombre del Proyecto", "Instalación sistema de detección de incendios")
empresa = st.sidebar.text_input("Empresa", "Del Sur")
atencion = st.sidebar.text_input("Atención a:", "Rafael Zamora")
validez = st.sidebar.text_input("Validez de la Oferta", "20 días")
pago = st.sidebar.text_input("Condiciones de Pago", "60% Anticipo / 40% Contraentrega")

# PESTAÑAS PRINCIPALES DEL SISTEMA
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
                "Borrar": False,
                "Descripción": desc_eq.upper(),
                "Cantidad": int(cant_eq),
                "Costo Unitario ($)": float(costo_eq),
                "Costo Total ($)": float(costo_eq * cant_eq),
                "Rentabilidad (%)": float(rent_inicial),
                "Precio Venta U ($)": float(precio_venta_u),
                "Precio Venta Total ($)": float(precio_venta_u * cant_eq)
            })
            st.toast(f"Agregado: {desc_eq.upper()}")

    if st.session_state["equipos"]:
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
# --- PESTAÑA 2: MATERIALES (REDISEÑADA DESDE 0) ---
# ==========================================
with tab2:
    st.subheader("🏗️ Gestión Integrada de Materiales y Canalización")
    
    # Dividimos la sección superior en dos bloques: Buscador en Vivo y Carga Manual
    col_izq, col_der = st.columns([5, 4])
    
    with col_izq:
        st.markdown("#### 🔍 Scraping en Vivo — Servidor Freund")
        input_busqueda = st.text_input("Buscar insumo en Freund", placeholder="Ej. tubo, union, curva, caja conduit...")
        
        if st.button("🚀 Ejecutar Búsqueda Real"):
            if input_busqueda:
                with st.spinner(f"Escaneando catálogo web para '{input_busqueda}'..."):
                    st.session_state["resultados_scraping"] = raspado_puro_freund(input_busqueda)
                if not st.session_state["resultados_scraping"]:
                    st.warning("No se encontraron coincidencias directas en la web en este momento. Podés agregarlo manualmente al lado.")
            else:
                st.info("Por favor ingresá un término para buscar.")

    with col_der:
        st.markdown("#### ➕ Opción: Agregar Material Manual")
        with st.form("form_material_manual"):
            m_desc = st.text_input("Descripción del Material / Insumo")
            c1, c2 = st.columns(2)
            m_cant = c1.number_input("Cantidad", min_value=1, value=1)
            m_costo = c2.number_input("Costo por Unidad ($)", min_value=0.00, value=0.00, step=0.50)
            
            btn_manual = st.form_submit_button("Cargar Manualmente (Al 40%)")
            if btn_manual and m_desc:
                # Todo se calcula automáticamente bajo el 40% estricto de rentabilidad solicitado
                precio_v_u = m_costo / (1 - 0.40)
                st.session_state["materiales"].append({
                    "Borrar": False,
                    "Descripción": m_desc.upper(),
                    "Cantidad": int(m_cant),
                    "Costo Unitario ($)": float(m_costo),
                    "Costo Total ($)": float(m_costo * m_cant),
                    "Rentabilidad (%)": 40.0,
                    "Precio Venta U ($)": float(precio_v_u),
                    "Precio Venta Total ($)": float(precio_v_u * m_cant)
                })
                st.toast(f"📥 Material manual cargado: {m_desc.upper()}")

    # DESPLIEGUE DE TARJETAS EXTRAÍDAS POR EL SCRAPER (Si existen)
    lista_scraping = st.session_state.get("resultados_scraping", [])
    if lista_scraping:
        st.markdown(f"---")
        st.markdown(f"##### 📊 Opciones encontradas en Freund en este instante ({len(lista_scraping)})")
        
        for idx, item in enumerate(lista_scraping):
            with st.container():
                col_img, col_info, col_pr, col_add = st.columns([1.2, 3.5, 1, 2])
                
                with col_img:
                    if item.get("img"):
                        st.image(item["img"], use_container_width=True)
                    else:
                        st.markdown('<div style="background-color:#1e222b;border:1px dashed #4e5565;border-radius:5px;height:80px;display:flex;align-items:center;justify-content:center;text-align:center;"><span style="color:#8a92a6;font-size:11px;">Sin Imagen</span></div>', unsafe_allow_html=True)
                
                with col_info:
                    st.markdown(f"**{item['name']}**")
                    st.markdown(f"`SKU: {item['sku']}`")
                    if item['link'] != "#":
                        st.markdown(f"[🔗 Abrir ficha web ↗]({item['link']})")
                
                with col_pr:
                    st.markdown(f"#### ${item['price']:.2f}")
                    
                with col_add:
                    cant_sc = st.number_input("Cant.", min_value=1, value=1, step=1, key=f"scr_cant_{idx}")
                    if st.button("📥 Sumar a Cotización", key=f"scr_btn_{idx}"):
                        # Aplicación estricta de rentabilidad del 40%
                        precio_v_u = item['price'] / (1 - 0.40)
                        st.session_state["materiales"].append({
                            "Borrar": False,
                            "Descripción": item['name'],
                            "Cantidad": int(cant_sc),
                            "Costo Unitario ($)": float(item['price']),
                            "Costo Total ($)": float(item['price'] * cant_sc),
                            "Rentabilidad (%)": 40.0,
                            "Precio Venta U ($)": float(precio_v_u),
                            "Precio Venta Total ($)": float(precio_v_u * cant_sc)
                        })
                        st.toast(f"✅ Cargado: {item['name']}")
                st.markdown("<div style='border-bottom:1px solid #2d3139;margin:8px 0;'></div>", unsafe_allow_html=True)

    # TABLA CENTRALIZADA ABAJO (ACUMULATIVA PARA LA COTIZACIÓN)
    st.markdown("---")
    st.markdown("### 🛒 Tabla Consolidada de Materiales Cargados")
    
    if st.session_state["materiales"]:
        df_m_orig = pd.DataFrame(st.session_state["materiales"])
        df_m_edit = st.data_editor(
            df_m_orig,
            hide_index=True,
            use_container_width=True,
            disabled=["Descripción", "Costo Unitario ($)", "Costo Total ($)", "Precio Venta U ($)", "Precio Venta Total ($)"],
            column_config={
                "Borrar": st.column_config.CheckboxColumn("Borrar", default=False),
                "Cantidad": st.column_config.NumberColumn("Cantidad", min_value=1, step=1),
                "Rentabilidad (%)": st.column_config.NumberColumn("Rentabilidad (%)", min_value=0, max_value=99, step=1),
            }
        )
        
        # Recálculo en caliente del editor de datos
        for i in range(len(df_m_edit)):
            r_pct = df_m_edit.at[i, "Rentabilidad (%)"] / 100.0
            c_uni = df_m_edit.at[i, "Costo Unitario ($)"]
            cant = df_m_edit.at[i, "Cantidad"]
            
            df_m_edit.at[i, "Costo Total ($)"] = c_uni * cant
            p_venta_u = c_uni / (1 - r_pct) if r_pct < 1 else c_uni
            df_m_edit.at[i, "Precio Venta U ($)"] = p_venta_u
            df_m_edit.at[i, "Precio Venta Total ($)"] = p_venta_u * cant
            
        st.session_state["materiales"] = df_m_edit.to_dict(orient="records")
        
        col_del_m, _ = st.columns([3, 10])
        if col_del_m.button("🗑️ Eliminar Materiales Seleccionados", key="btn_del_mat_real"):
            st.session_state["materiales"] = [m for m in st.session_state["materiales"] if not m["Borrar"]]
            st.rerun()
    else:
        st.info("No hay materiales cargados en el proyecto actualmente.")

# ==========================================
# --- PESTAÑA 3: MANO DE OBRA ---
# ==========================================
with tab3:
    st.subheader("🛠️ Presupuesto de Mano de Obra y Logística")
    col_izq_mo, col_der_mo = st.columns([1, 1])

    with col_izq_mo:
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
                            "Borrar": False,
                            "Descripción": nombre,
                            "Cantidad": float(cant),
                            "Costo Unitario ($)": float(costo_u),
                            "Costo Interno ($)": float(costo_tot),
                            "Rentabilidad (%)": float(rent_mo),
                            "Costo del Cliente U ($)": float(precio_v_u),
                            "Precio Venta Total ($)": float(precio_v_u * cant)
                        })
                st.rerun()

    with col_der_mo:
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
        if st.button("🗑️ Eliminar Servicios Seleccionados", key="del_mo_sel"):
            st.session_state["servicios_mo"] = [s for s in st.session_state["servicios_mo"] if not s["Borrar"]]
            st.rerun()

# ==========================================
# --- PESTAÑA 4: RESUMEN COMERCIAL ---
# ==========================================
with tab4:
    st.subheader("📊 Resumen General Comercial")
    
    lista_eq = st.session_state.get("equipos", [])
    lista_mat = st.session_state.get("materiales", [])
    lista_mo = st.session_state.get("servicios_mo", [])
    
    costo_equipos = sum(x.get("Costo Total ($)", 0.0) for x in lista_eq)
    venta_equipos = sum(x.get("Precio Venta Total ($)", 0.0) for x in lista_eq)
    
    costo_materiales = sum(x.get("Costo Total ($)", 0.0) for x in lista_mat)
    venta_materiales = sum(x.get("Precio Venta Total ($)", 0.0) for x in lista_mat)
    
    costo_mo_tot = sum(x.get("Costo Interno ($)", 0.0) for x in lista_mo)
    venta_mo_tot = sum(x.get("Precio Venta Total ($)", 0.0) for x in lista_mo)
    
    costo_total_proyecto = costo_equipos + costo_materiales + costo_mo_tot
    subtotal_venta_proyecto = venta_equipos + venta_materiales + venta_mo_tot
    utilidad_total = subtotal_venta_proyecto - costo_total_proyecto
    
    rentabilidad_real_pct = (utilidad_total / subtotal_venta_proyecto * 100) if subtotal_venta_proyecto > 0 else 0.0
    
    aplicar_iva = st.checkbox("Aplicar IVA (13%) a la oferta comercial", value=True)
    iva_calc = subtotal_venta_proyecto * 0.13 if aplicar_iva else 0.0
    total_general_cliente = subtotal_venta_proyecto + iva_calc
    
    st.markdown("---")
    c_res1, c_res2, c_res3 = st.columns(3)
    c_res1.metric("Costo Total Interno", f"${costo_total_proyecto:,.2f}")
    c_res2.metric("Precio Venta (Subtotal)", f"${subtotal_venta_proyecto:,.2f}")
    c_res3.metric("Rentabilidad Real Global", f"{rentabilidad_real_pct:.2f}%")
    
    tabla_final_items = []
    for eq in lista_eq:
        tabla_final_items.append({"Descripción del Rubro": f"Equipo: {eq['Descripción']} (Cant: {eq['Cantidad']})", "Monto ($)": eq["Precio Venta Total ($)"]})
    if venta_materiales > 0:
        tabla_final_items.append({"Descripción del Rubro": "Materiales e Insumos de Canalización (Canasta/Tuberías)", "Monto ($)": venta_materiales})
    if venta_mo_tot > 0:
        tabla_final_items.append({"Descripción del Rubro": "Mano de Obra, Configuración e Ingeniería de Campo", "Monto ($)": venta_mo_tot})
        
    if tabla_final_items:
        st.table(pd.DataFrame(tabla_final_items))
        st.markdown(f"**SUBTOTAL:** ${subtotal_venta_proyecto:,.2f} | **IVA (13%):** ${iva_calc:,.2f} | **TOTAL:** **${total_general_cliente:,.2f}**")
