variable "do_token" {
}

variable "instance_size" {
}

variable "prefix" {
}

variable "region" {
}

variable "volume_region" {
}

variable "volume_size" {
}

variable "ssh_fingerprints" {
  type = list(string)
}

variable "COUNT" {
  default = "2"
}

variable "cli_version" {
}

variable "cli_space" {
}

variable "github_token" {
}

variable "git_branch" {
}

variable "docker_username" {
}

variable "docker_password" {
}

variable "db_password" {
}

variable "disk_mountpoint" {
}

variable "username" {
}

variable "password" {
}

variable "node_port" {
}

provider "digitalocean" {
  token = var.do_token
}

resource "digitalocean_volume" "datavolume" {
  count  = var.COUNT
  name   = "${var.prefix}-${count.index}"
  region = var.volume_region
  size   = var.volume_size
}

resource "digitalocean_droplet" "node" {
  count  = var.COUNT
  image  = "ubuntu-18-04-x64"
  name   = "${var.prefix}-${count.index}"
  region = var.region
  size   = var.instance_size

  ssh_keys = var.ssh_fingerprints

  connection {
    type = "ssh"
    user = "root"
    host = self.ipv4_address
    private_key = "${file("~/.ssh/id_rsa")}"
  }

  volume_ids = [digitalocean_volume.datavolume[count.index].id]

  provisioner "file" {
    source      = "./scripts/provision_node.sh"
    destination = "/tmp/provision_node.sh"
  }

  provisioner "file" {
    source      = "./wallets/wallet-${count.index}.txt"
    destination = "/tmp/wallet.txt"
  }

  provisioner "remote-exec" {
    inline = [
      "export VERSION_NUM=${var.cli_version}",
      "export CLI_SPACE=${var.cli_space}",

      "export TOKEN=${var.github_token}",
      "export BRANCH=${var.git_branch}",
      "export DOCKER_USERNAME=${var.docker_username}",
      "export DOCKER_PASSWORD=${var.docker_password}",
      "export DISK_MOUNTPOINT=${var.disk_mountpoint}",
      "export DB_PASSWORD=${var.db_password}",
      "export USERNAME=${var.username}",
      "export PASSWORD=${var.password}",
      "export NODE_IP=${self.ipv4_address}",
      "export NODE_PORT=${var.node_port}",
      "export NODE_NAME=${var.prefix}-${count.index}",
      "export ETH_PRIVATE_KEY=$(cat /tmp/wallet.txt)",
      "chmod +x /tmp/provision_node.sh",
      "sudo -E bash /tmp/provision_node.sh",
    ]
  }
}

//resource "digitalocean_volume_attachment" "foobar" {
//  count = "${var.COUNT}"
//
//  name = "${var.prefix}-${count.index}"
//  droplet_id = "${digitalocean_droplet.node.id}"
//  volume_id = "${digitalocean_volume.datavolume.id}"
//}

output "public_ips" {
  description = "map output of the hostname and public ip for each instance"
  value = zipmap(
    digitalocean_droplet.node.*.name,
    digitalocean_droplet.node.*.ipv4_address,
  )
}

