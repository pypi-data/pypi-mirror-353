import unittest
from unittest.mock import patch
from aira_cli.setup import setup_pre_check, setup_apply_deps, setup_install_aira

class TestSetupCommands(unittest.TestCase):

    @patch('builtins.print')
    def test_setup_pre_check(self, mock_print):
        args = argparse.Namespace()
        setup_pre_check(args)
        mock_print.assert_called_with("Running pre-checks...")

if __name__ == '__main__':
    unittest.main()