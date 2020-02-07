variable "do_token" {}

variable "instance_size" {}

variable "prefix" {}

variable "region" {}

variable "volume_region" {}

variable "volume_size" {}

variable "docker_lvmpy_stream" {}

variable "ssh_fingerprints" {
  type = list(string)
}

variable "container_configs_stream" {}

variable "COUNT" {}

variable "cli_version" {}

variable "cli_space" {}

variable "docker_username" {}

variable "docker_password" {}

variable "db_password" {}

variable "disk_mountpoint" {}

variable "username" {}
variable "password" {}
variable "node_port" {}

variable "manager_url" {}
variable "ima_url" {}

variable "endpoint" {}
variable "ima_endpoint" {}

variable "filebeat_url" {}
variable "sgx_url" {}
