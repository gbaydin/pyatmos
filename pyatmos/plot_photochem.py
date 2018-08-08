#!/usr/bin/env python3

from Axis import Axis 
import pandas as pd 
import matplotlib.pyplot as plt
import numpy as np

pressure = Axis('P', 'Pressure', 'bar')
altitude = Axis('Z', 'Altitude', 'km')
temperature = Axis('T', 'Temperature', 'K')

#_____________________________________________________________________________
def main(input_file):

    base_dir = '/Users/Will/Documents/FDL/results/docker_image'

    flux_path = base_dir + '/parsed_photochem_fluxes.csv'
    mix_path  = base_dir + '/parsed_photochem_mixing_ratios.csv'

    flux_dataframe = pd.read_csv(flux_path)
    mix_dataframe  = pd.read_csv(mix_path) 
    
    # convert cm to km
    mix_dataframe['Z'] = mix_dataframe['Z']/1e5
    flux_dataframe['Z'] = flux_dataframe['Z']/1e5 

    sum_fluxes(flux_dataframe, [])
    plot_mixing_ratios(mix_dataframe)
    plot_fluxes(flux_dataframe) 

#_____________________________________________________________________________
def sum_fluxes(df, gases):
    '''

    '''
    for col in df:
        print("{0} \t {1:.2E}".format(col, np.sum(df[col])))



#_____________________________________________________________________________
def find_set_minimum(df, columns):
    '''
    Find minimum of a set of columns from a pandas dataframe
    '''
    import numpy as np
    return np.amin( df.loc[:, columns].min(axis=1) )

#_____________________________________________________________________________
def find_set_maximum(df, columns):
    '''
    Find maximum of a set of columns from a pandas dataframe
    '''
    import numpy as np
    return np.amax( df.loc[:, columns].max(axis=1) )


#_____________________________________________________________________________
def plot_fluxes(df):
    
    # find min/max of a set of c
    gases = ['CH4', 'CO', 'O2', 'H2', 'O', 'O3']
    gases = ['CO', 'O2', 'H2O', 'H2']
    gases = ['O2']
    gases = ['CH4']

    maximum = find_set_maximum(df, gases)
    minimum = find_set_minimum(df, gases)
    print(minimum, maximum)

    for g in gases:
        gas = Axis(g, 'Flux', 'molecules s$^{-1}$ cm$^{-2}$')
        plot_profile(df, gas, altitude)

    plt.legend()
    plt.xlim(xmin=minimum, xmax=maximum)
    plt.savefig('fluxes.pdf')

    plt.xscale('symlog')
    plt.savefig('fluxes_symlog.pdf')

    plt.xscale('log')
    plt.savefig('fluxes_log.pdf')

    # clear plot 
    plt.clf()


#_____________________________________________________________________________
def plot_mixing_ratios(df):


    gases = ['CH4', 'CO', 'O2', 'H2']
    gases = ['CO', 'O2', 'H2O', 'H2']
    gases = ['O2']
    maximum = find_set_maximum(df, gases)
    minimum = find_set_minimum(df, gases)
    print(minimum, maximum)

    for g in gases:
        gas = Axis(g, 'Mixing ratio')
        plot_profile(df, gas, altitude) 
    plt.legend()
    plt.xlim(xmin=minimum, xmax=maximum)
    plt.savefig('mixing_ratios.pdf')
    plt.xscale('log')
    plt.savefig('mixing_ratios_log.pdf')

    # clear plot 
    plt.clf()


#_____________________________________________________________________________
def plot_profile(dataframe, xaxis, yaxis):

    plt.xlabel(xaxis.funits)
    plt.ylabel(yaxis.funits)
    plt.scatter(dataframe[xaxis.index], dataframe[yaxis.index], label=xaxis.label) 

#_____________________________________________________________________________
if __name__ == "__main__":

    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option("-i", "--input_file", action="store", type="string", help="Parsed input atmos file")
    import sys
    if len(sys.argv) == 0:
        parser.print_help()
        sys.exit(0)

    options, args = parser.parse_args()
    option_dict = dict( (k, v) for k, v in vars(options).items() if v is not None)
    main(**option_dict)
