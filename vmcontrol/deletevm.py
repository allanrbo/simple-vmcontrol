#!/usr/bin/env python

from subprocess import Popen, PIPE
import json
import os
import re
import sys

config = json.loads(open(os.path.dirname(os.path.abspath(__file__)) + '/../config.json', 'r').read())

vmimagelocation = '/srv/vm/'

datadisklocation = '/srv/vm/'
if 'datadisklocation' in config:
    datadisklocation = config['datadisklocation']

vmname = sys.argv[1]
if re.search('[^\w]', vmname):
    raise Exception('Name can only be alphanumeric chars')


# Stop the VM
p = Popen(['/usr/bin/virsh', 'destroy', vmname], stdin=PIPE, stdout=PIPE, stderr=PIPE)
r = '\n'.join(p.communicate())

# Delete the VM
p = Popen(['/usr/bin/virsh', 'undefine', vmname], stdin=PIPE, stdout=PIPE, stderr=PIPE)
r += '\n'.join(p.communicate())

# Delete OS disk image
os.remove(vmimagelocation + vmname + '.os.img')

# Delete data disk images
for filename in os.listdir(datadisklocation):
    if re.search(vmname +'.data\d+.img', filename):
        os.remove(datadisklocation + filename)

print r
