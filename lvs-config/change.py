#!/usr/bin/python

import getopt
import csv
import os
import sys

def main(argv):
   try:
      opts, args = getopt.getopt(argv,"ho:c:m:",["option","clientIP=","mark="])
   except getopt.GetoptError:
      print 'change.py -o <change-client> -c <clientIP> -m <fwmark>'
      sys.exit(2)

   for opt, arg in opts:
      if opt == '-h':
         print 'change.py -o <change-client> -c <clientIP> -m <fwmark>'
         sys.exit()
      elif opt in ("-o", "--option"):
         option = arg
      elif opt in ("-c", "--clientIP"):
         clientIP = arg
      elif opt in ("-m", "--mark"):
         fwmark = arg

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
		elif row['field']=="schedule":schedule=row['value'].strip("\n")
   if (option == 'change-client'):
	r = csv.reader(open('client-list.csv'))
	lines = [l for l in r]
	existing_Cfwmark_list=[]
	existing_Cip_list=[]
	for i in range(1,len(lines)):
		existing_Cip_list.append(lines[i][0])
	with open('fwmark-routing-list.csv') as myFile2:  
    		reader = csv.DictReader(myFile2)
    		for row in reader:
    			if row['fwmark'] in existing_Cfwmark_list: continue
    			else: existing_Cfwmark_list.append(row['fwmark'])	
	myFile2.close()
	if clientIP not in existing_Cip_list:
		if fwmark not in existing_Cfwmark_list: 
				print 'error! incorrect fwmark chosen for client. No real server associated with '+fwmark+'. Choose fwmark from '+str(existing_Cfwmark_list)
				sys.exit() 
		else:
			lines.append([clientIP,fwmark])
			os.system('sudo iptables -t mangle -A PREROUTING -d '+lvsIP+' -s '+clientIP+' -p tcp --dport 1935 -j MARK --set-mark '+fwmark)
			os.system('sudo iptables -t mangle -A PREROUTING -d '+lvsIP+' -s '+clientIP+' -p tcp --dport 8080 -j MARK --set-mark '+fwmark)	
	else:
		for i in range(1,len(lines)):
	           if (clientIP == lines[i][0]):
			if fwmark not in existing_Cfwmark_list: 
				print 'error! incorrect fwmark chosen for client. No real server associated with '+fwmark+'. Choose fwmark from '+str(existing_Cfwmark_list)
				sys.exit()
			else: 
				os.system('sudo iptables -t mangle -D PREROUTING -d '+lvsIP+' -s '+lines[i][0]+' -p tcp --dport 1935 -j MARK --set-mark '+lines[i][1])
				os.system('sudo iptables -t mangle -D PREROUTING -d '+lvsIP+' -s '+lines[i][0]+' -p tcp --dport 8080 -j MARK --set-mark '+lines[i][1])				
				lines[i][1]=fwmark
				os.system('sudo iptables -t mangle -A PREROUTING -d '+lvsIP+' -s '+lines[i][0]+' -p tcp --dport 1935 -j MARK --set-mark '+lines[i][1])
				os.system('sudo iptables -t mangle -A PREROUTING -d '+lvsIP+' -s '+lines[i][0]+' -p tcp --dport 8080 -j MARK --set-mark '+lines[i][1])
        writer = csv.writer(open('client-list.csv', 'w'))
	writer.writerows(lines)
	os.system("sudo bash -c \"iptables-save > /etc/iptables/rules.v4\"")
	
		
   else:
	print 'invalid option'
	sys.exit()
   

if __name__ == "__main__":
   main(sys.argv[1:])
