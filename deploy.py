# coding: utf-8
# -*- coding: utf-8 -*-
import subprocess
import collections
import xml.etree.ElementTree as ET
import paramiko
import paramiko as SSH
import os
import sys
import time
from robot.api import logger
from operation_new import create_storage_record
#from operations import create_storage_record
#from Init import Loop_PollLPAR
#from Init import print_and_send_email
import dynamic_WWPN
import dynamic_WWPN_lpar
numvios=0
numvscsi=0
numeth=0
WWPN_lists = [] 
lfc_DRC_slot = []
leth_DRC_slot = []
fc_DRC_slot = []
eth_DRC_slot = []
def CreateLpar(xmlfile):
	tree = ET.parse(xmlfile)
	root = tree.getroot()

	# First Loop read <CONFIG> elements
	for child in root:
		if child.tag == "SYSTEM":
			system = str(child.text)
		elif child.tag == "FSPIP":
			fspip = str(child.text)
		elif child.tag == "HMCHOSTNAME":
			hmchostname = str(child.text)
		elif child.tag == "HMCIP":
			hmcip = str(child.text)
		elif child.tag == "NIMSERVER":
			nimserver = str(child.text)
		elif child.tag == "VIOSERVER":
			numvios+=1
		# Second Loop read <VIOS> and <LPAR> elements
		for child2 in child:
			if child2.tag == "VIOSNAME":
				viosname = str(child2.text) 
			elif child2.tag == "VIOSIP":
				viosip = str(child2.text)
			elif child2.tag == "VIOSGATEWAY":
				viosgateway = str(child2.text)
			elif child2.tag == "VIOSNETMASK":
				viosnetmask = str(child2.text)
			elif child2.tag == "VIOSDNS":
				viosdns = str(child2.text)
			elif child2.tag == "VIOSDOMAIN":
				viosdomain = str(child2.text)
			elif child2.tag == "VIOSCPUMODE":
				vioscpumode = str(child2.text)
			elif child2.tag == "VIOSTYPE":
				vioscputype = str(child2.text)
			elif child2.tag == "VIOSMINCPU":
				viosmincpu = str(child2.text)
			elif child2.tag == "VIOSDESCPU":
				viosdescpu = str(child2.text)
			elif child2.tag == "VIOSMAXCPU":
				viosmaxcpu = str(child2.text)
			elif child2.tag == "VIOSMINVCPU":
				viosminvcpu = str(child2.text)
			elif child2.tag == "VIOSDESVCPU":
				viosdesvcpu = str(child2.text)
			elif child2.tag == "VIOSMAXVCPU":
				viosmaxvcpu = str(child2.text)
			elif child2.tag == "VIOSMEMMODE":
				viosmemmode = str(child2.text)
			elif child2.tag == "VIOSMINMEM":
				viosminmem = str(child2.text)
			elif child2.tag == "VIOSDESMEM":
				viosdesmem = str(child2.text)
			elif child2.tag == "VIOSMAXMEM":
				viosmaxmem = str(child2.text)
			elif child2.tag == "MSP":
				msp = str(child2.text)
			elif child2.tag == "VIOSFCSSLOTS":
				fc_DRC_slot = []
                        	for slot in child2:
                                	if slot.tag == 'SLOT':
                                        	fc_DRC_slot.append(slot.text)
                	elif child2.tag == "VIOSETHSLOTS":
				eth_DRC_slot = []
                        	for slot in child2:
                                	if slot.tag == 'SLOT':
                                        	eth_DRC_slot.append(slot.text)
				LogString = str.format("Create VIOS {}......", viosname)
				Log(LogString, "INFO") 
				# Create VIOS
				if vioscpumode == "dedicated":
					arg = str.format("mksyscfg -r lpar -m {} -i name={}, profile_name={},lpar_env={},min_mem={}, desired_mem={}, max_mem={}, proc_mode={}, min_procs={},desired_procs={}, max_procs={},sharing_mode={},conn_monitoring={},boot_mode={},max_virtual_slots={},sync_curr_profile={}",system, viosname, viosname, "vioserver", viosminmem, viosdesmem, viosmaxmem,"ded",viosmincpu,viosdescpu, viosmaxcpu,"share_idle_procs_always","1","norm","1000","1")
				else:
					arg = str.format("mksyscfg -r lpar -m {} -i name={}, profile_name={},lpar_env={},min_mem={}, desired_mem={}, max_mem={}, proc_mode={}, min_procs={},desired_procs={}, max_procs={},min_proc_units={},desired_proc_units={},max_proc_units={},uncap_weight={},sharing_mode={},conn_monitoring={},boot_mode={},max_virtual_slots={},sync_curr_profile={}",system, viosname, viosname, "vioserver", viosminmem, viosdesmem, viosmaxmem,"shared",viosminvcpu,viosdesvcpu,viosmaxvcpu,viosmincpu,viosdescpu, viosmaxcpu,"128","uncap","1","norm","1000","1")
				rc,out,err = sshexec(hmcip,arg,"hscroot","abc123")
				if rc != 0:
					LogString = str.format("mksyscfg failed with error {} {}", out,err)
					Log(LogString, "ERROR") 
					return -1	
				if msp != "NA":
					arg = str.format("chsyscfg -r prof -m {} -i name={},lpar_name={},msp={}",system,viosname,viosname,msp)
					rc,out,err = sshexec(hmcip,arg,"hscroot","abc123")
					if rc != 0:
						LogString = str.format("chsyscfg failed to set MSP on VIOS {} {}", out,err)
                                       		Log(LogString, "ERROR")
						return -1
				#Assign Fiber Channelphysical adapters to VIOS's
				for i in range(len(fc_DRC_slot)):
					if fc_DRC_slot[i] != "NA":
						arg = str.format("lshwres -r io -m {} --rsubtype slot -F phys_loc,description,lpar_id,drc_index,drc_name|grep -w {}",system,fc_DRC_slot[i])
						LogString = str.format("Assign Fiber Channel physical adapter to VIOS {}......",viosname)
						Log(LogString, "INFO") 
						rc,out,err = sshexec(hmcip,arg,"hscroot","abc123")
                                		if rc != 0:
							LogString = str.format("lshwres failed with to list the fiber chanel adapter {} {}", out,err)
							Log(LogString, "INFO") 
							exit(1)

						string = out.find("none")
						string1 = out.find(fc_DRC_slot[i])
						array = out.split(",")
						concat = array[3] + "/none/1"
						if string > 0 and string1 > 0:
							arg = str.format("chsyscfg -r prof -m {} -i name={},lpar_name={},io_slots+={}",system,viosname,viosname,concat)
							rc,out,err = sshexec(hmcip,arg,"hscroot","abc123")
                                                	if rc != 0:
								LogString = str.format("chsyscfg failed to assign the fiber channel adapter {} {}", out,err)
								Log(LogString, "ERROR") 
								exit(1)

				 #Assign ethernet physical adapters to VIOS's
				for i in range(len(eth_DRC_slot)):
					if eth_DRC_slot[i] != "NA":
						arg = str.format("lshwres -r io -m {} --rsubtype slot -F phys_loc,description,lpar_id,drc_index,drc_name|grep -w {}",system,eth_DRC_slot[i])
						LogString = str.format("Assign Ethernet physical adapter to VIOS {}......", viosname)
						Log(LogString, "INFO") 
						rc,out,err = sshexec(hmcip,arg,"hscroot","abc123")
                                                if rc != 0:
							LogString = str.format("lshwres failed with to list the Ethernet Adapter {} {}", out,err)
							Log(LogString, "ERROR") 
							exit(1)
						string = out.find("none")
						string1 = out.find(eth_DRC_slot[i])
						array1 = out.split(",")
						concat = array1[3] + "/none/1"
						if string > 0 and string1 > 0:
							arg = str.format("chsyscfg -r prof -m {} -i name={},lpar_name={},io_slots+={}",system,viosname,viosname,concat)
							rc,out,err = sshexec(hmcip,arg,"hscroot","abc123")
							if rc != 0:
								LogString = str.format("chsyscfg failed to assign the fiber channel adapter {} {}", out,err)
								Log(LogString, "ERROR") 
								exit(1)
			elif child2.tag == "LPARNAME":
				lparname = child2.text
			elif child2.tag == "LPARIP":
				lparip = child2.text
			elif child2.tag == "LPARGATEWAY":
				lpargateway = child2.text
			elif child2.tag == "LPARNETMASK":
				lparnetmask = child2.text
			elif child2.tag == "LPARCPUMODE":
				lparcpumode = child2.text
			elif child2.tag == "LPARCPUTYPE":
				lparcputype = child2.text
			elif child2.tag == "LPARMINCPU":
				lparmincpu = child2.text
			elif child2.tag == "LPARDESCPU":
				lpardescpu = child2.text
			elif child2.tag == "LPARMAXCPU":
				lparmaxcpu = child2.text
			elif child2.tag == "LPARMINVCPU":
				lparminvcpu = child2.text
			elif child2.tag == "LPARDESVCPU":
				lpardesvcpu = child2.text
			elif child2.tag == "LPARMAXVCPU":
				lparmaxvcpu = child2.text
			elif child2.tag == "LPARMEMMODE":
				lparmemmode = child2.text
			elif child2.tag == "LPARMINMEM":
				lparminmem = child2.text
			elif child2.tag == "LPARDESMEM":
				lpardesmem = child2.text
			elif child2.tag == "LPARMAXMEM":
				lparmaxmem = child2.text
			elif child2.tag == "SECUREBOOT":
				secureboot = child2.text
			elif child2.tag == "AME":
				memexp = child2.text
			elif child2.tag == "REMOTERESTART":
				rrestart = child2.text
			elif child2.tag == "LPARSFCSSLOTS":
                        	for slot in child2:
                                	if slot.tag == 'SLOT':
                                        	lfc_DRC_slot.append(slot.text)
                	elif child2.tag == "LPARETHSLOTS":
                        	for slot in child2:
                                	if slot.tag == 'SLOT':
                                        	leth_DRC_slot.append(slot.text)

				LogString = str.format("About to create LPAR {}", lparname)
                                Log(LogString, "INFO")
				# Create LPAR 
				if lparcpumode == "dedicated":
					arg = str.format("mksyscfg -r lpar -m {} -i name={}, profile_name={},lpar_env={},min_mem={}, desired_mem={}, max_mem={}, proc_mode={}, min_procs={},desired_procs={}, max_procs={},sharing_mode={},conn_monitoring={},boot_mode={},max_virtual_slots={}",system, lparname, lparname, "aixlinux", lparminmem, lpardesmem, lparmaxmem,"ded",lparmincpu,lpardescpu, lparmaxcpu,"share_idle_procs_always","1","norm","500")
				else:
					arg = str.format("mksyscfg -r lpar -m {} -i name={}, profile_name={},lpar_env={},min_mem={}, desired_mem={}, max_mem={}, proc_mode={}, min_procs={},desired_procs={}, max_procs={},min_proc_units={},desired_proc_units={},max_proc_units={},uncap_weight={},sharing_mode={},conn_monitoring={},boot_mode={},max_virtual_slots={}",system, lparname, lparname, "aixlinux", lparminmem, lpardesmem, lparmaxmem,"shared",lparminvcpu,lpardesvcpu,lparmaxvcpu,lparmincpu,lpardescpu, lparmaxcpu,"128","uncap","1","norm","500")
				rc,out,err = sshexec(hmcip,arg,"hscroot","abc123")
				if rc != 0:
					LogString = str.format("mksyscfg failed to create LPAR {} {}", out,err)
                                        Log(LogString, "ERROR")
					exit(1)

				if secureboot != "NA":	
					arg = str.format("chsyscfg -r prof -m {} -i name={},lpar_name={},secure_boot={}",system,lparname,lparname,secureboot)
					rc,out,err = sshexec(hmcip,arg,"hscroot","abc123")
					if rc != 0:
						LogString = str.format("chsyscfg failed to set secureboot on LPAR {} {}", out,err)
                                       		Log(LogString, "ERROR")
						return -1
				
				if memexp != "NA":	
					arg = str.format("chsyscfg -r prof -m {} -i name={},lpar_name={},mem_expansion={}",system,lparname,lparname,memexp)
					rc,out,err = sshexec(hmcip,arg,"hscroot","abc123")
					if rc != 0:
						LogString = str.format("chsyscfg failed to set Active Memory Expansion on LPAR {} {}", out,err)
                                       		Log(LogString, "ERROR")
						return -1
				
				if rrestart != "NA":	
					arg = str.format("chsyscfg -r prof -m {} -i name={},lpar_name={},remote_restart_capable={}",system,lparname,lparname,rrestart)
					rc,out,err = sshexec(hmcip,arg,"hscroot","abc123")
					if rc != 0:
						LogString = str.format("chsyscfg failed to set Remote Restart on LPAR {} {}", out,err)
                                       		Log(LogString, "ERROR")
						return -1
				#Assign fiber channel physical adapters to LPAR's
				for i in range(len(lfc_DRC_slot)):
					if lfc_DRC_slot[i] != "NA":
						arg = str.format("lshwres -r io -m {} --rsubtype slot -F unit_phys_loc,bus_id,phys_loc,description,lpar_id,drc_index|grep {}",system,lfc_DRC_slot[i])
						rc,out,err = sshexec(hmcip,arg,"hscroot","abc123")
						if rc != 0:
							LogString = str.format("lshwres failed to list fiber channel adapters {} {}", out,err)
                                       			Log(LogString, "ERROR")
							exit(1)
						string = out.find("none")
						string1 = out.find(lfc_DRC_slot[i])
						concat = lfc_DRC_slot[i] + "/none/1"
						if string > 0 and string1 > 0:
							arg = str.format("chsyscfg -r prof -m {} -i name={},lpar_name={},io_slots+={}",system,lparname,lparname,concat)
							rc,out,err = sshexec(hmcip,arg,"hscroot","abc123")
							if rc != 0:
								LogString = str.format("chsyscfg failed to assign fiber channel adapters {} {}", out,err)
                                       				Log(LogString, "ERROR")
								exit(1)
				#Assign ethernet physical adapters to LPAR's
				for i in range(len(leth_DRC_slot)):
					if leth_DRC_slot[i] != "NA":
						arg = str.format("lshhwres -r io -m {} --rsubtype slot -F unit_phys_loc,bus_id,phys_loc,description,lpar_id,drc_index|grep {}",system,leth_DRC_slot[i])
						rc,out,err = sshexec(hmcip,arg,"hscroot","abc123")
						if rc != 0:
							LogString = str.format("lshwres failed to list ethernet adapters  {} {}", out,err)
                                       			Log(LogString, "ERROR")
							exit(1)
						string = out.find("none")
						string1 = out.find(leth_DRC_slot[i])
						concat = leth_DRC_slot[i] + "/none/1"
						if string > 0 and string1 > 0:
							arg = str.format("chsyscfg -r prof -m {} -i name={},lpar_name={},io_slots+={}",system,lparname,lparname,concat)
							sshexec(hmcip,arg,"hscroot","abc123")
							rc,out,err = sshexec(hmcip,arg,"hscroot","abc123")
							if rc != 0:
								LogString = str.format("chsyscfg failed to add ethernet adapters  {} {}", out,err)
                                       				Log(LogString, "ERROR")
								exit(1)

def ViosStorageAlloc(filename, username):
    tree = ET.parse(filename)
    root = tree.getroot()
    vios_values = list()
    lpar_values = list()

    for child in root:
            # print(child.tag)
            if child.tag == 'SYSTEM':
                SYSTEM = child.text
            if child.tag == 'HMCIP':
                HMC = child.text
            for child2 in child:
                # print(child2.tag)
                if child2.tag == 'VIOSFCSSLOTS':
                    DRC_slot = []
                    for slot in child2:
			if slot.text != "NA" and  slot.tag == 'SLOT':
                            arg = str.format("lshwres -r io -m {} --rsubtype slot -F phys_loc,description,lpar_id,drc_index,drc_name|grep -w {}",SYSTEM,slot.text)
			    print(arg)
                            rc,out,err = sshexec(HMC,arg,"hscroot","abc123")
                            if rc != 0:
                                LogString = str.format("lshwres failed with to list the fiber chanel adapter {} {}", out,err)
                                Log(LogString, "INFO")
                                exit(1)
                            array = out.split(",")[4]
			    array = array[:-2]
                            DRC_slot.append(array)
                    	    print("CALLING DYNAMIC WWPN script")
                            print(SYSTEM, HMC, DRC_slot)
                            WWPN_list=dynamic_WWPN.WWPN(HMC, SYSTEM, DRC_SLOT=DRC_slot)
                            print(WWPN_list)
                if child2.tag == 'VIOSNAME':
                    name=child2.text
                if child2.tag == 'STORAGE' and child.tag=='VIOS':
                    for child3 in child2:
			print("inside child3")
                        storage_value=(child3.text).split(",")
                        L=7
			if storage_value[0] != 'NA':
				dict_STORAGE_DETAIL = dict()
				dict_STORAGE_DETAIL['name'] = name
				dict_STORAGE_DETAIL['quantity'] = storage_value[0]
				dict_STORAGE_DETAIL['size'] = storage_value[1]+'G'
				if child3.tag=='VIOSROOTVG':
				    dict_STORAGE_DETAIL['share'] = '0'
				    dict_STORAGE_DETAIL['type'] = 'root'
				elif child3.tag=='VIOSDATAVG':
				    dict_STORAGE_DETAIL['type'] = 'non-root'
				    if storage_value[2]=='shared':
					dict_STORAGE_DETAIL['share'] = '1'
				    else:
					dict_STORAGE_DETAIL['share'] = '0'

				WWPN_dict = dict()
				count = 1
				for _i in range(3, len(storage_value) - 1):
				    WWPN_dict['wwpn%d' % (count)] = storage_value[_i]
				    count += 1
				for _i in range(0,len(WWPN_list)):
				    WWPN_dict['wwpn%d' % (count)] = WWPN_list[_i]
				    count +=1
				    print("count is %d" % count)	
				print(WWPN_dict)
				"""
				WWPN_dict['wwpn1'] = storage_value[3]
				if len(storage_value)>= 5 and storage_value[4] != "":
				    WWPN_dict['wwpn2'] = storage_value[4]
				if len(storage_value)>=6 and storage_value[5] != "":
				    WWPN_dict['wwpn3'] = storage_value[5]
				if len(storage_value) >= 7 and storage_value[6] != "":
				    WWPN_dict['wwpn4'] = storage_value[6]
				#dict_STORAGE_DETAIL['share'] = storage_value[-1]
				"""

				dict_STORAGE_DETAIL['wwpns'] = WWPN_dict
				dict_STORAGE_DETAIL['pool'] = storage_value[-1]
				vios_values.append(dict_STORAGE_DETAIL)
    print(vios_values)
    print("calling storage_record")
    create_storage_record(vios_values, username)


def LparStorageAlloc(filename,username):
    tree = ET.parse(filename)
    root = tree.getroot()
    vios_values = list()
    lpar_values = list()

    for child in root:
            # print(child.tag)
            if child.tag == 'SYSTEM':
                SYSTEM = child.text
            if child.tag == 'HMCHOSTNAME':
                HMC = child.text
            for child2 in child:
                if child2.tag == "LPARNAME":
                    lparname=child2.text
                if child2.tag == 'LPARSTORAGE' and child.tag == 'LPAR':
                    for child3 in child2:
                        print("nside child3.tag")
                        storage_value=(child3.text).split(",")
                        L=7
			if storage_value[0] != 'NA':
				dict_STORAGE_DETAIL = dict()
				dict_STORAGE_DETAIL['name'] = lparname
				dict_STORAGE_DETAIL['quantity'] = storage_value[0]
				dict_STORAGE_DETAIL['size'] = storage_value[1]+'G'
				WWPN_list = dynamic_WWPN_lpar.WWPN_LPAR(HMC, SYSTEM, LPAR_NAME=lparname)
				if child3.tag == 'LPARROOTVG':
				    dict_STORAGE_DETAIL['share'] = '0'
				    dict_STORAGE_DETAIL['type'] = 'root'
				elif child3.tag == 'LPARDATAVG':
				    dict_STORAGE_DETAIL['type'] = 'non-root'
				    if storage_value[2] == 'shared':
					dict_STORAGE_DETAIL['share'] = '1'
				    else:
					dict_STORAGE_DETAIL['share'] = '0'
				WWPN_dict = dict()
				count = 1
				for _i in range(3, len(storage_value)-1):
				    WWPN_dict['wwpn%d'%(count)] = storage_value[_i]
				    count += 1
				for _i in range(0,len(WWPN_list)):
				    WWPN_dict['wwpn%d' % (count)] = WWPN_list[_i]
				    count +=1
				    print("count is %d" % count)	
				print(WWPN_dict)
				"""
				WWPN_dict['wwpn1'] = storage_value[3]
				if len(storage_value)>= 5 and storage_value[4] != "":
				    WWPN_dict['wwpn2'] = storage_value[4]
				if len(storage_value) >= 6 and storage_value[5] != "":
				    WWPN_dict['wwpn3'] = storage_value[5]
				if len(storage_value) >= 7 and storage_value[6] != "":
				    WWPN_dict['wwpn4'] = storage_value[6]
				#dict_STORAGE_DETAIL['share'] = storage_value[-1]
				"""
				dict_STORAGE_DETAIL['wwpns'] = WWPN_dict
				dict_STORAGE_DETAIL['pool'] = storage_value[-1]
                        	lpar_values.append(dict_STORAGE_DETAIL)

    				print(lpar_values)
    				print("calling create_storage_record")
   	   # if len(lpar_values) > 0:
    				create_storage_record(lpar_values, username)
				#lpar_values = []
				#dict_STORAGE_DETAIL = {}


# for x in list_of_value:
#     for i,j in x.items():
#         i = unicode(i, "utf-8")
#         j=j.decode('utf-8')
# JSON_DATA=json.dumps(list_of_value)
#  print(JSON_DATA)
#
#   y = json.loads(JSON_DATA)

	
#Create Virtual Adapters
def CreateVirtualAdapter(xmlfile):
	tree = ET.parse(xmlfile)
	root = tree.getroot()
	for child in root:
		if child.tag == "SYSTEM":
			system = str(child.text)
		elif child.tag == "HMCIP":
			hmcip = str(child.text)
		for child2 in child:
			if child2.tag == "VIOSNAME":
				viosname = str(child2.text)
			elif child2.tag == "VIOSIP":
				viosip = str(child2.text)
			elif child2.tag == "LPARNAME":
				lparname = child2.text
			elif child2.tag == "LPARIP":
				lparip = child2.text
			for child3 in child2:
				if child3.tag == "VIOSETHVIRSLOT":
					viosvirethslot = child3.text
				elif child3.tag == "PVID":
					viospvid = child3.text
				elif child3.tag == "IEEE802":
					viosieee = child3.text
				elif child3.tag == "ADDVLANID":
					viosaddvlanid = child3.text
				elif child3.tag == "VIRSWITCH":
					virswitch = child3.text
				elif child3.tag == "TRUNKPRI":
					trunkpri = child3.text
				elif child3.tag == "CNTLCHANSLOT":
					cntlchanslot = child3.text
				elif child3.tag == "CNTLCHANPVID":
					cntlchanpvid = child3.text
				elif child3.tag == "SEA":
					sea = child3.text
					if viosvirethslot != "NA" and viospvid != "NA":
						LogString = str.format("About to create virtual ethernet adapter with slot id {} and pvid {}....", viosvirethslot, viospvid)
                                       		Log(LogString, "INFO")
						if viosieee != "NA" and viosaddvlanid != "NA" and trunkpri != "NA" and virswitch != "NA":
							string = viosvirethslot + '/' + viosieee  + '/' + viospvid + '/' + viosaddvlanid + '/' + trunkpri + '/' + '1' + '/' + virswitch
							print(string)
						elif viosieee == "NA" and viosaddvlanid == "NA" and trunkpri != "NA" and virswitch != "NA":
							string = viosvirethslot + '/' + '0'  + '/' + viospvid + '/' +  '/' + trunkpri + '/' + '1' + '/' + virswitch
						elif viosieee != "NA" and viosaddvlanid == "NA" and trunkpri != "NA" and virswitch != "NA":
							string = viosvirethslot + '/' + viosieee  + '/' + viospvid + '/' +  '/' + trunkpri + '/' + '1' + '/' + virswitch
						print(string)
						arg = str.format("chsyscfg -r prof -m {} -i name={},lpar_name={},virtual_eth_adapters+={}",system,viosname,viosname,string)
                                       		Log(arg, "INFO")
						rc,out,err = sshexec(hmcip,arg,"hscroot","abc123")
						if rc != 0:
							LogString = str.format("Virtual Ethernet adapter creation failed with error  {} {}", out,err)
                                       			Log(LogString, "ERROR")
							exit(1)

					if cntlchanpvid != "NA" and cntlchanslot != "NA":
						LogString = str.format("About to create control channel adapter with slot id {} and pvid {}....", cntlchanslot, cntlchanpvid)
                                       		Log(LogString, "INFO")
						string = cntlchanslot + '/' + '0'  + '/' + cntlchanpvid + '/' +  '/' + '0' + '/' + '1' + '/' + virswitch
						arg = str.format("chsyscfg -r prof -m {} -i name={},lpar_name={},virtual_eth_adapters+={}",system,viosname,viosname,string)
						rc,out,err = sshexec(hmcip,arg,"hscroot","abc123")
						if rc != 0:
							LogString = str.format("control channel  adapter creation failed with error {} {}", out,err)
                                       			Log(LogString, "ERROR")
							exit(1)
				elif child3.tag == "VIOSVSCSIVIRSLOT":
					viosvirvscsislot = child3.text
				elif child3.tag == "LPARNAME":
					lparname = child3.text
				elif child3.tag == "VIOSVSCSIREMOTEVSLOT":
					viosvscsiremotevslot = child3.text
					if viosvirvscsislot != "NA" and lparname != "NA" and viosvscsiremotevslot != "NA":
						LogString = str.format("About to vscsi adapter with slot {}....", viosvirvscsislot)
                                       		Log(LogString, "INFO")
						string = viosvirvscsislot + '/' + "server" + '/' + '/' + lparname + '/' + viosvscsiremotevslot + '/' + '1'
						arg = str.format("chsyscfg -r prof -m {} -i name={},lpar_name={},virtual_scsi_adapters+={}",system,viosname,viosname,string)
						rc,out,err = sshexec(hmcip,arg,"hscroot","abc123")
						if rc != 0:
							LogString = str.format("vscsi  adapter creation on vios failed with error {} {}", out,err)
                                       			Log(LogString, "ERROR")
							exit(1)
				elif child3.tag == "VIOSVFCVIRSLOT":
					viosvirvfcslot = child3.text
				elif child3.tag == "LPARNAME":
					lparname = child3.text
				elif child3.tag == "VIOSVFCREMOTEVSLOT":
					viosvfcremotevslot = child3.text
					if viosvirvfcslot != "NA" and lparname != "NA" and viosvfcremotevslot != "NA":
						LogString = str.format("About to vfc adapter with slot {}....", viosvirvfcslot)
                                       		Log(LogString, "INFO")
                                        	string = viosvirvfcslot + '/' + "server" + '/' + '/' + lparname +  '/' + viosvfcremotevslot + '/' + '/' + '1'
                                		arg = str.format("chsyscfg -r prof -m {} -i name={},lpar_name={},virtual_fc_adapters+={}",system,viosname,viosname,string)
						rc,out,err = sshexec(hmcip,arg,"hscroot","abc123")
						if rc != 0:
							LogString = str.format("vfc adapter creation on vios failed with error {} {}", out,err)
                                       			Log(LogString, "ERROR")
							exit(1)
				elif child3.tag == "LPARETHVIRSLOT":
					lparvirethslot = child3.text
				elif child3.tag == "LPARPVID":
					lparpvid = child3.text
				elif child3.tag == "LPARIEEE802":
					lparieee = child3.text
				elif child3.tag == "LPARADDVLANID":
					lparaddvlanid = child3.text
				elif child3.tag == "LPARVIRSWITCH":
					lparvirswitch = child3.text
					if lparpvid != "NA" and lparvirethslot != "NA": 
						LogString = str.format("LPAR:About to create virtual ethernet adapter with slot {} and {}....", lparvirethslot, lparpvid)
                                       		Log(LogString, "INFO")
						if lparieee != "NA" and lparaddvlanid != "NA" and lparvirswitch != "NA":
							string = lparvirethslot + '/' + lparieee  + '/' + lparpvid + '/' + lparaddvlanid + '/' + '0' + '/' + '1' + '/' + lparvirswitch
						elif lparieee == "NA" and lparaddvlanid == "NA" and lparvirswitch != "NA":
							string = lparvirethslot + '/' + '0'  + '/' + lparpvid + '/' +  '/' + '0' + '/' + '1' + '/' + lparvirswitch
						elif lparieee != "NA" and lparaddvlanid == "NA" and lparvirswitch != "NA":
							string = lparvirethslot + '/' + lparieee  + '/' + lparpvid + '/' +  '/' + '0' + '/' + '1' + '/' + lparvirswitch
						arg = str.format("chsyscfg -r prof -m {} -i name={},lpar_name={},virtual_eth_adapters+={}",system,lparname,lparname,string)
						rc,out,err = sshexec(hmcip,arg,"hscroot","abc123")
						if rc != 0:
							LogString = str.format("Virtual ethernet adapter creatin on LPAR  failed with error {} {}", out,err)
                                       			Log(LogString, "ERROR")
							exit(1)
				elif child3.tag == "LPARVSCSIVIRSLOT":
					lparvirvscsislot = child3.text
				elif child3.tag == "VIOSNAME":
					viosname = child3.text
				elif child3.tag == "LPARVSCSIREMOTEVSLOT":
					lparvscsiremotevslot = child3.text
					if lparvirvscsislot != "NA" and viosname != "NA" and lparvscsiremotevslot != "NA":
						LogString = str.format("LPAR:About to create virtual scsi adapter with slot {}....", lparvirvscsislot)
                                       		Log(LogString, "INFO")
						string = lparvirvscsislot + '/' + "client" + '/' + '/' + viosname  + '/' + lparvscsiremotevslot + '/' + '1'
						arg = str.format("chsyscfg -r prof -m {} -i name={},lpar_name={},virtual_scsi_adapters+={}",system,lparname,lparname,string)
						rc,out,err = sshexec(hmcip,arg,"hscroot","abc123")
						if rc != 0:
							LogString = str.format("Virtual scsi adapter creatin on LPAR  failed with error {} {}", out,err)
                                       			Log(LogString, "ERROR")
							exit(1)
				elif child3.tag == "LPARVFCVIRSLOT":
					lparvirvfcslot = child3.text
				elif child3.tag == "VIOSNAME":
					viosname= child3.text
				elif child3.tag == "LPARVFCREMOTEVSLOT":
					lparvfcremotevslot = child3.text
					if lparvirvfcslot != "NA" and viosname != "NA" and lparvfcremotevslot != "NA":
						LogString = str.format("LPAR:About to create virtual fiber channel  adapter with slot {}....", lparvirvfcslot)
                                       		Log(LogString, "INFO")
						string = lparvirvfcslot + '/' + "client" + '/' + '/' + viosname  + '/' + lparvfcremotevslot + '/' + '/' + '1'
						arg = str.format("chsyscfg -r prof -m {} -i name={},lpar_name={},virtual_fc_adapters+={}",system,lparname,lparname,string)
						rc,out,err = sshexec(hmcip,arg,"hscroot","abc123")
						if rc != 0:
							LogString = str.format("Virtual fiber channel  adapter creatin on LPAR  failed with error {} {}", out,err)
                                       			Log(LogString, "ERROR")
                                            		exit(1)

def InstallVIOS(xmlfile):
	tree = ET.parse(xmlfile)
	root = tree.getroot()

	for child in root:
		if child.tag == "SYSTEM":
			system = str(child.text)
		elif child.tag == "HMCIP":
			hmcip = str(child.text)
		elif child.tag == "NIMSERVER":
			nimserver = str(child.text)
		elif child.tag == "VIOSMKSYSB":
			viosmksysb = str(child.text)
		elif child.tag == "VIOSSPOT":
			viosspot = str(child.text)
		elif child.tag == "VIOSDNS":
			viosdns = str(child.text)
		elif child.tag == "VIOSDOMAIN":
			viosdomain = str(child.text)
		for child2 in child:
			if child2.tag == "VIOSNAME":
				viosname = str(child2.text)
			elif child2.tag == "VIOSIP":
				viosip = str(child2.text)
			elif child2.tag == "VIOSGATEWAY":
				viosgateway = str(child2.text)
			elif child2.tag == "VIOSNETMASK":
				viosnetmask = str(child2.text)
			elif child2.tag == "BOOTPVID":
				bootpvid = str(child2.text)
		
				#Install Vios
				LogString = str.format("VIOS:about to install {} with {} build....", viosname, viosmksysb)
                                Log(LogString, "INFO")

				arg = str.format("/tmp/net_install {} {} \"hscroot\" {} {} {} {} {} {} {}",viosmksysb,viosspot,hmcip,viosname,viosip,nimserver,viosnetmask,viosgateway,system,bootpvid)
				rc,out,err = sshexec(nimserver,arg,"root","lionking")
                                if rc != 0:
					LogString = str.format("Installation of vios failed with error {} {}, Check /tmp/netinstall and /tmp/netinstall1 on isstnim02 for the cause of failure", out,err)
                                       	Log(LogString, "INFO")

def InstallLPAR(xmlfile):
	tree = ET.parse(xmlfile)
	root = tree.getroot()

	for child in root:
		if child.tag == "SYSTEM":
			system = str(child.text)
		elif child.tag == "HMCIP":
			hmcip = str(child.text)
		elif child.tag == "NIMSERVER":
			nimserver = str(child.text)
		elif child.tag == "LPARDNS":
			lpardns = str(child.text)
		elif child.tag == "LPARDOMAIN":
			lpardomain = str(child.text)
		for child2 in child:
			if child2.tag == "LPARNAME":
				lparname = str(child2.text)
			elif child2.tag == "LPARIP":
				lparip = str(child2.text)
			elif child2.tag == "LPARGATEWAY":
				lpargateway = str(child2.text)
			elif child2.tag == "LPARNETMASK":
				lparnetmask = str(child2.text)
			elif child2.tag == "LPPSOURCE":
				lppsource = str(child2.text)
			elif child2.tag == "LPARSPOT":
				lparspot = str(child2.text)
			elif child2.tag == "NWMACADDR":
				nwmacaddr = str(child2.text)
			elif child2.tag == "VLANID":
				vlanid = str(child2.text)
			elif child2.tag == "INSTALL":
				if str(child2.text) == 'N':
					LogString = str.format("Skipping LPAR {} Installation as defined in the XML", lparname)
                                	Log(LogString, "INFO")
					break
			elif child2.tag == "BOOTPVID":
				bootpvid = str(child2.text)
				#time.sleep(300)
				#Install LPAR 
				LogString = str.format("LPAR:about to install {} with {} build....", lparname, lppsource)
                                Log(LogString, "INFO")

				arg = str.format("/tmp/net_install.client {} {} \"hscroot\" {} {} {} {} {} {} {} {} {} {}",lppsource,lparspot,hmcip,lparname,lparip,nimserver,lparnetmask,lpargateway,system,bootpvid, nwmacaddr,vlanid)
				rc,out,err = sshexec(nimserver,arg,"root","lionking")
                                if rc != 0:
					LogString = str.format("Installation of lpar failed with error {} {}, Check /tmp/netinstall and /tmp/netinstall1 on isstnim02 for the cause of failure", out,err)
                                       	Log(LogString, "INFO")

def ViosSetPassword(xmlfile):
	tree = ET.parse(xmlfile)
        root = tree.getroot()
	for child in root:
                if child.tag == "SYSTEM":
                        system = str(child.text)
                elif child.tag == "HMCIP":
                        hmcip = str(child.text)
                for child2 in child:
                        if child2.tag == "VIOSNAME":
                                viosname = str(child2.text)
                        elif child2.tag == "VIOSIP":
                                viosip = str(child2.text)
				ret = subprocess.call(["./vioslogin.exp",hmcip,system,viosname])
				


def CreateMap(xmlfile):
        tree = ET.parse(xmlfile)
        root = tree.getroot()

	for child in root:
		if child.tag == "SYSTEM":
			system = str(child.text)
		elif child.tag == "HMCIP":
			hmcip = str(child.text)
		for child2 in child:
			if child2.tag == "VIOSNAME":
				viosname = str(child2.text)
			elif child2.tag == "VIOSIP":
				viosip = str(child2.text)
			elif child2.tag == "VIOSGATEWAY":
                                viosgateway = str(child2.text)
                        elif child2.tag == "VIOSNETMASK":
                                viosnetmask = str(child2.text)
                        elif child2.tag == "VIOSDNS":
                                viosdns = str(child2.text)
                        elif child2.tag == "VIOSDOMAIN":
                                viosdomain = str(child2.text)
			elif child2.tag == "VIOSFCSSLOTS":
				DRC_slot = []
                                array = []
                                for slot in child2:
					if slot.text != "NA" and  slot.tag == 'SLOT':
                            			arg = str.format("lshwres -r io -m {} --rsubtype slot -F phys_loc,description,lpar_id,drc_index,drc_name|grep -w {}",system,slot.text)
                            			rc,out,err = sshexec(hmcip,arg,"hscroot","abc123")
                            			if rc != 0:
                                			LogString = str.format("lshwres failed with to list the fiber chanel adapter {} {}", out,err)
                                			Log(LogString, "INFO")
                                			exit(1)
                            			array = out.split(",")
                            			DRC_slot.append(array[3])
                    	    			print("CALLING DYNAMIC WWPN script")
                            			print(system, hmcip, DRC_slot)
                            			WWPN_list=dynamic_WWPN.WWPN(hmcip, system, DRC_SLOT=DRC_slot)
                            			print(WWPN_list)
						WWPN_lists.append(WWPN_list)
                        elif child2.tag == "VIOSETHSLOTS":
                                eth_DRC_slot = []
                                for slot in child2:
                                        if slot.tag == 'SLOT':
                                                eth_DRC_slot.append(slot.text)
			elif child2.tag == "LPARNAME":
				lparname = child2.text
			elif child2.tag == "LPARIP":
				lparip = child2.text
			elif child2.tag == "LPARSFCSSLOTS":
                                for slot in child2:
                                        if slot.tag == 'SLOT':
                                                lfc_DRC_slot.append(slot.text)
                        elif child2.tag == "LPARETHSLOTS":
                                for slot in child2:
                                        if slot.tag == 'SLOT':
                                                leth_DRC_slot.append(slot.text)
			for child3 in child2:
				if child3.tag == "VIOSETHVIRSLOT":
					viosvirethslot = child3.text
				elif child3.tag == "PVID":
					viospvid = child3.text
				elif child3.tag == "IEEE802":
					viosieee = child3.text
				elif child3.tag == "ADDVLANID":
					viosaddvlanid = child3.text
				elif child3.tag == "VIRSWITCH":
					virswitch = child3.text
				elif child3.tag == "TRUNKPRI":
					trunkpri = child3.text
				elif child3.tag == "CNTLCHANSLOT":
					cntlchanslot = child3.text
				elif child3.tag == "CNTLCHANPVID":
					cntlchanpvid = child3.text
				elif child3.tag == "SEAPHYSPORT":
					port = child3.text
				elif child3.tag == "SEAIP":
					seaip = child3.text
				elif child3.tag == "SEA":
					sea = child3.text
					if sea == '1':
						if viosvirethslot != "NA" and viospvid != "NA":
                                                        arg = str.format("ioscli lsmap -all -net | grep -w C{} | cut -d\" \" -f1 | tr -d ' '",viosvirethslot)
                                                        rc,out,err = sshexec(viosip,arg,"padmin","padmin")
                                                        if rc != 0:
                                                                LogString = str.format("lsmap failed with to list the virtual ethernet adapter {} {}", out,err)
                                                                Log(LogString, "ERROR")
                                                                exit(1)
                                                        vadapter = out.rstrip()
                                                        arg = str.format("ioscli lsmap -all -net | grep -w C{} | cut -d\" \" -f1",cntlchanslot)
                                                        rc,out,err = sshexec(viosip,arg,"padmin","padmin")
                                                        if rc != 0:
                                                                LogString = str.format("lsmap failed with to list the virtual ethernet adapter {} {}", out,err)
                                                                Log(LogString, "ERROR")
                                                                exit(1)

							entadapter = get_adapter(viosip, port, type='ent')
							print(entadapter)
							interface = entadapter.replace('t','')
							print(interface)
                                                        ret = subprocess.call(["./ifdown.exp",hmcip,system,viosname, interface])
                                                        #ret = subprocess.call(["./mkvdev.exp",hmcip,system,viosname,vadapter,viospvid])
                                                        LogString = str.format("Creating SEA on {}......", viosname)
                                                        Log(LogString, "INFO")
                                                        if cntlchanslot == "NA":
                                                                ret = subprocess.call(["./mkvdevsea.exp",hmcip,system,viosname,vadapter,viospvid, entadapter])
                                                        else:
                                                                ret = subprocess.call(["./mkvdevseacntlchan.exp",hmcip,system,viosname,vadapter,viospvid,cntlchanadapter, entadapter])

                                                        #configure ip on SEA
							if seaip != "NA":
                                                        	LogString = str.format("Assgning IP on  SEA {}......", viosname)
                                                        	Log(LogString, "INFO")
								ret = subprocess.call(["./mktcpip.exp",hmcip,system,viosname,viosname,seaip,viosnetmask,viosgateway,viosdns,viosdomain])
				elif child3.tag == "VIOSVSCSIVIRSLOT":
					viosvirvscsislot = child3.text
				elif child3.tag == "LPARNAME":
					lparname = child3.text
				elif child3.tag == "VIOSVSCSIREMOTEVSLOT":
					viosvscsiremotevslot = child3.text
					if viosvirvscsislot != "NA" and lparname != "NA" and viosvscsiremotevslot != "NA":
						string = viosvirvscsislot + '/' + "server" + '/' + '/' + lparname + '/' + viosvirvscsislot + '/' + '1'
						arg = str.format("chsyscfg -r prof -m {} -i name={},lpar_name={},virtual_scsi_adapters+={}",hmcip,system,viosname,viosname,string)
						#ret = subprocess.check_output(arg, shell=True)
				elif child3.tag == "VIOSVFCVIRSLOT":
					viosvirvfcslot = child3.text
				elif child3.tag == "LPARNAME":
					lparname = child3.text
				elif child3.tag == "VIOSFCSPHYSPORT":
					port = child3.text
				elif child3.tag == "VIOSVFCREMOTEVSLOT":
					viosvfcremotevslot = child3.text
					if viosvirvfcslot != "NA" and lparname != "NA" and viosvfcremotevslot != "NA":
						arg = str.format("ioscli lsmap -all -npiv | grep -w C{} | cut -f1 -d \" \"",viosvirvfcslot)
						rc,out,err = sshexec(viosip,arg,"padmin","padmin")
                               			if rc != 0:
                                        		LogString = str.format("ioscli lsmap failed with error {} {}", out,err)
                                        		Log(LogString, "ERROR")
                                        		exit(1)
						vfcadapter = out.rstrip()
						fcsadapter = get_adapter(viosip, port, type='fcs')
						
						LogString = str.format("Mapping fcs with vfc on  {}......", viosname)
                                		Log(LogString, "INFO")
                                        	arg = str.format("ioscli vfcmap -fcp {} -vadapter {}", fcsadapter, vfcadapter)
						print(arg)
						rc,out,err = sshexec(viosip,arg,"padmin","padmin")
                               			if rc != 0:
                                        		LogString = str.format("ioscli vfcmap failed with error {} {}", out,err)
                                        		Log(LogString, "ERROR")
                                        		exit(1)

				elif child3.tag == "LPARETHVIRSLOT":
					lparvirethslot = child3.text
				elif child3.tag == "LPARPVID":
					lparpvid = child3.text
				elif child3.tag == "LPARIEEE802":
					lparieee = child3.text
				elif child3.tag == "LPARADDVLANID":
					lparaddvlanid = child3.text
				elif child3.tag == "LPARVIRSWITCH":
					lparvirswitch = child3.text
				elif child3.tag == "LPARVSCSIVIRSLOT":
					lparvirvscsislot = child3.text
				elif child3.tag == "VIOSNAME":
					viosname = child3.text
				elif child3.tag == "LPARVSCSIREMOTEVSLOT":
					lparvscsiremotevslot = child3.text
					if lparvirvscsislot != "NA" and viosname != "NA" and lparvscsiremotevslot != "NA":
						string = lparvirvscsislot + '/' + "client" + '/' + '/' + viosname  + '/' + lparvscsiremotevslot + '/' + '1'
						arg = str.format("ssh -l hscroot {} chsyscfg -r prof -m {} -i name={},lpar_name={},virtual_scsi_adapters+={}",hmcip,system,lparname,lparname,string)
			#			ret = subprocess.check_output(arg, shell=True)

def sshexec(ip,cmd,usrname,passwd):
	 
	dssh = paramiko.SSHClient()
	dssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	paramiko.util.log_to_file('paramiko.log')
	try:
		dssh.connect(ip, username=usrname, password=passwd)
	except Exception as e:
		print "SSH failed with Error : %s" % (e)
		exit(1)
	stdin, stdout, stderr = dssh.exec_command(cmd, get_pty=True)
	out = stdout.read()
	err = stderr.read()
	if stdout.channel.recv_exit_status() != 0:
		LogString = str.format("Command Failed: {} {}", out,err)
                Log(LogString, "ERROR")
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
	if typeOfLog=="INFO":
        	logger.console(logString)
        	logger.info(logString)
    	elif typeOfLog=="DEBUG":
        	logger.console(logString)
        	logger.debug(logString)
    	elif typeOfLog=="WARN":
        	logger.console(logString)
        	logger.warn(logString)
    	elif typeOfLog=="ERROR":
        	logger.error(logString)
    	elif typeOfLog=="":
        	logger.console(logString)
        	logger.trace(logString)   




def LparStorageDeploy(xmlfile, username):
	tree = ET.parse(xmlfile)
	root = tree.getroot()
    	vios_values = list()
    	lpar_values = list()
    	WWPN_lists = list()

	# First Loop read <CONFIG> elements
	for child in root:
		if child.tag == "SYSTEM":
			system = str(child.text)
		elif child.tag == "FSPIP":
			fspip = str(child.text)
		elif child.tag == "HMCHOSTNAME":
			hmchostname = str(child.text)
		elif child.tag == "HMCIP":
			hmcip = str(child.text)
		elif child.tag == "NIMSERVER":
			nimserver = str(child.text)
		elif child.tag == "VIOSERVER":
			numvios+=1
		# Second Loop read <VIOS> and <LPAR> elements
		for child2 in child:
			if child2.tag == "VIOSNAME":
				viosname = str(child2.text) 
			elif child2.tag == "VIOSIP":
				viosip = str(child2.text)
			elif child2.tag == "VIOSFCSSLOTS":
				DRC_slot = []
				array = []
			elif child2.tag == "LPARNAME":
				lparname = child2.text
			elif child2.tag == "LPARIP":
				lparip = child2.text
			elif child2.tag == "LPARFCSSLOTS":
				DRC_slot = []
				array = []
                        	for slot in child2:
					if slot.text != "NA":
                                		if slot.tag == 'SLOT':
							arg = str.format("lshwres -r io -m {} --rsubtype slot -F phys_loc,description,lpar_id,drc_index,drc_name|grep -w {}",system,slot.text)
							rc,out,err = sshexec(hmcip,arg,"hscroot","abc123")
                                                	if rc != 0:
                                                		LogString = str.format("lshwres failed with to list the fiber chanel adapter {} {}", out,err)
                                                        	Log(LogString, "INFO")
                                                        	exit(1)
							array = out.split(",")
                                        		DRC_slot.append(array[3])
					WWPN_list=dynamic_WWPN.WWPN(hmcip, system, DRC_SLOT=DRC_slot)
			elif child2.tag == "LPARSTORAGE" and child.tag=='LPAR':
				for child3 in child2:
                                        storage_value=(child3.text).split(",")
					if storage_value[0] != "NA":
						# print(child3.tag, child3.text)
						L=7
						dict_STORAGE_DETAIL = dict()
						dict_STORAGE_DETAIL['name'] = lparname
						dict_STORAGE_DETAIL['quantity'] = storage_value[0]
						dict_STORAGE_DETAIL['size'] = storage_value[1]+'G'
						WWPN_list = dynamic_WWPN_lpar.WWPN_LPAR(hmcip, system, LPAR_NAME=lparname)
						if child3.tag == 'LPARROOTVG':
							dict_STORAGE_DETAIL['share'] = '0'
							dict_STORAGE_DETAIL['type'] = 'root'
						elif child3.tag == 'LPARDATAVG':
							dict_STORAGE_DETAIL['type'] = 'non-root'
						if storage_value[2] == 'shared':
							dict_STORAGE_DETAIL['share'] = '1'
						else:
							dict_STORAGE_DETAIL['share'] = '0'
						WWPN_dict = dict()
						count = 1
						for _i in range(3, len(storage_value) - 1):
						    WWPN_dict['wwpn%d' % (count)] = storage_value[_i]
						    count += 1
						for _i in range(0,len(WWPN_list)):
						    WWPN_dict['wwpn%d' % (count)] = WWPN_list[_i]
						    count +=1

						#print("WWPN_dict is %s" % WWPN_dict)
						"""
						WWPN_dict['wwpn1'] = storage_value[3]
						if len(storage_value)>= 5 and storage_value[4] != "":
						    WWPN_dict['wwpn2'] = storage_value[4]
						if len(storage_value) >= 6 and storage_value[5] != "":
						    WWPN_dict['wwpn3'] = storage_value[5]
						if len(storage_value) >= 7 and storage_value[6] != "":
						    WWPN_dict['wwpn4'] = storage_value[6]
						#dict_STORAGE_DETAIL['share'] = storage_value[-1]
						"""
						dict_STORAGE_DETAIL['wwpns'] = WWPN_dict
						dict_STORAGE_DETAIL['pool'] = storage_value[-1]
						lpar_values.append(dict_STORAGE_DETAIL)
						#print(lpar_values)	

				print(lpar_values)	
				if len(lpar_values)>0:
					print("Calling record storage")
					#create_storage_record(lpar_values, username)
					#lpar_values[:] = []


def WorkloadDeploy(xmlfile):
	tree = ET.parse(xmlfile)
        root = tree.getroot()
	
	for child in root:
		if child.tag == "LPARDOMAIN":
			lpardomain = child.text
		elif child.tag == "LPARDNS":
			lpardns = child.text
        	for child2 in child:
			if child2.tag == "LPARNAME":
				lparname = child2.text
			elif child2.tag == "LPARIP":
				lparip = child2.text
			elif child2.tag == "USER":
				userid = child2.text
			elif child2.tag == "LPPSOURCE":
				lppsource = child2.text
			elif child2.tag == "INSTALL":
				if str(child2.text) == 'N':
					break	
			elif child2.tag == "WORKLOAD":
				for child3 in child2:
					if child3.tag == "WORKLOADTYPE":
						workloadtype = child3.text
					elif child3.tag == "SIZE":
						size = child3.text
						#Run workload
						if workloadtype != "NA":
							if workloadtype == "ORACLEDB":
								if size == "S":
									dbsize = "50G"
								elif size == "M":
									dbsize = "100G"
								elif size == "L":
									dbsize = "150G"
								elif size == "XL":
									dbsize = "250G"
								
								ret = subprocess.call(["./ChangePasswd.exp",lparname])
                                                                LogString = str.format(" Installing ssh on LPAR {}......", lparname)
                                                                Log(LogString, "INFO")
                                                                ret = subprocess.call(["./InstallSSH.exp",lparname])
                                                                arg = "what /unix|grep build|awk -F' ' '{print $7}'"
                                                                rc,out,err = sshexec(lparip,arg,"root","abc123")
                                                                if rc != 0:
                                                                        LogString = str.format("Failed to find out the build level {} {}", out,err)
                                                                        Log(LogString, "ERROR")
                                                                        break

                                                                LogString = str.format(" Configuring DNS on LPAR {}......", lparname)
                                                                Log(LogString, "INFO")
                                                                arg = str.format("namerslv -a -i {} -D {}",lpardns,lpardomain)
                                                                rc,out,err = sshexec(lparip,arg,"root","abc123")
                                                                if rc != 0:
                                                                        LogString = str.format("namerslv failed with error {} {}", out,err)
                                                                        Log(LogString, "ERROR")
                                                                        exit(1)
	
								arg = str.format("mount 9.3.49.251:/0817_driver /driver")
								rc,out,err = sshexec(lparip,arg,"root","abc123")
								if rc != 0:
									LogString = str.format("mount failed with error {} {}", out,err)
									Log(LogString, "ERROR")
									exit(1)
								LogString = str.format(" Configuring Public Key Authentication {}......", lparname)
								Log(LogString, "INFO") 
								ret = subprocess.call(["./ConfSSH.exp",lparip])
								LogString = str.format("COnfiguring Oracle and OAST Workload on {}......", lparname)
								Log(LogString, "INFO") 
								arg = str.format("ssh {} -l root /driver/tools/APPS_TOOLS/oracle_automation_complete/oracle_db_install.ksh.18c {}",lparip, lparip)
								ret = subprocess.call(arg,shell=True)
								LogString = str.format("Starting OAST Workload on {}......", lparname)
								Log(LogString, "INFO") 
								arg = str.format("/driver/tools/APPS_TOOLS/oracle_automation_complete/startWorkload.ksh")
								rc,out,err = sshexec(lparip,arg,"root","abc123")
                                                                if rc != 0:
                                                                        LogString = str.format("Oracle/OAST execution failed with error {} {}", out,err)
                                                                        Log(LogString, "ERROR")
                                                                        exit(1)
							elif workloadtype == "ORACLERAC":
								if size == "S":
									dbsize = "50G"
								elif size == "M":
									dbsize = "100G"
								elif size == "L":
									dbsize = "150G"
								elif size == "XL":
									dbsize = "250G"
							elif "DB2" in workloadtype:
								ret = subprocess.call(["./ChangePasswd.exp",lparname])
                                                                LogString = str.format(" Installing ssh on LPAR {}......", lparname)
                                                                Log(LogString, "INFO")
                                                                ret = subprocess.call(["./InstallSSH.exp",lparname])
                                                                arg = "what /unix|grep build|awk -F' ' '{print $7}'"
                                                                rc,out,err = sshexec(lparip,arg,"root","abc123")
                                                                if rc != 0:
                                                                        LogString = str.format("Failed to find out the build level {} {}", out,err)
                                                                        Log(LogString, "ERROR")
                                                                        break

                                                                LogString = str.format(" Configuring DNS on LPAR {}......", lparname)
                                                                Log(LogString, "INFO")
                                                                arg = str.format("namerslv -a -i {} -D {}",lpardns,lpardomain)
                                                                rc,out,err = sshexec(lparip,arg,"root","abc123")
                                                                if rc != 0:
                                                                        LogString = str.format("namerslv failed with error {} {}", out,err)
                                                                        Log(LogString, "ERROR")
                                                                        exit(1)

                                                                if "10.5" in workloadtype:
                                                                        version = "10.5"
                                                                        fp = "FP10"  # modify this line if newer fix pack comes for 10.5
                                                                elif "11.1" in workloadtype:
                                                                        version = "11.1"
                                                                        fp = "FP4"  # modify this line if newer fix pack comes for 11.1
                                                                else:
                                                                        version = None
                                                                        fp = None
                                                                        print("newer version other than db2 10.5 & 11.1 came, please alter code")
                                                                        sys.exit(1)
                                                                ########### adding code to form the statement for execution ##################
                                                                # phase2 statement is for small size workload type execution
                                                                # phase3 statement is for medium size workload type execution
                                                                # phase 4 statement is for large size workload type execution
                                                                ##############################################################################
                                                                if "BLU" in workloadtype:
                                                                        db2_workload = "BLU"
                                                                        db2_dir = r"tools/APPS_TOOLS/BLU_Automation"
                                                                        db2_phase1_statement = r"/BLU_Automation/DB2INSTALL.ksh " + version + " " + fp \
                                                                                +       r" 1>/tmp/db2_phase1.log 2>/tmp/db2_phase1.log"
                                                                        db2_phase2_statement = r"echo '/BLU_Automation/blu_script  2>/tmp/db2_phase2.log 1>/tmp/db2_phase2.log' | at now"
                                                                        db2_phase3_statement = None
									db2_phase4_statement = None
                                                                elif "TPCE" in workloadtype:
                                                                        db2_workload = "TPCE"
                                                                        db2_dir = r"tools/APPS_TOOLS/DB2_TPCE_AUTOMATION"
                                                                        db2_phase1_statement = r"/DB2_TPCE_AUTOMATION/1.sh 1>/tmp/db2_phase1.log 2>/tmp/db2_phase1.log"
                                                                        db2_phase2_statement = r"echo '/DB2_TPCE_AUTOMATION/db2_tpce.ksh " + version + " " + fp \
                                                                                + r" 1>/tmp/db2_phase2.log 2>/tmp/db2_phase2.log ' | at now"
                                                                        db2_phase3_statement = None
                                                                        db2_phase4_statement = None
                                                                else:
                                                                        db2_workload = None
                                                                        print("Unknown or New db2 workload type mentioned exiting now")
                                                                        sys.exit(2)
                                                                ########### copying scripts from logger to test machine ####################
                                                                arg = r" echo 'mounting logger ... \c'; mount logger:/0817_driver /mnt "
                                                                rc,out,err = sshexec(lparip,arg,"root","abc123")
                                                                arg = r" echo 'copying scripts to test machine ... \c'; cp -r /mnt/" + db2_dir + r" /  "
                                                                rc,out,err = sshexec(lparip,arg,"root","abc123")
                                                                if rc != 0:
                                                                        print " \t\t    Failed to copy scripts "
                                                                        sys.exit(3)
                                                                else:
                                                                        print " \t\t    Successfully copied scripts  "
                                                                arg = r"echo 'DB2 phase1 execution started, please be patient & monitor the logs in " \
									+ r" test machine at /tmp/db2_phase1.log ...\c'"
                                                                rc,out,err = sshexec(lparip,arg,"root","abc123")
                                                                ################# db2 installation & execution phase1 code started ###############
                                                                rc,out,err = sshexec(lparip,db2_phase1_statement,"root","abc123")
                                                                if rc != 0:
                                                                        print " \t\t    Failure reported in phase 1, please check log file "
                                                                        sys.exit(4)
                                                                else:
                                                                        print " \t\t    Successfully completed phase 1, logs are available at /tmp/db2_phase1.log "
                                                                ################# db2 installation & execution phase2 code started ###############
                                                                arg = r"echo 'DB2 phase2 execution started, please be patient & monitor the logs in "  \
                                                                      + r" test machine at /tmp/db2_phase2.log ...\c'"
                                                                rc,out,err = sshexec(lparip,arg,"root","abc123")
                                                                ################# if db2 size is small ###########################################
                                                                if size == 'S':
                                                                        rc,out,err = sshexec(lparip,db2_phase2_statement,"root","abc123")
                                                                elif size == 'M':
                                                                        pass
                                                                elif size == 'L':
                                                                        pass
                                                                elif size == 'XL':
                                                                        pass
								if rc != 0:
                                                                        print " \t\t    Failure reported in phase 2, please check log file "
                                                                        sys.exit(5)
                                                                else:
                                                                        print " \t\t    Successfully triggered script for phase 2 execution, please monitor logs in test machine @ /tmp/db2_phase2.log "
							elif workloadtype == "DB2BLU":
								if size == "S":
									dbsize = "50G"
								elif size == "M":
									dbsize = "100G"
								elif size == "L":
									dbsize = "150G"
								elif size == "XL":
                                                                	dbsize = "250G"
							elif workloadtype == "AUTOREGRESSION":
								return_status = PollLPAR(lparname)
    								if return_status:
									LogString = str.format("LPAR {} is not up",lparname)
									Log(LogString, "ERROR")
        								print_and_send_email(userid,"LPAR is not up",lparname)
        								break
								else:
									ret = subprocess.call(["./ChangePasswd.exp",lparname])
									LogString = str.format(" Installing ssh on LPAR {}......", lparname)
                                                                	Log(LogString, "INFO")
                                                                	ret = subprocess.call(["./InstallSSH.exp",lparname])
                                                                	arg = "what /unix|grep build|awk -F' ' '{print $7}'"
                                                                	rc,out,err = sshexec(lparip,arg,"root","abc123")
                                                                	if rc != 0:
                                                                        	LogString = str.format("Failed to find out the build level {} {}", out,err)
                                                                        	Log(LogString, "ERROR")
                                                                        	break

                                                                	LogString = str.format(" Configuring DNS on LPAR {}......", lparname)
                                                                	Log(LogString, "INFO")
                                                                	arg = str.format("namerslv -a -i {} -D {}",lpardns,lpardomain)
                                                                	rc,out,err = sshexec(lparip,arg,"root","abc123")
                                                                	if rc != 0:
                                                                        	LogString = str.format("namerslv failed with error {} {}", out,err)
                                                                        	Log(LogString, "ERROR")




def AutoregExec(xmlfile):
	tree = ET.parse(xmlfile)
	root = tree.getroot()
	for child in root:
        	for child2 in child:
			if child2.tag == "LPARNAME":
				lparname = child2.text
			elif child2.tag == "USER":
				userid = child2.text
			elif child2.tag == "INSTALL":
				if str(child2.text) == 'N':
					break
				LogString = str.format("About to execute Autoregression on  {}......", lparname)
				Log(LogString, "INFO") 
				arg = str.format("./Init.py {} {} {}", lparname, userid, "&")
				ret = subprocess.call(arg,shell=True)
				if ret != 0:
					LogString = str.format("Autoreg failed with error {} {}", out,err)
					Log(LogString, "ERROR")


def FirmwareUpdate(xmlfile):
	tree = ET.parse(xmlfile)
	root = tree.getroot()

	# First Loop read <CONFIG> elements
	for child in root:
		if child.tag == "SYSTEM":
			system = str(child.text)
		elif child.tag == "FSPIP":
			fspip = str(child.text)
		elif child.tag == "HMCIP":
			hmcip = str(child.text)
		elif child.tag == "FIRMWARE":
			firmware_level = str(child.text)
		elif child.tag == "UPGRADE":
			if str(child.text) == 'N':
				break
		elif child.tag == "USER":
			userid = str(child.text)
			arg = str.format("./UpdateGFW.py {} {} {} {} {} {} &", "lcb201", fspip, firmware_level, hmcip, "hscroot/abc123",userid)
			LogString = str.format("About to update firmware {}......", arg)
			Log(LogString, "INFO") 
                        ret,out,err = subprocess.call(arg,shell=True)
			if ret != 0:
				LogString = str.format("Firmware update failed with error {} {}", out,err)
				Log(LogString, "ERROR")


def Loop_PollLPAR(host):
    exit_status = 1
    polling = 60
    while polling:
        time.sleep(60)
        exit_status = os.system("ping -c 1 " + host)
        if exit_status == 0:
            time.sleep(300)
            return 0
        polling = polling - 1
    return 1

def PollLPAR(host):
    exit_status = 1
    polling = 1
    while polling:
        exit_status = os.system("ping -c 1 " + host)
        if exit_status == 0:
            return 0
        polling = polling - 1
    return 1

def print_and_send_email(email_address, message, lpar_name):
    print(message)
    hostname="9.3.121.20"
    full_mgs= lpar_name+": "+message
    email_address1="sniranjan@in.ibm.com"
    client = paramiko.client.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    command="echo \"Subject : \""+full_mgs+ "\"<eom> \" | sendmail "+email_address
    command1="echo \"Subject : \""+full_mgs+ "\"<eom> \" | sendmail "+email_address1
    client.connect(hostname, username="ctalert", password="ctalert")
    stdin, stdout, stderr = client.exec_command(command)
    stdin, stdout, stderr = client.exec_command(command1)
    exit_status = stdout.channel.recv_exit_status()
    client.close()
    return exit_status

def get_ssh_client(host='', username='', password=''):
    """
    Method to get a SSH Client Object
    :param host: IP Address/ hostname
    :param username: Login username
    :param password: Login password
    :return: SSH Client Object
    """
    try:
        client = SSH.SSHClient()
        client.set_missing_host_key_policy(SSH.AutoAddPolicy())
        client.connect(hostname=host, username=username,password=password)
        return client
    except Exception as e:
        print(str(e))
        return None

def get_adapter_for_slot(ssh_obj, slot, type='ent'):
    """
    Get adapter name from Slot name.
    :param ssh_obj: SSH Client Object
    :param slot: Slot number
    :param type: Type of adapter. ent or fcs or vscsi
    :return: Adapter name
    """
    try:
        command = 'echo "lscfg | grep %s | grep %s"| ioscli oem_setup_env'%(type, slot)
        stdin, stdout, stderr = ssh_obj.exec_command(command)
        adapter = stdout.readlines()
        adapter = [item.split('\n')[0].split('+ ')[-1] for item in adapter[0].split(' '*6) if len(item)>0 ]
        print(adapter[0])
        return adapter[0]
    except Exception as e:
        print(str(e))
        print('Error occured')
        return None

def get_adapter(hostname='', slot_name='', type='ent'):
    ssh_clt = get_ssh_client(host=hostname, username='padmin', password='padmin')
    slot = get_adapter_for_slot(ssh_clt, slot_name, type=type)
    return slot	

#CreateLpar("/home/niranj/CT/alto.xml")
#CreateVirtualAdapter("/home/niranj/CT/alto.xml")
ViosStorageAlloc("/home/niranj/CT/storage40G.xml",'dhanu')
#InstallVIOS("/home/niranj/CT/pinch.xml")
#time.sleep(1800)
#ViosSetPassword("/home/niranj/CT/config.xml")
#CreateMap("/home/niranj/CT/config.xml")
#LparStorageAlloc("/home/guest/CT/fightnpiv.xml",'niranj')
#time.sleep(300)
#InstallLPAR("/home/niranj/CT/yeti.xml")
#time.sleep(1200)
#WorkloadDeploy("/home/niranj/CT/config.xml")
#FirmwareUpdate("/home/niranj/CT/firmware_update.xml")
