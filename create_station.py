#!/usr/local/bin/python3.6
# coding=utf-8
import sys
from socket import *
from string import Template

import logging

# import paramiko
import sarge


SSH_USERNAME = "root"
SSH_PASSWORD = "12345678"
SERVER_1_IP = "192.168.110.121"
SERVER_2_IP = "192.168.110.199"
FILENAME = "stations_list.csv"
PORT = 61001
SEPARATOR = "#"

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def create_sub(data):
    udp_socket = socket(AF_INET, SOCK_DGRAM)
    address = (SERVER_2_IP, 59999)
    try:
        data = str.encode(data)
        udp_socket.sendto(data, address)
        data, _ = udp_socket.recvfrom(1024)
        data = bytes.decode(data)
        if data != "":
            raise Exception(data)
        else:
            print("Good job")

    except (KeyboardInterrupt, SystemExit):
        print('Stopped...')
        udp_socket.close()
    udp_socket.close()


# def ssh_run(cmd, address=SERVER_2_IP, username=SSH_USERNAME, password=SSH_PASSWORD):
#     ssh = paramiko.client.SSHClient()
#     ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
#     ssh.connect(address, username=username, password=password)
#     std = ssh.exec_command(cmd)
#     return std, ssh


def save_data(logic_name, MAC_address, mask, client_ip_address, subnet, broadcast):
    # Наименование логического объекта, маска подсети, IP-адрес клиентской ПЭВМ, ... ->
    # ->... адрес подсети, широковещательный адрес, MAC-адрес
    new_line = ",".join([logic_name, mask, client_ip_address, subnet, broadcast, MAC_address]) + "\n"
    with open(FILENAME, 'a+') as fp:
        fp.write(new_line)
    with open(FILENAME, 'r') as fp:
        station_number = len(fp.readlines())
    return str(station_number)

variables = {}

def add_station(logic_name, MAC_address, mask, client_ip_address, subnet, broadcast):
    MAC_address = MAC_address.replace(":", "_").replace("-", "_")

    target_name = logic_name
    lvm_volume_name = logic_name
    drbd_res_name = logic_name
    client_name = logic_name
    image_name = logic_name

    station_number = save_data(logic_name, MAC_address, mask, client_ip_address, subnet, broadcast)
    logging.info("added information")

    global variables
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
        with open("templates/" + template_name, "r") as fp:
            template = Template(fp.read())
        text = template.substitute(variables)
        with open(save_to, saving_param) as fp:
            fp.write(text)

    """
    1) Подготовить lvm-раздел
    """
    # if '0 logical volume(s) in volume group "arms" now active' != :
    #     return
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
    cmd = "modprobe drbd && drbdadm create-md {drbd_res_name} -fd && drbdadm up {drbd_res_name}".format(
        drbd_res_name=drbd_res_name)
    logging.info(cmd)
    sarge.run(cmd)

    # params = " ".join([logic_name, subnet, client_ip_address, MAC_address, broadcast, mask, station_number])
    # cmd = "python /root/stations_tool/sub_station_init.py " + params
    # logging.info(cmd)
    # (_, stdout, stderr), ssh = ssh_run(cmd)
    # error = stderr.read()
    # logging.info(stdout.read())
    # logging.error(error)
    # ssh.close()


    # ONLY ON sbdz1.nicetu
    cmd = "drbdadm -- --overwrite-data-of-peer primary {drbd_res_name}".format(drbd_res_name=drbd_res_name)
    logging.info(cmd)
    result = sarge.run(cmd).returncode
    if result != 0:
        return

    create_sub(SEPARATOR.join([logic_name, subnet, client_ip_address, MAC_address, broadcast, mask, station_number]))

    # on TWO! servers:
    cmd = "/etc/init.d/drbd start && chkconfig --level 35 drbd on"
    logging.info(cmd)
    result = sarge.run(cmd).returncode
    if result != 0:
        return
    # (_, stdout, stderr), ssh = ssh_run(cmd)
    # error = stderr.read()
    # logging.info("info:" + stdout.read())
    # logging.info("error:" + error)
    # ssh.close()
    # if error != "":
    #     return

    logging.info("4! \n")
    """
    5) После окончания синхронизации на сервере sbdz1.nicetu создать логические тома для каждой клиентской станции
    """
    # ONLY ON sbdz1.nicetu BEGIN!!!
    cmd = "pvcreate /dev/drbd{station_number}".format(station_number=station_number)
    logging.info(cmd)

    cmd = "vgcreate {client_name} /dev/drbd{station_number}".format(client_name=client_name,
                                                                    station_number=station_number)
    logging.info(cmd)
    result = sarge.run(cmd).returncode
    if result != 0:
        return

    cmd = "lvcreate -L 20G -n rootfs {client_name}".format(client_name=client_name) #92G # Странная ошибка с фильтром
    logging.info(cmd)
    result = sarge.run(cmd).returncode
    if result != 0:
        return

    cmd = "lvcreate -l 100%free -n swap {client_name}".format(client_name=client_name)
    logging.info(cmd)
    result = sarge.run(cmd).returncode
    if result != 0:
        return

    logging.info("5! \n")
    """
    6) Создать на сервере sbdz1.nicetu файловые системы на клиентских разделах
    """
    sarge.run("mkfs.ext4 /dev/{client_name} /rootfs && mkswap /dev/{client_name} /swap".format(client_name=client_name))
    logging.info("6! \n")

    """
    7) Создать на сервере sbdz1.nicetu корневую файловую систему клиентской станции
    """
    sarge.run(
        "mkdir /mnt/newroot && mount -t ext4 /dev/{client_name}/rootfs /mnt/newroot && rsync –aHAXv /* /mnt/newroot --exclude=/dev --exclude=/proc --exclude=/sys --exclude=/mnt".format(
            client_name=client_name))

    sarge.run("mkdir /mnt/newroot/dev /mnt/newroot/proc /mnt/newroot/sys /mnt/newroot/mnt")

    logging.info("7! \n")
    """
    10*) Отредактировать содержимое файла etc/fstab
    """
    save_by_template("fstab_template.txt", '/mnt/newroot/etc/fstab')
    logging.info("10*! \n")
    """
    11*) Отредактировать содержимое файла etc/sysconfig/network-scripts/ifcfg-eth0
    """
    save_by_template("ifcfg_template.txt", '/mnt/newroot/etc/sysconfig/network-scripts/ifcfg-eth0')

    with open("/mnt/newroot/etc/hosts", "w") as fp:
        hosts = fp.read()
        fp.write(hosts.replace("sbdz1.nicetu", client_name))

    with open("/mnt/newroot/etc/sysconfig/network", "w") as fp:
        network = fp.read()
        fp.write(network.replace("sbdz1.nicetu", client_name))

    sarge.run("rm /mnt/newroot/etc/sysconfig/network-scripts/ifcfg-eth1")
    sarge.run("rm /mnt/newroot/etc/sysconfig/network-scripts/ifcfg-eth2")

    sarge.run("sync && sync && umount /mnt/newroot && vgchange -an")
    logging.info("11*! \n")
    # FOR TWO SERVERS!!!!
    """
    8) На каждом сервере создать iSCSI-target (/etc/tgt/targets.conf)
    """
    save_by_template("targets_conf_template.txt", "/etc/tgt/targets.conf", "a")

    sarge.run('scp /etc/tgt/targets.conf {sub_server}:/etc/tgt/targets.conf'.format(sub_server=SERVER_2_IP))

    sarge.run(
        "chkconfig --level 35 drbd on && /etc/init.d/drbd start")

    logging.info("8! \n")
    """
    9) На любом сервере подготовить загрузочный образ корневой ФС, включающий в себя нужные для загрузки модули ядра (драйвера iSCSI,
    файловых систем, device mapper т.п.), программы конфигурации сетевых интерфейсов (ifconfig) конфигурации томов (lvm)
    и подключения iSCSI-target iscsistart, динамические библиотеки, необходимые для их работы
    """

    script_mkinitrd = "mkinitrd --preload=crc-t10dif --preload=dm-log --preload=dm-memcache --preload=dm-mirror --preload=dm-mod --preload=dm-raid45 --preload=dm-region-hash --preload=dm-snapshot --preload=dm-zero --preload=ext3 --preload=ide-core --preload=ide-gd_mod --preload=jbd --preload=mbcache --preload=mptbase --preload=mptscsih --preload=mptspi --preload=scsi_transport_spi --preload=sd_mod --preload=xor --preload=pcnet32 	--preload=scsi_transport_iscsi --preload=iscsi_tcp --preload=libiscsi --preload=libiscsi_tcp --nocompress 2.6.32-kernel.img 2.6.32-358.14.1.el6.x86_64"

    sarge.run("mkdir /root/initrd")
    sarge.run(script_mkinitrd)
    sarge.run("yes | cp -rf 2.6.32-kernel.img /root/initrd")

    sarge.run("cpio -ic < /root/initrd/2.6.32-kernel.img")

    # ldd_ifconfig = sarge.get_stdout("ldd /sbin/ifconfig")
    """
    linux-vdso.so.1 =>  (0x00007fff127ff000)
  	libc.so.6 => /lib64/libc.so.6 (0x00007f7d72399000)
    /lib64/ld-linux-x86-64.so.2 (0x00007f7d72718000)
    """
    # ldd_ifconfig_files = list(filter(bool, [x.split(" ")[0] for x in ldd_ifconfig.split("\n")]))
    # ldd_real_path = list(filter(bool, [sarge.get_stdout("ls -l /lib64" + x) for x in ldd_ifconfig_files]))

    sarge.run(
        "mkdir /root/initrd/lib64 && cp /lib64/libc-2.5.so /root/initrd/lib64/ && cp /lib64/ld-2.5.so /root/initrd/lib64")

    #sarge.run("cd /root/initrd/lib64 && ln -s libc-2.5.so libc.so.6 && ln -s ld-2.5.so ld-linux-x86-64.so.2")
    sarge.run("ln -s /root/initrd/lib64/libc-2.5.so /root/initrd/lib64/libc.so.6")
    sarge.run("ln -s /root/initrd/lib64/ld-2.5.so /root/initrd/lib64/ld-linux-x86-64.so.2")
    sarge.run("yes | cp -rf /sbin/ifconfig /sbin/iscsistart /sbin/lvm /root/initrd/bin/")

    """
    После этого отредактировать файл init в корневом каталоге initrd /root/initrd.
    Необходимо добавить команды для конфигурации сетевого интерфейса и подключения iscsi-target’а в раздел,
    предшествующий созданию и монтирования блочного устройства /dev/root,
    но после загрузки всех модулей ядра (см. листинг файла init).
    """

    save_by_template('init_template.txt', '/root/initrd/init')

    sarge.run(
        "find . -print| cpio -H newc -o |gzip -9 -c > ../initrd_{image_name}.img && "
        "yes | cp -rf /root/initrd_{image_name}.img /tftpboot".format(image_name=image_name))

    sarge.run("yes | cp -rf /usr/share/system-config-netboot/pxelinux.cfg/ /tftpboot/")

    save_by_template("mac_template.txt", '/tftpboot/pxelinux.cfg/01_{MAC_address}'.format(MAC_address=MAC_address))
    logging.info("9! DONE! \n")

    return True


def revert():
    sarge.run("/etc/init.d/drbd stop")
    sarge.run("rmmod drbd")
    sarge.run('rm /etc/drbd.d/{drbd_res_name}.res -r'.format(drbd_res_name=drbd_res_name))


if __name__ == "__main__":
    logging.info("started")
    try:

        if add_station(subnet="192.168.0.0",
                    client_ip_address="192.168.178.198",
                    MAC_address="00:0C:29:05:81:BB",
                    broadcast="192.168.255.255",
                    mask="255.255.0.0",
                    logic_name="my_station10") != True:
            raise Exception("Failed")
    except Exception as e:
        print("Error: " + e.message)
        revert()
