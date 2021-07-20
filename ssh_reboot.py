import paramiko
import time

dssh = paramiko.SSHClient()
dssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
# paramiko.util.log_to_file('paramiko.log')
try:
    dssh.connect("10.33.8.76", username="root", password="abc123",timeout=2)
except Exception as e:
    print("SSH failed with Error : %s" % e)
    exit(1)
dssh.exec_command('shutdown -r', get_pty=True,timeout=2)
time.sleep(60)
dssh.close()
