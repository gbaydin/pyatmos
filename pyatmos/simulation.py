import docker

class Simulation():
    def __init__(self, docker_image='registry.gitlab.com/frontierdevelopmentlab/astrobiology/pyatmos'):
        self._docker_image = docker_image
        print('Initializing Docker...')
        self._docker_client = docker.from_env()
        print('Pulling latest image... {}'.format(self._docker_image))
        self._docker_client.images.pull(self._docker_image)
        print('Ready.')

    def start(self):
        print('Starting Docker container...')
        self._container = self._docker_client.containers.run('registry.gitlab.com/frontierdevelopmentlab/astrobiology/pyatmos', detach=True)
        print('Container running.')
        print('Initializing simulation...')
        self._container.exec_run('./pyatmos_coupled_init.sh')
        print('Ready.')
