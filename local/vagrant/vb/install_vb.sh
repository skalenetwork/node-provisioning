#!/bin/bash
# Install Virtualbox from Oracle Repository
echo "deb [arch=amd64] http://download.virtualbox.org/virtualbox/debian $(lsb_release -sc) contrib" | sudo tee /etc/apt/sources.list.d/virtualbox.list
sudo su -c 'wget -q -O- https://www.virtualbox.org/download/oracle_vbox.asc | apt-key add -'
sudo su -c 'wget -q -O- http://download.virtualbox.org/virtualbox/debian/oracle_vbox_2016.asc | apt-key add -'
sudo apt-get update
sudo apt-get -y install linux-headers-$(uname -r) build-essential gcc make perl dkms bridge-utils
sudo apt-get -y install virtualbox-6.1
sudo dpkg --configure -a && sudo apt-get -f -y install
export VBOX_VER=`VBoxManage --version | awk -Fr '{print $1}'`
wget -c http://download.virtualbox.org/virtualbox/$VBOX_VER/Oracle_VM_VirtualBox_Extension_Pack-$VBOX_VER.vbox-extpack
sudo VBoxManage extpack install Oracle_VM_VirtualBox_Extension_Pack-$VBOX_VER.vbox-extpack
sudo usermod -a -G vboxusers $USER
sudo update-grub
sudo /sbin/vboxconfig