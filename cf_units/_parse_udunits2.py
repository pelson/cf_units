# (C) British Crown Copyright 2019, Met Office
#
# This file is part of cf-units.
#
# cf-units is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the
# Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# cf-units is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with cf-units.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import (absolute_import, division, print_function)
from six.moves import (filter, input, map, range, zip)  # noqa

from antlr4 import InputStream, CommonTokenStream
from antlr4.error.ErrorListener import ErrorListener

from ._udunits2_p.udunits2Lexer import udunits2Lexer as LabeledExprLexer
from ._udunits2_p.udunits2Parser import udunits2Parser as LabeledExprParser
from ._udunits2_p.udunits2Visitor import udunits2Visitor as LabeledExprVisitor


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
    #  def __getattribute__(self, attr):
    #      # Useful to debug what is getting called.
    #      print('GET:', attr)
    #      return super().__getattribute__(attr)

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
        # TODO: This should be removed once the grammar is fixed
        # up. (xref: space between "x * 2")
        if not r.strip():
            return None
        return Leaf(r)

    def visitProduct_spec(self, ctx):
        # UDUNITS grammar makes no parse distinction for these types,
        # so we have to do the grunt work here.
        children = super().visitMultiply(ctx)

        if isinstance(children, Node):
            node = children
        elif len(children) == 3 and isinstance(children[1], Operand):
            # TODO: This should be removed once the grammar is fixed
            # up. (xref: space between "x * 2")
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
        _ = super().visitDivide(ctx)  # noqa: F841
        return Operand('/')

    def visitMultiply(self, ctx):
        _ = super().visitMultiply(ctx)  # noqa: F841
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
        _ = super().visitShift(ctx)  # noqa: F841
        return '@'

    def visitUnit_spec(self, ctx):
        call_through = super().visitShift(ctx)
        # Drop the EOF
        if str(call_through[-1]) != '<EOF>':
            print(call_through)
            print([str(n) for n in call_through])
            raise RuntimeError('EOF not found at end.')

        # print(self._walk_ast(call_through[0]))
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


class ErrorListener(ErrorListener):
    def __init__(self, the_string):
        # At the time of writing, I didn't find a better way of getting
        # the string being parsed. There definitely will be though.
        self.the_string = the_string
        super(ErrorListener, self).__init__()

    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        # https://stackoverflow.com/a/36367357/741316

        context = ("inline", line, column+2, "'{}'".format(self.the_string))
        syntax_error = SyntaxError(msg, context)
        raise syntax_error from None


def normalize(unit_str):
    return str(parse(unit_str))


def parse(unit_str):
    # nb: The definition (C code) says to strip the unit string first.
    unit_str = unit_str.strip()
    lexer = LabeledExprLexer(InputStream(unit_str))
    stream = CommonTokenStream(lexer)
    parser = LabeledExprParser(stream)

    parser._listeners = [ErrorListener(unit_str)]

    # The top level concept.
    tree = parser.unit_spec()

    visitor = ExprVisitor()
    return visitor.visit(tree)


def main(argv):
    ast = parse(argv[1])
    print('AST:', repr(repr_walk_ast(ast)))
    print(ast)


if __name__ == '__main__':
    import sys
    main(sys.argv)
