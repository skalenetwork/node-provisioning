#!/usr/bin/env bash

export $(cat .env | xargs)
python prepare_wallets.py

case $PROVIDER in
    do)
          export TF_VAR_COUNT=$N_WALLETS
          terraform apply
          terraform output -json instance_ips > result.json
          ;;
     aws)
          cd aws_tf
          TF_VAR_COUNT=$N_WALLETS bash run.sh
          ;;
     *)
          echo 'Provide valid PROVIDER option: do/aws'
          ;;
esac