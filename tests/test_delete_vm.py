import contextlib
import json
import pathlib
import runpy
import subprocess
import tempfile
import unittest
import unittest.mock


class DeleteVMTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.disks = pathlib.Path(self.directory.name)
        (self.disks / 'testvm.os.img').touch()
        (self.disks / 'testvm.data1.img').touch()
        self.script = pathlib.Path(__file__).resolve().parents[1] / 'sudo-scripts/deletevm.py'
        config = json.dumps({
            'vmimagelocation': str(self.disks) + '/',
            'datadisklocation': str(self.disks) + '/',
        })
        self.patches = contextlib.ExitStack()
        self.addCleanup(self.patches.close)
        self.patches.enter_context(unittest.mock.patch('builtins.open', unittest.mock.mock_open(read_data=config)))
        self.patches.enter_context(unittest.mock.patch('sys.argv', [str(self.script), 'testvm']))
        self.running = self.patches.enter_context(unittest.mock.patch('subprocess.check_output', return_value=''))
        self.run = self.patches.enter_context(unittest.mock.patch('subprocess.run'))

    def test_delete_stopped_vm(self):
        #
        # Arrange
        #
        self.running.return_value = 'another_vm\n'

        #
        # Act
        #
        runpy.run_path(str(self.script), run_name='__main__')

        #
        # Assert
        #
        self.run.assert_called_once_with(['/usr/bin/virsh', 'undefine', 'testvm'], check=True)
        self.assertFalse((self.disks / 'testvm.os.img').exists())
        self.assertFalse((self.disks / 'testvm.data1.img').exists())

    def test_delete_running_vm(self):
        #
        # Arrange
        #
        self.running.return_value = 'testvm\n'

        #
        # Act
        #
        runpy.run_path(str(self.script), run_name='__main__')

        #
        # Assert
        #
        self.assertEqual(self.run.call_args_list, [
            unittest.mock.call(['/usr/bin/virsh', 'destroy', 'testvm'], check=True),
            unittest.mock.call(['/usr/bin/virsh', 'undefine', 'testvm'], check=True),
        ])
        self.assertFalse((self.disks / 'testvm.os.img').exists())

    def test_failed_destroy_preserves_disks_and_definition(self):
        #
        # Arrange
        #
        self.running.return_value = 'testvm\n'
        self.run.side_effect = subprocess.CalledProcessError(1, 'virsh destroy')

        #
        # Act
        #
        with self.assertRaises(subprocess.CalledProcessError):
            runpy.run_path(str(self.script), run_name='__main__')

        #
        # Assert
        #
        self.run.assert_called_once_with(['/usr/bin/virsh', 'destroy', 'testvm'], check=True)
        self.assertTrue((self.disks / 'testvm.os.img').exists())
        self.assertTrue((self.disks / 'testvm.data1.img').exists())

    def test_failed_undefine_preserves_disks(self):
        #
        # Arrange
        #
        self.run.side_effect = subprocess.CalledProcessError(1, 'virsh undefine')

        #
        # Act
        #
        with self.assertRaises(subprocess.CalledProcessError):
            runpy.run_path(str(self.script), run_name='__main__')

        #
        # Assert
        #
        self.assertTrue((self.disks / 'testvm.os.img').exists())
        self.assertTrue((self.disks / 'testvm.data1.img').exists())

    def test_delete_preserves_similarly_named_files(self):
        #
        # Arrange
        #
        (self.disks / 'othertestvm.data1.img').touch()
        (self.disks / 'testvmXdata2Yimg').touch()
        (self.disks / 'testvm.data3.img.backup').touch()

        #
        # Act
        #
        runpy.run_path(str(self.script), run_name='__main__')

        #
        # Assert
        #
        self.assertTrue((self.disks / 'othertestvm.data1.img').exists())
        self.assertTrue((self.disks / 'testvmXdata2Yimg').exists())
        self.assertTrue((self.disks / 'testvm.data3.img.backup').exists())
        self.assertFalse((self.disks / 'testvm.data1.img').exists())
