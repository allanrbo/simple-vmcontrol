Simple VM Control UI
====================

Very minimal web UI for creating and deleting Libvirt/KVM VMs.

I wrote this quick and dirty system because it seemed the existing web UIs there were for Libvirt/KVM had more dependencies than I wanted to have installed on my VM host. This system is therefore fairly self contained and only dependant on Python and Lighttpd, besides Libvirt and KVM itself of course. No other libraries needed.

As this system was written specifically for a VM host I had, I took the shortcut of hardcoding some paths:
 * VM disk images will be created in /srv/vm/
 * OS installation ISO image files are expected to be in /srv/iso/

![Screenshot](https://github.com/allanrbo/simple-vmcontrol/blob/master/docs/screenshot1.png?raw=true)

Server setup
------------
My VM host is an Ubuntu 18.04 installation.

### Installation
    cd /usr/lib
    git clone https://github.com/allanrbo/simple-vmcontrol.git

    mkdir -p /var/www/html/cgi-bin
    ln -s /usr/lib/simple-vmcontrol/cgi-bin/vmcontrol.py /var/www/html/cgi-bin/vmcontrol.py

Allow the web server to switch to root to run the control commands by adding the following to /etc/sudoers

    www-data ALL=NOPASSWD: /usr/lib/simple-vmcontrol/vmcontrol/listvm.py
    www-data ALL=NOPASSWD: /usr/lib/simple-vmcontrol/vmcontrol/createvm.py
    www-data ALL=NOPASSWD: /usr/lib/simple-vmcontrol/vmcontrol/deletevm.py
    www-data ALL=NOPASSWD: /usr/lib/simple-vmcontrol/vmcontrol/mountiso.py
    www-data ALL=NOPASSWD: /usr/lib/simple-vmcontrol/vmcontrol/startvm.py
    www-data ALL=NOPASSWD: /usr/lib/simple-vmcontrol/vmcontrol/stopvm.py
    www-data ALL=NOPASSWD: /usr/lib/simple-vmcontrol/vmcontrol/createdatadisk.py
    www-data ALL=NOPASSWD: /usr/lib/simple-vmcontrol/vmcontrol/deletedatadisk.py
    www-data ALL=NOPASSWD: /usr/lib/simple-vmcontrol/vmcontrol/setautostart.py
    www-data ALL=NOPASSWD: /usr/lib/simple-vmcontrol/vmcontrol/shutdownvm.py

### Web server setup

Installed lighttpd:

    apt-get install lighttpd python
    rm /var/www/html/index.lighttpd.html
    lighttpd-enable-mod cgi
    lighttpd-enable-mod ssl
    lighttpd-enable-mod auth
    cd /etc/lighttpd/
    openssl req -x509 -nodes -newkey rsa:2048 -keyout server.pem -out server.pem -days 3650 -subj "/CN=server" -sha256
    chmod 400 server.pem

Configured lighttpd by adding a file /etc/lighttpd/conf-enabled/myserver.conf

    # Only allow https on vmcontrol.py
    $HTTP["scheme"] == "http" {
        $HTTP["url"] =~ "^/cgi-bin/vmcontrol.py" {
             url.access-deny = ("")
        }
    }

    # Require login for vmcontrol.pyn
    $HTTP["url"] =~ "^/cgi-bin/vmcontrol.py" {
        auth.backend = "htpasswd"
        auth.backend.htpasswd.userfile = "/etc/lighttpd/htpasswd"
        auth.require = ( "" => (
            "method"  => "basic",
            "realm"   => "",
            "require" => "valid-user"
        ))
    }

Created the file /etc/lighttpd/htpasswd with credentials I wanted to use (for example use http://aspirine.org/htpasswd_en.html ).

Restarted Lighttpd for changes to take effect:

    /etc/init.d/lighttpd restart

### KVM and Libvirt setup

Installed KVM and Libvirt:

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

Applied the network config:

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

Created folder for VM disk images and relocated folder containing save states:

    mkdir /srv/iso
    cd /srv/iso
    wget https://fedorapeople.org/groups/virt/virtio-win/direct-downloads/stable-virtio/virtio-win.iso
    mkdir /srv/vm
    mv /var/lib/libvirt/ /srv/libvirt ; ln -s /srv/libvirt /var/lib/libvirt

Modified /etc/init.d/libvirt-guests

    ON_BOOT=start
    ON_SHUTDOWN=suspend


License
-------

Simple VM Control UI is licensed under the [MIT license.](https://github.com/allanrbo/simple-vmcontrol/blob/master/LICENSE.txt)
