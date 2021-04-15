#!/bin/bash

curl -sL https://raw.githubusercontent.com/ogaltsov/ansible-encrypt-vault/master/ansible-encrypt-vault.py | bash
chmod +x ansible-encrypt-vault.py
mv ansible-encrypt-vault.py /usr/local/bin/ansible-encrypt-vault

apt update
apt-get install python3-pip
python3 -m pip --version

pip3 install ansible-vault
pip3 install termcolor
