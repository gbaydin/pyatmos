import pyatmos

atmos = pyatmos.Simulation(docker_image="gcr.io/i-agility-205814/pyatmos_docker",DEBUG=True)
atmos.Start()
state = atmos.run()
data = atmos.get_metadata() 
#atmos.exit()
