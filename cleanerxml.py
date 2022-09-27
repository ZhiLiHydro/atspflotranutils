import os
import sys
import glob

def get_fin():
    if len(sys.argv) == 1:
        print('input xml file not defined')
        print('example: python '+sys.argv[0]+' ats.xml')
        fl = glob.glob('*.xml')
        print('working dir has '+str(len(fl))+' xml files:')
        for i, f in enumerate(fl):
            print(str(i+1).zfill(2)+' : '+f)
        sys.exit(1)
    elif len(sys.argv) == 2:
        fin = sys.argv[1]
        if not os.path.exists(fin):
            print(fin+' does not exist')
            fl = glob.glob('*.xml')
            print('working dir has '+str(len(fl))+' xml files:')
            for i, f in enumerate(fl):
                print(str(i+1).zfill(2)+' : '+f)
            sys.exit(1)
    else:
        print('too many args')
        print('example: python '+sys.argv[0]+' myinput.xml')
        sys.exit(1)
    return fin

def reorganize_fin(fin):
    with open(fin) as f:
        indent = 0
        t = ''
        for i, line in enumerate(f):
            if indent < 0:
                print('indent < 0')
                print('closing tag error at line '+str(i+1))
                print(line)
                sys.exit(1)
            if line.strip().startswith('<ParameterList'):
                t += ' '*indent+line.strip().replace(' type="ParameterList"','')+'\n'
                indent += 8
            elif line.strip().startswith('</ParameterList'):
                indent -= 8
                t += ' '*indent+line.strip().replace(' type="ParameterList"','')+'\n'
    fout = fin.split('.xml')[0]+'_cleaned.xml'
    with open(fout, 'w') as f:
        f.write(t)
    print(fout+' generated')

if __name__ == '__main__':
    reorganize_fin(get_fin())

