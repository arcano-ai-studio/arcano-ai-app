import streamlit as st
import google.generativeai as genai
from PIL import Image, ImageDraw
from fpdf import FPDF
import io

# Configuración de la pantalla
st.set_page_config(page_title="Arcano AI Studio", page_icon="🏢", layout="wide")

st.title("🏢 Arcano AI Studio")
st.subheader("Central de Inteligencia Inmobiliaria - Versión Pro (Marca Blanca)")
st.markdown("Genera kits de venta personalizados al instante: Mensaje de WhatsApp, Collage y Ficha PDF con imágenes integradas.")
st.markdown("---")

st.sidebar.header("⚙️ Configuración del Motor")
api_key = st.sidebar.text_input("API Key de Gemini:", type="password")

col1, col2 = st.columns([1, 1])

with col1:
    st.write("### 👤 1. Configuración de Marca Blanca")
    inmobiliaria = st.text_input("Nombre de la Inmobiliaria:", value="Arconte Bienes Raíces")
    asesor = st.text_input("Nombre del Asesor:", value="Javier Enciso")
    contacto = st.text_input("WhatsApp de Contacto (Ej: 7711234567):")
    
    st.write("### 📝 2. Datos del Inmueble")
    titulo_propiedad = st.text_input("Título Comercial (Ej: Casa Moderna en Forjadores):")
    precio_inmueble = st.text_input("Precio de Operación (Ej: $2,700,000 MXN):")
    descripcion = st.text_area("Descripción cruda (Metros, distribución, esquema legal, etc.):", height=120)
    
    st.write("### 📸 3. Expediente Fotográfico (Sube 4 Fotos)")
    foto1 = st.file_uploader("Foto 1: Fachada Principal", type=['jpg', 'jpeg', 'png'])
    foto2 = st.file_uploader("Foto 2: Estancia / Interiores", type=['jpg', 'jpeg', 'png'])
    foto3 = st.file_uploader("Foto 3: Recámaras / Cocina", type=['jpg', 'jpeg', 'png'])
    foto4 = st.file_uploader("Foto 4: Amenidades / Detalles", type=['jpg', 'jpeg', 'png'])

def crear_collage(img1, img2, img3, img4):
    lienzo = Image.new('RGB', (1080, 1080), color=(26, 43, 76)) 
    def preparar(f): return Image.open(f).resize((540, 540))
    lienzo.paste(preparar(img1), (0, 0))
    lienzo.paste(preparar(img2), (540, 0))
    lienzo.paste(preparar(img3), (0, 540))
    lienzo.paste(preparar(img4), (540, 540))
    dibujo = ImageDraw.Draw(lienzo)
    dibujo.rectangle([0, 950, 1080, 1080], fill=(197, 168, 128)) 
    return lienzo

# EL NUEVO MOTOR ESTÉTICO DE PDF
def generar_pdf(titulo, precio, copy_ia, name_inmo, name_asesor, num_cont, f1, f2, f3, f4):
    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=False) # Bloqueamos los saltos automáticos para tener control total
    
    # --- PÁGINA 1: FICHA TÉCNICA E IDENTIDAD ---
    pdf.add_page()
    
    # Banner Superior (Azul Marino)
    pdf.set_fill_color(26, 43, 76)
    pdf.rect(0, 0, 210, 30, 'F')
    
    # Textos del Banner Superior
    pdf.set_font("Helvetica", 'B', 22)
    pdf.set_text_color(255, 255, 255) # Blanco
    pdf.set_xy(15, 8)
    pdf.cell(0, 10, name_inmo.upper(), ln=False)
    
    pdf.set_font("Helvetica", '', 10)
    pdf.set_text_color(197, 168, 128) # Dorado
    pdf.set_xy(15, 18)
    pdf.cell(0, 5, f"FICHA TÉCNICA EXCLUSIVA | ASESOR: {name_asesor.upper()}", ln=False)
    
    # Caja Gris para Título y Precio
    pdf.set_fill_color(240, 240, 240)
    pdf.rect(15, 40, 180, 15, 'F')
    
    pdf.set_font("Helvetica", 'B', 14)
    pdf.set_text_color(26, 43, 76)
    pdf.set_xy(18, 42.5)
    pdf.cell(110, 10, titulo.upper()[:45], ln=False) # Corta si el título es inmenso
    
    pdf.set_font("Helvetica", 'B', 14)
    pdf.set_text_color(197, 168, 128)
    pdf.set_xy(130, 42.5)
    pdf.cell(60, 10, precio, ln=False, align='R')
    
    # Título de Descripción
    pdf.set_xy(15, 65)
    pdf.set_font("Helvetica", 'B', 12)
    pdf.set_text_color(26, 43, 76)
    pdf.cell(0, 10, "DESCRIPCIÓN DE LA PROPIEDAD", ln=True)
    pdf.line(15, pdf.get_y(), 195, pdf.get_y())
    pdf.ln(5)
    
    # Texto Descriptivo
    texto_seguro = copy_ia.encode('latin-1', 'ignore').decode('latin-1')
    pdf.set_font("Helvetica", '', 11)
    pdf.set_text_color(60, 60, 60)
    pdf.multi_cell(180, 6.5, texto_seguro)
    
    # Banner Inferior de Contacto (Pegado al fondo)
    pdf.set_fill_color(26, 43, 76)
    pdf.rect(15, 260, 180, 22, 'F')
    
    pdf.set_font("Helvetica", 'B', 11)
    pdf.set_text_color(197, 168, 128)
    pdf.set_xy(15, 263)
    pdf.cell(180, 7, "¿Listo para agendar una visita?", align='C', ln=True)
    pdf.set_font("Helvetica", '', 11)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(180, 7, f"Contacte a {name_asesor} al WhatsApp: {num_cont}", align='C')
    
    # --- PÁGINA 2: GALERÍA VISUAL EXACTA ---
    pdf.add_page()
    
    # Mini Banner Superior para Galería
    pdf.set_fill_color(26, 43, 76)
    pdf.rect(0, 0, 210, 20, 'F')
    pdf.set_font("Helvetica", 'B', 14)
    pdf.set_text_color(255, 255, 255)
    pdf.set_xy(15, 5)
    pdf.cell(180, 10, "GALERÍA FOTOGRÁFICA", align='C')
    
    # Cuadrícula matemática (2x2 perfecta)
    try:
        # X, Y, Ancho, Alto
        if f1: pdf.image(Image.open(f1), x=15, y=30, w=85, h=85)
        if f2: pdf.image(Image.open(f2), x=110, y=30, w=85, h=85)
        if f3: pdf.image(Image.open(f3), x=15, y=125, w=85, h=85)
        if f4: pdf.image(Image.open(f4), x=110, y=125, w=85, h=85)
    except Exception as e:
        pass
        
    # Disclaimer Legal
    pdf.set_xy(15, 280)
    pdf.set_font("Helvetica", 'I', 9)
    pdf.set_text_color(150, 150, 150)
    pdf.cell(180, 10, f"Catálogo digital generado exclusivamente para {name_inmo}", align='C')
    
    return bytes(pdf.output())

with col2:
    st.write("### 🪐 Materiales Listos para Descarga")
    
    if st.button("🚀 Iniciar Procesamiento de Alta Velocidad", use_container_width=True):
        if not api_key: st.error("⚠️ Falta ingresar tu API Key maestra.")
        elif not descripcion or not precio_inmueble or not titulo_propiedad: st.warning("⚠️ Faltan datos del inmueble.")
        elif not contacto: st.warning("⚠️ Ingresa un número de WhatsApp.")
        elif not (foto1 and foto2 and foto3 and foto4): st.warning("⚠️ Faltan fotografías.")
        else:
            try:
                genai.configure(api_key=api_key)
                modelo = genai.GenerativeModel('gemini-2.5-flash')
                
                with st.spinner('Modelando diseño, adaptando branding y ensamblando PDF Estético...'):
                    # Modificamos el prompt para limitar las palabras y evitar desbordes en el PDF
                    prompt = f"""
                    Eres un experto copywriter del sector inmobiliario. Escribe DOS bloques separados por "===SEPARADOR===". Sin saludos.
                    
                    Información:
                    - Título: {titulo_propiedad}
                    - Precio: {precio_inmueble}
                    - Detalles: {descripcion}
                    - Asesor: {asesor}
                    - Link: https://wa.me/{contacto}
                    
                    BLOQUE 1: Copy de WhatsApp persuasivo, viñetas, emojis y llamado a la acción.
                    ===SEPARADOR===
                    BLOQUE 2: Descripción ejecutiva, formal, sin emojis. MÁXIMO 130 PALABRAS (muy importante para que quepa en la hoja membretada). Enfocado en beneficios.
                    """
                    
                    respuesta = modelo.generate_content(prompt)
                    textos = respuesta.text.split("===SEPARADOR===")
                    copy_whatsapp = textos[0].strip()
                    texto_pdf = textos[1].strip() if len(textos) > 1 else copy_whatsapp
                    
                    collage_final = crear_collage(foto1, foto2, foto3, foto4)
                    pdf_final_bytes = generar_pdf(
                        titulo_propiedad, precio_inmueble, texto_pdf, 
                        inmobiliaria, asesor, contacto, 
                        foto1, foto2, foto3, foto4
                    )
                
                st.download_button(
                    label="📄 Descargar Nueva Ficha Estética PDF",
                    data=pdf_final_bytes,
                    file_name=f"Ficha_Premium_{titulo_propiedad.replace(' ', '_')}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
                
                st.success("¡Ficha Premium Generada con Éxito!")
                st.markdown("#### 📲 Mensaje Personalizado de WhatsApp:")
                st.info(copy_whatsapp)
                st.markdown("#### 📸 Visual para Estados de WhatsApp y Catálogo:")
                st.image(collage_final, use_container_width=True)
                
            except Exception as e:
                st.error(f"Error en la línea de ensamblaje del sistema: {e}")
