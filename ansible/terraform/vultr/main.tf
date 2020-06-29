provider "vultr" {
    api_key = var.api_key
}

resource "vultr_ssh_key" "main_key" {
    name = "main_key"
    ssh_key = var.ssh_key
}

resource "vultr_block_storage" "datavolume" {
    count = var.NUMBER
    region_id = var.region_id
    size_gb = var.volume_size
    attached_id = vultr_server.node[count.index].id
    depends_on = [vultr_server.node]
}

resource "vultr_server" "node" {
    count = var.NUMBER
    plan_id = var.plan_id
    region_id = var.region_id
    os_id = 270 # Ubuntu 18.04 x64
    label = "${var.prefix}-${count.index}"
    hostname = "${var.prefix}-${count.index}"
    ssh_key_ids = [vultr_ssh_key.main_key.id]
    depends_on = [vultr_ssh_key.main_key]

    provisioner "local-exec" {
        command = "echo 'node${count.index} ansible_host=${self.main_ip}' >> hosts"
    }
}

output "public_ips" {
    description = "map output of the hostname and public ip for each instance"
    value = zipmap(
        vultr_server.node.*.hostname,
        vultr_server.node.*.main_ip,
    )
}

output "ids_of_droplets" {
    description = "map output of the hostname and ID for each instance"
    value = zipmap(
        vultr_server.node.*.hostname,
        vultr_server.node.*.id,
    )
}
