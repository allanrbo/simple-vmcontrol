#!/usr/bin/python3

from subprocess import Popen, PIPE
import re
import sys

vmname = sys.argv[1]
if re.search('[^\w]', vmname):
    raise Exception('Name can only be alphanumeric chars')

p = Popen(['/usr/bin/virsh', 'destroy', vmname], stdin=PIPE, stdout=PIPE, stderr=PIPE)
r = b'\n'.join(p.communicate())

print(r.decode('utf-8'))
