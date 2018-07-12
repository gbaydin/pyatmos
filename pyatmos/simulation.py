import docker
import tempfile
import os
#import numpy

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

    def run(self, species, max_iterations, n_clima_steps):
        '''
        Args: 
            species: dictionary, 
            max_iterations: int, 
            n_clima_steps: int, number of steps taken by clima 
        '''

        # modify species file
        species_file = self._read_container_file('/code/atmos/PHOTOCHEM/INPUTFILES/species.dat')

        # overwrite a file 
        print(type(species_file))



        # run photochem 
        self._container.exec_run('./Photo.run')
        print('run photo finished')

        # check for convergence of photochem   
        photochem_converged = self.check_photochem_convergence(max_iterations)

        if photochem_converged: 
            print('photochem converged')

            #Modify /CLIMA/IO/TEMPLATES/ModernEarth/input_clima.dat to /CLIMA/IO (this includes NSTEPS=    (number)) to change the number of steps
            clima_input = self._read_container_file('/code/atmos/CLIMA/IO/TEMPLATES/ModernEarth/input_clima.dat')
            replacement_clima = [] 
            for line in clima_input:
                if 'NSTEPS=' in line:
                    line = 'NSTEPS=    {0}           !step number (200 recommended for coupling)\n'.format(n_clima_steps)
                replacement_clima.append(line)
            tmp_file_name = tempfile.NamedTemporaryFile().name
            tmp_file = open(tmp_file_name, 'w')
            for l in replacement_clima:
                tmp_file.write(l)
            self._write_container_file(tmp_file, '/code/atmos/CLIMA/IO/TEMPLATES/ModernEarth/input_clima.dat')


            # check that it worked
            new_clima = self._read_container_file('/code/atmos/CLIMA/IO/TEMPLATES/ModernEarth/input_clima.dat')








            #To help with convergence, potentially replace /CLIMA/IO/TempIn.dat with /CLIMA/IO/TempOut.dat
            #Also set IUP=       0 in /CLIMA/IO/input_clima.dat

            #if converged:
            #./Clima.run

            #

            print('running clima ...')
            #self._container.exec_run('./Clima.run')
            print('finished clima')
            return 1 

        else:
            print('photochem did not converge before {0} iterations'.format(max_iterations))

            return 1 



    def check_photochem_convergence(self, max_iterations):
        '''
        Check that photochem has converged, search the output file for N = (number)
        if number < max_iterations then convergence has been achived 
        Args:
            max_iterations: an interger with the maximum number of iterations for convergence 
        '''

        #output = self._container.exec_run("grep 'N =' /code/atmos/PHOTOCHEM/OUTPUT/out.out")
        output = self._read_container_file('/code/atmos/PHOTOCHEM/OUTPUT/out.out')

        # find last "N = " and "EMAX"
        iterations = []
        for line in output:
            if 'N =' in line and 'EMAX' in line:
                iterations.append(line)
        last_line = iterations[-1]
        last_line = ' '.join(last_line.split()) # merge whitespace 
        number_of_iterations = int(last_line.split()[2])

        if number_of_iterations < max_iterations:
            return True
        else:
            return False 

    def _write_container_file(self, input_file_name, output_file_name):
        cmd = 'docker cp ' + input_file_name + ' ' + self._container.name + ':' + output_file_name

    def _read_container_file(self, container_file_name):
        tmp_file_name = tempfile.NamedTemporaryFile().name
        print('_read_container_file: ' + tmp_file_name)
        cmd = 'docker cp ' + self._container.name + ':' + container_file_name + ' ' + tmp_file_name
        os.system(cmd)
        return pyatmos.util.strings_file(tmp_file_name)

    def _get_container_file(self, container_file_name):
        tmp_file_name = tempfile.NamedTemporaryFile().name
        cmd = 'docker cp ' + self._container.name + ':' + container_file_name + ' ' + tmp_file_name
        os.system(cmd)
        return pyatmos.util.read_file(tmp_file_name)


    def _set_container_file(self):
        # todo 
        pass

    '''
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


    '''

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
