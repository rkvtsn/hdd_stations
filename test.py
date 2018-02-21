import paramiko


SSH_USERNAME = "root"
SSH_PASSWORD = "12345678"
SERVER_1_IP = "192.168.110.121"
SERVER_2_IP = "192.168.110.199"
DB_FILENAME = 'stations_list.csv'

def ssh_run(cmd):
    ssh = paramiko.client.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SERVER_2_IP, username=SSH_USERNAME, password=SSH_PASSWORD)
    std = ssh.exec_command(cmd)
    return std, ssh


if __name__ == "__main__":
    (_, stdout, stderr), ssh = ssh_run('vgchange -ay')
    print(stdout.read())
    print(stderr.read())
    ssh.close()

    (_, stdout, stderr), ssh = ssh_run('/etc/init.d/drbd start && chkconfig --level 35 drbd on')
    print(stdout.read())
    print(stderr.read())
    ssh.close()

    (_, stdout, stderr), ssh = ssh_run('ls -l')
    print(stdout.read())
    print(stderr.read())
    ssh.close()
