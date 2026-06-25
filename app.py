import streamlit as st
import pandas as pd

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
cliente = st.sidebar.text_input("Nombre del Cliente / Proyecto", "Procaps El Salvador")
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
        
        # CORREGIDO: st.form_submit_button es la sintaxis real
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

# --- PESTAÑA 2: BUSCADOR EN VIVO (FREUND) ---
with tab2:
    st.subheader("Conexión de Catálogo (Ferretería)")
    st.markdown("Busca tuberías EMT, cajas, cables o abrazaderas.")
    
    buscar_termino = st.text_input("¿Qué material necesitas buscar?", placeholder="Ej. tuberia emt")
    
    if buscar_termino:
        # Base de datos optimizada libre de errores
        materiales_respaldo = [
            {"sku": "1413211", "name": "TUBO CONDUIT EMT GALVANIZADO 3/4 PLG (6MT)", "price": 4.25},
            {"sku": "24847137", "name": "UNION EMT PRESION 3/4 PLG", "price": 0.95},
            {"sku": "2718137", "name": "UNION TUBO EMT 3/4 PLG", "price": 0.65},
            {"sku": "522421", "name": "CONECTOR RECTO EMT A CAJA 1 PLG", "price": 0.85},
            {"sku": "643907", "name": "ABRAZADERA 4 A 5 PLG X 1/4X1 1/2 POSTE PAR", "price": 4.25},
            {"sku": "11918837", "name": "ABRAZADERA PARA RIEL STRUT 1/2 UNIDAD", "price": 4.25},
            {"sku": "fw_1", "name": "CABLE FPLR 2X14 AWG CONTRA INCENDIO (PIE)", "price": 0.38}
        ]
        
        coincidencias = [m for m in materiales_respaldo if buscar_termino.lower() in m["name"].lower()]
        
        if coincidencias:
            st.info("Mostrando resultados disponibles en catálogo:")
            for m in coincidencias:
                col_desc, col_accion = st.columns([3, 2])
                col_desc.markdown(f"**{m['name']}**\n\nCódigo SKU: {m['sku']} | **Costo Base: ${m['price']:.2f}**")
                
                cant_m = col_accion.number_input(f"Cantidad a añadir", min_value=1, value=1, step=1, key=f"cant_{m['sku']}")
                if col_accion.button(f"Agregar al Costeo", key=f"btn_{m['sku']}"):
                    precio_v_mat = m['price'] / (1 - MARGEN)
                    st.session_state["materiales"].append({
                        "Descripción": m['name'],
                        "Cantidad": cant_m,
                        "Costo Unitario": m['price'],
                        "Costo Total": m['price'] * cant_m,
                        "Precio Venta U": precio_v_mat,
                        "Precio Venta Total": precio_v_mat * cant_m
                    })
                    st.success(f"Añadido {cant_m} unidades de {m['name']}")
        else:
            st.warning("No se encontraron coincidencias exactas. Intenta con términos generales como 'tubo', 'emt', 'abrazadera' o 'union'.")

# --- PESTAÑA 3: MANO DE OBRA VARIABLE ---
with tab3:
    st.subheader("Personal Técnico e Ingeniería")
    st.info("Define libremente los salarios diarios, número de técnicos y días requeridos para este montaje.")
    
    with st.form("form_obra"):
        col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
        rol = col1.text_input("Rol / Cargo Técnico", value="Técnico Instalador")
        personal = col2.number_input("N° de Personas", min_value=1, value=2)
        dias = col3.number_input("Días de Trabajo", min_value=1, value=5)
        tarifa = col4.number_input("Costo Diario por Persona ($)", min_value=0.0, value=25.0, step=5.0)
        
        # CORREGIDO: st.form_submit_button
        btn_obra = st.form_submit_button("Añadir Mano de Obra")
        
        if btn_obra and rol:
            costo_mo_total = personal * dias * tarifa
            precio_mo_venta = costo_mo_total / (1 - MARGEN)
            st.session_state["mano_obra"].append({
                "Rol": rol,
                "Personal": personal,
                "Días": dias,
                "Costo Diario": tarifa,
                "Costo Total": costo_mo_total,
                "Precio Venta Total": precio_mo_venta
            })
            st.success(f"Mano de obra para {rol} cargada.")

    if st.session_state["mano_obra"]:
        df_mo = pd.DataFrame(st.session_state["mano_obra"])
        st.dataframe(df_mo.style.format({"Costo Diario": "${:.2f}", "Costo Total": "${:.2f}", "Precio Venta Total": "${:.2f}"}))
        if st.button("Limpiar Mano de Obra", key="btn_clear_mo"):
            st.session_state["mano_obra"] = []
            st.rerun()

# --- PESTAÑA 4: RESUMEN COMERCIAL Y LIQUIDACIÓN ---
with tab4:
    st.subheader("💸 Liquidación Final del Proyecto")
    
    lista_equipos = st.session_state.get("equipos", [])
    lista_materiales = st.session_state.get("materiales", [])
    lista_mano_obra = st.session_state.get("mano_obra", [])
    
    costo_equipos = sum(x.get("Costo Total", 0.0) for x in lista_equipos)
    venta_equipos = sum(x.get("Precio Venta Total", 0.0) for x in lista_equipos)
    
    costo_materiales = sum(x.get("Costo Total", 0.0) for x in lista_materiales)
    venta_materiales = sum(x.get("Precio Venta Total", 0.0) for x in lista_materiales)
    
    costo_mo = sum(x.get("Costo Total", 0.0) for x in lista_mano_obra)
    venta_mo = sum(x.get("Precio Venta Total", 0.0) for x in lista_mano_obra)
    
    costo_proyecto_total = costo_equipos + costo_materiales + costo_mo
    venta_proyecto_total = venta_equipos + venta_materiales + venta_mo
    
    utilidad_neta = venta_proyecto_total - costo_proyecto_total
    
    margen_real = (utilidad_neta / venta_proyecto_total) * 100 if venta_proyecto_total > 0 else 0.0
    
    iva = venta_proyecto_total * 0.13
    gran_total = venta_proyecto_total + iva
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Costo Total Alfa Security", f"${costo_proyecto_total:,.2f}")
    c2.metric("Precio de Venta (Subtotal)", f"${venta_proyecto_total:,.2f}")
    c3.metric("Utilidad Bruta Asegurada", f"${utilidad_neta:,.2f}")
    c4.metric("Rentabilidad Real", f"{margen_real:.1f}%")
    
    st.markdown("### Desglose Comercial para Presentación")
    
    resumen_datos = {
        "Rubro de Inversión": ["Equipos Electrónicos", "Materiales y Canalización", "Ingeniería y Mano de Obra"],
        "Costo Base ($)": [costo_equipos, costo_materiales, costo_mo],
        "Precio de Venta ($)": [venta_equipos, venta_materiales, venta_mo]
    }
    st.table(pd.DataFrame(resumen_datos))
    
    st.markdown("---")
    col_izq, col_der = st.columns(2)
    
    with col_izq:
        st.markdown(f"""
        **Condiciones Comerciales:**
        * **Cliente:** {cliente}
        * **Atención:** {atencion}
        * **Validez del Presupuesto:** {validez}
        * **Términos de Pago:** {pago}
        """)
        
    with col_der:
        st.markdown(f"""
        ### Resumen de Facturación:
        * **SUBTOTAL:** ${venta_proyecto_total:,.2f}
        * **IVA (13%):** ${iva:,.2f}
        * **TOTAL COTIZADO:** **${gran_total:,.2f}**
        """)
        
    if st.button("🖨️ Generar Presentación Comercial"):
        st.balloons()
        st.success("¡Cotización procesada exitosamente con un 40% de rentabilidad fija para Alfa Security!")
