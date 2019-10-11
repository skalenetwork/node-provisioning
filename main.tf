provider "digitalocean" {
  token = var.do_token
}

resource "digitalocean_volume" "datavolume" {
  count = var.COUNT
  name = "${var.prefix}-${count.index}"
  region = var.volume_region
  size = var.volume_size
}

resource "digitalocean_droplet" "node" {
  count = var.COUNT
  image = "ubuntu-18-04-x64"
  name = "${var.prefix}-${count.index}"
  region = var.region
  size = var.instance_size

  ssh_keys = var.ssh_fingerprints

  connection {
    type = "ssh"
    user = "root"
    host = self.ipv4_address
    private_key = "${file("~/.ssh/id_rsa")}"
  }

  volume_ids = [
    digitalocean_volume.datavolume[count.index].id]

  provisioner "file" {
    source = "./scripts/provision_node.sh"
    destination = "/tmp/provision_node.sh"
  }

  provisioner "file" {
    source = "./wallets/wallet-${count.index}.txt"
    destination = "/tmp/wallet.txt"
  }

  provisioner "remote-exec" {
    inline = [
      "export VERSION_NUM=${var.cli_version}",
      "export CLI_SPACE=${var.cli_space}",

      "export STREAM=${var.stream}",
      "export TOKEN=${var.github_token}",
      "export DOCKER_USERNAME=${var.docker_username}",
      "export DOCKER_PASSWORD=${var.docker_password}",
      "export DISK_MOUNTPOINT=${var.disk_mountpoint}",
      "export DB_PASSWORD=${var.db_password}",
      "export SKALE_USERNAME=${var.username}",
      "export PASSWORD=${var.password}",
      "export NODE_IP=${self.ipv4_address}",
      "export NODE_PORT=${var.node_port}",
      "export NODE_NAME=${var.prefix}-${count.index}",
      "export ETH_PRIVATE_KEY=$(cat /tmp/wallet.txt)",

      "export ENDPOINT=${var.endpoint}",
      "export IMA_ENDPOINT=${var.ima_endpoint}",

      "export MANAGER_URL=${var.manager_url}",
      "export IMA_URL=${var.ima_url}",
      "export FILEBEAT_URL=${var.filebeat_url}",

      "chmod +x /tmp/provision_node.sh",
      "sudo -E bash /tmp/provision_node.sh",
    ]
  }
}

output "public_ips" {
  description = "map output of the hostname and public ip for each instance"
  value = zipmap(
  digitalocean_droplet.node.*.name,
  digitalocean_droplet.node.*.ipv4_address,
  )
}

