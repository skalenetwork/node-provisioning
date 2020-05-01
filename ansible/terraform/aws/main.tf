# https://cloud-images.ubuntu.com/locator/ec2/ for ami identication

variable "NUMBER" {
  default = 2
}

provider "aws" {
  access_key = var.access_key
  secret_key = var.secret_key
  region = var.region
}

data "aws_ami" "ubuntu" {
  most_recent = true

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-bionic-18.04-amd64-server-*"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }

  owners = ["099720109477"] # Canonical
}


resource "aws_volume_attachment" "ebs_att" {
  count = "${var.NUMBER}"
  device_name = "/dev/sdd"
  volume_id   = aws_ebs_volume.lvm_volume[count.index].id
  instance_id = aws_instance.node[count.index].id

  provisioner "remote-exec" {
    inline = [
      "export VOLUME_SIZE=${var.lvm_volume_size}",
      "echo /dev/`lsblk -do NAME,SIZE | grep $VOLUME_SIZE | cut -d ' ' -f 1` | sudo tee /root/lvm-block-device",
    ]
    connection {
      type     = "ssh"
      user     = "ubuntu"
      host = aws_eip.node_eip[count.index].public_ip
      private_key = file(var.ssh_private_key_path)
    }
  }

}

resource "aws_ebs_volume" "lvm_volume" {
  count = "${var.NUMBER}"
  availability_zone = var.availability_zone
  size = var.lvm_volume_size

  tags = {
    Name = "LvmVolume"
  }  
}

resource "aws_instance" "node" {
  count = "${var.NUMBER}"
  ami           = "${data.aws_ami.ubuntu.id}"
  instance_type = var.instance_type
  availability_zone = var.availability_zone
  key_name = var.key_name

  root_block_device {
    volume_size = var.root_volume_size
  }

  tags = {
    Name = "${var.prefix}-${count.index}"
  }

}


resource "aws_eip" "node_eip" {
   count = "${var.NUMBER}"
   instance = aws_instance.node[count.index].id
   provisioner "local-exec" {
     command = "echo 'node${count.index} ansible_host=${self.public_ip}' >> hosts"
   }
}
