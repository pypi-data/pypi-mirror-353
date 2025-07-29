import unittest
from unittest.mock import patch
from aira_cli.storage import storage_usage, storage_logs_show_sizes, storage_logs_clean, storage_backup_create, storage_backup_list, storage_backup_restore

class TestStorageCommands(unittest.TestCase):

    @patch('builtins.print')
    def test_storage_usage(self, mock_print):
        args = argparse.Namespace()
        storage_usage(args)
        mock_print.assert_called_with("df -h")

if __name__ == '__main__':
    unittest.main()