# Configure the AWS Provider
provider "aws" {
  access_key = "${var.aws_access_key}"
  secret_key = "${var.aws_secret_key}"
  region     = "us-east-2"
}

variable "COUNT" {
  default = "2"
}

variable "rpc_ip" {}
variable "rpc_ws_port" {}

variable "disk_mountpoint" {}


variable "ssh_fingerprints" {
  type = "list"
}
variable "aws_access_key" {}
variable "aws_secret_key" {}
variable "ami" {}
variable "instance_type" {}
variable "security_group1" {}
variable "subnet_id" {}
variable "volume_size" {}
variable  "instance_name" {}

variable "key_name" {}

variable "github_token" {}
variable "git_branch" {
  default = "test-ash"
}
variable "docker_username" {}
variable "docker_password" {}

variable "address" {}
variable "private_key" {}
variable "pem_file" {}

variable "db_root_password" {}
variable "db_user" {}
variable "db_password" {}
variable "db_port" {}

variable "prefix" {}

variable "username" {
  default = "ubuntu"
}
variable "password" {}

# Create a web server
resource "aws_instance" "node" {
  count = "${var.COUNT}"
  ami = "${var.ami}"
  instance_type = "${var.instance_type}"
  security_groups = ["${var.security_group1}"]
  subnet_id = "${var.subnet_id}"
  key_name = "${var.key_name}"
  root_block_device {
    volume_size = "${var.volume_size}"
  }
  tags {
    Name = "${var.instance_name}-${count.index}"
  }
  connection {
    user = "ubuntu"
    private_key = "${file(var.pem_file)}"
  }

  provisioner "file" {
    source = "../scripts/provision_host.sh"
    destination = "/tmp/provision_host.sh"
  }

  provisioner "file" {
    source = "../node_wallets.json"
    destination = "/tmp/node_wallets.json"
  }

  provisioner "file" {
    source = "../../config/data.json"
    destination = "/tmp/data.json"
  }

  provisioner "remote-exec" {
    inline = [
      "export GITHUB_TOKEN=${var.github_token}",
      "export GIT_BRANCH=${var.git_branch}",
      "chmod +x /tmp/provision_host.sh",
      "sudo -E bash /tmp/provision_host.sh",
    ]
  }

  provisioner "file" {
    source = "../scripts/provision_node.sh"
    destination = "/tmp/provision_node.sh"
  }

  provisioner "remote-exec" {
    inline = [
      "export GITHUB_TOKEN=${var.github_token}",
      "export DOCKER_USERNAME=${var.docker_username}",
      "export DOCKER_PASSWORD=${var.docker_password}",
      "export ADDRESS=${var.address}",
      "export PRIVATE_KEY=${var.private_key}",

      "export RPC_IP=${var.rpc_ip}",
      "export RPC_PORT=${var.rpc_ws_port}",

      "export DB_ROOT_PASSWORD=${var.db_root_password}",
      "export DB_USER=${var.db_user}",
      "export DB_PASSWORD=${var.db_password}",
      "export DB_PORT=${var.db_port}",

      "export DISK_MOUNTPOINT=${var.disk_mountpoint}",
      "export DEPLOY_INDEX=${count.index}",

      "chmod +x /tmp/provision_node.sh",
      "sudo -E bash /tmp/provision_node.sh ${self.public_ip} ${var.username} ${var.password}",
    ]
  }
  # ...
}

output "instance_ips" {
  value = ["${aws_instance.node.*.public_ip}"]
}