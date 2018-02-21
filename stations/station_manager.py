#!/usr/local/bin/python3.6
# coding=utf-8
import sys
import logging
from socket import *
from string import Template

import sarge

from config import Configuration


class StationManager:
    """
    Station Manager:
    """

    def __init__(self, configurator=None):
        """

        :type config: config.Configuration
        """
        if configurator is None:
            configurator = Configuration()

        self.configurator = configurator
        self.config = configurator.config

        self.server_2_ip = ""

    def __create_substation(self, data):
        udp_socket = socket(AF_INET, SOCK_DGRAM)
        try:
            address = (self.server_2_ip, 59999)
            data = str.encode(data)
            udp_socket.sendto(data, address)
            data, _ = udp_socket.recvfrom(1024)
            data = bytes.decode(data)
            if data != "":
                raise Exception(data)
            else:
                logging.info("Substation created")
        finally:
            udp_socket.close()

        pass

    def rollback(self):
        pass

    def create(self):
        pass

    def get(self):
        pass

    def remove(self):
        pass

    def edit(self):
        pass

