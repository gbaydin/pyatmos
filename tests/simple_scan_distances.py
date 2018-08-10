from pyatmos import Simulation

import platform

# for MAC
if platform.system() == 'Darwin':
    BASE_ATMOS   = '/Users/Will/Documents/FDL/atmos2'
    BASE_ATMOS   = '/Users/Will/Documents/FDL/atmos'
    BASE_RESULTS = '/Users/Will/Documents/FDL/results/distance_scan'

# for GCS
if platform.system() == 'Linux':
    BASE_ATMOS   = '/home/willfaw/atmos'
    BASE_RESULTS = '/home/willfaw/results/distance_scan'

atmos = Simulation(code_path = BASE_ATMOS, DEBUG=False)

distances = [1.0] 
distances = [1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 2.0]
distances = [0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2]
for distance in distances:
    flux_scaling = 1.0 / distance**2
    output_directory = BASE_RESULTS + '/flux_scan_results/distance_{0}'.format(distance)
    print('distance {0}\tflux scaling {1}\toutput directory {2}'.format(distance, flux_scaling, output_directory))

    result = atmos.run(flux_scaling = flux_scaling, 
                                             output_directory = BASE_RESULTS+'/distance_{0}'.format(distance),
                                             max_clima_steps  = 400,
                                             save_logfiles    = True)

    print('Result: ', result, '\n')
    print('')

atmos.close()




