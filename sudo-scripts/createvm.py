#!/usr/bin/env python

from subprocess import Popen, PIPE
import json
import os
import os.path
import re
import sys

config = {}
def reload_config():
    global config
    config = json.loads(open("/usr/lib/simple-vmcontrol/config.json", "r").read())
reload_config()


vmname = sys.argv[1]
if re.search('[^\w]', vmname):
    raise Exception('Name can only be alphanumeric chars')

cores = str(int(sys.argv[2]))

memory = str(int(sys.argv[3]))

osdisksize = str(int(sys.argv[4]))

installiso = sys.argv[5]
if not os.path.isfile(config['isolocation'] + installiso):
    raise Exception('Install ISO not found')


# Create the OS disk image
p = Popen([
    '/usr/bin/qemu-img',
    'create',
    '-f', 'qcow2',
    config['vmimagelocation'] + vmname + '.os.img',
    osdisksize + 'G'
    ], stdin=PIPE, stdout=PIPE, stderr=PIPE)
r = '\n'.join(p.communicate())

# Create the VM
p = Popen([
    '/usr/bin/virt-install',
    '-n', vmname,
    '-r', memory,
    '--vcpus=sockets=1,cores=' + cores,
    '--disk', 'path=' + config['vmimagelocation'] + vmname + '.os.img,format=qcow2,bus=virtio,cache=writeback',
    '-c', config['isolocation'] + installiso,
    '--boot=cdrom,hd',
    '--accelerate',
    '--bridge=br0',
    '--connect=qemu:///system',
    '--video=vga',
    '--vnc',
    '--noautoconsole',
    '-v'
    ], stdin=PIPE, stdout=PIPE, stderr=PIPE)
r += '\n'.join(p.communicate())

print r
