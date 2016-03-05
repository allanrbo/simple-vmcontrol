#!/usr/bin/env python

from subprocess import Popen, PIPE
import os
import re
import sys

vmimagelocation = '/srv/vm/'

vmname = sys.argv[1]
if re.search('[^\w]', vmname):
    raise Exception('Name can only be alphanumeric chars')

autostartstate = False
if sys.argv[2] == 'True':
    autostartstate = True


command = ['/usr/bin/virsh', 'autostart', vmname]

if not autostartstate:
    command.append('--disable')

p = Popen(command, stdin=PIPE, stdout=PIPE, stderr=PIPE)
r = '\n'.join(p.communicate())
print r
