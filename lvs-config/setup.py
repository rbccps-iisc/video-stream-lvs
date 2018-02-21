import csv
import os
import sys
from subprocess import call
raw_input("Welcome to load balancer setup, Press enter to continue")
#read parameters
text="param.csv"
f=open(text,'r')
with f:
	reader = csv.DictReader(f)
	for row in reader:
		if row['field']=="ip_domain":ip_domain=row['value'].strip("\n")
		elif row['field']=="mailid":mail_id=row['value'].strip("\n")
		elif row['field']=="lvsIP":lvsIP=row['value'].strip("\n")
		elif row['field']=="persistence_time":persistence_time=row['value'].strip("\n")
        	elif row['field']=="fwdefault":fwdefault=row['value'].strip("\n")
ip_domain=ip_domain.rsplit('.',1)

#Copy original for back-referencing
os.system('sudo cp client-list.csv client-list-org.csv')
with open('client-list.csv') as myFile1: 
		reader = csv.DictReader(myFile1)
		existing_ip_list=[]
		for row in reader:
			existing_ip_list.append(row['IP']) 
myFile1.close()
myFile = open('client-list.csv', 'a') 
with myFile:  
    		myFields = ['IP', 'fwmark']
    		writer = csv.DictWriter(myFile, fieldnames=myFields)    
		for i in range (1,255):
			IP=str(ip_domain[0])+"."+str(i)
			if IP in existing_ip_list:continue
			else:writer.writerow({'IP' : IP, 'fwmark': fwdefault})

myFile.close()
#Set IPTABLES for fwmarking tcp packets from a given IP
#FW marks are user provided or marked as 'fwdefault'
#Usually the applications on the same physical server should be given same FWmark so as to
# to be routed to the video server on the same physical server (if present)
#--dport 1935 for rtmp and --dport 8080 for HLS
with open('client-list.csv') as myFile2:  
    reader = csv.DictReader(myFile2)
    ls=[]
    for row in reader:
        os.system('sudo iptables -t mangle -A PREROUTING -d '+lvsIP+' -s '+row['IP']+' -p tcp --dport 1935 -j MARK --set-mark '+row['fwmark'])
	os.system('sudo iptables -t mangle -A PREROUTING -d '+lvsIP+' -s '+row['IP']+' -p tcp --dport 8080 -j MARK --set-mark '+row['fwmark'])
myFile2.close()
os.system("sudo bash -c \"iptables-save > /etc/iptables/rules.v4\"")
os.system("echo \"iptable rules saved\"")

with open('fwmark-routing-list.csv') as myFile2:  
    reader = csv.DictReader(myFile2)
    #Set IPVSADM rules
    # -g for Direct Server Return
    # -p persistence time (required for HLS connections, else the same stream request can get load balanced )

    for row in reader:
	   if not row['schedule']:
	   	os.system("sudo ipvsadm -A -p %s -f %s" %(persistence_time,row['fwmark']))
	   else:
		os.system("sudo ipvsadm -A -p %s -f %s -s %s" %(persistence_time,row['fwmark'],row['schedule']))
	   for l in row['server'].split(","):
        	os.system("sudo ipvsadm -a -f %s -r %s -g" %(row['fwmark'],l))
myFile1.close()
#save IPVS table to auto load the rules on system boot
os.system("sudo bash -c \"ipvsadm -S > /etc/ipvsadm.rules\"")
os.system("echo \"IPVS rules saved\"")
#Mon configuration
os.system("sudo cp lvs.alert /usr/lib/mon/alert.d/lvs.alert")
os.system("sudo chmod +x /usr/lib/mon/alert.d/lvs.alert")
#os.system("sudo /etc/init.d/mon stop")
os.system("echo \"changing mon configuration\"")
#Edit mon configuration to monitor each video server
#Set monitor interval and the service to monitor (For eg. monitor tcp service on port 1935)
#Set mailid to send alert messages when the video server goes down or when it comes back up.
with open('realserver-backup-list.csv') as myFile1:  
    reader = csv.DictReader(myFile1)
    i=1
    for row in reader:
        os.system("sudo sed -i -e \"\$ a hostgroup www"+str(i)+" "+row['RIP']+"\" /etc/mon/mon.cf")
	os.system("sudo sed -i -e \"\$ a \n\" /etc/mon/mon.cf")
	os.system("sudo sed -i -e \"\$ a watch www"+str(i)+"\" /etc/mon/mon.cf")
	os.system("sudo sed -i -e \"\$ a \\\tservice tcp\" /etc/mon/mon.cf")
	os.system("sudo sed -i -e \"\$ a \\\t\\\tinterval 10s\" /etc/mon/mon.cf")
	os.system("sudo sed -i -e \"\$ a \\\t\\\tmonitor tcp.monitor -p 1935\" /etc/mon/mon.cf")
	os.system("sudo sed -i -e \"\$ a \\\t\\\tperiod\" /etc/mon/mon.cf")
	os.system("sudo sed -i -e \"\$ a \\\t\\\t\\\talert mail.alert "+mail_id+"\" /etc/mon/mon.cf")
	os.system("sudo sed -i -e \"\$ a \\\t\\\t\\\tupalert mail.alert "+mail_id+"\" /etc/mon/mon.cf")
	rip=row['RIP']
	backup=row['backup']
	with open('fwmark-routing-list.csv') as myFile2:  
    	  reader = csv.DictReader(myFile2)
    	  for row in reader:
	      for l in row['server'].split(","):
	        if l==rip:
		  #if a single Video server is associated with a firewall mark
		  if not row['schedule']:
			#On Video server going down, Instruct lvs.alert to replace routing rule for the server with backup in the IPVS table
			os.system("sudo sed -i -e \"\$ a \\\t\\\t\\\talert lvs.alert -P tcp -R "+rip+" -F dr -B "+backup+" -M "+row['fwmark']+"\" /etc/mon/mon.cf")
			#On Video server coming back up, Instruct lvs.alert to replace routing rule for the backup with server in the IPVS table
        		os.system("sudo sed -i -e \"$ a \\\t\\\t\\\tupalert lvs.alert -P tcp -R "+rip+" -F dr -B "+backup+" -M "+row['fwmark']+"\" /etc/mon/mon.cf")
		 #if multiple Video servers are associated with a firewall mark
		  elif row['schedule']:
			#On Video server going down, Instruct lvs.alert to remove routing rule for the server from IPVS table
			os.system("sudo sed -i -e \"\$ a \\\t\\\t\\\talert lvs.alert -P tcp -R "+rip+" -F dr -M "+row['fwmark']+" -X\" /etc/mon/mon.cf")
			#On Video server coming back up, Instruct lvs.alert to add routing rule for the server to IPVS table
        		os.system("sudo sed -i -e \"$ a \\\t\\\t\\\tupalert lvs.alert -P tcp -R "+rip+" -F dr -M "+row['fwmark']+" -X\" /etc/mon/mon.cf")
	os.system("sudo sed -i -e \"\$ a \n\" /etc/mon/mon.cf")
	i=i+1
myFile1.close()
#os.system("echo \"starting mon service\"")
#os.system("sudo /etc/init.d/mon start")
#os.system("sudo mon -d")
