from pyatmos import Simulation

import platform

# for MAC
if platform.system() == 'Darwin':
    BASE_ATMOS   = '/Users/Will/Documents/FDL/atmos'
    BASE_RESULTS = '/Users/Will/Documents/FDL/results/distance_scan'

# for GCS
if platform.system() == 'Linux':
    BASE_ATMOS   = '/home/willfaw/atmos'
    BASE_RESULTS = '/home/willfaw/results/distance_scan'

atmos = Simulation(code_path = BASE_ATMOS, DEBUG=True)

distances = [ 0.39, 0.723, 1.0, 1.524, 2.0, 3.0 ]
distances = [1.0]
print(distances)
for distance in distances:
    flux_scaling = 1.0 / distance**2
    flux_scaling_str = '{0:.3f}'.format(flux_scaling)
    output_directory = BASE_RESULTS + '/flux_scan_results/distance_{0}'.format(distance)
    print('distance {0}\tflux scaling {1}\toutput directory {2}'.format(distance, flux_scaling_str, output_directory))
    result = atmos.run_distance_modification(flux_scaling = flux_scaling_str, output_directory = BASE_RESULTS+'/test_results', max_clima_steps=400, save_logfiles =True)
    print('Result: ', result, '\n')




