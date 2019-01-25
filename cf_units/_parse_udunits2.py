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
from ._udunits2_p.udunits2ParserVisitor import udunits2ParserVisitor as LabeledExprVisitor


class Node:
    """
    Represents a node in an expression graph.

    """
    def children(self):
        """
        Return the children of this node.

        """
        return []

    def __repr__(self):
        return '<{}>'.format(self)



class Root(Node):
    """
    The first node in the expression graph.

    """
    def __init__(self, *units):
        self.units = units

    def children(self):
        return self.units

    def __str__(self):
        return ' '.join(str(u) for u in self.units)


class Leaf(Node):
    """
    A generic terminal node in an expression graph.

    """
    def __init__(self, content):
        self.content = content

    def __str__(self):
        return '{}'.format(self.content)


class Operand(Leaf):
    pass


class Number(Leaf):
    pass


class Identifier(Leaf):
    """The unit itself (e.g. meters, m, km and π)"""
    pass


class BinaryOp(Node):
    def __init__(self, op, lhs, rhs):
        self.lhs = lhs
        self.rhs = rhs
        self.op = op

    def children(self):
        return self.lhs, self.op, self.rhs

    def __str__(self):
        return '{self.lhs}{self.op}{self.rhs}'.format(self=self)


class Shift(Node):
    def __init__(self, unit, shift_from):
        self.unit = unit  # AKA Gregorian in the udunits2 codebase.
        self.shift_from = shift_from

    def children(self):
        return self.unit, self.shift_from

    def __str__(self):
        return f'({self.unit} @ {self.shift_from})'

class Timestamp(Node):
    def __init__(self, date, clock, tz_offset=0):
        self.date = date
        self.clock = clock
        self.tz_offset = tz_offset

    def children(self):
        return self.date, self.clock, self.tz_offset

    def __str__(self):
        return f'{self.date} {self.clock} {self.tz_offset}'


class NaiveClock(Node):
    def __init__(self, hour=0, minute=0, second=0):
        self.hour = hour
        self.minute = minute
        self.second = second

    def children(self):
        return self.hour, self.minute, self.second

    def __str__(self):
        if self.second != 0:
            return f'{self.hour}:{self.minute}:{self.second}'
        else:
            return f'{self.hour}:{self.minute}'


class NegativeNaiveClock(NaiveClock):
    # Inheritance makes checks in the codebase for approximate types easier.
    # There is test coverage if you choose to break this inheritance in the future.
    def __init__(self, clock):
        # NOTE: The implementation of this can be found at
        # https://github.com/Unidata/UDUNITS-2/blob/v2.2.27.6/lib/scanner.l#L49-L71
        self.clock = clock

    def children(self):
        return (self.clock, )

    def __str__(self):
        return f'-{self.clock}'


class Date(Node):
    def __init__(self, year, month=1, day=1):
        self.year = year
        self.month = month
        self.day = day

    def children(self):
        return self.year, month, self.day

    def __str__(self):
        return f'{self.year}-{self.month}-{self.day}'


class PackedDate(Date):
    # Udunits supports integers that look a bit like YYYYMMDD. Problem is, they are also allowed to exceed, so
    # 1990234 is actually Y: 1990 + M//12, M: 23%12, D: 4 + the number of days that adding extra months requires.
    # Additionally, +1990 miraculously reaches y: 198, m: 12, d: 01

    # Rather than try to reverse engineer this, let's encapsualte it and pass it on to UDUNITS if we possibly can.
    def __init__(self, datestamp):
        self.datestamp = datestamp

    def children(self):
        return (self.datestamp,)

    def __str__(self):
        return f'{self.datestamp}'


class ExprVisitor(LabeledExprVisitor):
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

        symbol_idx = ctx.symbol.type
        if symbol_idx < 0:
            # EOF
            pass
        else:
            lexer = ctx.symbol.source[0]

            import unicodedata
            consumers = {lexer.INT: lambda string: Number(int(string)),
                         lexer.SIGNED_INT: lambda string: Number(int(string)),
                         lexer.WS: lambda n: None,
                         lexer.ID: Identifier,
                         # Convert unicode to compatibility form
                         lexer.UNICODE_EXPONENT: lambda n: int(unicodedata.normalize('NFKC', n).replace('−', '-')),
                         #                          lexer.MINUS: Operand,
                         lexer.DIVIDE: Operand,
                         lexer.MULTIPLY: lambda op: Operand('*'),
                         lexer.RAISE: Operand,
                         lexer.SHIFT_OP: str,
                         lexer.HOUR_MINUTE_SECOND: self.prepareCLOCK,  #lambda arg: arg.split(':'), #lambda *args: ' '.join(args),
                         lexer.HOUR_MINUTE: self.prepareCLOCK,  #lambda arg: arg.split(':'), #lambda *args: ' '.join(args),
                         lexer.TIMESTAMP: self.prepareTIMESTAMP,
                         lexer.PERIOD: str,
                         lexer.E_POWER: str,
                         lexer.DATE: lambda arg: Date(*arg.strip().rsplit('-', 2)),  # TODO: Handle -1-3
                         lexer.OPEN_PAREN: str,
                         lexer.CLOSE_PAREN: str,
                         #                          lexer.SIGNED_INT: str,
                         }
            if symbol_idx in consumers:
                r = consumers[symbol_idx](r)
            else:
                print('UNHANDLED TERMINAL:', repr(r))

        if not isinstance(r, Node):
            r = Leaf(r)
        return r

    def visitDate(self, ctx):
        nodes = self.visitChildren(ctx)
        return Date(*[node.content for node in nodes if node.content != '-'])

    def prepareCLOCK(self, string):
        return NaiveClock(*string.split(':'))

    def prepareTIMESTAMP(self, string):
        packed_date, packed_clock = string.split('T')


        # https://github.com/Unidata/UDUNITS-2/blob/v2.2.27.6/lib/scanner.l#L243-L252
        packed_date = PackedDate(packed_date)

        # REF: https://github.com/Unidata/UDUNITS-2/blob/v2.2.27.6/lib/parser.y#L113-L126
        negative_hr = packed_clock[0] == '-'

        # NB: This is NOT what the grammar states, but is what udunits appears to do.
        h, m, s = packed_clock[:2], packed_clock[2:4], packed_clock[4:6]

        h, m, s = int(h or 0), int(m or 0), int(s or 0)
        if negative_hr:
            h = -h

        node = Timestamp(packed_date, NaiveClock(h, m, s))
        return node

    def visitBasic_spec(self, ctx):
        nodes = self.visitChildren(ctx)
        if isinstance(nodes, list):
            open_p, node, close_p = nodes
            assert open_p.content == '('
            assert close_p.content == ')'
        else:
            node = nodes
        return node
    
    def strip_whitespace(self, nodes):
        return [n for n in nodes if (isinstance(n, Node) and not (isinstance(n, Leaf) and n.content is None))]


    def visitProduct(self, ctx):
        # UDUNITS grammar makes no parse distinction for these types,
        # so we have to do the grunt work here.
        nodes = self.visitChildren(ctx)
        op = Operand('*')
        if isinstance(nodes, Node):
            node = nodes
        else:
            nodes = self.strip_whitespace(nodes)

            last = nodes[-1]

            # Walk the nodes backwards applying the operand to each node successively.
            # i.e. 1*2*3*4*5 = 1*(2*(3*(4*5)))
            for node in nodes[:-1][::-1]:
                if isinstance(node, Operand):
                    op = node
                else:
                    last = BinaryOp(op, node, last)
                    op = Operand('*')
            node = last
        return node

    def visitTimestamp(self, ctx):
        nodes = self.visitChildren(ctx)
        #if isinstance(nodes, Leaf):
        #    nodes = Timestamp(*nodes.content)

        if not isinstance(nodes, Node):
            nodes = self.strip_whitespace(nodes)

            types = [type(n) for n in nodes]

            def matches(specs):
                if len(specs) != len(types):
                    return False

                return all(
                    issubclass(node_type, spec)
                    for spec, node_type in zip(specs, types)) 

            if matches([Date, Leaf]):
                # DATE + packed_time
                return Timestamp(nodes[0], NaiveClock(nodes[1].content))
            elif matches([Leaf, NaiveClock]):
                # Int Clock
                return Timestamp(Date(nodes[0]), nodes[1])
            elif matches([Date, NaiveClock]):
                return Timestamp(*nodes)
            elif matches([Date, NaiveClock, Leaf]):
                return Timestamp(*nodes)
            elif matches([Date, NaiveClock, NaiveClock]) or matches([Date, Leaf, NaiveClock]):
                # https://github.com/Unidata/UDUNITS-2/blob/v2.2.27.6/lib/parser.y#L442
                # Ref
                return Timestamp(nodes[0], nodes[1], nodes[2])
            elif matches([Date, Leaf, Leaf]):
                # Date + packed_clock + tz_offset
                hour = nodes[1].content
                hour = NaiveClock(hour)
                return Timestamp(nodes[0], hour, nodes[2])
            else:
                for node in nodes:
                    print(node)
                raise RuntimeError('Unhandled timestamp form {}.'.format(types))
        return nodes

    def visitPower(self, ctx):
        nodes = self.visitChildren(ctx)
        if isinstance(nodes, Node):
            node = nodes
        elif len(nodes) == 2:
            node = BinaryOp(Operand('^'), nodes[0], nodes[1])
        elif len(nodes) == 3:
            assert nodes[1].content == '^'
            node = BinaryOp(Operand('^'), nodes[0], nodes[2])
        return node

    def visitShift_spec(self, ctx):
        nodes = self.visitChildren(ctx)
        if not isinstance(nodes, Node):
            nodes = Shift(nodes[0], nodes[2])
        return nodes

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
        return [repr_walk_ast(n) for n in node.children()]
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


def parse(unit_str, root='unit_spec'):
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
        tree = getattr(parser2, root)()

        # NOTE, because of the parser._listeners error handler, this only works if we have a valid grammar in the first place.
        print()
        for token in stream2.tokens:
            if token.text != '<EOF>':
                token_type_idx = token.type 
                rule = token_lookup[token_type_idx]
                print("%s: %s" % (token.text, rule))

    # The top level concept.
    tree = getattr(parser, root)()

    visitor = ExprVisitor()
    return visitor.visit(tree)


def main(argv):
    ast = parse(argv[1])
    print('AST:', repr(repr_walk_ast(ast)))
    print(ast)


if __name__ == '__main__':
    import sys
    main(sys.argv)
