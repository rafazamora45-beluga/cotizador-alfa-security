import streamlit as st
import pandas as pd

# 1. INICIALIZACIÓN ABSOLUTA DEL ESTADO DE LA SESIÓN
if "equipos" not in st.session_state:
    st.session_state["equipos"] = []
if "materiales" not in st.session_state:
    st.session_state["materiales"] = []

# Inicialización segura del bloque de Mano de Obra
if "mano_obra_bloque" not in st.session_state:
    st.session_state["mano_obra_bloque"] = {
        "Costo Interno": 0.0,
        "Rentabilidad Aplicada (%)": 20.0,
        "Detalle": {
            "Servicio de Configuración Especializada": 0.0,
            "Servicio de Técnico Instalador": 0.0,
            "Logística de Estadía fuera de San Salvador": 0.0,
            "Viáticos de Alimentación y Campo": 0.0,
            "Soporte de Técnico Outsourcing": 0.0,
            "Servicio Técnico Nocturno / Fin de Semana": 0.0,
            "Movilización y Combustible del Proyecto": 0.0
        }
    }

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

# --- PESTAÑA 1: EQUIPOS PRINCIPALES ---
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
        
        st.markdown(" ")
        col_btn1, col_btn2 = st.columns([3, 10])
        
        if col_btn1.button("🗑️ Aplicar Eliminación de Marcados"):
            st.session_state["equipos"] = [eq for eq in st.session_state["equipos"] if not eq["Borrar"]]
            st.success("Equipos eliminados correctamente.")
            st.rerun()
                
        if col_btn2.button("Limpiar Toda la Lista", key="btn_clear_eq"):
            st.session_state["equipos"] = []
            st.rerun()

# --- PESTAÑA 2: BUSCADOR FREUND ---
with tab2:
    st.subheader("Conexión de Catálogo (Ferretería Freund)")
    buscar_termino = st.text_input("¿Qué material o SKU necesitas buscar?", placeholder="Ej. tuberia emt")
    
    materiales_respaldo = [
        {"sku": "1413211", "name": "TUBO CONDUIT EMT GALVANIZADO 3/4 PLG (6MT)", "price": 4.25},
        {"sku": "24847137", "name": "UNION EMT PRESION 3/4 PLG", "price": 0.95},
        {"sku": "2718137", "name": "UNION TUBO EMT 3/4 PLG", "price": 0.65},
        {"sku": "522421", "name": "CONECTOR RECTO EMT A CAJA 1 PLG", "price": 0.85},
        {"sku": "643907", "name": "ABRAZADERA 4 A 5 PLG X 1/4X1 1/2 POSTE PAR", "price": 4.25}
    ]
    
    if buscar_termino:
        coincidencias = [m for m in materiales_respaldo if buscar_termino.lower() in m["name"].lower()]
        if coincidencias:
            for i, m in enumerate(coincidencias):
                col_desc, col_accion = st.columns([3, 2])
                col_desc.markdown(f"**{m['name']}** - Costo: ${m['price']:.2f}")
                cant_m = col_accion.number_input("Cantidad", min_value=1, value=1, key=f"f_cant_{i}")
                if col_accion.button("Agregar", key=f"f_btn_{i}"):
                    p_v = m['price'] / (1 - 0.40)
                    st.session_state["materiales"].append({
                        "Borrar": False,
                        "Descripción": m['name'],
                        "Cantidad": cant_m,
                        "Costo Unitario ($)": m['price'],
                        "Costo Total ($)": m['price'] * cant_m,
                        "Rentabilidad (%)": 40.0,
                        "Precio Venta U ($)": p_v,
                        "Precio Venta Total ($)": p_v * cant_m
                    })
                    st.success("Agregado al costeo.")

# --- PESTAÑA 3: MANO DE OBRA ---
with tab3:
    st.subheader("🛠️ Presupuesto de Mano de Obra, Viáticos y Herramientas")
    st.info("Configura los costos operativos globales. El bloque técnico calcula por defecto una rentabilidad del 20% editable.")

    col_izq, col_der = st.columns([1, 1])

    with col_izq:
        st.markdown("#### ⚙️ 1. Personal Técnico y Logística")
        rent_mo = st.number_input("Rentabilidad Comercial del Bloque (%)", min_value=0.0, max_value=99.0, value=20.0, step=5.0, key="rent_mo_p3")

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
            tarifa_inst = st.number_input("Costo Diario Instalador ($)", min_value=0.0, value=25.0)
            
            st.markdown("---")
            st.markdown("**Viáticos y Estadías:**")
            c5, c6 = st.columns(2)
            dias_estadia = c5.number_input("Días Estadía fuera de SS", min_value=0, value=0)
            costo_estadia = c6.number_input("Costo Diario Estadía ($)", min_value=0.0, value=0.0)
            
            c7, c8 = st.columns(2)
            dias_viaticos = c7.number_input("Días de Viáticos", min_value=0, value=0)
            costo_viaticos = c8.number_input("Costo Diario Viáticos ($)", min_value=0.0, value=0.0)
            
            st.markdown("---")
            st.markdown("**Soporte Especializado:**")
            c9, c10 = st.columns(2)
            dias_out = c9.number_input("Días Técnico Outsourcing", min_value=0, value=0)
            costo_out = c10.number_input("Costo Diario Outsourcing ($)", min_value=0.0, value=0.0)
            
            c11, c12 = st.columns(2)
            dias_noc = c11.number_input("Días Técnico Nocturno / Fin de Semana", min_value=0, value=0)
            costo_noc = c12.number_input("Costo Diario Nocturno ($)", min_value=0.0, value=0.0)
            
            st.markdown("---")
            st.markdown("**Movilización:**")
            col_km1, col_km2 = st.columns(2)
            kms_proyecto = col_km1.number_input("Kilómetros totales a recorrer (KM)", min_value=0.0, value=0.0)
            costo_por_km = col_km2.number_input("Precio / Costo por Kilómetro ($)", min_value=0.0, value=0.36, step=0.05, format="%.2f")
            
            btn_guardar_mo = st.form_submit_button("Guardar Bloque Operativo")

            if btn_guardar_mo:
                c_conf_tot = float(cant_conf * dias_conf * tarifa_conf)
                c_inst_tot = float(cant_inst * dias_inst * tarifa_inst)
                c_est_tot = float(dias_estadia * costo_estadia)
                c_via_tot = float(dias_viaticos * costo_viaticos)
                c_out_tot = float(dias_out * costo_out)
                c_noc_tot = float(dias_noc * costo_noc)
                c_comb_tot = float(kms_proyecto * costo_por_km)
                
                costo_operativo_total = c_conf_tot + c_inst_tot + c_est_tot + c_via_tot + c_out_tot + c_noc_tot + c_comb_tot
                
                st.session_state["mano_obra_bloque"] = {
                    "Costo Interno": costo_operativo_total,
                    "Rentabilidad Aplicada (%)": rent_mo,
                    "Detalle": {
                        "Servicio de Configuración Especializada": c_conf_tot,
                        "Servicio de Técnico Instalador": c_inst_tot,
                        "Logística de Estadía fuera de San Salvador": c_est_tot,
                        "Viáticos de Alimentación y Campo": c_via_tot,
                        "Soporte de Técnico Outsourcing": c_out_tot,
                        "Servicio Técnico Nocturno / Fin de Semana": c_noc_tot,
                        "Movilización y Combustible del Proyecto": c_comb_tot
                    }
                }
                st.success("¡Costos calculados y retenidos!")

    with col_der:
        st.markdown("#### 🔧 2. Certificaciones y Herramientas Especiales")
        with st.form("form_herramientas"):
            c_desc = st.text_input("Descripción del Item", placeholder="Ej. Certificación o Alquiler de Andamios")
            c_monto = st.number_input("Costo Total ($)", min_value=0.0, value=0.0)
            btn_add_h = st.form_submit_button("Agregar Herramienta")
            
            if btn_add_h and c_desc:
                st.session_state["materiales"].append({
                    "Borrar": False,
                    "Descripción": f"[HERRAMIENTA] {c_desc}",
                    "Cantidad": 1,
                    "Costo Unitario ($)": float(c_monto),
                    "Costo Total ($)": float(c_monto),
                    "Rentabilidad (%)": 0.0,
                    "Precio Venta U ($)": float(c_monto),
                    "Precio Venta Total ($)": float(c_monto)
                })
                st.success("Agregado al proyecto.")

        items_h = [x for x in st.session_state["materiales"] if x["Descripción"].startswith("[HERRAMIENTA]")]
        if items_h:
            st.dataframe(pd.DataFrame(items_h)[["Descripción", "Costo Total ($)"]], hide_index=True, use_container_width=True)
            if st.button("Limpiar Herramientas"):
                st.session_state["materiales"] = [x for x in st.session_state["materiales"] if not x["Descripción"].startswith("[HERRAMIENTA]")]
                st.rerun()

    # Cálculo dinámico de totales para la pestaña
    mo_datos = st.session_state["mano_obra_bloque"]
    costo_interno_personal = mo_datos["Costo Interno"]
    rent_actual_pct = mo_datos["Rentabilidad Aplicada (%)"] / 100.0
    precio_cliente_personal = costo_interno_personal / (1 - rent_actual_pct) if rent_actual_pct < 1 else costo_interno_personal
    total_herramientas = sum(x["Costo Total ($)"] for x in st.session_state["materiales"] if x["Descripción"].startswith("[HERRAMIENTA]"))
    
    gran_costo_interno_mo = costo_interno_personal + total_herramientas
    gran_precio_cliente_mo = precio_cliente_personal + total_herramientas

    st.markdown("---")
    st.markdown("### 📊 Balance de Costo de Operación de Mano de Obra")
    cb1, cb2 = st.columns(2)
    cb1.metric("A MÍ ME CUESTA (Costo Interno)", f"${gran_costo_interno_mo:,.2f}")
    cb2.metric("AL CLIENTE LE CUESTA (Precio Venta)", f"${gran_precio_cliente_mo:,.2f}")

# --- PESTAÑA 4: RESUMEN COMERCIAL Y LIQUIDACIÓN ---
with tab4:
    st.subheader("📊 Resumen General de Cotización y Liquidación")
    
    lista_eq = st.session_state.get("equipos", [])
    lista_mat = [x for x in st.session_state.get("materiales", []) if not x["Descripción"].startswith("[HERRAMIENTA]")]
    items_herramientas = [x for x in st.session_state.get("materiales", []) if x["Descripción"].startswith("[HERRAMIENTA]")]
    
    costo_equipos = sum(x.get("Costo Total ($)", 0.0) for x in lista_eq)
    venta_equipos = sum(x.get("Precio Venta Total ($)", 0.0) for x in lista_eq)
    
    costo_materiales = sum(x.get("Costo Total ($)", 0.0) for x in lista_mat)
    venta_materiales = sum(x.get("Precio Venta Total ($)", 0.0) for x in lista_mat)
    
    # Procesamiento del desglose de servicios individuales
    mo_datos_global = st.session_state["mano_obra_bloque"]
    rent_mo_pct = mo_datos_global["Rentabilidad Aplicada (%)"] / 100.0
