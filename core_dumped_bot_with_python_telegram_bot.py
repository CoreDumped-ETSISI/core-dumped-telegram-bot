#!/usr/bin/env python
# -*- coding: utf-8 -*-
import random

import telegram
import network_scan as scan
import datetime
import time
import os
from logger import get_logger
from data_loader import DataLoader
import sys
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, BaseFilter, RegexHandler

from telegram.error import (TelegramError, Unauthorized, BadRequest,
                            TimedOut, ChatMigrated, NetworkError)


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
        logger.exception("the chat_id of a group has changed, use e.new_chat_id instead")
    except TelegramError:
        logger.exception("There is some error with Telegram")


reload(sys)
sys.setdefaultencoding('utf8')
settings = DataLoader()


class LaughFilter(BaseFilter):
    def filter(self, message):
        result = False
        result = result or 'hahaha' in message.text.lower()
        result = result or 'jajaja' in message.text.lower()
        result = result or 'me despollo' in message.text.lower()
        result = result or 'me descojono' in message.text.lower()
        return result


class PlayaFilter(BaseFilter):
    def filter(self, message):
        result = False
        result = result or 'primera linea de playa' in message.text.lower()
        result = result or u'primera línea de playa' in message.text.lower()
        return result


def load_settings():
    global settings
    settings = DataLoader()


def is_member(username):
    answer = False
    for member in settings.members:
        answer = answer or username == member
    return answer


def help(bot, update):
    log_message(update)
    bot.sendMessage(update.message.chat_id, settings.help_string, parse_mode=telegram.ParseMode.MARKDOWN)


def ask(bot, update):
    log_message(update)
    bot.sendMessage(update.message.chat_id, settings.answers[random.randint(0, int(len(settings.answers) - 1))],
                    parse_mode=telegram.ParseMode.MARKDOWN)


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
					 reply_to_message_id = update.message.message_id)
    reply_markup = telegram.ReplyKeyboardRemove()


def log_message(update):
    logger.info("He recibido: \"" + update.message.text + "\" de " + update.message.from_user.username + " [ID: " + str(
            update.message.chat_id) + "]")


def fotonevera(bot, update):
    log_message(update)

    if update.message.chat_id == settings.admin_chatid or update.message.chat_id == settings.president_chatid:
        take_rtsp_screenshot(0)
        reply_markup = telegram.ReplyKeyboardRemove()
        bot.sendPhoto(chat_id=update.message.chat_id,
                      photo=open(settings.pictures_directory + '/snapshot.jpg', 'rb'), reply_markup=reply_markup)
        logger.debug(settings.pictures_directory + '/snapshot.jpg')


def fotorack(bot, update):
    log_message(update)
    if update.message.chat_id == settings.admin_chatid or update.message.chat_id == settings.president_chatid:
        take_rtsp_screenshot(1)
        reply_markup = telegram.ReplyKeyboardRemove()
        bot.sendPhoto(chat_id=update.message.chat_id,
                      photo=open(settings.pictures_directory + '/snapshot.jpg', 'rb'), reply_markup=reply_markup)
        logger.debug(settings.pictures_directory + 'snapshot.jpg')


def alguien(bot, update):
    global last_room_call
    log_message("NET SCAN " +update)
    msg_id = update.message.message_id
    if datetime.datetime.now() - last_room_call > datetime.timedelta(minutes=10):
        bot.sendMessage(update.message.chat_id,
                        scan.who_is_there()[
                            0] + "\n`No podrás hacer otro /alguien hasta dentro de 10 minutos`.",
                        parse_mode=telegram.ParseMode.MARKDOWN)
        last_room_call = datetime.datetime.now()
    else:
        bot.deleteMessage(msg_id)


def jokes(bot, update):
    global last_joke
    log_message("JOKES " + update)
    if datetime.datetime.now() - last_joke > datetime.timedelta(minutes=60):
        bot.sendMessage(update.message.chat_id, jokes[random.randint(0, int(len(jokes) - 1))])
        last_joke = datetime.datetime.now()


def reload(bot, update):
    log_message("RELOAD " +update)
    if update.message.chat_id == settings.president_chatid:
        load_settings()
        bot.send_message(chat_id=update.message.chat_id, text="Datos cargados")

    # loop del bot


def playa(bot, update):
    log_message("PLAYA " +update)
    bot.sendSticker(update.message.chat_id, u'CAADBAADyAADD2LqAAEgnSqFgod7ggI')


def name_changer(bot, job):
    logger.info("Starting scheduled network scan.")
    try:
        if scan.is_someone_there():
            bot.setChatTitle(settings.public_chatid, u">CORE DUMPED_: \U00002705 Abierto")
            logger.info("Hay alguien.")
        else:
            bot.setChatTitle(settings.public_chatid, u">CORE DUMPED_: \U0000274C Cerrado")
            logger.info("No hay nadie.")
    except Exception as ex:
        logger.exception("Error al actualizar el nombre del grupo Core Dumped.")


if __name__ == "__main__":
    print("Core Dumped Bot: Starting...")

    logger = get_logger("bot_starter", True)
    load_settings()

    last_room_call = datetime.datetime.now() - datetime.timedelta(minutes=10);
    last_joke = datetime.datetime.now() - datetime.timedelta(minutes=60);

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
        dispatcher.add_handler(CommandHandler('reload', reload))
        dispatcher.add_handler(MessageHandler(LaughFilter(), jokes))
        dispatcher.add_handler(MessageHandler(PlayaFilter(), playa))
        dispatcher.add_handler(RegexHandler("(ja)+", jokes))
        dispatcher.add_handler(MessageHandler(Filters.text, playa))
        dispatcher.add_error_handler(error_callback)
    except Exception as ex:
        logger.exception("Error al conectar con la API de Telegram.")
        quit()

    try:
        jobs = updater.job_queue
        job_name_changer = jobs.run_repeating(name_changer, 15 * 60, 30)
        logger.info("Iniciando jobs")
    except Exception as ex:
        logger.exception("Error al cargar la job list")

    updater.start_polling()
    logger.info("Core Dumped Bot: Estoy escuchando.")

    while 1:
        time.sleep(5)
