import numpy as np

lbound = 0.5
ubound = 3.5
cores = 8
start = 1.0 


iterations_per_core = 50 
total_iterations = iterations_per_core * cores
iteration_spacing = (ubound - lbound)/total_iterations

print(total_iterations)
print(iteration_spacing)

iterations = np.arange(ubound, lbound, iteration_spacing)
print(iterations)

