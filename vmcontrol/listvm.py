#!/usr/bin/env python

from subprocess import Popen, PIPE
import json
import os
import re
import xml.etree.ElementTree as ET

vms = {}

# Find all VM configs
configdir = '/etc/libvirt/qemu/'
for d in os.listdir(configdir):
    if not d.endswith('.xml'):
        continue

    vm = {}
    vmname = d.replace('.xml', '')
    vm['vmname'] = vmname

    # Set defaults
    vm['state'] = 'Stopped'
    vm['vncport'] = None

    # Read values from config file
    configXml = ET.parse(configdir + d)
    vm['memory'] = int(configXml.find('./memory').text) / 1024
    vm['cores'] = int(configXml.find('./cpu/topology').attrib['cores'])

    # Loop over mounted block devices
    mounts = []
    p = Popen(['/usr/bin/virsh', 'domblklist', vmname], stdin=PIPE, stdout=PIPE, stderr=PIPE)
    r = p.communicate()[0]
    for line in r.strip().splitlines()[2:]:
        m = re.search(r'(\w+) +([^ ]*)', line)
        mount = {}
        mount['dev'] = m.group(1)
        mount['file'] = m.group(2)
        mount['currentsize'] = ''
        mount['maxsize'] = ''

        # If block device is not a CD-ROM drive
        if mount['file'] != '-' and not mount['file'].endswith('.iso') and os.path.isfile(mount['file']):
            # Get actual file on disk
            mount['currentsize'] = str(os.path.getsize(mount['file']) / 1024L / 1024L / 1024L)

            # Use qemu-img to get max size of dynamically expanding images
            p = Popen(['/usr/bin/qemu-img', 'info', mount['file']], stdin=PIPE, stdout=PIPE, stderr=PIPE)
            r = p.communicate()[0]
            m = re.search(r'virtual size: [^\(]+\((\d+)', r)
            if m:
                mount['maxsize'] = str(long(m.group(1))  / 1024L / 1024L / 1024L)
            else:
                mount['maxsize'] = mount['currentsize']

        mounts.append(mount)

    vm['mounts'] = mounts

    vms[vmname] = vm


# Determine which VMs are running
p = Popen(['/usr/bin/virsh', 'list'], stdin=PIPE, stdout=PIPE, stderr=PIPE)
r = p.communicate()[0]
lines = r.strip().split('\n')
for line in lines[2:]:
    m = re.search(r'(\d+) +(\w+) +(\w+)', line)
    vmname = m.group(2)
    vms[vmname]['state'] = m.group(3).title()

    # Determine which port VNC is listening on for this VMs console
    p2 = Popen(['/usr/bin/virsh', 'vncdisplay', vmname], stdin=PIPE, stdout=PIPE, stderr=PIPE)
    r2 = p2.communicate()[0]
    m2 = re.search(r'(\d+)', r2)
    vms[vmname]['vncport'] = str(int(m2.group(1)) + 5900)

print json.dumps(vms)
