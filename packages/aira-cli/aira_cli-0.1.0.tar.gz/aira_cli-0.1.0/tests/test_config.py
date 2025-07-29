import unittest
from unittest.mock import patch
from aira_cli.config import config_set, config_get, config_defaults

class TestConfigCommands(unittest.TestCase):

    @patch('builtins.print')
    def test_config_set(self, mock_print):
        args = argparse.Namespace(key="test_key", value="test_value")
        config_set(args)
        mock_print.assert_called_with("sudo bash -c echo 'test_value' > /etc/aira/test_key")

if __name__ == '__main__':
    unittest.main()