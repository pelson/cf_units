import sys
with open(sys.argv[1]) as fh:
    content = fh.read()


for line in content.split('\n'):
    if 'inherit from DEFAULT_MODE' in line:
        # Drop the ";"
        _, names = line[:-1].split(': ')
        names = names.split(', ')
        print(line.rstrip())
        for name in names:
            print('D_{name}: {name} -> type({name});'.format(name=name))
    else:
        print(line.rstrip())
