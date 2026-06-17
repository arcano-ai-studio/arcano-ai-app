import streamlit as st
import google.generativeai as genai

# Configuración de la página
st.set_page_config(page_title="Arcano AI Studio", page_icon="🏢", layout="centered")

# Encabezado
st.title("🏢 Arcano AI Studio")
st.subheader("Generador Ejecutivo Inmobiliario")
st.markdown("Transforma descripciones básicas en materiales de alto impacto en segundos.")
st.markdown("---")

# Menú lateral para la llave (Seguridad)
st.sidebar.header("⚙️ Configuración del Motor")
st.sidebar.markdown("Para que la IA funcione, pega aquí tu llave maestra.")
api_key = st.sidebar.text_input("API Key de Gemini:", type="password")

# Área principal de trabajo
st.write("### 1. Ingresa los datos de la propiedad")
descripcion = st.text_area("Pega aquí el texto desordenado del asesor (metros, precio, ubicación, etc.):", height=150)

# Botón de acción
if st.button("🚀 Generar Ficha Ejecutiva"):
    if not api_key:
        st.error("⚠️ Por favor, ingresa tu API Key en el menú lateral izquierdo primero.")
    elif not descripcion:
        st.warning("⚠️ No olvides pegar la descripción de la propiedad antes de generar.")
    else:
        try:
            # Conexión con el motor de Google
            genai.configure(api_key=api_key)
            modelo = genai.GenerativeModel('gemini-2.5-flash')
            
            # Instrucciones a la IA
            prompt = f"""
            Eres un experto copywriter inmobiliario de alto nivel. Transforma este texto desordenado en un mensaje de WhatsApp de impacto.
            Usa emojis estratégicamente.
            Destaca el precio, la ubicación y las métricas principales (terreno y construcción).
            Estructura el texto con títulos claros (Distribución, Planta Baja, Planta Alta, etc.).
            Añade un llamado a la acción claro al final.
            Texto original: {descripcion}
            """
            
            # Procesamiento con animación de carga
            with st.spinner('Analizando datos y redactando estructura ejecutiva...'):
                respuesta = modelo.generate_content(prompt)
                
            # Resultados
            st.success("¡Copy generado con éxito!")
            st.markdown("### 📲 Copy Optimizado para WhatsApp:")
            
            # Caja con el texto final listo para copiar
            st.info(respuesta.text)
            
        except Exception as e:
            st.error(f"Hubo un error de conexión con el motor: {e}")
