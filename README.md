# 🤖 Salidas Bot - Buenos Aires Guide Agent

Agent inteligente para buscar salidas, lugares, reviews y más en Buenos Aires usando smolagents + Groq.

## ✨ Features

- 🏟️ **Búsqueda de lugares** - Bares, restaurantes, parques, etc en BA (8+ zonas)
- ⭐ **Reviews** - Opiniones de usuarios y calificaciones
- 🌤️ **Clima** - Información meteorológica en tiempo real
- 🧠 **Memoria** - Corto plazo (sesión) y largo plazo (persistente)
- 📚 **ChromaDB FAQ** - Base de conocimiento sobre Buenos Aires
- 🧮 **Herramientas útiles** - Calculadora, horarios, etc
- 🌐 **Frontend Web** - Interfaz FastAPI + Gradio para HF Spaces

## 🚀 Quick Start

### Local (CLI)

```bash
# 1. Clonar/entrar
cd ~/Desktop/agentes/salidas-bot

# 2. Instalar
pip install -r requirements.txt

# 3. Crear .env
cp .env.example .env
# Editar con tu GROQ_API_KEY

# 4. Ejecutar agent CLI
python main.py

# 5. O ejecutar FastAPI
uvicorn backend.api:app --reload

# 6. O ejecutar Gradio (para HF Spaces)
python app_gradio.py
```

## 🌐 Deployment Opciones

### Opción 1: HuggingFace Spaces (RECOMENDADO - GRATIS)

```bash
# 1. Fork en HuggingFace
# https://huggingface.co/spaces/new

# 2. Crear Space:
# - Nombre: salidas-bot
# - Licencia: MIT
# - SDK: Gradio
# - Hardware: CPU (gratis)

# 3. Cargar archivos:
git clone https://github.com/tuusuario/salidas-bot
cd salidas-bot
git remote set-url origin https://huggingface.co/spaces/tuusuario/salidas-bot
git push

# 4. Agregar secret en Settings:
# GROQ_API_KEY = tu_clave_aqui
```

### Opción 2: Vercel (Frontend + Serverless)

```bash
# 1. Deploy solo frontend
vercel deploy

# 2. Backend en Vercel Functions:
# - Usar FastAPI con serverless handler
# - O usar ngrok para backend local
```

### Opción 3: Docker Local

```bash
# Build
docker build -t salidas-bot .

# Run
docker run -e GROQ_API_KEY=tu_clave \
           -p 8000:8000 \
           salidas-bot
```

### Opción 4: GitHub + Railway / Render

```bash
# Railway (https://railway.app)
# 1. Conectar repo GitHub
# 2. Agregar GROQ_API_KEY env var
# 3. Deploy automático

# O Render (https://render.com)
# Similar setup
```

## 📁 Estructura

```
salidas-bot/
├── main.py                 # Agent CLI
├── backend/
│   └── api.py             # FastAPI + HTML
├── app_gradio.py          # Interfaz Gradio (HF Spaces)
├── agent/
│   ├── tools.py           # 8 tools del agent
│   ├── memory.py          # Memory manager
│   └── faq.py             # ChromaDB FAQ
├── scrapers/
│   ├── lugares.py         # 8+ zonas BA
│   └── clima.py           # Datos clima
├── Dockerfile             # Para deploy
├── requirements.txt       # Dependencias
└── .github/workflows/     # CI/CD GitHub Actions
```

## 🔧 Dependencias Principales

- **smolagents** - Framework para agents
- **groq** - LLM Llama 3.3 (gratis)
- **litellm** - Router de LLMs
- **fastapi** - Backend API
- **chromadb** - Vector store para FAQ
- **gradio** - UI alternativa

## 📊 Características del Agent

### Tools Disponibles

1. **search_places** - Busca lugares por zona/tipo
2. **get_place_reviews** - Reviews de un lugar
3. **get_climate** - Clima actual
4. **get_forecast** - Pronóstico 5 días
5. **get_time** - Hora actual BA
6. **calc** - Calculadora
7. **get_top_places** - Ranking por rating
8. **should_i_bring_umbrella** - Necesidad paraguas

### Memory System

**Short-term**: En RAM (sesión actual)
- Historial de mensajes
- Contexto del usuario

**Long-term**: SQLite persistente
- Conversaciones guardadas
- Preferencias usuario
- Lugares favoritos

## 📝 Ejemplos de Uso

### CLI
```bash
👤 ¿Qué bares hay en Palermo?
🤖 Fierro Hotel, Bahrain, Casa Lucio

👤 ¿Necesito paraguas?
🤖 No (10% probabilidad de lluvia)

👤 Horarios de comida en BA?
🤖 Desayuno: 7-10hs, Almuerzo: 12-15hs, Cena: 20-23hs
```

### API REST
```bash
curl http://localhost:8000/api/search \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"query": "bares Palermo"}'

curl http://localhost:8000/api/weather

curl http://localhost:8000/api/time
```

### Gradio Web
Interfaz visual en http://localhost:7860

## 🛠️ Desarrollo

### Setup local

```bash
# Entorno virtual
python -m venv venv
source venv/bin/activate

# Dependencias
pip install -r requirements.txt

# Dev tools
pip install pytest black ruff

# Linting
ruff check .
black .

# Tests
pytest tests/
```

## 🚀 Roadmap

- [x] Agent básico con smolagents
- [x] 8 tools funcionales
- [x] Memory (corto + largo plazo)
- [x] ChromaDB para FAQ
- [x] Frontend FastAPI
- [x] Interfaz Gradio (HF Spaces)
- [ ] Scraping real (Google Places, TripAdvisor)
- [ ] OpenWeather API real
- [ ] Más zonas y lugares
- [ ] Multiidioma (inglés, portugués)
- [ ] Botón compartir resultados
- [ ] Historial con persistencia

## 📦 API Keys Necesarias

### Gratuitas (Tier libre)

1. **Groq** (REQUERIDA)
   - https://console.groq.com
   - Llama 3.3 70B - Muy rápido
   - Límite: 30 requests/minuto (suficiente)

2. **OpenWeather** (Opcional)
   - https://openweathermap.org/api
   - API actual vs simulada
   - Límite: 1000 calls/día

## 🤝 Contribuir

1. Fork el repo
2. Crea una rama (`git checkout -b feature/amazing`)
3. Commit (`git commit -m "Add amazing feature"`)
4. Push (`git push origin feature/amazing`)
5. Abre PR

## 📄 Licencia

MIT - Usa libremente

## 📞 Soporte

- Abre issue en GitHub
- Revisa [GitHub Discussions](https://github.com/tuusuario/salidas-bot/discussions)

---

**Made with ❤️ in Buenos Aires**

## Roadmap

- [x] Estructura base
- [ ] Agent básico funcionando
- [ ] Scrapers (lugares, reviews, clima)
- [ ] Memory manager
- [ ] ChromaDB FAQ
- [ ] FastAPI frontend
- [ ] Deploy HuggingFace Spaces
- [ ] Deploy Vercel

## Desarrollo

```bash
# Testing
poetry run pytest

# Linting
poetry run ruff check .
poetry run black .
```
