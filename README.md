# SKALE Node Provisoning

[![Discord](https://img.shields.io/discord/534485763354787851.svg)](https://discord.gg/vvUtWJB)

This repo will help deploy and register multiple SKALE nodes in the cloud automatically.

NOTE: This is for QA and testing purposes only.

## Host requirements

- Terraform >= 0.12
- Python >= 3.6

## Supported providers

- DigitalOcean
- A̶W̶S̶ (deprecated and should be updated)

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

### Upload SSL certificates

1) Copy `cert.pem` and `privkey.pem` files to the `ansible/files` directory
2) Run:
3) 
```bash
ansible-playbook -i path-to-your-inventory ssl.yaml 
```
