def obtener_datos_reales_producto(url_producto):
    """
    Visita la página del producto y extrae la información real usando etiquetas Open Graph
    y selectores específicos de precio para asegurar consistencia al 100%.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "es-SV,es;q=0.9,en;q=0.8" # Forzamos contexto de El Salvador si aplica
    }
    try:
        respuesta = requests.get(url_producto, headers=headers, timeout=7)
        if respuesta.status_code == 200:
            soup = BeautifulSoup(respuesta.text, "html.parser")
            
            # 1. Extraer Imagen Real de Azure Blob Storage via og:image
            meta_img = soup.find("meta", property="og:image")
            url_imagen = meta_img["content"] if meta_img else None
            
            # 2. Extraer Título Real del Producto via og:title
            meta_title = soup.find("meta", property="og:title")
            nombre_real = meta_title["content"].strip().upper() if meta_title else None
            
            # 3. EXTRAER PRECIO REAL VISIBLE EN TIENDA (Evita desfases de centavos)
            precio = None
            
            # Prioridad 1: Buscar la clase de precio de venta principal en el HTML visible
            # Freund suele usar clases específicas como 'product-price', 'current-price', o IDs contenedores
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
                            break # Encontró el precio visible de la página web
                    except ValueError:
                        continue
            
            # Prioridad 2: Si el raspado visual falla, usamos la etiqueta meta de comercio
            if not precio:
                meta_price = soup.find("meta", property="product:price:amount")
                if meta_price:
                    precio = float(meta_price["content"])
            
            return {"name": nombre_real, "image": url_imagen, "price": precio}
    except Exception as e:
        # Imprime el error en la consola de Streamlit para diagnóstico si es necesario
        print(f"Error de scraping en producto: {e}") 
    return None
