import docker
import tempfile
import os

import pyatmos

class Simulation():
    def __init__(self, docker_image='registry.gitlab.com/frontierdevelopmentlab/astrobiology/pyatmos'):
        self._docker_image = docker_image
        print('Initializing Docker...')
        self._docker_client = docker.from_env()
        print('Pulling latest image... {}'.format(self._docker_image))
        self._docker_client.images.pull(self._docker_image)
        self._container = None
        print('Ready.')

    def start(self):
        print('Starting Docker container...')
        self._container = self._docker_client.containers.run('registry.gitlab.com/frontierdevelopmentlab/astrobiology/pyatmos', detach=True, tty=True)
        print('Container running.')
        print('Initializing simulation...')
        self._container.exec_run('./pyatmos_coupled_init.sh')
        print('Ready.')

    def run(self, iterations=1):
        print('Running {} iterations...'.format(iterations))
        for i in range(iterations):
            print('Iteration {}'.format(i+1))
            self._container.exec_run('./pyatmos_coupled_iterate.sh')
        print('Done.')

    def get_input_clima(self):
        return self._get_container_file('/code/atmos/CLIMA/IO/input_clima.dat')

    def get_input_photochem(self):
        return self._get_container_file('/code/atmos/PHOTOCHEM/INPUTFILES/input_photchem.dat')

    def _get_container_file(self, container_file_name):
        tmp_file_name = tempfile.NamedTemporaryFile().name
        cmd = 'docker cp ' + self._container.name + ':' + container_file_name + ' ' + tmp_file_name
        os.system(cmd)
        return pyatmos.util.read_file(tmp_file_name)

    def __enter__(self):
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        self.close()

    def __del__(self):
        self.close()

    def close(self):
        print('Exiting...')
        if self._container is not None:
            print('Container killed.')
            self._container.kill()
