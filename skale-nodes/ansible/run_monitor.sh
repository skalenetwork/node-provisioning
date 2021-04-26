cd ../..
source venv/bin/activate
export BASE_DIR=skale-nodes/ansible/files
export INVENTORY_DIR=skale-nodes/ansible/inventory
echo 'Generating hosts'
python skale-nodes/ansible/utils/generate_hosts.py

cd skale-nodes/ansible
echo 'Run monitor script'
ansible-playbook -i inventory run_monitor.yaml