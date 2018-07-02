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
