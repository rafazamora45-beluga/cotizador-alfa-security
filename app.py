import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
from fpdf import FPDF
import io

# 1. INICIALIZACIÓN ABSOLUTA DEL ESTADO DE LA SESIÓN
if "equipos" not in st.session_state:
    st.session_state["equipos"] = []
if "materiales" not in st.session_state:
    st.session_state["materiales"] = []
if "mano_obra" not in st.session_state:
    st.session_state["mano_obra"] = []

# Configuración de la página
st.set_page_config(page_title="Cotizador - Alfa Security", layout="wide")

# Título
st.title("🛡️ Sistema de Cotizaciones Automáticas — Alfa Security")
st.markdown("---")

# 2. INFORMACIÓN DEL PROYECTO
st.sidebar.header("📋 Datos del Proyecto")
cliente = st.sidebar.text_input("Nombre del Cliente / Proyecto", "Procaps El Salvador")
atencion = st.sidebar.text_input("Atención a:", "Ing. Miguel Melendez")
validez = st.sidebar.text_input("Validez de la Oferta", "15 Días")
pago = st.sidebar.text_input("Condiciones de Pago", "60% Anticipo / 40% Contraentrega")

MARGEN = 0.40

# PESTAÑAS PRINCIPALES
tab1, tab2, tab3, tab4 = st.tabs([
    "📦 Equipos Principales", 
    "🔍 Buscador Web (Freund)", 
    "🛠️ Mano de Obra", 
    "📊 Liquidación y PDF"
])

# --- PESTAÑA 1: EQUIPOS PRINCIPALES ---
with tab1:
    st.subheader("Componentes y Equipos de Seguridad Electrónica")
    with st.form("form_equipos"):
        col1, col2, col3 = st.columns([3, 1, 1])
        desc_eq = col1.text_input("Descripción del Equipo", placeholder="Ej. Panel Honeywell")
        cant_eq = col2.number_input("Cantidad", min_value=1, value=1, step=1)
        costo_eq = col3.number_input("Costo Unitario ($)", min_value=0.0, value=0.0, step=10.0)
        btn_eq = st.form_submit_button("Agregar Equipo")
        
        if btn_eq and desc_eq:
            precio_venta_u = costo_eq / (1 - MARGEN)
            st.session_state["equipos"].append({
                "Descripción": desc_eq, "Cantidad": cant_eq,
                "Costo Unitario": costo_eq, "Costo Total": costo_eq * cant_eq,
                "Precio Venta U": precio_venta_u, "Precio Venta Total": precio_venta_u * cant_eq
            })
            st.success(f"Agregado: {desc_eq}")

    if st.session_state["equipos"]:
        st.dataframe(pd.DataFrame(st.session_state["equipos"]).style.format({"Costo Unitario": "${:.2f}", "Costo Total": "${:.2f}", "Precio Venta U": "${:.2f}", "Precio Venta Total": "${:.2f}"}))
        if st.button("Limpiar Equipos", key="btn_clear_eq"):
            st.session_state["equipos"] = []
            st.rerun()

# --- PESTAÑA 2: BUSCADOR WEB (FREUND) ---
with tab2:
    st.subheader("🌐 Rastreador Web de Materiales (Freund El Salvador)")
    st.info("Ingresa el SKU o nombre del producto. El sistema buscará en internet los precios actuales.")
    
    buscar_termino = st.text_input("¿Qué material necesitas buscar?", placeholder="Ej. tubo emt 3/4")
    
    if buscar_termino:
        st.write(f"Conectando con freundferreteria.com para buscar: **'{buscar_termino}'**...")
        
        # Lógica de Web Scraping para intentar obtener datos reales de Freund
        termino_url = buscar_termino.replace(' ', '+')
        url_busqueda = f"https://www.freundferreteria.com/busqueda?q={termino_url}"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        
        resultados_encontrados = []
        
        try:
            respuesta = requests.get(url_busqueda, headers=headers, timeout=8)
            if respuesta.status_code == 200:
                soup = BeautifulSoup(respuesta.text, 'html.parser')
                
                # Búsqueda heurística de productos en la página
                productos_html = soup.find_all('div', class_=lambda c: c and 'product' in c.lower())
                
                for prod in productos_html:
                    nombre_tag = prod.find(['h2', 'h3', 'a'], class_=lambda c: c and ('name' in c.lower() or 'title' in c.lower()))
                    precio_tag = prod.find(['span', 'div'], class_=lambda c: c and 'price' in c.lower())
                    
                    if nombre_tag and precio_tag:
                        nombre = nombre_tag.get_text(strip=True)
                        precio_txt = precio_tag.get_text(strip=True).replace('$', '').replace(',', '')
                        try:
                            precio_float = float(precio_txt)
                            resultados_encontrados.append({"name": nombre, "price": precio_float})
                        except ValueError:
                            continue
        except Exception as e:
            st.warning("El servidor de Freund está bloqueando el rastreo automático en este momento.")

        # Fallback de emergencia por si Freund bloquea la conexión del bot
        if not resultados_encontrados:
            st.info("Mostrando materiales guardados en memoria alternativa...")
            materiales_respaldo = [
                {"name": "TUBO CONDUIT EMT GALVANIZADO 3/4 PLG", "price": 4.25},
                {"name": "UNION EMT PRESION 3/4 PLG", "price": 0.95},
                {"name": "CONECTOR RECTO EMT A CAJA 1 PLG", "price": 0.85},
                {"name": "ABRAZADERA 4 A 5 PLG", "price": 4.25},
                {"name": "CABLE FPLR 2X14 AWG CONTRA INCENDIO (PIE)", "price": 0.38}
            ]
            resultados_encontrados = [m for m in materiales_respaldo if buscar_termino.lower() in m["name"].lower()]

        if resultados_encontrados:
            for i, m in enumerate(resultados_encontrados[:5]): # Mostrar los top 5
                col_desc, col_accion = st.columns([3, 2])
                col_desc.markdown(f"**{m['name']}** \n**Costo Base: ${m['price']:.2f}**")
                
                cant_m = col_accion.number_input("Cantidad", min_value=1, value=1, step=1, key=f"c_m_{i}")
                if col_accion.button("Añadir", key=f"b_m_{i}"):
                    precio_v_mat = m['price'] / (1 - MARGEN)
                    st.session_state["materiales"].append({
                        "Descripción": m['name'], "Cantidad": cant_m,
                        "Costo Unitario": m['price'], "Costo Total": m['price'] * cant_m,
                        "Precio Venta U": precio_v_mat, "Precio Venta Total": precio_v_mat * cant_m
                    })
                    st.success(f"Añadido: {m['name']}")
        else:
            st.error("No se encontraron resultados en el catálogo.")

# --- PESTAÑA 3: MANO DE OBRA ---
with tab3:
    st.subheader("Ingeniería y Mano de Obra")
    with st.form("form_obra"):
        col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
        rol = col1.text_input("Rol / Cargo", value="Técnico Instalador")
        personal = col2.number_input("Personas", min_value=1, value=2)
        dias = col3.number_input("Días", min_value=1, value=5)
        tarifa = col4.number_input("Costo Diario ($)", min_value=0.0, value=25.0)
        btn_obra = st.form_submit_button("Añadir")
        
        if btn_obra and rol:
            costo_mo = personal * dias * tarifa
            st.session_state["mano_obra"].append({
                "Rol": rol, "Personal": personal, "Días": dias,
                "Costo Diario": tarifa, "Costo Total": costo_mo,
                "Precio Venta Total": costo_mo / (1 - MARGEN)
            })
            st.success("Mano de obra cargada.")

    if st.session_state["mano_obra"]:
        st.dataframe(pd.DataFrame(st.session_state["mano_obra"]).style.format({"Costo Diario": "${:.2f}", "Costo Total": "${:.2f}", "Precio Venta Total": "${:.2f}"}))
        if st.button("Limpiar Mano de Obra", key="btn_clear_mo"):
            st.session_state["mano_obra"] = []
            st.rerun()

# --- PESTAÑA 4: RESUMEN Y GENERACIÓN DE PDF ---
with tab4:
    st.subheader("💸 Liquidación y Exportación")
    
    lista_equipos = st.session_state.get("equipos", [])
    lista_mat = st.session_state.get("materiales", [])
    lista_mo = st.session_state.get("mano_obra", [])
    
    venta_equipos = sum(x.get("Precio Venta Total", 0.0) for x in lista_equipos)
    venta_materiales = sum(x.get("Precio Venta Total", 0.0) for x in lista_mat)
    venta_mo = sum(x.get("Precio Venta Total", 0.0) for x in lista_mo)
    
    subtotal = venta_equipos + venta_materiales + venta_mo
    iva = subtotal * 0.13
    total_final = subtotal + iva

    # Mostrar KPI Rápidos
    c1, c2, c3 = st.columns(3)
    c1.metric("Equipos", f"${venta_equipos:,.2f}")
    c2.metric("Materiales (Totales)", f"${venta_materiales:,.2f}")
    c3.metric("Mano de Obra (Oculta)", f"${venta_mo:,.2f}")

    st.markdown("---")
    
    # MOTOR DE GENERACIÓN DE PDF
    class PDF(FPDF):
        def header(self):
            self.set_font('Arial', 'B', 16)
            self.set_text_color(0, 51, 102) # Color azul oscuro corporativo
            self.cell(0, 10, 'ALFA SECURITY', 0, 1, 'L')
            self.set_font('Arial', '', 10)
            self.set_text_color(100, 100, 100)
            self.cell(0, 5, 'Soluciones en Seguridad Electrónica', 0, 1, 'L')
            self.ln(10)

        def footer(self):
            self.set_y(-15)
            self.set_font('Arial', 'I', 8)
            self.cell(0, 10, f'Página {self.page_no()}', 0, 0, 'C')

    # Función para compilar el PDF
    def crear_pdf():
        pdf = PDF()
        pdf.add_page()
        
        # Datos del Cliente
        pdf.set_font('Arial', 'B', 12)
        pdf.set_text_color(0, 0, 0)
        pdf.cell(0, 8, 'PROPUESTA COMERCIAL', 0, 1, 'C')
        pdf.ln(5)
        
        pdf.set_font('Arial', '', 11)
        pdf.cell(0, 6, f'Cliente / Proyecto: {cliente}', 0, 1)
        pdf.cell(0, 6, f'Atención a: {atencion}', 0, 1)
        pdf.cell(0, 6, f'Validez de Oferta: {validez}', 0, 1)
        pdf.cell(0, 6, f'Condiciones de Pago: {pago}', 0, 1)
        pdf.ln(10)
        
        # Desglose de Precios (Cumpliendo reglas de privacidad solicitadas)
        pdf.set_font('Arial', 'B', 11)
        pdf.cell(140, 8, 'Descripción del Rubro', 1, 0, 'C')
        pdf.cell(50, 8, 'Total Estimado', 1, 1, 'C')
        
        pdf.set_font('Arial', '', 11)
        
        # 1. Equipos (Con detalle si hay)
        pdf.cell(140, 8, ' Suministro de Equipos de Seguridad Electrónica', 1, 0, 'L')
        pdf.cell(50, 8, f'${venta_equipos:,.2f}', 1, 1, 'R')
        
        # 2. Materiales (Solo costo total como pediste)
        pdf.cell(140, 8, ' Suministro de Materiales de Instalación y Canalización', 1, 0, 'L')
        pdf.cell(50, 8, f'${venta_materiales:,.2f}', 1, 1, 'R')
        
        # 3. Mano de Obra (Sin dar información de técnicos o días, solo el costo total)
        pdf.cell(140, 8, ' Ingeniería, Configuración y Mano de Obra Técnica', 1, 0, 'L')
        pdf.cell(50, 8, f'${venta_mo:,.2f}', 1, 1, 'R')
        
        pdf.ln(5)
        
        # Totales
        pdf.set_font('Arial', 'B', 11)
        pdf.cell(140, 8, 'SUBTOTAL', 0, 0, 'R')
        pdf.cell(50, 8, f'${subtotal:,.2f}', 1, 1, 'R')
        
        pdf.cell(140, 8, 'IVA (13%)', 0, 0, 'R')
        pdf.cell(50, 8, f'${iva:,.2f}', 1, 1, 'R')
        
        pdf.set_text_color(0, 100, 0) # Verde para el total
        pdf.cell(140, 8, 'TOTAL OFERTA', 0, 0, 'R')
        pdf.cell(50, 8, f'${total_final:,.2f}', 1, 1, 'R')
        
        # Retornar el archivo PDF codificado
        return pdf.output(dest='S').encode('latin-1')

    # Botón de Descarga del PDF
    if subtotal > 0:
        pdf_bytes = crear_pdf()
        st.download_button(
            label="📄 Descargar Cotización Oficial (PDF)",
            data=pdf_bytes,
            file_name=f"Cotizacion_Alfa_Security_{cliente.replace(' ', '_')}.pdf",
            mime="application/pdf"
        )
    else:
        st.info("Agrega equipos, materiales o mano de obra para habilitar la descarga del PDF.")
