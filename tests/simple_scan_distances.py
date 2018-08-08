from pyatmos import Simulation
#BASE_ATMOS = '/Users/Will/Documents/FDL/atmos'
BASE_ATMOS = '/home/willfaw/atmos'

BASE_RESULTS = '/home/willfaw/results'

atmos = Simulation(code_path = BASE_ATMOS, DEBUG=True)


for x in range(5, 51, 5):
    distance = float(x)/10
    flux_scaling = 1.0 / distance**2
    output_directory = BASE_RESULTS + '/flux_scan_results/distance_{0}'.format(distance)
    print(distance, flux_scaling, output_directory)
    atmos.run_distance_modification(flux_scaling = flux_scaling, output_directory = BASE_RESULTS+'/test_results', max_clima_steps=10, save_logfiles =True)
    print('')

#atmos.run_distance_modification(flux_scaling = 0.30, output_directory = output_directory)



