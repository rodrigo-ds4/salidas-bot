"""
Backend FastAPI para Salidas Bot
Interfaz web + API REST + WebSocket Chat
"""

import os
import json
from fastapi import FastAPI, WebSocket, HTTPException, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import asyncio
from typing import List, Dict
from datetime import datetime

# Cargar variables
load_dotenv()

# Importar agent y tools
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from agent.tools import search_buenos_aires_places, get_reviews, get_weather_ba, get_current_time
from agent.faq import get_faq_response
from agent.memory import MemoryManager
from main import SalidasAgent

# Agente global (una instancia, conversaciones separadas por usuario via memoria)
_global_agent: SalidasAgent | None = None
active_users: Dict[str, SalidasAgent] = {}

def get_or_create_agent(user_id: str) -> SalidasAgent:
    """Retorna un agente dedicado por usuario, créandolo si no existe."""
    if user_id not in active_users:
        active_users[user_id] = SalidasAgent()
        active_users[user_id].set_user(user_id)
    return active_users[user_id]

# ===================== SETUP FASTAPI =====================

app = FastAPI(
    title="🤖 Salidas Bot API",
    description="Bot inteligente para buscar salidas en Buenos Aires",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===================== MODELOS =====================

class MessageRequest(BaseModel):
    message: str
    user_id: str = "default"

class PlaceSearchRequest(BaseModel):
    query: str
    category: str = "general"

class ReviewRequest(BaseModel):
    place_name: str

# ===================== RUTAS API =====================

@app.get("/", response_class=HTMLResponse)
async def get_home():
    """Página principal"""
    return HOMEPAGE_HTML

@app.get("/api/health")
async def health_check():
    """Health check"""
    return {"status": "ok", "message": "🤖 Salidas Bot está online"}

@app.get("/api/time")
async def get_time():
    """Obtiene hora actual"""
    result = get_current_time()
    return json.loads(result)

@app.get("/api/weather")
async def get_weather():
    """Obtiene clima actual"""
    result = get_weather_ba()
    return json.loads(result)

@app.post("/api/search")
async def search_places(request: PlaceSearchRequest):
    """Busca lugares"""
    result = search_buenos_aires_places(request.query, request.category)
    return json.loads(result)

@app.post("/api/reviews")
async def get_place_reviews(request: ReviewRequest):
    """Obtiene reviews de un lugar"""
    result = get_reviews(request.place_name)
    return json.loads(result)

@app.get("/api/faq")
async def search_faq(q: str):
    """Busca en FAQ"""
    result = get_faq_response(q)
    if result:
        return {"status": "found", "answer": result}
    return {"status": "not_found"}

@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    """WebSocket para chat en tiempo real con el agent"""
    await websocket.accept()
    user_id = f"web_{datetime.now().timestamp()}"

    agent = get_or_create_agent(user_id)

    try:
        await websocket.send_json({
            "type": "system",
            "message": "🤖 Bienvenido a Salidas Bot. Preguntame sobre lugares, clima, horarios en Buenos Aires..."
        })

        while True:
            data = await websocket.receive_json()
            user_message = data.get("message", "").strip()

            if not user_message:
                continue

            # Procesar con el agente real (smolagents + Groq)
            try:
                # Ejecutar en thread pool para no bloquear el event loop
                response = await asyncio.get_event_loop().run_in_executor(
                    None, agent.chat, user_message
                )

                await websocket.send_json({
                    "type": "response",
                    "message": response
                })
            except Exception as e:
                print(f"Error procesando query: {e}")
                await websocket.send_json({
                    "type": "error",
                    "message": f"❌ Error: {str(e)}"
                })

    except WebSocketDisconnect:
        print(f"Usuario {user_id} desconectado")
        if user_id in active_users:
            del active_users[user_id]
    except Exception as e:
        print(f"WebSocket error: {e}")
        if user_id in active_users:
            del active_users[user_id]


# ===================== HTML =====================

HOMEPAGE_HTML = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🤖 Salidas Bot - Buenos Aires</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        
        .container {
            background: white;
            border-radius: 12px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            width: 100%;
            max-width: 500px;
            overflow: hidden;
        }
        
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px 20px;
            text-align: center;
        }
        
        .header h1 {
            font-size: 28px;
            margin-bottom: 5px;
        }
        
        .header p {
            font-size: 14px;
            opacity: 0.9;
        }
        
        .content {
            padding: 20px;
        }
        
        .search-box {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
        }
        
        .search-box input {
            flex: 1;
            padding: 12px;
            border: 2px solid #eee;
            border-radius: 8px;
            font-size: 14px;
            transition: border-color 0.3s;
        }
        
        .search-box input:focus {
            outline: none;
            border-color: #667eea;
        }
        
        .search-box button {
            padding: 12px 20px;
            background: #667eea;
            color: white;
            border: none;
            border-radius: 8px;
            font-weight: 600;
            cursor: pointer;
            transition: background 0.3s;
        }
        
        .search-box button:hover {
            background: #764ba2;
        }
        
        .tabs {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
            border-bottom: 2px solid #eee;
        }
        
        .tab {
            padding: 10px 15px;
            background: none;
            border: none;
            cursor: pointer;
            font-weight: 500;
            color: #999;
            border-bottom: 3px solid transparent;
            transition: all 0.3s;
        }
        
        .tab.active {
            color: #667eea;
            border-bottom-color: #667eea;
        }
        
        .results {
            background: #f9f9f9;
            border-radius: 8px;
            padding: 15px;
            max-height: 400px;
            overflow-y: auto;
        }
        
        .result-item {
            background: white;
            padding: 12px;
            margin-bottom: 10px;
            border-radius: 6px;
            border-left: 4px solid #667eea;
        }
        
        .result-item h3 {
            font-size: 16px;
            margin-bottom: 5px;
        }
        
        .result-item p {
            font-size: 13px;
            color: #666;
            margin: 3px 0;
        }
        
        .rating {
            color: #ffc107;
            font-weight: bold;
        }
        
        .info-box {
            background: #e3f2fd;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 15px;
            border-left: 4px solid #2196f3;
        }
        
        .info-box h4 {
            color: #1976d2;
            margin-bottom: 8px;
        }
        
        .info-box p {
            font-size: 14px;
            color: #555;
        }
        
        .loading {
            text-align: center;
            color: #999;
            padding: 20px;
        }
        
        .error {
            background: #ffebee;
            color: #c62828;
            padding: 12px;
            border-radius: 6px;
            margin-bottom: 15px;
            border-left: 4px solid #c62828;
        }
        
        .footer {
            background: #f5f5f5;
            padding: 15px;
            text-align: center;
            font-size: 12px;
            color: #999;
            border-top: 1px solid #eee;
        }
        
        .chat-container {
            display: flex;
            flex-direction: column;
            height: 400px;
        }
        
        .chat-messages {
            flex: 1;
            overflow-y: auto;
            padding: 15px;
            background: #fafafa;
            border-radius: 8px;
            margin-bottom: 10px;
            display: flex;
            flex-direction: column;
            gap: 10px;
        }
        
        .chat-message {
            display: flex;
            gap: 10px;
            align-items: flex-end;
            animation: slideIn 0.3s ease-in;
        }
        
        @keyframes slideIn {
            from {
                opacity: 0;
                transform: translateY(10px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        .message-bubble {
            max-width: 80%;
            padding: 10px 15px;
            border-radius: 12px;
            word-wrap: break-word;
            line-height: 1.4;
            font-size: 14px;
        }
        
        .user-message .message-bubble {
            background: #667eea;
            color: white;
            align-self: flex-end;
            margin-left: auto;
        }
        
        .bot-message .message-bubble {
            background: white;
            color: #333;
            border: 1px solid #eee;
            align-self: flex-start;
        }
        
        .system-message .message-bubble {
            background: #e3f2fd;
            color: #1976d2;
            align-self: center;
            font-size: 13px;
            width: 100%;
            text-align: center;
        }
        
        .chat-input-box {
            display: flex;
            gap: 10px;
        }
        
        .chat-input-box input {
            flex: 1;
            padding: 12px;
            border: 2px solid #eee;
            border-radius: 8px;
            font-size: 14px;
            transition: border-color 0.3s;
        }
        
        .chat-input-box input:focus {
            outline: none;
            border-color: #667eea;
        }
        
        .chat-input-box button {
            padding: 12px 20px;
            background: #667eea;
            color: white;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-weight: 600;
            transition: background 0.3s;
        }
        
        .chat-input-box button:hover {
            background: #764ba2;
        }
        
        .chat-input-box button:disabled {
            background: #ccc;
            cursor: not-allowed;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 Salidas Bot</h1>
            <p>Descubre los mejores lugares en Buenos Aires</p>
        </div>
        
        <div class="content">
            <div class="tabs">
                <button class="tab active" onclick="switchTab('chat')">💬 Chat</button>
                <button class="tab" onclick="switchTab('search')">🔍 Búsqueda</button>
                <button class="tab" onclick="switchTab('weather')">🌤️ Clima</button>
                <button class="tab" onclick="switchTab('info')">ℹ️ Información</button>
            </div>
            
            <div id="chat" class="tab-content">
                <div class="chat-container">
                    <div class="chat-messages" id="chatMessages"></div>
                    <div class="chat-input-box">
                        <input type="text" id="chatInput" placeholder="Pregúntame sobre lugares, clima...">
                        <button id="sendBtn">Enviar</button>
                    </div>
                </div>
            </div>
            
            <div id="search" class="tab-content" style="display: none;">
                <div class="search-box" style="margin-bottom: 15px;">
                    <input type="text" id="searchInput" placeholder="Busca bares, restaurantes, zonas...">
                    <button onclick="search()">🔍</button>
                </div>
                <div class="results" id="searchResults">
                    <p style="text-align: center; color: #999;">Escribe algo para buscar...</p>
                </div>
            </div>
            
            <div id="weather" class="tab-content" style="display: none;">
                <button onclick="getWeather()" style="width: 100%; padding: 12px; margin-bottom: 15px; background: #667eea; color: white; border: none; border-radius: 6px; cursor: pointer;">Cargar Clima</button>
                <div id="weatherResults"></div>
            </div>
            
            <div id="info" class="tab-content" style="display: none;">
                <div class="info-box">
                    <h4>📚 Información Útil</h4>
                    <p>Horario de comida: Almuerzo 12-15hs, Cena 20-23hs</p>
                </div>
                <div class="info-box">
                    <h4>🚇 Transporte</h4>
                    <p>Subte, colectivo, taxi. La tarjeta SUBE funciona en todo.</p>
                </div>
                <div class="info-box">
                    <h4>🗺️ Zonas Populares</h4>
                    <p>Palermo (trendy), San Telmo (histórico), La Boca (turístico)</p>
                </div>
            </div>
        </div>
        
        <div class="footer">
            <p>🤖 Salidas Bot v1.0 | Powered by Groq + smolagents</p>
        </div>
    </div>
    
    <script>
        // Variables globales
        window.ws = null;
        
        // Conectar WebSocket
        window.connectWebSocket = function() {
            console.log('🔌 Intentando conectar WebSocket...');
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const wsUrl = protocol + '//' + window.location.host + '/ws/chat';
            console.log('URL:', wsUrl);
            
            window.ws = new WebSocket(wsUrl);
            
            window.ws.onopen = () => {
                console.log('✅ Conectado al chat');
            };
            
            window.ws.onmessage = (event) => {
                console.log('📨 Mensaje recibido:', event.data);
                const data = JSON.parse(event.data);
                window.displayChatMessage(data);
            };
            
            window.ws.onerror = (error) => {
                console.error('❌ Error WebSocket:', error);
                window.displayChatMessage({
                    type: 'error',
                    message: 'Error de conexión. Recargando...'
                });
            };
            
            window.ws.onclose = () => {
                console.log('❌ Desconectado');
                setTimeout(window.connectWebSocket, 3000);
            };
        };
        
        window.displayChatMessage = function(data) {
            const messagesDiv = document.getElementById('chatMessages');
            const messageDiv = document.createElement('div');
            messageDiv.className = `chat-message ${data.type}-message`;
            
            const bubble = document.createElement('div');
            bubble.className = 'message-bubble';
            
            // Convertir markdown simple a HTML
            let text = data.message;
            text = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
            text = text.replace(/\n/g, '<br>');
            
            bubble.innerHTML = text;
            messageDiv.appendChild(bubble);
            messagesDiv.appendChild(messageDiv);
            
            // Auto-scroll al final
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
            
            // Re-habilitar botón
            document.getElementById('sendBtn').disabled = false;
        };
        
        window.sendChatMessage = function() {
            console.log('📤 sendChatMessage llamado');
            const input = document.getElementById('chatInput');
            const message = input.value.trim();
            
            console.log('Mensaje:', message, 'WS:', window.ws, 'Ready:', window.ws ? window.ws.readyState : 'N/A');
            
            if (!message || !window.ws || window.ws.readyState !== WebSocket.OPEN) {
                console.log('❌ No se puede enviar:', {message: message, ws: !!window.ws, ready: window.ws?.readyState});
                return;
            }
            
            // Deshabilitar botón mientras envía
            document.getElementById('sendBtn').disabled = true;
            
            // Mostrar mensaje del usuario
            window.displayChatMessage({
                type: 'user',
                message: message
            });
            
            // Enviar al servidor
            window.ws.send(JSON.stringify({
                message: message
            }));
            
            // Limpiar input
            input.value = '';
            input.focus();
        };
        
        window.switchTab = function(tab) {
            document.querySelectorAll('.tab-content').forEach(e => e.style.display = 'none');
            document.getElementById(tab).style.display = 'block';
            
            document.querySelectorAll('.tab').forEach(e => e.classList.remove('active'));
            event.target.classList.add('active');
            
            // Focus en chat input si es necesario
            if (tab === 'chat') {
                setTimeout(() => document.getElementById('chatInput').focus(), 100);
            }
        };
        
        window.search = async function() {
            const query = document.getElementById('searchInput').value;
            if (!query) return;
            
            const resultsDiv = document.getElementById('searchResults');
            resultsDiv.innerHTML = '<div class="loading">🔍 Buscando...</div>';
            
            try {
                const response = await fetch('/api/search', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({query, category: 'general'})
                });
                
                const data = await response.json();
                
                if (data.places && data.places.length > 0) {
                    let html = '';
                    data.places.forEach(place => {
                        html += `
                            <div class="result-item">
                                <h3>📍 ${place.name}</h3>
                                <p><strong>Zona:</strong> ${place.zone}</p>
                                <p><strong>Tipo:</strong> ${place.type}</p>
                                <p class="rating">⭐ ${place.rating}/5</p>
                                <p><small>${place.vibe}</small></p>
                            </div>
                        `;
                    });
                    resultsDiv.innerHTML = html;
                } else {
                    resultsDiv.innerHTML = '<p style="text-align: center; color: #999;">No encontré nada. Intenta con otro término.</p>';
                }
            } catch (e) {
                resultsDiv.innerHTML = '<div class="error">❌ Error en la búsqueda</div>';
            }
        };
        
        window.getWeather = async function() {
            const resultsDiv = document.getElementById('weatherResults');
            resultsDiv.innerHTML = '<div class="loading">🌤️ Cargando clima...</div>';
            
            try {
                const response = await fetch('/api/weather');
                const data = await response.json();
                
                const weather = data.weather;
                resultsDiv.innerHTML = `
                    <div class="info-box">
                        <h4>🌡️ Clima Actual</h4>
                        <p><strong>${weather.condition}</strong></p>
                        <p>Temperatura: <strong>${weather.temperature}°C</strong> (siente ${weather.feels_like}°C)</p>
                        <p>Humedad: ${weather.humidity}% | Viento: ${weather.wind_speed} km/h</p>
                        <p>Probabilidad de lluvia: ${weather.rain_probability}%</p>
                    </div>
                `;
            } catch (e) {
                resultsDiv.innerHTML = '<div class="error">❌ Error cargando clima</div>';
            }
        };
        
        // Inicializar al cargar
        window.addEventListener('DOMContentLoaded', () => {
            window.connectWebSocket();
            
            const sendBtn = document.getElementById('sendBtn');
            if (sendBtn) {
                sendBtn.addEventListener('click', window.sendChatMessage);
            }
            
            const chatInput = document.getElementById('chatInput');
            if (chatInput) {
                chatInput.addEventListener('keypress', (e) => {
                    if (e.key === 'Enter') window.sendChatMessage();
                });
            }
            
            const searchInput = document.getElementById('searchInput');
            if (searchInput) {
                searchInput.addEventListener('keypress', (e) => {
                    if (e.key === 'Enter') window.search();
                });
            }
        });
    </script>
</body>
</html>
"""

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
