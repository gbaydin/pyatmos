#!/usr/bin/env python3
import pyatmos

'''
Script to parse the tables produced by clima
Reads the text-based format and converts the inital and final tables into separate CSV files

Example usage 
python parse.py -o /Users/Will/Documents/FDL/results/google_cloud -c /Users/Will/Documents/FDL/results/google_cloud/clima_allout.tab -p /Users/Will/Documents/FDL/results/google_cloud/out.out 

'''

def main(output_directory, clima_input, photochem_input, debug):


    print('Will write to '+output_directory)
    print('Reading '+clima_input)
    pyatmos.parser.parse_clima(input_file = clima_input,         output_directory = output_directory, debug=debug )
    print('Reading '+photochem_input)
    pyatmos.parser.parse_photochem(input_file = photochem_input, output_directory = output_directory, debug=debug )





if __name__ == "__main__": 

    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option("-o", "--output_directory", action="store", type="string", help="Parsed input clima file")
    parser.add_option("-p", "--photochem_input", action="store", type="string", help="Parsed input clima file")
    parser.add_option("-c", "--clima_input", action="store", type="string", help="Parsed input clima file")
    parser.add_option("-d", "--debug", action="store_true", dest="debug", default=False, help="print debug messages")

    options, args = parser.parse_args()
    option_dict = dict( (k, v) for k, v in vars(options).items() if v is not None)
    main(**option_dict)
