# --- PESTAÑA 3: MANO DE OBRA, LOGÍSTICA Y HERRAMIENTAS ---
with tab3:
    st.subheader("🛠️ Presupuesto de Mano de Obra, Viáticos y Herramientas")
    st.info("Configura los costos operativos. El bloque técnico y logístico calcula por defecto una rentabilidad del 20% (editable).")

    # CONTENEDOR GLOBAL DE ENTRADAS
    col_izq, col_der = st.columns([1, 1])

    with col_izq:
        st.markdown("#### ⚙️ 1. Personal Técnico y Logística")
        
        # Control de Rentabilidad para este bloque (Por defecto 20%)
        rent_mo = st.number_input("Rentabilidad Comercial del Bloque (%)", min_value=0.0, max_value=99.0, value=20.0, step=5.0, key="rent_mo_global")
        margen_mo_dec = rent_mo / 100.0

        # Formulario ordenado para capturar cada rubro técnico
        with st.form("form_mano_obra_detallado"):
            st.markdown("**Carga de Personal y Estadías:**")
            
            # Configuradores e Instaladores
            c1, c2 = st.columns(2)
            cant_conf = c1.number_input("Cantidad Configuradores", min_value=0, value=0, step=1)
            dias_conf = c2.number_input("Días Configurador", min_value=0, value=0, step=1)
            tarifa_conf = st.number_input("Costo Diario Configurador ($)", min_value=0.0, value=50.0, step=5.0)
            
            st.markdown("---")
            c3, c4 = st.columns(2)
            cant_inst = c3.number_input("Cantidad Instaladores", min_value=0, value=0, step=1)
            dias_inst = c4.number_input("Días Instalador", min_value=0, value=0, step=1)
            tarifa_inst = st.number_input("Costo Diario Instalador ($)", min_value=0.0, value=25.0, step=5.0)
            
            st.markdown("---")
            # Rubros adicionales solicitados
            c5, c6 = st.columns(2)
            dias_estadia = c5.number_input("Días Estadía fuera de SS", min_value=0, value=0, step=1)
            costo_estadia = c6.number_input("Costo Diario Estadía ($)", min_value=0.0, value=0.0, step=5.0)
            
            c7, c8 = st.columns(2)
            dias_viaticos = c7.number_input("Días de Viáticos", min_value=0, value=0, step=1)
            costo_viaticos = c8.number_input("Costo Diario Viáticos ($)", min_value=0.0, value=0.0, step=5.0)
            
            st.markdown("---")
            c9, c10 = st.columns(2)
            dias_out = c9.number_input("Días Técnico Outsourcing", min_value=0, value=0, step=1)
            costo_out = c10.number_input("Costo Diario Outsourcing ($)", min_value=0.0, value=0.0, step=10.0)
            
            c11, c12 = st.columns(2)
            dias_noc = c11.number_input("Días Técnico Nocturno / Fin de Semana", min_value=0, value=0, step=1)
            costo_noc = c12.number_input("Costo Diario Nocturno ($)", min_value=0.0, value=0.0, step=10.0)
            
            st.markdown("---")
            # Combustible integrado en el formulario
            st.markdown("**Movilización:**")
            kms_proyecto = st.number_input("Kilómetros totales a recorrer (KM)", min_value=0.0, value=0.0, step=10.0)
            
            btn_guardar_mo = st.form_submit_button("🔒 Guardar y Calcular Bloque Operativo")

            if btn_guardar_mo:
                # ESTRUCTURACIÓN DE COSTOS INTERNOS (LO QUE TE CUESTA A TI)
                c_conf_tot = cant_conf * dias_conf * tarifa_conf
                c_inst_tot = cant_inst * dias_inst * tarifa_inst
                c_est_tot = dias_estadia * costo_estadia
                c_via_tot = dias_viaticos * costo_viaticos
                c_out_tot = dias_out * costo_out
                c_noc_tot = dias_noc * costo_noc
                c_comb_tot = kms_proyecto * 0.36
                
                costo_operativo_pestaña = c_conf_tot + c_inst_tot + c_est_tot + c_via_tot + c_out_tot + c_noc_tot + c_comb_tot
                
                # Guardamos en session_state para mantener la persistencia entre pestañas
                st.session_state["mano_obra_bloque"] = {
                    "Costo Interno": costo_operativo_pestaña,
                    "Rentabilidad Aplicada (%)": rent_mo,
                    "Detalle": {
                        "Configuradores": c_conf_tot,
                        "Instaladores": c_inst_tot,
                        "Estadía fuera de SS": c_est_tot,
                        "Viáticos": c_via_tot,
                        "Outsourcing": c_out_tot,
                        "Nocturno/Finde": c_noc_tot,
                        "Combustible": c_comb_tot
                    }
                }
                st.success("¡Costos operativos y de personal guardados exitosamente!")

    with col_der:
        st.markdown("#### 🔧 2. Certificaciones y Herramientas Especiales")
        st.caption("Los montos ingresados aquí se suman directamente al costo final sin aplicar el margen del personal.")
        
        # Formulario para añadir certificaciones/herramientas de forma independiente
        with st.form("form_herramientas"):
            c_desc = st.text_input("Descripción del Item", placeholder="Ej. Certificación de SLC Honeywell o Renta de Andaquios")
            c_monto = st.number_input("Costo Total del Item ($)", min_value=0.0, value=0.0, step=25.0)
            btn_add_h = st.form_submit_button("Agregar Herramienta / Certificación")
            
            if btn_add_h and c_desc:
                st.session_state["materiales"].append({
                    "Borrar": False,
                    "Descripción": f"[HERRAMIENTA/CERT] {c_desc}",
                    "Cantidad": 1,
                    "Costo Unitario ($)": float(c_monto),
                    "Costo Total ($)": float(c_monto),
                    "Rentabilidad (%)": 0.0, # 0% porque va al costo directo
                    "Precio Venta U ($)": float(c_monto),
                    "Precio Venta Total ($)": float(c_monto)
                })
                st.success(f"Agregado: {c_desc}")

        # Visualización de herramientas añadidas utilizando el editor dinámico
        items_herramientas = [x for x in st.session_state["materiales"] if x["Descripción"].startswith("[HERRAMIENTA/CERT]")]
        if items_herramientas:
            st.markdown("##### Herramientas y Certificaciones en este Proyecto:")
            df_h = pd.DataFrame(items_herramientas)
            st.dataframe(df_h[["Descripción", "Costo Total ($)"]], hide_index=True, use_container_width=True)
            if st.button("Limpiar Herramientas", key="clear_h_btn"):
                st.session_state["materiales"] = [x for x in st.session_state["materiales"] if not x["Descripción"].startswith("[HERRAMIENTA/CERT]")]
                st.rerun()

    # =========================================================================
    # 3. SECCIÓN DE BALANCE: CUÁNTO TE CUESTA A TI VS CUÁNTO AL CLIENTE
    # =========================================================================
    st.markdown("---")
    st.markdown("### 📊 Balance Financiero de Operación (Mano de Obra + Logística + Herramientas)")
    
    # Extraemos los datos calculados del bloque de personal
    mo_datos = st.session_state.get("mano_obra_bloque", {"Costo Interno": 0.0, "Rentabilidad Aplicada (%)": 20.0, "Detalle": {}})
    costo_interno_personal = mo_datos["Costo Interno"]
    rent_actual_pct = mo_datos["Rentabilidad Aplicada (%)"] / 100.0
    
    # Cálculo del precio al cliente para el personal aplicando el margen respectivo
    precio_cliente_personal = costo_interno_personal / (1 - rent_actual_pct) if rent_actual_pct < 1 else costo_interno_personal
    
    # Sumatoria de herramientas/certificaciones directas
    total_herramientas_directas = sum(x["Costo Total ($)"] for x in st.session_state["materiales"] if x["Descripción"].startswith("[HERRAMIENTA/CERT]"))
    
    # TOTALES FINALES CONSOLIDADOS DE ESTA PESTAÑA
    gran_costo_interno_mo = costo_interno_personal + total_herramientas_directas
    gran_precio_cliente_mo = precio_cliente_personal + total_herramientas_directas

    # Despliegue de tarjetas KPI informativas
    cb1, cb2, cb3 = st.columns(3)
    cb1.metric("Tu Costo Interno Real", f"${gran_costo_interno_mo:,.2f}", help="Suma de tu planilla real, combustible consumido y herramientas.")
    cb2.metric("Precio de Venta al Cliente", f"${gran_precio_cliente_mo:,.2f}", help="Suma del personal con el margen aplicado + herramientas al costo.")
    cb3.metric("Utilidad Operativa Retenida", f"${(gran_precio_cliente_mo - gran_costo_interno_mo):,.2f}")

    # Tabla ejecutiva de desglose interno para validación visual rápida
    st.markdown("##### Desglose de Distribución Económica:")
    tabla_balance_mo = {
        "Concepto Operativo": ["Personal Técnico y Logística", "Herramientas y Certificaciones Directas", "TOTAL ACUMULADO"],
        "A mi me cuesta ($)": [costo_interno_personal, total_herramientas_directas, gran_costo_interno_mo],
        "Al Cliente le cuesta ($)": [precio_cliente_personal, total_herramientas_directas, gran_precio_cliente_mo]
    }
    st.table(pd.DataFrame(tabla_balance_mo))
