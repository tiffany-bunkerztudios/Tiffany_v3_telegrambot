import json
import random
import requests
import logging
from datetime import datetime, timedelta
import asyncio

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TiffanyPersonality:
    def __init__(self, name="Tiffany"):
        self.name = name
        self.load_phrases()
        self.user_interactions = {}
        self.last_activity = {}
        self.api_available = True
        
    def load_phrases(self):
        """Carga las frases desde el archivo JSON"""
        try:
            with open('frases.json', 'r', encoding='utf-8') as f:
                self.phrases = json.load(f)
        except FileNotFoundError:
            # Frases por defecto si no existe el archivo
            self.phrases = {
                "ciberseguridad": ["Hablando de ciberseguridad..."],
                "general": ["Hola a todos!"]
            }
            logger.warning("Archivo frases.json no encontrado, usando frases por defecto")
    
    async def get_laozhang_response(self, message):
        """Obtiene respuesta de la API de Laozhang"""
        if not self.api_available:
            return None
            
        try:
            headers = {'Authorization': f'Bearer {LAOZHANG_API_KEY}'}
            data = {'message': message, 'bot_name': 'Tiffany'}
            
            response = requests.post(
                LAOZHANG_API_URL,
                headers=headers,
                json=data,
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json().get('response')
            else:
                self.api_available = False
                logger.warning("API de Laozhang no disponible, usando frases locales")
                return None
                
        except Exception as e:
            self.api_available = False
            logger.error(f"Error con API Laozhang: {e}")
            return None
    
    def get_greeting(self, username):
        """Obtiene un saludo para nuevos usuarios"""
        greeting = random.choice([
            f"¡Hola @{username}! 👋 Bienvenido al grupo de ciberseguridad.",
            f"¡Saludos @{username}! 🛡️ ¿Te gusta la ciberseguridad?",
            f"¡Bienvenido @{username}! 🔐 Aquí hablamos de seguridad y tecnología."
        ])
        return greeting
    
    def get_farewell(self, username):
        """Obtiene una despedida para usuarios que se van"""
        farewell = random.choice([
            f"Hasta luego @{username} 👋",
            f"Nos vemos pronto @{username} 👋",
            f"¡Que tengas buen día @{username}! 👋"
        ])
        return farewell
    
    def get_topic_response(self, topic):
        """Obtiene una frase relacionada con un tema"""
        if topic in self.phrases and self.phrases[topic]:
            return random.choice(self.phrases[topic])
        return random.choice(self.phrases.get("general", ["Interesante conversación."]))
    
    def detect_topic(self, message):
        """Detecta el tema de la conversación"""
        message_lower = message.lower()
        
        topics_keywords = {
            "ciberseguridad": ["hack", "seguridad", "virus", "malware", "firewall", "ataque", "brecha", "vulnerabilidad"],
            "tecnologia": ["python", "linux", "windows", "programar", "código", "github", "git"],
            "proxies": ["proxy", "vpn", "ip", "conexión", "anonimato"],
            "noticias": ["noticia", "novedad", "actualidad", "último", "nuevo"]
        }
        
        for topic, keywords in topics_keywords.items():
            if any(keyword in message_lower for keyword in keywords):
                return topic
        
        return "general"
    
    def check_inactivity(self, group_id):
        """Verifica inactividad en el grupo"""
        now = datetime.now()
        last_activity = self.last_activity.get(group_id)
        
        if last_activity:
            inactivity_time = (now - last_activity).seconds
            return inactivity_time > 300  # 5 minutos
        return True
    
    def update_activity(self, group_id):
        """Actualiza el tiempo de última actividad"""
        self.last_activity[group_id] = datetime.now()
    
    def get_inactivity_message(self):
        """Obtiene mensaje para cuando hay inactividad"""
        return random.choice(self.phrases.get("inactividad", [
            "¿Todos ocupados? 😄",
            "Parece que hay silencio por aquí...",
            "¿Nadie quiere hablar de ciberseguridad hoy?"
        ]))
    
    async def respond(self, message, username=None, group_id=None):
        """Genera una respuesta apropiada"""
        if group_id:
            self.update_activity(group_id)
        
        # Intentar con API de Laozhang primero
        if self.api_available:
            api_response = await self.get_laozhang_response(message)
            if api_response:
                return api_response
        
        # Si la API falla, usar sistema local
        topic = self.detect_topic(message)
        
        if "adiós" in message.lower() or "hasta luego" in message.lower():
            return f"Hasta luego @{username} 👋" if username else "Hasta luego 👋"
        
        if "hola" in message.lower() or "buenos días" in message.lower():
            return self.get_greeting(username) if username else "¡Hola a todos! 👋"
        
        return self.get_topic_response(topic)
