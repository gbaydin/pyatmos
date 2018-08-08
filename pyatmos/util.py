import re

#____________________________________________________________________________
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

#____________________________________________________________________________
def UTC_now():
    '''
    Return int of unix time (in UTC) to nearest second
    '''
    import calendar
    from datetime import datetime  
    d = datetime.utcnow()
    unixtime = calendar.timegm(d.utctimetuple())
    return unixtime 

#____________________________________________________________________________
def strings_file(file_name):
    li = []
    with open(file_name, 'r') as file:
        for line in file.readlines():
            li.append(line)
    return li 

#____________________________________________________________________________
def printcol(text, fgcol='white', style='normal', bgcol='none'):
    '''
    Returns input text with some colour and style formatting 
    '''
    fgcols = {
        'dgrey':   2,
        'ddgrey':  8,

        'black':   30,
        'dred':    31,
        'dgreen':  32,
        'dyellow': 33,
        'dblue':   34,
        'dpink' :  35,
        'dcyan':   36,

        'pgrey':   37,
        'white':   38,

        'grey':    90,
        'red':     91,
        'green':   92,
        'yellow':  93,
        'blue':    94,
        'pink' :   95,
        'cyan':    96,
        }


    bgcols = {
        'none':    40,
        'red':     41,
        'green':   42,
        'yellow':  43,
        'blue':    44,
        'pink' :   45,
        'cyan':    46,
        'grey':    47,
        }


    styles = {
        'normal': 0,
        'bold': 1,
        'faded': 2,
        'underlined': 4,
        'flashing': 5,
        'fgbgrev': 7,
        'invisible': 8,
        }

    st = styles[style]
    fg = fgcols[fgcol]
    bg = bgcols[bgcol]

    format = ';'.join([str(st), str(fg), str(bg)])
    colstring = '\x1b[%sm%s\x1b[0m' % (format, text) 
    return colstring


#____________________________________________________________________________
def plot_multiscatter(dataframe, xvariables, xlabel, yvariable, ylabel, save_name):
    """Wrapper for matplotlib scatter
    Plot multiple scatter plots on the same figure
    Will also save with normal, log and symlog 
    """
    import matplotlib.pyplot as plt
    maximum = find_set_maximum(dataframe, xvariables)
    minimum = find_set_minimum(dataframe, xvariables)

    for xvar in xvariables:
        plt.scatter(dataframe[xvar], dataframe[yvariable],label=xvar) 
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)

    plt.legend()
    plt.xlim(xmin=minimum, xmax=maximum)
    plt.savefig(save_name)

    # assumes only one "." in the save_name, 
    save_name_symlog = save_name.replace('.', '_symlog.')
    plt.xscale('symlog')
    plt.savefig(save_name_symlog)

    plt.xscale('log')
    save_name_log = save_name_symlog.replace('_symlog','_log')
    plt.savefig(save_name_log)

    # clear plot 
    plt.clf()



#____________________________________________________________________________
def plot_scatter(dataframe, xvariable, xlabel, yvariable, ylabel, save_name, do_log=False):
    '''
    Wrapper for matplotlib scatter
    Plot and save a simple scatter plot of xvariable against yvariable
    Will label the axes as xlabel, ylabel
    Args:
        dataframe: pandas DataFrame.
        xvariable: Name of xvariable to be plotted, must be inside dataframe
        yvariable: Name of yvariable to be plotted, must be inside dataframe
        xlabel: string, x-axis label
        ylabel: string, y-axis label
        save_name: string, path of where to save the plot, must have file extension (e.g. .pdf)
        do_log: bool, have x-axis log scale (default false)
    '''
    import matplotlib.pyplot as plt

    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.scatter(dataframe[xvariable], dataframe[yvariable]) 
    if do_log:
        plt.xscale('log')
    plt.savefig(save_name)
    plt.clf()


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

