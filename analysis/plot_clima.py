#!/usr/bin/env python3

import pandas as pd 
import matplotlib.pyplot as plt

class Axis():
    def __init__(self, index, title, units):
        self.index = index
        self.title = title
        self.units = units
        self.funits = '{0} [{1}]'.format(self.title, self.units)


def main():

    f1 = '/Users/Will/Documents/FDL/results/parsed_clima_initial.csv'
    f2 = '/Users/Will/Documents/FDL/results/parsed_clima_final.csv'

    print('Read clima into dataframe ...')
    clima_dataframe = pd.read_csv(f1)
    print('Make plot...')

    pressure = Axis('P', 'Pressure', 'bar')
    altitude = Axis('ALT', 'Altitude', 'km')
    temperature = Axis('T', 'Temperature', 'K')

    plot_clima_profile(clima_dataframe, xaxis=pressure, yaxis=altitude) 
    plot_clima_profile(clima_dataframe, xaxis=temperature, yaxis=altitude) 
    #print(clima_dataframe)
    
def plot_clima_profile(clima, xaxis, yaxis):

    plt.xlabel(xaxis.funits)
    plt.ylabel(yaxis.funits)
    plt.scatter(clima[xaxis.index], clima[yaxis.index]) 
    plt.xscale('log')

    print('show...')
    plt.savefig('{0}_{1}.pdf'.format(xaxis.title, yaxis.title))
    #plt.clf()



if __name__ == "__main__":
    main()
