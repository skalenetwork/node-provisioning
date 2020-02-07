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

printenv > /root/init-env
sudo -E bash -c "curl -L https://skale-cli.sfo2.cdn.digitaloceanspaces.com/$CLI_SPACE/skale-$VERSION_NUM-`uname -s`-`uname -m` >  /usr/local/bin/skale"
sudo chmod +x /usr/local/bin/skale

skale node init --install-deps --env-file /root/init-env

echo "Waiting for sgx certificates handshake"
sleep 60
