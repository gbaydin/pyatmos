#!/usr/bin/env python3
import pandas as pd 

'''
Script to parse the tables produced by clima
Reads the text-based format and converts the inital and final tables into separate CSV files

Example usage 
python parse.py -o /Users/Will/Documents/FDL/results/google_cloud -c /Users/Will/Documents/FDL/results/google_cloud/clima_allout.tab -p /Users/Will/Documents/FDL/results/google_cloud/out.out 

'''

def main(output_directory, clima_input, photochem_input, debug):


    print('Will write to '+output_directory)
    print('Reading '+clima_input)
    parse_clima(input_file = clima_input,         output_directory = output_directory, debug=debug )
    print('Reading '+photochem_input)
    parse_photochem(input_file = photochem_input, output_directory = output_directory, debug=debug )


def parse_photochem(input_file, output_directory, debug):

    ph_file = open(input_file, 'r')

    flux_tables = [] 
    all_tables = [] 

    capture_flux = False 
    mixing_ratio_line_number = 0 
    line_number = 0
    for line in ph_file:
        line_number += 1 

        '''
        Note to reader, one could capture _all_ tables using Z as the start/stop condition.
        (one would have to be careful)
        '''

        # prepare line for CSV 
        info = line.rstrip('\n\r')
        info = info.split()
        info = ','.join(info)

        ###################
        # Simply capture all tables (may be poorly formatted) 
        ###################
        if len(info) > 0:
            if 'Z,' in info:
                try:
                    if len(this_all_table) > 0:
                        all_tables.append(this_all_table)
                        this_all_table = []
                except UnboundLocalError:
                    this_all_table = []
                this_all_table.append(info)


        ###################
        # Capture flux tables
        ###################
        if 'FLUXES OF LONG-LIVED SPECIES' in line:
            capture_flux = True
            continue # skip this line


        if capture_flux:
            if len(info) > 0:
                if 'Z' in info: # start condition for new table 
                    try: 
                        if len(this_flux_table) > 0:
                            flux_tables.append(this_flux_table)
                            this_flux_table = [] # clear it 
                    except UnboundLocalError: # create the first table 
                        this_flux_table = [] 

                if not 'AQUEOUS PHASE SPECIES' in line:
                    this_flux_table.append(info.split(','))
                
                if 'AQUEOUS PHASE SPECIES' in line:
                    flux_tables.append(this_flux_table)

        # stop condition 
        if 'AQUEOUS PHASE SPECIES' in line:
            capture_flux = False 


        ###################
        # get line number of last 'mixing ratios' 
        ###################
        if 'MIXING RATIOS OF LONG-LIVED SPECIES' in line:
            mixing_ratio_line_number = line_number 

    ph_file.close()

    ###################
    # parse mixing ratios
    ###################

    # open file again and re-read
    ph_file = open(input_file, 'r')
    line_number = 0
    capture_mixratio = False 
    tptl_line_number = -999 
    mix_tables = []
    for line in ph_file:
        line_number += 1

        # start 
        if line_number >= mixing_ratio_line_number:

            # prepare line for CSV 
            info = line.rstrip('\n\r')
            info = info.split()
            info = ','.join(info)

            if len(info) > 0:
                if 'Z,' in info or 'OZONE COLUMN DEPTH' in line: # start condition for new table
                    capture_mixratio = True
                    try:
                        if len(this_mix_table) > 0:
                            mix_tables.append(this_mix_table)
                            this_mix_table = [] 
                    except UnboundLocalError:
                        this_mix_table = [] 

                # skip next two lines for 'TP, TL'  
                if 'TP, TL' in line:
                    tptl_line_number = line_number 
                    capture_mixratio = False
                if line_number == tptl_line_number or line_number == tptl_line_number+1 or line_number == tptl_line_number+2:
                    continue

                if capture_mixratio:
                    this_mix_table.append(info.split(','))

            # start 
            if 'MIXING RATIOS OF LONG-LIVED SPECIES' in line:
                capture_mixratio = True

            # stop 
            if 'OZONE COLUMN DEPTH' in line:
                capture_mixratio = False 

            # end
            if 'OZONE COLUMN DEPTH' in line:
                break

    ph_file.close()


    ########################
    # concatenate tables, write to output CSV
    ########################
    if debug: print('flux tables: ', len(flux_tables))
    final_flux_table = concatenate_tables(flux_tables)
    if debug: print('mixing ratio tables: ', len(mix_tables))
    final_mix_table = concatenate_tables(mix_tables)

    final_flux_table.to_csv(output_directory+'/parsed_photochem_fluxes.csv')
    print('Writing', output_directory+'/parsed_photochem_fluxes.csv')
    final_mix_table.to_csv(output_directory+'/parsed_photochem_mixing_ratios.csv')
    print('Writing', output_directory+'/parsed_photochem_mixing_ratios.csv')




def check_float_conversion(li):
    '''
    Takes a list of strings (where each string represents a number)
    Checks that the string can be converted to a float and then does so
    designed to catch poory formatted numbers, such as 
    ValueError: could not convert string to float: '5.36-102' 
    Args:
        li: a list of strings
    '''

    new_list = []
    for element in li:
        try:
            f_element = float(element)
        except ValueError:
            sign = None
            if '-' in element: 
                sign = '-'
                # could be negative
                tokens = element.split('-')
                if len(tokens) > 2:
                    tokens = ['-'+tokens[1], tokens[2]]
                #print(element, tokens)

            if '+' in element:
                sign = '+'
                tokens = element.split('+')
            exponent = tokens[-1]
            if int(exponent) > 99:
                new_number_str = '{0}E{1}{2}'.format(tokens[0], sign, exponent)
                f_element = float(new_number_str) 
            else:
                print('WARNING, some other issue')

        new_list.append(f_element)
    return new_list 


def concatenate_tables(tables):
    '''
    Method to concatenate a set of tables by "Z" value. Assumes tables are in the same ordering 
    Args:
        tables: list of sub-lists, each sub-list has a "Z" column 
    '''
    dfs = []
    for t in tables:
        df = table_to_dataframe(t) 
        #print(df)
        dfs.append(df) 
    results = pd.concat(dfs, axis=1, sort=False)
    return results 


def table_to_dataframe(table):
    '''
    Convert table into pandas dataframe 
    Check that the floats can be converted 
    Args:
        table: list of sub-lists, first sub-list must be columns, second must be floats 
    '''
    columns = table[0]
    data_temp    = table[1:]
    data = []
    for d in data_temp:
        data.append(check_float_conversion(d))
    df = pd.DataFrame(data=data,columns=columns)
    return df 

    '''
    #data    = [x.split(',') for x in table[1:]]
    #columns = table[0].split(',')
    convert to floats 
    import numpy as np
    for col in df:
        df[col]=df[col].astype(np.number)
    '''


def parse_clima(input_file, output_directory, debug):

    # Define the "boxing" used in the clima output file
    binding = "J     P         ALT         T        CONVEC       DT          TOLD        FH20       FSAVE        FO3        TCOOL       THEAT"
    
    cfile = open(input_file, 'r')
    
    ofile1 = open(output_directory+'/parsed_clima_initial.csv', 'w')
    ofile2 = open(output_directory+'/parsed_clima_final.csv', 'w')
    
    unused_lines = [] 
    capture = False
    n_tables = 0 
    for line in cfile: 

        # test for box
        if binding in line:
            capture = not capture
            if capture:
                n_tables += 1 

        # CSV-ify the table 
        if capture:
            info = line.split()

            if n_tables == 1:
                ofile1.write( ','.join(info)) 
                ofile1.write('\n')
            if n_tables == 2:
                ofile2.write( ','.join(info)) 
                ofile2.write('\n')
    ofile1.close()
    ofile2.close()

    if debug: print('parse_clima finished')

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
