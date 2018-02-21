import sarge



def delete_station(logic_name):

    drbd_resource = '/etc/drbd.d/{drbd_res_name}.res'.format(drbd_res_name=logic_name)
    sarge.run("rm " + drbd_resource)

    targets = "/etc/tgt/targets.conf"

    mac = "/tftpboot/pxelinux.cfg"

    pass


if __name__ == "__main__":
    delete_station("my_station")