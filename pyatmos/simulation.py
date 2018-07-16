import docker
import tempfile
import os
#import numpy

import pyatmos

def print_list(li):
    for e in li:
        print(e.replace('\n',''))

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
        print('Container running {0}.'.format(self._container.name))

    def run(self, species, max_photochem_iterations, n_clima_steps=400):
        '''
        Args: 
            species: dictionary of species and concentrations to change them to 
            max_photochem_iterations: int, maximum number of iterations allowed by photochem to test for convergence  
            n_clima_steps: int, number of steps taken by clima (default 400) 
        '''

        # modify species file: TODO
        species_file = self._read_container_file('/code/atmos/PHOTOCHEM/INPUTFILES/species.dat')


        





        # run photochem 
        self._container.exec_run('./Photo.run')
        print('run photo finished')

        # check for convergence of photochem   
        photochem_converged = self.check_photochem_convergence(max_photochem_iterations)

        # copy photochem results
        cmd = 'docker cp ' + self._container.name + ':/code/atmos/PHOTOCHEM/OUTPUT/out.out /Users/Will/Documents/FDL/results' 
        os.system(cmd)
        cmd = 'docker cp ' + self._container.name + ':/code/atmos/PHOTOCHEM/OUTPUT/out.dist /Users/Will/Documents/FDL/results' 
        os.system(cmd)



        ################################
        # if photochem converged, run clima
        ################################

        if photochem_converged: 
            print('photochem converged')

            # Modify CLIMA/IO/TEMPLATES/ModernEarth/input_clima.dat to change NSTEPS parameter 
            clima_input = self._read_container_file('/code/atmos/CLIMA/IO/input_clima.dat')
            replacement_clima = [] 
            for line in clima_input:
                if 'NSTEPS=' in line:
                    line = 'NSTEPS=    {0}           !step number (200 recommended for coupling)\n'.format(n_clima_steps)
                replacement_clima.append(line)
            tmp_file_name = tempfile.NamedTemporaryFile().name
            tmp_file = open(tmp_file_name, 'w')
            for l in replacement_clima:
                tmp_file.write(l)
            tmp_file.close() # VERY important to close the file!! 
            self._write_container_file(tmp_file_name, '/code/atmos/CLIMA/IO/input_clima.dat')


            
            ################################
            #To help with convergence, potentially replace /CLIMA/IO/TempIn.dat with /CLIMA/IO/TempOut.dat
            #Also set IUP=       0 in /CLIMA/IO/input_clima.dat
            ################################


            self._container.exec_run("cp  /code/atmos/CLIMA/IO/TempOut.dat /code/atmos/CLIMA/IO/TempIn.dat")
            self._container.exec_run("sed -i 's/IUP=       1/IUP=       0/g' /code/atmos/CLIMA/IO/input_clima.dat")


            # Run clima 
            print('running clima with {0} steps ...'.format(n_clima_steps))
            self._container.exec_run('./Clima.run')
            print('finished clima')

    
            # copy clima output files 
            cmd = 'docker cp ' + self._container.name + ':/code/atmos/CLIMA/IO/clima_allout.tab /Users/Will/Documents/FDL/results' 
            os.system(cmd)
            
            
            return 1 

        else:
            print('photochem did not converge before {0} iterations'.format(max_photochem_iterations))

            return 1 



    def check_photochem_convergence(self, max_photochem_iterations):
        '''
        Check that photochem has converged, search the output file for N = (number)
        if number < max_photochem_iterations then convergence has been achived 
        Args:
            max_photochem_iterations: an interger with the maximum number of iterations for convergence 
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

        if number_of_iterations < max_photochem_iterations:
            return True
        else:
            return False 

    def _write_container_file(self, input_file_name, output_file_name):
        cmd = 'docker cp ' + input_file_name + ' ' + self._container.name + ':' + output_file_name
        os.system(cmd)


    def _read_container_file(self, container_file_name):
        tmp_file_name = tempfile.NamedTemporaryFile().name
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
