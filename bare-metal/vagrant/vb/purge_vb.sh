# Purge Virtualbox
sudo vboxmanage list runningvms | sed -r 's/.*\{(.*)\}/\1/' | sudo xargs -L1 -I {} VBoxManage controlvm {} savestate
sudo VBoxManage extpack uninstall "Oracle VM VirtualBox Extension Pack"
sudo systemctl stop vboxweb-service.service
# using wildcard may not work on some linux systems, and you have to specify the version to remove:
sudo apt-get -y autoremove --purge virtualbox*
sudo rm -rf /etc/vbox /usr/lib/virtualbox /opt/VirtualBox /etc/apt/sources.list.d/virtualbox.list
# optional:
# sudo rm -rf ~/.config/VirtualBox