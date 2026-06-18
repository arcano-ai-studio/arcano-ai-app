import streamlit as st
import google.generativeai as genai
from PIL import Image, ImageDraw
from fpdf import FPDF
import io
import json

# Configuración de la pantalla
st.set_page_config(page_title="Arcano AI Studio", page_icon="🏢", layout="wide")

st.title("🏢 Arcano AI Studio")
st.subheader("Central de Inteligencia Inmobiliaria - Versión Pro (Marca Blanca)")
st.markdown("Genera kits de venta personalizados al instante: Mensaje de WhatsApp, Collage y Ficha PDF Estructurada.")
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
    
    st.write("### 📸 3. Expediente Fotográfico")
    foto1 = st.file_uploader("Foto 1: Fachada Principal", type=['jpg', 'jpeg', 'png'])
    foto2 = st.file_uploader("Foto 2: Estancia / Interiores", type=['jpg', 'jpeg', 'png'])
    foto3 = st.file_uploader("Foto 3: Recámaras / Privado", type=['jpg', 'jpeg', 'png'])
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

def procesar_imagen(file_obj):
    if not file_obj: return None
    img = Image.open(file_obj)
    if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
        bg = Image.new("RGB", img.size, (255, 255, 255))
        bg.paste(img, mask=img.convert('RGBA').split()[-1])
        img = bg
    temp = io.BytesIO()
    img.save(temp, format="JPEG")
    temp.seek(0)
    return temp

# NUEVO MOTOR PDF DE ARQUITECTURA ESTRUCTURADA
def generar_pdf_estructurado(titulo, precio, datos, name_inmo, name_asesor, num_cont, f1, f2, f3, f4):
    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=False)
    
    # ---------------- PÁGINA 1 ----------------
    pdf.add_page()
    
    # Encabezado Comercial
    pdf.set_font("Helvetica", 'B', 22)
    pdf.set_text_color(26, 43, 76)
    pdf.cell(100, 8, name_inmo.upper()[:25], ln=0)
    
    pdf.set_font("Helvetica", 'B', 10)
    pdf.set_text_color(120, 120, 120)
    pdf.cell(90, 8, "FICHA TÉCNICA EJECUTIVA", ln=1, align='R')
    
    # Línea Divisoria
    pdf.set_draw_color(26, 43, 76)
    pdf.set_line_width(0.8)
    pdf.line(15, 22, 195, 22)
    
    # Título y Precio
    pdf.set_xy(15, 28)
    pdf.set_font("Helvetica", 'B', 15)
    pdf.set_text_color(50, 50, 50)
    pdf.cell(120, 8, titulo.upper()[:45], ln=0)
    
    pdf.set_font("Helvetica", 'B', 16)
    pdf.set_text_color(26, 43, 76)
    pdf.cell(60, 8, precio, ln=1, align='R')
    
    pdf.set_xy(15, 36)
    pdf.set_font("Helvetica", '', 10)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(180, 5, datos.get('ubicacion', '').encode('latin-1', 'ignore').decode('latin-1'), ln=1)
    
    # Función de ayuda para Títulos de Sección
    def titulo_seccion(texto, y_pos):
        pdf.set_xy(15, y_pos)
        pdf.set_fill_color(197, 168, 128) 
        pdf.rect(15, y_pos, 2, 6, 'F')
        pdf.set_xy(19, y_pos)
        pdf.set_font("Helvetica", 'B', 12)
        pdf.set_text_color(26, 43, 76)
        pdf.cell(150, 6, texto.upper(), ln=1)
        return y_pos + 8
        
    # SECCIÓN: DATOS TÉCNICOS (Tabla)
    y = titulo_seccion("Datos Técnicos del Inmueble", 48)
    
    pdf.set_fill_color(26, 43, 76)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", 'B', 9)
    pdf.set_xy(15, y)
    pdf.cell(180, 6, "ESPECIFICACIÓN GENERAL", fill=True, ln=1)
    y += 6
    
    def fila_tabla(etiqueta, valor, gris):
        nonlocal y
        if gris: pdf.set_fill_color(248, 250, 252)
        else: pdf.set_fill_color(255, 255, 255)
        pdf.set_xy(15, y)
        pdf.set_font("Helvetica", 'B', 9)
        pdf.set_text_color(70, 85, 104)
        pdf.cell(55, 7, etiqueta, fill=True, border='B')
        
        pdf.set_font("Helvetica", '', 9)
        pdf.set_text_color(45, 55, 72)
        val_clean = valor.encode('latin-1', 'ignore').decode('latin-1')[:85]
        pdf.cell(125, 7, val_clean, fill=True, border='B', ln=1)
        y += 7

    fila_tabla("Ubicación", datos.get('ubicacion', 'No especificado'), False)
    fila_tabla("Superficie de Terreno", datos.get('terreno', 'No especificado'), True)
    fila_tabla("Superficie de Construcción", datos.get('construccion', 'No especificado'), False)
    fila_tabla("Niveles Construidos", datos.get('niveles', 'No especificado'), True)
    fila_tabla("Esquema Legal", "Propiedad privada, libre de gravamen.", False)
    fila_tabla("Modalidad de Venta", "Trato Directo / Operación Ejecutiva", True)
    
    # SECCIÓN: DESCRIPCIÓN
    y = titulo_seccion("Descripción General", y + 8)
    pdf.set_xy(15, y)
    pdf.set_font("Helvetica", '', 10)
    pdf.set_text_color(45, 55, 72)
    desc_clean = datos.get('descripcion_pdf', '').encode('latin-1', 'ignore').decode('latin-1')
    pdf.multi_cell(180, 5, desc_clean)
    
    # SECCIÓN: DISTRIBUCIÓN DE ESPACIOS (Dos Columnas)
    y = titulo_seccion("Distribución de Espacios", pdf.get_y() + 8)
    
    # Columna Planta Baja
    pdf.set_xy(15, y)
    pdf.set_font("Helvetica", 'B', 10)
    pdf.set_text_color(26, 43, 76)
    pdf.cell(85, 6, "Planta Baja", ln=1)
    pdf.set_font("Helvetica", '', 9)
    pdf.set_text_color(70, 85, 104)
    y_col1 = pdf.get_y()
    for item in datos.get('planta_baja', []):
        pdf.set_x(15)
        pdf.multi_cell(85, 4.5, f"• {item.encode('latin-1', 'ignore').decode('latin-1')}")
    y_final_col1 = pdf.get_y()
    
    # Columna Planta Alta
    pdf.set_xy(110, y)
    pdf.set_font("Helvetica", 'B', 10)
    pdf.set_text_color(26, 43, 76)
    pdf.cell(85, 6, "Planta Alta & Amenidades", ln=1)
    pdf.set_font("Helvetica", '', 9)
    pdf.set_text_color(70, 85, 104)
    pdf.set_y(y_col1)
    for item in datos.get('planta_alta', []):
        pdf.set_x(110)
        pdf.multi_cell(85, 4.5, f"• {item.encode('latin-1', 'ignore').decode('latin-1')}")
    y_final_col2 = pdf.get_y()
    
    # Pie de página 1
    pdf.set_xy(15, 280)
    pdf.set_font("Helvetica", 'I', 8)
    pdf.set_text_color(150, 150, 150)
    pdf.cell(180, 10, f"{name_inmo} | Página 1 de 2", align='C')

    # ---------------- PÁGINA 2 ----------------
    pdf.add_page()
    
    y = titulo_seccion("Galería Registrada en Catálogo", 20)
    pdf.set_xy(15, y)
    pdf.set_font("Helvetica", '', 9)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(180, 5, "Este expediente vincula automáticamente las fotografías validadas dentro del catálogo maestro.", ln=1)
    
    # Cuadrícula 2x2
    y_img = 40
    try:
        # Foto 1 y 2
        if f1: pdf.image(procesar_imagen(f1), x=20, y=y_img, w=80, h=60)
        if f2: pdf.image(procesar_imagen(f2), x=110, y=y_img, w=80, h=60)
        pdf.set_font("Helvetica", 'B', 9)
        pdf.set_text_color(26, 43, 76)
        pdf.set_xy(20, y_img + 62)
        pdf.cell(80, 5, "Fachada Principal / Acceso", align='C')
        pdf.set_xy(110, y_img + 62)
        pdf.cell(80, 5, "Estancia / Interiores", align='C')
        
        # Foto 3 y 4
        y_img = 115
        if f3: pdf.image(procesar_imagen(f3), x=20, y=y_img, w=80, h=60)
        if f4: pdf.image(procesar_imagen(f4), x=110, y=y_img, w=80, h=60)
        pdf.set_xy(20, y_img + 62)
        pdf.cell(80, 5, "Área Privada / Recámaras", align='C')
        pdf.set_xy(110, y_img + 62)
        pdf.cell(80, 5, "Acabados / Amenidades", align='C')
    except Exception as e:
        pass
        
    # Caja Call to Action (Abajo)
    pdf.set_fill_color(26, 43, 76)
    pdf.rect(15, 230, 180, 30, 'F')
    pdf.set_font("Helvetica", 'B', 12)
    pdf.set_text_color(197, 168, 128)
    pdf.set_xy(15, 235)
    pdf.cell(180, 8, "¿LISTO PARA COORDINAR UNA VISITA?", align='C', ln=1)
    pdf.set_font("Helvetica", '', 10)
    pdf.set_text_color(255, 255, 255)
    pdf.set_xy(15, 245)
    pdf.cell(180, 6, f"Póngase en contacto inmediato con el asesor {name_asesor} para agendar su cita.", align='C', ln=1)
    pdf.set_xy(15, 250)
    pdf.cell(180, 6, f"Línea Directa / WhatsApp: {num_cont}", align='C', ln=1)

    # Pie de página 2
    pdf.set_xy(15, 280)
    pdf.set_font("Helvetica", 'I', 8)
    pdf.set_text_color(150, 150, 150)
    pdf.cell(180, 10, f"{name_inmo} | Página 2 de 2", align='C')
    
    return bytes(pdf.output())

with col2:
    st.write("### 🪐 Materiales Listos para Descarga")
    
    if st.button("🚀 Procesar Estructura Inteligente", use_container_width=True):
        if not api_key: st.error("⚠️ Ingresa tu API Key maestra.")
        elif not descripcion or not titulo_propiedad: st.warning("⚠️ Faltan datos del inmueble.")
        elif not (foto1 and foto2 and foto3 and foto4): st.warning("⚠️ Faltan fotografías.")
        else:
            try:
                genai.configure(api_key=api_key)
                modelo = genai.GenerativeModel('gemini-2.5-flash')
                
                with st.spinner('Extrayendo datos arquitectónicos y dibujando cuadrículas PDF...'):
                    # Prompt especializado para JSON
                    prompt = f"""
                    Analiza esta descripción y extrae los datos solicitados. Devuelve ÚNICAMENTE un formato JSON válido, sin texto extra, con esta estructura exacta:
                    {{
                        "whatsapp": "Mensaje persuasivo con emojis para vender",
                        "ubicacion": "Ubicación corta",
                        "terreno": "Superficie de terreno",
                        "construccion": "Superficie de construcción",
                        "niveles": "Número de niveles",
                        "descripcion_pdf": "Párrafo corporativo y formal sobre ventajas y plusvalía (máximo 80 palabras)",
                        "planta_baja": ["Elemento 1", "Elemento 2", "Elemento 3"],
                        "planta_alta": ["Elemento 1", "Elemento 2", "Elemento 3"]
                    }}
                    
                    Propiedad: {titulo_propiedad} a {precio_inmueble}
                    Descripción: {descripcion}
                    """
                    
                    respuesta = modelo.generate_content(prompt)
                    
                    # Corrección segura a prueba de GitHub
                    marca_codigo = "`" * 3
                    res_texto = respuesta.text.replace(marca_codigo + "json", "").replace(marca_codigo, "").strip()
                    
                    try:
                        datos_json = json.loads(res_texto)
                    except:
                        st.error("Error de la IA al formatear datos. Intenta de nuevo.")
                        st.stop()
                    
                    collage_final = crear_collage(foto1, foto2, foto3, foto4)
                    pdf_final_bytes = generar_pdf_estructurado(
                        titulo_propiedad, precio_inmueble, datos_json, 
                        inmobiliaria, asesor, contacto, 
                        foto1, foto2, foto3, foto4
                    )
                
                st.success("¡Ficha Estructurada Generada con Éxito!")
                
                st.download_button(
                    label="📄 Descargar Ficha Técnica PDF (Diseño Arconte)",
                    data=pdf_final_bytes,
                    file_name=f"Ficha_Arconte_{titulo_propiedad.replace(' ', '_')}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
                
                st.markdown("#### 📲 Mensaje Personalizado de WhatsApp:")
                st.info(datos_json.get("whatsapp", ""))
                
                st.markdown("#### 📸 Visual para Estados:")
                st.image(collage_final, use_container_width=True)
                
            except Exception as e:
                st.error(f"Error en el motor gráfico: {e}")
