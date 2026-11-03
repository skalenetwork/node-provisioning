# SKALE and Fair Node Provisioning

[![Discord](https://img.shields.io/discord/534485763354787851.svg)](https://discord.gg/vvUtWJB)

This repo will help deploy and register multiple SKALE and Fair nodes in the cloud automatically.

NOTE: This is for QA and testing purposes only.

- [Fair Node Provisoning](#fair-node-provisoning)
  - [Fair network creating](#fair-network-creating)
    - [Setup Fair boot nodes](#1-prepare-inventory)
    - [Prepare inventory](#2-setup-fair-boot-nodes)
    - [Create schain](#3-create-schain)
    - [Deploy Fair contracts](#4-deploy-fair-contracts) 
    - [Migrate Fair boot nodes](#5-migrate-fair-boot-nodes)
    - [Setup Fair nodes](#6-setup-fair-nodes)

- [SKALE Node Provisoning](#skale-node-provisoning)
  - [Host requirements](#host-requirements)
  - [Supported providers](#supported-providers)
  - [Usage](#usage)
    - [Secrets preparation](#secrets-preparation)
    - [Provision SKALE nodes in the cloud](#provision-skale-nodes-in-the-cloud)
  - [Setup on existent nodes from sources](#setup-on-existent-nodes-from-sources)
    - [Other options](#other-options)
  - [Tasks](#tasks)
    - [Deploy SM](#deploy-sm)
    - [Upload SSL certificates](#upload-ssl-certificates)
    - [Upload authorized_keys to nodes](#upload-authorized_keys-to-nodes)
    - [Run main script without IMA deployment](#run-main-script-without-ima-deployment)
    - [Run skaled monitor](#run-skaled-monitor)
    - [Upgrade OS packages](#upgrade-os-packages)

- [Pipelines](#pipelines)

- [Bare-metal VMs (KVM)](#bare-metal-vms-kvm)


# Fair Node Provisioning

## Fair network creation

### 1. Prepare inventory
1) Set `node_type=fair_boot`
2) Set `build_type=git` (to use Docker image versions specified in the corresponding branch of the 
`skale-node` repository on GitHub), or `build_type=source` (to build from source). In the second 
case, set the appropriate local paths to the required cloned repositories.
3) Don't forget to set all other necessary variables like `eth_private_key`, `endpoint`, etc.

### 2. Setup Fair boot nodes
Run these playbooks in order: _run_anvil.yaml, deploy_contracts.yaml, sgx_sim.yaml, setup.yaml,
validator.yaml, signature.yaml, link_addresses.yaml, register.yaml_. `fair_pipeline.yaml` runs
steps 2-5 in one go (see [Pipelines](#pipelines)).

### 3. Create schain
1) Set the schain name (it must match the name specified in the `fair_static_params.yaml` file for 
the corresponding network in the relevant branch of the `skale-node` repository). For example, for 
the **devnet**, the typical name is `fair-devnet1`.
2) Set the desired `chain_type` (for example, LARGE4 - for 4-nodes chain )
3) Run the following playbook:
```bash
ansible-playbook -i inventory create_chain.yaml
```
### 4. Deploy Fair contracts
1) Set `fair_tag` variable (Fair manager version)
2) Set `boot_endpoint` variable (endpoint of schain that was created before)
3) Run the following playbook: 
```bash
ansible-playbook -i inventory deploy_fair_manager.yaml
```
### 5. Migrate Fair boot nodes
1) Set `node_type=fair`
2) Run the following playbook:
```bash
ansible-playbook -i inventory fair_migrate.yaml
```
### 6. Setup Fair nodes
1) Set `node_type=fair`
2) Run the following playbook:
```bash
ansible-playbook -i inventory fair_node.yaml
```

# SKALE Node Provisioning

## Host requirements

- Python 3.14 (`.python-version`) with `skale-nodes/ansible/requirements.txt` installed:
  `uv venv && uv pip install -r skale-nodes/ansible/requirements.txt`, and the DigitalOcean
  collection that ansible no longer ships:
  `ansible-galaxy collection install -r skale-nodes/ansible/requirements.yml`
- Docker, jq and rsync on the machine running Ansible (contracts are deployed from Docker images;
  `build_type=source` copies the clones with rsync)
- Terraform >= 1.17 (only to create cloud machines)
- The `helper-scripts` submodule: `git submodule update --init`

## Supported providers

- AWS

## Usage

### Secrets preparation

Copy `skale-nodes/ansible/inventory-template` to `skale-nodes/ansible/inventory` and fill `dev`.
Copy `skale-nodes/ansible/terraform/aws/terraform.tfvars.template` to `terraform.tfvars` in the
same directory and fill all variables.

### Provision SKALE nodes in the cloud

`create.sh` creates the machines, writes them to `inventory/hosts` and runs `skale_pipeline.yaml`;
`destroy.sh` removes them:

```bash
cd skale-nodes/ansible
NODES_NUMBER=4 bash create.sh
NODES_NUMBER=4 bash destroy.sh
```

## Setup on existent nodes from sources

Ansible directory contains ansible provision for setuping skale node system.

Steps to run provision
1. Firstly you should create two nodes and attach external volume to it.
2. Install ansible on your machine.
3. Then you should copy inventory template from inventory-template/dev and fill it with absent fields.
4. Also you should add information about host that you cerated before
5. Run ```ansible-playbook -i path-to-your-inventory skale_pipeline.yaml```

### Other options

Setups node on remove server:
1. Uploads sources.
2. Reinstalls skale-cli.
3. Runs skale node init.

```
ansible-playbook -i path-to-your-inventory setup.yaml
```

Installs needed dependecies and setups os configs.
```
ansible-playbook -i path-to-your-inventory base.yaml
```

## Tasks

### Deploy SM

Required variables in the inventory:

```
manager_tag=''
ima_tag=''
eth_private_key=''
endpoint=''
deploy_gas_price=''
```

Deploy and save the contract addresses:

```bash
ansible-playbook -i inventory deploy_contracts.yaml
```

Deploy only:

```bash
ansible-playbook -i inventory deploy_contracts.yaml --tags deploy_sm,deploy_ima
```

Save the addresses only (from `helper-scripts/contracts_data/manager.json` and `ima.json`):

```bash
ansible-playbook -i inventory deploy_contracts.yaml --tags upload_sm,upload_ima
```


### Upload SSL certificates

1) Set `cert_mode=custom` and `ssl_src` to a directory with `fullchain.pem` and `privkey.pem`
2) Run:
```bash
ansible-playbook -i path-to-your-inventory ssl.yaml 
```

### Upload authorized_keys to nodes

1) add `authorized_keys` file with all id_rsa.pub what you want to add for access on nodes to the `ansible/files` directory
2) Run:
```bash
ansible-playbook -i path-to-your-inventory base.yaml --tags ssh
```

### Run main script without IMA deployment

Set `ima_tag` and `ima_contracts` to an existing IMA deployment (preflight checks `ima_tag`, the node
config needs `ima_contracts`), then run:

```bash
ansible-playbook -i inventory skale_pipeline.yaml --skip-tags deploy_ima,upload_ima
```

### Run skaled monitor

Starts `files/node-side-monitor.sh` (skaled process and log exporters) on the nodes:

```bash
ansible-playbook -i inventory deploy_net_monitor.yaml
```

### Upgrade OS packages

Runs `apt update && apt upgrade` on every host in the inventory, one host at a time, so the nodes
of a chain don't all restart Docker at once. Use `--limit` to pick hosts (e.g. `--limit kvm_host`
for the bare-metal servers, `--limit nodes`) and `-e upgrade_serial=<n>` to upgrade more at a time:

```bash
ansible-playbook -i inventory upgrade_packages.yaml
```

Hosts that need a reboot afterwards are listed; they are rebooted, one at a time, only with
`-e upgrade_reboot=true`. Rebooting a bare-metal server also restarts all its VMs.

# Pipelines

`skale_pipeline.yaml` and `fair_pipeline.yaml` run a whole setup (anvil, contracts, SGX simulator,
nodes, registration, chain; Fair also deploys its contracts and migrates the boot nodes).
`fair_node.yaml`, `skale_node_passive.yaml` and `fair_node_passive.yaml` set up more nodes.

`skale_node_passive.yaml` first whitelists the nodes' IPs in SyncManager
(`whitelist_passive_skale.yaml`), so the sChain nodes let them sync. Each IP that no range covers
yet gets a one-address range named `<host>-<ip>`. Adding ranges needs `SYNC_MANAGER_ROLE` for
`eth_private_key`; the script grants it with `eth_private_key`, which is a SyncManager admin when
`deploy_contracts.yaml` deployed the contracts with it (with existing contracts, `eth_private_key`
has to be a SyncManager admin).

They start with `preflight.yaml`, which checks the inventory values they need (keys, contract
tags, CLI URLs or source paths, `base_domain_name`, `chain_name`, ...) before changing anything.

Values the playbooks produce for later runs (contract addresses, the anvil endpoint and key,
`node_type` while Fair boot nodes are set up) are saved in `group_vars/all` next to the inventory,
e.g. `inventory/group_vars/all` (or `group_vars/all/generated.yml` when `group_vars/all` is a
directory), so each inventory keeps its own. They take precedence over `[all:vars]` in the
inventory file: delete a line, or run `cleanup_local.yaml` to clear them all. Older versions saved
them in `skale-nodes/ansible/group_vars/all`, where they apply to every inventory: the pipelines stop
until you move those lines next to the inventory they belong to, or delete them.

With `build_type=source`, each local clone is mirrored into a fixed directory under `base_path`
(`skale-admin`, `node-cli`, ...), whatever the clone is called. The nodes use the compose file
from your skale-node clone: `files/compose_from_source.py` adds a build section and a local image
name to the services built from those repos (admin, api, transaction-manager, ...) and leaves
everything else as it is. If skale-node adds a service that should be built from source, add it to
`SERVICES` in that script. To see what it changes:

```bash
diff <skale-node>/docker-compose.yml <(python3 files/compose_from_source.py <skale-node>/docker-compose.yml /root)
```

# Bare-metal VMs (KVM)

`skale-nodes/ansible/vms.yaml` creates node machines as KVM VMs on your own server, so the
playbooks above run on them the same way as on cloud machines.

Add the server to the `kvm_host` group and every host that should become a VM to the `vms` group.
Keep them in the same inventory file as your node groups. Each VM uses its `ansible_host` as its
static LAN address:

```
[kvm_host]
bm-1 ansible_host=<server-ip> vm_lan_iface=eno2

[nodes]
node-0 ansible_host=192.168.1.50
node-1 ansible_host=192.168.1.51

[vms:children]
nodes

[vms:vars]
ansible_ssh_user=root
vm_cpus=2
vm_ram_mb=8192
vm_datadir_gb=80
```

Create the VMs (existing VMs are left as they are), then provision them as usual:

```bash
ansible-playbook -i inventory vms.yaml
```
```bash
ansible-playbook -i inventory base.yaml
```

- With several servers, list them all in `kvm_host` and set `vm_kvm_host=<server name>` for a VM or a group.
  VMs without it go to the first server.
- Each VM has a NAT interface for internet access and a LAN interface on `vm_lan_iface` with the static IP.
  The default route goes through NAT, so replies to hosts outside the LAN subnet are dropped: only
  machines on that subnet, including the one running Ansible, can connect to the VMs. Set
  `vm_lan_gateway=<LAN router>` to route through the LAN instead.
- The server can't reach its own VMs over macvtap, so it can't be an SSH jump host for them. Set
  `vm_lan_bridge` to an existing bridge on the server if it must.
- The VM data disk is `/dev/sdb`, so set `block_device=/dev/sdb`.
- root on each VM accepts your `~/.ssh/id_ed25519`, `id_ecdsa` and `id_rsa` keys (whichever exist on the machine
  running Ansible). Set `vm_ssh_public_key_file` to use a different key.
- When a VM is created, its old SSH host key is removed from `~/.ssh/known_hosts` on that machine.
- `vms.yaml` always logs into the VMs as root. Other playbooks use the inventory user, so keep
  `ansible_ssh_user=root` in `[vms:vars]`.
- `base.yaml` replaces root's `authorized_keys` with `files/authorized_keys`, so keep your key in that file.
- Changes to VM size or IP apply only when the VM is recreated.
- All settings and their defaults are in `roles/vms/defaults/main.yaml`.

Remove the VMs and their disks:

```bash
ansible-playbook -i inventory vms.yaml --tags destroy
```

