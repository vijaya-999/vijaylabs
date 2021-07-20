#! /usr/bin/python

"""vdbench.py

This script install vdbench and starts vdbench workload on LPAR,
Developed by: racharys@in.ibm.com
Date: 15/07/2020
Lab : ISST

Modified on 22:072020
Copying the vdbench to exe to /tmp instead of /vdbench """


import paramiko
import sys
import os
import time
import datetime
from robot.api import logger


def sshexec(ip, cmd, usrname, passwd):
    dssh = paramiko.SSHClient()
    dssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    paramiko.util.log_to_file('paramiko.log')
    try:
        dssh.connect(ip, username=usrname, password=passwd)
    except Exception as e:
        print("SSH failed with Error : %s" % e)
        exit(1)
    stdin, stdout, stderr = dssh.exec_command(cmd, get_pty=True)
    out = stdout.read()
    err = stderr.read()
    if stdout.channel.recv_exit_status() != 0:
        log_string = str.format("Command Failed: {} {}", out, err)
        log(log_string, "WARN")

    # log_string = str.format("Command Successful: {} {}", out, err)
    # log(log_string, "INFO")

    dssh.close()
    return stdout.channel.recv_exit_status(), out, err


def sshexec_invoke(ip, cmd, usrname, passwd):

    dssh = paramiko.SSHClient()
    dssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        dssh.connect(ip, username=usrname, password=passwd)
    except Exception as e:
        print("SSH failed with Error : %s" % e)
        exit(1)

    dssh.invoke_shell()
    stdin, stdout, stderr = dssh.exec_command(cmd, get_pty=True)
    out = stdout.read()
    err = stderr.read()

    return stdout.channel.recv_exit_status(), out, err


def log(log_string, log_type):
    ts = time.time()
    st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
    print(st)
    if log_type == "INFO":
        logger.console(st + '  ' + log_string)
        logger.info(log_string)
    elif log_type == "DEBUG":
        logger.console(st + '  ' + log_string)
        logger.debug(log_string)
    elif log_type == "WARN":
        logger.console(st + '  ' + log_string)
        logger.warn(log_string)
    elif log_type == "ERROR":
        logger.console(st + '  ' + log_string)
        logger.error(st + '  ' + log_string)
    elif log_type == "":
        logger.console(log_string)
        logger.trace(log_string)


def check_vdbench_process(lpar_ip, passwd):
    
    # To get PID of vdbench process
    log("Checking if vdbench is running ..........", "INFO")
    arg = "ps -aef | grep './vdbench -f vdbench_conf.aix -o vdbench_stress_result' | awk '{print $2}'"
    rc, out, err = sshexec(lpar_ip, arg, "root", passwd)
    check_vdbench = [i for i in out.split('\r\n') if i]
    print(check_vdbench)
    time.sleep(0.5)
    
    arg = "ps -aef | grep './vdbench.jar Vdb.Vdbmain -f vdbench_conf.aix -o vdbench_stress_result' | awk '{print $2}'"
    rc, out, err = sshexec(lpar_ip, arg, "root", passwd)
    check_vdbench1 = [i for i in out.split('\r\n') if i]
    print(check_vdbench1)
    time.sleep(0.5)
    
    arg = str.format("kill -9 {}", ' '.join(check_vdbench))
    rc, out, err = sshexec(lpar_ip, arg, "root", passwd)  
    
    arg = str.format("kill -9 {}", ' '.join(check_vdbench1))
    rc, out, err = sshexec(lpar_ip, arg, "root", passwd)
    
    log("Killing vdbench process if running ....", "INFO")
    
    return 0


def get_free_disks(lpar_ip,lspv_disk,passwd):
    
    arg = "lspv | grep None | awk '{print $1}'\n"
    log(arg, "INFO")
    rc, out, err = sshexec(lpar_ip, arg, "root", passwd)
    if rc != 0 or out is None:
        log_string = str.format("Failed to Check Free Disks {} Error : {}", out, err)
        log(log_string, "ERROR")
        return -1
    
    check_disk = [i for i in out.split('\r\n') if i]
    check_disk1 = [int(sub.replace('hdisk', '')) for sub in check_disk]
    
    # Final list disk to add if tmp size cannot be increased
    final_disk = list(set(check_disk1) & set(lspv_disk))
    
    return final_disk

 
# To change tmp size if needed 
def tmp_size_change(lpar_ip, lspv_disk, passwd):
    
    # To Check /tmp size
    arg = "df -g /tmp | awk '{print $3}'\n"
    log(arg, "INFO")
    rc, out, err = sshexec(lpar_ip, arg, "root", passwd)
    if rc != 0 or out is None:
        log_string = str.format("Failed to get /tmp free size {} Error : {}", out, err)
        log(log_string, "ERROR")
    
    check_disk = [i for i in out.split('\r\n') if i]
    print(check_disk)
    if float(check_disk[1]) < 1:
        arg = "chfs -a size=+1G /tmp"
        log(arg, "INFO")
        rc, out, err = sshexec(lpar_ip, arg, "root", passwd)
        if rc != 0 or out is None:
            free_disks = get_free_disks(lpar_ip, lspv_disk, passwd)
            if free_disks is not -1:
                print(free_disks)
                arg = str.format("extendvg rootvg hdisk{}", free_disks[0])
                log(arg, "INFO")
                rc, out, err = sshexec(lpar_ip, arg, "root", passwd)
                if rc == 0:
                    arg = "chfs -a size=+1G /tmp"
                    log(arg, "INFO")
                    rc, out, err = sshexec(lpar_ip, arg, "root", passwd)
                    if rc != 0 or out is None:
                        log_string = str.format("Failed to change size of /tmp {} Error : {}", out, err)
                        log(log_string, "ERROR")
                        return -1
                    else:
                        return 0
                return 0
            return -1
        
    return 0


def check_disk_to_create_conf_file(lpar_ip, test_disk_list, test_iosize, test_rdpct, test_time,
                                   test_xfersize, test_seekpct, passwd):

    # Create a conf_file
    arg = "mkdir -p /tmp/vdbench"
    log(arg, "INFO")
    rc, out, err = sshexec(lpar_ip, arg, "root", passwd)
    if rc != 0 or out is None:
        log_string = str.format("Failed to Create conf file ..{} Error : {}", out, err)
        log(log_string, "ERROR")
        return -1

    # Check if vdbench_conf.aix file is there if overwrite else create a new one
    arg = "ls -al /tmp/vdbench/ | grep vdbench_conf.aix"
    log(arg, "INFO")
    rc, out, err = sshexec(lpar_ip, arg, "root", passwd)
    if rc != 0 or out is None:
        arg = "touch /tmp/vdbench/vdbench_conf.aix"
        log(arg, "INFO")
        rc, out, err = sshexec(lpar_ip, arg, "root", passwd)
        if rc != 0 or out is None:
            log_string = str.format("Failed to Create conf file ..{} Error : {}", out, err)
            log(log_string, "ERROR")
            return -1

    else:
        arg = "rm -rf /tmp/vdbench/vdbench_conf.aix; touch /tmp/vdbench/vdbench_conf.aix"
        log(arg, "INFO")
        rc, out, err = sshexec(lpar_ip, arg, "root", passwd)
        if rc != 0 or out is None:
            log_string = str.format("Failed to Create conf file ..{} Error : {}", out, err)
            log(log_string, "ERROR")
            return -1

    # Checking for Disk present in lpar
    arg = "lspv | awk '{print $1}'\n"
    log(arg, "INFO")
    rc, out, err = sshexec(lpar_ip, arg, "root", passwd)
    if rc != 0 or out is None:
        log_string = str.format("Failed to get freee disks..{} Error : {}", out, err)
        log(log_string, "ERROR")
        return -1

    check_disk = [i for i in out.split('\r\n') if i]
    check_disk1 = [int(sub.replace('hdisk', '')) for sub in check_disk]
    # print(check_disk1)

    # Final list disk to add in the conf file
    final_disk = list(set(check_disk1) & set(test_disk_list))
    
    # Reamining disk to add to /tmp if the disk size fails
    lspv_disk = list(set(check_disk1)  - set(test_disk_list))
    if tmp_size_change(lpar_ip, lspv_disk, passwd) is -1:
        log("Unable to change size of /tmp", "ERROR")
        return -1
        
    # Check if disk in lpar and adding disk to the config file.
    # print(final_disk)
    disk = ""
    for disk_num in final_disk:
        # sd=sd1,lun=/dev/rhdisk1
        disk += ("sd=sd" + str(disk_num) + ",lun=/dev/rhdisk" + str(disk_num) + "\n")

    # Adding rdpct size
    # wd = wd1, sd = sd *, xfersize = 131072, rdpct = 100
    if str(test_seekpct) and int(test_xfersize) and int(test_rdpct):
        disk += "wd=wd1,sd=sd*,xfersize=" + test_xfersize + ",rdpct=" + test_rdpct + ",seekpct=" + test_seekpct + "\n"
    elif int(test_xfersize) and int(test_rdpct):
        disk += "wd=wd1,sd=sd*,xfersize=" + test_xfersize + ",rdpct=" + test_rdpct + "\n"
    else:
        log_string = "Invalid values of rdpct, seekpct and  xfersize ...Error"
        log(log_string, "ERROR")
        return -1

    #  Adding the test_iosize and testime to thefile
    # rd = run1, wd = wd1, iorate = 10000, elapsed = 86400, interval = 1
    if int(test_iosize) and int(test_time):
        disk += "rd=run1,wd=wd1,iorate=" + test_iosize + ",elapsed=" + test_time + ",interval=1\n"
    else:
        log_string = "Invalid values of iorate and elapsed time ...Error"
        log(log_string, "ERROR")
        return -1

    # Adding contents to the vdbench.conf file
    arg = str.format("echo \"{}\" >> /tmp/vdbench/vdbench_conf.aix ", disk)
    log(arg, "INFO")
    rc, out, err = sshexec(lpar_ip, arg, "root", passwd)
    if rc != 0 or out is None:
        log_string = str.format("Failed to add disks to vdbench.conf ..{} Error : {}", out, err)
        log(log_string, "ERROR")
        return -1
    
    
        
    return 0


def copy_vdbench_from_logger(lpar_ip, passwd):
       
    arg = "mount 9.3.121.20:/home/deepthi/vdbench-50402 /mnt"
    log(arg, "INFO")
    rc, out, err = sshexec(lpar_ip, arg, "root", passwd)
    if rc != 0 or out is None:
        log_string = str.format("Unable to mount logger for copying vdbench ..{} Error : {}", out, err)
        log(log_string, "ERROR")
        return -1

    arg = "cp -r /mnt/* /tmp/vdbench"
    log(arg, "INFO")
    rc, out, err = sshexec(lpar_ip, arg, "root", passwd)
    if rc != 0 or out is None:
        log_string = str.format("Unable to mount logger for copying vdbench ..{} Error : {}", out, err)
        log(log_string, "ERROR")
        return -1

    arg = "umount -f /mnt"
    log(arg, "INFO")
    rc, out, err = sshexec(lpar_ip, arg, "root", passwd)
    if rc != 0 or out is None:
        log_string = str.format("Unable to mount logger for copying vdbench ..{} Error : {}", out, err)
        log(log_string, "ERROR")
        return -1
    
    return 0


def start_vdbench(lpar_ip, passwd):
    # Check if java is added to path
    arg = "echo $PATH"
    log(arg, "INFO")
    rc, out, err = sshexec(lpar_ip, arg, "root", passwd)
    if rc != 0 or out is None:
        log_string = str.format("Unable to find Java in variable PATH ..{} Error : {}", out, err)
        log(log_string, "ERROR")
        return -1

    if '/usr/java8_64/jre/bin' not in out:
        arg = "export PATH=/usr/java8_64/jre/bin:$PATH"
        log(arg, "INFO")
        rc, out, err = sshexec(lpar_ip, arg, "root", passwd)
        if rc != 0 or out is None:
            log_string = str.format("Unable to add Java in variable PATH ..{} Error : {}", out, err)
            log(log_string, "ERROR")
            return -1

    arg = "chmod -R 777 /tmp/vdbench/"
    log(arg, "INFO")
    rc, out, err = sshexec(lpar_ip, arg, "root", passwd)
    if rc != 0 or out is None:
        log_string = str.format("Changing /vdbench Permissions ..{} Error : {}", out, err)
        log(log_string, "ERROR")
        return -1

    arg = "cd /tmp/vdbench; nohup ./vdbench  -f vdbench_conf.aix -o vdbench_stress_result  & "
    log(arg, "INFO")
    rc, out, err = sshexec_invoke(lpar_ip, arg, "root", passwd)
    if rc != 0 or out is None:
        log_string = str.format("Unable to start vdbench ..{} Error : {}", out, err)
        log(log_string, "ERROR")
        return -1

    arg = "ps -aef | grep vdbench"
    log(arg, "INFO")
    rc, out, err = sshexec(lpar_ip, arg, "root", passwd)
    if rc != 0 or out is None:
        log_string = str.format("Unable to start vdbench ..{} Error : {}", out, err)
        log(log_string, "ERROR")
        return -1

    return 0


# Ping check to host
def ping_lpar(host):
    polling = 10
    while polling:
        exit_status = os.system("ping -c 1 " + host)
        if exit_status == 0:
            return 0

        sleep(10)
        polling = polling - 1
    return 1


def print_and_send_email(email_address, message, lpar_name):
    print(message)
    hostname = "9.3.121.20"
    full_mgs = lpar_name + ": " + message
    client = paramiko.client.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    command = "echo \"Subject : \"" + full_mgs + "\"<eom> \" | sendmail " + email_address
    client.connect(hostname, username="ctalert", password="ctalert")
    stdin, stdout, stderr = client.exec_command(command)
    exit_status = stdout.channel.recv_exit_status()
    client.close()
    return exit_status


def main():
    sys.stdout.flush()
    tgt_lpar = sys.argv[1]
    email_address = sys.argv[2]
    test_disk = sys.argv[3]
    test_iosize = sys.argv[4]
    test_rdpct = sys.argv[5]
    test_seekpct = sys.argv[6]
    test_xfersize = sys.argv[7]
    test_time = sys.argv[8]
    passwd = sys.argv[9]
    sys.stdout.flush()

    print("Checking LPAR Status ............")
    return_status = ping_lpar(tgt_lpar)
    if return_status:
        sys.exit(1)
    
    # To check if vdbenc process is running and kill if running.
    check_vdbench_process(tgt_lpar, passwd)
    
    test_disk_list = []
    if '-' in test_disk:
        test_disk = (test_disk.replace('hdisk', "")).split('-')
        test_disk_list = list(range(int(test_disk[0]), int(test_disk[1])+1, 1))

    elif ',' in test_disk:
        test_disk = (test_disk.replace("hdisk", "")).split(',')
        test_disk_list = [int(i) for i in test_disk]

    if check_disk_to_create_conf_file(tgt_lpar, test_disk_list, test_iosize, test_rdpct, test_time,
                                      test_xfersize, test_seekpct, passwd) is -1:
        sys.exit(1)

    if copy_vdbench_from_logger(tgt_lpar, passwd) is -1:
        sys.exit(1)

    if start_vdbench(tgt_lpar, passwd) is -1:
        sys.exit(1)

    # message = str.format("Vdbench Workload Started Successfully!! on {}", tgt_lpar)
    # log(message, "INFO")
    # if print_and_send_email(email_address, message, tgt_lpar) is -1:
        # sys.exit(1)

    return 0


main()
