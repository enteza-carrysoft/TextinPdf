# -*- coding: utf-8 -*-
import streamlit as st
import io
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

# --- Configuración de la interfaz de usuario ---
st.title("Añadir Código a Documento PDF")
st.markdown("Sube un PDF y añade texto a la primera página.")

# Componente para subir el archivo PDF
uploaded_file = st.file_uploader("Sube tu archivo PDF aquí", type="pdf")

# Componentes para la entrada de texto y coordenadas
user_text = st.text_input("Escribe el texto que quieres añadir:", "Texto de ejemplo")
col1, col2 = st.columns(2)
with col1:
    pos_x = st.number_input("Coordenada X del texto (horizontal):", value=50, min_value=0)
with col2:
    pos_y = st.number_input("Coordenada Y del texto (vertical):", value=680, min_value=0)

# El botón de generación solo se muestra si se ha subido un archivo
if uploaded_file is not None:
    if st.button("Generar PDF Modificado"):
        st.info("Generando tu PDF, por favor espera...")
        
        try:
            # --- Lógica del proceso (Backend) ---
            
            # 1. Leer el PDF original subido por el usuario en memoria
            original_pdf_buffer = io.BytesIO(uploaded_file.getvalue())
            original_reader = PdfReader(original_pdf_buffer)
            
            # Obtener el tamaño de la primera página del PDF original para el lienzo
            first_page = original_reader.pages[0]
            page_width = first_page.mediabox.width
            page_height = first_page.mediabox.height
            
            # 2. Crear un nuevo PDF temporal de una sola página con el texto de superposición
            text_overlay_buffer = io.BytesIO()
            # El tamaño del lienzo debe coincidir con el de la primera página del PDF
            text_canvas = canvas.Canvas(text_overlay_buffer, pagesize=(page_width, page_height))
            
            # Dibujar el texto en el lienzo en las coordenadas especificadas
            text_canvas.setFont("Helvetica", 12)
            text_canvas.drawString(pos_x, pos_y, user_text)
            
            # Finalizar la creación del lienzo
            text_canvas.showPage()
            text_canvas.save()
            
            # Mover el cursor al inicio del buffer para poder leerlo
            text_overlay_buffer.seek(0)
            
            # 3. Leer el PDF de superposición
            text_reader = PdfReader(text_overlay_buffer)
            overlay_page = text_reader.pages[0]
            
            # 4. Fusionar la página de superposición sobre la primera página del PDF original
            original_first_page = original_reader.pages[0]
            # La superposición se realiza en su lugar
            original_first_page.merge_page(overlay_page)
            
            # 5. Crear un nuevo objeto PdfWriter para construir el PDF final
            pdf_writer = PdfWriter()
            
            # 6. Añadir la primera página modificada al nuevo PDF
            pdf_writer.add_page(original_first_page)
            
            # 7. Ya no se añaden las páginas restantes. Solo se guarda la primera página.
            
            # 8. Guardar el PDF final en un buffer de memoria
            final_pdf_buffer = io.BytesIO()
            pdf_writer.write(final_pdf_buffer)
            final_pdf_buffer.seek(0)
            
            # 9. Mostrar el botón de descarga
            st.success("¡PDF generado exitosamente!")
            st.download_button(
                label="Descargar PDF Modificado",
                data=final_pdf_buffer,
                file_name="documento_modificado.pdf",
                mime="application/pdf"
            )
            
        except Exception as e:
            st.error(f"Ocurrió un error al procesar el archivo: {e}")
            
# Mensaje de ayuda si no se ha subido ningún archivo
else:
    st.warning("Por favor, sube un archivo PDF para comenzar.")