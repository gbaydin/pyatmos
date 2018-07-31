import docker
import tempfile
import os
#import numpy

import pyatmos

#_________________________________________________________________________
def print_list(li):
    for e in li:
        print(e.replace('\n',''))

#_________________________________________________________________________
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
    def __init__(self, 
            docker_image='registry.gitlab.com/frontierdevelopmentlab/astrobiology/pyatmos', 
            code_path=None
            DEBUG=False, 
            atmos_directory = '/code/atmos'
            gcs_bucket=None):
        '''
        docker_image: string (optional). If specified, pyatmos will communicate with a docker image, otherwise use the code_path 
        code_path: string (optional). If specified, pyatmos will communicate witha local version of atmos. The string is the path to the atmos directory 
        DEBUG: bool, if set to true, extra debug messages are printed
        gcs_bucket: string, name of gcs bucket 
        '''

        # get input arguments
        self._docker_image = docker_image
        if self._docker_image:
            self._initialize_docker()
        self._debug = DEBUG
        self._atmos_directory = atmos_directory 

        # test if GCS bucket is enabled  
        if not gcs_bucket is None:
            self._gcs_enabled = True 
        else:
            self._gcs_enabled = False 

        # metadata for runtime 
        self._start_time         = None
        self._run_time_start     = None
        self._run_time_end       = None
        self._photochem_duration = None
        self._clima_duration     = None
        self._initialize_time    = pyatmos.util.UTC_now()

        # other run metadata
        self._n_photochem_iterations = None 
        self._n_clima_iterations = None
        print('Initialization complete: '+format_datetime(self._initialize_time))

    #_________________________________________________________________________
    def _initialize_docker(self):
        print('Initializing Docker...')
        self._docker_client = docker.from_env()
        print('Pulling latest image... {}'.format(self._docker_image))
        self._docker_client.images.pull(self._docker_image)
        self._container = None



    #_________________________________________________________________________
    def start(self):
        if self._docker_image:
            print('Starting Docker container...')
            self._container = self._docker_client.containers.run(self._docker_image, detach=True, tty=True)
            self._start_time = pyatmos.util.UTC_now()
            print("Container '{0}' running at {1}.".format(self._container.name, format_datetime(self._start_time) ))
        else:
            print('pyatmos is ready to go! ')

    #_________________________________________________________________________
    def run(self, 
            species_concentrations={}, 
            max_photochem_iterations=10000, 
            max_clima_steps=500, 
            input_file_path = None,
            output_directory='/Users/Will/Documents/FDL/results'
            ):
        '''
        Configures and runs ATMOS, then collects the output.  
        - Modifes species file with custom concentrations (supplied via species_concentrations) 
        - Runs the photochemical model and checks for convergence in max_photochem_iterations steps 
        - If converged, then runs the clima model. First modifies the clima input file with max_clima_steps   
        - copies the results files to output_directory 

        Args: 
            species_concentrations: dictionary of species and concentrations to change them to, formatted as 
                                    { 'species name' : concentration (float) }
                                    concentration should be fractional (not a percentage) 
            max_photochem_iterations: int, maximum number of iterations allowed by photochem to test for convergence  
            max_clima_steps: int, number of steps taken by clima (default 400) 
            input_file_path: string, path to the previous solution for photochem 
            output_directory: string, path to the directory to store outputs 
        '''

        self._run_time_start = pyatmos.util.UTC_now() 

        # make sure we're in the right directory
        self._generic_run('cd '+self._atmos_directory) 

        # run the photochemical model 
        photochem_converged = self._run_photochem(species_concentrations, max_photochem_iterations, output_directory, input_file_path)

        # if photochem didn't converge, exit 
        if not photochem_converged: 
            return 'photochem_error' 
        else:
            print('photochem converged')

        # run clima  
        if 'CH4' in species_concentrations.keys():
            methane_concentration = species_concentrations['CH4'] 
        else: 
            methane_concentration = 1.80E-06 
        clima_converged = self._run_clima(max_clima_steps, output_directory, methane_concentration)

        # if clima didn't converge, exit
        if not clima_converged:
            return 'clima_error'
        else:
            print('clima converged')

        self._run_time_end = pyatmos.util.UTC_now()
        return 'success' 

    #_________________________________________________________________________
    def get_metadata(self):

        return {
                'start_time' : self._start_time,
                'photochem_duration' : self._photochem_duration,
                'photochem_iterations' : self._n_photochem_iterations,  
                'clima_duration' : self._clima_duration,
                #'clima_iterations' : self._n_clima_iterations, # TO DO, clima iterations not set   
                'run_duraton' : self._run_time_end - self._run_time_start,
                }

    #_________________________________________________________________________
    def _run_photochem(self, species_concentrations, max_photochem_iterations, output_directory, input_file_path):
        '''
        Function to actually run the photochemical model, copies the results once finished 
        '''

        ################################
        # modify species file, changes the concentrations inside species.dat as specified by species_concentrations
        ################################
        self._modify_atmospheric_species(self._atmos_directory+'/PHOTOCHEM/INPUTFILES/species.dat', species_concentrations) 
        print('Modified species file with:')
        print(species_concentrations)

        
        # put in the new in.dist file (can be from previous run of photochem)
        if input_file_path:
            self._write_container_file(input_file_path, self._atmos_directory+'/PHOTOCHEM/in.dist')


        
        ################################
        # Run photochem 
        ################################
        self._photochem_duration = pyatmos.util.UTC_now()
        self._generic_run('./Photo.run')
        self._photochem_duration = pyatmos.util.UTC_now() - self._photochem_duration 

        # check for convergence of photochem   
        [photochem_converged, n_photochem_iterations] = self._check_photochem_convergence(max_photochem_iterations)
        self._n_photochem_iterations = n_photochem_iterations 
        if not photochem_converged:
            return False

        print('photochem finished after {0} iterations'.format(n_photochem_iterations))
        self.debug('photochem took {0} seconds'.format(self._photochem_duration))


        ################################
        # copy photochem results
        ################################

        self._copy_container_file(self._atmos_directory+'/PHOTOCHEM/OUTPUT/out.out', output_directory)
        self._copy_container_file(self._atmos_directory+'/PHOTOCHEM/OUTPUT/out.dist', output_directory) 
        self._copy_container_file(self._atmos_directory+'/PHOTOCHEM/INPUTFILES/species.dat', output_directory)
        self._copy_container_file(self._atmos_directory+'/PHOTOCHEM/in.dist', output_directory) 

        # copy photochem results inside the docker image, ready for the next run of photochem 
        self._generic_run("cp  {0}/PHOTOCHEM/OUTPUT/out.dist /PHOTOCHEM/in.dist.".format(self._atmos_directory)

        return True 

    #_________________________________________________________________________
    def _run_clima(self, max_clima_steps, output_directory, methane_concentration):


        # Modify CLIMA/IO/TEMPLATES/ModernEarth/input_clima.dat to change NSTEPS parameter 
        # Also change IMET parameter depending on methane concentration 

       
        clima_input = self._read_container_file(self._atmos_directory+'/CLIMA/IO/input_clima.dat') # clima_input: file containing strings of input_clima.dat 

        replacement_clima = [] 
        for line in clima_input:
            if 'NSTEPS=' in line:
                line = 'NSTEPS=    {0}           !step number (200 recommended for coupling)\n'.format(max_clima_steps)
            if 'IMET=' in line and methane_concentration > 1e-4:
                line = 'IMET=      {0}\n'.format(1)
            replacement_clima.append(line)
        tmp_file_name = tempfile.NamedTemporaryFile().name
        tmp_file = open(tmp_file_name, 'w')
        for l in replacement_clima:
            tmp_file.write(l)
        tmp_file.close() # VERY important to close the file!! 
        self._write_container_file(tmp_file_name, self._atmos_directory+'/CLIMA/IO/input_clima.dat')


        ################################
        #To help with convergence, potentially replace /CLIMA/IO/TempIn.dat with /CLIMA/IO/TempOut.dat
        #Also set IUP=       0 in /CLIMA/IO/input_clima.dat
        ################################

        self._generic_run("cp  /code/atmos/CLIMA/IO/TempOut.dat /code/atmos/CLIMA/IO/TempIn.dat")
        self._generic_run("sed -i 's/IUP=       1/IUP=       0/g' /code/atmos/CLIMA/IO/input_clima.dat")

        # Run clima 
        print('running clima with {0} steps ...'.format(max_clima_steps))
        self._clima_duration = pyatmos.util.UTC_now()
        self._generic_run('./Clima.run')
        self._clima_duration = pyatmos.util.UTC_now() - self._clima_duration 
        print('finished clima')
        self.debug('Clima took '+str(self._clima_duration)+' seconds')

        # copy clima output files out of docker image  
        self._copy_container_file(self._atmos_directory+'/CLIMA/IO/clima_allout.tab', output_directory)

        return True 


    #_________________________________________________________________________
    def print_run_metadata(self):
        '''
        Prints metadata from the previous call of run 
        '''
        print('Photochem duration {0}'.format(self._photochem_duration))
        print('Clima duration {0}'.format(self._clima_duration))



    #_________________________________________________________________________
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
        self._copy_container_file( species_file_name, tmp_input_file_name )
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
    

    #_________________________________________________________________________
    def _check_photochem_convergence(self, max_photochem_iterations):
        '''
        Check that photochem has converged, search the output file for N = (number)
        if number < max_photochem_iterations then convergence has been achived 
        Args:
            max_photochem_iterations: an interger with the maximum number of iterations for convergence 
        '''
        #output = self._generic_run("grep 'N =' /code/atmos/PHOTOCHEM/OUTPUT/out.out")
        #print('output\n')
        #print(output)

        # output is a string containing the lines of /PHOTOCHEM/OUTPUT/out.out 
        output = self._read_container_file(self._atmos_directory+'/PHOTOCHEM/OUTPUT/out.out')

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

    #_________________________________________________________________________
    def _write_container_file(self, input_file_name, output_file_name):
        '''
        Copies a file INTO of docker image 
        Args:
            input_file_name: string, path of file on local filesystem
            output_file_name: string, path of file inside docker image
        '''
        if self._docker_image:
            cmd = 'docker cp {0} {1}:{2}'.format(input_file_name, self._container.name, output_file_name)
        else:
            cmd = 'cp {0} {1}'.format(input_file_name, output_file_name)
        self.debug(cmd)
        os.system(cmd)

    #_________________________________________________________________________
    def _copy_container_file(self, input_file_name, output_path):
        '''
        Copies a file OUT of the docker image
        Args:
            input_file_name: string, path of file inside the docker image
            output_path: string, destination path (or directory) of file 
        '''

        if self._docker_image:
            cmd = 'docker cp ' + self._container.name +':'+input_file_name + ' ' + output_path  
        else:
            cmd = 'cp {0} {1}'.format(input_file_name, output_path)
        self.debug(cmd)
        os.system(cmd) 


    #_________________________________________________________________________
    def _read_container_file(self, container_file_name):
        '''
        Copy file out of the container and turn it into python strings 
        '''
        tmp_file_name = tempfile.NamedTemporaryFile().name
        self._copy_container_file(container_file_name, tmp_file_name) 
        #cmd = 'docker cp ' + self._container.name + ':' + container_file_name + ' ' + tmp_file_name
        #self.debug(cmd)
        #os.system(cmd)
        return pyatmos.util.strings_file(tmp_file_name)

    def _generic_run(self, command):
        '''
        Runs command either inside docker or simple os system command
        '''
        if self._docker_image:
            self._container.exec_run(command)
        else:
            os.system(command)



    #_________________________________________________________________________
    def debug(self, message):
        if self._debug: 
            print('DEBUG: '+message)


    #_________________________________________________________________________
    def _set_container_file(self):
        # todo 
        pass

    '''
    #_________________________________________________________________________
    def _get_container_file(self, container_file_name):
        # Copies a file OUT of the docker image to a temp file, and then returns the string of at file  
        tmp_file_name = tempfile.NamedTemporaryFile().name
        cmd = 'docker cp ' + self._container.name + ':' + container_file_name + ' ' + tmp_file_name
        self.debug(cmd)
        os.system(cmd)
        return pyatmos.util.read_file(tmp_file_name)

    def run(self, iterations=1):
        print('Running {} iterations...'.format(iterations))
        for i in range(iterations):
            print('Iteration {}'.format(i+1))
            self._generic_run('./pyatmos_coupled_iterate.sh')
        print('Done.')

    def get_input_clima(self):
        return self._get_container_file(self._atmos_directory+'/CLIMA/IO/input_clima.dat')

    def get_input_photochem(self):
        return self._get_container_file(self._atmos_directory+'/PHOTOCHEM/INPUTFILES/input_photchem.dat')


    '''

    #_________________________________________________________________________
    def __enter__(self):
        return self

    #_________________________________________________________________________
    def __exit__(self, exception_type, exception_value, traceback):
        self.close()

    #_________________________________________________________________________
    def __del__(self):
        self.close()

    #_________________________________________________________________________
    def close(self):
        print('Exiting...')
        if self._container is not None:
            print('Container killed.')
            self._container.kill()
