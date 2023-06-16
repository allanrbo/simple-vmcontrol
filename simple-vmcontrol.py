#!/usr/bin/python3

from subprocess import Popen, PIPE
from urllib.parse import parse_qs
import base64
import binascii
import hashlib
import html
import http.server
import json
import os
import re
import socketserver
import ssl
import sys

config = {}
def reload_config():
    global config
    config = json.loads(open("/usr/lib/simple-vmcontrol/config.json", "r").read())
reload_config()

def runcmd(cmd):
    p = Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE)
    return '\n'.join((s.decode("utf-8") for s in p.communicate()))

class MyHandler(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        reload_config()

        content_len = int(self.headers.get('Content-Length'))
        post_body = self.rfile.read(content_len)
        form_vals = parse_qs(post_body)

        def form(key):
            k = key.encode("utf-8")
            if k not in form_vals:
                return None
            return form_vals[k][0].decode("utf-8")

        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

        message = None
        valid = True

        if form('create'):
            vmname = form('vmname')
            if not vmname or re.search(r'[^\w]', vmname):
                message = 'Name can only be alphanumeric chars'
                valid = False

            cores = form('cores')
            if not cores or re.search(r'[^0-9]', cores):
                message = 'Cores can only be numeric'
                valid = False

            memory = form('memory')
            if not memory or re.search(r'[^0-9]', memory):
                message = 'Memory can only be numeric'
                valid = False

            osdisksize = form('osdisksize')
            if not osdisksize or re.search(r'[^0-9]', osdisksize):
                message = 'OS disk size can only be numeric'
                valid = False

            installiso = form('installiso')
            isos = os.listdir(config['isolocation'])
            if not installiso or installiso not in isos:
                message = 'Invalid OS installer ISO'
                valid = False

            if valid:
                cmd = [
                    '/usr/bin/sudo',
                    '/usr/lib/simple-vmcontrol/sudo-scripts/createvm.py',
                    vmname,
                    cores,
                    memory,
                    osdisksize,
                    installiso,
                ]
                r = runcmd(cmd)
                message = '<i>Command output from creating VM ' + vmname + ':\n<pre>' + html.escape(r).strip() + '</pre></i>'

        elif form('shutdown'):
            vmname = form('shutdown')
            if not vmname or re.search(r'[^\w]', vmname):
                message = 'Name can only be alphanumeric chars'
                valid = False

            if valid:
                cmd = ['/usr/bin/sudo', '/usr/lib/simple-vmcontrol/sudo-scripts/shutdownvm.py', vmname]
                r = runcmd(cmd)
                message = '<i>Command output from shutdown of VM ' + vmname + ':\n<pre>' + html.escape(r).strip() + '</pre></i>'

        elif form('stop'):
            vmname = form('stop')
            if not vmname or re.search(r'[^\w]', vmname):
                message = 'Name can only be alphanumeric chars'
                valid = False

            if valid:
                cmd = [
                    '/usr/bin/sudo',
                    '/usr/lib/simple-vmcontrol/sudo-scripts/stopvm.py',
                    vmname,
                ]
                r = runcmd(cmd)
                message = '<i>Command output from stopping VM ' + vmname + ' ("destroy" means stop in this case):\n<pre>' + html.escape(r).strip() + '</pre></i>'

        elif form('start'):
            vmname = form('start')
            if not vmname or re.search(r'[^\w]', vmname):
                message = 'Name can only be alphanumeric chars'
                valid = False

            if valid:
                cmd = ['/usr/bin/sudo', '/usr/lib/simple-vmcontrol/sudo-scripts/startvm.py', vmname]
                r = runcmd(cmd)
                message = '<i>Command output from starting VM ' + vmname + ':\n<pre>' + html.escape(r).strip() + '</pre></i>'

        elif form('autostarton'):
            vmname = form('autostarton')
            if not vmname or re.search(r'[^\w]', vmname):
                message = 'Name can only be alphanumeric chars'
                valid = False

            if valid:
                cmd = ['/usr/bin/sudo', '/usr/lib/simple-vmcontrol/sudo-scripts/setautostart.py', vmname, 'True']
                r = runcmd(cmd)
                message = '<i>Command output from enabling autostart for VM ' + vmname + ':\n<pre>' + html.escape(r).strip() + '</pre></i>'

        elif form('autostartoff'):
            vmname = form('autostartoff')
            if not vmname or re.search(r'[^\w]', vmname):
                message = 'Name can only be alphanumeric chars'
                valid = False

            if valid:
                cmd = ['/usr/bin/sudo', '/usr/lib/simple-vmcontrol/sudo-scripts/setautostart.py', vmname, 'False']
                r = runcmd(cmd)
                message = '<i>Command output from disabling autostart for VM ' + vmname + ':\n<pre>' + html.escape(r).strip() + '</pre></i>'

        elif form('delete'):
            deletionconfirmed = form('deletionconfirmed')
            if deletionconfirmed != 'true':
                valid = False

            vmname = form('delete')
            if not vmname or re.search(r'[^\w]', vmname):
                message = 'Name can only be alphanumeric chars'
                valid = False

            if valid:
                cmd = ['/usr/bin/sudo', '/usr/lib/simple-vmcontrol/sudo-scripts/deletevm.py', vmname]
                r = runcmd(cmd)
                message = '<i>Command output from deleting VM ' + vmname + ':\n<pre>' + html.escape(r).strip() + '</pre></i>'

        elif form('changeiso'):
            vmname = form('changeiso')
            if not vmname or re.search(r'[^\w]', vmname):
                message = 'Name can only be alphanumeric chars'
                valid = False

            iso = form('mount_iso_' + vmname)
            if iso == None:
                iso = ''
            isos = os.listdir(config['isolocation'])
            if iso != '' and iso not in isos:
                message = 'Invalid ISO'
                valid = False

            if valid:
                cmd = ['/usr/bin/sudo', '/usr/lib/simple-vmcontrol/sudo-scripts/mountiso.py', vmname, iso]
                r = runcmd(cmd)
                message = '<i>Command output from mounting ISO to VM ' + vmname + ':\n<pre>' + html.escape(r).strip() + '</pre></i>'

        elif form('createdatadisk'):
            vmname = form('createdatadisk')
            if not vmname or re.search(r'[^\w]', vmname):
                message = 'Name can only be alphanumeric chars'
                valid = False

            datadisksize = form('datadisk_size_' + vmname)
            if not datadisksize or re.search(r'[^0-9]', datadisksize):
                message = 'Data disk size can only be numeric'
                valid = False

            if valid:
                cmd = ['/usr/bin/sudo', '/usr/lib/simple-vmcontrol/sudo-scripts/createdatadisk.py', vmname, datadisksize]
                r = runcmd(cmd)
                message = '<i>Command output from creating data disk for VM ' + vmname + ':\n<pre>' + html.escape(r).strip() + '</pre></i>'


        elif form('deletedatadisk'):
            deletionconfirmed = form('deletionconfirmed')
            if deletionconfirmed != 'true':
                valid = False

            vmname, datadiskfilename = form('deletedatadisk').split(',')

            if not vmname or re.search(r'[^\w]', vmname):
                message = 'Name can only be alphanumeric chars'
                valid = False

            if not re.search(config['datadisklocation'] + vmname + '.data\d+.img', datadiskfilename):
                message = 'Invalid data disk name'
                valid = False

            if valid:
                cmd = ['/usr/bin/sudo', '/usr/lib/simple-vmcontrol/sudo-scripts/deletedatadisk.py', vmname, datadiskfilename]
                r = runcmd(cmd)
                message = '<i>Command output from deleting data disk ' + datadiskfilename + ' from VM ' + vmname + ':\n<pre>' + html.escape(r).strip() + '</pre></i>'

        self.render(message)

    def do_GET(self):
        reload_config()
        
        if not self.check_authenticated():
            return

        path = self.path.split("?")[0];
        if path == "/":
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.render(None)
        else:
            self.send_response(404)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(b"not found")

    def check_authenticated(self):
        def send_auth_response_header():
            self.send_response(401)
            self.send_header("WWW-Authenticate", 'Basic realm="Authentication Required"')
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(b"authentication required")

        auth_header = self.headers.get('Authorization')
        if auth_header == None:
            send_auth_response_header()
            return False

        auth_header_split = auth_header.split(" ")
        if len(auth_header_split) != 2 or auth_header_split[0] != "Basic":
            send_auth_response_header()
            return False

        decoded = None
        try:
            decoded = base64.b64decode(auth_header_split[1]).decode("utf-8")
        except:
            send_auth_response_header()
            return False

        decoded_split = decoded.split(":")
        if len(decoded_split) != 2:
            send_auth_response_header()
            return False

        username, password = decoded_split

        if username not in config["users"]:
            send_auth_response_header()
            return False

        stored = config["users"][username]
        stored_bytes = None
        try:
            stored_bytes = binascii.unhexlify(stored)
        except:
            send_auth_response_header()
            return False

        if len(stored_bytes) <= 32:
            send_auth_response_header()
            return False

        salt = stored_bytes[-32:]
        stored_key = stored_bytes[:-32]
        computed_key = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100000)

        if stored_key != computed_key:
            send_auth_response_header()
            return False

        return True

    def render(self, message):
        cmd = ['/usr/bin/sudo', '/usr/lib/simple-vmcontrol/sudo-scripts/listvm.py']
        r = runcmd(cmd)
        vms = json.loads(r)

        def w(s):
            self.wfile.write(s.encode("UTF-8"))
            self.wfile.write(b"\n")

        w('<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"')
        w('   "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">')
        w('<html xmlns="http://www.w3.org/1999/xhtml" lang="en-US">')
        w('<head>')
        w('<meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />')
        w('<title>Simple VM Control UI</title>')
        w('<style type="text/css">')
        w('body { font-family: sans-serif; }')
        w('th { text-align: left; }')
        w('.vmlist td, .vmlist th { padding: 1px 4px; }')
        w('.vmlist th { background-color: #f09911; }')
        w('.vmlist td { background-color: #eeeeee; }')
        w('.blkdevlist td { border-top: 1px solid #656565; }')
        w('</style>')
        w('</head>')
        w('')
        w('<body>')
        w('')

        if message:
            w('<p><em>' + message + '</em></p>')

        w('<h2>Current VMs</h2>')
        w('<form method="get" action=""><p><button type="submit">Refresh</button></p></form>')
        w('<form method="post" action="">')
        w('<input type="hidden" id="deletionconfirmed" name="deletionconfirmed" value="false" />')
        w('<table class="vmlist"><tr><th>Name</th><th>Memory</th><th>Cores</th><th>State</th><th>Auto start</th><th>Console VNC</th><th>Control</th><th>Current mounts</th><th>Create data disk</th><th>Network</th></tr>\n')
        for vm in vms.values():
            w('<tr>')
            w('<td>' + vm['vmname'] + '</td>')
            w('<td>' + str(vm['memory']) + ' MB</td>')
            w('<td>' + str(vm['cores']) + '</td>')
            w('<td>' + vm['state'] + '</td>')
            w('<td>' + str(vm['autostart']) + '</td>')
            w('<td>' + ('localhost:' + vm['vncport'] if vm['vncport'] else '') + '</td>')
            w('<td>')
            w('<button type="submit" name="start" value="' + vm['vmname'] + '">Start</button><br/>')
            w('<button type="submit" name="shutdown" value="' + vm['vmname'] + '" onclick="return confirm(\'Are you sure you want to shut down ' + vm['vmname'] + '?\')">Shutdown</button><br/>')
            w('<button type="submit" name="stop" value="' + vm['vmname'] + '" onclick="return confirm(\'Are you sure you want to stop ' + vm['vmname'] + '?\')">Stop</button><br/>')
            w('<button type="submit" name="delete" value="' + vm['vmname'] + '" onclick="')
            w('    var r = prompt(\'Type ' + vm['vmname'] + ' below to confirm that you really want to delete this VM and all its data disks.\');')
            w('    if(r == \'' + vm['vmname'] + '\') {')
            w('        document.getElementById(\'deletionconfirmed\').value = \'true\';')
            w('        return true;')
            w('     };')
            w('     return false;')
            w('">Delete</button><br/>')
            w('<button type="submit" name="autostarton" value="' + vm['vmname'] + '">Autostart on</button><br/>')
            w('<button type="submit" name="autostartoff" value="' + vm['vmname'] + '">Autostart off</button><br/>')
            w('</td>')

            w('<td>')
            w('<table class="blkdevlist"><tr><th>Dev</th><th>File</th><th>Current</th><th>Max</th><th>Control</th></tr>')
            for mount in vm['mounts']:
                currentsize = mount['currentsize'] + ' GB' if mount['currentsize'] else ''
                maxsize = mount['maxsize'] + ' GB' if mount['maxsize'] else ''
                w('<tr>')
                w('<td>' + mount['dev'] + '</td>')
                w('<td>' + mount['file'] + '</td>')
                w('<td>' + currentsize + '</td>')
                w('<td>' + maxsize + '</td>')

                w('<td>')
                if re.search(config['datadisklocation'] + vm['vmname'] + '.data\d+.img', mount['file']) and os.path.isfile(mount['file']):
                    w('<button type="submit" name="deletedatadisk" value="' + vm['vmname'] + ',' + mount['file'] + '" onclick="')
                    w('    var r = prompt(\'Type ' + vm['vmname'] + ' below to confirm that you really want to delete the data disk ' + mount['file'] +'.\');')
                    w('    if(r == \'' + vm['vmname'] + '\') {')
                    w('        document.getElementById(\'deletionconfirmed\').value = \'true\';')
                    w('        return true;')
                    w('     };')
                    w('     return false;')
                    w('">Delete</button>')
                w('</td>')

                w('</tr>')

            w('</table>')
            w('<br/>')
            w('<select name="mount_iso_' + vm['vmname'] + '">')
            w('<option value="">Eject</option>')
            isos = os.listdir(config['isolocation'])
            for iso in isos:
                w('<option value="' + iso + '">' + iso + '</option>')
            w('</select><br/>')
            w('<button type="submit" name="changeiso" value="' + vm['vmname'] + '">Change ISO</button>')
            w('</td>')

            w('<td>')
            w('Grow to max <input name="datadisk_size_' + vm['vmname'] + '" size="3"/> GB<br/>')
            w('<button type="submit" name="createdatadisk" value="' + vm['vmname'] + '">Create</button>')
            w('</td>')

            w('<td>')
            w('<table class="iflist"><tr><th>Iface</th><th>Model</th><th>MAC</th></tr>')
            for iface in vm['interfaces']:
                w('<tr>')
                w('<td>' + iface['iface'] + '</td>')
                w('<td>' + iface['model'] + '</td>')
                w('<td>' + iface['mac'] + '</td>')
                w('</tr>')

            w('</table>')
            w('</td>')

            w('</tr>')
        w('</table>')
        w('</form>')

        w('<h2>Create new VM</h2>')
        w('<form method="post" action="">')
        w('<table>')
        w('<tr><td>Name</td><td><input type="text" name="vmname"/></td></tr>')
        w('<tr><td>Cores</td><td><input type="text" name="cores" value="2"/></td></tr>')
        w('<tr><td>Memory</td><td><input type="text" name="memory" value="512"/> MB</td></tr>')
        w('<tr><td>OS disk size</td><td><input type="text" name="osdisksize" value="10"/> GB</td></tr>')

        w('<tr>')
        w('<td>OS installer ISO</td>')
        w('<td><select name="installiso">')
        isos = os.listdir(config['isolocation'])
        for iso in isos:
            w('<option value="' + iso + '">' + iso + '</option>')
        w('</select></td>')
        w('</tr>')

        w('<tr><td><button type="submit" name="create" value="create">Create</button></td><td></td></tr>')
        w('</table>')

        w('</form>')
        w('</body>')
        w('</html>')


try:
    server = http.server.HTTPServer(("0.0.0.0", config["port"]), MyHandler)
    server.socket = ssl.wrap_socket(server.socket,
        server_side=True,
        certfile=config["cert_pem_path"],
        ssl_version=ssl.PROTOCOL_TLS)
    print("Started http server")
    server.serve_forever()
except KeyboardInterrupt:
    print("^C received, shutting down server")
    server.socket.close()
