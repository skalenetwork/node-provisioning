set -e
: "${NODES_NUMBER?Need to set NODES_NUMBER}"
ansible-playbook -v cleanup.yaml
cd terraform/aws
TF_VAR_NUMBER=$NODES_NUMBER terraform destroy -auto-approve
cd ..

