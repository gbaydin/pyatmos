from pyatmos import Simulation

atmos = Simulation(code_path = '/Users/Will/Documents/FDL/atmos')
atmos.run_distance_modification(flux_scaling = 0.30, output_directory = 'test_results')



