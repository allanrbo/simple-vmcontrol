#!/usr/bin/env python

from subprocess import Popen, PIPE
import json
import os
import re
import sys

config = json.loads(open(os.path.dirname(os.path.abspath(__file__)) + '/../config.json', 'r').read())

datadisklocation = '/srv/vm/'
if 'datadisklocation' in config:
    datadisklocation = config['datadisklocation']

vmname = sys.argv[1]
if re.search('[^\w]', vmname):
    raise Exception('Name can only be alphanumeric chars')

datadiskfilename = sys.argv[2]
if not re.search(datadisklocation + vmname + '.data\d+\.img', datadiskfilename):
    raise Exception('Invalid data disk file name specified:' + datadiskfilename)


# Find the device name for this data disk image file name
p = Popen(['/usr/bin/virsh', 'domblklist', vmname], stdin=PIPE, stdout=PIPE, stderr=PIPE)
r2 = p.communicate()[0]
m  = re.search('^(\w+) +' + datadiskfilename, r2, re.MULTILINE)
devname = m.group(1)

# Detach the disk image
p = Popen(['/usr/bin/virsh', 'detach-disk', vmname, devname, '--config'],
    stdin=PIPE, stdout=PIPE, stderr=PIPE)
r = '\n'.join(p.communicate())

os.remove(datadiskfilename)

r += '\nNote: Disk will first disappear fully on VM restart\n'

print r
