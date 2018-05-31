#!/usr/bin/env python
# -*- coding: utf-8 -*-
from logger import get_logger
import json

logger = get_logger("data_loader")


class DataLoader:

    def __init__(self):
        global data_and_settings
        try:
            json_file = open('data-and-settings.json')
            data_and_settings = json.load(json_file, encoding="utf-8")
        except:
            logger.exception("Error al cargar el JSON de configuración")
        else:
            logger.info("JSON cargado con éxito")
            self.telegram_token = data_and_settings["telegram token"]
            self.answers = data_and_settings["answers"]
            self.help_string = data_and_settings["help"]
            self.jokes = data_and_settings["jokes"]
            self.devices = data_and_settings["devices"]
            self.members = data_and_settings["members"]
            self.working_directory = data_and_settings["working directory"]
            self.pictures_directory = data_and_settings["pictures directory"]
            self.cam_urls = data_and_settings["cams urls"]
            self.network = data_and_settings["network"]
            self.admin_password = data_and_settings["admin password"]
            self.public_chatid = data_and_settings["public group chat id"]
            self.admin_chatid = data_and_settings["admin group chat id"]
            self.president_chatid = data_and_settings["president chat id"]

    @property
    def telegram_token(self):
        return self.telegram_token

    @property
    def president_chatid(self):
        return self.president_chatid

    @property
    def answers(self):
        return self.answers

    @property
    def help_string(self):
        return self.help_string

    @property
    def jokes(self):
        return self.jokes

    @property
    def devices(self):
        return self.devices

    @property
    def members(self):
        return self.members

    @property
    def working_directory(self):
        return self.working_directory

    @property
    def cam_urls(self):
        return self.cam_urls

    @property
    def network(self):
        return self.network

    @property
    def admin_password(self):
        return self.admin_password

    @property
    def admin_chatid(self):
        return self.admin_chatid

    @property
    def public_chatid(self):
        return self.public_chatid

    @property
    def pictures_directory(self):
        return self.pictures_directory

    def cam_url(self, cam_id=0):
        return self.cam_urls[cam_id]
