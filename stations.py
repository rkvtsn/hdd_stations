#!/usr/bin/env python
# coding=utf-8
from string import Template

import sarge

SERVER_1_IP = ""
SERVER_2_IP = ""


def add_station(client_name, client_ip_address, target_name, MAC_address, broadcast_net, mask_net, mask_subnet):
    lvm_volume_name = ""
    drbd_res_name = ""
    station_number = ""
    image_name = ""
    MAC_address = ""  # через "_"

    variables = {
        "drbd_res_name": drbd_res_name,
        "station_number": station_number,
        "lvm_volume_name": lvm_volume_name,
        "server1_ip_address": SERVER_1_IP,
        "server2_ip_address": SERVER_2_IP,
        "client_ip_address": client_ip_address,
        "target_name": target_name,
        "client_name": client_name
    }

    def save_by_template(template_name, save_to, saving_param='w'):
        with open(template_name, "r") as fp:
            template = Template(fp.read())
        text = template.substitute(variables)
        with open(save_to, saving_param) as fp:
            fp.write(text)

    """
    1) Подготовить lvm-раздел
    """
    if '0 logical volume(s) in volume group "arms" now active' != sarge.get_stdout("vgchange –ay"):
        return

    """
    2) Подготовить lvm-раздел для будущего iscsi-target'а, выполнив команду
    """
    if 'Logical volume {0} created'.format(lvm_volume_name) != sarge.get_stdout("lvcreate -L 100G -n {0} arms".format(lvm_volume_name)):
        return

    """
    3) На серверах настроить drbd-ресурсы для клиентских станций
    """
    with open('drbd_resource_template.txt', 'r') as fp:
        drbd_resource_template = Template(fp.read())

    drbd_resource = drbd_resource_template.substitute(variables)

    with open('/etc/drbd.d/{drbd_res_name}.res'.format(drbd_res_name=drbd_res_name), 'w') as fp:
        fp.write(drbd_resource)

    """
    4) Для создания и инициализации ресурса выполнить команды
    """
    sarge.run("modprobe drbd && drbdadm create-md {drbd_res_name} && drbdadm up {drbd_res_name}".format(
        drbd_res_name=drbd_res_name))
    # drbd end

    # ONLY ON sbdz1.nicetu
    sarge.run("drbdadm -- --overwrite-data-of-peer primary {drbd_res_name}".format(drbd_res_name=drbd_res_name))

    # on TWO! servers:
    sarge.run("/etc/init.d/drbd start && chkconfig –level 3 5 drbd on")

    # heartbeat resources <<
    # "/etc/ha.d/haresources"


    """
    5) После окончания синхронизации на сервере sbdz1.nicetu создать логические тома для каждой клиентской станции
    """
    # ONLY ON sbdz1.nicetu BEGIN!!!
    p = sarge.run("vgcreate {client_name} /dev/drbd{station_number}".format(client_name=client_name,
                                                                            station_number=station_number),
                  stdout=sarge.Capture())
    if 'Volume group "{client_name}" successfully created'.format(client_name=client_name) != p.stdout.read().decode(
            'unicode_escape'):
        return

    p = sarge.run("lvcreate -L 92G -n rootfs {client_name}".format(client_name=client_name), stdout=sarge.Capture())
    if 'Logical volume "rootfs" created' != p.stdout.read().decode('unicode_escape'):
        return

    p = sarge.run("lvcreate -l 100%free -n swap {client_name}".format(client_name=client_name), stdout=sarge.Capture())
    if 'Logical volume "swap" created' != p.stdout.read().decode('unicode_escape'):
        return

    """
    6) Создать на сервере sbdz1.nicetu файловые системы на клиентских разделах
    """
    sarge.run("mkfs.ext3 /dev/{client_name} /rootfs && mkswap /dev/{client_name} /swap".format(client_name=client_name))


    """
    7) Создать на сервере sbdz1.nicetu корневую файловую систему клиентской станции
    """
    sarge.run(
        "mkdir /mnt/newroot && mount /dev/{client_name} /rootfs /mnt/newroot && rsync –aHAXv /* /mnt/newroot --exclude=/dev --exclude=/proc --exclude=/sys --exclude=/mnt".format(
            client_name=client_name))

    sarge.run("mkdir /mnt/newroot/dev /mnt/newroot/proc /mnt/newroot/sys /mnt/newroot/mnt")

    sarge.run("cd /mnt/newroot/")

    with open("/etc/hosts", "w") as fp:
        hosts = fp.read()
        hosts.replace("sbdz1.nicetu", client_name)
        fp.write(hosts)

    with open("/etc/sysconfig/network", "w") as fp:
        network = fp.read()
        network.replace("sbdz1.nicetu", client_name)
        fp.write(network)

    """
    10*) Отредактировать содержимое файла etc/fstab
    """

    save_by_template("fstab_template.txt", '/etc/fstab')

    """
    11*) Отредактировать содержимое файла etc/sysconfig/network-scripts/ifcfg-eth0
    """
    save_by_template("ifcfg_template.txt", '/etc/sysconfig/network-scripts/ifcfg-eth0')

    sarge.run("sync && sync && umount /mnt/newroot && vgchange -an")

    # FOR TWO SERVERS!!!!

    """
    8) На каждом сервере создать iSCSI-target (/etc/tgt/targets.conf)
    """
    with open("targets_conf.txt", "r") as fp:
        targets_conf_template = Template(fp.read())
    targets_conf = targets_conf_template.substitute(variables)
    with open("/etc/tgt/targets.conf", "a") as fp:
        fp.write(targets_conf)

    sarge.run(
        "chkconfig --level 35 drbd on && chkconfig --level 35 heartbeat on && /etc/init.d/drbd start && /etc/init.d/heartbeat start")

    """
    9) На любом сервере подготовить загрузочный образ корневой ФС, включающий в себя нужные для загрузки модули ядра (драйвера iSCSI, 
    файловых систем, device mapper т.п.), программы конфигурации сетевых интерфейсов (ifconfig) конфигурации томов (lvm) 
    и подключения iSCSI-target iscsistart, динамические библиотеки, необходимые для их работы
    """

    script_mkinitrd = "mkinitrd --preload=crc-t10dif --preload=dm-log --preload=dm-memcache --preload=dm-mirror --preload=dm-mod --preload=dm-raid45 --preload=dm-region-hash --preload=dm-snapshot --preload=dm-zero --preload=ext3 --preload=ide-core --preload=ide-gd_mod --preload=jbd --preload=mbcache --preload=mptbase --preload=mptscsih --preload=mptspi --preload=scsi_transport_spi --preload=sd_mod --preload=xor --preload=pcnet32 	--preload=scsi_transport_iscsi --preload=iscsi_tcp --preload=libiscsi --preload=libiscsi_tcp -- nocompress 2.6.32-kernel.img 2.6.32-358.14.1.el6.x86_64"

    sarge.run("mkdir /root/initrd && cd /root/initrd && " + script_mkinitrd)

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

    sarge.run("cd /root/initrd/lib64 && ln -s libc-2.5.so libc.so.6 && ln -s ld-2.5.so ld-linux-x86-64.so.2")

    sarge.run("cp /sbin/ifconfig /sbin/iscsistart /sbin/lvm /root/initrd/bin/")

    """
    После этого отредактировать файл init в корневом каталоге initrd /root/initrd. 
    Необходимо добавить команды для конфигурации сетевого интерфейса и подключения iscsi-target’а в раздел, 
    предшествующий созданию и монтирования блочного устройства /dev/root, 
    но после загрузки всех модулей ядра (см. листинг файла init).
    """

    sarge.run(
        "find . -print| cpio -H newc -o |gzip -9 -c > ../initrd_{image_name}.img && "
        "cp /root/initrd_{image_name}.img /tftpboot".format(image_name=image_name))

    sarge.run("cp -rf /usr/share/system-config-netboot/pxelinux.cfg/ /tftpboot/")

    save_by_template("mac_template.txt", 'touch /tftpboot/pxelinux.cfg/{MAC_address}'.format(MAC_address=MAC_address))

    """
    10) Отредактировать содержимое файла etc/fstab
    """
    save_by_template("fstab_template.txt", '/etc/fstab')

    """
    11) Отредактировать содержимое файла etc/sysconfig/network-scripts/ifcfg-eth0
    """
    save_by_template("ifcfg_template.txt", '/etc/sysconfig/network-scripts/ifcfg-eth0')
