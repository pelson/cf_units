import sys
import jinja2



with open(sys.argv[1]) as fh:
    content = fh.read()

g4_template = jinja2.Environment(loader=jinja2.BaseLoader).from_string(content)


write = print
write = lambda v: None


import re

mode_pattern = re.compile(r'mode ([A-Z_]+)\;')

token_pattern = re.compile(r'([A-Z_]+) ?\:.*')

mode = 'DEFAULT_MODE'


default_tokens = []
import collections
tokens = collections.defaultdict(list)

for line in content.split('\n'):
    mode_g = mode_pattern.match(line)
    if mode_g:
        mode = mode_g.group(1)

    token_g = token_pattern.match(line)
    if token_g:
        tokens[mode].append(token_g.group(1))

    if mode and 'inherit from DEFAULT_MODE' in line:
        # Drop the ";"
        _, names = line[:-1].split(': ')
        names = names.split(', ')
        write(line.rstrip())
        if '*' in names:
            names = default_tokens
        for name in names:
            write('_{mode}_{name}: {name} -> type({name});'.format(name=name, mode=mode))
    else:
        write(line.rstrip())


print(g4_template.render(tokens=tokens)) 


