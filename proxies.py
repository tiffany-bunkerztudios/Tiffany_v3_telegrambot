import requests
import re
import random
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ProxyFetcher:
    def __init__(self):
        self.proxy_sources = [
            'https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all',
            'https://api.proxyscrape.com/v2/?request=getproxies&protocol=socks4&timeout=10000&country=all',
            'https://api.proxyscrape.com/v2/?request=getproxies&protocol=socks5&timeout=10000&country=all',
            'https://www.proxy-list.download/api/v1/get?type=http',
            'https://www.proxy-list.download/api/v1/get?type=https'
        ]
        
    def fetch_proxies(self, proxy_type='http'):
        """Obtiene proxies de diferentes fuentes"""
        all_proxies = set()
        
        for source in self.proxy_sources:
            try:
                response = requests.get(source, timeout=10)
                if response.status_code == 200:
                    proxies = response.text.strip().split('\n')
                    # Filtrar proxies válidos
                    for proxy in proxies:
                        proxy = proxy.strip()
                        if self.is_valid_proxy(proxy):
                            all_proxies.add(proxy)
            except Exception as e:
                logger.error(f"Error fetching from {source}: {e}")
                continue
        
        return list(all_proxies)[:100]  # Limitar a 100 proxies
    
    def is_valid_proxy(self, proxy):
        """Verifica si un proxy tiene formato válido"""
        pattern = r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{1,5}$'
        return re.match(pattern, proxy) is not None
    
    def format_proxies_message(self, proxies, proxy_type='HTTP'):
        """Formatea los proxies para enviar por Telegram"""
        if not proxies:
            return "No se encontraron proxies disponibles en este momento."
        
        message = f"🔒 *Lista de Proxies {proxy_type}*\n"
        message += f"📅 Actualizado: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
        message += f"📊 Total: {len(proxies)} proxies\n\n"
        
        # Agrupar proxies en bloques
        chunk_size = 10
        for i in range(0, min(len(proxies), 50), chunk_size):  # Máximo 50 proxies
            chunk = proxies[i:i+chunk_size]
            message += "```\n"
            for proxy in chunk:
                message += f"{proxy}\n"
            message += "```\n\n"
        
        message += f"⚠️ *Nota:* Estos proxies son públicos, úsalos con responsabilidad.\n"
        message += "🔧 Para probar: `curl --proxy http://IP:PORT http://ifconfig.me`"
        
        return message
    
    def get_random_proxies(self, count=10):
        """Obtiene una selección aleatoria de proxies"""
        all_proxies = self.fetch_proxies()
        if len(all_proxies) > count:
            return random.sample(all_proxies, count)
        return all_proxies
