# Skale automation

[![Discord](https://img.shields.io/discord/534485763354787851.svg)](https://discord.gg/vvUtWJB)

This repo will help you to deploy and register multiple SKALE nodes in the cloud automatically.

## Host requirements

- Terraform >= 0.12
- Python >= 3.6

## Supported provides

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

### Run provision script

```bash
bash run.sh
```