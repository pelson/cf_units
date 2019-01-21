import pytest
import cf_units
from cf_units._parse_udunits2 import normalize

testdata = [
    '',
    '1',
    '1.2',
    '+1',
    '+1.2',
    '-1',
    '-1.2',
    '-1.2e0',
    '2e6',
    '2e-6',
    '2.e-6',
    '.1e2',
    '2e',  # <- TODO: Assert this isn't 2e1, but is infact the unit e *2
    'm',
    'meter',
    '1m',
    '1*m',
    '1 m',
    '1   m',
    'm1',
    'm2',
    'm+2',
    'm-1',
    'm^2',
    'm^+2',
    'm^-1',

]

invalid = [
    '-m',
    '.1e2.',
    'm+-1',
]

not_done = [
    'm--1',  # TODO: CANT FIGURE OUT WHAT THIS IS SUPPOSED TO BE!

    'm¹',
    'm²',
    'm³',
]

@pytest.mark.parametrize("_, unit_str", enumerate(testdata))
def test_normed_unit(_, unit_str):
    # nb: The "_" argument allows an easier interface for seeing which
    # test was being run.

    # TODO: Take care that the Unit class isn't getting in the
    # way (e.g. its custom definitions).

    # Get the udunits symbolic form for the raw unit.
    raw_symbol = cf_units.Unit(unit_str).symbol

    # Now get the parsed form of the unit, and then convert that to
    # symbolic form. The two should match.
    unit_expr = normalize(unit_str)
    parsed_expr_symbol = cf_units.Unit(unit_expr).symbol

    # Whilst the symbolic form from udunits is ugly, it *is* acurate,
    # so check that the two represent the same unit.
    assert raw_symbol == parsed_expr_symbol
