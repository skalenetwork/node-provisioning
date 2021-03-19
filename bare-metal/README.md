# Bare metal provisioning

## Vagrant provision

Run this playbook to spin up Vagrant VMs, provision them and generate hosts file for node-provisioning:

```bash
ansible-playbook -i inventory run-vms.yaml
```

Dev inventory example:

```
[all:vars]
base_path=/home/root
subnet="192.168.1"
num_of_vms=4
disk_size=80
base_ip=50
ssh_user=vagrant
ram_size=4096
cpus=1
vm_base_name=mynode
```

Ansible cfg example:

```
[defaults]
remote_user = root
inventory = ./inventory
private_key_file = /Users/test/.ssh/id_rsa
host_key_checking = False
```

When Vagrant provision is completed `hosts` file will be created in `bare-metal/ansible`. Copy this file to `ansible/inventory` and you can do node-provision as usual, for example:

```bash
ansible-playbook -i inventory -v main.yaml
```

Default `DISK_MOUNTPOINT` for VirtualBox VMs: `/dev/sdb`

## Destroy machines

To destroy running VMs run:

```bash
ansible-playbook -i inventory run-vms.yaml --tags destroy
```
