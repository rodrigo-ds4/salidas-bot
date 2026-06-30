# Interfaz Gradio para Salidas Bot
# Usa el SalidasAgent real (smolagents + Groq) con chat conversacional

import gradio as gr
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

# Importar el agente real
from main import SalidasAgent

# ===================== INICIALIZACIÓN =====================

# El agente se crea una sola vez por sesión de Gradio
_agent_instance = None

def get_agent() -> SalidasAgent:
    """Retorna (o crea) la instancia del agente."""
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = SalidasAgent()
    return _agent_instance


# ===================== LÓGICA DE CHAT =====================

def respond(message: str, history: list) -> tuple:
    """
    Procesa un mensaje del usuario y retorna la respuesta del agente.

    Args:
        message: Mensaje del usuario
        history: Historial de chat de Gradio (lista de dicts con role/content)

    Returns:
        ("", history actualizado)
    """
    if not message.strip():
        return "", history

    try:
        agent = get_agent()
        response = agent.chat(message)
    except Exception as e:
        response = (
            f"❌ Error al inicializar el agente: {str(e)}\n\n"
            "Verificá que GROQ_API_KEY esté configurada en el archivo .env"
        )

    # Agregar al historial en formato correcto para Chatbot
    history.append({
        "role": "user",
        "content": message
    })
    history.append({
        "role": "assistant", 
        "content": response
    })
    return "", history


def clear_conversation():
    """Limpia el historial y reinicia la memoria del agente."""
    global _agent_instance
    if _agent_instance:
        _agent_instance.memory.short_term.clear()
    return []


# ===================== INTERFAZ =====================

DESCRIPTION = """
# 🤖 Salidas Bot — Buenos Aires

Tu guía inteligente para salir en Buenos Aires. Preguntame sobre **bares**, **restaurantes**,
**parques**, **clima**, **horarios** y todo lo que necesitás para planear tu salida.

**Ejemplos:** *"Bares en Palermo"* · *"¿Hay lluvia hoy?"* · *"Mejores restaurantes de asado"* · *"Qué hay en San Telmo?"*
"""

with gr.Blocks(title="🤖 Salidas Bot") as demo:
    gr.Markdown(DESCRIPTION)

    chatbot = gr.Chatbot(
        label="Chat con Salidas Bot",
        height=480,
        show_label=False,
    )

    with gr.Row():
        msg_input = gr.Textbox(
            placeholder="Preguntame algo... (ej: bares baratos en Palermo)",
            label="Tu mensaje",
            scale=5,
            lines=1,
        )
        send_btn = gr.Button("Enviar", scale=1, variant="primary")

    with gr.Row():
        clear_btn = gr.Button("🗑️ Limpiar conversación", size="sm")

    gr.Markdown(
        "---\n"
        "**Powered by:** smolagents · Groq · LLaMA 3.3 · ChromaDB  |  "
        "🏙️ Especializado en Buenos Aires, Argentina"
    )

    # Events
    send_btn.click(respond, inputs=[msg_input, chatbot], outputs=[msg_input, chatbot])
    msg_input.submit(respond, inputs=[msg_input, chatbot], outputs=[msg_input, chatbot])
    clear_btn.click(clear_conversation, outputs=[chatbot])


if __name__ == "__main__":
    demo.launch(show_error=True, theme=gr.themes.Soft(primary_hue="violet"))
