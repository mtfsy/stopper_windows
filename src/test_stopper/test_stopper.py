import unittest
from unittest.mock import patch, MagicMock, mock_open
import os

from stopper import *


class TestCheckReq(unittest.TestCase):
    @patch('os.path.exists')
    def test_exit_on_file_not_found(self, mock_exists):
        """Test that FileNotFoundError return exit program"""
        mock_exists.return_value = False
        
        with self.assertRaises(SystemExit) as cm:
            Task.check_req("missing.txt")
    
        # Optional: Check if it exited with code 1
        self.assertEqual(cm.exception.code, 1)

    # In your test (No @patch needed!)
    def test_check_req(self):
        mock_fs = MagicMock()
        mock_fs.exists.return_value = False
        Task.check_req("test.txt", fs_tool=mock_fs) # Just pass the mock in!
    """
    @patch('subprocess.run')
    @patch('os.name', 'nt')
    def test_kill_program_windows_success(self, mock_run):
        # Setup mock to simulate a successful taskkill
        mock_run.return_value = MagicMock(returncode=0, stdout="SUCCESS")
        
        result = Task.kill_program("notepad.exe")
        
        self.assertIn("SUCCESS", result)
        mock_run.assert_called_with(
            ['taskkill', '/f', '/im', 'notepad.exe'],
            capture_output=True, text=True
        )
    """

if __name__ == '__main__':
    unittest.main()