from cf_units._parse_udunits2 import parse as ud_parse
import sys




class Visitor:
    """
    This class may be used to help traversing the AST.
    
    It follows the same pattern as the Python ~`ast.NodeVisitor`.
    Users should typically not need to override either ``visit`` or
    ``generic_visit``, and should instead implement ``visit_<ClassName>``.

    Remember that each method MUST ``yield from generic_visit(node)`` if a node's
    children should be processed.

    An example of an implementation can be seen in ~`TeXVisitor`.

    """
    def visit(self, node):
        """Visit a node."""
        method = 'visit_' + node.__class__.__name__
        visitor = getattr(self, method, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        """
        Called if no explicit visitor function exists for a node.

        Should also be called by ``visit_<ClassName`` implementations
        if children of the node are to be processed.
        
        """
        return [self.visit(child) for child in iter_fields(node)]


def iter_fields(node):
    if hasattr(node, '_items'):
        yield from node._items()


class TeXVisitor(Visitor):
    def visit_BinaryOp(self, node):
        lhs = self.visit(node.lhs)
        rhs = self.visit(node.rhs)

        # Insert curly braces so that we don't have to
        # put them in the format string itself.
        lhs = '{{{}}}'.format(lhs)
        rhs = '{{{}}}'.format(rhs)

        if node.op.content == '*':
            format = '{lhs}\cdot{rhs}'
        elif node.op.content == '/':
            format = '\frac{lhs}{rhs}'
        elif node.op.content == '^':
            format = '{lhs}^{rhs}'
        else:
            format = '{lhs} {node.op.content} {rhs}'

        return format.format(lhs=lhs, rhs=rhs, node=node)

    def visit_Leaf(self, node):
        return node.content

    visit_Number = visit_Leaf

    def visit_Identifier(self, node):
        if node.content.lower() in ['pi']:
            result = '\pi'
        else:
            result = node.content
        return result


def walk_tree(tree, _d=0):
    print(' '* _d*2, type(tree), tree)
    if hasattr(tree, '_items'):
        for n in tree._items():
            walk_tree(n, _d=_d+1)




if __name__ == '__main__':
    t = ud_parse(sys.argv[1])

    print(type(t))
    print(t)

    print('---')

    walk_tree(t)


    print('======')
    r = TeXVisitor().visit(t)

    print(' '.join(r))
