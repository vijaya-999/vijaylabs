"""Blast_IO.py

This script starts the Blast IO Workload on the newly installed LPAR,
Developed by: racharys@in.ibm.com
Date: 01/07/2020
Lab : ISST """

#! /usr/bin/python
import sys
import datetime
import time
import os
import paramiko
from robot.api import logger

def sshexec(ip,cmd,usrname,passwd):
	 
	dssh = paramiko.SSHClient()
	dssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	paramiko.util.log_to_file('paramiko.log')
	try:
		dssh.connect(ip, username=usrname, password=passwd)
	except Exception as e:
		print("SSH failed with Error : %s" % (e))
		exit(1)
	stdin, stdout, stderr = dssh.exec_command(cmd, get_pty=True)
	out = stdout.read()
	err = stderr.read()
	if stdout.channel.recv_exit_status() != 0:
		LogString = str.format("Command Failed: {} {}", out,err)
                Log(LogString, "WARN")
	else:
		LogString = str.format("Command Successful: {} {}", out,err)
                Log(LogString, "INFO")
	dssh.close()
	return (stdout.channel.recv_exit_status(), out, err)


def sshexec_invoke(ip,cmd,usrname,passwd):
	#lpar = str(sys.argv[1])
	 
	dssh = paramiko.SSHClient()
	dssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	try:
		dssh.connect(ip, username=usrname, password=passwd)
	except Exception as e:
		print "SSH failed with Error : %s" % (e)
		exit(1)
#	command = "hostname"
	dssh.invoke_shell()
	stdin, stdout, stderr = dssh.exec_command(cmd, get_pty=True)
	out = stdout.read()
	err = stderr.read()
	#if stdout.channel.recv_exit_status() != 0:
	#	print "Command Failed: %s %s" % (out, err)
		#print "Command Successful : %s" % (stdout.channel.recv(4096),stderr.channel.recv(4096))
	#else:
		#print "Command Successful : %s" % (stdout.channel.recv(4096),stderr.channel.recv(4096))
	#	print "Command Successful : %s" % (out)
	dssh.close()
	return (stdout.channel.recv_exit_status(), out, err)


def Log( logString,typeOfLog):
	ts = time.time()
	st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
	print(st)
	if typeOfLog=="INFO":
        	logger.console(st + '  ' + logString)
        	logger.info(logString)
    	elif typeOfLog=="DEBUG":
        	logger.console(st + '  ' + logString)
        	logger.debug(logString)
    	elif typeOfLog=="WARN":
        	logger.console(st + '  ' + logString)
        	logger.warn(logString)
    	elif typeOfLog=="ERROR":
        	logger.console(st + '  ' + logString)
        	logger.error(st + '  ' + logString)
    	elif typeOfLog=="":
        	logger.console(logString)
        	logger.trace(logString)   

   
# Checking the Freee disks and its size in AIX
def check_free_disks(lpar_ip):

    arg = "lspv | grep None | awk '{print $1}'\n"
    Log(arg, "INFO")
    rc,out,err=sshexec(lpar_ip,arg,"root","abc123")
    if rc != 0 or out is None:
        LogString = str.format("Failed to get freee disks..{} Error : {}", out,err)
        Log(LogString, "ERROR")
        return -1
            
    # Checking for Disk Size
    blast_disk = [i for i in out.split('\r\n') if i ]
    blast_disk_size = []
    
    for disk in blast_disk:
        arg = "bootinfo -s " + disk
        rc,out,err=sshexec(lpar_ip,arg,"root","abc123")
        if rc != 0 or out is None:
            LogString = str.format("Failed to find disk size of {} ..{} Error : {}", disk, out,err)
            Log(LogString, "ERROR")
            return -1
            
        else:      
            blast_disk_size.append(out.rstrip())
            
    return blast_disk, blast_disk_size
    

# Creating testvg and filesystems to mount in LPAR
def create_vg(lpar_ip, blast_disk, blast_disk_size):
       
    # Creating testvg
  
    arg = str.format("mkvg -f -y testvg  {}", ' '.join(blast_disk))
    Log(arg, "INFO")
    rc,out,err=sshexec(lpar_ip,arg,"root","abc123")
    if rc != 0 or out is None:
        LogString = str.format("Failed to create testvg..{} Error : {}", out,err)
        Log(LogString, "ERROR")
        return -1
             
    # Creating Filesystems for the testvg to attach
    
    for i in range(len(blast_disk_size)):
        arg =str.format("crfs -v jfs2 -m /blastfs{} -g testvg -a size={} -A yes", i+1, blast_disk_size[i])
        Log(arg, "INFO")
        rc,out,err=sshexec(lpar_ip,arg,"root","abc123")
        if rc != 0 or out is None:
            LogString = str.format("Failed to create filesystems..{} Error : {}", out,err)
            Log(LogString, "ERROR")
            return -1
            
        arg = str.format("mount /blastfs{} ", i+1)
        Log(arg, "INFO")
        rc,out,err=sshexec(lpar_ip,arg,"root","abc123")
        if rc != 0 or out is None:
            LogString = str.format("Failed to mount blastfs..{} Error : {}", out,err)
            Log(LogString, "ERROR")
            return -1
  

# Copying the exe file from logger
def copy_blast_from_logger(lpar_ip, blast_disk_size):

    arg = "mkdir -p /tmp/blast"
    Log(arg, "INFO")
    rc,out,err=sshexec(lpar_ip,arg,"root","abc123")
    if rc != 0 or out is None:
        LogString = str.format("Failed to create directory /tmp/blast..{} Error : {}", out,err)
        Log(LogString, "ERROR")
        return -1
           
    arg= "mount 9.3.121.20:/images/IO/blast /mnt"
    Log(arg, "INFO")
    rc,out,err=sshexec(lpar_ip,arg,"root","abc123")
    if rc != 0 or out is None:
        LogString = str.format("Failed to mount logger:/images/IO/blast..{} Error : {}", out,err)
        Log(LogString, "ERROR")
        return -1
        
    arg = 'oslevel'
    Log(arg, "INFO")
    rc,out,err=sshexec(lpar_ip,arg,"root","abc123")
    if rc != 0 or out is None:
        LogString = str.format("Failed to get OS Level ..{} Error : {}", out,err)
        Log(LogString, "ERROR")
        return -1
    
    print(out)
    arg = str.format("cp -r /mnt/blast8.14/blast.AIX{}_powerpc /tmp/blast/blast.AIX", out.rstrip())
    Log(arg, "INFO")
    rc,out,err=sshexec(lpar_ip,arg,"root","abc123")
    if rc != 0 or out is None:
        LogString = str.format("Failed to copy Blast exe from Logger ..{} Error : {}", out,err)
        Log(LogString, "ERROR")
        return -1
        
    arg = "touch /tmp/blast/blast_test.lst"
    Log(arg, "INFO")
    rc,out,err=sshexec(lpar_ip,arg,"root","abc123")
    if rc != 0 or out is None:
        LogString = str.format("Failed to create file /tmp/blast/blast_test.lst ..{} Error : {}", out,err)
        Log(LogString, "ERROR")
        return -1
   
    file_contents = " prt_file_timer=4\r\n" 
    for i in range(len(blast_disk_size)):
        file_contents += "WRITE_VERIFY_LOOP MNT_PNT=/blastfs" + str(i+1) + " \r\n"
    
    arg = str.format("echo \"{} \">> /tmp/blast/blast_test.lst", file_contents)
    Log(arg, "INFO")
    rc,out,err=sshexec(lpar_ip,arg,"root","abc123")
    if rc != 0 or out is None:
        LogString = str.format("Failed to write to file /tmp/blast/blast_test.lst  ..{} Error : {}", out,err)
        Log(LogString, "ERROR")
        return -1
    
    arg = "umount -f /mnt"
    Log(arg, "INFO")
    rc,out,err=sshexec(lpar_ip,arg,"root","abc123")
    if rc != 0 or out is None:
        LogString = str.format("Failed to umount /mnt  ..{} Error : {}", out,err)
        Log(LogString, "ERROR")
        return -1


# Starting Blast Workload
def start_blast(lpar_ip):
    
    arg = "nohup /tmp/blast/blast.AIX /tmp/blast/blast_test.lst &"
    Log(arg, "INFO")
    rc,out,err=sshexec_invoke(lpar_ip,arg,"root","abc123")
    if rc != 0 or out is None:
        LogString = str.format("Failed to start blast  ..{} Error : {}", out,err)
        Log(LogString, "ERROR")
        return -1


# Ping check to host
def ping_lpar(host):
    polling = 10
    while polling:
        exit_status = os.system("ping -c 1 " + host)
        if exit_status == 0:
            return 0
            
        time.sleep(10)
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

    sys.stdout.flush()
  
    # print("Checking LPAR status .............................................\n")
    return_status = ping_lpar(tgt_lpar)
    if return_status:
        sys.exit(1)
        
    # print("LPAR is up and running . . . ")  
    blast_disk_attr = check_free_disks(tgt_lpar)
    if blast_disk_attr is -1:
        sys.exit(1)
        
    if create_vg(tgt_lpar, blast_disk_attr[0], blast_disk_attr[1])   is  -1:
        sys.exit(1)
        
    if copy_blast_from_logger(tgt_lpar, blast_disk_attr[1]) is -1:
        sys.exit(1)
    # print("Configuring LPAR ends.............................................\n")
    
    return_status = ping_lpar("logger")
    if return_status:
        sys.exit(1)
        
    # print("Starting Blast Workload on  LPAR....................................\n")
    if start_blast(tgt_lpar) is -1:
        sys.exit(1)
        
    print_and_send_email(email_address, "Blast IO Workload Started Successfully!", tgt_lpar)
    return 0


main()
