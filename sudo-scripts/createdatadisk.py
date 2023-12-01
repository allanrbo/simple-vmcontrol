#!/usr/bin/python3

from subprocess import Popen, PIPE
import json
import os
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

datadisksize = str(int(sys.argv[2]))

# Find unique file name
i = 1
while os.path.isfile(config['datadisklocation'] + vmname + '.data' + str(i) + '.img'):
    i = i + 1
filename = config['datadisklocation'] + vmname + '.data' + str(i) + '.img'

# Find unique device name
devnames = [
    'vda','vdb','vdc','vdd','vde','vdf','vdg','vdh','vdi','vdj','vdk', 'vdl',
    'vdm','vdn','vdo','vdp','vdq','vdr','vds','vdt','vdu','vdv','vdw', 'vdx',
    'vdy','vdz'
]
p = Popen(['/usr/bin/virsh', 'domblklist', vmname], stdin=PIPE, stdout=PIPE, stderr=PIPE)
r = p.communicate()[0].decode('utf-8')
i = 0
while re.search('^ *' + devnames[i] +' +', r, re.MULTILINE):
    i = i + 1
devname = devnames[i]

# Create image file
p = Popen([
    '/usr/bin/qemu-img',
    'create',
    '-f', 'qcow2',
    filename,
    datadisksize + 'G'
    ], stdin=PIPE, stdout=PIPE, stderr=PIPE)
r = b'\n'.join(p.communicate())

# Attach image file
p = Popen([
    '/usr/bin/virsh',
    'attach-disk',
    vmname,
    filename,
    devname,
    '--driver', 'qemu',
    '--subdriver', 'qcow2',
    '--cache', 'writeback',
    '--persistent'
    ], stdin=PIPE, stdout=PIPE, stderr=PIPE)
r = b'\n'.join(p.communicate())

print(r.decode('utf-8'))
