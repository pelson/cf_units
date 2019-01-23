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


class Timestamp(Node):
    def __init__(self, date, clock, tz_offset=0):
        self.date = date
        self.clock = clock
        self.tz_offset = tz_offset

    def _items(self):
        return self.date, self.clock, self.tz_offset

    def __str__(self):
        return f'{self.date}T{self.clock}+{self.tz_offset}'


class NaiveClock(Node):
    def __init__(self, hour=0, minute=0, second=0):
        self.hour = hour
        self.minute = minute
        self.second = second

    def _items(self):
        return self.hour, self.minute, self.second

    def __str__(self):
        return f'{self.hour}:{self.minute}:{self.second}'



class Date(Node):
    def __init__(self, year, month=1, day=1):
        self.year = year
        self.month = month
        self.day = day

    def _items(self):
        return self.year, month, self.day

    def __str__(self):
        return f'{self.year}-{self.month}-{self.day}'


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
                         lexer.PLUS: str,
                         lexer.MINUS: str,
                         lexer.DIVIDE: str,
                         lexer.MULTIPLY: str,
                         lexer.RAISE: str,
                         lexer.SHIFT_OP: str,
                         lexer.CLOCK: self.prepareCLOCK,  #lambda arg: arg.split(':'), #lambda *args: ' '.join(args),
                         lexer.TIMESTAMP: self.prepareTIMESTAMP
                         }
            if symbol_idx in consumers:
                r = consumers[symbol_idx](r)
            else:
                print('UNHANDLED TERMINAL:', repr(r))

        if not isinstance(r, Node):
            r = Leaf(r)
        return r

    def prepareDATE(self, string):
        print("PREPARE DATE:", string)
        return Date(*string.split('-'))

    def visitDate(self, ctx):
        nodes = self.visitChildren(ctx)
        print(nodes)

        return Date(*[node.content for node in nodes if node.content != '-'])

    def prepareCLOCK(self, string):
        print('PREPARE CLOCK', string)
        return NaiveClock(*string.split(':'))

    def prepareTIMESTAMP(self, string):
        packed_date, packed_clock = string.split('T')
        y, mnth = packed_date[:4], packed_date[4:6]
        mnth = int(mnth or 1)
        if mnth > 12:
            # It seems like a bug, but udunits supports months >12 in timestamps.
            # d = packed_date[5:]
            # mnth = int(packed_date[4:5])
            d = packed_date[6:]
        else:
            d = packed_date[6:]
        d = int(d or 1)


        # REF: https://github.com/Unidata/UDUNITS-2/blob/v2.2.27.6/lib/parser.y#L113-L126
        negative_hr = packed_clock[0] == '-'
        if packed_date[0] in ['-', '+']:
            packed_clock = packed_clock[1:]

        # NB: This is NOT what the grammar states, but is what udunits does.
        h, m, s = packed_clock[:2], packed_clock[2:4], packed_clock[4:6]

        h, m, s = int(h or 0), int(m or 0), int(s or 0)
        if negative_hr:
            h = -h

        node = Timestamp(Date(int(y), mnth, d), NaiveClock(h, m, s))
        return node

    def visitSigned_int(self, ctx):
        return self.visitAny_signed_number(ctx)

    def strip_whitespace(self, nodes):
        return [n for n in nodes if (isinstance(n, Node) and not (isinstance(n, Leaf) and n.content is None))]

    def visitJuxtaposed_multiplication(self, ctx):
        nodes = self.visitChildren(ctx)
        lhs, rhs = self.strip_whitespace(nodes)
        return BinaryOp('*', lhs, rhs)

    def visitPower_spec(self, ctx):
        nodes = self.visitChildren(ctx)
        print('NODES:', nodes)
        if isinstance(nodes, list):
            print("POWER!", nodes, ctx)
            last = nodes[-1]
            new = []
            # Walk the nodes backwards applying raise to each successivelyi.
            for node in nodes[:-1][::-1]:
                last = BinaryOp('^', node, last)
            nodes = last
#            if len(nodes) == 2:
#                nodes = BinaryOp('^', *nodes)
        return nodes

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

    def visitShift(self, ctx):
        nodes = self.visitChildren(ctx)
        [operand] = self.strip_whitespace(nodes)
        return operand

    def visitClock(self, ctx):
        nodes = self.visitChildren(ctx)
        print('TICK TOCK CLOCK:', nodes, type(nodes))
        if not isinstance(nodes.content, list):
            # Signed integer.
            nodes = Leaf([nodes])
        return nodes

#    def prepareClock(self, clock_nodes):

    def visitTimestamp(self, ctx):
        nodes = self.visitChildren(ctx)
        print('TIMESTAMP', nodes)
        print(type(nodes))
        #if isinstance(nodes, Leaf):
        #    nodes = Timestamp(*nodes.content)

        if not isinstance(nodes, Node):
            nodes = self.strip_whitespace(nodes)
            print('STRIPPED:', nodes)

            types = [type(n) for n in nodes]
            print('t:', types)

            if types == [Date, Leaf]:
                # DATE + packed_time
                return Timestamp(nodes[0], NaiveClock(nodes[1].content))
            elif types == [Date, NaiveClock]:
                return Timestamp(*nodes)
            elif types == [Date, NaiveClock, Leaf]:
                return Timestamp(*nodes)
            elif types == [Date, NaiveClock, NaiveClock]:
                raise RuntimeError('NEED TO IMPLEMENT CLOCK SUBTRACT')
            elif types == [Date, Leaf, NaiveClock]:
                raise RuntimeError('NEED TO IMPLEMENT CLOCK SUBTRACT')
            elif types == [Date, Leaf, Leaf]:
                hour = nodes[1].content
                hour = NaiveClock(hour)
                return Timestamp(nodes[0], hour, nodes[1])

        return nodes

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
