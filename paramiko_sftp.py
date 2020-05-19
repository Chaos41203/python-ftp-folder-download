import paramiko
import os

host, port, usr, pwd = '125.227.7.147', 10822, 'root', 'Nokia12345'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host,port,usr,pwd)
stdin, stdout, stderr = ssh.exec_command("ls")
print(stdout.readlines())