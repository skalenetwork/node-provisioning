set -e
: "${NODES_NUMBER?Need to set NODES_NUMBER}"

echo "[nodes]" > inventory/hosts
cd terraform/aws
rm -f hosts
rm -f terraform.tfstate.backup
mkdir tfstate_backup
mv terraform.tfstate tfstate_backup/terraform.tfstate-$(date +"%F-%T")
TF_VAR_NUMBER=$NODES_NUMBER terraform apply -auto-approve
echo 'Nodes machines created'
sort hosts >> ../../inventory/hosts
cd ../../
cat inventory/hosts
echo 'Sleep 20 seconds'
sleep 20
ANSIBLE_HOST_KEY_CHECKING=False ansible-playbook -v main.yaml
