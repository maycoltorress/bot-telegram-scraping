from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, WebDriverException
from selenium.webdriver.chrome.options import Options
import os

from time import time, sleep
from telegram import MessageEntity
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

TOKEN = '1379951431:AAGI2iIux8xUPIa0PTQy-w01nBlFBtjw2GM'

def cmd_start(bot, update):
    '''Manejador comando /start'''
    # Obtenemos el ID y el tipo de chat
    chat_id = update.message.chat_id
    chat_type = update.message.chat.type
    bot_msg = "Comando start recibido.\n" \
              "\n" \
              "- Chat ID: {}\n" \
              "- Tipo de Chat: {}".format(chat_id, chat_type)
    # Si no estamos en un chat privado
    if chat_type != "private":
        # Intentamos obtener el titulo y el alias del chat
        chat_title = update.message.chat.title
        if chat_title:
            bot_msg = "{}\n- Titulo del Chat: {}".format(bot_msg, chat_title)
        else:
            bot_msg = "{}\n- Titulo del Chat: [No disponible]".format(bot_msg)
        chat_link = update.message.chat.username
        if chat_link:
            bot_msg = "{}\n- Link del Chat: {}".format(bot_msg, chat_title)
        else:
            bot_msg = "{}\n- Link del Chat: [No disponible]".format(bot_msg)
    # Enviar el mensaje con el Bot
    bot.send_message(chat_id, bot_msg)


def cmd_help(bot, update):
    '''Manejador comando /help'''
    # Preparamos el texto que queremos enviar
    bot_msg = "Comandos disponibles:\n" \
              "- /start\n" \
              "- /help\n" \
              "- /producto\n"
    # Respondemos al mensaje recibido (aqui no hace falta determinar cual es el ID del chat, ya que 
    # "update" contiene dicha informacion y lo que vamos es a responder)
    update.message.reply_text(bot_msg)


def cmd_producto(bot, update, args):
    '''Manejador comando /producto'''
    # Obtenemos el ID de chat
    chat_id = update.message.chat_id
    # Si el comando decir presenta argumentos
    if len(args) > 0:

        try:
            # Enviar el mensaje con el Bot
            CHROMEDRIVER_PATH = os.getenv('CHROMEDRIVER_PATH')
            GOOGLE_CHROME_BIN = os.getenv('GOOGLE_CHROME_BIN')
            options = Options()
            options.binary_location = GOOGLE_CHROME_BIN
            options.add_argument('--disable-gpu')
            options.add_argument('--no-sandbox')
            options.headless = True
            driver = webdriver.Chrome(executable_path=CHROMEDRIVER_PATH, chrome_options=options)
            
            # Scraping
            url = 'https://www.magasa.cl/producto/aparador-tv-'+ args[0] #args[0] contiene el producto
            driver.get(url)
            el = driver.find_element_by_tag_name('bdi') #sacar los comentarios de la tarjeta
            msg = el.text

            
            #si no tiene comentarios la tarjeta
            if msg == "":
                bot_msg = "Este producto no tiene precio."

            #Se comentan los caracteres vacíos para que no de error al momento de ejecutar
            else:  
                bot_msg = msg.replace("_", "\\_").replace("*", "\\*").replace("[", "\\[").replace("`", "\\`")

        except Exception as e:
            bot_msg = str(e)
        
    else:
        bot_msg = "El comando /producto tiene que incluir el producto."
    
    bot.send_message(chat_id, bot_msg) #Se imprime el mensaje
    

def msg_nocmd(bot, update):
    '''Manejador para todos aquellos mensajes que no son comandos'''
    # Obtenemos el texto del mensaje recibido
    text = update.message.text
    # Si en el mensaje aparece la palabra clave "bot", responder con un mensaje
    if " bot " in text:
        bot_msg = "En este mensaje se ha dicho la palabra \"bot\"."
        update.message.reply_text(bot_msg)

####################################################################################################

# Funcion Main #

def main():
    '''Funcion Main'''
    # Crear el manejador de eventos (updater) y el dispatcher para el Bot, dado su token
    updater = Updater(TOKEN)
    dp = updater.dispatcher
    # Establecer en el dispatcher un manejador para cada comando a recibir
    dp.add_handler(CommandHandler("start", cmd_start))
    dp.add_handler(CommandHandler("help", cmd_help))
    dp.add_handler(CommandHandler("producto", cmd_producto, pass_args=True))
    # Establecer en el dispatcher un manejador para mensajes a recibir que no sean comandos. Para 
    # ello se hacen uso de los filtros, es decir, el manejador saltara si se detecta alguno de 
    # estos tipos de mensajes (texto, imagen, audio...)
    dp.add_handler(MessageHandler(Filters.text | Filters.photo | Filters.audio | Filters.voice | \
        Filters.video | Filters.sticker | Filters.document | Filters.location | Filters.contact, \
        msg_nocmd))
    # Lanzar el Bot ignorando los mensajes que se hayan recibido cuando estaba inactivo (clean=True)
    #updater.start_polling(clean=True)
    updater.start_webhook(listen="0.0.0.0",
                          port=int(PORT),
                          url_path=TOKEN)
    updater.bot.setWebhook('https://bot-telegram-scraping.herokuapp.com/' + TOKEN)
    
    # Bucle infinito con el cual se muestra como enviar mensajes del Bot cada minuto
    bot = updater.bot
    t_inicial = time()
    while True:
        # Si el tiempo actual es mayor al tiempo inicial mas 60s
        if time() >= t_inicial + 60:
            # Enviar el mensaje y establecer como tiempo inicial el actual
            bot.send_message(chat_id, "Acaba de pasar 1 minuto.")
            t_inicial = time()
        # Esperamos 10s (liberar el uso de CPU por parte de este bucle)
        sleep(10)


if __name__ == '__main__':
    main()




