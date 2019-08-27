#!/usr/bin/env bash

terraform apply
terraform output -json instance_ips > result.json