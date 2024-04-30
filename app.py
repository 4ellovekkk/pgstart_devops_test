#!/usr/bin/env python
import sys
import paramiko
import logging

# Настройка логирования
logging.basicConfig(filename='./log.txt', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def use_sudo(ssh, password, log_file=None):
    command = "sudo su "
    ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(command, get_pty=True)
    logging.info("Original command sent")
    ssh_stdin.write(f"{password}\n")
    logging.info("password sent")
    ssh_stdin.flush()
    logging.info("input flushed")

def execute_ssh_command(ssh, command, log_file=None):
    ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(command, get_pty=True)
    ssh_stdin.write(f"{admin_password}\n")
    ssh_stdin.flush()
    if ssh_stderr.channel.recv_exit_status() != 0:
        logging.error(f"The following error occured {ssh_stderr.readlines()}")
    else:
        logging.info(f"The following output was produced:\n {ssh_stdout.readlines()}")
    return ssh_stdout.readlines(), ssh_stderr.readlines()

def install_postgresql(ssh, log_file=None):
    logging.info("Установка PostgreSQL...")
    execute_ssh_command(ssh, "sudo apt-get install postgresql postgresql-contrib postgresql-client-common -y", log_file)
    logging.info("PostgreSQL успешно установлен.")

def configure_postgresql(ssh, log_file=None):
    logging.info("Настройка PostgreSQL...")
    execute_ssh_command(ssh, "sudo sed -i 's/^listen_addresses.*/listen_addresses = '*'/' /etc/postgresql/*/main/postgresql.conf", log_file)
    execute_ssh_command(ssh, "echo 'host all all 0.0.0.0/0 md5' | sudo tee -a /etc/postgresql/*/main/pg_hba.conf", log_file)
    execute_ssh_command(ssh, "sudo service postgresql restart", log_file)
    logging.info("PostgreSQL успешно настроен для приема внешних соединений.")

def check_database(ssh, log_file=None):
    logging.info("Проверка работы БД...")
    stdout_result, stderr_result = execute_ssh_command(ssh, "psql -c 'SELECT 1;'", log_file)

def main(remote_host, ssh_username, ssh_password, admin_password, log_file=None):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(remote_host, username=ssh_username, password=ssh_password)
    ssh.get_transport()
    use_sudo(ssh, admin_password, log_file)
    install_postgresql(ssh, log_file)
    configure_postgresql(ssh, log_file)
    check_database(ssh, log_file)

    ssh.close()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(1)
    
    remote_host = sys.argv[1]
    log_file = "./log.txt"
    
    ssh_username = input("Введите имя пользователя SSH: ")
    ssh_password = input("Введите пароль SSH: ")
    admin_password = input("Введите пароль администратора: ")

    main(remote_host, ssh_username, ssh_password, admin_password, log_file)
