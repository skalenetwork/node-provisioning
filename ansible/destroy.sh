set -e
: "${NODES_NUMBER?Need to set NODES_NUMBER}"
cd terraform/aws
TF_VAR_NUMBER=$NODES_NUMBER terraform destroy
cd ..

