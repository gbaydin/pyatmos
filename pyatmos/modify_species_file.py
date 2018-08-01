#_____________________________________________________________________________
def parse_species(file_name):

    long_lived_species  = {}
    short_lived_species = {}
    inert_species       = {}
    other_species       = {}

    with open(file_name, 'r') as file:

        for line in file.readlines():
            if not (line.startswith('*')):
                line = line.rstrip('\n\r')
                if len(line) > 0:
                    info = line.split()
                    species = info[0] 

                    if 'LL' in line:
                        long_lived_species[species] = {
                                'LONG-LIVED' : info[1], 
                                'O' :  info[2], 
                                'H' :  info[3], 
                                'C' :  info[4], 
                                'S' : info[5], 
                                'N' : info[6], 
                                'CL' : info[7], 
                                'LBOUND' : info[8], 
                                'VDEP0' : info[9], 
                                'FIXEDMR' : info[10], 
                                'SGFLUX' : info[11], 
                                'DISTH' : info[12], 
                                'MBOUND' : info[13], 
                                'SMFLUX' :  info[14], 
                                'VEFF0' : info[15]
                                }
                    elif 'SL' in line:
                        short_lived_species[species] = {
                                'SHORT-LIVED' : info[1], 
                                'O' : info[2],
                                'H' : info[3],
                                'C' : info[4],
                                'S' : info[5],
                                'N' : info[6],
                                'CL' : info[7]
                                }
                    elif 'IN' in line:
                        inert_species[species] = {
                                'INERT-SPECIES' : info[1], 
                                'O' : info[2],
                                'H' : info[3],
                                'C' : info[4],
                                'S' : info[5],
                                'N' : info[6],
                                'CL' : info[7],
                                #'LBOUND': info[8]
                                'FIXEDMR' : info[8]
                                }
                    else:
                        other_species[species] = {
                                'other-species' : info[1], 
                                'O' : info[2],
                                'H' : info[3],
                                'C' : info[4],
                                'S' : info[5],
                                'N' : info[6],
                                'CL' : info[7],
                                }

        return [long_lived_species, short_lived_species, inert_species, other_species] 


#_____________________________________________________________________________
def find_species_union(dict1, dict2): 
    '''
    Return the union of the list of keys of two dictonaries
    '''
    keys1 = set(dict1.keys())
    keys2 = set(dict2.keys())
    return list( keys1.intersection(keys2) )

#_____________________________________________________________________________
def dictonary_keys_symmetric_difference(dict1, dict2):
    '''
    Return the list of keys that are in one dictinary but not the other
    '''
    keys1 = set(dict1.keys())
    keys1 = set(dict2.keys())
    return list( keys1.symmetric_difference(keys2) ) 

#_____________________________________________________________________________
def format_spaced_text(n_total_space, word):
    '''
    add a number of trainling spaces depending on the size of the word
    
    '''
    n_spaces = n_total_space - len(word)
    return word + ' '*n_spaces 

#_____________________________________________________________________________
def write_species_long_lived(original_species, modified_species):

    species_to_modify = find_species_union(original_species, modified_species)
    new_text = '*   LONG-LIVED O H C S N CL LBOUND  VDEP0   FIXEDMR SGFLUX    DISTH MBOUND SMFLUX  VEFF0  \n'
    for species in original_species.keys():

        # get original line (a dict of the original line)
        original_line = original_species[species] 

        # very carefully replace gas concentration entry in this line, preservespacing between entries (just in case this matters ...) 
        # Example lines below (with spacing) 
        #*   LONG-LIVED O H C S N CL LBOUND  VDEP0   FIXEDMR SGFLUX    DISTH MBOUND SMFLUX  VEFF0
        #O          LL  1 0 0 0 0 0    0     1.0E+00 0.      0.        0.      0      0.      0.
        #O2         LL  2 0 0 0 0 0    1     0.      2.1E-01 0.        0.      0      0.      0.
        #H2O        LL  1 2 0 0 0 0    0     0.      0.      0.        0.      0      0.      0.
        # Note should have used "format" for all of this ... 
        new_line = species
        nSpaces = 11 - len(species) 
        new_line += nSpaces*' '
        new_line += 'LL '
        for molecule in ['O', 'H', 'C', 'S', 'N', 'CL']:
            new_line += ' '+original_line[molecule]
        new_line += '    '
        new_line += format_spaced_text(6, original_line['LBOUND'])
        new_line += format_spaced_text(8, original_line['VDEP0']) 
        if species in species_to_modify:
            new_line += format_spaced_text(8, "{:.1E}".format(float(modified_species[species]))) # Modification to gas concentration here  
        else:
            new_line += format_spaced_text(8, original_line['FIXEDMR'])
        new_line += format_spaced_text(10, original_line['SGFLUX'])
        new_line += format_spaced_text(8, original_line['DISTH'])
        new_line += format_spaced_text(7, original_line['MBOUND'])
        new_line += format_spaced_text(8, original_line['SMFLUX'])
        new_line += original_line['VEFF0'] 

        #lines.append(new_line += '\n')
        new_text += new_line+'\n'
    return new_text 


#_____________________________________________________________________________
def write_species_short_lived(original_species, modified_species):
    '''
    Write information for the short-lived species
    Not currently forseen that these will be altered 
    '''

    new_text='''* NQ should be the number above
*   TRIDIAGONAL SOLVER
*NQ1 should be the number directly above
*   SHORT-LIVED SPECIES
'''
    for species in original_species.keys():
        element = original_species[species] 
        new_text += format_spaced_text( 11, species ) 
        new_text += 'SL  {0} {1} {2} {3} {4} {5}\n'.format( element['O'], element['H'], element['C'], element['S'], element['N'], element['CL'] )


    return new_text


#_____________________________________________________________________________
def write_species_inert(original_species, modified_species):
    '''
    Write information for inert species, format as below:
    CO2        IN  2 0 1 0 0 0    3.6E-4       !must be second to last IN
    N2         IN  0 0 0 0 2 0    0.78          !must be last IN  (FIXED MR NOT YET USED...)
    '''


    new_text = '*   INERT SPECIES\n'
    species_to_modify = find_species_union(original_species, modified_species)
    for species in original_species.keys():
        original_line = original_species[species] 
        new_line = format_spaced_text(11, species)
        new_line +='IN  '
        new_line += '{0} {1} {2} {3} {4} {5}'.format(
                original_line['O'],
                original_line['H'],
                original_line['C'],
                original_line['S'],
                original_line['N'],
                original_line['CL'],
                ) 

        if species in species_to_modify:
            print(species_to_modify)
            new_line += '    {0}'.format(modified_species[species])
        else:
            new_line += '    '+original_line['FIXEDMR']

        new_text += new_line+'\n'

    return new_text 

#_____________________________________________________________________________
def write_species_other(original_species, modified_species):
    '''
    Write information for the 'other' species
    Not currently forseedn that these will be altered 
    '''
    return '''* NSP should be the number directly above
HV         HV  0 0 0 0 0 0
M          M   0 0 0 0 0 0'''




#_____________________________________________________________________________
def species_header():
    return '''***** SPECIES DEFINITIONS *****
*
*define LL,SL,TD, etc here
*
*LBOUND = lower boundary conditions
* 0 = constant deposition velocity (VDEP)
* 1 = constant mixing ratio
* 2 = constant upward flux (SGFLUX)
* 3 = constant vdep + vertically distributed upward flux  (uses SGFLUX and DISTH)
*
*MBOUND - Upper boundary conditions
* 0 = CONSTANT EFFUSION VELOCITY (VEFF)  - (H and H2 set in code for molecular diffusion/diffusion limited flux)
* 1 = constant mixing ratio - never been used so needs testing
* 2 = CONSTANT FLUX (SMFLUX) (option for CO2/CO/0 in code)
*
* 
'''

def species_footer():
    return '''
* NQ should be the number above
*   TRIDIAGONAL SOLVER
*NQ1 should be the number directly above
*   SHORT-LIVED SPECIES
HNO2       SL  2 1 0 0 1 0
O1D        SL  1 0 0 0 0 0
CH21       SL  0 2 1 0 0 0
CH23       SL  0 2 1 0 0 0
C2H5       SL  0 5 2 0 0 0
SO21       SL  2 0 0 1 0 0
SO23       SL  2 0 0 1 0 0
HSO3       SL  3 1 0 1 0 0
OCS2       SL  1 0 1 2 0 0
*   INERT SPECIES
CO2        IN  2 0 1 0 0 0    3.6E-4       !must be second to last IN 
N2         IN  0 0 0 0 2 0    0.78          !must be last IN  (FIXED MR NOT YET USED...)
* NSP should be the number directly above
HV         HV  0 0 0 0 0 0
M          M   0 0 0 0 0 0'''





