"""extracts skeletons of ATS xml files for easier understanding
"""

import os
import sys
import glob

if len(sys.argv) == 1:
    print()
    print('input xml file not defined')
    print('example: python '+sys.argv[0]+' ats.xml')
    fl = glob.glob('*.xml')
    print('working dir has '+str(len(fl))+' xml files:')
    for f,i in zip(fl,range(len(fl))):
            print(str(i+1).zfill(2)+' : '+f)
    print()
    sys.exit(1)
elif len(sys.argv) == 2:
    fin = sys.argv[1]
    if not os.path.exists(fin):
        print()
        print(fin+' does not exist')
        fl = glob.glob('*.xml')
        print('working dir has '+str(len(fl))+' xml files:')
        for f,i in zip(fl,range(len(fl))):
            print(str(i+1).zfill(2)+' : '+f)
        print()
        sys.exit(1)
else:
    print()
    print('too many args')
    print('example: python '+sys.argv[0]+' ats.xml')
    print()
    sys.exit(1)

fout = fin.split('.xml')[0]+'_cleaned.xml'

try:
    os.remove(fout)
except:
    pass

with open(fin) as f:
    indent = 0
    lines = f.readlines()
    tout = ''
    for line in lines:
        if indent < 0:
            print('indent < 0 error')
            sys.exit(1)
        if line.strip().startswith('<ParameterList'):
            tout += ' '*indent+line.strip().replace(' type="ParameterList"','')+'\n'
            indent += 8
        elif line.strip().startswith('</ParameterList'):
            indent -= 8
            tout += ' '*indent+line.strip().replace(' type="ParameterList"','')+'\n'
    with open(fout, 'w') as g:
        g.write(tout)

