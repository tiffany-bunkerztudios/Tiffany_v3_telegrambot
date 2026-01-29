import feedparser
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NewsFeedFetcher:
    def __init__(self):
        self.last_fetch = {}
        
    def fetch_hackernews(self):
        """Obtiene noticias de HackerNews"""
        try:
            feed = feedparser.parse('https://hnrss.org/frontpage')
            news_items = []
            
            for entry in feed.entries[:10]:  # Últimas 10 noticias
                item = {
                    'title': entry.title,
                    'link': entry.link,
                    'published': entry.published if hasattr(entry, 'published') else '',
                    'source': 'HackerNews'
                }
                news_items.append(item)
                
            return news_items
        except Exception as e:
            logger.error(f"Error fetching HackerNews: {e}")
            return []
    
    def fetch_zeroclickzero(self):
        """Obtiene noticias de Zero Click Zero"""
        try:
            feed = feedparser.parse('https://feeds.feedburner.com/TheHackersNews')
            news_items = []
            
            for entry in feed.entries[:10]:
                item = {
                    'title': entry.title,
                    'link': entry.link,
                    'published': entry.published if hasattr(entry, 'published') else '',
                    'summary': entry.summary[:200] + '...' if hasattr(entry, 'summary') else '',
                    'source': 'ZeroClickZero'
                }
                news_items.append(item)
                
            return news_items
        except Exception as e:
            logger.error(f"Error fetching ZeroClickZero: {e}")
            return []
    
    def fetch_security_forums(self):
        """Obtiene noticias de foros de seguridad"""
        forums = []
        # Aquí puedes añadir más foros
        try:
            # Ejemplo: SecurityWeek RSS
            feed = feedparser.parse('https://feeds.feedburner.com/securityweek')
            for entry in feed.entries[:5]:
                forums.append({
                    'title': entry.title,
                    'link': entry.link,
                    'source': 'SecurityWeek'
                })
        except Exception as e:
            logger.error(f"Error fetching forums: {e}")
            
        return forums
    
    def format_news_message(self, news_items, source=None):
        """Formatea las noticias para enviar por Telegram"""
        if not news_items:
            return "No se encontraron noticias recientes."
        
        message = f"📰 *Últimas noticias de {source if source else 'Ciberseguridad'}*\n\n"
        
        for i, item in enumerate(news_items[:5], 1):
            title = item['title'].replace('*', '\\*').replace('_', '\\_')
            message += f"{i}. *{title}*\n"
            if 'summary' in item:
                message += f"   {item['summary']}\n"
            message += f"   🔗 [Leer más]({item['link']})\n\n"
        
        message += f"\n📊 Total: {len(news_items)} noticias"
        return message
