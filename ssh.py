import sarge


def run(cmd, address, username, password):

    sarge.run("ssh " + address + " -l " + username)
    return


if __name__ == "__main__":
    SSH_USERNAME = "root"
    SSH_PASSWORD = "12345678"
    IP_ADDRESS = "192.168.110.199"
    run("ls", IP_ADDRESS, SSH_USERNAME, SSH_PASSWORD)