#!/bin/bash
sudo ipvsadm -C
sudo bash -c "cat /dev/null > /etc/ipvsadm.rules"
sudo iptables -t mangle -F
sudo bash -c "cat /dev/null > /etc/iptables/rule.v4"
sudo sed -i '/hostgroup/,$d' /etc/mon/mon.cf

