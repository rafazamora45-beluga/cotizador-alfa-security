import streamlit as st
import pandas as pd
import plotly.express as px
from fpdf import FPDF
import io

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

# 2. PANEL IZQUIERDO: DATOS DEL PROYECTO
st.sidebar.header("📋 Datos del Proyecto")
proyecto = st.sidebar.text_input("Nombre del Proyecto", "Proyecto Procaps El Salvador")
empresa = st.sidebar.text_input("Empresa", "Alfa Security")
atencion = st.sidebar.text_input("Atención a:", "Ing. Miguel Melendez")
validez = st.sidebar.text_input("Validez de la Oferta", "15 Días")
pago = st.sidebar.text_input("Condiciones de Pago", "60% Anticipo / 40% Contraentrega")

# Creación limpia de las 4 pestañas
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

# ==========================================
# --- PESTAÑA 3: MANO DE OBRA ---
# ==========================================
with tab3:
    st.subheader("🛠️ Presupuesto de Mano de Obra, Viáticos y Herramientas")
    st.info("Configura los costos operativos globales. Al presionar 'Agregar al Balance', el servicio se sumará a la tabla interactiva inferior.")

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
                    st.success("¡Servicios inyectados exitosamente!")
                    st.rerun()
                else:
                    st.warning("No ingresaste cantidades válidas mayores a cero.")

    with col_der:
        st.markdown("#### 🔧 2. Certificaciones y Herramientas Especiales")
        with st.form("form_herramientas"):
            c_desc = st.text_input("Descripción del Item", placeholder="Ej. Certificación o Alquiler de Andamios")
            c_monto = st.number_input("Costo Total ($)", min_value=0.0, value=0.0)
            btn_add_h = st.form_submit_button("Agregar Herramienta")
            
            if btn_add_h and c_desc:
                st.session_state["servicios_mo"].append({
                    "Borrar": False,
                    "Descripción": f"[HERRAMIENTA] {c_desc}",
                    "Cantidad": 1.0,
                    "Costo Unitario ($)": float(c_monto),
                    "Costo Interno ($)": float(c_monto),
                    "Rentabilidad (%)": 0.0,
                    "Costo del Cliente U ($)": float(c_monto),
                    "Precio Venta Total ($)": float(c_monto)
                })
                st.success("Herramienta agregada a la tabla de balance.")
                st.rerun()

    st.markdown("---")
    st.markdown("### 📊 Balance del Costo de Operación de Mano de Obra")
    
    if st.session_state["servicios_mo"]:
        df_mo_original = pd.DataFrame(st.session_state["servicios_mo"])
        
        df_mo_editado = st.data_editor(
            df_mo_original,
            hide_index=True,
            use_container_width=True,
            disabled=["Descripción", "Costo Unitario ($)", "Costo Interno ($)", "Costo del Cliente U ($)", "Precio Venta Total ($)"],
            column_config={
                "Borrar": st.column_config.CheckboxColumn("Seleccionar para Borrar", default=False),
                "Cantidad": st.column_config.NumberColumn("Cantidad / Factor", min_value=0.0, step=0.5, format="%.2f"),
                "Rentabilidad (%)": st.column_config.NumberColumn("Rentabilidad (%)", min_value=0, max_value=99, step=1),
                "Costo Unitario ($)": st.column_config.NumberColumn(format="$%.2f"),
                "Costo Interno ($)": st.column_config.NumberColumn(format="$%.2f"),
                "Costo del Cliente U ($)": st.column_config.NumberColumn(format="$%.2f"),
                "Precio Venta Total ($)": st.column_config.NumberColumn(format="$%.2f"),
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
            st.success("Items operativos eliminados.")
            st.rerun()
            
        if col_mo_b2.button("Limpiar Tabla de Balance Completa", key="clear_mo_all"):
            st.session_state["servicios_mo"] = []
            st.rerun()
            
        gran_costo_interno_mo = sum(x["Costo Interno ($)"] for x in st.session_state["servicios_mo"])
        gran_precio_cliente_mo = sum(x["Precio Venta Total ($)"] for x in st.session_state["servicios_mo"])
        
        st.markdown(" ")
        cb1, cb2 = st.columns(2)
        cb1.metric("Costo Interno Total (Mano de Obra)", f"${gran_costo_interno_mo:,.2f}")
        cb2.metric("Precio de Venta Total (Cliente)", f"${gran_precio_cliente_mo:,.2f}")
    else:
        st.info("No hay registros en la tabla de balance de operación.")

# ==========================================
# --- PESTAÑA 4: RESUMEN COMERCIAL ---
# ==========================================
with tab4:
    st.subheader("📊 Resumen General Comercial")
    
    lista_eq = st.session_state.get("equipos", [])
    lista_mat = st.session_state.get("materiales", [])
    lista_mo = st.session_state.get("servicios_mo", [])
    
    # Costos y ventas cruzadas por sección
    costo_equipos = sum(x.get("Costo Total ($)", 0.0) for x in lista_eq)
    venta_equipos = sum(x.get("Precio Venta Total ($)", 0.0) for x in lista_eq)
    utilidad_equipos = venta_equipos - costo_equipos
    
    costo_materiales = sum(x.get("Costo Total ($)", 0.0) for x in lista_mat)
    venta_materiales = sum(x.get("Precio Venta Total ($)", 0.0) for x in lista_mat)
    utilidad_materiales = venta_materiales - costo_materiales
    
    costo_mo_tot = sum(x.get("Costo Interno ($)", 0.0) for x in lista_mo)
    venta_mo_tot = sum(x.get("Precio Venta Total ($)", 0.0) for x in lista_mo)
    utilidad_mo = venta_mo_tot - costo_mo_tot
    
    # Consolidados finales del proyecto
    costo_total_proyecto = costo_equipos + costo_materiales + costo_mo_tot
    subtotal_venta_proyecto = venta_equipos + venta_materiales + venta_mo_tot
    utilidad_total = subtotal_venta_proyecto - costo_total_proyecto
    
    rentabilidad_real_pct = (utilidad_total / subtotal_venta_proyecto * 100) if subtotal_venta_proyecto > 0 else 0.0
    
    # --- NUEVO: Checkbox interactivo para aplicar o no el IVA ---
    st.markdown("#### ⚙️ Impuestos")
    aplicar_iva = st.checkbox("Aplicar IVA (13%) a la oferta comercial", value=True)
    iva_calc = subtotal_venta_proyecto * 0.13 if aplicar_iva else 0.0
    total_general_cliente = subtotal_venta_proyecto + iva_calc
    
    st.markdown("---")
    
    # KPI de Rentabilidades Objetivo vs Real
    st.markdown("#### 🎯 Análisis de Rentabilidad y Objetivos")
    col_rent1, col_rent2, col_rent3 = st.columns(3)
    
    rent_objetivo = col_rent1.number_input("Fijar Rentabilidad Objetivo (%)", min_value=0.0, max_value=100.0, value=30.0, step=1.0)
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
        st.caption(f"**Proyecto:** {proyecto} | **Empresa:** {empresa} | **Atención:** {atencion}")
        
        # Estructuración visual de las secciones agrupadas como se pidió
        tabla_final_items = []
        
        # 1. Equipos detallados uno por uno
        for eq in lista_eq:
            tabla_final_items.append({
                "Descripción del Rubro": f"Equipo: {eq['Descripción']} (Cant: {eq['Cantidad']} x ${eq['Precio Venta U ($)']:.2f})",
                "Monto ($)": eq["Precio Venta Total ($)"]
            })
            
        # 2. Enunciado unificado para Mano de Obra
        if venta_mo_tot > 0:
            tabla_final_items.append({
                "Descripción del Rubro": "Mano de Obra (Incluye servicios técnicos, logística, certificaciones y herramientas)",
                "Monto ($)": venta_mo_tot
            })
            
        # 3. Enunciado unificado para Materiales y Suministros
        if venta_materiales > 0:
            tabla_final_items.append({
                "Descripción del Rubro": "Materiales y Suministros (Insumos de canalización y accesorios)",
                "Monto ($)": venta_materiales
            })
        
        if tabla_final_items:
            st.table(pd.DataFrame(tabla_final_items))
        else:
            st.warning("No hay rubros cargados todavía en la cotización.")
            
        col_f1, col_f2 = st.columns(2)
        col_f1.markdown(f"* **Términos de Pago:** {pago}\n* **Validez de Oferta:** {validez}")
        col_f2.markdown(f"* **SUBTOTAL:** ${subtotal_venta_proyecto:,.2f}\n* **IVA (13%):** ${iva_calc:,.2f}\n* **TOTAL NETO:** **${total_general_cliente:,.2f}**")

        # --- NUEVO: Motor de generación de PDF integrado ---
        def generar_pdf():
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            
            # Encabezado Alfa Security
            pdf.set_font("Arial", "B", 16)
            pdf.cell(200, 10, txt="ALFA SECURITY EL SALVADOR", ln=True, align="C")
            pdf.set_font("Arial", "", 12)
            pdf.cell(200, 10, txt="Oferta Económica Comercial", ln=True, align="C")
            pdf.ln(10)
            
            # Metadatos del Proyecto
            pdf.set_font("Arial", "B", 12)
            pdf.cell(200, 8, txt="Datos Generales:", ln=True)
            pdf.set_font("Arial", "", 11)
            pdf.cell(200, 6, txt=f"Proyecto: {proyecto}", ln=True)
            pdf.cell(200, 6, txt=f"Cliente / Empresa: {empresa}", ln=True)
            pdf.cell(200, 6, txt=f"Atención a: {atencion}", ln=True)
            pdf.cell(200, 6, txt=f"Validez de Oferta: {validez}", ln=True)
            pdf.cell(200, 6, txt=f"Condiciones de Pago: {pago}", ln=True)
            pdf.ln(8)
            
            # Tabla de Cotización
            pdf.set_font("Arial", "B", 12)
            pdf.cell(140, 8, txt="Descripción del Rubro / Componente", border=1)
            pdf.cell(50, 8, txt="Total ($)", border=1, ln=True, align="R")
            pdf.set_font("Arial", "", 10)
            
            # Detalle de Equipos Principales
            if lista_eq:
                pdf.set_font("Arial", "B", 10)
                pdf.cell(190, 6, txt="--- EQUIPOS PRINCIPALES (DETALLADO) ---", border=1, ln=True)
                pdf.set_font("Arial", "", 10)
                for eq in lista_eq:
                    txt_desc = f"{eq['Descripción']} (Cant: {eq['Cantidad']} x ${eq['Precio Venta U ($)']:.2f})"
                    pdf.cell(140, 6, txt=txt_desc, border=1)
                    pdf.cell(50, 6, txt=f"${eq['Precio Venta Total ($)']:.2f}", border=1, ln=True, align="R")
            
            # Bloque unificado de Mano de Obra
            if venta_mo_tot > 0:
                pdf.cell(140, 6, txt="Mano de Obra (Servicios técnicos, logística, certificaciones y herramientas)", border=1)
                pdf.cell(50, 6, txt=f"${venta_mo_tot:.2f}", border=1, ln=True, align="R")
                
            # Bloque unificado de Materiales y Suministros
            if venta_materiales > 0:
                pdf.cell(140, 6, txt="Materiales y Suministros", border=1)
                pdf.cell(50, 6, txt=f"${venta_materiales:.2f}", border=1, ln=True, align="R")
                
            pdf.ln(6)
            
            # Bloque de Cierre Económico
            pdf.set_font("Arial", "B", 11)
            pdf.cell(140, 6, txt="SUBTOTAL", align="R")
            pdf.cell(50, 6, txt=f"${subtotal_venta_proyecto:.2f}", border=1, ln=True, align="R")
            
            pdf.cell(140, 6, txt="IVA (13%)" if aplicar_iva else "IVA (0%)", align="R")
            pdf.cell(50, 6, txt=f"${iva_calc:.2f}", border=1, ln=True, align="R")
            
            pdf.cell(140, 6, txt="TOTAL NETO", align="R")
            pdf.set_font("Arial", "B", 12)
            pdf.cell(50, 6, txt=f"${total_general_cliente:.2f}", border=1, ln=True, align="R")
            
            return pdf.output(dest="S").encode("latin-1", errors="ignore")

        # Botón de Descarga Física del PDF
        pdf_bytes = generar_pdf()
        st.markdown(" ")
        st.download_button(
            label="📥 Descargar Cotización en PDF",
            data=pdf_bytes,
            file_name=f"Cotizacion_{proyecto.replace(' ', '_')}.pdf",
            mime="application/pdf"
        )

    with col_der_res:
        st.markdown("#### 📊 Distribución de la Utilidad Retenida")
        
        if utilidad_total > 0:
            data_grafico = {
                "Sección": ["Equipos Principales", "Materiales e Insumos", "Mano de Obra y Logística"],
                "Utilidad ($)": [max(0.0, utilidad_equipos), max(0.0, utilidad_materiales), max(0.0, utilidad_mo)]
            }
            df_grafico = pd.DataFrame(data_grafico)
            
            fig = px.pie(
                df_grafico, 
                values="Utilidad ($)", 
                names="Sección",
                hole=0.3,
                title="Aporte de Utilidad por Sección"
            )
            fig.update_traces(textposition='inside', textinfo='percent+value')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Agrega equipos o servicios con rentabilidad en las pestañas anteriores para proyectar el gráfico de pastel.")
