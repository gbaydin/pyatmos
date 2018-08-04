import os
THISDIR=os.path.dirname(os.path.abspath(__file__))

import pyatmos

atmos = pyatmos.Simulation(
        code_path = '/Users/Will/Documents/FDL/atmos',
        #docker_image="gcr.io/i-agility-205814/pyatmos:co2-photogenic",
        DEBUG=True)
atmos.start()
state = atmos.run(
        output_directory=THISDIR+'/test_results',
        save_logfiles = True,
        )
data = atmos.get_metadata() 
#atmos.exit()
