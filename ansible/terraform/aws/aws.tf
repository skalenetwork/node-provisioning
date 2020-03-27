# https://cloud-images.ubuntu.com/locator/ec2/ for ami identication

variable "NUMBER" {
  default = 2
}

provider "aws" {
  access_key = "AKIAVNK4IZ3P7EX6TXJV"
  secret_key = "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"
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
  key_name = "ivan-key"

  root_block_device {
    volume_size = var.root_volume_size
  }

  tags = {
    Name = "${var.prefix}-${count.index}"
  }

  provisioner "local-exec" {
    command = "echo 'node${count.index} ansible_host=${self.public_ip}' >> hosts"
  }
}

