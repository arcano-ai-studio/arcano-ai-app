import streamlit as st
import google.generativeai as genai
from PIL import Image, ImageDraw, ImageFont
from fpdf import FPDF
import io
import json
import os
import urllib.request

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Arcano AI Studio", page_icon="logo.png", layout="wide")

# 2. INYECCIÓN DE ESTILOS CORPORATIVOS
st.markdown("""
<style>
    div.stButton > button:first-child {
        background-color: #000066; 
        color: white;
        border-radius: 8px;
        border: 2px solid #008f39; 
        font-weight: bold;
        transition: all 0.3s ease;
    }
    div.stButton > button:first-child:hover {
        background-color: #008f39; 
        color: white;
        border-color: #000066; 
    }
    h1, h2, h3 {
        color: #000066; 
        font-family: 'Helvetica Neue', sans-serif;
    }
</style>
""", unsafe_allow_html=True)

# 3. ENCABEZADO Y LOGOTIPO OFICIAL
col_logo, col_titulo = st.columns([1.5, 4])
with col_logo:
    try:
        st.image("logo.png", use_container_width=True)
    except:
        st.markdown("<h1 style='text-align: center; font-size: 3.5rem;'>🏢</h1>", unsafe_allow_html=True)

with col_titulo:
    st.markdown("<div style='margin-top: 25px;'></div>", unsafe_allow_html=True)
    st.markdown("<h1 style='margin-bottom: 0px; color: #000066;'>ARCANO AI Studio</h1>", unsafe_allow_html=True)
    st.markdown("<h4 style='color: #ff6600; margin-top: 0px;'>Soluciones Inmobiliarias de Precisión</h4>", unsafe_allow_html=True)

st.markdown("---")

if 'resultados' not in st.session_state:
    st.session_state.resultados = None

st.sidebar.header("⚙️ Configuración del Motor")
api_key = st.sidebar.text_input("API Key de Gemini:", type="password")

col1, col2 = st.columns([1, 1])

with col1:
    st.write("### 🏠 1. ¿Qué vamos a comercializar hoy?")
    col_tipo, col_operacion = st.columns(2)
    with col_tipo:
        tipo_propiedad = st.radio("Tipo de inmueble:", ["Casa Habitación", "Terreno"])
    with col_operacion:
        operacion = st.radio("Modalidad:", ["Venta", "Renta"])
    
    st.write("### 👤 2. Datos del Asesor")
    inmobiliaria = st.text_input("Nombre de la Inmobiliaria:", value="Arconte Bienes Raíces")
    asesor = st.text_input("Tu Nombre Completo:", value="Javier Enciso")
    contacto = st.text_input("Tu WhatsApp para que te contacten (Ej: 7711234567):")
    
    st.write("### 📝 3. Detalles de la Propiedad")
    titulo_propiedad = st.text_input("Título Comercial (Ej: Casa Moderna en Forjadores):")
    precio_inmueble = st.text_input(f"Precio de {operacion} (Ej: $15,000 MXN mensuales):")
    descripcion = st.text_area("Pega aquí todos los detalles (Metros, distribución, amenidades, etc.):", height=120)
    
    st.write("### 📸 4. Carga de Fotografías")
    st.info("💡 En celular: Si abre 'Archivos', toca el menú de las 3 rayitas para ir a tu Galería.")
    
    if tipo_propiedad == "Casa Habitación":
        lbl_foto1 = "🖼️ 1. Foto Principal (Fachada)"
        lbl_foto2 = "🛋️ 2. Foto de Interiores"
        lbl_foto3 = "🛏️ 3. Foto de Privados"
        lbl_foto4 = "✨ 4. Foto de Amenidades"
    else:
        lbl_foto1 = "🗺️ 1. Foto Principal (Vista General)"
        lbl_foto2 = "📍 2. Foto del Terreno (Ángulo diferente)"
        lbl_foto3 = "🛣️ 3. Foto de Entorno / Accesos"
        lbl_foto4 = "✨ 4. Foto de Colindancias / Detalles"

    foto1 = st.file_uploader(lbl_foto1, type=['jpg', 'jpeg', 'png'], key="foto_1")
    foto2 = st.file_uploader(lbl_foto2, type=['jpg', 'jpeg', 'png'], key="foto_2")
    foto3 = st.file_uploader(lbl_foto3, type=['jpg', 'jpeg', 'png'], key="foto_3")
    foto4 = st.file_uploader(lbl_foto4, type=['jpg', 'jpeg', 'png'], key="foto_4")

def crear_collage(img1, img2, img3, img4, tipo, modalidad, titulo, precio):
    lienzo = Image.new('RGB', (1080, 1080), color=(0, 0, 102)) 
    def preparar(f): return Image.open(f).resize((540, 540))
    lienzo.paste(preparar(img1), (0, 0))
    lienzo.paste(preparar(img2), (540, 0))
    lienzo.paste(preparar(img3), (0, 540))
    lienzo.paste(preparar(img4), (540, 540))
    
    capa_dibujo = Image.new('RGBA', (1080, 1080), (255, 255, 255, 0))
    dibujo = ImageDraw.Draw(capa_dibujo)
    
    dibujo.rectangle([0, 380, 1080, 700], fill=(0, 0, 102, 230)) 
    dibujo.rectangle([0, 980, 1080, 1080], fill=(255, 102, 0, 255)) 
    
    font_path = "Roboto-Bold.ttf"
    if not os.path.exists(font_path):
        try: urllib.request.urlretrieve("https://github.com/googlefonts/roboto/raw/main/src/hinted/Roboto-Bold.ttf", font_path)
        except: pass

    try:
        fuente_gigante = ImageFont.truetype(font_path, 80)
        fuente_mediana = ImageFont.truetype(font_path, 45)
    except:
        fuente_gigante = ImageFont.load_default()
        fuente_mediana = ImageFont.load_default()
        
    texto_oferta = f"¡{tipo.upper()} EN {modalidad.upper()}!"
    dibujo.text((540, 450), texto_oferta, fill=(0, 143, 57, 255), font=fuente_gigante, anchor="mm") 
    titulo_corto = str(titulo) if len(str(titulo)) < 38 else str(titulo)[:35] + "..."
    dibujo.text((540, 540), titulo_corto.upper(), fill=(255, 255, 255, 255), font=fuente_mediana, anchor="mm")
    dibujo.text((540, 620), str(precio), fill=(255, 255, 255, 255), font=fuente_gigante, anchor="mm")
    
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

def generar_pdf_estructurado(titulo, precio, datos, name_inmo, name_asesor, num_cont, f1, f2, f3, f4, modalidad, tipo_inmueble):
    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=False)
    
    # PAGINA 1
    pdf.add_page()
    partes = str(name_inmo).split(" ", 1)
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
    
    pdf.set_xy(100, 10)
    pdf.set_font("Helvetica", 'B', 10)
    pdf.set_text_color(120, 120, 120)
    pdf.cell(95, 5, "FICHA TÉCNICA EJECUTIVA", ln=1, align='R')
    pdf.set_xy(100, 15)
    pdf.set_font("Helvetica", 'B', 9)
    pdf.set_text_color(46, 125, 50)
    pdf.cell(95, 5, "DISPONIBLE", ln=1, align='R')
    pdf.set_fill_color(46, 125, 50)
    pdf.ellipse(172, 16.5, 2.5, 2.5, 'F') 
    
    pdf.set_draw_color(26, 43, 76)
    pdf.set_line_width(0.8)
    pdf.line(15, 24, 195, 24)
    
    pdf.set_xy(145, 28)
    pdf.set_font("Helvetica", 'B', 18)
    pdf.set_text_color(26, 43, 76)
    pdf.cell(50, 8, str(precio), ln=0, align='R') 
    
    pdf.set_xy(15, 28)
    pdf.set_text_color(50, 50, 50)
    pdf.set_font("Helvetica", 'B', 14)
    pdf.multi_cell(125, 6, str(titulo).upper(), align='L') 
    
    y_ubicacion = pdf.get_y() + 2
    if y_ubicacion < 38: y_ubicacion = 38 
    pdf.set_xy(15, y_ubicacion)
    pdf.set_font("Helvetica", '', 10)
    pdf.set_text_color(100, 100, 100)
    ubi_str = str(datos.get('ubicacion', ''))
    pdf.cell(180, 5, ubi_str.encode('latin-1', 'ignore').decode('latin-1'), ln=1)
    
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
        val_str = str(valor)
        val_clean = val_str.encode('latin-1', 'ignore').decode('latin-1')[:85]
        pdf.cell(125, 7, val_clean, fill=True, border='B', ln=1)
        y += 7

    fila_tabla("Ubicación", datos.get('ubicacion', 'No especificado'), False)
    fila_tabla("Superficie de Terreno", datos.get('terreno', 'No especificado'), True)
    fila_tabla("Superficie de Construcción", datos.get('construccion', 'No aplica'), False)
    fila_tabla("Niveles", datos.get('niveles', 'No aplica'), True)
    
    texto_legal = "Propiedad lista para estructuración jurídica." if modalidad == "Venta" else "Disponible mediante contrato de arrendamiento."
    fila_tabla("Esquema / Disponibilidad", texto_legal, False)
    
    y = titulo_seccion("Descripción General", y + 8)
    pdf.set_xy(15, y)
    pdf.set_font("Helvetica", '', 10)
    pdf.set_text_color(45, 55, 72)
    desc_str = str(datos.get('descripcion_pdf', ''))
    desc_clean = desc_str.encode('latin-1', 'ignore').decode('latin-1')
    pdf.multi_cell(180, 5.5, desc_clean)
    
    titulo_dist = "Distribución / Amenidades" if tipo_inmueble == "Casa Habitación" else "Características del Terreno"
    y = titulo_seccion(titulo_dist, pdf.get_y() + 8)
    pdf.set_xy(15, y)
    pdf.set_font("Helvetica", 'B', 10)
    pdf.set_text_color(26, 43, 76)
    
    col_1_title = "Zonas Principales" if tipo_inmueble == "Casa Habitación" else "Ventajas Principales"
    pdf.cell(85, 6, col_1_title, ln=1)
    
    pdf.set_font("Helvetica", '', 9)
    pdf.set_text_color(70, 85, 104)
    y_col1 = pdf.get_y()
    for item in datos.get('planta_baja', []):
        pdf.set_x(15)
        item_str = str(item)
        pdf.multi_cell(85, 4.5, f"- {item_str.encode('latin-1', 'ignore').decode('latin-1')}")
    
    pdf.set_xy(110, y)
    pdf.set_font("Helvetica", 'B', 10)
    pdf.set_text_color(26, 43, 76)
    col_2_title = "Extras / Privados" if tipo_inmueble == "Casa Habitación" else "Entorno / Colindancias"
    pdf.cell(85, 6, col_2_title, ln=1)
    
    pdf.set_font("Helvetica", '', 9)
    pdf.set_text_color(70, 85, 104)
    pdf.set_y(y_col1)
    for item in datos.get('planta_alta', []):
        pdf.set_x(110)
        item_str = str(item)
        pdf.multi_cell(85, 4.5, f"- {item_str.encode('latin-1', 'ignore').decode('latin-1')}")
    
    pdf.set_y(268)
    pdf.set_font("Helvetica", 'I', 7.5)
    pdf.set_text_color(130, 130, 130)
    aviso_legal = "* Aviso Legal: La información técnica contenida en este documento es de carácter informativo. Solicite a su asesor la revisión completa de la documentación jurídica pertinente antes de formalizar el cierre u operación."
    pdf.multi_cell(180, 3.5, aviso_legal.encode('latin-1', 'ignore').decode('latin-1'), align='C')
    
    pdf.set_xy(15, 280)
    pdf.set_font("Helvetica", 'I', 8)
    pdf.set_text_color(150, 150, 150)
    pdf.cell(90, 10, f"{name_inmo} | Página 1 de 2", align='L')
    pdf.set_font("Helvetica", 'B', 9) 
    pdf.set_text_color(110, 120, 140) 
    pdf.cell(90, 10, "By Arcano AI Studio", align='R')

    # PAGINA 2
    pdf.add_page()
    y = titulo_seccion("Galería Registrada en Catálogo", 20)
    pdf.set_xy(15, y)
    pdf.set_font("Helvetica", '', 9)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(180, 5, "Este expediente vincula automáticamente las fotografías validadas dentro del catálogo maestro.", ln=1)
    
    lbl_img1 = "Vista Principal" if tipo_inmueble == "Casa Habitación" else "Vista General"
    lbl_img2 = "Interiores" if tipo_inmueble == "Casa Habitación" else "Topografía / Ángulo"
    lbl_img3 = "Área Privada" if tipo_inmueble == "Casa Habitación" else "Accesos / Entorno"
    lbl_img4 = "Detalles Adicionales" if tipo_inmueble == "Casa Habitación" else "Colindancias"

    y_img = 40
    try:
        if f1: pdf.image(procesar_imagen(f1), x=20, y=y_img, w=80, h=60)
        if f2: pdf.image(procesar_imagen(f2), x=110, y=y_img, w=80, h=60)
        pdf.set_font("Helvetica", 'B', 9)
        pdf.set_text_color(26, 43, 76)
        pdf.set_xy(20, y_img + 62)
        pdf.cell(80, 5, lbl_img1, align='C')
        pdf.set_xy(110, y_img + 62)
        pdf.cell(80, 5, lbl_img2, align='C')
        
        y_img = 115
        if f3: pdf.image(procesar_imagen(f3), x=20, y=y_img, w=80, h=60)
        if f4: pdf.image(procesar_imagen(f4), x=110, y=y_img, w=80, h=60)
        pdf.set_xy(20, y_img + 62)
        pdf.cell(80, 5, lbl_img3, align='C')
        pdf.set_xy(110, y_img + 62)
        pdf.cell(80, 5, lbl_img4, align='C')
    except Exception as e:
        pass
        
    # --- CAJA CTA CON TEXTO DEL ASESOR EN NARANJA ---
    pdf.set_fill_color(26, 43, 76)
    pdf.rect(15, 230, 180, 30, 'F')
    
    pdf.set_font("Helvetica", 'B', 12)
    pdf.set_text_color(197, 168, 128) # Dorado
    pdf.set_xy(15, 233)
    pdf.cell(180, 8, "¿LISTO PARA RECIBIR MÁS INFORMACIÓN?", align='C', ln=1)
    
    pdf.set_font("Helvetica", '', 10)
    pdf.set_text_color(255, 255, 255) # Blanco
    pdf.set_xy(15, 242)
    pdf.cell(180, 6, "Póngase en contacto directo con su asesor para agendar una cita:", align='C', ln=1)
    
    pdf.set_font("Helvetica", 'B', 12)
    pdf.set_text_color(255, 102, 0) # Naranja Arcano Vibrante
    pdf.set_xy(15, 249)
    pdf.cell(180, 6, f"{name_asesor} | WhatsApp: {num_cont}", align='C', ln=1)
    # ------------------------------------------------

    pdf.set_xy(15, 280)
    pdf.set_font("Helvetica", 'I', 8)
    pdf.set_text_color(150, 150, 150)
    pdf.cell(90, 10, f"{name_inmo} | Página 2 de 2", align='L')
    pdf.set_font("Helvetica", 'B', 9) 
    pdf.set_text_color(110, 120, 140) 
    pdf.cell(90, 10, "By Arcano AI Studio", align='R')
    
    return bytes(pdf.output())

with col2:
    st.write("### 🪐 Centro de Procesamiento")
    
    if st.button("🚀 Generar Todo el Material", use_container_width=True):
        if not api_key: st.error("⚠️ Ingresa tu API Key maestra en el menú izquierdo.")
        elif not descripcion or not titulo_propiedad: st.warning("⚠️ Faltan datos del inmueble.")
        elif not (foto1 and foto2 and foto3 and foto4): st.warning("⚠️ Sube las 4 fotografías.")
        else:
            try:
                genai.configure(api_key=api_key)
                modelo = genai.GenerativeModel('gemini-2.5-flash')
                
                with st.spinner(f'Analizando {tipo_propiedad} en {operacion} y ensamblando materiales...'):
                    prompt = f"""
                    Analiza esta descripción de {tipo_propiedad} para {operacion} y extrae los datos. Devuelve ÚNICAMENTE JSON válido:
                    {{
                        "whatsapp": "Mensaje altamente persuasivo con emojis diseñado para promover esta {tipo_propiedad} en {operacion}",
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
                    
                    collage_final = crear_collage(foto1, foto2, foto3, foto4, tipo_propiedad, operacion, titulo_propiedad, precio_inmueble)
                    pdf_final_bytes = generar_pdf_estructurado(
                        titulo_propiedad, precio_inmueble, datos_json, 
                        inmobiliaria, asesor, contacto, 
                        foto1, foto2, foto3, foto4, operacion, tipo_propiedad
                    )
                    
                    img_byte_arr = io.BytesIO()
                    collage_final.save(img_byte_arr, format='JPEG')
                    img_bytes = img_byte_arr.getvalue()
                    
                    st.session_state.resultados = {
                        "pdf": pdf_final_bytes,
                        "whatsapp": str(datos_json.get("whatsapp", "")),
                        "collage_img": collage_final,
                        "collage_bytes": img_bytes,
                        "titulo": str(titulo_propiedad)
                    }
            except Exception as e:
                st.error(f"Error en el motor: {e}")

    if st.session_state.resultados:
        res = st.session_state.resultados
        
        st.success("¡Materiales Generados con Éxito!")
        
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            st.download_button(
                label="📄 DESCARGAR PDF",
                data=res["pdf"],
                file_name=f"Ficha_{res['titulo'].replace(' ', '_')}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        with col_btn2:
            st.download_button(
                label="📸 DESCARGAR ARTE",
                data=res["collage_bytes"],
                file_name=f"Estado_{res['titulo'].replace(' ', '_')}.jpg",
                mime="image/jpeg",
                use_container_width=True
            )
            
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔄 Crear Nueva Ficha Inmobiliaria", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
        
        st.markdown("#### 💬 Copy WhatsApp Listo:")
        st.info(res["whatsapp"])
        
        st.markdown("#### 📱 Vista Previa del Arte:")
        st.image(res["collage_img"], use_container_width=True)
