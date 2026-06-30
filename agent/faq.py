"""
FAQ Manager con ChromaDB
Almacena y busca FAQs sobre Buenos Aires
"""

import chromadb
from pathlib import Path

# Inicializar ChromaDB con nueva API
DB_PATH = Path(__file__).parent.parent / "chroma_data"
DB_PATH.mkdir(exist_ok=True)

# Nueva API de ChromaDB (versión 0.4+)
client = chromadb.PersistentClient(path=str(DB_PATH))
faq_collection = client.get_or_create_collection(name="salidas_faq")


# FAQs de ejemplo sobre Buenos Aires
FAQS = [
    {
        "id": "1",
        "question": "¿Dónde puedo encontrar las mejores medialunas?",
        "answer": "Las mejores medialunas están en panaderías tradicionales. Café Tortoni, Confitería del Molino y Persicco son excelentes."
    },
    {
        "id": "2",
        "question": "¿Cuál es el mejor horario para visitar la Boca?",
        "answer": "La Boca es hermosa de día (10-17hs) para ver Caminito y el arte. Por la noche hay muchos restaurantes con tango."
    },
    {
        "id": "3",
        "question": "¿Dónde puedo ver un show de tango?",
        "answer": "Bares con tango: Piazzolla (La Boca), Café Tortoni (San Telmo). También El Querandí (Monserrat)."
    },
    {
        "id": "4",
        "question": "¿Cuáles son las estaciones del subte más importantes?",
        "answer": "Línea A (Subte clásico): 9 de Julio, Congreso. Línea D: Catedral, Retiro. Línea B: Leandro N. Alem."
    },
    {
        "id": "5",
        "question": "¿Dónde puedo hacer compras?",
        "answer": "Palermo Viejo, Calle Florida (peatonal), Galerías Pacífico, Patio Bullrich (Recoleta)."
    },
    {
        "id": "6",
        "question": "¿Cuál es la mejor zona para salir de noche?",
        "answer": "Palermo Viejo (bares trendy), San Telmo (histórico + tango), La Boca (turístico), Almagro (craft beer)."
    },
    {
        "id": "7",
        "question": "¿Dónde puedo ir a comer asado?",
        "answer": "Fervor (Recoleta, top), Fierro (Palermo), El Hipolito (Liniers), La Cabrera (Palermo)."
    },
    {
        "id": "8",
        "question": "¿Cuáles son los horarios de comida en Buenos Aires?",
        "answer": "Desayuno: 7-10hs. Almuerzo: 12-15hs. Merienda: 17-19hs. Cena: 20-23hs (después es muy tarde)."
    },
    {
        "id": "9",
        "question": "¿Cuál es el clima típico de Buenos Aires?",
        "answer": "Primavera/Otoño: 15-25°C (ideal). Verano: 25-35°C. Invierno: 8-15°C. Lluvia todo el año."
    },
    {
        "id": "10",
        "question": "¿Dónde está el Cementerio de La Recoleta?",
        "answer": "En Recoleta, Junín 1760. Es un museo histórico donde están enterrados personajes famosos (Eva Perón, etc)."
    }
]


def init_faq_db():
    """Inicializa la base de FAQs en ChromaDB"""
    # Verificar si ya tiene datos
    if faq_collection.count() > 0:
        return
    
    # Agregar FAQs
    for faq in FAQS:
        faq_collection.add(
            ids=[faq["id"]],
            documents=[faq["question"] + " " + faq["answer"]],
            metadatas=[{"type": "faq", "question": faq["question"]}]
        )
    
    print(f"✅ {len(FAQS)} FAQs cargadas en ChromaDB")


def search_faq(query: str, top_k: int = 3) -> list:
    """
    Busca FAQs relevantes por similaridad.
    
    Args:
        query: Pregunta del usuario
        top_k: Cantidad de resultados
    
    Returns:
        Lista de FAQs relevantes
    """
    try:
        init_faq_db()
        results = faq_collection.query(
            query_texts=[query],
            n_results=top_k
        )
        
        if results and results["documents"]:
            return [
                {
                    "score": score,
                    "text": doc
                }
                for doc, score in zip(results["documents"][0], results["distances"][0])
            ]
        return []
    except Exception as e:
        print(f"Error en búsqueda FAQ: {e}")
        return []


def get_faq_response(query: str) -> str:
    """Obtiene respuesta FAQ si existe"""
    faqs = search_faq(query, top_k=1)
    
    if faqs and faqs[0]["score"] < 0.5:  # Threshold de similaridad
        return f"📚 **FAQ:** {faqs[0]['text'][:200]}..."
    
    return None


# Inicializar al importar
init_faq_db()
