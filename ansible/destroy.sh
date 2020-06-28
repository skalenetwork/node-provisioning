set -e
: "${NODES_NUMBER?Need to set NODES_NUMBER}"
: "${PROVIDER?Need to set PROVIDER: aws, do, vultr}"
if [ $PROVIDER = "vultr" ]; then
  : "${VULTR_API_KEY?Need to set VULTR_API_KEY}"
fi

ansible-playbook -v cleanup.yaml
cd terraform/$PROVIDER
if [ $PROVIDER = "vultr" ]; then
  TF_VAR_NUMBER=$NODES_NUMBER TF_VAR_api_key=$VULTR_API_KEY terraform destroy
else
  TF_VAR_NUMBER=$NODES_NUMBER terraform destroy
fi
cd ..

