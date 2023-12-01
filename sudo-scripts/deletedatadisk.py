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

datadiskfilename = sys.argv[2]
if not re.search(config['datadisklocation'] + vmname + '.data\d+\.img', datadiskfilename):
    raise Exception('Invalid data disk file name specified:' + datadiskfilename)


# Find the device name for this data disk image file name
p = Popen(['/usr/bin/virsh', 'domblklist', vmname], stdin=PIPE, stdout=PIPE, stderr=PIPE)
r2 = p.communicate()[0].decode("utf-8")
m  = re.search('^ *(\w+) +' + datadiskfilename, r2, re.MULTILINE)
devname = m.group(1)

# Detach the disk image
p = Popen(['/usr/bin/virsh', 'detach-disk', vmname, devname, '--config'],
    stdin=PIPE, stdout=PIPE, stderr=PIPE)
r = b'\n'.join(p.communicate())

os.remove(datadiskfilename)

r += b'\nNote: Disk will first disappear fully on VM restart\n'

print(r.decode('utf-8'))
