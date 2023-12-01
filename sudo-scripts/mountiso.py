#!/usr/bin/python3

from subprocess import Popen, PIPE
import json
import os
import re
import sys
import xml.etree.ElementTree as ET

config = {}
def reload_config():
    global config
    config = json.loads(open("/usr/lib/simple-vmcontrol/config.json", "r").read())
reload_config()

vmname = sys.argv[1]
if re.search('[^\w]', vmname):
    raise Exception('Name can only be alphanumeric chars')

iso = sys.argv[2]
if iso != '' and not os.path.isfile(config["isolocation"] + iso):
    raise Exception('ISO not found')

# Determine cdrom device name
configdir = '/etc/libvirt/qemu/'
cdromdev = ''
configXml = ET.parse(configdir + vmname + '.xml')
disks = configXml.findall('./devices/disk')
for disk in disks:
    if disk.attrib['device'] == 'cdrom':
        cdromdev = disk.find('./target').attrib['dev']
if cdromdev == '':
    raise Exception('cdrom device not found')

# Always eject existing ISO if there is any
p = Popen(['/usr/bin/virsh', 'change-media', vmname, cdromdev, '--eject', '--force'], stdin=PIPE, stdout=PIPE, stderr=PIPE)
p.communicate()
p = Popen(['/usr/bin/virsh', 'change-media', vmname, cdromdev, '--eject', '--config'], stdin=PIPE, stdout=PIPE, stderr=PIPE)
p.communicate()

r = b''
if iso != '':
    # Determine if VM is running
    p = Popen(['/usr/bin/virsh', 'list'], stdin=PIPE, stdout=PIPE, stderr=PIPE)
    r2 = p.communicate()[0].decode('utf-8')
    m = re.search(vmname +' +running', r2)
    running = m != None

    if running:
        p = Popen(['/usr/bin/virsh', 'attach-disk', vmname, config["isolocation"] + iso, cdromdev, '--type', 'cdrom'],
            stdin=PIPE, stdout=PIPE, stderr=PIPE)
        r += b'\n'.join(p.communicate())
    else:
        # If VM was not running, the ISO file would not be persisted unless the cdrom dev was recreated. Perhaps a bug in virsh.
        p = Popen(['/usr/bin/virsh', 'detach-disk', vmname, cdromdev, '--config'],
            stdin=PIPE, stdout=PIPE, stderr=PIPE)
        r += b'\n'.join(p.communicate())

        p = Popen(['/usr/bin/virsh', 'attach-disk', vmname, config["isolocation"] + iso, cdromdev, '--type', 'cdrom', '--config'],
            stdin=PIPE, stdout=PIPE, stderr=PIPE)
        r += b'\n'.join(p.communicate())

print(r.decode('utf-8'))
