variable "do_token" {}

variable "instance_size" {}

variable "prefix" {}

variable "region" {}

variable "volume_region" {}

variable "volume_size" {}

variable "ssh_fingerprints" {
  type = list(string)
}
