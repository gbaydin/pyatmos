import pyatmos 

atmos = pyatmos.Simulation(
    #docker_image="registry.gitlab.com/frontierdevelopmentlab/astrobiology/pyatmos:modified-atmos",
    code_path="/code/atmos",
    DEBUG=True)

atmos.start()
status = atmos.run(species_concentrations = {},
        max_photochem_iterations=10000, 
        max_clima_steps=500, 
        input_file_path = None,
        output_directory='/code/results'
        )

metadata = atmos.get_metadata()
