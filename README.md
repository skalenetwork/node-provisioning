# Skale automation

#### Requirements

- terraform
- python 3.6+
- bash

##### Supported provides

- DigitalOcean
- AWS

#### Run Skale nodes in the cloud 

```bash
export $(cat .env | xargs) && bash run.sh
```