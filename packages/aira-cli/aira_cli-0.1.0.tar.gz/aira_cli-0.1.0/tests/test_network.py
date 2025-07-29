import unittest
from unittest.mock import patch
from aira_cli.network import network_status, network_firewall_list, network_firewall_allow, network_firewall_deny, network_firewall_block, network_firewall_unblock, network_firewall_reset, network_dns_add_host, network_dns_remove_host, network_dns_show_hosts, network_dns_configure_resolver

class TestNetworkCommands(unittest.TestCase):

    @patch('builtins.print')
    def test_network_status(self, mock_print):
        args = argparse.Namespace()
        network_status(args)
        mock_print.assert_called_with("ip addr")

if __name__ == '__main__':
    unittest.main()