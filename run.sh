#!/usr/bin/env bash

export $(cat .env | xargs)
python prepare_wallets.py

case $PROVIDER in
    do)
          export TF_VAR_COUNT=$NODES
          terraform apply 2>&1 | tee terraform.log
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
