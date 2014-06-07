#!/usr/bin/env python

from subprocess import Popen, PIPE
import os
import re
import sys

isolocation = '/srv/iso/'

vmname = sys.argv[1]
if re.search('[^\w]', vmname):
    raise Exception('Name can only be alphanumeric chars')

iso = sys.argv[2]
if iso != '' and not os.path.isfile(isolocation + iso):
    raise Exception('ISO not found')

# Always eject existing ISO if there is any
p = Popen(['/usr/bin/virsh', 'change-media', vmname, 'hdc', '--eject', '--config'], stdin=PIPE, stdout=PIPE, stderr=PIPE)
r = '\n'.join(p.communicate())

if iso != '':
    # Determine if VM is running
    p = Popen(['/usr/bin/virsh', 'list'], stdin=PIPE, stdout=PIPE, stderr=PIPE)
    r2 = p.communicate()[0]
    m = re.search(vmname +' +running', r2)
    running = m != None

    if running:
        p = Popen(['/usr/bin/virsh', 'attach-disk', vmname, isolocation + iso, 'hdc', '--type', 'cdrom'],
            stdin=PIPE, stdout=PIPE, stderr=PIPE)
        r += '\n'.join(p.communicate())
    else:
        # If VM was not running, the ISO file would not be persisted unless hdc was recreated. Perhaps a bug in virsh.
        p = Popen(['/usr/bin/virsh', 'detach-disk', vmname, 'hdc', '--config'],
            stdin=PIPE, stdout=PIPE, stderr=PIPE)
        r += '\n'.join(p.communicate())

        p = Popen(['/usr/bin/virsh', 'attach-disk', vmname, isolocation + iso, 'hdc', '--type', 'cdrom', '--config'],
            stdin=PIPE, stdout=PIPE, stderr=PIPE)
        r += '\n'.join(p.communicate())

print r
