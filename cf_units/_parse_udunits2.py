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


from ._udunits2_parser import graph


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
            consumers = {lexer.INT: lambda string: graph.Number(int(string)),
                         lexer.SIGNED_INT: lambda string: graph.Number(int(string)),
                         lexer.WS: lambda n: None,
                         lexer.ID: graph.Identifier,
                         # Convert unicode to compatibility form
                         lexer.UNICODE_EXPONENT: lambda n: int(unicodedata.normalize('NFKC', n).replace('−', '-')),
                         #                          lexer.MINUS: graph.Operand,
                         lexer.DIVIDE: graph.Operand,
                         lexer.MULTIPLY: lambda op: graph.Operand('*'),
                         lexer.RAISE: graph.Operand,
                         lexer.SHIFT_OP: str,
                         lexer.HOUR_MINUTE_SECOND: self.prepareCLOCK,  #lambda arg: arg.split(':'), #lambda *args: ' '.join(args),
                         lexer.HOUR_MINUTE: self.prepareCLOCK,  #lambda arg: arg.split(':'), #lambda *args: ' '.join(args),
                         lexer.TIMESTAMP: self.prepareTIMESTAMP,
                         lexer.PERIOD: str,
                         lexer.E_POWER: str,
                         lexer.DATE: lambda arg: graph.Date(*arg.strip().rsplit('-', 2)),  # TODO: Handle -1-3
                         lexer.OPEN_PAREN: str,
                         lexer.CLOSE_PAREN: str,
                         #                          lexer.SIGNED_INT: str,
                         }
            if symbol_idx in consumers:
                r = consumers[symbol_idx](r)
            else:
                print('UNHANDLED TERMINAL:', repr(r))

        if not isinstance(r, graph.Node):
            r = graph.Terminal(r)
        return r

    def visitDate(self, ctx):
        nodes = self.visitChildren(ctx)
        return graph.Date(*[node.content for node in nodes if node.content != '-'])

    def prepareCLOCK(self, string):
        return graph.NaiveClock(*string.split(':'))

    def prepareTIMESTAMP(self, string):
        packed_date, packed_clock = string.split('T')


        # https://github.com/Unidata/UDUNITS-2/blob/v2.2.27.6/lib/scanner.l#L243-L252
        packed_date = graph.PackedDate(packed_date)

        # REF: https://github.com/Unidata/UDUNITS-2/blob/v2.2.27.6/lib/parser.y#L113-L126
        negative_hr = packed_clock[0] == '-'

        # NB: This is NOT what the grammar states, but is what udunits appears to do.
        h, m, s = packed_clock[:2], packed_clock[2:4], packed_clock[4:6]

        h, m, s = int(h or 0), int(m or 0), int(s or 0)
        if negative_hr:
            h = -h

        node = graph.Timestamp(packed_date, graph.NaiveClock(h, m, s))
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
        return [n for n in nodes if (isinstance(n, graph.Node) and not (isinstance(n, graph.Terminal) and n.content is None))]


    def visitProduct(self, ctx):
        # UDUNITS grammar makes no parse distinction for these types,
        # so we have to do the grunt work here.
        nodes = self.visitChildren(ctx)
        op = graph.Operand('*')
        if isinstance(nodes, graph.Node):
            node = nodes
        else:
            nodes = self.strip_whitespace(nodes)

            last = nodes[-1]

            # Walk the nodes backwards applying the operand to each node successively.
            # i.e. 1*2*3*4*5 = 1*(2*(3*(4*5)))
            for node in nodes[:-1][::-1]:
                if isinstance(node, graph.Operand):
                    op = node
                else:
                    last = graph.BinaryOp(op, node, last)
                    op = graph.Operand('*')
            node = last
        return node

    def visitTimestamp(self, ctx):
        nodes = self.visitChildren(ctx)
        #if isinstance(nodes, graph.Terminal):
        #    nodes = graph.Timestamp(*nodes.content)

        if not isinstance(nodes, graph.Node):
            nodes = self.strip_whitespace(nodes)

            types = [type(n) for n in nodes]

            def matches(specs):
                if len(specs) != len(types):
                    return False

                return all(
                    issubclass(node_type, spec)
                    for spec, node_type in zip(specs, types)) 

            if matches([graph.Date, graph.Terminal]):
                # DATE + packed_time
                return graph.Timestamp(nodes[0], graph.NaiveClock(nodes[1].content))
            elif matches([graph.Terminal, graph.NaiveClock]):
                # Int Clock
                return graph.Timestamp(graph.Date(nodes[0]), nodes[1])
            elif matches([graph.Date, graph.NaiveClock]):
                return graph.Timestamp(*nodes)
            elif matches([graph.Date, graph.NaiveClock, graph.Terminal]):
                return graph.Timestamp(*nodes)
            elif matches([graph.Date, graph.NaiveClock, graph.NaiveClock]) or matches([graph.Date, graph.Terminal, graph.NaiveClock]):
                # https://github.com/Unidata/UDUNITS-2/blob/v2.2.27.6/lib/parser.y#L442
                # Ref
                return graph.Timestamp(nodes[0], nodes[1], nodes[2])
            elif matches([graph.Date, graph.Terminal, graph.Terminal]):
                # graph.Date + packed_clock + tz_offset
                hour = nodes[1].content
                hour = graph.NaiveClock(hour)
                return graph.Timestamp(nodes[0], hour, nodes[2])
            else:
                for node in nodes:
                    print(node)
                raise RuntimeError('Unhandled timestamp form {}.'.format(types))
        return nodes

    def visitPower(self, ctx):
        nodes = self.visitChildren(ctx)
        if isinstance(nodes, graph.Node):
            node = nodes
        elif len(nodes) == 2:
            node = graph.BinaryOp(graph.Operand('^'), nodes[0], nodes[1])
        elif len(nodes) == 3:
            assert nodes[1].content == '^'
            node = graph.BinaryOp(graph.Operand('^'), nodes[0], nodes[2])
        return node

    def visitShift_spec(self, ctx):
        nodes = self.visitChildren(ctx)
        if not isinstance(nodes, graph.Node):
            nodes = graph.Shift(nodes[0], nodes[2])
        return nodes

    def visitUnit_spec(self, ctx):
        nodes = self.visitChildren(ctx)
        
        # Drop the EOF
        if isinstance(nodes, graph.Node):
            node = graph.Root()
            assert str(nodes) == '<EOF>'
        else:
            assert len(nodes) == 2
            assert isinstance(nodes, list)
            if isinstance(nodes[0], graph.Node):
                node = graph.Root(nodes[0])
            else:
                node = graph.Root(*nodes[0])
        return node


def repr_walk_ast(node):
    if isinstance(node, graph.Terminal):
        return str(node)
    elif isinstance(node, graph.BinaryOp):
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
