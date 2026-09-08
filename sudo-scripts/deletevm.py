#!/usr/bin/python3

import json
import os
import re
import subprocess
import sys

config = {}
def reload_config():
    global config
    config = json.loads(open("/usr/lib/simple-vmcontrol/config.json", "r").read())
reload_config()

vmname = sys.argv[1]
if re.search(r'[^\w]', vmname):
    raise Exception('Name can only be alphanumeric chars')


# Stop the VM if it is active.
running_vms = subprocess.check_output(['/usr/bin/virsh', 'list', '--name'], text=True)
if vmname in running_vms.splitlines():
    subprocess.run(['/usr/bin/virsh', 'destroy', vmname], check=True)

# Remove the definition before deleting its disks.
subprocess.run(['/usr/bin/virsh', 'undefine', vmname], check=True)

# Delete OS disk image
os.remove(config['vmimagelocation'] + vmname + '.os.img')

# Delete data disk images
for filename in os.listdir(config['datadisklocation']):
    if re.fullmatch(vmname + r'\.data\d+\.img', filename):
        os.remove(config['datadisklocation'] + filename)
