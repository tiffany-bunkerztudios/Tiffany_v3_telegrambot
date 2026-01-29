import os
from dotenv import load_dotenv

load_dotenv()

# Configuración del Bot
BOT_TOKEN = os.getenv('BOT_TOKEN', 'TU_TOKEN_AQUI')
ADMIN_IDS = [int(id) for id in os.getenv('ADMIN_IDS', '').split(',') if id]

# Configuración de Feeds
FEEDS = {
    'hackernews': 'https://hnrss.org/frontpage',
    'zeroclickzero': 'https://feeds.feedburner.com/TheHackersNews',
    'securityweek': 'https://feeds.feedburner.com/securityweek',
    'threatpost': 'https://threatpost.com/feed/'
}

# Configuración de Proxies
PROXY_SOURCES = [
    'https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all',
    'https://www.proxy-list.download/api/v1/get?type=http'
]

# Configuración de la Personalidad
LAOZHANG_API_URL = os.getenv('LAOZHANG_API_URL', 'https://api.laozhang.com/chat')
LAOZHANG_API_KEY = os.getenv('LAOZHANG_API_KEY', '')

# Configuración de Grupos
GROUPS_CONFIG = {
    'inactivity_timeout': 300,  # 5 minutos en segundos
    'max_proxies_per_message': 20,
    'max_news_per_message': 5
}

# Saludos y despedidas
SALUDOS = [
    "¡Bienvenido {nombre}! 👋",
    "¡Hola {nombre}! Bienvenido al grupo de ciberseguridad 🛡️",
    "¡Saludos {nombre}! ¿Listo para hablar de seguridad informática? 🔐"
]

DESPEDIDAS = [
    "¡Hasta luego {nombre}! 👋",
    "Nos vemos pronto {nombre} 👋",
    "¡Que tengas buen día {nombre}! 👋"
]
