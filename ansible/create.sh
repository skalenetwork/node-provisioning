export ANSIBLE_HOST_KEY_CHECKING=False
echo "[nodes]" > inventory/hosts
cd terraform
TF_VAR_NUMBER=$NODES_NUMBER terraform apply
echo 'Nodes machines created'
sort hosts >> ../inventory/hosts
rm hosts
cd ../
cat inventory/hosts
echo 'Sleep 10 seconds'
sleep 20
# ansible-playbook -i inventory main2.yaml
