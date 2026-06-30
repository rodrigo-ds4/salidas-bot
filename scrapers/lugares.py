"""
Scraper de lugares en Buenos Aires
Datos por ahora son simulados, después puedes agregar scraping real
"""

import json
from typing import List, Dict

# Datos hardcodeados de lugares en BA
LUGARES_BA = {
    "Palermo": [
        {
            "name": "Fierro Hotel",
            "type": "bar",
            "address": "Acoyte 1350",
            "rating": 4.7,
            "price": "$$$",
            "vibe": "Hipster, diseño"
        },
        {
            "name": "Bahrain",
            "type": "bar",
            "address": "Armenia 1343",
            "rating": 4.5,
            "price": "$$",
            "vibe": "Relax, cocktails"
        },
        {
            "name": "Casa Lucio",
            "type": "restaurante",
            "address": "Córdoba 5496",
            "rating": 4.6,
            "price": "$$$",
            "vibe": "Gourmet, parrilla"
        }
    ],
    "San Telmo": [
        {
            "name": "Bar Fundacional",
            "type": "bar",
            "address": "Bolívar 960",
            "rating": 4.4,
            "price": "$$",
            "vibe": "Histórico, tango"
        },
        {
            "name": "El Ateneo Grand Splendid",
            "type": "café-librería",
            "address": "Santa Fe 1860",
            "rating": 4.8,
            "price": "$$",
            "vibe": "Cultural, arquitectura"
        },
        {
            "name": "Café Tortoni",
            "type": "café",
            "address": "Avenida de Mayo 825",
            "rating": 4.5,
            "price": "$$",
            "vibe": "Histórico, tradicional"
        }
    ],
    "La Boca": [
        {
            "name": "Bodegón del Caminante",
            "type": "restaurante",
            "address": "Magallanes 444",
            "rating": 4.3,
            "price": "$$",
            "vibe": "Típico, vista al río"
        },
        {
            "name": "Bar Piazzolla",
            "type": "bar-tango",
            "address": "Balcarce 1000",
            "rating": 4.6,
            "price": "$$$",
            "vibe": "Tango show, cena"
        }
    ],
    "Recoleta": [
        {
            "name": "Fervor",
            "type": "restaurante",
            "address": "Posadas 1086",
            "rating": 4.7,
            "price": "$$$",
            "vibe": "Fine dining, parrilla"
        },
        {
            "name": "Patio Bullrich",
            "type": "shopping",
            "address": "Posadas 1245",
            "rating": 4.4,
            "price": "Variado",
            "vibe": "Luxury shopping"
        }
    ],
    "Belgrano": [
        {
            "name": "Green Parrilla",
            "type": "restaurante",
            "address": "Echeverría 1900",
            "rating": 4.5,
            "price": "$$$",
            "vibe": "Parrilla premium"
        },
        {
            "name": "Café Literario",
            "type": "café",
            "address": "Acoyte 1800",
            "rating": 4.3,
            "price": "$$",
            "vibe": "Tranquilo, libros"
        }
    ],
    "Almagro": [
        {
            "name": "The Picaresques",
            "type": "bar",
            "address": "Medrano 1670",
            "rating": 4.6,
            "price": "$$",
            "vibe": "Craft beer, moderno"
        },
        {
            "name": "Bárbara",
            "type": "restaurante",
            "address": "Carlos Pellegrini 240",
            "rating": 4.4,
            "price": "$$$",
            "vibe": "Italiana, elegante"
        }
    ],
    "Flores": [
        {
            "name": "Mishima",
            "type": "restaurante",
            "address": "Córdoba 3003",
            "rating": 4.7,
            "price": "$$$",
            "vibe": "Japonés, fusion"
        },
        {
            "name": "Parque Centenario",
            "type": "parque",
            "address": "Donato Álvarez 300",
            "rating": 4.5,
            "price": "$",
            "vibe": "Verde, naturaleza"
        }
    ],
    "Microcentro": [
        {
            "name": "Brebaje",
            "type": "bar",
            "address": "Corrientes 1200",
            "rating": 4.5,
            "price": "$$",
            "vibe": "Clásico, tradicional"
        },
        {
            "name": "Café Tortoni Clásico",
            "type": "café",
            "address": "Avenida de Mayo 825",
            "rating": 4.6,
            "price": "$$",
            "vibe": "Histórico, literario"
        }
    ]
}

# Reviews por lugar
REVIEWS = {
    "Fierro Hotel": [
        {"author": "Juan", "rating": 5, "text": "¡Impresionante! El diseño es único y la atmósfera increíble."},
        {"author": "María", "rating": 4, "text": "Bueno pero un poco caro para la cantidad."},
        {"author": "Pedro", "rating": 5, "text": "Volvería mil veces. Staff muy amable."}
    ],
    "Bahrain": [
        {"author": "Sofia", "rating": 5, "text": "Cocktails excelentes, ambiente muy chill."},
        {"author": "Lucas", "rating": 4, "text": "Bueno, pero esperas mucho para que te atiendan."},
    ],
    "Bar Fundacional": [
        {"author": "Ana", "rating": 4, "text": "Buen lugar para empezar la noche en San Telmo."},
        {"author": "Carlos", "rating": 5, "text": "Atmósfera única, gente interesante."},
    ],
    "Fervor": [
        {"author": "Diego", "rating": 5, "text": "La mejor parrilla de Buenos Aires. Imprescindible."},
        {"author": "Luisa", "rating": 5, "text": "Servicio excelente, carne de primera calidad."},
    ]
}


def search_places(query: str, zona: str = None) -> List[Dict]:
    """
    Busca lugares en Buenos Aires.
    
    Args:
        query: Qué buscar (ej: "bares", "restaurantes", "cafés", "Palermo")
        zona: Zona específica (ej: "Palermo", "San Telmo")
    
    Returns:
        Lista de lugares
    """
    results = []
    query_lower = query.lower()
    
    # Buscar zonas en el query
    zonas_encontradas = [z for z in LUGARES_BA.keys() if z.lower() in query_lower]
    
    # Si se especifica zona, usarla; si no, usar las encontradas en query; si no, todas
    if zona:
        zonas_a_buscar = [z for z in LUGARES_BA.keys() if z.lower() == zona.lower()]
    elif zonas_encontradas:
        zonas_a_buscar = zonas_encontradas
    else:
        zonas_a_buscar = list(LUGARES_BA.keys())
    
    # Buscar en las zonas
    for zona_name in zonas_a_buscar:
        for lugar in LUGARES_BA[zona_name]:
            # Filtrar: buscar query en tipo, nombre, o vibe
            if (query_lower in lugar["type"].lower() or 
                query_lower in lugar["name"].lower() or
                query_lower in lugar.get("vibe", "").lower()):
                results.append({
                    **lugar,
                    "zone": zona_name
                })
    
    return results


def get_place_reviews(place_name: str) -> Dict:
    """
    Obtiene reviews de un lugar.
    
    Args:
        place_name: Nombre del lugar
    
    Returns:
        Dict con reviews e info del lugar
    """
    # Buscar el lugar
    for zona in LUGARES_BA.values():
        for lugar in zona:
            if lugar["name"].lower() == place_name.lower():
                reviews = REVIEWS.get(lugar["name"], [
                    {"author": "Usuario", "rating": lugar["rating"], "text": "Buen lugar"}
                ])
                
                avg_rating = sum(r["rating"] for r in reviews) / len(reviews) if reviews else lugar["rating"]
                
                return {
                    "place": lugar["name"],
                    "reviews": reviews,
                    "average_rating": round(avg_rating, 1),
                    "total_reviews": len(reviews),
                    "place_info": lugar
                }
    
    return {
        "status": "not_found",
        "message": f"No se encontró información para '{place_name}'"
    }


def get_popular_places_by_type(place_type: str) -> List[Dict]:
    """
    Obtiene los lugares más populares de un tipo específico.
    
    Args:
        place_type: Tipo de lugar (ej: "bar", "restaurante")
    
    Returns:
        Lista de lugares ordenados por rating
    """
    results = []
    
    for zona, lugares in LUGARES_BA.items():
        for lugar in lugares:
            if lugar["type"].lower() == place_type.lower():
                results.append({
                    **lugar,
                    "zone": zona
                })
    
    # Ordenar por rating descendente
    results.sort(key=lambda x: x["rating"], reverse=True)
    
    return results


def search_by_zone(zona: str) -> List[Dict]:
    """
    Obtiene todos los lugares de una zona.
    
    Args:
        zona: Nombre de la zona
    
    Returns:
        Lista de lugares en la zona
    """
    if zona.lower() in {z.lower() for z in LUGARES_BA.keys()}:
        for z in LUGARES_BA.keys():
            if z.lower() == zona.lower():
                return [
                    {**lugar, "zone": z}
                    for lugar in LUGARES_BA[z]
                ]
    
    return []
