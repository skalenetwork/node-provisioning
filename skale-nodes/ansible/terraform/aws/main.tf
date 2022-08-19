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
  count = var.NUMBER
  device_name = "/dev/sdd"
  volume_id   = aws_ebs_volume.lvm_volume[count.index].id
  instance_id = var.spot_instance ? aws_spot_instance_request.node[count.index].spot_instance_id : aws_instance.node[count.index].id

  provisioner "remote-exec" {
    inline = [
      "export VOLUME_SIZE=${var.lvm_volume_size}",
      "echo /dev/`lsblk -do NAME,SIZE | grep $VOLUME_SIZE | cut -d ' ' -f 1` | sudo tee /root/lvm-block-device",
    ]
    connection {
      type     = "ssh"
      user     = "ubuntu"
      host = aws_eip.node_eip[count.index].public_ip
      # host = "${var.spot_instance ? aws_spot_instance_request.node[count.index].public_ip : aws_instance.node[count.index].public_ip}"
      private_key = file(var.ssh_private_key_path)
    }
  }

}

resource "aws_ebs_volume" "lvm_volume" {
  count = var.NUMBER
  # availability_zone = var.availability_zone
  availability_zone = "${var.region}${var.zones[count.index % 3]}"
  size = var.lvm_volume_size
  volume_type = var.lvm_volume_type

  tags = {
    Name = "${var.prefix}-${count.index}-lvm-volume"
  }
}


resource "aws_spot_instance_request" "node" {
  count = var.spot_instance ? var.NUMBER : 0
  spot_price    = var.spot_price[var.instance_type]
  ami           = data.aws_ami.ubuntu.id
  instance_type = var.instance_type
  availability_zone = "${var.region}${var.zones[count.index % 3]}"
  wait_for_fulfillment = true
  vpc_security_group_ids = [aws_security_group.security_group.id]
  key_name = var.key_name

  root_block_device {
    volume_size = var.root_volume_size
    volume_type = var.root_volume_type
  }

  tags = {
    Name = "${var.prefix}-${count.index}"
  }
  # provisioner "local-exec" {
  #   command = "echo 'node${count.index} ansible_host=${self.public_ip}' >> hosts"
  # }
}

resource "aws_instance" "node" {
  count = !var.spot_instance ? var.NUMBER : 0
  ami   = data.aws_ami.ubuntu.id
  instance_type = var.instance_type
  # availability_zone = var.availability_zone
  availability_zone = "${var.region}${var.zones[count.index % 3]}"
  key_name = var.key_name
  vpc_security_group_ids = [aws_security_group.security_group.id]

  root_block_device {
    volume_size = var.root_volume_size
    volume_type = var.root_volume_type
  }

  tags = {
    Name = "${var.prefix}-${count.index}"
  }
  # provisioner "local-exec" {
  #   command = "echo 'node${count.index} ansible_host=${self.public_ip}' >> hosts"
  # }
}


data "aws_vpc" "default" {
  default = true
}

resource "aws_security_group" "security_group" {
  vpc_id       = data.aws_vpc.default.id
  name         = var.security_group
  description  = "Security group for nodes"

  # allow ingress of port 22
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 9100
    to_port     = 9100
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 8080
    to_port     = 8080
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 10000
    to_port     = 12000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 53
    to_port     = 53
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 3009
    to_port     = 3009
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # allow egress of all ports
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  tags = {
    Name = var.security_group
    Description = "Security Group for nodes"
  }
}


resource "aws_eip_association" "eip_assoc" {
  count = var.NUMBER
  allocation_id = aws_eip.node_eip[count.index].id
  instance_id = var.spot_instance ? aws_spot_instance_request.node[count.index].spot_instance_id : aws_instance.node[count.index].id
  provisioner "local-exec" {
    command = "echo 'node${count.index} ansible_host=${self.public_ip}' >> hosts"
  }
}

resource "aws_eip" "node_eip" {
  count = var.NUMBER
}
