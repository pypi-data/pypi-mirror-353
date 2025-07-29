import unittest
from unittest.mock import patch
from aira_cli.docker import docker_ps, docker_images, docker_logs, docker_start, docker_stop, docker_restart, docker_compose_up, docker_compose_down, docker_compose_build, docker_compose_ps, docker_cleanup

class TestDockerCommands(unittest.TestCase):

    @patch('builtins.print')
    def test_docker_ps(self, mock_print):
        args = argparse.Namespace(all=False)
        docker_ps(args)
        mock_print.assert_called_with("docker ps")

if __name__ == '__main__':
    unittest.main()