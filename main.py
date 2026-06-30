"""
Main entry point del Salidas Bot Agent
Usa smolagents + Groq
"""

import os
from dotenv import load_dotenv
import json
from typing import Optional

# Imports de smolagents
try:
    from smolagents import CodeAgent, ToolCallingAgent, tool, LiteLLMModel
except ImportError:
    print("⚠️  Instala smolagents: pip install smolagents")
    exit(1)

from agent.tools import (
    search_buenos_aires_places,
    get_reviews,
    get_weather_ba,
    get_current_time,
    calculator,
    SALIDAS_TOOLS
)
from agent.memory import MemoryManager

# ===================== SETUP =====================

# Cargar variables de entorno
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    print("❌ GROQ_API_KEY no configurada en .env")
    exit(1)

print("✅ API Key cargada correctamente")


# ===================== AGENT SETUP =====================

# Registrar tools como decoradores
@tool
def search_places(query: str, category: str = "general") -> str:
    """
    Busca lugares, bares, restaurantes, parques en Buenos Aires.
    
    Args:
        query: Qué buscar (ej: bares, restaurantes, Palermo)
        category: Categoría opcional (ej: bar, restaurante)
    """
    from agent.tools import search_buenos_aires_places
    result = search_buenos_aires_places(query, category)
    # Retornar como string legible, no JSON complejo
    import json
    parsed = json.loads(result)
    if parsed.get("places"):
        places_str = "Lugares encontrados:\n"
        for p in parsed["places"][:5]:  # Top 5
            places_str += f"- {p['name']} ({p.get('zone', 'N/A')}) - Rating: {p.get('rating', 'N/A')} - {p.get('vibe', '')}\n"
        return places_str
    return "No se encontraron lugares"

@tool
def get_place_reviews(place_name: str) -> str:
    """
    Obtiene reviews y opiniones de un lugar específico.
    
    Args:
        place_name: Nombre del lugar completo
    """
    from agent.tools import get_reviews
    result = get_reviews(place_name)
    import json
    parsed = json.loads(result)
    if parsed.get("status") == "not_found":
        return f"No encontré información para '{place_name}'"
    
    place = place_name
    avg_rating = parsed.get("average_rating", "N/A")
    reviews_str = f"Reseñas para {place} (Calificación: {avg_rating}/5):\n"
    for r in parsed.get("reviews", [])[:3]:  # Top 3 reviews
        reviews_str += f"- {r['author']}: {r['text']} ⭐{r['rating']}\n"
    return reviews_str

@tool
def get_climate() -> str:
    """Obtiene el clima actual en Buenos Aires."""
    from agent.tools import get_weather_ba
    result = get_weather_ba()
    import json
    parsed = json.loads(result)
    weather = parsed["weather"]
    return f"Clima en Buenos Aires: {weather['condition']}, {weather['temperature']}°C (siente {weather['feels_like']}°C), Humedad: {weather['humidity']}%, Viento: {weather['wind_speed']} km/h"

@tool
def get_forecast() -> str:
    """Obtiene el pronóstico del clima para los próximos 5 días."""
    from agent.tools import get_weather_forecast_ba
    result = get_weather_forecast_ba()
    import json
    parsed = json.loads(result)
    forecast_str = "Pronóstico de 5 días:\n"
    for day in parsed["forecast"][:5]:
        forecast_str += f"- {day['day_name']}: {day['condition']}, {day['temperature']}°C, Lluvia: {day['rain_probability']}%\n"
    return forecast_str

@tool
def get_time() -> str:
    """Retorna la hora actual en Buenos Aires."""
    from agent.tools import get_current_time
    result = get_current_time()
    import json
    parsed = json.loads(result)
    return f"Hora en Buenos Aires: {parsed['time']} ({parsed['day_name']}, {parsed['date']})"

@tool
def calc(operation: str) -> str:
    """
    Realiza cálculos matemáticos simples.
    
    Args:
        operation: Operación matemática (ej: 2 + 2, 10 * 5)
    """
    from agent.tools import calculator
    result = calculator(operation)
    import json
    parsed = json.loads(result)
    if parsed.get("status") == "success":
        return f"{parsed['operation']} = {parsed['result']}"
    return parsed.get("message", "Error en cálculo")

@tool
def get_top_places(place_type: str) -> str:
    """
    Obtiene los lugares más populares (mejor calificados) de un tipo.
    
    Args:
        place_type: Tipo de lugar (ej: bar, restaurante, café)
    """
    from agent.tools import get_popular_places
    result = get_popular_places(place_type)
    import json
    parsed = json.loads(result)
    places_str = f"Mejores {place_type}s en Buenos Aires:\n"
    for p in parsed.get("places", [])[:5]:
        places_str += f"- {p['name']} ({p.get('zone')}) ⭐ {p['rating']} - {p.get('vibe', '')}\n"
    return places_str

@tool
def should_i_bring_umbrella() -> str:
    """Verifica si es necesario llevar paraguas hoy."""
    from agent.tools import check_umbrella_needed
    result = check_umbrella_needed()
    import json
    parsed = json.loads(result)
    need_umbrella = parsed.get("should_bring_umbrella")
    rain_prob = parsed.get("rain_probability")
    return f"Probabilidad de lluvia: {rain_prob}% - {'SÍ, lleva paraguas' if need_umbrella else 'No es necesario paraguas'}"


class SalidasAgent:
    """
    Agent principal para Salidas Bot.
    Usa smolagents con Llama 3.1 vía Groq.
    """
    
    def __init__(self):
        """Inicializa el agent"""
        self.memory = MemoryManager()
        
        # Configurar modelo - Intentar con modelos disponibles en Groq
        models_to_try = [
            "groq/llama-3.3-70b-versatile",      # Más nuevo
            "groq/mixtral-8x7b-32768",            # Alternativa buena
            "groq/llama-3.1-8b-instant",          # Rápido y gratis
            "groq/gemma-7b-it"                    # Alternativa
        ]
        
        self.model = None
        for model_id in models_to_try:
            try:
                self.model = LiteLLMModel(
                    model_id=model_id,
                    api_key=GROQ_API_KEY
                )
                print(f"✅ Modelo configurado: {model_id}")
                break
            except Exception as e:
                print(f"⚠️  {model_id} no disponible: {str(e)[:80]}...")
                continue
        
        if self.model is None:
            raise Exception("❌ No se pudo configurar ningún modelo de Groq. Verifica la API key y modelos disponibles.")
        
        # Crear agent con tools
        tools = [
            search_places,
            get_place_reviews,
            get_climate,
            get_forecast,
            get_time,
            calc,
            get_top_places,
            should_i_bring_umbrella
        ]
        
        self.system_prompt = """Eres Salidas Bot, un asistente experto en salidas y actividades en Buenos Aires, Argentina.

Tu personalidad:
- Sos porteño, amigable y entusiasta
- Usás lenguaje coloquial argentino ("che", "dale", "barbaro", "genial")
- Das recomendaciones concretas y útiles, no genéricas
- Recordás el contexto de la conversación previa

Tus capacidades:
- Buscar bares, restaurantes, parques, museos y todo tipo de lugares en BA
- Ver reviews y calificaciones de lugares
- Consultar el clima actual y pronóstico
- Recomendar según zona, presupuesto o tipo de salida
- Dar info sobre transporte, horarios y costumbres porteñas

Reglas:
- Siempre respondé en español rioplatense
- Si no encontrás algo, sugerí alternativas relacionadas
- Sé conciso pero útil; máximo 5 lugares por búsqueda
- Incluí emojis para hacer las respuestas más visuales
- Si el usuario menciona preferencias (no le gusta el ruido, busca algo romántico, etc.), teneelas en cuenta"""

        self.agent = CodeAgent(
            model=self.model,
            tools=tools,
            name="SalidasBot",
            description="Bot inteligente para buscar salidas en Buenos Aires",
            additional_authorized_imports=["json", "requests"]
        )
    
    def chat(self, user_input: str) -> str:
        """
        Procesa un input del usuario manteniendo contexto de la conversación.
        
        Args:
            user_input: Mensaje del usuario
        
        Returns:
            Respuesta del agent
        """
        # Guardar en memoria
        self.memory.add_message("user", user_input)
        
        try:
            # Construir prompt con system_prompt + historial para multi-turno
            recent = self.memory.short_term.get_recent_context(limit=6)
            # Excluir el mensaje que acabamos de agregar (el último)
            history_msgs = recent[:-1]
            
            # Construir prompt con instrucción del sistema
            system_context = f"{self.system_prompt}\n\n"
            
            if history_msgs:
                history_text = "\n".join(
                    f"{'Usuario' if m['role'] == 'user' else 'Asistente'}: {m['content']}"
                    for m in history_msgs
                )
                prompt = f"{system_context}Historial:\n{history_text}\n\nUsuario: {user_input}"
            else:
                prompt = f"{system_context}Usuario: {user_input}"
            
            # Llamar al agent con contexto
            response = self.agent.run(prompt)
            
            # Guardar respuesta en memoria
            self.memory.add_message("assistant", str(response))
            
            return str(response)
            
        except Exception as e:
            error_msg = f"❌ Error procesando tu consulta: {str(e)}"
            self.memory.add_message("assistant", error_msg)
            return error_msg
    
    def set_user(self, user_id: str):
        """Cambia el usuario actual"""
        self.memory.set_user(user_id)
    
    def save_session(self, summary: str = ""):
        """Guarda la sesión en memoria larga"""
        self.memory.save_session(summary)
    
    def add_favorite(self, place_name: str, category: str, rating: float, notes: str = ""):
        """Añade un lugar a favoritos"""
        self.memory.long_term.add_favorite_place(
            self.memory.current_user,
            place_name,
            category,
            rating,
            notes
        )


# ===================== MAIN LOOP =====================

def main():
    """Loop principal del agent"""
    
    print("\n" + "="*60)
    print("🤖  SALIDAS BOT - Buenos Aires")
    print("="*60)
    print("Escribe 'salir' para terminar")
    print("Escribe 'guardar' para guardar sesión")
    print("Escribe 'user [id]' para cambiar usuario")
    print("="*60 + "\n")
    
    # Inicializar agent
    agent = SalidasAgent()
    
    while True:
        try:
            user_input = input("\n👤 Tú: ").strip()
            
            if not user_input:
                continue
            
            # Comandos especiales
            if user_input.lower() == "salir":
                print("👋 ¡Hasta luego!")
                agent.save_session("Sesión terminada por usuario")
                break
            
            if user_input.lower() == "guardar":
                agent.save_session("Sesión guardada manualmente")
                print("✅ Sesión guardada")
                continue
            
            if user_input.lower().startswith("user "):
                user_id = user_input.split(" ", 1)[1]
                agent.set_user(user_id)
                print(f"✅ Cambiado a usuario: {user_id}")
                continue
            
            # Procesar con agent
            print("\n🤔 Pensando...")
            response = agent.chat(user_input)
            print(f"\n🤖 Salidas: {response}")
            
        except KeyboardInterrupt:
            print("\n\n👋 ¡Interrumpido!")
            agent.save_session("Sesión interrumpida")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    main()
