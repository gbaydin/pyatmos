from pyatmos import Simulation

import platform


def main(ranges, iteration):

    # for MAC
    if platform.system() == 'Darwin':
        BASE_ATMOS   = '/Users/Will/Documents/FDL/atmos'
        BASE_ATMOS   = '/Users/Will/Documents/FDL/atmos'
        BASE_RESULTS = '/Users/Will/Documents/FDL/results/distance_scan'

    # for GCS
    if platform.system() == 'Linux':
        BASE_ATMOS   = '/home/willfaw/atmos'
        BASE_RESULTS = '/home/willfaw/results/distance_scan'


    # convert string ranges into numers
    distances = [float(x) for x in ranges.split(',')]
    print(distances)

    # define base atmos path
    BASE_ATMOS = BASE_ATMOS+iteration 
    print('will use atmos: ', BASE_ATMOS) 
    

    atmos = Simulation(code_path = BASE_ATMOS, DEBUG=False)
    for distance in distances:
        flux_scaling = 1.0 / distance**2
        output_directory = BASE_RESULTS + '/flux_scan_results/distance_{0:.3f}'.format(distance)
        print('distance {0}\tflux scaling {1}\toutput directory {2}'.format(distance, flux_scaling, output_directory))

        result = atmos.run(flux_scaling = flux_scaling, 
                output_directory = output_directory,
                max_clima_steps  = 400,
                save_logfiles    = True)

        print('Result: ', result, '\n')
        print('')

    atmos.close()


if __name__ == "__main__":
    from optparse import OptionParser
    parser = OptionParser()

    parser.add_option("-r", "--ranges",            action="store", type="string")
    parser.add_option("-i", "--iteration",          action="store", type="string")

    options, args = parser.parse_args()
    #option_dict = dict( (k, v) for k, v in vars(options).iteritems() if v is not None)
    option_dict = dict( (k, v) for k, v in vars(options).items() if v is not None)

    main(**option_dict)
