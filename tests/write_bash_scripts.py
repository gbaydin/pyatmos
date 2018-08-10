import numpy as np

lbound = 0.5
start = 1.0 
ubound = 3.5

lower_cores = 3
upper_cores = 5
cores = 8

def main():

    iterations_per_core = 50 
    total_iterations = iterations_per_core * cores
    iteration_spacing = (ubound - lbound)/total_iterations

    print(total_iterations)
    print(iteration_spacing)

    iterations = np.arange(lbound, ubound, iteration_spacing)

    lower_iterations = np.arange(lbound, 1.0, iteration_spacing)
    upper_iterations = np.arange(1.0, ubound, iteration_spacing)

    #lower_iterations1 = lower_iterations[::2]
    #lower_iterations2 = np.setdiff1d(lower_iterations, lower_iterations1)

    lower_ranges = split_range_into_n(lower_iterations, 2)
    upper_ranges = split_range_into_n(upper_iterations, 4) 


    for i, r in enumerate(lower_ranges+upper_ranges):
        ifile = open('test{0}.sh'.format(i), 'w')
        ifile.write('#!/usr/bin/env bash\n')
        str_range = [str(x) for x in list(r)]
        str_range = ','.join(str_range)
        ifile.write('python run_with_range.py -r "{0}" -i {1}\n'.format(str_range, i))
        ifile.close()







def split_range_into_n(array, n):
    print('split_range_into_n')

    # sample from every n'th and then remove the first element (assuming the first element is sampled)
    arrays = [] 
    for i in range(n):
        split_range = array[::n]
        array=np.delete(array, [0]) 
        #print(i, array) 
        arrays.append(split_range)
    return arrays 



if __name__ == "__main__":
    main()


