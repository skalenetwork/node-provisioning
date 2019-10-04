#!/usr/bin/env bash

# core dump logs
mkdir -p /skale_node_data/dump
echo '/skale_node_data/dump/core.%t.%e.%p' | sudo tee /proc/sys/kernel/core_pattern
ulimit -Sc unlimited

printf "root hard core unlimited\nroot soft core unlimited\n"  >> /etc/security/limits.conf

NODE_DATA_DIR="/skale_node_data"
TOKEN_FILE=$NODE_DATA_DIR/tokens.json

sudo -E bash -c "curl -L https://skale-cli.sfo2.cdn.digitaloceanspaces.com/$CLI_SPACE/skale-$VERSION_NUM-`uname -s`-`uname -m` >  /usr/local/bin/skale"
sudo chmod +x /usr/local/bin/skale

skale node init --github-token $TOKEN --docker-username $DOCKER_USERNAME \
    --docker-password $DOCKER_PASSWORD --db-password $DB_PASSWORD --disk-mountpoint $DISK_MOUNTPOINT \
    --stream $STREAM --endpoint $ENDPOINT --ima-endpoint $IMA_ENDPOINT --manager-url $MANAGER_URL \
     --ima-url $IMA_URL --dkg-url $DKG_URL --filebeat-url $FILEBEAT_URL --install-deps

while ! [ -f $TOKEN_FILE ];
do
  echo "Waiting for tokens.json file..."
  sleep 2
done

USER_REGISTRATION_TOKEN=$(skale user token --short)
skale user register -u $SKALE_USERNAME -p $PASSWORD -t $USER_REGISTRATION_TOKEN

skale wallet set --private-key $ETH_PRIVATE_KEY
skale node register --name $NODE_NAME --ip $NODE_IP --port $NODE_PORT
