#!/usr/bin/env bash

export N_WALLETS=$NODES
SKALE_AMOUNT=200 ETH_AMOUNT=20 python prepare_wallets.py

case $PROVIDER in
    do)
          TF_VAR_COUNT=$NODES
          terraform apply
          terraform output -json instance_ips > result.json
          ;;
     aws)
          cd aws_tf
          TF_VAR_COUNT=$NODES bash run.sh
          ;;
     *)
          echo 'Provide valid PROVIDER option: do/aws'
          ;;
esac