
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
if "mano_obra_items" not in st.session_state:
    st.session_state["mano_obra_items"] = []

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
    "🛠️ Mano de Obra y Logística", 
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
        
        if col_btn1.button("🗑️ Aplicar Eliminación de Marcados", key="del_eq_btn"):
            st.session_state["equipos"] = [eq for eq in st.session_state["equipos"] if not eq["Borrar"]]
            st.success("Actualizado correctamente.")
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

# --- PESTAÑA 3: MANO DE OBRA Y LOGÍSTICA (NUEVO MODELO DE COMPONENTES SEPARADOS) ---
with tab3:
    st.subheader("🛠️ Presupuesto Dinámico de Mano de Obra, Viáticos y Logística")
    st.info("Agrega los rubros uno por uno. Podrás modificar la rentabilidad, días o costos directamente en la tabla.")

    # Formulario dinámico de ingreso por ítem
    with st.form("form_registro_mo"):
        col_tipo, col_cant, col_dias, col_costo, col_rent = st.columns([3, 1, 1, 1, 1])
        
        tipo_item = col_tipo.selectbox("Tipo de Rubro Operativo", [
            "Configurador", 
            "Técnico Instalador", 
            "Estadía fuera de SS", 
            "Viáticos", 
            "Técnico Outsourcing", 
            "Técnico Nocturno / Fin de Semana",
            "Combustible (Movilización)",
            "Certificaciones y Herramientas Especiales"
        ])
        
        cant = col_cant.number_input("Cantidad / Personal", min_value=1, value=1)
        dias = col_dias.number_input("Días / Unidades", min_value=1, value=1)
        
        # Costos sugeridos adaptativos
        costo_def = 25.0
        if "Configurador" in tipo_item: costo_def = 50.0
        elif "Combustible" in tipo_item: costo_def = 0.36  # CORREGIDO: Costo de KM totalmente editable de entrada
        elif "Certificaciones" in tipo_item: costo_def = 100.0
        
        costo_u = col_costo.number_input("Costo Unitario ($)", min_value=0.0, value=costo_def, step=1.0)
        
        # Rentabilidad sugerida (20% para técnicos, 0% para herramientas directas)
        rent_def = 0.0 if "Certificaciones" in tipo_item else 20.0
        rent_u = col_rent.number_input("Rentabilidad (%)", min_value=0.0, max_value=99.0, value=rent_def, step=5.0)
        
        btn_add_mo = st.form_submit_button("⚡ Agregar Rubro Operativo")
        
        if btn_add_mo:
            # Para combustible o viáticos globales, multiplicamos cantidad * unidades * costo unitario
            costo_total_i = cant * dias * costo_u
            m_dec = rent_u / 100.0
            precio_v_u = (costo_u * dias) / (1 - m_dec) if m_dec < 1 else (costo_u * dias)
            
            # Si es herramienta va sin margen
            if "Certificaciones" in tipo_item:
                precio_v_u = costo_u * dias
                rent_u = 0.0

            st.session_state["mano_obra_items"].append({
                "Borrar": False,
                "Rubro": tipo_item,
                "Cantidad (Pers)": int(cant),
                "Días / Factor": int(dias),
                "Costo Base Unitario ($)": float(costo_u),
                "Costo Total Interno ($)": float(costo_total_i),
                "Rentabilidad (%)": float(rent_u),
                "Precio Venta Total ($)": float(precio_v_u * cant)
            })
            st.success(f"Agregado de forma independiente: {tipo_item}")

    # Tabla Interactiva de Mano de Obra
    if st.session_state["mano_obra_items"]:
        st.markdown("#### 📊 Tabla de Distribución de Mano de Obra")
        st.caption("Puedes cambiar los costos, la cantidad de días o la rentabilidad celda por celda directamente en la cuadrícula.")
        
        df_mo_orig = pd.DataFrame(st.session_state["mano_obra_items"])
        
        df_mo_editado = st.data_editor(
            df_mo_orig,
            hide_index=True,
            use_container_width=True,
            disabled=["Rubro", "Costo Total Interno ($)", "Precio Venta Total ($)"],
            column_config={
                "Borrar": st.column_config.CheckboxColumn("Borrar", default=False),
                "Cantidad (Pers)": st.column_config.NumberColumn("Cantidad", min_value=1, step=1),
                "Días / Factor": st.column_config.NumberColumn("Días / Cant. KM", min_value=1, step=1),
                "Costo Base Unitario ($)": st.column_config.NumberColumn("Costo Unitario ($)", format="$%.2f"),
                "Rentabilidad (%)": st.column_config.NumberColumn("Rentabilidad (%)", min_value=0, max_value=99),
                "Costo Total Interno ($)": st.column_config.NumberColumn(format="$%.2f"),
                "Precio Venta Total ($)": st.column_config.NumberColumn(format="$%.2f")
            }
        )
        
        # Recálculo de fórmulas dinámicas sobre la marcha de la tabla de MO
        for i in range(len(df_mo_editado)):
            c_pers = df_mo_editado.at[i, "Cantidad (Pers)"]
            d_fact = df_mo_editado.at[i, "Días / Factor"]
            c_base = df_mo_editado.at[i, "Costo Base Unitario ($)"]
            r_pct = df_mo_editado.at[i, "Rentabilidad (%)"] / 100.0
            
            # Recalcular Costo Interno Real
            c_tot_int = c_pers * d_fact * c_base
            df_mo_editado.at[i, "Costo Total Interno ($)"] = c_tot_int
            
            # Recalcular Venta Final al Cliente
            p_v_u_rec = (c_base * d_fact) / (1 - r_pct) if r_pct < 1 else (c_base * d_fact)
            df_mo_editado.at[i, "Precio Venta Total ($)"] = p_v_u_rec * c_pers

        st.session_state["mano_obra_items"] = df_mo_editado.to_dict(orient="records")
        
        # Botones de control para la tabla de MO
        st.markdown(" ")
        col_mo_b1, col_mo_b2 = st.columns([3, 10])
        if col_mo_b1.button("🗑️ Eliminar Rubros Seleccionados", key="del_mo_btn"):
            st.session_state["mano_obra_items"] = [x for x in st.session_state["mano_obra_items"] if not x["Borrar"]]
            st.success("Tabla de mano de obra actualizada.")
            st.rerun()
            
        if col_mo_b2.button("Limpiar Tabla Operativa", key="clear_mo_all"):
            st.session_state["mano_obra_items"] = []
            st.rerun()

        # Desglose Financiero Integrado de la pestaña
        st.markdown("---")
        total_costo_a_mi = sum(x["Costo Total Interno ($)"] for x in st.session_state["mano_obra_items"])
        total_venta_cliente = sum(x["Precio Venta Total ($)"] for x in st.session_state["mano_obra_items"])
        
        st.markdown("### 📊 Balance Financiero de la Pestaña")
        c_kpi1, c_kpi2, c_kpi3 = st.columns(3)
        c_kpi1.metric("A MÍ ME CUESTA (Costo Interno)", f"${total_costo_a_mi:,.2f}")
        c_kpi2.metric("AL CLIENTE LE CUESTA (Precio Venta)", f"${total_venta_cliente:,.2f}")
        c_kpi3.metric("MARGEN RETENIDO ($)", f"${(total_venta_cliente - total_costo_a_mi):,.2f}")

# --- PESTAÑA 4: LIQUIDACIÓN COMERCIAL TOTAL Y RESUMEN ---
with tab4:
    st.subheader("📊 Resumen General de Cotización y Liquidación")
    
    lista_eq = st.session_state.get("equipos", [])
    lista_mat = st.session_state.get("materiales", [])
    lista_mo = st.session_state.get("mano_obra_items", [])
    
    # Consolidados Económicos por categoría
    costo_equipos = sum(x.get("Costo Total ($)", 0.0) for x in lista_eq)
    venta_equipos = sum(x.get("Precio Venta Total ($)", 0.0) for x in lista_eq)
    
    costo_materiales = sum(x.get("Costo Total ($)", 0.0) for x in lista_mat)
    venta_materiales = sum(x.get("Precio Venta Total ($)", 0.0) for x in lista_mat)
    
    costo_mo_tot = sum(x.get("Costo Total Interno ($)", 0.0) for x in lista_mo)
    venta_mo_tot = sum(x.get("Precio Venta Total ($)", 0.0) for x in lista_mo)
    
    # Totales absolutos del proyecto completo
    costo_total_proyecto = costo_equipos + costo_materiales + costo_mo_tot
    subtotal_venta_proyecto = venta_equipos + venta_materiales + venta_mo_tot
    
    iva_calc = subtotal_venta_proyecto * 0.13
    total_general_cliente = subtotal_venta_proyecto + iva_calc
    
    st.markdown("#### 🔒 Panel Privado Alfa Security")
    c_liq1, c_liq2, c_liq3 = st.columns(3)
    c_liq1.metric("Costo Total Operativo Interno", f"${costo_total_proyecto:,.2f}")
    c_liq2.metric("Precio de Venta (Subtotal)", f"${subtotal_venta_proyecto:,.2f}")
    c_liq3.metric("Utilidad Total Retenida", f"${(subtotal_venta_proyecto - costo_total_proyecto):,.2f}")
    
    st.markdown("---")
    st.markdown("#### 📄 Datos de cara al Cliente para la Propuesta")
    st.write(f"**Proyecto:** {proyecto} | **Empresa:** {empresa} | **Atención:** {atencion}")
    
    resumen_cliente = {
        "Descripción del Rubro": ["Suministro de Equipos de Seguridad", "Materiales e Insumos de Canalización", "Ingeniería, Mano de Obra y Logística"],
        "Monto ($)": [venta_equipos, venta_materiales, venta_mo_tot]
    }
    st.table(pd.DataFrame(resumen_cliente))
    
    col_f1, col_f2 = st.columns(2)
    col_f1.markdown(f"""
    * **Términos de Pago:** {pago}
    * **Validez de Oferta:** {validez}
    """)
    col_f2.markdown(f"""
    * **SUBTOTAL:** ${subtotal_venta_proyecto:,.2f}
    * **IVA (13%):** ${iva_calc:,.2f}
    * **TOTAL NETO:** **${total_general_cliente:,.2f}**
    """)
