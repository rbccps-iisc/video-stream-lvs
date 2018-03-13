#!/bin/sh
wget -qO- https://deb.nodesource.com/setup_8.x | sudo bash -
sudo apt-get install -y nodejs
sudo apt-get install npm
sudo npm install 
sudo npm install csv-parse
sudo npm install request
sudo apt-get install tmux
sudo cp rc.local /etc/rc.local
sudo sed -i -e "s|home_path|$HOME|" /etc/rc.local 
sudo chmod +x /etc/rc.local
