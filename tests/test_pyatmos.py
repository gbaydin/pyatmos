import os
THISDIR=os.path.dirname(os.path.abspath(__file__))

import pyatmos

atmos = pyatmos.Simulation(docker_image="gcr.io/i-agility-205814/pyatmos_docker",DEBUG=True)
atmos.Start()
state = atmos.run(output_directory=THISDIR+'/test_results')
data = atmos.get_metadata() 
#atmos.exit()
