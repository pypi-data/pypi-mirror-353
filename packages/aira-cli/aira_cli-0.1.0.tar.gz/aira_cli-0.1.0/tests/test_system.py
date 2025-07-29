import unittest
from unittest.mock import patch, MagicMock
import argparse
from aira_cli.system import system_info, system_status, system_update_check, system_update_apply, system_update_history, system_reboot, system_shutdown, system_healthcheck, system_disk

class TestSystemCommands(unittest.TestCase):

    @patch('builtins.print')
    def test_system_info(self, mock_print):
        args = argparse.Namespace(json=False)
        system_info(args)
        mock_print.assert_called_with("System Information:")
        mock_print.assert_any_call("CPU: Intel i7-9700K")
        mock_print.assert_any_call("RAM: 32GB")
        mock_print.assert_any_call("Disk: 1TB SSD")
        mock_print.assert_any_call("OS: Ubuntu 20.04")
        mock_print.assert_any_call("Kernel: 5.4.0-42-generic")
        mock_print.assert_any_call("Network:")
        mock_print.assert_any_call("  IP: 192.168.1.2")
        mock_print.assert_any_call("  MAC: 00:1A:2B:3C:4D:5E")

    @patch('builtins.print')
    def test_system_status(self, mock_print):
        args = argparse.Namespace(json=False)
        system_status(args)
        mock_print.assert_called_with("Service Status:")
        mock_print.assert_any_call("Docker: running")
        mock_print.assert_any_call("Database: running")
        mock_print.assert_any_call("Web_server: running")

    @patch('builtins.print')
    def test_system_update_check(self, mock_print):
        args = argparse.Namespace()
        system_update_check(args)
        mock_print.assert_called_with("Checking for updates...")
        mock_print.assert_any_call("No updates available.")

    @patch('builtins.input', return_value='y')
    @patch('builtins.print')
    def test_system_update_apply(self, mock_print, mock_input):
        args = argparse.Namespace(force=False)
        system_update_apply(args)
        mock_print.assert_called_with("Applying updates...")
        mock_print.assert_any_call("Updates applied successfully.")

    @patch('builtins.print')
    def test_system_update_history(self, mock_print):
        args = argparse.Namespace(json=False)
        system_update_history(args)
        mock_print.assert_called_with("Update History:")
        mock_print.assert_any_call("Date: 2023-10-01, Status: success")
        mock_print.assert_any_call("Date: 2023-09-15, Status: success")

    @patch('builtins.input', return_value='y')
    @patch('builtins.print')
    def test_system_reboot(self, mock_print, mock_input):
        args = argparse.Namespace(force=False)
        system_reboot(args)
        mock_print.assert_called_with("Rebooting system...")
        mock_print.assert_any_call("System rebooted.")

    @patch('builtins.input', return_value='y')
    @patch('builtins.print')
    def test_system_shutdown(self, mock_print, mock_input):
        args = argparse.Namespace(force=False)
        system_shutdown(args)
        mock_print.assert_called_with("Shutting down system...")
        mock_print.assert_any_call("System shut down.")

    @patch('builtins.print')
    def test_system_healthcheck(self, mock_print):
        args = argparse.Namespace()
        system_healthcheck(args)
        mock_print.assert_called_with("Performing system health check...")
        mock_print.assert_any_call("System health check completed. No issues found.")

    @patch('aira_cli.utils.run_command', return_value="Disk Usage:\nFilesystem      Size  Used Avail Use% Mounted on\n/dev/sda1       100G   50G   50G  50% /\n")
    @patch('builtins.print')
    def test_system_disk(self, mock_print, mock_run_command):
        args = argparse.Namespace()
        system_disk(args)
        mock_print.assert_called_with("Disk Usage:")
        mock_print.assert_any_call("Disk Usage:\nFilesystem      Size  Used Avail Use% Mounted on\n/dev/sda1       100G   50G   50G  50% /\n")

if __name__ == '__main__':
    unittest.main()