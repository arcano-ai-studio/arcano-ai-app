import streamlit as st
import google.generativeai as genai
from PIL import Image, ImageDraw
from fpdf import FPDF
import io

# Configuración de la pantalla de trabajo
st.set_page_config(page_title="Arcano AI Studio", page_icon="🏢", layout="wide")

st.title("🏢 Arcano AI Studio")
st.subheader("Central de Inteligencia Inmobiliaria - Versión Pro (Marca Blanca)")
st.markdown("Genera kits de venta personalizados al instante: Mensaje de WhatsApp, Collage y Ficha PDF con imágenes integradas.")
st.markdown("---")

# Panel lateral de control técnico
st.sidebar.header("⚙️ Configuración del Motor")
api_key = st.sidebar.text_input("API Key de Gemini:", type="password")

# Organización del espacio de trabajo en dos grandes bloques (Entradas y Salidas)
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

# Función para armar el collage visual de los estados de WhatsApp
def crear_collage(img1, img2, img3, img4):
    lienzo = Image.new('RGB', (1080, 1080), color=(26, 43, 76)) # Fondo Azul Marino Arconte
    def preparar(f): return Image.open(f).resize((540, 540))
    lienzo.paste(preparar(img1), (0, 0))
    lienzo.paste(preparar(img2), (540, 0))
    lienzo.paste(preparar(img3), (0, 540))
    lienzo.paste(preparar(img4), (540, 540))
    dibujo = ImageDraw.Draw(lienzo)
    dibujo.rectangle([0, 950, 1080, 1080], fill=(197, 168, 128)) # Banner dorado inferior
    return lienzo

# Función Maestra para fabricar la Ficha Técnica Ejecutiva en PDF
def generar_pdf(titulo, precio, copy_ia, name_inmo, name_asesor, num_cont, f1, f2, f3, f4):
    pdf = FPDF()
    
    # --- PÁGINA 1: IDENTIDAD CORPORATIVA Y DATOS TÉCNICOS ---
    pdf.add_page()
    
    # Encabezado Comercial Dinámico
    pdf.set_font("Helvetica", 'B', 22)
    pdf.set_text_color(26, 43, 76) # Azul Ejecutivo
    pdf.cell(0, 10, name_inmo.upper(), ln=True, align='L')
    
    pdf.set_font("Helvetica", '', 10)
    pdf.set_text_color(197, 168, 128) # Dorado Elegante
    pdf.cell(0, 5, f"FICHA TÉCNICA EXCLUSIVA | ASESOR ATENDIENDO: {name_asesor.upper()}", ln=True, align='L')
    pdf.ln(10)
    
    # Título del Inmueble y Precio
    pdf.set_font("Helvetica", 'B', 15)
    pdf.set_text_color(50, 50, 50)
    pdf.cell(120, 10, titulo.upper(), ln=False)
    pdf.set_text_color(26, 43, 76)
    pdf.cell(0, 10, precio, ln=True, align='R')
    pdf.line(10, pdf.get_y()+2, 200, pdf.get_y()+2)
    pdf.ln(10)
    
    # Reseña de la Propiedad redactada por la IA
    # (Filtramos emojis con codificación segura latin-1 para evitar caídas del PDF)
    texto_seguro = copy_ia.encode('latin-1', 'ignore').decode('latin-1')
    pdf.set_font("Helvetica", '', 11)
    pdf.set_text_color(60, 60, 60)
    pdf.multi_cell(0, 7, texto_seguro)
    
    # Bloque de Cierre y Contacto Directo de la Inmobiliaria
    pdf.set_y(-35)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(4)
    pdf.set_font("Helvetica", 'B', 11)
    pdf.set_text_color(26, 43, 76)
    pdf.cell(0, 6, f"Para más informes o agendar una visita, contacte directamente a:", ln=True, align='C')
    pdf.set_font("Helvetica", '', 11)
    pdf.set_text_color(50, 50, 50)
    pdf.cell(0, 6, f"Asesor: {name_asesor}  |  Teléfono / WhatsApp: {num_cont}", ln=True, align='C')
    
    # --- PÁGINA 2: GALERÍA DE IMÁGENES AUTOMÁTICA ---
    pdf.add_page()
    pdf.set_font("Helvetica", 'B', 14)
    pdf.set_text_color(26, 43, 76)
    pdf.cell(0, 10, "GALERÍA REGISTRADA DEL INMUEBLE", ln=True, align='C')
    pdf.ln(10)
    
    # Cuadrícula matemática para incrustar las fotos en formato 2x2 en la hoja A4
    try:
        if f1: pdf.image(Image.open(f1), x=15, y=35, w=85, h=85)
        if f2: pdf.image(Image.open(f2), x=110, y=35, w=85, h=85)
        if f3: pdf.image(Image.open(f3), x=15, y=135, w=85, h=85)
        if f4: pdf.image(Image.open(f4), x=110, y=135, w=85, h=85)
    except Exception as e:
        # En caso de error de formato, el sistema continúa para no romper la descarga
        pass
        
    # Pie de página de la Galería
    pdf.set_y(-25)
    pdf.set_font("Helvetica", 'I', 9)
    pdf.set_text_color(150, 150, 150)
    pdf.cell(0, 10, f"Este catálogo digital es de uso exclusivo para clientes de {name_inmo}.", align='C')
    
    return pdf.output(dest='S')

with col2:
    st.write("### 🪐 Materiales Listos para Descarga")
    
    if st.button("🚀 Iniciar Procesamiento de Alta Velocidad", use_container_width=True):
        if not api_key: 
            st.error("⚠️ Falta ingresar tu API Key maestra en el menú izquierdo.")
        elif not descripcion or not precio_inmueble or not titulo_propiedad: 
            st.warning("⚠️ Debes llenar los campos de texto del inmueble para alimentar el cerebro.")
        elif not contacto:
            st.warning("⚠️ Ingresa un número de WhatsApp para poder tejer los llamados a la acción dinámicos.")
        elif not (foto1 and foto2 and foto3 and foto4): 
            st.warning("⚠️ Se requieren exactamente las 4 fotografías del expediente para generar la ficha e imagen.")
        else:
            try:
                genai.configure(api_key=api_key)
                modelo = genai.GenerativeModel('gemini-2.5-flash')
                
                with st.spinner('Modelando copywriter, adaptando branding y ensamblando PDF...'):
                    # Prompt inteligente con arquitectura de marca blanca
                    prompt = f"""
                    Eres un experto copywriter del sector inmobiliario de lujo. Escribe estrictamente DOS bloques de texto separados por la palabra clave "===SEPARADOR===". No saludes, no agregues explicaciones.
                    
                    Información base:
                    - Título del Inmueble: {titulo_propiedad}
                    - Precio: {precio_inmueble}
                    - Detalles técnicos: {descripcion}
                    
                    Datos de Identidad (Marca Blanca):
                    - Inmobiliaria: {inmobiliaria}
                    - Asesor Ejecutivo: {asesor}
                    - Enlace Directo: https://wa.me/{contacto}
                    
                    BLOQUE 1: Crea un copy de WhatsApp altamente persuasivo. Usa emojis de forma limpia, estructura con viñetas los puntos clave del inmueble y finaliza invitando al cliente a revisar la Ficha Técnica PDF adjunta y a agendar una cita dando clic al enlace directo de WhatsApp.
                    
                    ===SEPARADOR===
                    
                    BLOQUE 2: Genera una descripción corporativa y elegante (redacción ejecutiva en prosa fluida). NO uses emojis, NO uses exclamaciones. Enfócate exclusivamente en las ventajas del espacio, acabados y ubicación, optimizada para leerse en un documento impreso o PDF formal.
                    """
                    
                    respuesta = modelo.generate_content(prompt)
                    textos = respuesta.text.split("===SEPARADOR===")
                    copy_whatsapp = textos[0].strip()
                    texto_pdf = textos[1].strip() if len(textos) > 1 else copy_whatsapp
                    
                    # Ejecución de los motores visuales y documentales
                    collage_final = crear_collage(foto1, foto2, foto3, foto4)
                    pdf_final_bytes = generar_pdf(
                        titulo_propiedad, precio_inmueble, texto_pdf, 
                        inmobiliaria, asesor, contacto, 
                        foto1, foto2, foto3, foto4
                    )
                
                st.success("¡Ficha y Materiales Generados de Forma Exitosa!")
                
                # 📥 BOTÓN DIGITAL DE DESCARGA DE FICHA PDF
                st.download_button(
                    label="📄 Descargar Ficha Técnica PDF Personalizada",
                    data=pdf_final_bytes,
                    file_name=f"Ficha_{titulo_propiedad.replace(' ', '_')}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
                
                st.markdown("#### 📲 Mensaje Personalizado de WhatsApp (Copia y Pega):")
                st.info(copy_whatsapp)
                
                st.markdown("#### 📸 Visual para Estados de WhatsApp y Catálogo:")
                st.image(collage_final, caption=f"Diseño Automatizado - {inmobiliaria}", use_container_width=True)
                
            except Exception as e:
                st.error(f"Error en la línea de ensamblaje del sistema: {e}")
