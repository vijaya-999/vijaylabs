#! /usr/bin/python
"""get_shared_disks.py

Th is script will get the nodes disks
Developed by: racharys@in.ibm.com
Date: 27/08/2020
Lab : ISST """

import collections
from ssh import sshexec
from ssh import Log
from changediskpvid import change_disk_pvid


# Get pvid of nodes 
def get_disks_pvid(vios_ip, user_name, passwd):
    arg = "ioscli lspv | awk '{ print $2 }'"
    # Log(arg, "INFO")
    rc, out, err = sshexec(vios_ip, arg, user_name, passwd)
    if out is None:
        log_string = str.format("Failed to get pvids of all Disks ..{} Error : {}", out, err)
        Log(log_string, "ERROR")
        return -1

    return out.split('\r\n')


# Get diskname by PVIDs
def get_disks_name(vios_ip, user_name, passwd, pvids):
    arg = str.format("ioscli lspv | grep {} | awk ", pvids) + "'{ print $1 }'"
    # Log(arg, "INFO")
    rc, out, err = sshexec(vios_ip, arg, user_name, passwd)
    if out is None:
        log_string = str.format("Failed to get disk name by PVID ..{} Error : {}", out, err)
        Log(log_string, "ERROR")
        return -1

    disk_pvid = out.rstrip().split()
    return disk_pvid


def get_common_disk_pvid(cluster_nodes, username, passwd):
    shared_pvid = []
    for nodes in cluster_nodes:
        nodes_pvid = get_disks_pvid(nodes, username, passwd)
        if nodes_pvid is -1:
            return -1

        shared_pvid.extend(nodes_pvid)

    # print(shared_pvid)
    shared_pvid_list = [item for item, count in collections.Counter(shared_pvid).items() if count > 1]

    return list(filter(None, shared_pvid_list))


def get_diskname_by_pvid(cluster_nodes, username, passwd, shared_pvid_list):
    shared_disk = []
    for pvids in shared_pvid_list:
        node_disk = get_disks_name(cluster_nodes[0], username, passwd, pvids)
        if node_disk is -1:
            return -1

        shared_disk.extend(node_disk)
    # shared_disk_list = [item for item, count in collections.Counter(shared_pvid).items() if count > 1]
    return shared_disk


def get_free_disks(cluster_nodes, username, passwd):
    arg = "ioscli lspv -free | awk '{ print $1 }'"
    # Log(arg, "INFO")
    rc, out, err = sshexec(cluster_nodes[0], arg, username, passwd)
    if out is None:
        log_string = str.format("Failed to get free disks ..{} Error : {}", out, err)
        Log(log_string, "ERROR")
        return -1

    free_disk = out.rstrip().split()

    return free_disk


# Function to get free size of common disks
def get_free_space(cluster_nodes, username, passwd, shared_disk):
    disk_size = []
    for disk in shared_disk:
        arg = str.format("bootinfo -s {}", disk)
        # Log(arg, "INFO")
        rc, out, err = sshexec(cluster_nodes[0], arg, username, passwd)
        if out is None:
            log_string = str.format("Failed to get free disks ..{} Error : {}", out, err)
            Log(log_string, "ERROR")
            return -1

        disk_size.append(out.rstrip())

    return dict(zip(shared_disk,disk_size))


def get_common_disks(cluster_nodes, username, passwd):

    if change_disk_pvid(cluster_nodes, username, passwd) is -1:
        return -1

    # Get common PVIDs
    shared_pvid_list = get_common_disk_pvid(cluster_nodes, username, passwd)
    if shared_pvid_list is -1:
        return -1

    # Get Common Disk from Common PVIDs
    shared_disk_list = get_diskname_by_pvid(cluster_nodes, username, passwd, shared_pvid_list)
    if shared_pvid_list is -1:
        return -1

    # Get Free disks of the DBN Node using 'lspv -free' command
    free_disk = get_free_disks(cluster_nodes, username, passwd)
    # print(free_disk)

    shared_disk = list(set(shared_disk_list) & set(free_disk))
    shared_disk.remove('NAME')
    # print(shared_disk)

    cluster_disk = get_free_space(cluster_nodes, username, passwd, shared_disk)

    return cluster_disk
