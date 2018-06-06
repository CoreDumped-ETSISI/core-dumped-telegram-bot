#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
import string
import random
import telegram
import network_scan as scan
import datetime
import time
import os
from logger import get_logger
from data_loader import DataLoader
import sys
from telegram.ext import Updater, CommandHandler, MessageHandler, BaseFilter
from random import normalvariate
from telegram.error import (TelegramError, Unauthorized, BadRequest,
                            TimedOut, ChatMigrated, NetworkError)

reload(sys)
sys.setdefaultencoding('utf8')


def error_callback(bot, update, error):
    try:
        raise error
    except Unauthorized:
        logger.exception("remove update.message.chat_id from conversation list")
    except BadRequest:
        logger.exception("handle malformed requests - read more below!")
    except TimedOut:
        logger.exception("handle slow connection problems")
    except NetworkError:
        logger.exception("handle other connection problems")
    except ChatMigrated as e:
        logger.exception("the chat_id of a group has changed, use " + e.new_chat_id + " instead")
    except TelegramError:
        logger.exception("There is some error with Telegram")


class LaughFilter(BaseFilter):
    def filter(self, message):
        lower_message = str(message.text).lower()
        regex = r"\b([aeiou]*(?:[hj]+[aeiou]+){2,}[hj]?(\W|$))|((?:l+o+)+l+)\b"

        return re.match(re.compile(regex), lower_message) != None


class PlayaFilter(BaseFilter):
    def filter(self, message):
        lower_message = str(message.text).lower()
        
        return lower_message in ['primera linea de playa', 'primera línea de playa']


def load_settings():
    global settings
    global last_function_calls
    settings = DataLoader()
    last_function_calls = {}


def is_member(bot, user_id):
    try:
        return bot.get_chat_member(chat_id=settings.admin_chatid,
                                   user_id=user_id).status in ['creator', 'administrator', 'member']
    except BadRequest:
        return False


def is_call_available(name, chat_id, cooldown):
    global last_function_calls
    now = datetime.datetime.now()
    cooldown_time = datetime.datetime.now() - datetime.timedelta(minutes=cooldown)
    if name in last_function_calls.keys():
        if chat_id in last_function_calls[name].keys():
            if last_function_calls[name][chat_id] > cooldown_time:
                last_function_calls[name][chat_id] = now
                return False
            else:
                last_function_calls[name][chat_id] = now
                return True
        else:
            last_function_calls[name] = {chat_id: now}
            return True
    else:
        last_function_calls[name] = {chat_id: now}
        return True


def help(bot, update):
    log_message(update)
    bot.sendMessage(update.message.chat_id, settings.help_string, parse_mode=telegram.ParseMode.MARKDOWN, reply_to_message_id=update.message.message_id)


def ask(bot, update):
    log_message(update)
    bot.send_chat_action(chat_id=update.message.chat_id, action='typing')
    selected_string = settings.answers[random.randint(0, int(len(settings.answers) - 1))]
    human_texting(selected_string)
    if random.randint(0,100) >= 95:
        tempLetterPos = random.randint(0,len(selected_string)-1) 
        tempAsk = selected_string[:tempLetterPos] + random.choice(string.ascii_letters) +  selected_string[tempLetterPos:]
        tempMessage = bot.sendMessage(update.message.chat_id, tempAsk, reply_to_message_id=update.message.message_id)
        bot.send_chat_action(chat_id=update.message.chat_id, action='typing')
        human_texting(selected_string)
        bot.edit_message_text(selected_string, chat_id=update.message.chat_id, message_id=tempMessage.message_id)
    else:
        bot.sendMessage(update.message.chat_id, selected_string, parse_mode=telegram.ParseMode.MARKDOWN,
						reply_to_message_id=update.message.message_id)


def take_rtsp_screenshot(cam_id):
    os.system('rm ' + settings.pictures_directory + '/snapshot.jpg')
    os.system(
        'ffmpeg -i \"' + settings.cam_url(
            cam_id) + '\" -y -f image2  -frames 1 ' + settings.pictures_directory + '/snapshot.jpg')


def foto(bot, update):
    log_message(update)
    teclado_fotos = [['/fotonevera'], ['/fotorack']]
    reply_markup = telegram.ReplyKeyboardMarkup(teclado_fotos)
    bot.send_message(chat_id=update.message.chat_id,
                     text="¿Qué foto quieres?",
                     reply_markup=reply_markup,
                     reply_to_message_id=update.message.message_id)


def log_message(update):
    logger.info("He recibido: \"" + update.message.text + "\" de " + update.message.from_user.username + " [ID: " + str(
        update.message.chat_id) + "]")


def fotonevera(bot, update):
    log_message(update)

    if update.message.chat_id == settings.admin_chatid or update.message.chat_id == settings.president_chatid:
        bot.send_chat_action(chat_id=update.message.chat_id, action='upload_photo')
        take_rtsp_screenshot(0)
        reply_markup = telegram.ReplyKeyboardRemove()
        bot.sendPhoto(chat_id=update.message.chat_id,
                      photo=open(settings.pictures_directory + '/snapshot.jpg', 'rb'), reply_markup=reply_markup)
        logger.debug(settings.pictures_directory + '/snapshot.jpg')


def fotorack(bot, update):
    log_message(update)
    if update.message.chat_id == settings.admin_chatid or update.message.chat_id == settings.president_chatid:
        bot.send_chat_action(chat_id=update.message.chat_id, action='upload_photo')
        take_rtsp_screenshot(1)
        reply_markup = telegram.ReplyKeyboardRemove()
        bot.sendPhoto(chat_id=update.message.chat_id,
                      photo=open(settings.pictures_directory + '/snapshot.jpg', 'rb'), reply_markup=reply_markup)
        logger.debug(settings.pictures_directory + 'snapshot.jpg')


def alguien(bot, update):
    if is_call_available("alguien", update.message.chat_id, 15):
        bot.send_chat_action(chat_id=update.message.chat_id, action='typing')
        bot.sendMessage(update.message.chat_id,
                        scan.who_is_there()[
                            0] + "\n`No podrás hacer otro /alguien hasta dentro de 15 minutos`.",
                        parse_mode="Markdown", reply_to_message_id=update.message.message_id)
    else:
        bot.deleteMessage(update.message.message_id)


def human_texting(string):
    wait_time = len(string) * normalvariate(0.1, 0.05)
    if wait_time > 8:
        wait_time = 8
    time.sleep(wait_time)


def jokes(bot, update):
    chat_id = update.message.chat.id
    if is_call_available("joke", chat_id, 30) and random.randint(0,100) >= 30:
        bot.send_chat_action(chat_id=update.message.chat_id, action='typing')
        selected_joke = settings.jokes[random.randint(0, int(len(settings.jokes) - 1))]
        human_texting(selected_joke)

        if random.randint(0,100) >= 95:
            tempLetterPos = random.randint(0,len(selected_joke)-1) 
            tempJoke = selected_joke[:tempLetterPos] + random.choice(string.ascii_letters) +  selected_joke[tempLetterPos:]
            tempMessage = bot.sendMessage(update.message.chat_id, tempJoke,
                        reply_to_message_id=update.message.message_id)
            bot.send_chat_action(chat_id=update.message.chat_id, action='typing')
            human_texting(selected_joke)
            bot.edit_message_text(selected_joke, chat_id=update.message.chat_id, message_id=tempMessage.message_id)
        else:
            bot.sendMessage(update.message.chat_id, selected_joke,
                        reply_to_message_id=update.message.message_id)


def reload_data(bot, update):
    if update.message.from_user.id == settings.president_chatid:
        load_settings()
        bot.send_message(chat_id=update.message.chat_id, text="Datos cargados",
                        reply_to_message_id=update.message.message_id)


def playa(bot, update):
    if is_call_available("playa", update.message.chat.id, 10) and random.randint(0,100) >= 30:
        bot.sendSticker(update.message.chat_id, u'CAADBAADyAADD2LqAAEgnSqFgod7ggI', reply_to_message_id=update.message.message_id)


def name_changer(bot, job):
    logger.info("Starting scheduled network scan.")
    try:
        if scan.is_someone_there():
            bot.setChatTitle(settings.public_chatid, u">CORE DUMPED_: \U00002705 Abierto")
            logger.info("Hay alguien.")
        else:
            bot.setChatTitle(settings.public_chatid, u">CORE DUMPED_: \U0000274C Cerrado")
            logger.info("No hay nadie.")
    except:
        logger.exception("Error al actualizar el nombre del grupo Core Dumped.")


if __name__ == "__main__":
    print("Core Dumped Bot: Starting...")

    logger = get_logger("bot_starter", True)
    load_settings()

    try:
        logger.info("Conectando con la API de Telegram.")
        updater = Updater(settings.telegram_token)
        dispatcher = updater.dispatcher
        dispatcher.add_handler(CommandHandler('help', help))
        dispatcher.add_handler(CommandHandler('ask', ask))
        dispatcher.add_handler(CommandHandler('foto', foto))
        dispatcher.add_handler(CommandHandler('fotonevera', fotonevera))
        dispatcher.add_handler(CommandHandler('fotorack', fotorack))
        dispatcher.add_handler(CommandHandler('alguien', alguien))
        dispatcher.add_handler(CommandHandler('reload', reload_data))
        joke_filter = LaughFilter()
        dispatcher.add_handler(MessageHandler(joke_filter, jokes))
        # Inside joke
        playa_filter = PlayaFilter()
        dispatcher.add_handler(MessageHandler(playa_filter, playa))
        dispatcher.add_error_handler(error_callback)
    except Exception as ex:
        logger.exception("Error al conectar con la API de Telegram.")
        quit()

    try:
        jobs = updater.job_queue
        job_name_changer = jobs.run_repeating(name_changer, 15 * 60, 300)
        logger.info("Iniciando jobs")
    except Exception as ex:
        logger.exception("Error al cargar la job list. Ignorando jobs...")

    updater.start_polling()
    logger.info("Core Dumped Bot: Estoy escuchando.")
    updater.idle()
