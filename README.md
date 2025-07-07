# SKALE and Mirage Node Provisoning

[![Discord](https://img.shields.io/discord/534485763354787851.svg)](https://discord.gg/vvUtWJB)

This repo will help deploy and register multiple SKALE and Mirage nodes in the cloud automatically.

NOTE: This is for QA and testing purposes only.

- [Mirage Node Provisoning](#mirage-node-provisoning)
  - [Mirage network creating](#mirage-network-creating)
    - [Setup Mirage boot nodes](#1-prepare-inventory)
    - [Prepare inventory](#2-setup-mirage-boot-nodes)
    - [Create schain](#3-create-schain)
    - [Deploy Mirage contracts](#4-deploy-mirage-contracts) 
    - [Migrate Mirage boot nodes](#5-migrate-mirage-boot-nodes)

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


# Mirage Node Provisioning

## Mirage network creating

### 1. Prepare inventory
1) Set `node_type=mirage_boot`
2) Set `build_type=git` (to use Docker image versions specified in the corresponding branch of the 
`skale-node` repository on GitHub), or `build_type=source` (to build from source). In the second 
case, set the appropriate local paths to the required cloned repositories and set  
`container_configs_dir` variable (usually it's `/root/skale-node`).
3) Don't forget to set all other necessary variables like `eth_private_key`, `endpoint`, etc.

### 2. Setup Mirage boot nodes
```bash
ansible-playbook -i inventory main.yaml
```
The following playbooks are processed here: _deploy_contracts.yaml, sgx_sim.yaml, setup.yaml, 
validator.yaml, signature.yaml, link_addresses.yaml, register.yaml_

### 3. Create schain
1) Set the schain name (it must match the name specified in the `mirage_static_params.yaml` file for 
the corresponding network in the relevant branch of the `skale-node` repository). For example, for 
the **devnet**, the typical name is `mirage-devnet1`.
2) Set the desired `chain_type` (for example, LARGE4 - for 4-nodes chain )
3) Run the following playbook:
```bash
ansible-playbook -i inventory create_chain.yaml
```
### 4. Deploy Mirage contracts
1) Set `mirage_tag` variable (Mirage manager version)
2) Set `boot_endpoint` variable (endpoint of schain that was created before)
3) Run the following playbook: 
```bash
ansible-playbook -i inventory deploy_mirage_manager.yaml
```
### 5. Migrate Mirage boot nodes
1) Set `node_type=mirage`
2) Run the following playbook:
```bash
ansible-playbook -i inventory mirage_migrate.yaml
```


# SKALE Node Provisioning

## Host requirements

- Terraform >= 0.12
- Python >= 3.6

## Supported providers

- AWS

## Usage

### Secrets preparation

1) Copy contents of the `terraform.tfvars.template` to the `terraform.tfvars` and fill all variables
2) Set following variables to the environment:

```
PROVIDER - Cloud provider: `do` or `aws`
ENDPOINT - Endpoint of the ETH network with manager contract
NODES - Number of nodes to be created
SKALE_AMOUNT - Amount of SKALE tokens to transfer
ETH_AMOUNT- Amount of ETH to transfer
ETH_PRIVATE_KEY - Base ETH private key to send funds
```

### Provision SKALE nodes in the cloud

```bash
bash run.sh
```

## Setup on existent nodes from sources

Ansible directory contains ansible provision for setuping skale node system.

Steps to run provision
1. Firstly you should create two nodes and attach external volume to it.
2. Install ansible on your machine.
3. Then you should copy inventory template from inventory/dev and fill it with absent fields.
4. Also you should add information about host that you cerated before
5. Run ```ansible-playbook -i path-to-your-inventory main.yaml```

### Other options

Recreates accounts from which sgx key will be configured.
```
ansible-playbook -i path-to-your-inventory wallet.yaml
```

Setups node on remove server:
1. Uploads sources.
2. Reinstalls skale-cli.
3. Runs skale node init.
4. Registers node on manager.

```
ansible-playbook -i path-to-your-inventory setup.yaml
```

Installs needed dependecies and setups os configs.
```
ansible-playbook -i path-to-your-inventory base.yaml
```

Destroys all containers, removes .skale, reruns setup.yaml steps.
```
ansible-playbook -i path-to-your-inventory restart.yaml 
```

Destroys all containers, removes .skale, reruns setup.yaml steps.
```
ansible-playbook -i path-to-your-inventory restart.yaml 
```

Recreates accounts and runs restart.yaml steps.
```
ansible-playbook -i path-to-your-inventory restart.yaml 
```

## Tasks

### Deploy SM

Required variables in the inventory:

```
manager_tag=''
eth_private_key=''
endpoint=''
deploy_gas_price=''

aws_key='' # for S3 upload
aws_secret='' # for S3 upload
```

Deploy and upload ABIs to AWS S3:

```bash
ansible-playbook -i inventory deploy_contracts.yaml
```

Deploy only:

```bash
ansible-playbook -i inventory deploy_contracts.yaml --tags deploy_contracts
```

Upload only (from `helper-scripts/contracts_data/manager.json`):

```bash
ansible-playbook -i inventory deploy_contracts.yaml --tags upload_contracts
```


### Upload SSL certificates

1) Copy `cert.pem` and `privkey.pem` files to the `ansible/files` directory
2) Run:
3) 
```bash
ansible-playbook -i path-to-your-inventory ssl.yaml 
```

### Upload authorized_keys to nodes

1) add `authorized_keys` file with all id_rsa.pub what you want to add for access on nodes to the `ansible/files` directory
2) Run:
```bash
ansible-playbook -i path-to-your-inventory upload_authorized_keys.yaml 
```

### Run main script without IMA deployment

```bash
ansible-playbook -i inventory main.yaml --skip-tags deploy_ima,upload_ima
```

### Run skaled monitor

1) Create if not exists virtual env for python 3.7 or higher in root of project
and activate she before script start
2) Run from root of roject:
```bash
pip install -r skale-nodes/ansible/requirements.txt
```
3) copy `inventory-template` like `inventory` and fill `dev` file with absent fields.
4) Add `node_ips.json` file with all ips what you want 
(example `{"node_name": "node_ip", ..., "node_name": "node_ip"}`) 
to the `ansible/files` directory
5) Go to `skale-nodes/ansible` dir and run:
```bash
bash utils/generate_hosts.sh
```
```bash
ansible-playbook -i inventory run_monitor.yaml
```

