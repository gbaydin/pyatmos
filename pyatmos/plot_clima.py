#!/usr/bin/env python3

from Axis import Axis
import pandas as pd 
import matplotlib.pyplot as plt

#_____________________________________________________________________________
def main(input_file, output_directory):

    f1 = '/Users/Will/Documents/FDL/results/parsed_clima_initial.csv'
    f2 = '/Users/Will/Documents/FDL/results/parsed_clima_final.csv'

    print('Read clima into dataframe ...')
    # synthetic feature 
    clima_dataframe = pd.read_csv(input_file)
    clima_dataframe['atm'] = clima_dataframe['P']*0.986923
    print(clima_dataframe) 
    print('Make plot...')

    pressure = Axis('P', 'Pressure', 'bar')
    atmospheres = Axis('atm', 'Pressure', 'atm') 
    altitude = Axis('ALT', 'Altitude', 'km')
    temperature = Axis('T', 'Temperature', 'K')

    #plot_clima_profile(clima_dataframe, xaxis=pressure, yaxis=altitude, output_directory=output_directory) 
    plot_clima_profile(clima_dataframe, xaxis=atmospheres, yaxis=altitude, output_directory=output_directory) 
    plot_clima_profile(clima_dataframe, xaxis=temperature, yaxis=altitude, output_directory=output_directory) 
    #print(clima_dataframe)
    
#_____________________________________________________________________________
def plot_clima_profile(dataframe, xaxis, yaxis, output_directory):

    plt.xlabel(xaxis.funits)
    plt.ylabel(yaxis.funits)
    plt.scatter(dataframe[xaxis.index], dataframe[yaxis.index]) 
    #plt.xscale('log')

    plt.savefig(output_directory+'/{0}_{1}.pdf'.format(xaxis.title, yaxis.title))
    plt.clf()

#_____________________________________________________________________________
if __name__ == "__main__":

    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option("-i", "--input_file", action="store", type="string", help="Parsed input clima file")
    parser.add_option("-o", "--output_directory", action="store", type="string", help="Output directory path")
    import sys
    if len(sys.argv) == 0:
        parser.print_help()
        sys.exit(0)

    options, args = parser.parse_args()
    option_dict = dict( (k, v) for k, v in vars(options).items() if v is not None)
    main(**option_dict)
