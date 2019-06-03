#!/usr/bin/env python

from subprocess import Popen, PIPE
import cgi
import cgitb
import json
import os
import re

config = dict()
if os.path.isfile('/usr/lib/simple-vmcontrol/config.json'):
    config = json.loads(open('/usr/lib/simple-vmcontrol/config.json', 'r').read())

datadisklocation = '/srv/vm/'
if 'datadisklocation' in config:
    datadisklocation = config['datadisklocation']

isolocation = '/srv/iso/'

# CGI troubleshooting
cgitb.enable()

isos = os.listdir(isolocation)

message = None

form = cgi.FieldStorage()


if form.getvalue('create'):
    valid = True

    vmname = form.getvalue('vmname')
    if not vmname or re.search('[^\w]', vmname):
        message = 'Name can only be alphanumeric chars'
        valid = False

    cores = form.getvalue('cores')
    if not cores or re.search('[^0-9]', cores):
        message = 'Cores can only be numeric'
        valid = False

    memory = form.getvalue('memory')
    if not memory or re.search('[^0-9]', memory):
        message = 'Memory can only be numeric'
        valid = False

    osdisksize = form.getvalue('osdisksize')
    if not osdisksize or re.search('[^0-9]', osdisksize):
        message = 'OS disk size can only be numeric'
        valid = False

    installiso = form.getvalue('installiso')
    if not installiso or installiso not in isos:
        message = 'Invalid OS installer ISO'
        valid = False

    if valid:
        p = Popen([
            '/usr/bin/sudo',
            '/usr/lib/simple-vmcontrol/vmcontrol/createvm.py',
            vmname,
            cores,
            memory,
            osdisksize,
            installiso
            ], stdin=PIPE, stdout=PIPE, stderr=PIPE)
        r = '\n'.join(p.communicate())
        message = '<i>Command output from creating VM ' + vmname + ':\n<pre>' + cgi.escape(r).strip() + '</pre></i>'


if form.getvalue('stop'):
    valid = True

    vmname = form.getvalue('stop')
    if not vmname or re.search('[^\w]', vmname):
        message = 'Name can only be alphanumeric chars'
        valid = False

    if valid:
        p = Popen(['/usr/bin/sudo', '/usr/lib/simple-vmcontrol/vmcontrol/stopvm.py', vmname], stdin=PIPE, stdout=PIPE, stderr=PIPE)
        r = '\n'.join(p.communicate())
        message = '<i>Command output from stopping VM ' + vmname + ' ("destroy" means stop in this case):\n<pre>' + cgi.escape(r).strip() + '</pre></i>'


if form.getvalue('start'):
    valid = True

    vmname = form.getvalue('start')
    if not vmname or re.search('[^\w]', vmname):
        message = 'Name can only be alphanumeric chars'
        valid = False

    if valid:
        p = Popen(['/usr/bin/sudo', '/usr/lib/simple-vmcontrol/vmcontrol/startvm.py', vmname], stdin=PIPE, stdout=PIPE, stderr=PIPE)
        r = '\n'.join(p.communicate())
        message = '<i>Command output from starting VM ' + vmname + ':\n<pre>' + cgi.escape(r).strip() + '</pre></i>'


if form.getvalue('autostarton'):
    valid = True

    vmname = form.getvalue('autostarton')
    if not vmname or re.search('[^\w]', vmname):
        message = 'Name can only be alphanumeric chars'
        valid = False

    if valid:
        p = Popen(['/usr/bin/sudo', '/usr/lib/simple-vmcontrol/vmcontrol/setautostart.py', vmname, 'True'], stdin=PIPE, stdout=PIPE, stderr=PIPE)
        r = '\n'.join(p.communicate())
        message = '<i>Command output from enabling autostart for VM ' + vmname + ':\n<pre>' + cgi.escape(r).strip() + '</pre></i>'


if form.getvalue('autostartoff'):
    valid = True

    vmname = form.getvalue('autostartoff')
    if not vmname or re.search('[^\w]', vmname):
        message = 'Name can only be alphanumeric chars'
        valid = False

    if valid:
        p = Popen(['/usr/bin/sudo', '/usr/lib/simple-vmcontrol/vmcontrol/setautostart.py', vmname, 'False'], stdin=PIPE, stdout=PIPE, stderr=PIPE)
        r = '\n'.join(p.communicate())
        message = '<i>Command output from disabling autostart for VM ' + vmname + ':\n<pre>' + cgi.escape(r).strip() + '</pre></i>'


if form.getvalue('start'):
    valid = True

    vmname = form.getvalue('start')
    if not vmname or re.search('[^\w]', vmname):
        message = 'Name can only be alphanumeric chars'
        valid = False

    if valid:
        p = Popen(['/usr/bin/sudo', '/usr/lib/simple-vmcontrol/vmcontrol/startvm.py', vmname], stdin=PIPE, stdout=PIPE, stderr=PIPE)
        r = '\n'.join(p.communicate())
        message = '<i>Command output from starting VM ' + vmname + ':\n<pre>' + cgi.escape(r).strip() + '</pre></i>'


if form.getvalue('delete'):
    valid = True

    deletionconfirmed = form.getvalue('deletionconfirmed')
    if deletionconfirmed != 'true':
        valid = False

    vmname = form.getvalue('delete')
    if not vmname or re.search('[^\w]', vmname):
        message = 'Name can only be alphanumeric chars'
        valid = False

    if valid:
        p = Popen(['/usr/bin/sudo', '/usr/lib/simple-vmcontrol/vmcontrol/deletevm.py', vmname], stdin=PIPE, stdout=PIPE, stderr=PIPE)
        r = '\n'.join(p.communicate())
        message = '<i>Command output from deleting VM ' + vmname + ':\n<pre>' + cgi.escape(r).strip() + '</pre></i>'


if form.getvalue('changeiso'):
    valid = True

    vmname = form.getvalue('changeiso')
    if not vmname or re.search('[^\w]', vmname):
        message = 'Name can only be alphanumeric chars'
        valid = False

    iso = form.getvalue('mount_iso_' + vmname)
    if iso == None:
        iso = ''
    if iso != '' and iso not in isos:
        message = 'Invalid ISO'
        valid = False

    if valid:
        p = Popen(['/usr/bin/sudo', '/usr/lib/simple-vmcontrol/vmcontrol/mountiso.py', vmname, iso], stdin=PIPE, stdout=PIPE, stderr=PIPE)
        r = '\n'.join(p.communicate())
        message = '<i>Command output from mounting ISO to VM ' + vmname + ':\n<pre>' + cgi.escape(r).strip() + '</pre></i>'


if form.getvalue('createdatadisk'):
    valid = True

    vmname = form.getvalue('createdatadisk')
    if not vmname or re.search('[^\w]', vmname):
        message = 'Name can only be alphanumeric chars'
        valid = False

    datadisksize = form.getvalue('datadisk_size_' + vmname)
    if not datadisksize or re.search('[^0-9]', datadisksize):
        message = 'Data disk size can only be numeric'
        valid = False

    if valid:
        p = Popen(['/usr/bin/sudo', '/usr/lib/simple-vmcontrol/vmcontrol/createdatadisk.py', vmname, datadisksize], stdin=PIPE, stdout=PIPE, stderr=PIPE)
        r = '\n'.join(p.communicate())
        message = '<i>Command output from creating data disk for VM ' + vmname + ':\n<pre>' + cgi.escape(r).strip() + '</pre></i>'


if form.getvalue('deletedatadisk'):
    valid = True

    deletionconfirmed = form.getvalue('deletionconfirmed')
    if deletionconfirmed != 'true':
        valid = False

    vmname, datadiskfilename = form.getvalue('deletedatadisk').split(',')

    if not vmname or re.search('[^\w]', vmname):
        message = 'Name can only be alphanumeric chars'
        valid = False

    if not re.search(datadisklocation + vmname + '.data\d+.img', datadiskfilename):
        message = 'Invalid data disk name'
        valid = False

    if valid:
        p = Popen(['/usr/bin/sudo', '/usr/lib/simple-vmcontrol/vmcontrol/deletedatadisk.py', vmname, datadiskfilename], stdin=PIPE, stdout=PIPE, stderr=PIPE)
        r = '\n'.join(p.communicate())
        message = '<i>Command output from deleting data disk ' + datadiskfilename + ' from VM ' + vmname + ':\n<pre>' + cgi.escape(r).strip() + '</pre></i>'



p = Popen(['/usr/bin/sudo', '/usr/lib/simple-vmcontrol/vmcontrol/listvm.py'], stdin=PIPE, stdout=PIPE, stderr=PIPE)
r = p.communicate()[0]
vms = json.loads(r)

print '''Content-type: text/html

<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
   "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" lang="en-US">
<head>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
<title>Simple VM Control UI</title>
<style type="text/css">
body { font-family: sans-serif; }
th { text-align: left; }
.vmlist td, .vmlist th { padding: 1px 4px; }
.vmlist th { background-color: #f09911; }
.vmlist td { background-color: #eeeeee; }
.blkdevlist td { border-top: 1px solid #656565; }
</style>
</head>

<body>

'''

if message:
    print '<p><em>' + message + '</em></p>'

print '<h2>Current VMs</h2>'
print '<form method="get" action=""><p><button type="submit">Refresh</button></p></form>'
print '<form method="post" action="">'
print '<input type="hidden" id="deletionconfirmed" name="deletionconfirmed" value="false" />'
print '<table class="vmlist"><tr><th>Name</th><th>Memory</th><th>Cores</th><th>State</th><th>Auto start</th><th>Console VNC</th><th>Control</th><th>Current mounts</th><th>Create data disk</th><th>Network</th></tr>\n'
for vm in vms.itervalues():
    print '<tr>'
    print '<td>' + vm['vmname'] + '</td>'
    print '<td>' + str(vm['memory']) + ' MB</td>'
    print '<td>' + str(vm['cores']) + '</td>'
    print '<td>' + vm['state'] + '</td>'
    print '<td>' + str(vm['autostart']) + '</td>'
    print '<td>' + ('localhost:' + vm['vncport'] if vm['vncport'] else '') + '</td>'
    print '<td>'
    print '<button type="submit" name="start" value="' + vm['vmname'] + '">Start</button><br/>'
    print '<button type="submit" name="stop" value="' + vm['vmname'] + '" onclick="return confirm(\'Are you sure you want to stop ' + vm['vmname'] + '?\')">Stop</button><br/>'
    print '<button type="submit" name="delete" value="' + vm['vmname'] + '" onclick="'
    print '    var r = prompt(\'Type ' + vm['vmname'] + ' below to confirm that you really want to delete this VM and all its data disks.\');'
    print '    if(r == \'' + vm['vmname'] + '\') {'
    print '        document.getElementById(\'deletionconfirmed\').value = \'true\';'
    print '        return true;'
    print '     };'
    print '     return false;'
    print '">Delete</button><br/>'
    print '<button type="submit" name="autostarton" value="' + vm['vmname'] + '">Autostart on</button><br/>'
    print '<button type="submit" name="autostartoff" value="' + vm['vmname'] + '">Autostart off</button><br/>'
    print '</td>'

    print '<td>'
    print '<table class="blkdevlist"><tr><th>Dev</th><th>File</th><th>Current</th><th>Max</th><th>Control</th></tr>'
    for mount in vm['mounts']:
        currentsize = mount['currentsize'] + ' GB' if mount['currentsize'] else ''
        maxsize = mount['maxsize'] + ' GB' if mount['maxsize'] else ''
        print '<tr>'
        print '<td>' + mount['dev'] + '</td>'
        print '<td>' + mount['file'] + '</td>'
        print '<td>' + currentsize + '</td>'
        print '<td>' + maxsize + '</td>'

        print '<td>'
        if re.search(datadisklocation + vm['vmname'] + '.data\d+.img', mount['file']) and os.path.isfile(mount['file']):
            print '<button type="submit" name="deletedatadisk" value="' + vm['vmname'] + ',' + mount['file'] + '" onclick="'
            print '    var r = prompt(\'Type ' + vm['vmname'] + ' below to confirm that you really want to delete the data disk ' + mount['file'] +'.\');'
            print '    if(r == \'' + vm['vmname'] + '\') {'
            print '        document.getElementById(\'deletionconfirmed\').value = \'true\';'
            print '        return true;'
            print '     };'
            print '     return false;'
            print '">Delete</button>'
        print '</td>'

        print '</tr>'

    print '</table>'
    print '<br/>'
    print '<select name="mount_iso_' + vm['vmname'] + '">'
    print '<option value="">Eject</option>'
    for iso in isos:
        print '<option value="' + iso + '">' + iso + '</option>'
    print '</select><br/>'
    print '<button type="submit" name="changeiso" value="' + vm['vmname'] + '">Change ISO in hdc</button>'
    print '</td>'

    print '<td>'
    print 'Grow to max <input name="datadisk_size_' + vm['vmname'] + '" size="3"/> GB<br/>'
    print '<button type="submit" name="createdatadisk" value="' + vm['vmname'] + '">Create</button>'
    print '</td>'


    print '<td>'
    print '<table class="iflist"><tr><th>Iface</th><th>Model</th><th>MAC</th></tr>'
    for iface in vm['interfaces']:
        print '<tr>'
        print '<td>' + iface['iface'] + '</td>'
        print '<td>' + iface['model'] + '</td>'
        print '<td>' + iface['mac'] + '</td>'
        print '</tr>'

    print '</table>'
    print '</td>'


    print '</tr>'
print '</table>'

print '''
<h2>Create new VM</h2>
<table>
<tr><td>Name</td><td><input type="text" name="vmname"/></td></tr>
<tr><td>Cores</td><td><input type="text" name="cores" value="2"/></td></tr>
<tr><td>Memory</td><td><input type="text" name="memory" value="512"/> MB</td></tr>
<tr><td>OS disk size</td><td><input type="text" name="osdisksize" value="10"/> GB</td></tr>
'''
print '<tr>'
print '<td>OS installer ISO</td>'
print '<td><select name="installiso">'
for iso in isos:
    print '<option value="' + iso + '">' + iso + '</option>'
print '</select></td>'
print '</tr>'

print '''
<tr><td><button type="submit" name="create" value="create">Create</button></td><td></td></tr>
</table>
'''

print '</form>\n</body>\n</html>'
