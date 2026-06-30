"""Agent tools para Salidas Bot"""

import requests
import json
from datetime import datetime
from typing import Optional

# Importar scrapers
from scrapers.lugares import search_places as scraper_search_places
from scrapers.lugares import get_place_reviews as scraper_get_reviews
from scrapers.lugares import get_popular_places_by_type, search_by_zone
from scrapers.clima import get_current_weather, get_weather_forecast, should_bring_umbrella

# ===================== TOOLS DEFINITIONES =====================


def search_buenos_aires_places(query: str, category: str = "general") -> str:
    """
    Busca lugares en Buenos Aires.
    
    Args:
        query: Qué buscar (ej: "bares", "restaurantes", "parques")
        category: Categoría opcional (ej: "bar", "restaurante")
    
    Returns:
        JSON con lugares encontrados
    """
    try:
        # Usar el scraper
        places = scraper_search_places(query)
        
        if not places:
            # Intentar buscar por zona si es un nombre de zona
            places = search_by_zone(query)
        
        return json.dumps({
            "status": "success",
            "query": query,
            "places": places[:10],  # Top 10
            "count": len(places)
        }, ensure_ascii=False, indent=2)
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})


def get_reviews(place_name: str) -> str:
    """
    Obtiene reviews de un lugar específico.
    
    Args:
        place_name: Nombre del lugar
    
    Returns:
        JSON con reviews
    """
    try:
        result = scraper_get_reviews(place_name)
        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})


def get_weather_ba() -> str:
    """
    Obtiene el clima actual en Buenos Aires.
    
    Returns:
        JSON con información del clima
    """
    try:
        weather = get_current_weather()
        return json.dumps(weather, ensure_ascii=False, indent=2)
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})


def get_weather_forecast_ba() -> str:
    """
    Obtiene el pronóstico del clima para los próximos 5 días.
    
    Returns:
        JSON con pronóstico
    """
    try:
        forecast = get_weather_forecast(5)
        return json.dumps(forecast, ensure_ascii=False, indent=2)
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})


def get_current_time() -> str:
    """
    Retorna la hora actual en Buenos Aires.
    """
    now = datetime.now()
    return json.dumps({
        "status": "success",
        "time": now.strftime("%H:%M:%S"),
        "date": now.strftime("%d/%m/%Y"),
        "day_name": ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"][now.weekday()],
        "timezone": "Argentina/Buenos_Aires"
    }, ensure_ascii=False)


def calculator(operation: str) -> str:
    """
    Calculadora simple.
    
    Args:
        operation: Operación a realizar (ej: "2 + 2", "10 * 5")
    
    Returns:
        Resultado
    """
    try:
        # Seguro: solo permite números y operadores básicos
        allowed_chars = set("0123456789+-*/.() ")
        if not all(c in allowed_chars for c in operation):
            return json.dumps({"status": "error", "message": "Operación no permitida"})
        
        result = eval(operation)
        return json.dumps({"status": "success", "operation": operation, "result": result})
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})


def get_popular_places(place_type: str) -> str:
    """
    Obtiene los lugares más populares de un tipo específico.
    
    Args:
        place_type: Tipo de lugar (ej: "bar", "restaurante", "café")
    
    Returns:
        JSON con lugares ordenados por rating
    """
    try:
        places = get_popular_places_by_type(place_type)
        return json.dumps({
            "status": "success",
            "type": place_type,
            "places": places,
            "count": len(places)
        }, ensure_ascii=False, indent=2)
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})


def check_umbrella_needed() -> str:
    """Verifica si es necesario llevar paraguas."""
    try:
        result = should_bring_umbrella()
        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})


# ===================== TOOL REGISTRY =====================

SALIDAS_TOOLS = [
    {
        "name": "search_buenos_aires_places",
        "description": "Busca lugares, bares, restaurantes, parques en Buenos Aires",
        "function": search_buenos_aires_places,
        "inputs": [
            {"name": "query", "type": "string", "description": "Qué buscar (ej: bares, restaurantes)"},
            {"name": "category", "type": "string", "description": "Categoría opcional"}
        ]
    },
    {
        "name": "get_reviews",
        "description": "Obtiene reviews y opiniones de un lugar específico",
        "function": get_reviews,
        "inputs": [
            {"name": "place_name", "type": "string", "description": "Nombre del lugar"}
        ]
    },
    {
        "name": "get_weather_ba",
        "description": "Obtiene el clima actual en Buenos Aires",
        "function": get_weather_ba,
        "inputs": []
    },
    {
        "name": "get_weather_forecast_ba",
        "description": "Obtiene el pronóstico del clima para los próximos 5 días",
        "function": get_weather_forecast_ba,
        "inputs": []
    },
    {
        "name": "get_current_time",
        "description": "Retorna la hora actual en Buenos Aires",
        "function": get_current_time,
        "inputs": []
    },
    {
        "name": "calculator",
        "description": "Realiza cálculos matemáticos simples",
        "function": calculator,
        "inputs": [
            {"name": "operation", "type": "string", "description": "Operación matemática (ej: 2 + 2)"}
        ]
    },
    {
        "name": "get_popular_places",
        "description": "Obtiene los lugares más populares de un tipo específico",
        "function": get_popular_places,
        "inputs": [
            {"name": "place_type", "type": "string", "description": "Tipo de lugar (ej: bar, restaurante)"}
        ]
    },
    {
        "name": "check_umbrella_needed",
        "description": "Verifica si es necesario llevar paraguas",
        "function": check_umbrella_needed,
        "inputs": []
    }
]
