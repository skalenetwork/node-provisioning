#!/usr/bin/env bash

CURRENT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

sudo apt install -y python3-pip

pip3 install -r $CURRENT_DIR/requirements.txt
python3 $CURRENT_DIR/transfer_funds.py

skale node register --name $NODE_NAME --ip $NODE_IP --port $NODE_PORT
