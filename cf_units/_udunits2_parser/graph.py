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


class Node:
    """
    Represents a node in an expression graph.

    """
    def __init__(self, **kwargs):
        self._attrs = kwargs

    def children(self):
        """
        Return the children of this node.

        """
        # Since this is py>=36, the order of the attributes is well defined.
        return self.attrs.values()

    def __getattr__(self, name):
        # Allow this to raise KeyError if missing.
        return self._attrs[name]

    def _repr_ctx(self):
        # Return a dictionary that is useful for passing to string.format.
        kwargs = ', '.join(
            '{}={}'.format(key, value)
            for key, value in self._attrs.items())
        return dict(cls_name=self.__class__.__name__, kwargs=kwargs)

    def __repr__(self):
        return '{cls_name}({kwargs})'.format(**self._repr_ctx())


class Root(Node):
    """
    The first node in the expression graph.

    """
    # TODO: Is this being used?
    def __init__(self, *units):
        self.units = units

    def children(self):
        return self.units

    def __str__(self):
        return ' '.join(str(u) for u in self.units)


class Terminal(Node):
    """
    A generic terminal node in an expression graph.

    """
    def __init__(self, content):
        super().__init__(content=content)

    def children(self):
        return []

    def __str__(self):
        return '{}'.format(self.content)


class Operand(Terminal):
    pass


class Number(Terminal):
    pass


class Identifier(Terminal):
    """The unit itself (e.g. meters, m, km and π)"""
    pass


class BinaryOp(Node):
    def __init__(self, op, lhs, rhs):
        super().__init__(lhs=lhs, op=op, rhs=rhs)

    def __str__(self):
        return f'{self.lhs}{self.op}{self.rhs}'


class Shift(Node):
    def __init__(self, unit, shift_from):
        # The product unit to be shifted.
        super().__init__(unit=unit, shift_from=shift_from)

    def __str__(self):
        return f'({self.unit} @ {self.shift_from})'


class Timestamp(Node):
    def __init__(self, date, clock, tz_offset=0):
        super().__init__(date=date, clock=clock, tz_offset=tz_offset)

    def __str__(self):
        return f'{self.date} {self.clock} {self.tz_offset}'


class NaiveClock(Node):
    def __init__(self, hour=0, minute=0, second=0):
        # A timezone unaware timestamp.
        super().__init__(hour=hour, minute=minute, second=second)

    def __str__(self):
        clock = f'{self.hour}:{self.minute}'
        if self.second != 0:
            clock += f':{self.second}'
        return clock


class Date(Node):
    def __init__(self, year, month=1, day=1):
        super().__init__(year=year, month=month, day=day)

    def __str__(self):
        return f'{self.year}-{self.month}-{self.day}'


class PackedDate(Node):
    # Udunits supports integers that look a bit like YYYYMMDD.
    # Problem is, they are also allowed to exceed, so 1990234 is actually
    #    Y: 1990 + M//12, M: 23%12, D: 4 + the number of days that adding
    #    extra months requires.
    # Furthermore, +1990 miraculously reaches y: 198, m: 12, d: 01...
    # 
    # Rather than try to reverse engineer this, let's encapsualte it and
    # pass it on to UDUNITS to handle. Sorry if you are looking for this
    # value to be decoded here.
    #
    def __init__(self, datestamp):
        super().__init__(datestamp=datestamp)

    def __str__(self):
        return f'{self.datestamp}'
