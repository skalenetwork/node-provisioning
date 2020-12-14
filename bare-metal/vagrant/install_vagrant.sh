#!/bin/bash

wget https://releases.hashicorp.com/vagrant/2.2.14/vagrant_2.2.14_linux_amd64.zip
unzip vagrant_2.2.14_linux_amd64.zip
mv vagrant_2.2.14_linux_amd64 /usr/local/bin/vagrant
chmod +x /usr/local/bin/vagrant
