export ANSIBLE_HOST_KEY_CHECKING=False
echo "[nodes]" > inventory/hosts
cd terraform
TF_VAR_NUMBER=$NODES_NUMBER terraform apply
cat hosts >> ../inventory/hosts
rm hosts
cd ../
echo 'Yeah boy'
cat inventory/hosts
echo 'Sleep 10 seconds'
sleep 20
ansible-playbook -i inventory main.yaml
