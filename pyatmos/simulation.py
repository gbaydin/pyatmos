import docker
import tempfile
import os
#import numpy

import pyatmos

def print_list(li):
    for e in li:
        print(e.replace('\n',''))

def format_datetime(unix_timestamp):
    '''
    Convert unix timestamp to human readable format
    Should automatically be in the timezone of the host machine
    '''
    import datetime
    return datetime.datetime.fromtimestamp(
        int(unix_timestamp)
    ).strftime('%Y-%m-%d %H:%M:%S')

class Simulation():
    def __init__(self, docker_image='registry.gitlab.com/frontierdevelopmentlab/astrobiology/pyatmos', DEBUG=False):
        self._docker_image = docker_image
        print('Initializing Docker...')
        self._docker_client = docker.from_env()
        print('Pulling latest image... {}'.format(self._docker_image))
        self._docker_client.images.pull(self._docker_image)
        self._container = None
        self._debug = DEBUG

        self._start_time         = None
        self._run_time_start     = None
        self._run_time_end       = None
        self._photochem_duration = None
        self._clima_duration     = None
        self._initialize_time    = pyatmos.util.UTC_now()
        print('Initialization complete: '+format_datetime(self._initialize_time))


    def start(self):
        print('Starting Docker container...')
        self._container = self._docker_client.containers.run('registry.gitlab.com/frontierdevelopmentlab/astrobiology/pyatmos', detach=True, tty=True)
        self._start_time = pyatmos.util.UTC_now()
        print("Container '{0}' running at {1}.".format(self._container.name, format_datetime(self._start_time) ))

    def run(self, species_concentrations, max_photochem_iterations, n_clima_steps=400, output_directory='/Users/Will/Documents/FDL/results'):
        '''
        Args: 
            species_concentrations: dictionary of species and concentrations to change them to, formatted as 
                                    { 'species name' : concentration }
                                    concentration should be fractional (not a percentage) 
            max_photochem_iterations: int, maximum number of iterations allowed by photochem to test for convergence  
            n_clima_steps: int, number of steps taken by clima (default 400) 
            output_directory: string, path to the directory to store outputs 
        '''

        self._run_time_start = pyatmos.util.UTC_now() 


        ################################
        # modify species file, changes the concentrations inside species.dat as specified by species_concentrations
        ################################
        self._modify_atmospheric_species('/code/atmos/PHOTOCHEM/INPUTFILES/species.dat', species_concentrations) 
        print('Modified species file with:')
        print(species_concentrations)

        
        ################################
        # Run photochem 
        ################################
        self._photochem_duration = pyatmos.util.UTC_now()
        self._container.exec_run('./Photo.run')
        self._photochem_duration = pyatmos.util.UTC_now() - self._photochem_duration 

        # check for convergence of photochem   
        [photochem_converged, n_photochem_iterations] = self._check_photochem_convergence(max_photochem_iterations)

        print('photochem finished after {0} iterations'.format(n_photochem_iterations))
        self.debug('photochem took {0} seconds'.format(self._photochem_duration))

        # copy photochem results
        cmd = 'docker cp ' + self._container.name + ':/code/atmos/PHOTOCHEM/OUTPUT/out.out ' + output_directory
        os.system(cmd)
        cmd = 'docker cp ' + self._container.name + ':/code/atmos/PHOTOCHEM/OUTPUT/out.dist ' + output_directory
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
            self._clima_duration = pyatmos.util.UTC_now()
            self._container.exec_run('./Clima.run')
            self._clima_duration = pyatmos.util.UTC_now() - self._clima_duration 
            print('finished clima')
            self.debug('Clima took '+str(self._clima_duration)+' seconds')

    
            # copy clima output files 
            cmd = 'docker cp ' + self._container.name + ':/code/atmos/CLIMA/IO/clima_allout.tab ' + output_directory 
            os.system(cmd)
            
            

        else:
            print('photochem did not converge before {0} iterations'.format(max_photochem_iterations))

        self._run_time_end = pyatmos.util.UTC_now()

        return 1 

    def _modify_atmospheric_species(self, species_file_name, species_concentrations):
        '''
        Modify the species file (species_file_name) to find-and-replace the concentrations listed in species_concentrations
        Copies the files out of the docker image, modifies them, and then puts them back 
        Args:
            species_file_name: string, path to species file inside the docker image
            species_concentrations: dictionary, containing species' concentrations' to modify
        '''
        
        # Parse existing species file 
        tmp_input_file_name = tempfile.NamedTemporaryFile().name
        cmd = 'docker cp ' + self._container.name + ':' + species_file_name + ' ' + tmp_input_file_name
        os.system(cmd)
        [long_lived_species, short_lived_species, inert_species, other_species] = pyatmos.modify_species_file.parse_species(tmp_input_file_name)

        # Reswrite species file
        tmp_output_file_name = tempfile.NamedTemporaryFile().name
        ofile = open(tmp_output_file_name, 'w')
        ofile.write( pyatmos.modify_species_file.species_header() ) 

        ofile.write( pyatmos.modify_species_file.write_species_long_lived(long_lived_species,   species_concentrations) )
        ofile.write( pyatmos.modify_species_file.write_species_short_lived(short_lived_species, species_concentrations) )
        ofile.write( pyatmos.modify_species_file.write_species_inert(inert_species,             species_concentrations) )
        ofile.write( pyatmos.modify_species_file.write_species_other(other_species,             species_concentrations) )

        ofile.close() 

        # Over-write the species file 
        self._write_container_file(tmp_output_file_name, species_file_name) 
    

    def _check_photochem_convergence(self, max_photochem_iterations):
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
            return [True, number_of_iterations]
        else:
            return [False, number_of_iterations] 

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

    def debug(self, message):
        if self._debug: 
            print('DEBUG: '+message)


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
