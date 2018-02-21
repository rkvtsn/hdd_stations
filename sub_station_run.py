#!/usr/local/bin/python3.6
# coding=utf-8
from socket import *

import sys
from string import Template
import logging

import sarge

SERVER_1_IP = "192.168.110.121"
SERVER_2_IP = "192.168.110.199"
PORT = 60000

HOST = '192.168.110.199'
UDP_PORT = 59999
ADDRESS = (HOST, UDP_PORT)
SEPARATOR = "#"

udp_socket = socket(AF_INET, SOCK_DGRAM)
udp_socket.bind(ADDRESS)
udp_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')



def add_sub_station(logic_name, MAC_address, mask, client_ip_address, subnet, broadcast, station_number):
    target_name = logic_name
    lvm_volume_name = logic_name
    drbd_res_name = logic_name
    client_name = logic_name
    image_name = logic_name

    variables = {
        "drbd_res_name": drbd_res_name,
        "station_number": station_number,
        "lvm_volume_name": lvm_volume_name,
        "server1_ip_address": SERVER_1_IP,
        "server2_ip_address": SERVER_2_IP,
        "client_ip_address": client_ip_address,
        "target_name": target_name,
        "client_name": client_name,
        "image_name": image_name,
        "broadcast": broadcast,
        "subnet": subnet,
        "port": PORT + int(station_number),
        "mask": mask
    }

    def save_by_template(template_name, save_to, saving_param='w'):
        with open("/root/stations_tool/templates/" + template_name, "r") as fp:
            template = Template(fp.read())
        text = template.substitute(variables)
        with open(save_to, saving_param) as fp:
            fp.write(text)

    """
    1) Подготовить lvm-раздел
    """
    logging.info('vgchange -ay')
    sarge.run('vgchange -ay')

    """
    2) Подготовить lvm-раздел для будущего iscsi-target'а, выполнив команду
    """
    cmd = "lvcreate -L 25G -n {0} arms".format(lvm_volume_name)  # !!! TODO 100G
    logging.info(cmd)
    sarge.run(cmd)

    """
    3) На серверах настроить drbd-ресурсы для клиентских станций
    """
    cmd = '/etc/drbd.d/{drbd_res_name}.res'.format(drbd_res_name=drbd_res_name)
    logging.info(cmd)
    save_by_template('drbd_resource_template.txt', cmd)
    logging.info("3! \n")

    """
    4) Для создания и инициализации ресурса выполнить команды
    """
    cmd = "modprobe drbd && drbdadm create-md {drbd_res_name} --fd && drbdadm up {drbd_res_name}".format(
        drbd_res_name=drbd_res_name)
    logging.info(cmd)
    sarge.run(cmd)



if __name__ == "__main__":
    try:
        while True:
            print('Wait data... to stop Ctrl+C')

            data, address = udp_socket.recvfrom(4096)
            print('Client addr: ', address)

            try:
                print('Data: ', data)
                params = data.split(SEPARATOR)
                logic_name = params[0]
                subnet = params[1]
                client_ip_address = params[2]
                MAC_address = params[3]
                broadcast = params[4]
                mask = params[5]
                station_number = params[6]

                add_sub_station(subnet=subnet,
                                client_ip_address=client_ip_address,
                                MAC_address=MAC_address,
                                broadcast=broadcast,
                                mask=mask,
                                logic_name=logic_name,
                                station_number=station_number)

                udp_socket.sendto(b'', address)
            except Exception as e:
                udp_socket.sendto(str.encode(e.message), address)

    except (KeyboardInterrupt, SystemExit):
        print('Stopped...')
        udp_socket.close()
