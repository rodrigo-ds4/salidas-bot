"""
Información del clima en Buenos Aires
Usa OpenWeather API (tier gratis)
Por ahora datos simulados realistas
"""

import json
from datetime import datetime, timedelta
from typing import Dict, Optional

# Simulación de datos de clima
def get_weather_forecast(days: int = 5) -> Dict:
    """
    Obtiene pronóstico del clima para Buenos Aires.
    
    Args:
        days: Cantidad de días para el pronóstico
    
    Returns:
        Dict con información del clima
    """
    today = datetime.now()
    forecast = []
    
    # Datos simulados realistas
    temps = [24, 22, 25, 23, 26]  # Temperaturas
    conditions = ["Parcialmente nublado", "Nublado", "Soleado", "Lluvias", "Soleado"]
    humidities = [65, 70, 55, 80, 50]
    winds = [10, 12, 8, 15, 7]
    
    for i in range(days):
        day = today + timedelta(days=i)
        forecast.append({
            "date": day.strftime("%d/%m/%Y"),
            "day_name": ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"][day.weekday()],
            "temperature": temps[i % len(temps)],
            "feels_like": temps[i % len(temps)] - 2,
            "condition": conditions[i % len(conditions)],
            "humidity": humidities[i % len(humidities)],
            "wind_speed": winds[i % len(winds)],
            "uv_index": 7,
            "rain_probability": [10, 50, 5, 75, 5][i % 5]
        })
    
    return {
        "status": "success",
        "location": "Buenos Aires, Argentina",
        "timezone": "America/Argentina/Buenos_Aires",
        "current": {
            "temperature": 24,
            "feels_like": 22,
            "condition": "Parcialmente nublado",
            "humidity": 65,
            "wind_speed": 10,
            "uv_index": 7,
            "timestamp": datetime.now().isoformat()
        },
        "forecast": forecast
    }


def get_current_weather() -> Dict:
    """Obtiene el clima actual en Buenos Aires."""
    now = datetime.now()
    
    return {
        "status": "success",
        "location": "Buenos Aires, Argentina",
        "current_time": now.isoformat(),
        "weather": {
            "temperature": 24,
            "temperature_min": 18,
            "temperature_max": 28,
            "feels_like": 22,
            "condition": "Parcialmente nublado",
            "description": "Cielo parcialmente nublado con vientos leves",
            "humidity": 65,
            "wind_speed": 10,
            "wind_direction": "NE",
            "pressure": 1013,
            "visibility": 10,
            "uv_index": 7,
            "rain_probability": 10
        },
        "clothes_recommendation": "Campera ligera, no lluvia esperada",
        "activity_recommendation": "Buen día para salir. Ideal para actividades al aire libre."
    }


def should_bring_umbrella() -> Dict:
    """
    Verifica si es necesario llevar paraguas.
    
    Returns:
        Dict con recomendación
    """
    weather = get_current_weather()
    rain_prob = weather["weather"]["rain_probability"]
    
    should_bring = rain_prob > 40
    
    return {
        "status": "success",
        "rain_probability": rain_prob,
        "should_bring_umbrella": should_bring,
        "recommendation": "Sí, lleva paraguas" if should_bring else "No es necesario paraguas",
        "reason": "Hay probabilidad de lluvia" if should_bring else "No se espera lluvia"
    }


def get_best_hours_for_outdoor() -> Dict:
    """
    Sugerencias de mejores horarios para actividades al aire libre.
    
    Returns:
        Dict con recomendaciones
    """
    forecast = get_weather_forecast()
    current = forecast["current"]
    
    return {
        "status": "success",
        "current_weather": current,
        "best_hours": {
            "morning": {"time": "09:00 - 12:00", "temperature": 22, "recommendation": "Excelente"},
            "afternoon": {"time": "14:00 - 18:00", "temperature": 26, "recommendation": "Muy bueno"},
            "evening": {"time": "19:00 - 21:00", "temperature": 23, "recommendation": "Bueno"}
        },
        "tip": "La tarde es la mejor hora. Lleva protector solar."
    }
