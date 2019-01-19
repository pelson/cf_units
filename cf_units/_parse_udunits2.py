from antlr4 import InputStream, CommonTokenStream
from _udunits2_p.udunits2Lexer import udunits2Lexer as LabeledExprLexer
from _udunits2_p.udunits2Parser import udunits2Parser as LabeledExprParser
from _udunits2_p.udunits2Visitor import udunits2Visitor as LabeledExprVisitor


class Node:
    pass

class Leaf(Node):
    def __init__(self, content):
        self.content = content

    def __str__(self):
        return '{}'.format(self.content)


class Operand(Leaf):
    pass


class BinaryOp(Node):
    def __init__(self, op, lhs, rhs):
        self.lhs = lhs
        self.rhs = rhs
        self.op = op

    def _items(self):
        return self.lhs, self.op, self.rhs

    def __str__(self):
        return '{self.lhs}{self.op}{self.rhs}'.format(self=self)



class ExprVisitor(LabeledExprVisitor):
#    def __getattribute__(self, attr):
#        # Useful to debug what is getting called.
#        print('GET:', attr)
#        return super().__getattribute__(attr)


    def defaultResult(self):
        # Called once per ``visitChildren`` call.
        return []

    def aggregateResult(self, aggregate, nextResult):
        # Always result a list from visitChildren
        # (default behaviour is to return the last element).
        aggregate.append(nextResult)
        return aggregate

    def visitChildren(self, node):
        # If there is only a single item in the visitChildren's list,
        # return the item. The list itself has no semantics.
        result = super().visitChildren(node)
        if len(result) == 1:
            return result[0]
        else:
            return result

    def visitTerminal(self, ctx):
        print('CTX TERM:', ctx.__dict__)
        r = ctx.getText()
        # TODO: This should be removed once the grammar is fixed up. (xref: space between "x * 2")
        if not r.strip():
            return None
        return Leaf(r)

    def visitProduct_spec(self, ctx):
        # UDUNITS grammar makes no parse distinction for these types, so we have
        # to do the grunt work here.
        children = super().visitMultiply(ctx)

        if isinstance(children, Node):
            node = children
        elif len(children) == 3 and isinstance(children[1], Operand):
            # TODO: This should be removed once the grammar is fixed up. (xref: space between "x * 2")
            if children[0] is None:
                node = children[2]
            elif children[2] is None:
                node = children[0]

            else:
                node = BinaryOp(children[1], children[0], children[2])
        elif not children:
            return []
        elif len(children) == 2:
            print("CAREFUL: could be mult/raise")
            # A special case that the grammar doesn't pick out well.
            node = BinaryOp('^', children[0], children[1])
        else:
            node = 'UNKNOWN'
            print(ctx.__dict__)
            print('DEAL WITH ME:')
            print(children)
            for c in children:
                print(type(c), c.__dict__)
            node = children[0]
        return node

    def visitDivide(self, ctx):
        call_through = super().visitDivide(ctx)
        return Operand('/')

    def visitMultiply(self, ctx):
        call_through = super().visitMultiply(ctx)
        # Multiply is just the symbol (for now), so reach out to the parent.
        return Operand('*')

    def visitNegative_exponent(self, ctx):
        call_through = super().visitMultiply(ctx)
        return BinaryOp('^-', call_through[0], call_through[2])
        return [call_through[0], '^-', call_through[2]]

    def visitExponent(self, ctx):
        call_through = super().visitMultiply(ctx)
        return BinaryOp('^', call_through[0], call_through[2])

    def visitShift(self, ctx):
        call_through = super().visitShift(ctx)
        return '@'

    def visitUnit_spec(self, ctx):
        call_through = super().visitShift(ctx)
        # Drop the EOF
        if str(call_through[-1]) != '<EOF>':
            print(call_through)
            print([str(n) for n in call_through])
            raise RuntimeError('EOF not found at end.')

        #print(self._walk_ast(call_through[0]))
        assert len(call_through) == 2
        return call_through[0]

def repr_walk_ast(node):
    if isinstance(node, Leaf):
        return str(node)
    elif isinstance(node, BinaryOp):
        return [repr_walk_ast(n) for n in node._items()]
    else:
        # A string.
        return node
        #            print("DEAL WITH:", node)



from antlr4.error.ErrorListener import ErrorListener

class MyErrorListener( ErrorListener ):

    def __init__(self, the_string):
        # At the time of writing, I didn't find a better way of getting
        # the string being parsed. There definitely will be though.
        self.the_string = the_string
        super(MyErrorListener, self).__init__()

    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        # https://stackoverflow.com/a/36367357/741316
        raise SyntaxError(msg, (("inline", line, column+2, "'{}'".format(self.the_string)))) from None


def normalize(unit_str):
    return str(parse(unit_str))

def parse(unit_str):
    # nb: The definition (C code) says to strip the unit string first.
    unit_str = unit_str.strip()
    input = InputStream(unit_str)
    lexer = LabeledExprLexer(input)
    stream = CommonTokenStream(lexer)
    parser = LabeledExprParser(stream)

    parser._listeners = [MyErrorListener(unit_str)]

    # The top level concept.
    tree = parser.unit_spec()

    visitor = ExprVisitor()
    r = visitor.visit(tree)
    return visitor.visit(tree)


def main(argv):
    ast = parse(argv[1])
    print('AST:', repr(repr_walk_ast(ast)))
    print(ast)


if __name__ == '__main__':
    import sys
    main(sys.argv)
