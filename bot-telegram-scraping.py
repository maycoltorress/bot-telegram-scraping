from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, WebDriverException
from selenium.webdriver.chrome.options import Options
import os
PORT = int(os.environ.get('PORT', 5000))

from telegram import MessageEntity
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from time import time, sleep

TOKEN = '1200803966:AAE2lZYxw7k7sj4z2iU6mQPwXx6H3x-io9E'

  

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


def cmd_comandos(bot, update):
    '''Manejador comando /comandos'''
    # Preparamos el texto que queremos enviar
    bot_msg = "Comandos disponibles:\n" \
              "- /start\n" \
              "- /comandos\n" \
              "- /kb <N° de tatjeta>\n"
    # Respondemos al mensaje recibido (aqui no hace falta determinar cual es el ID del chat, ya que 
    # "update" contiene dicha informacion y lo que vamos es a responder)
    update.message.reply_text(bot_msg)


def cmd_kb(bot, update, args):
    '''Manejador comando /kb'''
    # Obtenemos el ID de chat
    chat_id = update.message.chat_id
    # Si el comando decir presenta argumentos
    if len(args) > 0:

        try:
            CHROMEDRIVER_PATH = os.getenv('CHROMEDRIVER_PATH')
            GOOGLE_CHROME_BIN = os.getenv('GOOGLE_CHROME_BIN')
            # Enviar el mensaje con el Bot
            options = Options()
            options.binary_location = GOOGLE_CHROME_BIN
            options.add_argument('--disable-gpu')
            options.add_argument('--no-sandbox')
            options.headless = True
            
            bot.send_message(chat_id, "pasa por el try")
            driver = webdriver.Chrome(executable_path=CHROMEDRIVER_PATH, chrome_options=options)
            
            # Scraping
            url = 'http://192.168.200.226/kanboard-1.2.7/public/task/'+ args[0] +'/ca8a96eba8157552d6b59f64ea302d340865cfcb694aaf78326e19b4e2ac' #args[0] contiene el n° de la tarjeta
            driver.get(url)
            el = driver.find_element_by_class_name('comments') #sacar los comentarios de la tarjeta
            msg = el.text
            
            #si no tiene comentarios la tarjeta
            if msg == "":
                bot_msg = "Esta tarjeta no tiene comentarios."

            #Se comentan los caracteres vacíos para que no de error al momento de ejecutar
            else:
              bot_msg = msg.replace("_", "\\_").replace("*", "\\*").replace("[", "\\[").replace("`", "\\`")
        
        except Exception as e:
            bot_msg = str(e)  
        #except:
        #  bot_msg = "Tarjeta no encontrada, favor intente nuevamente."
        
    else:
        bot_msg = "El comando /kb tiene que incluir el N° de tarjeta."
    
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
    dp.add_handler(CommandHandler("comandos", cmd_comandos))
    dp.add_handler(CommandHandler("kb", cmd_kb, pass_args=True))
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
    updater.bot.setWebhook('https://botqa.herokuapp.com/' + TOKEN)
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
