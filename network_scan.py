#!/usr/bin/env python
# -*- coding: utf-8 -*-
import subprocess
import re
from data_loader import DataLoader
from logger import get_logger

settings = DataLoader()
logger = get_logger("network_scan")
network = settings.network
admin_password = settings.admin_password


def scan_for_devices():
    scan = subprocess.check_output("echo "+admin_password+" | nmap -sP " + network, shell=True)
    p = re.compile(ur'(?:[0-9a-fA-F]:?){12}')
    return re.findall(p, scan)


def room_members_parser(people):
    answer_string = ""
    for member in people:
        answer_string += "- " + member + "\n"
    if answer_string == "":
        answer_string = "No parece haber nadie :'("
    else:
        answer_string = "Presentes:\n" + answer_string
    return answer_string


def who_is_there():
    macs = scan_for_devices()
    who_are_there = []
    logger.debug("ENCONTRADOS: " + str(macs))
    for mac in scan_for_devices():
        if mac in list(settings.devices.keys()):
            who_are_there.append(settings.devices[mac])
    who_are_there = sorted(set(who_are_there))
    respuesta = room_members_parser(who_are_there)
    return respuesta, who_are_there


def is_someone_there():
    who = who_is_there()[1]
    return len(who) != 0
