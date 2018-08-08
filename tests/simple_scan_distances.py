from pyatmos import Simulation

atmos = Simulation(code_path = '/home/willfaw/atmos', DEBUG=True)


for x in range(5, 51, 5):
    distance = float(x)/10
    flux_scaling = 1.0 / distance**2
    output_directory = '/home/willfaw/flux_scan_results/distance_{0}'.format(distance)
    print(distance, flux_scaling, output_directory)
    atmos.run_distance_modification(flux_scaling = flux_scaling, output_directory = 'test_results', max_clima_steps=10)
    print('')

#atmos.run_distance_modification(flux_scaling = 0.30, output_directory = output_directory)



