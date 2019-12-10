#!/usr/bin/env bash
set -a
set -o allexport

export $(printenv | xargs)

# core dump logs
mkdir -p /skale_node_data/dump
echo '/skale_node_data/dump/core.%t.%e.%p' | sudo tee /proc/sys/kernel/core_pattern
ulimit -Sc unlimited

printf "root hard core unlimited\nroot soft core unlimited\n"  >> /etc/security/limits.conf

SKALE_DIR="$HOME"/.skale
NODE_DATA_DIR=$SKALE_DIR/node_data
TOKEN_FILE=$NODE_DATA_DIR/tokens.json

sudo -E bash -c "curl -L https://skale-cli.sfo2.cdn.digitaloceanspaces.com/$CLI_SPACE/skale-$VERSION_NUM-`uname -s`-`uname -m` >  /usr/local/bin/skale"
sudo chmod +x /usr/local/bin/skale

skale node init --sgx-url $SGX_URL --disk-mountpoint $DISK_MOUNTPOINT --install-deps

while ! [ -f $TOKEN_FILE ];
do
  echo "Waiting for tokens.json file..."
  sleep 2
done

USER_REGISTRATION_TOKEN=$(skale user token --short)
skale user register -u $SKALE_USERNAME -p $PASSWORD -t $USER_REGISTRATION_TOKEN

