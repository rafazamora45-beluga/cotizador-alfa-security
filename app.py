import streamlit as st
import pandas as pd
import plotly.express as px
from fpdf import FPDF
import requests
from bs4 import BeautifulSoup
import re
import time
import os
from urllib.parse import quote_plus

# ─────────────────────────────────────────────
# CONFIGURACION
# ─────────────────────────────────────────────
st.set_page_config(page_title="Cotizador Inteligente - Alfa Security", layout="wide")

for key, default in [("equipos", []), ("materiales", []), ("servicios_mo", [])]:
    if key not in st.session_state:
        st.session_state[key] = default

st.title("🛡️ Sistema de Cotizaciones Automaticas — Alfa Security")
st.markdown("---")

DEPARTAMENTOS_FREUND = {
    "🏗️ Tubería y Ductos (Cableado)":       "https://www.freundferreteria.com/categoria/TUBERIA-Y-DUCTOS-CABLEADO-ELECTRICO/productos/NVL3-149",
    "🔌 Conductores Eléctricos":             "https://www.freundferreteria.com/categoria/CONDUCTORES-ELECTRICOS/productos/NVL2-37",
    "🔩 Accesorios Conductores Eléctricos":  "https://www.freundferreteria.com/categoria/ACCESORIOS-CONDUCTORES-ELECTRICOS/productos/NVL3-432",
    "⚡ Material Eléctrico":                 "https://www.freundferreteria.com/categoria/MATERIAL-ELECTRICOS/productos/NVL2-38",
    "⛓️ Alambres y Mallas":                  "https://www.freundferreteria.com/categoria/ALAMBRES-Y-MALLAS/productos/NVL2-27",
}

BASE_URL = "https://www.freundferreteria.com"

# ─────────────────────────────────────────────
# CATALOGO LOCAL (respaldo garantizado)
# ─────────────────────────────────────────────
CATALOGO_LOCAL = [
    {"sku":"1413211","name":"TUBO CONDUIT EMT GALVANIZADO 3/4 PLG (6MT)","price":4.25,"dep":"🏗️ Tubería y Ductos (Cableado)","link":f"{BASE_URL}/producto/TUBO-CONDUIT-EMT-GALVANIZADO-3-4-PLG--6MT-/1413211","img":f"{BASE_URL}/foto/1413211/TUBO-CONDUIT-EMT-GALVANIZADO-3-4-PLG--6MT-.jpg","marca":"Genérica","unidad":"Unidad"},
    {"sku":"1413212","name":"TUBO CONDUIT EMT GALVANIZADO 1/2 PLG (6MT)","price":3.15,"dep":"🏗️ Tubería y Ductos (Cableado)","link":f"{BASE_URL}/producto/TUBO-CONDUIT-EMT-GALVANIZADO-1-2-PLG--6MT-/1413212","img":f"{BASE_URL}/foto/1413212/TUBO-CONDUIT-EMT-GALVANIZADO-1-2-PLG--6MT-.jpg","marca":"Genérica","unidad":"Unidad"},
    {"sku":"1413213","name":"TUBO CONDUIT EMT GALVANIZADO 1 PLG (6MT)","price":7.80,"dep":"🏗️ Tubería y Ductos (Cableado)","link":f"{BASE_URL}/producto/TUBO-CONDUIT-EMT-GALVANIZADO-1-PLG--6MT-/1413213","img":f"{BASE_URL}/foto/1413213/TUBO-CONDUIT-EMT-GALVANIZADO-1-PLG--6MT-.jpg","marca":"Genérica","unidad":"Unidad"},
    {"sku":"24847137","name":"UNION EMT PRESION 3/4 PLG","price":0.95,"dep":"🏗️ Tubería y Ductos (Cableado)","link":f"{BASE_URL}/producto/UNION-EMT-PRESION-3-4-PLG/24847137","img":f"{BASE_URL}/foto/24847137/UNION-EMT-PRESION-3-4-PLG.jpg","marca":"Genérica","unidad":"Unidad"},
    {"sku":"2718137","name":"UNION TUBO EMT 3/4 PLG","price":0.65,"dep":"🏗️ Tubería y Ductos (Cableado)","link":f"{BASE_URL}/producto/UNION-TUBO-EMT-3-4-PLG/2718137","img":f"{BASE_URL}/foto/2718137/UNION-TUBO-EMT-3-4-PLG.jpg","marca":"Genérica","unidad":"Unidad"},
    {"sku":"748392","name":"TECNO-DUCTO 19 MM (3/4 IN) CORRUGADO CABLEADO ELECTRICO PVC GRIS","price":0.85,"dep":"🏗️ Tubería y Ductos (Cableado)","link":f"{BASE_URL}/producto/TECNO-DUCTO-19-MM/748392","img":f"{BASE_URL}/foto/748392/TECNO-DUCTO-19-MM.jpg","marca":"Genérica","unidad":"Metro"},
    {"sku":"748393","name":"TECNO-DUCTO 13 MM (1/2 IN) CORRUGADO CABLEADO ELECTRICO PVC GRIS","price":0.60,"dep":"🏗️ Tubería y Ductos (Cableado)","link":f"{BASE_URL}/producto/TECNO-DUCTO-13-MM/748393","img":f"{BASE_URL}/foto/748393/TECNO-DUCTO-13-MM.jpg","marca":"Genérica","unidad":"Metro"},
    {"sku":"850211","name":"CAJA CONDUIT EMT METALICA 4X4 CUADRADA","price":1.45,"dep":"🏗️ Tubería y Ductos (Cableado)","link":f"{BASE_URL}/producto/CAJA-CONDUIT-EMT-4X4/850211","img":f"{BASE_URL}/foto/850211/CAJA-CONDUIT-EMT-4X4.jpg","marca":"Genérica","unidad":"Unidad"},
    {"sku":"850200","name":"CAJA CONDUIT EMT METALICA 2X4 RECTANGULAR","price":0.95,"dep":"🏗️ Tubería y Ductos (Cableado)","link":f"{BASE_URL}/producto/CAJA-CONDUIT-EMT-2X4/850200","img":f"{BASE_URL}/foto/850200/CAJA-CONDUIT-EMT-2X4.jpg","marca":"Genérica","unidad":"Unidad"},
    {"sku":"551003","name":"CONECTOR RECTO EMT 3/4 PLG TIPO PRESION","price":0.55,"dep":"🏗️ Tubería y Ductos (Cableado)","link":f"{BASE_URL}/producto/CONECTOR-RECTO-EMT-3-4/551003","img":f"{BASE_URL}/foto/551003/CONECTOR-RECTO-EMT.jpg","marca":"Genérica","unidad":"Unidad"},
    {"sku":"551001","name":"CONECTOR RECTO EMT 1/2 PLG TIPO PRESION","price":0.40,"dep":"🏗️ Tubería y Ductos (Cableado)","link":f"{BASE_URL}/producto/CONECTOR-RECTO-EMT-1-2/551001","img":f"{BASE_URL}/foto/551001/CONECTOR-RECTO-EMT-12.jpg","marca":"Genérica","unidad":"Unidad"},
    {"sku":"CABLE-14-NEGRO","name":"CABLE ELECTRICO THHN NEGRO NO. 14 AWG COMULSA (METRO)","price":0.45,"dep":"🔌 Conductores Eléctricos","link":f"{BASE_URL}/buscar?text=CABLE+THHN+14+NEGRO","img":"","marca":"Comulsa","unidad":"Metro"},
    {"sku":"CABLE-12-NEGRO","name":"CABLE ELECTRICO THHN NEGRO NO. 12 AWG (METRO)","price":0.70,"dep":"🔌 Conductores Eléctricos","link":f"{BASE_URL}/buscar?text=CABLE+THHN+12+NEGRO","img":"","marca":"Comulsa","unidad":"Metro"},
    {"sku":"CABLE-10-NEGRO","name":"CABLE ELECTRICO THHN NEGRO NO. 10 AWG (METRO)","price":1.10,"dep":"🔌 Conductores Eléctricos","link":f"{BASE_URL}/buscar?text=CABLE+THHN+10+NEGRO","img":"","marca":"Comulsa","unidad":"Metro"},
    {"sku":"CABLE-FPLR","name":"CABLE PARA ALARMA CONTRA INCENDIO 18 AWG 2C FPLR BLINDADO (METRO)","price":0.85,"dep":"🔌 Conductores Eléctricos","link":f"{BASE_URL}/buscar?text=CABLE+ALARMA+INCENDIO","img":"","marca":"Belden","unidad":"Metro"},
    {"sku":"CABLE-CAT6","name":"CABLE UTP CAT 6 GRIS 4 PARES (METRO)","price":0.55,"dep":"🔌 Conductores Eléctricos","link":f"{BASE_URL}/buscar?text=CABLE+UTP+CAT6","img":"","marca":"AMP","unidad":"Metro"},
    {"sku":"CABLE-2X18","name":"CABLE GEMELO FLEXIBLE 2X18 AWG (METRO)","price":0.30,"dep":"🔌 Conductores Eléctricos","link":f"{BASE_URL}/buscar?text=CABLE+GEMELO+2X18","img":"","marca":"Comulsa","unidad":"Metro"},
    {"sku":"ACC-100","name":"ABRAZADERA METALICA PARA CONDUIT 3/4 PLG TIPO D","price":0.25,"dep":"🔩 Accesorios Conductores Eléctricos","link":f"{BASE_URL}/buscar?text=ABRAZADERA+CONDUIT+3-4","img":"","marca":"Genérica","unidad":"Unidad"},
    {"sku":"ACC-101","name":"ABRAZADERA METALICA PARA CONDUIT 1/2 PLG TIPO D","price":0.20,"dep":"🔩 Accesorios Conductores Eléctricos","link":f"{BASE_URL}/buscar?text=ABRAZADERA+CONDUIT+1-2","img":"","marca":"Genérica","unidad":"Unidad"},
    {"sku":"ACC-200","name":"BRIDA PLASTICA BLANCA 15CM (PACK 100 UND)","price":2.50,"dep":"🔩 Accesorios Conductores Eléctricos","link":f"{BASE_URL}/buscar?text=BRIDA+PLASTICA+15CM","img":"","marca":"Genérica","unidad":"Paquete"},
    {"sku":"ACC-201","name":"BRIDA PLASTICA NEGRA 20CM (PACK 100 UND)","price":3.20,"dep":"🔩 Accesorios Conductores Eléctricos","link":f"{BASE_URL}/buscar?text=BRIDA+PLASTICA+20CM","img":"","marca":"Genérica","unidad":"Paquete"},
    {"sku":"ACC-300","name":"CANALETA RANURADA PVC BLANCA 40X25MM (2MT)","price":4.80,"dep":"🔩 Accesorios Conductores Eléctricos","link":f"{BASE_URL}/buscar?text=CANALETA+RANURADA+40X25","img":"","marca":"Genérica","unidad":"Unidad"},
    {"sku":"ACC-301","name":"CANALETA RANURADA PVC BLANCA 60X40MM (2MT)","price":7.50,"dep":"🔩 Accesorios Conductores Eléctricos","link":f"{BASE_URL}/buscar?text=CANALETA+RANURADA+60X40","img":"","marca":"Genérica","unidad":"Unidad"},
    {"sku":"ELEC-001","name":"INTERRUPTOR TERMICO 1X20A RIEL DIN SCHNEIDER","price":8.50,"dep":"⚡ Material Eléctrico","link":f"{BASE_URL}/buscar?text=BREAKER+1X20A+SCHNEIDER","img":"","marca":"Schneider","unidad":"Unidad"},
    {"sku":"ELEC-002","name":"INTERRUPTOR TERMICO 2X20A RIEL DIN SCHNEIDER","price":15.90,"dep":"⚡ Material Eléctrico","link":f"{BASE_URL}/buscar?text=BREAKER+2X20A","img":"","marca":"Schneider","unidad":"Unidad"},
    {"sku":"ELEC-003","name":"TOMACORRIENTE DOBLE POLARIZADO BLANCO 110V","price":1.95,"dep":"⚡ Material Eléctrico","link":f"{BASE_URL}/buscar?text=TOMACORRIENTE+DOBLE","img":"","marca":"Leviton","unidad":"Unidad"},
    {"sku":"ELEC-004","name":"INTERRUPTOR SENCILLO 15A 120V BLANCO","price":1.50,"dep":"⚡ Material Eléctrico","link":f"{BASE_URL}/buscar?text=INTERRUPTOR+SENCILLO+15A","img":"","marca":"Leviton","unidad":"Unidad"},
    {"sku":"ELEC-005","name":"PANEL ELECTRICO RIEL DIN 12 ESPACIOS CON TAPA","price":28.00,"dep":"⚡ Material Eléctrico","link":f"{BASE_URL}/buscar?text=PANEL+ELECTRICO+12+ESPACIOS","img":"","marca":"Schneider","unidad":"Unidad"},
    {"sku":"ALAM-001","name":"ALAMBRE DE AMARRE GALVANIZADO NO. 16 (ROLLO 1LB)","price":1.80,"dep":"⛓️ Alambres y Mallas","link":f"{BASE_URL}/buscar?text=ALAMBRE+AMARRE+GALVANIZADO","img":"","marca":"Genérica","unidad":"Rollo"},
    {"sku":"ALAM-002","name":"ALAMBRE ESPIGADO GALVANIZADO CALIBRE 14 (ROLLO 200M)","price":45.00,"dep":"⛓️ Alambres y Mallas","link":f"{BASE_URL}/buscar?text=ALAMBRE+ESPIGADO+GALVANIZADO","img":"","marca":"Genérica","unidad":"Rollo"},
]

# ─────────────────────────────────────────────
# MOTOR DE BUSQUEDA
# ─────────────────────────────────────────────
HEADERS_WEB = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "es-ES,es;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
}

def _parsear_precio(texto):
    try:
        return float(re.sub(r"[^\d.]", "", texto.replace(",", ".")))
    except:
        return 0.0

def _extraer_imagen(soup):
    for img in soup.find_all("img"):
        src = img.get("src") or img.get("data-src") or ""
        if src and not src.endswith(".svg") and "logo" not in src.lower() and "icon" not in src.lower():
            return src if src.startswith("http") else BASE_URL + src
    return ""

def scraping_freund(termino, url_categoria=""):
    resultados = []
    urls_a_probar = []
    if termino:
        urls_a_probar.append(f"{BASE_URL}/buscar?text={quote_plus(termino)}")
    if url_categoria:
        urls_a_probar.append(url_categoria)
    try:
        s = requests.Session()
        s.headers.update(HEADERS_WEB)
        s.get(BASE_URL, timeout=5)
        time.sleep(0.3)
        for url in urls_a_probar:
            r = s.get(url, timeout=8)
            if r.status_code != 200:
                continue
            soup = BeautifulSoup(r.text, "html.parser")
            tarjetas = (
                soup.find_all("div", class_=re.compile(r"product-block|product-item|product-card", re.I)) or
                soup.find_all("div", class_=re.compile(r"product", re.I)) or
                soup.find_all("li",  class_=re.compile(r"product|item", re.I))
            )
            for t in tarjetas[:40]:
                ne = t.find(["h2","h3","h4","a"], class_=re.compile(r"name|title|product", re.I)) or t.find("a") or t.find("h3")
                if not ne:
                    continue
                nombre = ne.get_text(strip=True).upper()
                if termino and termino.lower() not in nombre.lower():
                    continue
                pe = t.find(["span","div","p"], class_=re.compile(r"price|precio", re.I))
                precio = _parsear_precio(pe.get_text()) if pe else 0.0
                le = t.find("a", href=True)
                href = le["href"] if le else ""
                if href and not href.startswith("http"):
                    href = BASE_URL + href
                m = re.search(r"/(\d+)$", href) if href else None
                sku = m.group(1) if m else f"F{len(resultados)+1}"
                img = _extraer_imagen(t)
                if nombre and len(nombre) > 3:
                    resultados.append({"sku": sku, "name": nombre, "price": precio, "link": href, "img": img, "marca": "", "unidad": "Unidad", "fuente": "🌐 Freund (en vivo)"})
            if resultados:
                break
    except Exception:
        pass
    return resultados

def buscar_catalogo_local(termino, dep_label=""):
    termino = termino.strip().upper()
    palabras = termino.split() if termino else []
    resultados = []
    for item in CATALOGO_LOCAL:
        if dep_label and dep_label != "🔍 Todos los Departamentos" and item["dep"] != dep_label:
            continue
        texto = f"{item['name']} {item['sku']} {item.get('marca','')}".upper()
        if termino and termino == item["sku"].upper():
            resultados.insert(0, {**item, "fuente": "📦 Catálogo Local"})
            continue
        if not palabras or all(p in texto for p in palabras):
            resultados.append({**item, "fuente": "📦 Catálogo Local"})
    return resultados

def buscar_productos(termino, url_categoria="", dep_label="", usar_scraping=True):
    resultados_web = []
    if usar_scraping and termino.strip():
        resultados_web = scraping_freund(termino, url_categoria)
        msg = f"✅ {len(resultados_web)} resultados encontrados en Freund (en vivo)" if resultados_web else "⚠️ Sin acceso web — usando catálogo local"
    else:
        msg = "📦 Buscando en catálogo local"
    skus_web = {r["sku"] for r in resultados_web}
    for item in buscar_catalogo_local(termino, dep_label):
        if item["sku"] not in skus_web:
            resultados_web.append(item)
    return resultados_web, msg

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
for logo_name in ["LOGO_ALFA-02.png", "logo_alfa-02.png"]:
    if os.path.exists(logo_name):
        st.sidebar.image(logo_name, use_container_width=True)
        break

st.sidebar.header("📋 Datos del Proyecto")
proyecto = st.sidebar.text_input("Nombre del Proyecto", "Instalación sistema de detección de incendios")
empresa  = st.sidebar.text_input("Empresa", "Del Sur")
atencion = st.sidebar.text_input("Atención a:", "Rafael Zamora")
validez  = st.sidebar.text_input("Validez de la Oferta", "20 días")
pago     = st.sidebar.text_input("Condiciones de Pago", "60% Anticipo / 40% Contraentrega")

# ─────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "📦 Equipos Principales",
    "🔍 Buscador Freund (Materiales)",
    "🛠️ Mano de Obra",
    "📊 Resumen Comercial",
])

# ══════════════════════════════
# TAB 1 — EQUIPOS
# ══════════════════════════════
with tab1:
    st.subheader("Componentes y Equipos de Seguridad Electrónica")
    st.info("Ingresa los equipos principales. Podrás ajustar la rentabilidad directamente en la tabla de abajo.")
    with st.form("form_equipos"):
        col1, col2, col3, col4 = st.columns([3,1,1,1])
        desc_eq      = col1.text_input("Descripción del Equipo", placeholder="Ej. Panel de incendio Honeywell 1 SLC")
        cant_eq      = col2.number_input("Cantidad", min_value=1, value=1, step=1)
        costo_eq     = col3.number_input("Costo Unitario ($)", min_value=0.0, value=0.0, step=10.0)
        rent_inicial = col4.number_input("Rentabilidad (%)", min_value=0.0, max_value=99.0, value=40.0, step=5.0)
        btn_eq = st.form_submit_button("Agregar Equipo")
        if btn_eq and desc_eq:
            m = rent_inicial / 100.0
            pv = costo_eq / (1 - m) if m < 1 else costo_eq
            st.session_state["equipos"].append({
                "Borrar": False, "Descripción": desc_eq.upper(),
                "Cantidad": int(cant_eq), "Costo Unitario ($)": float(costo_eq),
                "Costo Total ($)": float(costo_eq * cant_eq), "Rentabilidad (%)": float(rent_inicial),
                "Precio Venta U ($)": float(pv), "Precio Venta Total ($)": float(pv * cant_eq),
            })
            st.success(f"Agregado: {desc_eq.upper()}")

    if st.session_state["equipos"]:
        st.markdown("#### 📊 Lista de Equipos Cargados")
        df_e = st.data_editor(pd.DataFrame(st.session_state["equipos"]),
            hide_index=True, use_container_width=True,
            disabled=["Descripción","Costo Unitario ($)","Costo Total ($)","Precio Venta U ($)","Precio Venta Total ($)"],
            column_config={
                "Borrar":                 st.column_config.CheckboxColumn("Borrar", default=False),
                "Cantidad":               st.column_config.NumberColumn("Cantidad", min_value=1, step=1),
                "Rentabilidad (%)":       st.column_config.NumberColumn("Rentabilidad (%)", min_value=0, max_value=99, step=1),
                "Costo Unitario ($)":     st.column_config.NumberColumn(format="$%.2f"),
                "Costo Total ($)":        st.column_config.NumberColumn(format="$%.2f"),
                "Precio Venta U ($)":     st.column_config.NumberColumn(format="$%.2f"),
                "Precio Venta Total ($)": st.column_config.NumberColumn(format="$%.2f"),
            })
        for i in range(len(df_e)):
            r = df_e.at[i,"Rentabilidad (%)"]/100.0; cu = df_e.at[i,"Costo Unitario ($)"]; q = df_e.at[i,"Cantidad"]
            df_e.at[i,"Costo Total ($)"] = cu*q
            pv = cu/(1-r) if r<1 else cu
            df_e.at[i,"Precio Venta U ($)"] = pv; df_e.at[i,"Precio Venta Total ($)"] = pv*q
        st.session_state["equipos"] = df_e.to_dict(orient="records")
        ci = sum(x["Costo Total ($)"] for x in st.session_state["equipos"])
        cv = sum(x["Precio Venta Total ($)"] for x in st.session_state["equipos"])
        c1,c2 = st.columns(2)
        c1.metric("Costo Interno Total",    f"${ci:,.2f}")
        c2.metric("Precio de Venta Total",  f"${cv:,.2f}")
        b1,b2 = st.columns([3,10])
        if b1.button("🗑️ Eliminar Marcados", key="del_eq"):
            st.session_state["equipos"] = [e for e in st.session_state["equipos"] if not e["Borrar"]]; st.rerun()
        if b2.button("Limpiar Toda la Lista", key="clear_eq"):
            st.session_state["equipos"] = []; st.rerun()

# ══════════════════════════════
# TAB 2 — BUSCADOR FREUND
# ══════════════════════════════
with tab2:
    st.subheader("🔍 Buscador de Productos — Ferretería Freund El Salvador")

    col_dep, col_txt, col_tog = st.columns([2,3,1])
    dept_sel       = col_dep.selectbox("Departamento", ["🔍 Todos los Departamentos"] + list(DEPARTAMENTOS_FREUND.keys()))
    buscar_termino = col_txt.text_input("Buscar por nombre o SKU", placeholder="Ej: tubo conduit, 748392, cable thhn...")
    usar_scraping  = col_tog.toggle("🌐 Scraping en vivo", value=True)

    if st.button("🚀 Buscar Productos", type="primary", use_container_width=False):
        if not buscar_termino.strip() and dept_sel == "🔍 Todos los Departamentos":
            st.warning("Escribe una palabra clave o selecciona un departamento.")
        else:
            with st.spinner("Buscando en Freund..."):
                url_cat = DEPARTAMENTOS_FREUND.get(dept_sel, "")
                dep_label = dept_sel if dept_sel != "🔍 Todos los Departamentos" else ""
                resultados, msg = buscar_productos(buscar_termino.strip(), url_cat, dep_label, usar_scraping)
                st.session_state["resultados_freund"] = resultados
                st.session_state["msg_busqueda"] = msg

    if "resultados_freund" in st.session_state:
        resultados = st.session_state["resultados_freund"]
        msg = st.session_state.get("msg_busqueda","")
        if "✅" in msg: st.success(msg)
        elif "⚠️" in msg: st.warning(msg)
        else: st.info(msg)

        if not resultados:
            st.error("❌ No se encontraron productos. Intenta con otras palabras clave.")
        else:
            st.markdown(f"#### 🛒 {len(resultados)} producto(s) encontrado(s)")
            st.markdown("---")
            COLS = 3
            for row_start in range(0, len(resultados), COLS):
                fila = resultados[row_start: row_start + COLS]
                cols = st.columns(COLS)
                for ci, prod in enumerate(fila):
                    idx = row_start + ci
                    with cols[ci]:
                        img_url  = prod.get("img","")
                        prod_url = prod.get("link", BASE_URL)
                        fuente   = prod.get("fuente","")
                        fc = "#00c853" if "Web" in fuente else "#78909c"

                        if img_url:
                            st.markdown(f"""
                            <a href="{prod_url}" target="_blank" style="display:block;text-decoration:none;">
                              <div style="background:#1a1e27;border:1px solid #2d3139;border-radius:10px 10px 0 0;
                                          height:155px;display:flex;align-items:center;justify-content:center;overflow:hidden;padding:6px;">
                                <img src="{img_url}" style="max-height:143px;max-width:100%;object-fit:contain;border-radius:6px;"
                                     onerror="this.parentElement.innerHTML='<span style=&quot;color:#555;font-size:11px;&quot;>📷 Sin imagen</span>';"/>
                              </div>
                            </a>""", unsafe_allow_html=True)
                        else:
                            st.markdown(f"""
                            <a href="{prod_url}" target="_blank" style="display:block;text-decoration:none;">
                              <div style="background:#1a1e27;border:1px solid #2d3139;border-radius:10px 10px 0 0;
                                          height:155px;display:flex;align-items:center;justify-content:center;">
                                <span style="font-size:40px;">📦</span>
                              </div>
                            </a>""", unsafe_allow_html=True)

                        st.markdown(f"""
                        <div style="background:#1a1e27;border:1px solid #2d3139;border-top:none;
                                    border-radius:0 0 10px 10px;padding:10px 12px 6px 12px;">
                          <p style="font-size:12px;font-weight:700;color:#e0e6f0;margin:0 0 4px 0;line-height:1.35;min-height:38px;">
                            {prod['name'][:75]}{"..." if len(prod['name'])>75 else ""}
                          </p>
                          <p style="font-size:11px;color:#78909c;margin:0 0 4px 0;">
                            SKU: <span style="color:#90a4ae;">{prod['sku']}</span>
                            {f' &nbsp;|&nbsp; {prod.get("marca","")}' if prod.get("marca") else ""}
                          </p>
                          <p style="font-size:20px;font-weight:800;color:#00e676;margin:0 0 2px 0;">
                            ${prod['price']:.2f}
                            <span style="font-size:11px;font-weight:400;color:#78909c;">/{prod.get('unidad','Unidad')}</span>
                          </p>
                          <p style="font-size:10px;color:{fc};margin:0 0 6px 0;">{fuente}</p>
                        </div>""", unsafe_allow_html=True)

                        cant_sel = st.number_input("Cantidad", min_value=1, value=1, step=1,
                                                   key=f"cant_{idx}", label_visibility="collapsed")
                        if st.button("📥 Agregar al Costeo", key=f"btn_{idx}", use_container_width=True):
                            pv = prod['price'] / (1 - 0.40)
                            st.session_state["materiales"].append({
                                "Borrar": False, "Descripción": prod['name'],
                                "Cantidad": int(cant_sel),
                                "Costo Unitario ($)": float(prod['price']),
                                "Costo Total ($)": float(prod['price'] * cant_sel),
                                "Rentabilidad (%)": 40.0,
                                "Precio Venta U ($)": float(pv),
                                "Precio Venta Total ($)": float(pv * cant_sel),
                            })
                            st.toast(f"✅ Agregado: {prod['name'][:40]}...")
                        st.markdown("<div style='margin-bottom:16px'></div>", unsafe_allow_html=True)
            st.markdown("---")

    if st.session_state["materiales"]:
        st.markdown("### 🛒 Materiales Cargados en esta Cotización")
        df_m = st.data_editor(pd.DataFrame(st.session_state["materiales"]),
            hide_index=True, use_container_width=True,
            disabled=["Descripción","Costo Unitario ($)","Costo Total ($)","Precio Venta U ($)","Precio Venta Total ($)"],
            column_config={
                "Borrar":                 st.column_config.CheckboxColumn("Borrar", default=False),
                "Cantidad":               st.column_config.NumberColumn("Cantidad", min_value=1, step=1),
                "Rentabilidad (%)":       st.column_config.NumberColumn("Rentabilidad (%)", min_value=0, max_value=99, step=1),
                "Costo Unitario ($)":     st.column_config.NumberColumn(format="$%.2f"),
                "Costo Total ($)":        st.column_config.NumberColumn(format="$%.2f"),
                "Precio Venta U ($)":     st.column_config.NumberColumn(format="$%.2f"),
                "Precio Venta Total ($)": st.column_config.NumberColumn(format="$%.2f"),
            })
        for i in range(len(df_m)):
            r = df_m.at[i,"Rentabilidad (%)"]/100.0; cu = df_m.at[i,"Costo Unitario ($)"]; q = df_m.at[i,"Cantidad"]
            df_m.at[i,"Costo Total ($)"] = cu*q
            pv = cu/(1-r) if r<1 else cu
            df_m.at[i,"Precio Venta U ($)"] = pv; df_m.at[i,"Precio Venta Total ($)"] = pv*q
        st.session_state["materiales"] = df_m.to_dict(orient="records")
        d1,d2 = st.columns([3,10])
        if d1.button("🗑️ Eliminar Seleccionados", key="del_mat"):
            st.session_state["materiales"] = [m for m in st.session_state["materiales"] if not m["Borrar"]]; st.rerun()
        if d2.button("Limpiar todo", key="clear_mat"):
            st.session_state["materiales"] = []; st.rerun()
        tc = sum(x["Costo Total ($)"] for x in st.session_state["materiales"])
        tv = sum(x["Precio Venta Total ($)"] for x in st.session_state["materiales"])
        m1,m2 = st.columns(2)
        m1.metric("Costo Total Materiales",  f"${tc:,.2f}")
        m2.metric("Precio Venta Materiales", f"${tv:,.2f}")

# ══════════════════════════════
# TAB 3 — MANO DE OBRA
# ══════════════════════════════
with tab3:
    st.subheader("🛠️ Presupuesto de Mano de Obra y Logística")
    col_izq, col_der = st.columns([1,1])
    with col_izq:
        st.markdown("#### ⚙️ 1. Personal Técnico y Cargas")
        rent_mo = st.number_input("Rentabilidad Comercial MO (%)", min_value=0.0, max_value=99.0, value=20.0, step=5.0, key="rent_mo_p3")
        with st.form("form_mano_obra_completo"):
            c1,c2 = st.columns(2)
            cant_conf=c1.number_input("Cantidad Configuradores",min_value=0,value=0)
            dias_conf=c2.number_input("Días Configurador",min_value=0,value=0)
            tarifa_conf=st.number_input("Costo Diario Configurador ($)",min_value=0.0,value=50.0)
            st.markdown("---")
            c3,c4=st.columns(2)
            cant_inst=c3.number_input("Cantidad Instaladores",min_value=0,value=0)
            dias_inst=c4.number_input("Días Instalador",min_value=0,value=0)
            tarifa_inst=st.number_input("Costo Diario Instalador ($)",min_value=0.0,value=25.0)
            st.markdown("---")
            c5,c6=st.columns(2)
            dias_estadia=c5.number_input("Días Estadía fuera de SS",min_value=0,value=0)
            costo_estadia=c6.number_input("Costo Diario Estadía ($)",min_value=0.0,value=0.0)
            c7,c8=st.columns(2)
            dias_viaticos=c7.number_input("Días de Viáticos",min_value=0,value=0)
            costo_viaticos=c8.number_input("Costo Diario Viáticos ($)",min_value=0.0,value=0.0)
            st.markdown("---")
            c9,c10=st.columns(2)
            dias_out=c9.number_input("Días Técnico Outsourcing",min_value=0,value=0)
            costo_out=c10.number_input("Costo Diario Outsourcing ($)",min_value=0.0,value=0.0)
            c11,c12=st.columns(2)
            dias_noc=c11.number_input("Días Técnico Nocturno",min_value=0,value=0)
            costo_noc=c12.number_input("Costo Diario Nocturno ($)",min_value=0.0,value=0.0)
            st.markdown("---")
            ck1,ck2=st.columns(2)
            kms_proyecto=ck1.number_input("Kilómetros totales (KM)",min_value=0.0,value=0.0)
            costo_por_km=ck2.number_input("Costo por Kilómetro ($)",min_value=0.0,value=0.36,step=0.05)
            btn_mo=st.form_submit_button("Agregar al Balance Operativo")
            if btn_mo:
                servicios_nuevos=[
                    ("Servicio de Configuración Especializada",cant_conf*dias_conf,tarifa_conf),
                    ("Servicio de Técnico Instalador",cant_inst*dias_inst,tarifa_inst),
                    ("Logística de Estadía fuera de San Salvador",dias_estadia,costo_estadia),
                    ("Viáticos de Alimentación y Campo",dias_viaticos,costo_viaticos),
                    ("Soporte de Técnico Outsourcing",dias_out,costo_out),
                    ("Servicio Técnico Nocturno / Fin de Semana",dias_noc,costo_noc),
                    ("Movilización y Combustible del Proyecto",kms_proyecto,costo_por_km),
                ]
                guardado=False
                for nombre,cant,costo_u in servicios_nuevos:
                    if cant>0 and costo_u>0:
                        m=rent_mo/100.0; pv_u=costo_u/(1-m) if m<1 else costo_u
                        st.session_state["servicios_mo"].append({
                            "Borrar":False,"Descripción":nombre,"Cantidad":float(cant),
                            "Costo Unitario ($)":float(costo_u),"Costo Interno ($)":float(cant*costo_u),
                            "Rentabilidad (%)":float(rent_mo),"Costo del Cliente U ($)":float(pv_u),
                            "Precio Venta Total ($)":float(pv_u*cant),
                        }); guardado=True
                if guardado: st.success("¡Mano de obra guardada!"); st.rerun()

    with col_der:
        st.markdown("#### 🔧 2. Certificaciones y Equipos Especiales")
        with st.form("form_herramientas"):
            c_desc=st.text_input("Descripción del Item",placeholder="Ej. Alquiler de Andamios")
            c_monto=st.number_input("Costo Total ($)",min_value=0.0,value=0.0)
            btn_h=st.form_submit_button("Agregar Herramienta")
            if btn_h and c_desc:
                st.session_state["servicios_mo"].append({
                    "Borrar":False,"Descripción":f"[HERRAMIENTA] {c_desc.upper()}","Cantidad":1.0,
                    "Costo Unitario ($)":float(c_monto),"Costo Interno ($)":float(c_monto),
                    "Rentabilidad (%)":0.0,"Costo del Cliente U ($)":float(c_monto),"Precio Venta Total ($)":float(c_monto),
                }); st.success("Herramienta agregada."); st.rerun()

    st.markdown("---")
    if st.session_state["servicios_mo"]:
        df_mo=st.data_editor(pd.DataFrame(st.session_state["servicios_mo"]),
            hide_index=True,use_container_width=True,
            disabled=["Descripción","Costo Unitario ($)","Costo Interno ($)","Costo del Cliente U ($)","Precio Venta Total ($)"],
            column_config={
                "Borrar":           st.column_config.CheckboxColumn("Borrar",default=False),
                "Cantidad":         st.column_config.NumberColumn("Cantidad",min_value=0.0,format="%.2f"),
                "Rentabilidad (%)": st.column_config.NumberColumn("Rentabilidad (%)",min_value=0,max_value=99),
            })
        for i in range(len(df_mo)):
            r=df_mo.at[i,"Rentabilidad (%)"]/100.0; cu=df_mo.at[i,"Costo Unitario ($)"]; q=df_mo.at[i,"Cantidad"]
            df_mo.at[i,"Costo Interno ($)"]=cu*q
            pv=cu/(1-r) if r<1 else cu
            df_mo.at[i,"Costo del Cliente U ($)"]=pv; df_mo.at[i,"Precio Venta Total ($)"]=pv*q
        st.session_state["servicios_mo"]=df_mo.to_dict(orient="records")
        b1,b2=st.columns([3,10])
        if b1.button("🗑️ Eliminar Seleccionados",key="del_mo_sel"):
            st.session_state["servicios_mo"]=[s for s in st.session_state["servicios_mo"] if not s["Borrar"]]; st.rerun()
        if b2.button("Limpiar Tabla Completamente",key="clear_mo_all"):
            st.session_state["servicios_mo"]=[]; st.rerun()
        ci_mo=sum(x["Costo Interno ($)"] for x in st.session_state["servicios_mo"])
        cv_mo=sum(x["Precio Venta Total ($)"] for x in st.session_state["servicios_mo"])
        m1,m2=st.columns(2)
        m1.metric("Costo Total MO",       f"${ci_mo:,.2f}")
        m2.metric("Precio Venta Total MO",f"${cv_mo:,.2f}")

# ══════════════════════════════
# TAB 4 — RESUMEN COMERCIAL
# ══════════════════════════════
with tab4:
    st.subheader("📊 Resumen General Comercial")
    lista_eq=st.session_state.get("equipos",[])
    lista_mat=st.session_state.get("materiales",[])
    lista_mo=st.session_state.get("servicios_mo",[])
    costo_equipos=sum(x.get("Costo Total ($)",0.0) for x in lista_eq)
    venta_equipos=sum(x.get("Precio Venta Total ($)",0.0) for x in lista_eq)
    costo_materiales=sum(x.get("Costo Total ($)",0.0) for x in lista_mat)
    venta_materiales=sum(x.get("Precio Venta Total ($)",0.0) for x in lista_mat)
    costo_mo_tot=sum(x.get("Costo Interno ($)",0.0) for x in lista_mo)
    venta_mo_tot=sum(x.get("Precio Venta Total ($)",0.0) for x in lista_mo)
    costo_total=costo_equipos+costo_materiales+costo_mo_tot
    subtotal_venta=venta_equipos+venta_materiales+venta_mo_tot
    utilidad_total=subtotal_venta-costo_total
    utilidad_equipos=venta_equipos-costo_equipos
    utilidad_materiales=venta_materiales-costo_materiales
    utilidad_mo=venta_mo_tot-costo_mo_tot
    rent_real_pct=(utilidad_total/subtotal_venta*100) if subtotal_venta>0 else 0.0
    st.markdown("#### ⚙️ Impuestos")
    aplicar_iva=st.checkbox("Aplicar IVA (13%) a la oferta comercial",value=True)
    iva_calc=subtotal_venta*0.13 if aplicar_iva else 0.0
    total_neto=subtotal_venta+iva_calc
    st.markdown("---")
    st.markdown("#### 🎯 Análisis de Rentabilidad")
    r1,r2,r3=st.columns(3)
    rent_obj=r1.number_input("Rentabilidad Objetivo (%)",min_value=0.0,max_value=100.0,value=40.0,step=1.0)
    r2.metric("Rentabilidad Real",f"{rent_real_pct:.2f}%")
    if rent_real_pct>=rent_obj: r3.success("✅ Meta alcanzada!")
    else: r3.warning("⚠️ Bajo el objetivo.")
    st.markdown("---")
    col_l,col_r=st.columns([4,3])
    with col_l:
        st.markdown("#### 🔒 Panel Privado")
        p1,p2,p3=st.columns(3)
        p1.metric("Costo Total Interno",    f"${costo_total:,.2f}")
        p2.metric("Precio Venta Subtotal",  f"${subtotal_venta:,.2f}")
        p3.metric("Utilidad Total",         f"${utilidad_total:,.2f}")
        st.markdown("#### 📄 Propuesta al Cliente")
        items_cli=[]
        for eq in lista_eq:
            items_cli.append({"Descripción":f"Equipo: {eq['Descripción']} (Cant: {eq['Cantidad']} x ${eq['Precio Venta U ($)']:.2f})","Monto ($)":eq["Precio Venta Total ($)"]})
        if venta_mo_tot>0: items_cli.append({"Descripción":"Mano de Obra e Ingeniería","Monto ($)":venta_mo_tot})
        if venta_materiales>0: items_cli.append({"Descripción":"Materiales y Suministros","Monto ($)":venta_materiales})
        if items_cli: st.table(pd.DataFrame(items_cli))
        else: st.warning("No hay rubros cargados.")
        f1,f2=st.columns(2)
        f1.markdown(f"* **Pago:** {pago}\n* **Validez:** {validez}")
        f2.markdown(f"* **SUBTOTAL:** ${subtotal_venta:,.2f}\n* **IVA:** ${iva_calc:,.2f}\n* **TOTAL:** **${total_neto:,.2f}**")

        def generar_pdf():
            pdf=FPDF(); pdf.add_page(); pdf.set_font("Helvetica","B",16)
            pdf.cell(190,10,"ALFA SECURITY EL SALVADOR",ln=True,align="C")
            pdf.set_font("Helvetica","",12); pdf.cell(190,10,"Oferta Económica Comercial",ln=True,align="C"); pdf.ln(8)
            pdf.set_font("Helvetica","B",12); pdf.cell(190,8,"Datos Generales:",ln=True)
            pdf.set_font("Helvetica","",11)
            for lbl,val in [("Proyecto",proyecto),("Empresa",empresa),("Atención a",atencion),("Validez",validez),("Pago",pago)]:
                pdf.cell(190,6,f"{lbl}: {val}",ln=True)
            pdf.ln(8); pdf.set_font("Helvetica","B",11)
            pdf.cell(140,8,"Descripción",border=1); pdf.cell(50,8,"Total ($)",border=1,ln=True,align="R")
            if lista_eq:
                pdf.set_font("Helvetica","B",10); pdf.cell(190,6,"--- EQUIPOS PRINCIPALES ---",border=1,ln=True)
                pdf.set_font("Helvetica","",10)
                for eq in lista_eq:
                    pdf.cell(140,6,f"{eq['Descripción']} (Cant:{eq['Cantidad']} x ${eq['Precio Venta U ($)']:.2f})",border=1)
                    pdf.cell(50,6,f"${eq['Precio Venta Total ($)']:.2f}",border=1,ln=True,align="R")
            if venta_mo_tot>0:
                pdf.cell(140,6,"Mano de Obra e Ingeniería",border=1); pdf.cell(50,6,f"${venta_mo_tot:.2f}",border=1,ln=True,align="R")
            if venta_materiales>0:
                pdf.cell(140,6,"Materiales y Suministros",border=1); pdf.cell(50,6,f"${venta_materiales:.2f}",border=1,ln=True,align="R")
            pdf.ln(6); pdf.set_font("Helvetica","B",11)
            for lbl,val in [("SUBTOTAL",subtotal_venta),("IVA (13%)" if aplicar_iva else "IVA",iva_calc),("TOTAL NETO",total_neto)]:
                pdf.cell(140,6,lbl,align="R"); pdf.cell(50,6,f"${val:.2f}",border=1,ln=True,align="R")
            return pdf.output()

        if items_cli:
            try:
                st.download_button("📥 Descargar PDF",data=bytes(generar_pdf()),
                    file_name=f"Cotizacion_{proyecto.replace(' ','_')}.pdf",mime="application/pdf")
            except Exception as e:
                st.error(f"Error PDF: {e}")

    with col_r:
        st.markdown("#### 📊 Distribución de Utilidades")
        if utilidad_total>0:
            fig=px.pie(pd.DataFrame({
                "Sección":["Equipos","Materiales","Mano de Obra"],
                "Utilidad ($)":[max(0.0,utilidad_equipos),max(0.0,utilidad_materiales),max(0.0,utilidad_mo)],
            }),values="Utilidad ($)",names="Sección",hole=0.3)
            st.plotly_chart(fig,use_container_width=True)
        else:
            st.info("Agrega componentes con margen para ver utilidades.")
