variable "NUMBER" {
  default = 2
}

provider "digitalocean" {
  token = var.do_token
}

resource "digitalocean_volume" "datavolume" {
  count = var.NUMBER
  name = "${var.prefix}-${count.index}"
  region = var.volume_region
  size = var.volume_size
}

resource "digitalocean_droplet" "node" {
  count = var.NUMBER
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

  provisioner "local-exec" {
    command = "echo 'node${count.index} ansible_host=${self.ipv4_address}' >> hosts"
  }
}
