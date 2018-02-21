# Load Balancer for Video Server Cluster
Layer-4 load balancing is used to distribute RTMP based service requests to the video servers at the transport layer. IPVS (IP Virtual Server) implements this transport-layer load balancing inside the Linux kernel. IPVS extends the TCP/IP stack of the Linux kernel to support three IP load balancing techniques: LVS/NAT, LVS/TUN and LVS/DR.

After evaluating the specifics of our tasks we chose to employ the LVS/DR load balancing, which provides Direct Server Return (DSR). In DSR mode, the load balancer re-routes to the backend video server without changing anything in it but the destination MAC address. The backend video servers process the requests and answer directly to the clients without passing through the load balancer. One of the key benefits of using this is that network bandwidth of the load balancer is no longer a bottleneck.


## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. This project is tested on Ubuntu 16.04 machines.

### Prerequisites

Run the following command to install ipvsadm, mon and iptables-persistent

```
./prerequisite.sh
```
→  Installs ipvsadm, mon, iptables-persistent and mailutils packages

→  Runs ipvsadm on upstart and as a master daemon

### Setup
Before running the setup, create the following CSV files

* client-list.csv - Add client IPs that will access the video servers and specify corresponding Firewall mark to direct them to a particular Video Server
* fwmark-routing-list.csv - Specify video server IP(s) to route the incoming packets based on the firewall marking. If there are multiple video server IPs for a particular fwmark, specify a scheduling policy (rr, wrr, dh, sh, sed, nq, lc, wlc, lblc, lblcr) 
* realserver-backup-list.csv - Specify a backup server IP for each Video server to replace it during system downtime.. 
* param.csv - add values to following fields:
1. IP address of lvs machine
2. Network IP of the clients.
3. Mail id to send alert messages to
4. Persistence time for client connections
5. Default firewall mark to be used if no fw mark is specified against a client

Run the following

```
sudo python setup.py
```
→  Reads the client IP list and the corresponding fwmark.

→  Sets default fwmark to all the IPs in the domain of client Network IP that don’t have a fw mark assigned to them by the user.

→  Accordingly, the client IPs are marked with fwmark in the iptable rules for destination port 8080(HLS) and 1935(rtmp).

→  Saves the iptable rules to /etc/iptables/rules.v4 to automatically load the rules on system reboot.

→  Reads fwmark-routing-list.csv and sets IPVS rules using ipvsadm

→  Saves IPVS rules to /etc/ipvsadm.rules to automatically load the rules on system reboot.

→  Copies lvs.alert script to /usr/lib/mon/alert.d/ and sets permissions. 

→  lvs.alert script is configured to make changes to IPVS rules when instructed by mon.

→  Edit mon configuration to monitor each video server

→  Set monitor interval and the service to monitor (For eg. monitor tcp service on port 1935)

→  Set mail id to send alert messages when the video server goes down or when it comes back up.

→  Restart mon service

### Other scripts (post-startup)
#### Change Client IP list

After the initial setup of load balancing rules, inorder to dynamically add, remove or edit client list, run the following

```
sudo python change.py -o change-client -c <clientIP> -m <fwmark>
```
→  Make sure to enter a fwmark that is associated with any one of the real servers

#### Clear tables

To clear Iptable rules, IPVS table and mon configuration

```
./cleanup.sh
```
→  clears ipvsadm rules

→  clears iptables firewall mark routing rules

→  clears mon configuration

