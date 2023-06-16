#!/usr/bin/env python

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


# Stop the VM
p = Popen(['/usr/bin/virsh', 'destroy', vmname], stdin=PIPE, stdout=PIPE, stderr=PIPE)
r = '\n'.join(p.communicate())

# Delete the VM
p = Popen(['/usr/bin/virsh', 'undefine', vmname], stdin=PIPE, stdout=PIPE, stderr=PIPE)
r += '\n'.join(p.communicate())

# Delete OS disk image
os.remove(config['vmimagelocation'] + vmname + '.os.img')

# Delete data disk images
for filename in os.listdir(config['datadisklocation']):
    if re.search(vmname +'.data\d+.img', filename):
        os.remove(config['datadisklocation'] + filename)

print r
