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

def UTC_now():
    '''
    Return int of unix time (in UTC) to nearest second
    '''
    import calendar
    from datetime import datetime  
    d = datetime.utcnow()
    unixtime = calendar.timegm(d.utctimetuple())
    return unixtime 

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




