#!/bin/bash

#install LVS
sudo apt-get install ipvsadm
sudo apt-get install iptables-persistent
sudo apt-get install mailutils
sudo sed -i -e 's/AUTO="false"/AUTO="true"/' /etc/default/ipvsadm
sudo sed -i -e 's/DAEMON="none"/DAEMON="master"/' /etc/default/ipvsadm

#run at upstart
/etc/init.d/ipvsadm start 

#install mon
sudo apt-get install mon

