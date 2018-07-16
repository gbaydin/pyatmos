import re

def read_file(file_name):
    with open(file_name, 'r') as file:
        ret = {}
        for line in file.readlines():
            if not (line.startswith('*') or line.startswith('C') or line.startswith('c')):
                line = line.rstrip('\n\r')
                if len(line) > 0:
                    ll = re.split('= |=\t|!|\t', line)
                    key = ll[0]
                    val = ll[1].strip()
                    if val.startswith('\"'):
                        val = val.strip('\"')
                    else:
                        val = float(val)
                    ret[key] = val
    return ret

def strings_file(file_name):
    li = []
    with open(file_name, 'r') as file:
        for line in file.readlines():
            li.append(line)
    return li 



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
                                'LBOUND': info[8]
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





def species_header():
    return '''
***** SPECIES DEFINITIONS *****
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
*   LONG-LIVED O H C S N CL LBOUND  VDEP0   FIXEDMR SGFLUX    DISTH MBOUND SMFLUX  VEFF0  '''

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
