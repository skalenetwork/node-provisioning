set -e
: "${NODES_NUMBER?Need to set NODES_NUMBER}"
: "${PROVIDER?Need to set PROVIDER: aws, do, vultr}"
if [ $PROVIDER = "vultr" ]; then
  : "${VULTR_API_KEY?Need to set VULTR_API_KEY}"
fi

echo "[nodes]" > inventory/hosts
cd terraform/$PROVIDER
rm -f hosts
if [ $PROVIDER = "vultr" ]; then
  TF_VAR_NUMBER=$NODES_NUMBER TF_VAR_api_key=$VULTR_API_KEY terraform apply
  terraform output -json > post_install/hosts_info.json
  python post_install/check_instances.py
  sort hosts >> ../../inventory/hosts
  ANSIBLE_HOST_KEY_CHECKING=False ansible-playbook -v -i ../../inventory post_install/set_ssh.yaml
else
  TF_VAR_NUMBER=$NODES_NUMBER terraform apply
fi
echo 'Nodes machines created'
sort hosts >> ../../inventory/hosts
cd ../../
cat inventory/hosts
echo 'Sleep 10 seconds'
sleep 20
ANSIBLE_HOST_KEY_CHECKING=False ansible-playbook -v main.yaml
