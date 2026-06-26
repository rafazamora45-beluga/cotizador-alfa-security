freund_scraper.py
Motor de búsqueda para Ferretería Freund El Salvador
- Web scraping real con múltiples estrategias
- Soporte de imágenes de producto
- Búsqueda por SKU y nombre (coincidencia parcial)
- Base de datos local como fallback garantizado
"""

import requests
from bs4 import BeautifulSoup
import time
import re
from urllib.parse import quote_plus

# ============================================================
# HEADERS para imitar un navegador real
# ============================================================
HEADERS_DESKTOP = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
}

BASE_URL = "https://www.freundferreteria.com"

# ============================================================
# BASE DE DATOS LOCAL EXPANDIDA (fallback + enriquecimiento)
# ============================================================
CATALOGO_LOCAL = [
    # ---- TUBERÍAS Y DUCTOS ----
    {
        "sku": "1413211",
        "name": "TUBO CONDUIT EMT GALVANIZADO 3/4 PLG (6MT)",
        "price": 4.25,
        "dep": "🏗️ Tubería y Ductos (Cableado)",
        "link": f"{BASE_URL}/producto/TUBO-CONDUIT-EMT-GALVANIZADO-3-4-PLG--6MT-/1413211",
        "img": f"{BASE_URL}/foto/1413211/TUBO-CONDUIT-EMT-GALVANIZADO-3-4-PLG--6MT-.jpg",
        "marca": "Genérica",
        "unidad": "Unidad",
    },
    {
        "sku": "1413212",
        "name": "TUBO CONDUIT EMT GALVANIZADO 1/2 PLG (6MT)",
        "price": 3.15,
        "dep": "🏗️ Tubería y Ductos (Cableado)",
        "link": f"{BASE_URL}/producto/TUBO-CONDUIT-EMT-GALVANIZADO-1-2-PLG--6MT-/1413212",
        "img": f"{BASE_URL}/foto/1413212/TUBO-CONDUIT-EMT-GALVANIZADO-1-2-PLG--6MT-.jpg",
        "marca": "Genérica",
        "unidad": "Unidad",
    },
    {
        "sku": "1413213",
        "name": "TUBO CONDUIT EMT GALVANIZADO 1 PLG (6MT)",
        "price": 7.80,
        "dep": "🏗️ Tubería y Ductos (Cableado)",
        "link": f"{BASE_URL}/producto/TUBO-CONDUIT-EMT-GALVANIZADO-1-PLG--6MT-/1413213",
        "img": f"{BASE_URL}/foto/1413213/TUBO-CONDUIT-EMT-GALVANIZADO-1-PLG--6MT-.jpg",
        "marca": "Genérica",
        "unidad": "Unidad",
    },
    {
        "sku": "24847137",
        "name": "UNION EMT PRESION 3/4 PLG",
        "price": 0.95,
        "dep": "🏗️ Tubería y Ductos (Cableado)",
        "link": f"{BASE_URL}/producto/UNION-EMT-PRESION-3-4-PLG/24847137",
        "img": f"{BASE_URL}/foto/24847137/UNION-EMT-PRESION-3-4-PLG.jpg",
        "marca": "Genérica",
        "unidad": "Unidad",
    },
    {
        "sku": "2718137",
        "name": "UNION TUBO EMT 3/4 PLG",
        "price": 0.65,
        "dep": "🏗️ Tubería y Ductos (Cableado)",
        "link": f"{BASE_URL}/producto/UNION-TUBO-EMT-3-4-PLG/2718137",
        "img": f"{BASE_URL}/foto/2718137/UNION-TUBO-EMT-3-4-PLG.jpg",
        "marca": "Genérica",
        "unidad": "Unidad",
    },
    {
        "sku": "748392",
        "name": "TECNO-DUCTO 19 MM (3/4 IN) CORRUGADO CABLEADO ELECTRICO PVC GRIS",
        "price": 0.85,
        "dep": "🏗️ Tubería y Ductos (Cableado)",
        "link": f"{BASE_URL}/producto/TECNO-DUCTO-19-MM--3-4-IN--CORRUGADO-CABLEADO-ELECTRICO-PVC-GRIS/748392",
        "img": f"{BASE_URL}/foto/748392/TECNO-DUCTO-19-MM.jpg",
        "marca": "Genérica",
        "unidad": "Metro",
    },
    {
        "sku": "748393",
        "name": "TECNO-DUCTO 13 MM (1/2 IN) CORRUGADO CABLEADO ELECTRICO PVC GRIS",
        "price": 0.60,
        "dep": "🏗️ Tubería y Ductos (Cableado)",
        "link": f"{BASE_URL}/producto/TECNO-DUCTO-13-MM--1-2-IN--CORRUGADO-CABLEADO-ELECTRICO-PVC-GRIS/748393",
        "img": f"{BASE_URL}/foto/748393/TECNO-DUCTO-13-MM.jpg",
        "marca": "Genérica",
        "unidad": "Metro",
    },
    {
        "sku": "850211",
        "name": "CAJA CONDUIT EMT METALICA 4X4 CUADRADA",
        "price": 1.45,
        "dep": "🏗️ Tubería y Ductos (Cableado)",
        "link": f"{BASE_URL}/producto/CAJA-CONDUIT-EMT-METALICA-4X4/850211",
        "img": f"{BASE_URL}/foto/850211/CAJA-CONDUIT-EMT-4X4.jpg",
        "marca": "Genérica",
        "unidad": "Unidad",
    },
    {
        "sku": "850200",
        "name": "CAJA CONDUIT EMT METALICA 2X4 RECTANGULAR",
        "price": 0.95,
        "dep": "🏗️ Tubería y Ductos (Cableado)",
        "link": f"{BASE_URL}/producto/CAJA-CONDUIT-EMT-METALICA-2X4/850200",
        "img": f"{BASE_URL}/foto/850200/CAJA-CONDUIT-EMT-2X4.jpg",
        "marca": "Genérica",
        "unidad": "Unidad",
    },
    {
        "sku": "551003",
        "name": "CONECTOR RECTO EMT 3/4 PLG TIPO PRESION",
        "price": 0.55,
        "dep": "🏗️ Tubería y Ductos (Cableado)",
        "link": f"{BASE_URL}/producto/CONECTOR-RECTO-EMT-3-4-PLG/551003",
        "img": f"{BASE_URL}/foto/551003/CONECTOR-RECTO-EMT.jpg",
        "marca": "Genérica",
        "unidad": "Unidad",
    },
    {
        "sku": "551001",
        "name": "CONECTOR RECTO EMT 1/2 PLG TIPO PRESION",
        "price": 0.40,
        "dep": "🏗️ Tubería y Ductos (Cableado)",
        "link": f"{BASE_URL}/producto/CONECTOR-RECTO-EMT-1-2-PLG/551001",
        "img": f"{BASE_URL}/foto/551001/CONECTOR-RECTO-EMT-12.jpg",
        "marca": "Genérica",
        "unidad": "Unidad",
    },
    # ---- CONDUCTORES ELÉCTRICOS ----
    {
        "sku": "CABLE-14-NEGRO",
        "name": "CABLE ELECTRICO THHN NEGRO NO. 14 AWG COMULSA (METRO)",
        "price": 0.45,
        "dep": "🔌 Conductores Eléctricos",
        "link": f"{BASE_URL}/buscar?text=CABLE+THHN+14+NEGRO",
        "img": f"{BASE_URL}/foto/cable-14-negro/CABLE-THHN-14-NEGRO.jpg",
        "marca": "Comulsa",
        "unidad": "Metro",
    },
    {
        "sku": "CABLE-12-NEGRO",
        "name": "CABLE ELECTRICO THHN NEGRO NO. 12 AWG (METRO)",
        "price": 0.70,
        "dep": "🔌 Conductores Eléctricos",
        "link": f"{BASE_URL}/buscar?text=CABLE+THHN+12+NEGRO",
        "img": f"{BASE_URL}/foto/cable-12/CABLE-THHN-12.jpg",
        "marca": "Comulsa",
        "unidad": "Metro",
    },
    {
        "sku": "CABLE-10-NEGRO",
        "name": "CABLE ELECTRICO THHN NEGRO NO. 10 AWG (METRO)",
        "price": 1.10,
        "dep": "🔌 Conductores Eléctricos",
        "link": f"{BASE_URL}/buscar?text=CABLE+THHN+10+NEGRO",
        "img": f"{BASE_URL}/foto/cable-10/CABLE-THHN-10.jpg",
        "marca": "Comulsa",
        "unidad": "Metro",
    },
    {
        "sku": "CABLE-FPLR",
        "name": "CABLE PARA ALARMA CONTRA INCENDIO 18 AWG 2C FPLR BLINDADO (METRO)",
        "price": 0.85,
        "dep": "🔌 Conductores Eléctricos",
        "link": f"{BASE_URL}/buscar?text=CABLE+ALARMA+INCENDIO+18AWG",
        "img": f"{BASE_URL}/foto/cable-fplr/CABLE-ALARMA-INCENDIO.jpg",
        "marca": "Belden",
        "unidad": "Metro",
    },
    {
        "sku": "CABLE-CAT6",
        "name": "CABLE UTP CAT 6 GRIS 4 PARES (METRO)",
        "price": 0.55,
        "dep": "🔌 Conductores Eléctricos",
        "link": f"{BASE_URL}/buscar?text=CABLE+UTP+CAT6",
        "img": f"{BASE_URL}/foto/cable-cat6/CABLE-UTP-CAT6.jpg",
        "marca": "AMP/CommScope",
        "unidad": "Metro",
    },
    {
        "sku": "CABLE-2X18",
        "name": "CABLE GEMELO FLEXIBLE 2X18 AWG (METRO)",
        "price": 0.30,
        "dep": "🔌 Conductores Eléctricos",
        "link": f"{BASE_URL}/buscar?text=CABLE+GEMELO+2X18",
        "img": f"{BASE_URL}/foto/cable-2x18/CABLE-GEMELO.jpg",
        "marca": "Comulsa",
        "unidad": "Metro",
    },
    # ---- ACCESORIOS CONDUCTORES ----
    {
        "sku": "ACC-100",
        "name": "ABRAZADERA METALICA PARA CONDUIT 3/4 PLG TIPO D",
        "price": 0.25,
        "dep": "🔩 Accesorios Conductores Eléctricos",
        "link": f"{BASE_URL}/buscar?text=ABRAZADERA+CONDUIT+3-4",
        "img": f"{BASE_URL}/foto/acc-100/ABRAZADERA-CONDUIT.jpg",
        "marca": "Genérica",
        "unidad": "Unidad",
    },
    {
        "sku": "ACC-101",
        "name": "ABRAZADERA METALICA PARA CONDUIT 1/2 PLG TIPO D",
        "price": 0.20,
        "dep": "🔩 Accesorios Conductores Eléctricos",
        "link": f"{BASE_URL}/buscar?text=ABRAZADERA+CONDUIT+1-2",
        "img": f"{BASE_URL}/foto/acc-101/ABRAZADERA-CONDUIT-12.jpg",
        "marca": "Genérica",
        "unidad": "Unidad",
    },
    {
        "sku": "ACC-200",
        "name": "BRIDA PLASTICA BLANCA 15CM (PACK 100 UND)",
        "price": 2.50,
        "dep": "🔩 Accesorios Conductores Eléctricos",
        "link": f"{BASE_URL}/buscar?text=BRIDA+PLASTICA+15CM",
        "img": f"{BASE_URL}/foto/acc-200/BRIDA-PLASTICA.jpg",
        "marca": "Genérica",
        "unidad": "Paquete",
    },
    {
        "sku": "ACC-201",
        "name": "BRIDA PLASTICA NEGRA 20CM (PACK 100 UND)",
        "price": 3.20,
        "dep": "🔩 Accesorios Conductores Eléctricos",
        "link": f"{BASE_URL}/buscar?text=BRIDA+PLASTICA+20CM",
        "img": f"{BASE_URL}/foto/acc-201/BRIDA-PLASTICA-NEGRA.jpg",
        "marca": "Genérica",
        "unidad": "Paquete",
    },
    {
        "sku": "ACC-300",
        "name": "CANALETA RANURADA PVC BLANCA 40X25MM (2MT)",
        "price": 4.80,
        "dep": "🔩 Accesorios Conductores Eléctricos",
        "link": f"{BASE_URL}/buscar?text=CANALETA+RANURADA+40X25",
        "img": f"{BASE_URL}/foto/acc-300/CANALETA-RANURADA.jpg",
        "marca": "Genérica",
        "unidad": "Unidad",
    },
    {
        "sku": "ACC-301",
        "name": "CANALETA RANURADA PVC BLANCA 60X40MM (2MT)",
        "price": 7.50,
        "dep": "🔩 Accesorios Conductores Eléctricos",
        "link": f"{BASE_URL}/buscar?text=CANALETA+RANURADA+60X40",
        "img": f"{BASE_URL}/foto/acc-301/CANALETA-RANURADA-60.jpg",
        "marca": "Genérica",
        "unidad": "Unidad",
    },
    # ---- MATERIAL ELÉCTRICO ----
    {
        "sku": "ELEC-001",
        "name": "INTERRUPTOR TERMICO 1X20A RIEL DIN SCHNEIDER",
        "price": 8.50,
        "dep": "⚡ Material Eléctrico",
        "link": f"{BASE_URL}/buscar?text=INTERRUPTOR+TERMICO+1X20A+SCHNEIDER",
        "img": f"{BASE_URL}/foto/elec-001/BREAKER-SCHNEIDER.jpg",
        "marca": "Schneider Electric",
        "unidad": "Unidad",
    },
    {
        "sku": "ELEC-002",
        "name": "INTERRUPTOR TERMICO 2X20A RIEL DIN SCHNEIDER",
        "price": 15.90,
        "dep": "⚡ Material Eléctrico",
        "link": f"{BASE_URL}/buscar?text=INTERRUPTOR+TERMICO+2X20A",
        "img": f"{BASE_URL}/foto/elec-002/BREAKER-2X20.jpg",
        "marca": "Schneider Electric",
        "unidad": "Unidad",
    },
    {
        "sku": "ELEC-003",
        "name": "TOMACORRIENTE DOBLE POLARIZADO BLANCO 110V",
        "price": 1.95,
        "dep": "⚡ Material Eléctrico",
        "link": f"{BASE_URL}/buscar?text=TOMACORRIENTE+DOBLE+POLARIZADO",
        "img": f"{BASE_URL}/foto/elec-003/TOMACORRIENTE.jpg",
        "marca": "Leviton",
        "unidad": "Unidad",
    },
    {
        "sku": "ELEC-004",
        "name": "INTERRUPTOR SENCILLO 15A 120V BLANCO",
        "price": 1.50,
        "dep": "⚡ Material Eléctrico",
        "link": f"{BASE_URL}/buscar?text=INTERRUPTOR+SENCILLO+15A",
        "img": f"{BASE_URL}/foto/elec-004/INTERRUPTOR.jpg",
        "marca": "Leviton",
        "unidad": "Unidad",
    },
    {
        "sku": "ELEC-005",
        "name": "PANEL ELECTRICO RIEL DIN 12 ESPACIOS CON TAPA",
        "price": 28.00,
        "dep": "⚡ Material Eléctrico",
        "link": f"{BASE_URL}/buscar?text=PANEL+ELECTRICO+12+ESPACIOS",
        "img": f"{BASE_URL}/foto/elec-005/PANEL-ELECTRICO.jpg",
        "marca": "Schneider Electric",
        "unidad": "Unidad",
    },
    # ---- ALAMBRES Y MALLAS ----
    {
        "sku": "ALAM-001",
        "name": "ALAMBRE DE AMARRE GALVANIZADO NO. 16 (ROLLO 1LB)",
        "price": 1.80,
        "dep": "⛓️ Alambres y Mallas",
        "link": f"{BASE_URL}/buscar?text=ALAMBRE+AMARRE+GALVANIZADO+16",
        "img": f"{BASE_URL}/foto/alam-001/ALAMBRE-AMARRE.jpg",
        "marca": "Genérica",
        "unidad": "Rollo",
    },
    {
        "sku": "ALAM-002",
        "name": "ALAMBRE ESPIGADO GALVANIZADO CALIBRE 14 (ROLLO 200M)",
        "price": 45.00,
        "dep": "⛓️ Alambres y Mallas",
        "link": f"{BASE_URL}/buscar?text=ALAMBRE+ESPIGADO+GALVANIZADO",
        "img": f"{BASE_URL}/foto/alam-002/ALAMBRE-ESPIGADO.jpg",
        "marca": "Genérica",
        "unidad": "Rollo",
    },
]


def _crear_sesion():
    """Crea una sesión HTTP con headers realistas."""
    s = requests.Session()
    s.headers.update(HEADERS_DESKTOP)
    return s


def _parsear_precio(texto):
    """Extrae precio numérico de un string."""
    try:
        limpio = re.sub(r"[^\d.]", "", texto.replace(",", "."))
        return float(limpio) if limpio else 0.0
    except:
        return 0.0


def _extraer_imagen(soup, base_url=""):
    """Extrae la URL de imagen más probable de una tarjeta de producto."""
    # Intentar múltiples estrategias
    for selector in [
        {"name": "img", "attrs": {"class": lambda c: c and ("product" in " ".join(c).lower() or "foto" in " ".join(c).lower())}},
        {"name": "img", "attrs": {"itemprop": "image"}},
        {"name": "img", "attrs": {"class": "img-product"}},
    ]:
        img = soup.find(**selector)
        if img:
            src = img.get("src") or img.get("data-src") or img.get("data-lazy-src", "")
            if src and not src.endswith(".svg"):
                return src if src.startswith("http") else BASE_URL + src

    # Buscar cualquier imagen que no sea un logo/ícono pequeño
    for img in soup.find_all("img"):
        src = img.get("src") or img.get("data-src") or ""
        if src and not src.endswith(".svg") and "logo" not in src.lower() and "icon" not in src.lower():
            return src if src.startswith("http") else BASE_URL + src

    return ""


def scraping_busqueda_freund(termino: str, max_resultados: int = 30) -> list[dict]:
    """
    Realiza web scraping en la página de búsqueda de Freund.
    URL: /buscar?text=TERMINO
    Retorna lista de productos con imagen.
    """
    resultados = []
    url = f"{BASE_URL}/buscar?text={quote_plus(termino)}"

    try:
        sesion = _crear_sesion()
        # Visitar homepage primero para obtener cookies
        sesion.get(BASE_URL, timeout=5)
        time.sleep(0.5)

        resp = sesion.get(url, timeout=8)
        if resp.status_code != 200:
            return resultados

        soup = BeautifulSoup(resp.text, "html.parser")

        # Estrategia 1: Buscar tarjetas de producto con selectores comunes de Freund
        tarjetas = (
            soup.find_all("div", class_=re.compile(r"product", re.I)) or
            soup.find_all("article", class_=re.compile(r"product", re.I)) or
            soup.find_all("li", class_=re.compile(r"product", re.I))
        )

        for tarjeta in tarjetas[:max_resultados]:
            # Nombre
            nombre_elem = (
                tarjeta.find(["h2", "h3", "h4", "a"], class_=re.compile(r"name|title|product", re.I)) or
                tarjeta.find("a") or
                tarjeta.find(["h2", "h3", "h4"])
            )
            if not nombre_elem:
                continue
            nombre = nombre_elem.get_text(strip=True).upper()

            # Precio
            precio_elem = tarjeta.find(["span", "div", "p"], class_=re.compile(r"price|precio", re.I))
            precio = _parsear_precio(precio_elem.get_text()) if precio_elem else 0.0

            # Link
            link_elem = tarjeta.find("a", href=True)
            href = link_elem["href"] if link_elem else ""
            if href and not href.startswith("http"):
                href = BASE_URL + href

            # SKU (puede estar en data-sku, data-id, o en el link)
            sku = (
                tarjeta.get("data-sku") or
                tarjeta.get("data-product-id") or
                re.search(r"/(\d+)$", href).group(1) if href and re.search(r"/(\d+)$", href) else f"F-{len(resultados)+1}"
            )

            # Imagen
            img_url = _extraer_imagen(tarjeta)

            if nombre and len(nombre) > 3:
                resultados.append({
                    "sku": str(sku),
                    "name": nombre,
                    "price": precio,
                    "link": href,
                    "img": img_url,
                    "marca": "",
                    "unidad": "Unidad",
                    "fuente": "🌐 Web Freund (Live)",
                })

    except requests.exceptions.Timeout:
        pass
    except Exception:
        pass

    return resultados


def scraping_categoria_freund(url_categoria: str, termino: str = "", max_resultados: int = 30) -> list[dict]:
    """
    Scraping en una URL de categoría de Freund.
    """
    resultados = []
    try:
        sesion = _crear_sesion()
        sesion.get(BASE_URL, timeout=5)
        time.sleep(0.4)

        resp = sesion.get(url_categoria, timeout=8)
        if resp.status_code != 200:
            return resultados

        soup = BeautifulSoup(resp.text, "html.parser")

        tarjetas = (
            soup.find_all("div", class_=re.compile(r"product-block|product-item|product-card", re.I)) or
            soup.find_all("div", class_=re.compile(r"product", re.I)) or
            soup.find_all("li", class_=re.compile(r"product|item", re.I))
        )

        for tarjeta in tarjetas[:max_resultados]:
            nombre_elem = (
                tarjeta.find(["h3", "h2", "h4", "a"], class_=re.compile(r"name|title", re.I)) or
                tarjeta.find("a") or
                tarjeta.find("h3")
            )
            if not nombre_elem:
                continue
            nombre = nombre_elem.get_text(strip=True).upper()

            # Filtro por término si existe
            if termino and termino.lower() not in nombre.lower():
                continue

            precio_elem = tarjeta.find(["span", "div"], class_=re.compile(r"price|precio", re.I))
            precio = _parsear_precio(precio_elem.get_text()) if precio_elem else 0.0

            link_elem = tarjeta.find("a", href=True)
            href = link_elem["href"] if link_elem else ""
            if href and not href.startswith("http"):
                href = BASE_URL + href

            sku_match = re.search(r"/(\d+)$", href) if href else None
            sku = sku_match.group(1) if sku_match else f"C-{len(resultados)+1}"

            img_url = _extraer_imagen(tarjeta)

            if nombre and len(nombre) > 3:
                resultados.append({
                    "sku": str(sku),
                    "name": nombre,
                    "price": precio,
                    "link": href,
                    "img": img_url,
                    "marca": "",
                    "unidad": "Unidad",
                    "fuente": "🌐 Web Freund (Categoría)",
                })

    except Exception:
        pass

    return resultados


def buscar_catalogo_local(termino: str, departamento: str = "") -> list[dict]:
    """
    Búsqueda en la base de datos local por nombre, SKU o combinación.
    Soporta múltiples palabras clave (AND logic).
    """
    termino = termino.strip().upper()
    palabras = termino.split() if termino else []

    resultados = []
    for item in CATALOGO_LOCAL:
        # Filtro por departamento si se especifica
        if departamento and item["dep"] != departamento:
            continue

        texto_busqueda = f"{item['name']} {item['sku']} {item.get('marca','')}".upper()

        # Si hay SKU exacto, tiene prioridad máxima
        if termino and termino == item["sku"].upper():
            resultados.insert(0, {**item, "fuente": "📦 Catálogo Local"})
            continue

        # Búsqueda AND: todas las palabras deben estar presentes
        if not palabras:
            resultados.append({**item, "fuente": "📦 Catálogo Local"})
        elif all(p in texto_busqueda for p in palabras):
            resultados.append({**item, "fuente": "📦 Catálogo Local"})

    return resultados


def buscar_productos_freund(
    termino: str,
    url_categoria: str = "",
    departamento_label: str = "",
    usar_scraping: bool = True,
    max_resultados: int = 30,
) -> tuple[list[dict], str]:
    """
    Motor principal de búsqueda.
    1. Intenta scraping en /buscar?text=TERM
    2. Intenta scraping en la categoría si falla
    3. Siempre combina con catálogo local
    Retorna (lista_resultados, mensaje_fuente)
    """
    resultados_web = []
    mensaje = ""

    if usar_scraping and termino:
        # Intento 1: búsqueda general en Freund
        resultados_web = scraping_busqueda_freund(termino, max_resultados)

        # Intento 2: búsqueda en la categoría específica
        if not resultados_web and url_categoria:
            resultados_web = scraping_categoria_freund(url_categoria, termino, max_resultados)

        if resultados_web:
            mensaje = f"✅ {len(resultados_web)} productos encontrados en Freund (en vivo)"
        else:
            mensaje = "⚠️ Scraping no disponible — mostrando catálogo local"
    else:
        mensaje = "📦 Búsqueda en catálogo local"

    # Siempre agregar resultados del catálogo local (sin duplicar SKUs)
    skus_web = {r["sku"] for r in resultados_web}
    local = buscar_catalogo_local(termino, departamento_label)
    for item in local:
        if item["sku"] not in skus_web:
            resultados_web.append(item)

    return resultados_web, mensaje
