# --- SECCIÓN DE GENERACIÓN DE PDF CORREGIDA ---
        def generar_pdf():
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Helvetica", size=12)
            
            # Título
            pdf.set_font("Helvetica", "B", 16)
            pdf.cell(190, 10, txt="ALFA SECURITY EL SALVADOR", ln=True, align="C")
            pdf.set_font("Helvetica", "", 12)
            pdf.cell(190, 10, txt="Oferta Económica Comercial", ln=True, align="C")
            pdf.ln(10)
            
            # Datos Generales
            pdf.set_font("Helvetica", "B", 12)
            pdf.cell(190, 8, txt="Datos Generales:", ln=True)
            pdf.set_font("Helvetica", "", 11)
            pdf.cell(190, 6, txt=f"Proyecto: {proyecto}", ln=True)
            pdf.cell(190, 6, txt=f"Cliente / Empresa: {empresa}", ln=True)
            pdf.cell(190, 6, txt=f"Atención a: {atencion}", ln=True)
            pdf.cell(190, 6, txt=f"Validez de Oferta: {validez}", ln=True)
            pdf.cell(190, 6, txt=f"Condiciones de Pago: {pago}", ln=True)
            pdf.ln(8)
            
            # Tabla Encabezados
            pdf.set_font("Helvetica", "B", 11)
            pdf.cell(140, 8, txt="Descripción del Rubro / Componente", border=1)
            pdf.cell(50, 8, txt="Total ($)", border=1, ln=True, align="R")
            
            # 1. Equipos Principales Detallados
            if lista_eq:
                pdf.set_font("Helvetica", "B", 10)
                pdf.cell(190, 6, txt="--- EQUIPOS PRINCIPALES ---", border=1, ln=True)
                pdf.set_font("Helvetica", "", 10)
                for eq in lista_eq:
                    txt_desc = f"{eq['Descripción']} (Cant: {eq['Cantidad']} x ${eq['Precio Venta U ($)']:.2f})"
                    pdf.cell(140, 6, txt=txt_desc, border=1)
                    pdf.cell(50, 6, txt=f"${eq['Precio Venta Total ($)']:.2f}", border=1, ln=True, align="R")
            
            # 2. Bloque Mano de Obra
            if venta_mo_tot > 0:
                pdf.set_font("Helvetica", "", 10)
                pdf.cell(140, 6, txt="Mano de Obra (Servicios técnicos, logística, certificaciones y herramientas)", border=1)
                pdf.cell(50, 6, txt=f"${venta_mo_tot:.2f}", border=1, ln=True, align="R")
                
            # 3. Bloque Materiales y Suministros
            if venta_materiales > 0:
                pdf.set_font("Helvetica", "", 10)
                pdf.cell(140, 6, txt="Materiales y Suministros", border=1)
                pdf.cell(50, 6, txt=f"${venta_materiales:.2f}", border=1, ln=True, align="R")
                
            pdf.ln(6)
            
            # Cierre Totales
            pdf.set_font("Helvetica", "B", 11)
            pdf.cell(140, 6, txt="SUBTOTAL", align="R")
            pdf.cell(50, 6, txt=f"${subtotal_venta_proyecto:.2f}", border=1, ln=True, align="R")
            
            pdf.cell(140, 6, txt="IVA (13%)" if aplicar_iva else "IVA (0%)", align="R")
            pdf.cell(50, 6, txt=f"${iva_calc:.2f}", border=1, ln=True, align="R")
            
            pdf.cell(140, 6, txt="TOTAL NETO", align="R")
            pdf.set_font("Helvetica", "B", 12)
            pdf.cell(50, 6, txt=f"${total_general_cliente:.2f}", border=1, ln=True, align="R")
            
            # fpdf2 devuelve los bytes directamente con un output vacío
            return pdf.output()

        # Botón de Descarga Seguro
        if tabla_final_items:
            try:
                pdf_bytes = generar_pdf()
                st.download_button(
                    label="📥 Descargar Cotización en PDF",
                    data=bytes(pdf_bytes),
                    file_name=f"Cotizacion_{proyecto.replace(' ', '_')}.pdf",
                    mime="application/pdf"
                )
            except Exception as e:
                st.error(f"Error generando el PDF: {e}")
