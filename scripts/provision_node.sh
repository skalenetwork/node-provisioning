#!/usr/bin/env bash

NODE_DATA_DIR="/skale_node_data"
TOKEN_FILE=$NODE_DATA_DIR/tokens.json

sudo -E bash -c "curl -L https://skale-cli.sfo2.cdn.digitaloceanspaces.com/$CLI_SPACE/skale-$VERSION_NUM-`uname -s`-`uname -m` >  /usr/local/bin/skale"
sudo chmod +x /usr/local/bin/skale

skale node init --github-token $TOKEN --docker-username $DOCKER_USERNAME --docker-password $DOCKER_PASSWORD --db-password $DB_PASSWORD --disk-mountpoint $DISK_MOUNTPOINT --stream $STREAM --install-deps


while ! [ -f $TOKEN_FILE ];
do
  echo "Waiting for tokens.json file..."
  sleep 2
done

USER_REGISTRATION_TOKEN=$(skale user token --short)
skale user register -u $USERNAME -p $PASSWORD -t $USER_REGISTRATION_TOKEN

skale wallet set --private-key $ETH_PRIVATE_KEY
skale node register --name $NODE_NAME --ip $NODE_IP --port $NODE_PORT
