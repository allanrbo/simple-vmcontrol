import contextlib
import io
import json
import pathlib
import runpy
import unittest
import unittest.mock
import xml.etree.ElementTree


class VMHelperTests(unittest.TestCase):
    def test_list_vm_without_cpu_topology(self):
        #
        # Arrange
        #
        script = pathlib.Path(__file__).resolve().parents[1] / 'sudo-scripts/listvm.py'
        domain = xml.etree.ElementTree.ElementTree(xml.etree.ElementTree.fromstring(
            '<domain><memory>1048576</memory><vcpu>4</vcpu></domain>'
        ))
        output = io.StringIO()
        with \
            unittest.mock.patch('os.listdir', return_value=['testvm.xml']), \
            unittest.mock.patch('os.path.exists', return_value=False), \
            unittest.mock.patch('xml.etree.ElementTree.parse', return_value=domain), \
            unittest.mock.patch('subprocess.Popen') as process, \
            contextlib.redirect_stdout(output):
            process.return_value.communicate.return_value = (b'Header\n-----\n', b'')

            #
            # Act
            #
            runpy.run_path(str(script), run_name='__main__')

        #
        # Assert
        #
        self.assertEqual(json.loads(output.getvalue())['testvm']['cores'], 4)

    def test_create_vm_uses_configured_bridge(self):
        #
        # Arrange
        #
        script = pathlib.Path(__file__).resolve().parents[1] / 'sudo-scripts/createvm.py'
        config = json.dumps({
            'vmimagelocation': '/srv/vm/',
            'isolocation': '/srv/iso/',
            'bridge': 'lan-main',
        })
        with \
            unittest.mock.patch('builtins.open', unittest.mock.mock_open(read_data=config)), \
            unittest.mock.patch('os.path.isfile', return_value=True), \
            unittest.mock.patch('sys.argv', [str(script), 'testvm', '2', '1024', '10', 'debian.iso']), \
            unittest.mock.patch('subprocess.Popen') as process, \
            unittest.mock.patch('subprocess.check_output', return_value=b'--osinfo OSINFO'), \
            contextlib.redirect_stdout(io.StringIO()):
            process.return_value.communicate.return_value = (b'', b'')

            #
            # Act
            #
            runpy.run_path(str(script), run_name='__main__')

        #
        # Assert
        #
        self.assertIn('--bridge=lan-main', process.call_args_list[1].args[0])

    def test_create_vm_defaults_to_br0(self):
        #
        # Arrange
        #
        script = pathlib.Path(__file__).resolve().parents[1] / 'sudo-scripts/createvm.py'
        config = json.dumps({
            'vmimagelocation': '/srv/vm/',
            'isolocation': '/srv/iso/',
        })
        with \
            unittest.mock.patch('builtins.open', unittest.mock.mock_open(read_data=config)), \
            unittest.mock.patch('os.path.isfile', return_value=True), \
            unittest.mock.patch('sys.argv', [str(script), 'testvm', '2', '1024', '10', 'debian.iso']), \
            unittest.mock.patch('subprocess.Popen') as process, \
            unittest.mock.patch('subprocess.check_output', return_value=b'--osinfo OSINFO'), \
            contextlib.redirect_stdout(io.StringIO()):
            process.return_value.communicate.return_value = (b'', b'')

            #
            # Act
            #
            runpy.run_path(str(script), run_name='__main__')

        #
        # Assert
        #
        self.assertIn('--bridge=br0', process.call_args.args[0])

    def test_create_vm_omits_unsupported_osinfo(self):
        #
        # Arrange
        #
        script = pathlib.Path(__file__).resolve().parents[1] / 'sudo-scripts/createvm.py'
        config = json.dumps({
            'vmimagelocation': '/srv/vm/',
            'isolocation': '/srv/iso/',
            'bridge': 'br0',
        })
        with \
            unittest.mock.patch('builtins.open', unittest.mock.mock_open(read_data=config)), \
            unittest.mock.patch('os.path.isfile', return_value=True), \
            unittest.mock.patch('sys.argv', [str(script), 'testvm', '2', '1024', '10', 'debian.iso']), \
            unittest.mock.patch('subprocess.Popen') as process, \
            unittest.mock.patch('subprocess.check_output', return_value=b'--os-variant OS_VARIANT'), \
            contextlib.redirect_stdout(io.StringIO()):
            process.return_value.communicate.return_value = (b'', b'')

            #
            # Act
            #
            runpy.run_path(str(script), run_name='__main__')

        #
        # Assert
        #
        self.assertNotIn('--osinfo', process.call_args.args[0])

    def test_create_vm_includes_supported_osinfo(self):
        #
        # Arrange
        #
        script = pathlib.Path(__file__).resolve().parents[1] / 'sudo-scripts/createvm.py'
        config = json.dumps({
            'vmimagelocation': '/srv/vm/',
            'isolocation': '/srv/iso/',
            'bridge': 'br0',
        })
        with \
            unittest.mock.patch('builtins.open', unittest.mock.mock_open(read_data=config)), \
            unittest.mock.patch('os.path.isfile', return_value=True), \
            unittest.mock.patch('sys.argv', [str(script), 'testvm', '2', '1024', '10', 'debian.iso']), \
            unittest.mock.patch('subprocess.Popen') as process, \
            unittest.mock.patch('subprocess.check_output', return_value=b'--osinfo OSINFO'), \
            contextlib.redirect_stdout(io.StringIO()):
            process.return_value.communicate.return_value = (b'', b'')

            #
            # Act
            #
            runpy.run_path(str(script), run_name='__main__')

        #
        # Assert
        #
        command = process.call_args.args[0]
        self.assertIn('--osinfo', command)
        self.assertEqual(command[command.index('--osinfo') + 1], 'detect=on,require=off')
