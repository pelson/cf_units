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

    def __repr__(self):
        return '<{}>'.format(self)


class Operand(Leaf):
    pass

class Root(Node):
    def __init__(self, *units):
        self.units = units

    def _items(self):
        return self.units

    def __str__(self):
        return ' '.join(str(u) for u in self.units)


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
    # def __getattribute__(self, attr):
    #     # Useful to debug what is getting called.
    #     print('GET:', attr)
    #     return super().__getattribute__(attr)

    def defaultResult(self):
        # Called once per ``visitChildren`` call.
        return []

    def aggregateResult(self, aggregate, nextResult):
        # Always result a list from visitChildren
        # (default behaviour is to return the last element).
        if nextResult is not None:
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
        r = ctx.getText()
        # print(ctx)
        # print(ctx.__dict__)
        # print(ctx.symbol)
        # print(ctx.symbol.__dict__)
        # print(dir(ctx.symbol))
        # print('IDX:', ctx.symbol.tokenIndex)
        # print(ctx.symbol.type)

        symbol_idx = ctx.symbol.type
        if symbol_idx < 0:
            # EOF
            pass
        else:
            lexer = ctx.symbol.source[0]

            import unicodedata
            consumers = {lexer.INT: int,
                         lexer.FLOAT: float,
                         lexer.WS: lambda n: None,
                         lexer.ID: str,
                         # Convert unicode to compatibility form
                         lexer.UNICODE_EXPONENT: lambda n: int(unicodedata.normalize('NFKC', n).replace('−', '-')),
                         lexer.SIGN: str,
                         lexer.DIVIDE: str,
                         lexer.MULTIPLY: str,
                         lexer.RAISE: str,
                         }
            if symbol_idx in consumers:
                r = consumers[symbol_idx](r)
            else:
                print('UNHANDLED TERMINAL:', repr(r))

        return Leaf(r)

    def visitSigned_int(self, ctx):
        return self.visitAny_signed_number(ctx)

    def strip_whitespace(self, nodes):
        return [n for n in nodes if n.content is not None]

    def visitJuxtaposed_multiplication(self, ctx):
        nodes = self.visitChildren(ctx)
        lhs, rhs = self.strip_whitespace(nodes)
        return BinaryOp('*', lhs, rhs)

    def visitProduct_spec(self, ctx):
        # UDUNITS grammar makes no parse distinction for these types,
        # so we have to do the grunt work here.
        nodes = self.visitChildren(ctx)

        # power spec
        if isinstance(nodes, Node):
            node = nodes
        elif len(nodes) == 3 and isinstance(nodes[1], Operand):
            node = BinaryOp(nodes[1], nodes[0], nodes[2])
        else:
            raise RuntimeError('Unhandled product spec {}'.format(nodes))
        return node

    def visitDivide(self, ctx):
        _ = self.visitDivide(ctx)  # noqa: F841
        return Operand('/')

    def visitMultiply(self, ctx):
        _ = self.visitChildren(ctx)  # noqa: F841
        # Multiply is just the symbol (for now), so reach out to the parent.
        return Operand('*')

    def visitNegative_exponent(self, ctx):
        nodes = self.visitChildren(ctx)
        return BinaryOp('^-', nodes[0], nodes[2])

    def visitJuxtaposed_raise(self, ctx):
        nodes = self.visitChildren(ctx)
        lhs, rhs = self.strip_whitespace(nodes)
        return BinaryOp('^', lhs, rhs)

    def visitExponent_unicode(self, ctx):
        nodes = self.visitChildren(ctx)
        lhs, rhs = nodes
        return BinaryOp('^', lhs, rhs)

    def visitSci_number(self, ctx):
        nodes = self.visitChildren(ctx)
        if isinstance(nodes, Leaf):
            number = nodes
        else:  
            assert isinstance(nodes, list)
            assert len(nodes) == 2
            sign, number = nodes
            number = number.content
            if sign.content == '-':
                number = -number
            number = Leaf(number)
        return number

    visitAny_unsigned_number = visitSci_number
    visitAny_signed_number = visitSci_number

    def visitExponent(self, ctx):
        nodes = self.visitChildren(ctx)
        return BinaryOp('^', nodes[0], nodes[2])

    def visitShift(self, ctx):
        _ = self.visitChildren(ctx)  # noqa: F841
        return '@'

    def visitUnit_spec(self, ctx):
        nodes = self.visitChildren(ctx)
        
        # Drop the EOF
        if isinstance(nodes, Node):
            node = Root()
            assert str(nodes) == '<EOF>'
        else:
            assert len(nodes) == 2
            assert isinstance(nodes, list)
            if isinstance(nodes[0], Node):
                node = Root(nodes[0])
            else:
                node = Root(*nodes[0])
        return node


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


    token_lookup = {getattr(lexer, rule, -1): rule for rule in lexer.ruleNames}
#    print(token_lookup)

    if True:
        lexer2 = LabeledExprLexer(InputStream(unit_str))
        stream2 = CommonTokenStream(lexer2)

        parser2 = LabeledExprParser(stream2)
        # The top level concept.
        tree = parser2.unit_spec()

        # NOTE, because of the parser._listeners error handler, this only works if we have a valid grammar in the first place.
        print()
        for token in stream2.tokens:
            if token.text != '<EOF>':
                token_type_idx = token.type 
                rule = token_lookup[token_type_idx]
                print("%s: %s" % (token.text, rule))

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
