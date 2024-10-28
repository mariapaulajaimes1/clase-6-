import os
import streamlit as st
from bokeh.models.widgets import Button
from bokeh.models import CustomJS
from streamlit_bokeh_events import streamlit_bokeh_events
from PIL import Image
import time
import glob
from gtts import gTTS
from googletrans import Translator

# Configurar la página y título principal
st.set_page_config(page_title="Traductor de Voz", page_icon="🎤")
st.markdown("<h1 style='color: #4CAF50;'>🗣️ Traductor de Voz</h1>", unsafe_allow_html=True)
st.subheader("Escucha y traduce lo que deseas decir en diferentes idiomas.")

# Imagen principal y descripción lateral
image = Image.open('mundo.jfif')
st.image(image, width=300)
with st.sidebar:
    st.markdown("<h2 style='color: #FF5733;'>🎙️ Configuración del Traductor</h2>", unsafe_allow_html=True)
    st.write("Presiona el botón, cuando escuches la señal, habla lo que quieres traducir y selecciona la configuración de idioma que necesitas.")

st.write("Presiona el botón y habla lo que deseas traducir.")

# Botón de escucha con un estilo más visual
stt_button = Button(label=" 🎤 Escuchar", width=300, height=50)
stt_button.js_on_event("button_click", CustomJS(code="""
    var recognition = new webkitSpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;
 
    recognition.onresult = function (e) {
        var value = "";
        for (var i = e.resultIndex; i < e.results.length; ++i) {
            if (e.results[i].isFinal) {
                value += e.results[i][0].transcript;
            }
        }
        if (value != "") {
            document.dispatchEvent(new CustomEvent("GET_TEXT", {detail: value}));
        }
    }
    recognition.start();
    """))

# Capturar el resultado del reconocimiento de voz
result = streamlit_bokeh_events(
    stt_button,
    events="GET_TEXT",
    key="listen",
    refresh_on_update=False,
    override_height=75,
    debounce_time=0
)

# Manejar el texto recibido del botón
if result and "GET_TEXT" in result:
    st.write(f"**Texto capturado:** {result.get('GET_TEXT')}")
    
    # Configurar opciones de idioma y acento
    text = str(result.get("GET_TEXT"))
    st.markdown("<h2 style='color: #2E86C1;'>🔄 Opciones de Traducción</h2>", unsafe_allow_html=True)
    input_language = st.selectbox("Selecciona el idioma de Entrada", ["Inglés", "Español", "Bengali", "Coreano", "Mandarín", "Japonés", "Italiano"])
    output_language = st.selectbox("Selecciona el idioma de Salida", ["Inglés", "Español", "Bengali", "Coreano", "Mandarín", "Japonés", "Italiano"])
    
    # Diccionario para los idiomas
    lang_dict = {
        "Inglés": "en", "Español": "es", "Bengali": "bn", "Coreano": "ko",
        "Mandarín": "zh-cn", "Japonés": "ja", "Italiano": "it"
    }
    
    # Selección de acento
    st.markdown("<h2 style='color: #8E44AD;'>🌎 Acento del Audio</h2>", unsafe_allow_html=True)
    accent = st.selectbox("Selecciona el acento", ["Defecto", "Español", "Reino Unido", "Estados Unidos", "Canadá", "Australia", "Irlanda", "Sudáfrica"])
    
    accent_dict = {
        "Defecto": "com", "Español": "com.mx", "Reino Unido": "co.uk", 
        "Estados Unidos": "com", "Canadá": "ca", "Australia": "com.au", 
        "Irlanda": "ie", "Sudáfrica": "co.za"
    }
    
    # Función de conversión a voz
    def text_to_speech(input_language, output_language, text, tld):
        translator = Translator()
        translation = translator.translate(text, src=input_language, dest=output_language)
        trans_text = translation.text
        tts = gTTS(trans_text, lang=output_language, tld=tld, slow=False)
        
        my_file_name = text[:20] if text else "audio"
        tts.save(f"temp/{my_file_name}.mp3")
        return my_file_name, trans_text
    
    # Opcional: mostrar texto traducido
    display_output_text = st.checkbox("Mostrar el texto traducido")

    if not os.path.exists("temp"):
        os.makedirs("temp")
    
    # Conversión y salida de audio
    if st.button("🔊 Convertir"):
        result, output_text = text_to_speech(lang_dict[input_language], lang_dict[output_language], text, accent_dict[accent])
        audio_file = open(f"temp/{result}.mp3", "rb")
        audio_bytes = audio_file.read()
        
        st.markdown("### 🎧 Audio:")
        st.audio(audio_bytes, format="audio/mp3")
        
        if display_output_text:
            st.markdown("### 📜 Texto traducido:")
            st.write(output_text)
    
    # Función para limpiar archivos antiguos
    def remove_files(n):
        mp3_files = glob.glob("temp/*mp3")
        if mp3_files:
            now = time.time()
            n_days = n * 86400
            for f in mp3_files:
                if os.stat(f).st_mtime < now - n_days:
                    os.remove(f)
                    print("Archivo eliminado:", f)

    remove_files(7)

           


        
    


