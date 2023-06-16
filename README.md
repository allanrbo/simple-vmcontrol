Simple VM Control UI
====================

Very minimal web UI for creating and deleting Libvirt/KVM VMs.

I wrote this quick and dirty system because it seemed the existing web UIs there were for Libvirt/KVM had more dependencies than I wanted to have installed on my VM host. This system is therefore self contained and only dependant on Python 3, besides Libvirt and KVM itself of course. No other libraries needed.

![Screenshot](https://github.com/allanrbo/simple-vmcontrol/blob/master/docs/screenshot1.png?raw=true)

Server setup
------------
My VM host is an Ubuntu 20.04 installation.

### Installation

Run the following as root:

    useradd simple-vmcontrol_svc

    cd /usr/lib
    git clone https://github.com/allanrbo/simple-vmcontrol.git
    cd simple-vmcontrol
    cp config.default.json config.json
    # Modify config.json as needed.
    # Generate password hashes using generate_password_hash.py.

    # Generate web server's HTTPS cert:
    openssl genrsa -out /etc/ssl/simple-vmcontrol.key 2048
    openssl req -new -key /etc/ssl/simple-vmcontrol.key -subj "/CN=server" -x509 -days 3650 -out /etc/ssl/simple-vmcontrol.crt
    cat /etc/ssl/simple-vmcontrol.crt /etc/ssl/simple-vmcontrol.key > /etc/ssl/simple-vmcontrol.pem
    chown simple-vmcontrol_svc:simple-vmcontrol_svc /etc/ssl/simple-vmcontrol.*
    chmod 600 /etc/ssl/simple-vmcontrol.*

    # Create the Systemd service:
    cp /usr/lib/simple-vmcontrol/simple-vmcontrol.service /etc/systemd/system/simple-vmcontrol.service
    systemctl daemon-reload
    systemctl enable simple-vmcontrol
    systemctl stop simple-vmcontrol
    systemctl start simple-vmcontrol
    systemctl status simple-vmcontrol
    journalctl --follow --unit simple-vmcontrol


Allow the web server to switch to root to run the control commands by adding the following to /etc/sudoers

    simple-vmcontrol_svc ALL=NOPASSWD: /usr/lib/simple-vmcontrol/sudo-scripts/listvm.py
    simple-vmcontrol_svc ALL=NOPASSWD: /usr/lib/simple-vmcontrol/sudo-scripts/createvm.py
    simple-vmcontrol_svc ALL=NOPASSWD: /usr/lib/simple-vmcontrol/sudo-scripts/deletevm.py
    simple-vmcontrol_svc ALL=NOPASSWD: /usr/lib/simple-vmcontrol/sudo-scripts/mountiso.py
    simple-vmcontrol_svc ALL=NOPASSWD: /usr/lib/simple-vmcontrol/sudo-scripts/startvm.py
    simple-vmcontrol_svc ALL=NOPASSWD: /usr/lib/simple-vmcontrol/sudo-scripts/stopvm.py
    simple-vmcontrol_svc ALL=NOPASSWD: /usr/lib/simple-vmcontrol/sudo-scripts/createdatadisk.py
    simple-vmcontrol_svc ALL=NOPASSWD: /usr/lib/simple-vmcontrol/sudo-scripts/deletedatadisk.py
    simple-vmcontrol_svc ALL=NOPASSWD: /usr/lib/simple-vmcontrol/sudo-scripts/setautostart.py
    simple-vmcontrol_svc ALL=NOPASSWD: /usr/lib/simple-vmcontrol/sudo-scripts/shutdownvm.py


### KVM and Libvirt setup

Install KVM and Libvirt:

    apt-get install qemu-kvm virtinst bridge-utils libvirt-clients libvirt-daemon-system qemu-utils --no-install-recommends

Find the name of your ethernet interface from the existing config file (for example enp1s0f0):

    cat /etc/netplan/50-cloud-init.yaml

Write a new config file with a bridge configuration in (use your relevant ethernet interface name in place of enp1s0f0, and your IP settings). Create /etc/netplan/60-br0.yaml

    network:
      version: 2
      ethernets:
        enp1s0f0:
          dhcp4: false
      bridges:
        br0:
          dhcp4: false
          interfaces:
            - enp1s0f0
          addresses: [ 10.160.1.21/16 ]
          gateway4: 10.160.0.1
          interfaces: [enp1s0f0]
          nameservers:
            addresses: [8.8.8.8, 8.8.4.4]

Apply the network config:

    rm /etc/netplan/50-cloud-init.yaml
    echo "network: {config: disabled}" > /etc/cloud/cloud.cfg.d/99-disable-network-config.cfg
    netplan --debug generate
    netplan --debug apply

Set up libvirt to use this bridge (use whatever uuid it generated for you):

    virsh net-edit default
        <network>
          <uuid>391a0f4c-a39a-40d4-bf9a-d158c1ff520d</uuid>
          <name>default</name>
          <forward mode='bridge'/>
          <bridge name='br0'/>
        </network>
    virsh net-destroy default
    virsh net-start default
    virsh net-autostart default
    virsh net-list

Create folder for VM disk images and relocated folder containing save states:

    mkdir /srv/iso
    cd /srv/iso
    wget https://fedorapeople.org/groups/virt/virtio-win/direct-downloads/stable-virtio/virtio-win.iso
    mkdir /srv/vm
    mv /var/lib/libvirt/ /srv/libvirt ; ln -s /srv/libvirt /var/lib/libvirt

Modify /etc/init.d/libvirt-guests

    ON_BOOT=start
    ON_SHUTDOWN=suspend


License
-------

Simple VM Control UI is licensed under the [MIT license.](https://github.com/allanrbo/simple-vmcontrol/blob/master/LICENSE.txt)
