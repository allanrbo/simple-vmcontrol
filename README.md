Simple VM Control UI
====================

Very minimal web UI for creating and deleting Libvirt/KVM VMs.

I wrote this quick and dirty system because it seemed the existing web UIs there were for Libvirt/KVM had more dependencies than I wanted to have installed on my VM host. This system is therefore fairly self contained and only dependant on Python and Lighttpd, besides Libvirt and KVM itself of course. No other libraries needed.

As this system was written specifically for a VM host I had, I took the shortcut of hardcoding some paths:
 * VM disk images will be created in /srv/vm/
 * OS installation ISO image files are expected to be in /srv/iso/
 * The scripts in the vmcontrol folder are expected to be in /root/vmcontrol

![Screenshot](https://github.com/allanrbo/simple-vmcontrol/blob/master/docs/screenshot1.png?raw=true)

Server set up
-------------
My VM host is a basic Debian 7 installation.

### Script installation
 * Put cgi-bin/vmcontrol.py in /var/www/cgi-bin/
 * Put vmcontrol/* in /root/vmcontrol/

Allow the web server to switch to root to run the control commands by adding the following to /etc/sudoers

    www-data ALL=NOPASSWD: /root/vmcontrol/listvm.py
    www-data ALL=NOPASSWD: /root/vmcontrol/createvm.py
    www-data ALL=NOPASSWD: /root/vmcontrol/deletevm.py
    www-data ALL=NOPASSWD: /root/vmcontrol/mountiso.py
    www-data ALL=NOPASSWD: /root/vmcontrol/startvm.py
    www-data ALL=NOPASSWD: /root/vmcontrol/stopvm.py
    www-data ALL=NOPASSWD: /root/vmcontrol/createdatadisk.py
    www-data ALL=NOPASSWD: /root/vmcontrol/deletedatadisk.py

### Web server setup

Installed lighttpd:

    apt-get install lighttpd
    lighttpd-enable-mod cgi
    lighttpd-enable-mod ssl
    lighttpd-enable-mod auth
    cd /etc/lighttpd/
    openssl req -new -x509 -keyout server.pem -out server.pem -days 3650 -nodes
    chmod 400 server.pem

Configured lighttpd by adding a file /etc/lighttpd/conf-enabled/myserver.conf:

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

Created the file /etc/lighttpd/htpasswd with credentials I wanted to use (used htpasswd to create the file on a different computer which had Apache installed).

Restarted Lighttpd for changes to take effect:
    /etc/init.d/lighttpd restart

### KVM and Libvirt setup

Installed KVM and Libvirt:

    aptitude install qemu-kvm libvirt-bin
    apt-get install virtinst
    apt-get install bridge-utils

Modified /etc/network/interfaces

    allow-hotplug eth0
    iface eth0 inet manual

    auto br0
    iface br0 inet dhcp
            bridge_ports eth0

Created folder for VM disk images and relocated folder containing save states:

    mkdir /srv/vm
    mv /var/lib/libvirt/ /srv/libvirt ; ln -s /srv/libvirt /var/lib/libvirt

Modified /etc/init.d/libvirt-guests

    ON_BOOT=start
    ON_SHUTDOWN=suspend


License
-------

Simple VM Control UI is licensed under the [MIT license.](https://github.com/allanrbo/simple-vmcontrol/blob/master/LICENSE.txt)
