# =========================================================================
# NUEVA LÓGICA DE RENDERIZADO CON ENLACES CLICKEABLES EN VISTA PREVIA
# =========================================================================
if coincidencias:
    st.markdown(f"#### 📊 Materiales encontrados ({len(coincidencias)})")
    st.markdown("---")
    
    for i, m in enumerate(coincidencias):
        with st.container():
            c_img, c_desc, c_precio, c_accion = st.columns([1.2, 3.5, 1, 2])
            
            with c_img:
                # Determinamos una URL de destino (si el scraping no la da, apuntamos al home de la ferretería)
                url_producto_freund = m.get("link") if m.get("link") else "https://www.freundferreteria.com"
                
                # Renderizamos el contenedor como un botón/tarjeta totalmente clickeable con HTML
                st.markdown(
                    f"""
                    <a href="{url_producto_freund}" target="_blank" style="text-decoration: none;">
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
                    st.toast(f"✅ Agregado al presupuesto: {m['name']}")
            
            st.markdown("<div style='margin-top: 10px; margin-bottom: 10px; border-bottom: 1px solid #2d3139;'></div>", unsafe_allow_html=True)
