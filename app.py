
import streamlit as st
from google import genai

# =========================================================
# 1. CONFIGURACIÓN DE LA PÁGINA
# =========================================================

st.set_page_config(
    page_title="Asistente AI - Sistemas Inteligentes",
    page_icon="🤖",
    layout="centered"
)

st.title("🤖 Asistente Virtual Astra")
st.caption(
    "UAdeO • Materia: Sistemas Inteligentes • "
    "Dra. Aiblis Susej Herrera Palafox"
)

# =========================================================
# 2. CONFIGURACIÓN DE LA API KEY
# =========================================================

try:
    api_key = st.secrets["GEMINI_API_KEY"]
except (KeyError, FileNotFoundError):
    st.error(
        "No se encontró GEMINI_API_KEY. "
        "Configúrala en .streamlit/secrets.toml."
    )
    st.stop()

# =========================================================
# 3. CONFIGURACIÓN DEL MODELO
# =========================================================

MODEL_NAME = "gemini-3.8-flash"

SYSTEM_INSTRUCTION = """
Eres Astra, un asistente académico inteligente, formal y
estructurado para la materia Sistemas Inteligentes de la UAdeO.

Explica conceptos de Inteligencia Artificial, agentes
inteligentes y redes neuronales de manera clara y accesible.

Utiliza ejemplos cuando ayuden a comprender los conceptos.
Organiza las respuestas con títulos y listas cuando sea útil.

Si preguntan por fechas de entrega o actividades, indica
amablemente que deben verificar las instrucciones de la
Dra. Aiblis Susej Herrera Palafox.
"""

# =========================================================
# 4. INICIALIZAR CLIENTE E HISTORIAL
# =========================================================

if (
    "client" not in st.session_state
    or st.session_state.get("current_api_key") != api_key
):
    st.session_state.client = genai.Client(api_key=api_key)
    st.session_state.current_api_key = api_key
    st.session_state.messages = []
    st.session_state.previous_interaction_id = None

if "messages" not in st.session_state:
    st.session_state.messages = []

if "previous_interaction_id" not in st.session_state:
    st.session_state.previous_interaction_id = None

# =========================================================
# 5. BARRA LATERAL
# =========================================================

with st.sidebar:
    st.header("⚙️ Opciones del agente")
    st.markdown(f"**Modelo:** `{MODEL_NAME}`")

    if st.button(
        "🧹 Limpiar conversación",
        use_container_width=True
    ):
        st.session_state.messages = []
        st.session_state.previous_interaction_id = None
        st.rerun()

# =========================================================
# 6. MOSTRAR HISTORIAL
# =========================================================

if not st.session_state.messages:
    with st.chat_message("assistant"):
        st.markdown(
            "👋 ¡Hola! Soy Astra. ¿En qué tema de "
            "Sistemas Inteligentes te puedo ayudar hoy?"
        )

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# =========================================================
# 7. PROCESAR MENSAJES
# =========================================================

user_input = st.chat_input("Escribe tu pregunta aquí...")

if user_input:
    st.session_state.messages.append(
        {"role": "user", "content": user_input}
    )

    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Astra está pensando..."):
            try:
                request_args = {
                    "model": MODEL_NAME,
                    "input": user_input,
                    "system_instruction": SYSTEM_INSTRUCTION,
                }

                # Mantener el contexto de la conversación
                if st.session_state.previous_interaction_id:
                    request_args["previous_interaction_id"] = (
                        st.session_state.previous_interaction_id
                    )

                response = (
                    st.session_state.client.interactions.create(
                        **request_args
                    )
                )

                answer = response.output_text

                if not answer:
                    answer = (
                        "No se recibió texto en la respuesta. "
                        "Intenta nuevamente."
                    )

                st.markdown(answer)

                st.session_state.messages.append(
                    {"role": "assistant", "content": answer}
                )

                # Guardar el identificador para el siguiente turno
                st.session_state.previous_interaction_id = (
                    getattr(response, "id", None)
                )

            except Exception as e:
                # Quitar el mensaje fallido del historial
                if (
                    st.session_state.messages
                    and st.session_state.messages[-1]["role"] == "user"
                ):
                    st.session_state.messages.pop()

                st.error(f"Error al consultar la API: {e}")
