"""
Programmatically control Docker Compose.
"""

from optparse import Option
from pathlib import Path
import subprocess
from typing import List, Optional


DEFAULT_DOCKER_COMPOSE_BASE_CMD = ['docker', 'compose']
DEFAULT_DOCKER_COMPOSE_FILE_NAME = 'docker-compose.yml'


def sh(cmd_line: List[str]):
    subprocess.run(cmd_line, check=True)


def dir_from_file_path(pathname: str) -> Path:
    file = Path(pathname)
    return file.parent


def make_path(dir_pathname: str, filename: str) -> Path:
    base_dir = dir_from_file_path(dir_pathname)
    return base_dir / filename


class DockerCompose:
    """Control the operation of Docker Compose on a given Docker Compose
    YAML file.

    Typically you'd use this class in a test run to set up Docker services
    for your integration or end-to-end tests. Here's an example Pytest
    `conftest.py` file where we start Docker services before any test
    in the enclosing Python package gets run and then stop the services
    after the last test in the package has run. The services are declared
    in a `docker-compose.yml` file in the same directory as `conftest.py`.

        import pytest
        from fipy.docker import DockerCompose

        docker = DockerCompose(__file__)

        @pytest.fixture(scope='package', autouse=True)
        def run_services():
            docker.start()
            yield
            docker.stop()

    """

    def __init__(
        self,
        test_script_path: str,
        docker_compose_file_name: str = DEFAULT_DOCKER_COMPOSE_FILE_NAME,
        docker_compose_cmd: List[str] = DEFAULT_DOCKER_COMPOSE_BASE_CMD):
        self._base_dir = dir_from_file_path(test_script_path)
        self._docker_file = make_path(test_script_path,
                                      docker_compose_file_name)
        self._base_cmd = docker_compose_cmd


    def run_cmd(self, *xs):
        compose = self._base_cmd + ['-f', str(self._docker_file)]
        cmd = compose + [x for x in xs]
        sh(cmd)

    def build_images(self):
        self.run_cmd('build')

    def start(self):
        self.run_cmd('up', '-d')

    def stop(self):
        self.run_cmd('down', '-v')

    def start_service(self, name: str):
        self.run_cmd('start', name)

    def stop_service(self, name: str):
        self.run_cmd('stop', name)

    def pause_service(self, name: str):
        self.run_cmd('pause', name)

    def unpause_service(self, name: str):
        self.run_cmd('unpause', name)
