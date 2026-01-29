#!/usr/bin/env python3
import logging
from telegram import Update, BotCommand
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
    CallbackContext
)
import asyncio
from datetime import datetime
import schedule
import time
from threading import Thread

from config import BOT_TOKEN, GROUPS_CONFIG
from feeds import NewsFeedFetcher
from proxies import ProxyFetcher
from personality import TiffanyPersonality

# Configurar logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Inicializar componentes
news_fetcher = NewsFeedFetcher()
proxy_fetcher = ProxyFetcher()
tiffany = TiffanyPersonality()

# Diccionario para almacenar últimos mensajes enviados
sent_messages = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Maneja el comando /start"""
    welcome_message = (
        "👋 ¡Hola! Soy *Tiffany*, tu asistente de ciberseguridad.\n\n"
        "🔧 *Comandos disponibles:*\n"
        "• /news - Últimas noticias de ciberseguridad\n"
        "• /hackernews - Noticias de HackerNews\n"
        "• /zeroclick - Noticias de ZeroClickZero\n"
        "• /proxies - Lista de proxies actualizados\n"
        "• /randomproxies - 10 proxies aleatorios\n"
        "• /help - Muestra esta ayuda\n\n"
        "💬 También puedo conversar contigo sobre ciberseguridad y tecnología."
    )
    
    await update.message.reply_text(welcome_message, parse_mode='Markdown')

async def send_news(update: Update, context: ContextTypes.DEFAULT_TYPE, source=None):
    """Envía noticias"""
    chat_id = update.effective_chat.id
    
    # Mensaje de espera
    wait_msg = await update.message.reply_text("📡 Buscando noticias recientes...")
    
    try:
        if source == 'hackernews':
            news = news_fetcher.fetch_hackernews()
            message = news_fetcher.format_news_message(news, "HackerNews")
        elif source == 'zeroclickzero':
            news = news_fetcher.fetch_zeroclickzero()
            message = news_fetcher.format_news_message(news, "ZeroClickZero")
        else:
            # Noticias combinadas
            hn_news = news_fetcher.fetch_hackernews()[:3]
            zcz_news = news_fetcher.fetch_zeroclickzero()[:3]
            all_news = hn_news + zcz_news
            message = news_fetcher.format_news_message(all_news, "Ciberseguridad")
        
        # Editar mensaje original con las noticias
        await context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=wait_msg.message_id,
            text=message,
            parse_mode='Markdown',
            disable_web_page_preview=False
        )
        
    except Exception as e:
        logger.error(f"Error sending news: {e}")
        await context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=wait_msg.message_id,
            text="❌ Error al obtener noticias. Intenta más tarde."
        )

async def send_proxies(update: Update, context: ContextTypes.DEFAULT_TYPE, random_only=False):
    """Envía lista de proxies"""
    chat_id = update.effective_chat.id
    
    wait_msg = await update.message.reply_text("🔍 Buscando proxies actualizados...")
    
    try:
        if random_only:
            proxies = proxy_fetcher.get_random_proxies(10)
            message = proxy_fetcher.format_proxies_message(proxies, "HTTP Aleatorios")
        else:
            proxies = proxy_fetcher.fetch_proxies()
            message = proxy_fetcher.format_proxies_message(proxies, "HTTP/SOCKS")
        
        await context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=wait_msg.message_id,
            text=message,
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logger.error(f"Error sending proxies: {e}")
        await context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=wait_msg.message_id,
            text="❌ Error al obtener proxies. Intenta más tarde."
        )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Maneja mensajes de texto normales"""
    message = update.message.text
    username = update.message.from_user.username
    chat_id = update.effective_chat.id
    
    # Verificar si es un comando
    if message.startswith('/'):
        return
    
    # Detectar saludos/despedidas
    lower_message = message.lower()
    
    # Saludar a nuevos miembros
    if update.message.new_chat_members:
        for member in update.message.new_chat_members:
            if not member.is_bot:
                greeting = tiffany.get_greeting(member.username or member.first_name)
                await update.message.reply_text(greeting)
        return
    
    # Despedir a miembros que se van
    if update.message.left_chat_member:
        if not update.message.left_chat_member.is_bot:
            farewell = tiffany.get_farewell(update.message.left_chat_member.username or update.message.left_chat_member.first_name)
            await update.message.reply_text(farewell)
        return
    
    # Responder a mensajes normales
    response = await tiffany.respond(message, username, chat_id)
    if response and random.random() < 0.3:  # 30% de probabilidad de responder
        await update.message.reply_text(response)

async def scheduled_news(context: CallbackContext):
    """Envía noticias programadas a grupos configurados"""
    job = context.job
    chat_id = job.chat_id
    
    try:
        news = news_fetcher.fetch_hackernews()[:3]
        message = news_fetcher.format_news_message(news, "HackerNews")
        
        await context.bot.send_message(
            chat_id=chat_id,
            text=message,
            parse_mode='Markdown',
            disable_web_page_preview=False
        )
    except Exception as e:
        logger.error(f"Error in scheduled news: {e}")

async def check_inactivity(context: CallbackContext):
    """Verifica inactividad en grupos"""
    job = context.job
    chat_id = job.chat_id
    
    if tiffany.check_inactivity(chat_id):
        message = tiffany.get_inactivity_message()
        await context.bot.send_message(chat_id=chat_id, text=message)

async def setup_commands(application: Application):
    """Configura los comandos del bot"""
    commands = [
        BotCommand("start", "Inicia el bot"),
        BotCommand("news", "Últimas noticias de ciberseguridad"),
        BotCommand("hackernews", "Noticias de HackerNews"),
        BotCommand("zeroclick", "Noticias de ZeroClickZero"),
        BotCommand("proxies", "Lista completa de proxies"),
        BotCommand("randomproxies", "10 proxies aleatorios"),
        BotCommand("help", "Muestra la ayuda")
    ]
    
    await application.bot.set_my_commands(commands)

async def post_init(application: Application):
    """Tareas posteriores a la inicialización"""
    await setup_commands(application)
    
    # Programar tareas para grupos específicos (configura esto según tus grupos)
    # Ejemplo: Enviar noticias cada 6 horas
    # context.job_queue.run_repeating(scheduled_news, interval=21600, first=10, chat_id=TU_GRUPO_ID)
    
    # Verificar inactividad cada 5 minutos
    # context.job_queue.run_repeating(check_inactivity, interval=300, first=60, chat_id=TU_GRUPO_ID)

def run_schedule():
    """Ejecuta el planificador en un hilo separado"""
    while True:
        schedule.run_pending()
        time.sleep(1)

def main():
    """Función principal"""
    # Crear aplicación
    application = Application.builder().token(BOT_TOKEN).post_init(post_init).build()
    
    # Comandos
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("news", lambda u, c: send_news(u, c)))
    application.add_handler(CommandHandler("hackernews", lambda u, c: send_news(u, c, 'hackernews')))
    application.add_handler(CommandHandler("zeroclick", lambda u, c: send_news(u, c, 'zeroclickzero')))
    application.add_handler(CommandHandler("proxies", lambda u, c: send_proxies(u, c)))
    application.add_handler(CommandHandler("randomproxies", lambda u, c: send_proxies(u, c, True)))
    application.add_handler(CommandHandler("help", start))
    
    # Mensajes de texto
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Iniciar hilo para schedule
    schedule_thread = Thread(target=run_schedule, daemon=True)
    schedule_thread.start()
    
    # Iniciar el bot
    logger.info("Bot iniciado...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
