from cf_units._parse_udunits2 import parse as ud_parse
import sys

t = ud_parse(sys.argv[1])


print(type(t))


def walk_tree(tree):
    print(type(tree), tree)
    if hasattr(tree, '_items'):
        for n in tree._items():
            walk_tree(n)

print(t)


print('---')

walk_tree(t)

