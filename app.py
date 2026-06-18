import streamlit as st
import google.generativeai as genai
from PIL import Image, ImageDraw, ImageFont
from fpdf import FPDF
import io
import json

# Configuración de la pantalla
st.set_page_config(page_title="Arcano AI Studio", page_icon="🏢", layout="wide")

st.title("🏢 Arcano AI Studio")
st.subheader("Central de Inteligencia Inmobiliaria - Versión Pro (Marca Blanca)")
st.markdown("Genera kits de venta personalizados: Mensaje de WhatsApp, Collage con Textos y Ficha PDF.")
st.markdown("---")

# Inicializar la "Memoria"
if 'resultados' not in st.session_state:
    st.session_state.resultados = None

st.sidebar.header("⚙️ Configuración del Motor")
api_key = st.sidebar.text_input("API Key de Gemini:", type="password")

col1, col2 = st.columns([1, 1])

with col1:
    st.write("### 🏠 1. Tipo de Inmueble")
    tipo_propiedad = st.radio("Selecciona lo que vamos a comercializar:", ["Casa Habitación", "Terreno"], horizontal=True)
    
    st.write("### 👤 2. Marca Blanca")
    inmobiliaria = st.text_input("Nombre de la Inmobiliaria:", value="Arconte Bienes Raíces")
    asesor = st.text_input("Nombre del Asesor:", value="Javier Enciso")
    contacto = st.text_input("WhatsApp de Contacto (Ej: 7711234567):")
    
    st.write("### 📝 3. Datos del Inmueble")
    titulo_propiedad = st.text_input("Título Comercial (Ej: Casa Moderna en Forjadores):")
    precio_inmueble = st.text_input("Precio de Operación (Ej: $2,700,000 MXN):")
    descripcion = st.text_area("Descripción cruda (Metros, distribución, esquema legal, etc.):", height=120)
    
    st.write("### 📸 4. Expediente Fotográfico")
    foto1 = st.file_uploader("Foto 1: Fachada Principal", type=['jpg', 'jpeg', 'png'])
    foto2 = st.file_uploader("Foto 2: Estancia / Interiores", type=['jpg', 'jpeg', 'png'])
    foto3 = st.file_uploader("Foto 3: Recámaras / Privado", type=['jpg', 'jpeg', 'png'])
    foto4 = st.file_uploader("Foto 4: Amenidades / Detalles", type=['jpg', 'jpeg', 'png'])

def crear_collage(img1, img2, img3, img4, tipo):
    lienzo = Image.new('RGB', (1080, 1080), color=(26, 43, 76)) 
    def preparar(f): return Image.open(f).resize((540, 540))
    lienzo.paste(preparar(img1), (0, 0))
    lienzo.paste(preparar(img2), (540, 0))
    lienzo.paste(preparar(img3), (0, 540))
    lienzo.paste(preparar(img4), (540, 540))
    
    capa_dibujo = Image.new('RGBA', (1080, 1080), (255, 255, 255, 0))
    dibujo = ImageDraw.Draw(capa_dibujo)
    
    dibujo.rectangle([0, 460, 1080, 620], fill=(26, 43, 76, 220)) 
    dibujo.rectangle([0, 980, 1080, 1080], fill=(197, 168, 128, 255)) 
    
    try:
        fuente_grande = ImageFont.truetype("DejaVuSans-Bold.ttf", 65)
    except:
        fuente_grande = ImageFont.load_default()
        
    texto_oferta = f"¡{tipo.upper()} EN VENTA!"
    dibujo.text((540, 540), texto_oferta, fill=(255, 255, 255, 255), font=fuente_grande, anchor="mm")
    
    lienzo = Image.alpha_composite(lienzo.convert('RGBA'), capa_dibujo)
    return lienzo.convert('RGB')

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

# MOTOR PDF BLINDADO
def generar_pdf_estructurado(titulo, precio, datos, name_inmo, name_asesor, num_cont, f1, f2, f3, f4):
    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=False)
    
    # ---------------- PÁGINA 1 ----------------
    pdf.add_page()
    
    partes = name_inmo.split(" ", 1)
    palabra1 = partes[0]
    palabra2 = partes[1] if len(partes)>1 else ""
    
    pdf.set_xy(15, 8)
    pdf.set_font("Helvetica", 'B', 24)
    pdf.set_text_color(26, 43, 76)
    pdf.cell(90, 8, palabra1.upper(), ln=1)
    
    if palabra2:
        pdf.set_xy(15, 16)
        pdf.set_font("Helvetica", 'B', 9)
        pdf.set_text_color(197, 168, 128)
        pdf.cell(90, 4, palabra2.upper(), ln=1)
    
    # Encabezado Derecho
    pdf.set_xy(100, 10)
    pdf.set_font("Helvetica", 'B', 10)
    pdf.set_text_color(120, 120, 120)
    pdf.cell(95, 5, "FICHA TÉCNICA EJECUTIVA", ln=1, align='R')
    
    # Status DISPONIBLE con Círculo Vectorial (Corrección del error)
    pdf.set_xy(100, 15)
    pdf.set_font("Helvetica", 'B', 9)
    pdf.set_text_color(46, 125, 50)
    pdf.cell(95, 5, "DISPONIBLE", ln=1, align='R')
    # Dibujo del punto verde a la medida (X, Y, Ancho, Alto)
    pdf.set_fill_color(46, 125, 50)
    pdf.ellipse(172, 16.5, 2.5, 2.5, 'F') 
    
    # Línea Divisoria Superior
    pdf.set_draw_color(26, 43, 76)
    pdf.set_line_width(0.8)
    pdf.line(15, 24, 195, 24)
    
    # Título Dinámico y Precio
    pdf.set_xy(15, 28)
    pdf.set_font("Helvetica", 'B', 18)
    pdf.set_text_color(26, 43, 76)
    pdf.cell(180, 8, precio, ln=0, align='R') 
    
    pdf.set_xy(15, 28)
    pdf.set_text_color(50, 50, 50)
    longitud_titulo = len(titulo)
    if longitud_titulo < 35: pdf.set_font("Helvetica", 'B', 16)
    elif longitud_titulo < 55: pdf.set_font("Helvetica", 'B', 13)
    else: pdf.set_font("Helvetica", 'B', 11)
    pdf.multi_cell(120, 7, titulo.upper()) 
    
    # Ubicación
    pdf.set_xy(15, pdf.get_y() + 2)
    pdf.set_font("Helvetica", '', 10)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(180, 5, datos.get('ubicacion', '').encode('latin-1', 'ignore').decode('latin-1'), ln=1)
    
    def titulo_seccion(texto, y_pos):
        pdf.set_xy(15, y_pos)
        pdf.set_fill_color(197, 168, 128) 
        pdf.rect(15, y_pos, 2, 6, 'F')
        pdf.set_xy(19, y_pos)
        pdf.set_font("Helvetica", 'B', 12)
        pdf.set_text_color(26, 43, 76)
        pdf.cell(150, 6, texto.upper(), ln=1)
        return y_pos + 8
        
    y = titulo_seccion("Datos Técnicos del Inmueble", pdf.get_y() + 8)
    
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
    fila_tabla("Superficie de Construcción", datos.get('construccion', 'No aplica'), False)
    fila_tabla("Niveles", datos.get('niveles', 'No especificado'), True)
    fila_tabla("Esquema Legal", "Propiedad privada, lista para estructurar.", False)
    
    y = titulo_seccion("Descripción General", y + 8)
    pdf.set_xy(15, y)
    pdf.set_font("Helvetica", '', 10)
    pdf.set_text_color(45, 55, 72)
    desc_clean = datos.get('descripcion_pdf', '').encode('latin-1', 'ignore').decode('latin-1')
    pdf.multi_cell(180, 5.5, desc_clean)
    
    y = titulo_seccion("Distribución / Amenidades", pdf.get_y() + 8)
    
    pdf.set_xy(15, y)
    pdf.set_font("Helvetica", 'B', 10)
    pdf.set_text_color(26, 43, 76)
    pdf.cell(85, 6, "Zonas Principales", ln=1)
    pdf.set_font("Helvetica", '', 9)
    pdf.set_text_color(70, 85, 104)
    y_col1 = pdf.get_y()
    for item in datos.get('planta_baja', []):
        pdf.set_x(15)
        # Cambio de viñeta unicode a guión estándar
        pdf.multi_cell(85, 4.5, f"- {item.encode('latin-1', 'ignore').decode('latin-1')}")
    
    pdf.set_xy(110, y)
    pdf.set_font("Helvetica", 'B', 10)
    pdf.set_text_color(26, 43, 76)
    pdf.cell(85, 6, "Extras / Privados", ln=1)
    pdf.set_font("Helvetica", '', 9)
    pdf.set_text_color(70, 85, 104)
    pdf.set_y(y_col1)
    for item in datos.get('planta_alta', []):
        pdf.set_x(110)
        # Cambio de viñeta unicode a guión estándar
        pdf.multi_cell(85, 4.5, f"- {item.encode('latin-1', 'ignore').decode('latin-1')}")
    
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
    
    y_img = 40
    try:
        if f1: pdf.image(procesar_imagen(f1), x=20, y=y_img, w=80, h=60)
        if f2: pdf.image(procesar_imagen(f2), x=110, y=y_img, w=80, h=60)
        pdf.set_font("Helvetica", 'B', 9)
        pdf.set_text_color(26, 43, 76)
        pdf.set_xy(20, y_img + 62)
        pdf.cell(80, 5, "Vista Principal", align='C')
        pdf.set_xy(110, y_img + 62)
        pdf.cell(80, 5, "Interiores / Terreno", align='C')
        
        y_img = 115
        if f3: pdf.image(procesar_imagen(f3), x=20, y=y_img, w=80, h=60)
        if f4: pdf.image(procesar_imagen(f4), x=110, y=y_img, w=80, h=60)
        pdf.set_xy(20, y_img + 62)
        pdf.cell(80, 5, "Área Privada", align='C')
        pdf.set_xy(110, y_img + 62)
        pdf.cell(80, 5, "Detalles Adicionales", align='C')
    except Exception as e:
        pass
        
    pdf.set_fill_color(26, 43, 76)
    pdf.rect(15, 230, 180, 30, 'F')
    pdf.set_font("Helvetica", 'B', 12)
    pdf.set_text_color(197, 168, 128)
    pdf.set_xy(15, 235)
    pdf.cell(180, 8, "¿LISTO PARA RECIBIR MÁS INFORMACIÓN?", align='C', ln=1)
    pdf.set_font("Helvetica", '', 10)
    pdf.set_text_color(255, 255, 255)
    pdf.set_xy(15, 245)
    pdf.cell(180, 6, f"Póngase en contacto inmediato con el asesor {name_asesor} para agendar su cita.", align='C', ln=1)
    pdf.set_xy(15, 250)
    pdf.cell(180, 6, f"Línea Directa / WhatsApp: {num_cont}", align='C', ln=1)

    pdf.set_xy(15, 280)
    pdf.set_font("Helvetica", 'I', 8)
    pdf.set_text_color(150, 150, 150)
    pdf.cell(180, 10, f"{name_inmo} | Página 2 de 2", align='C')
    
    return bytes(pdf.output())

with col2:
    st.write("### 🪐 Centro de Procesamiento")
    
    if st.button("🚀 Generar Todo el Material", use_container_width=True):
        if not api_key: st.error("⚠️ Ingresa tu API Key maestra.")
        elif not descripcion or not titulo_propiedad: st.warning("⚠️ Faltan datos del inmueble.")
        elif not (foto1 and foto2 and foto3 and foto4): st.warning("⚠️ Sube las 4 fotografías.")
        else:
            try:
                genai.configure(api_key=api_key)
                modelo = genai.GenerativeModel('gemini-2.5-flash')
                
                with st.spinner(f'Analizando {tipo_propiedad} y ensamblando materiales...'):
                    prompt = f"""
                    Analiza esta descripción de {tipo_propiedad} y extrae los datos. Devuelve ÚNICAMENTE JSON válido:
                    {{
                        "whatsapp": "Mensaje altamente persuasivo con emojis diseñado para vender este {tipo_propiedad}",
                        "ubicacion": "Ciudad o colonia corta",
                        "terreno": "Superficie de terreno con m2",
                        "construccion": "Superficie de construcción (Pon 'N/A' si es terreno puro)",
                        "niveles": "Número de niveles (Pon 'N/A' si es terreno puro)",
                        "descripcion_pdf": "Párrafo corporativo sobre ventajas (máximo 80 palabras)",
                        "planta_baja": ["Punto clave 1", "Punto clave 2", "Punto clave 3"],
                        "planta_alta": ["Extra 1", "Extra 2", "Extra 3"]
                    }}
                    
                    Inmueble: {titulo_propiedad} a {precio_inmueble}
                    Descripción: {descripcion}
                    """
                    
                    respuesta = modelo.generate_content(prompt)
                    marca_codigo = "`" * 3
                    res_texto = respuesta.text.replace(marca_codigo + "json", "").replace(marca_codigo, "").strip()
                    datos_json = json.loads(res_texto)
                    
                    collage_final = crear_collage(foto1, foto2, foto3, foto4, tipo_propiedad)
                    pdf_final_bytes = generar_pdf_estructurado(
                        titulo_propiedad, precio_inmueble, datos_json, 
                        inmobiliaria, asesor, contacto, 
                        foto1, foto2, foto3, foto4
                    )
                    
                    st.session_state.resultados = {
                        "pdf": pdf_final_bytes,
                        "whatsapp": datos_json.get("whatsapp", ""),
                        "collage": collage_final,
                        "titulo": titulo_propiedad
                    }
            except Exception as e:
                st.error(f"Error en el motor: {e}")

    if st.session_state.resultados:
        res = st.session_state.resultados
        
        st.success("¡Materiales Generados con Éxito!")
        
        st.download_button(
            label="📄 DESCARGAR FICHA TÉCNICA (PDF)",
            data=res["pdf"],
            file_name=f"Ficha_{res['titulo'].replace(' ', '_')}.pdf",
            mime="application/pdf",
            use_container_width=True
        )
        
        st.markdown("#### 💬 Copy WhatsApp Listo:")
        st.info(res["whatsapp"])
        
        st.markdown("#### 📱 Arte para Estados (WhatsApp/Instagram):")
        st.image(res["collage"], use_container_width=True)
