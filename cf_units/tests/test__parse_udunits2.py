import pytest
import cf_units
from cf_units._parse_udunits2 import normalize, parse

testdata = [
    '',
    '1',
    '12',
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
    '.1e2.2',
    '2e',  # <- TODO: Assert this isn't 2e1, but is infact the unit e *2
    'm',
    'meter',
    '1 2 3',
    '1 -2 -3',
    '1m',
    '1*m',
    'm·m',
    '1 m',
    '1   m',
    'm -1',
    'm -1.2',
    'm 1',
    'm 1.2',
    'm-+2',
    'm--4',

    # TODO: add some tests with brackets.
    'm(2.3)',
    'm(2.3m)',


    'm/2',
    'm1',
    'm m',
    'm2',
    'm+2',
    'm¹',
    'm²',
    'm³',
    '2⁴',  # NOTE: Udunits can't do m⁴ for some reason. Bug?
    '2⁵',
    '2⁴²',
    '3⁻²',
    'm2 s2',
    'm^2*s^2',
   
    '1-2',
    '1-2-3',  # nb. looks a bit like a date, but it isn't!
    'm-1',
    'm^2',
    'm^+2',
    'm^-1',
    'm.2',  # This is 2*m
    'm.+2', # 2*m
    'm.2.4', # This is 2.4 * m
    'm0.2', # But this is 2 m^0
    'm2.5', # And this is 5m^2

# TODO: Test divide
#    'm per 2',
#    'm / 2',


    'm@10',
    'm @10',
    'm @ 10',
    'm@ 10',
    'm from2',
    'm from2e-1',

    's from 1990',
    'minutes since 1990',
    'hour@1990',
    'hours from 1990-1',
    'hours from 1990-1-1',
    'hours from 1990-1-1 0',
    'hours from 1990-1-1 0:1:1',
    'hours from 1990-1-1 0:0:1 +2',
    's since 1990-1-2+5:2:2',
    's since 1990-1-2+5:2',
    's since 1990-1-2 5 6:0',  # Undocumented packed_clock format (date + (t1 - t2)).
    's since 19900102T5',  # Packed format (undocumented?)
    's since 199022T1',  # UGLY! (bug?).


    's since 1990 +2:0:2.9',
    's since 1990-2T1',
    'hours from 1990-1-1 -19:4:2',
    'hours from 1990-1-1 3+1',

    'seconds from 1990-1-1 0:0:0 +2550',
    's since 1990-1-2+5:2:2',
]

invalid = [
    '1 * m',
    'm--m',
    '-m',
    '.1e2.',
    'm+-1',
    '--1',
    '+-1',
    '--3.1',
    '$',
    '£',  # TODO: What if udunits has this defined in its XML, does it work?
    
    #        'hours from 1990-1-1 0:1:60',
    #    'hours from 1990-0-0 0:0:0',
]


not_udunits = [
    ['foo', 'foo'],
    ['mfrom1', 'mfrom^1'],
    ['m⁴', 'm^4'],  # udunits bug.
    ['2¹²³⁴⁵⁶⁷⁸⁹⁰', '2^1234567890'],
]

udunits_bugs = [
        '2¹²³⁴⁵⁶⁷⁸⁹⁰',
        'm⁻²'
]

not_allowed = [
    'hours from 1990-1-1 -20:4:18 +2',
    'm++2',
    'm s^(-1)',
]

known_issues = [
    # [unit_str, what_we_SHOULD_get_or_which_exception_we_CURRENTLY_get]
    ['m--2--3', SyntaxError], # -2 * -3 * m

    ['s since +1990 +2:0:2.9', SyntaxError], # Disabled due to crazy results from UDUNITS.
    ['s since -1990 +2:0:2.9', SyntaxError],  # Disabled due to crazy results from UDUNITS.

]

not_done = [
    'm--1',  # TODO: CANT FIGURE OUT WHAT THIS IS SUPPOSED TO BE!
    'µ°F·Ω⁻¹',  # This is in the docs, so let's at least support that one!
    ]


expansions = [
    ['01', '1']
]


@pytest.mark.parametrize("_, unit_str", enumerate(invalid))
def test_invalid_units(_, unit_str):
    try:
        cf_units.Unit(unit_str)
        cf_valid = True
    except ValueError:
        cf_valid = False

    # Double check that udunits2 can't parse this.
    assert cf_valid is False

    try:
        unit_expr = normalize(unit_str)
        can_parse = True
    except SyntaxError:
        can_parse = False

    # Now confirm that we couldn't parse this either.
    assert can_parse == False, 'Parser unexpectedly able to deal with {}'.format(unit_str)


@pytest.mark.parametrize("_, unit_str, expected", [[i, s, e] for i, (s, e) in enumerate(not_udunits)])
def test_invalid_in_udunits_but_still_parses(_, unit_str, expected):
    #    unit_str, expected = unit_str_and_expected
    try:
        cf_units.Unit(unit_str)
        cf_valid = True
    except ValueError:
        cf_valid = False

    # Double check that udunits2 can't parse this.
    assert cf_valid is False

    try:
        unit_expr = normalize(unit_str)
        can_parse = True
    except SyntaxError:
        can_parse = False

    # Now confirm that we could.
    assert can_parse == True
    assert unit_expr == expected


@pytest.mark.parametrize("_, unit_str, expected", [[i, u, e] for i, (u, e) in enumerate(known_issues)])
def test_known_issues(_, unit_str, expected):
    # Unfortunately the grammar is not perfect.
    # These are the cases that don't work yet.

    # Get the udunits symbolic form for the raw unit.
    raw_symbol = cf_units.Unit(unit_str).symbol

    if isinstance(expected, type) and issubclass(expected, Exception):
        with pytest.raises(SyntaxError):
            unit_expr = normalize(unit_str)
    else:
        unit_expr = normalize(unit_str)
        assert unit_expr != expected


@pytest.mark.parametrize("_, unit_str", enumerate(not_allowed))
def test_not_allowed(_, unit_str):
    # Get the udunits symbolic form for the raw unit.

    with pytest.raises(ValueError):
        raw_symbol = cf_units.Unit(unit_str).symbol

    with pytest.raises(SyntaxError):
        unit_expr = normalize(unit_str)


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

@pytest.mark.parametrize("_, unit_str, expected", [[i, a, b] for i, (a, b) in enumerate([
    ['1.2', '1.2'],
    ['m.m', 'm*m'],
    ['m m', 'm*m'],
    ['m -1.2', 'm*-1.2'],
    ['km.2', 'km*2'],
])])
def test_product_spec(_, unit_str, expected):
    n = str(parse(unit_str, root='product_spec'))
    assert n == expected


@pytest.mark.parametrize("_, unit_str, expected", [[i, a, b] for i, (a, b) in enumerate([
    ['2.3', '2.3'],
    ['m2', 'm^2'],
    ['2m', '2'],  # <- no product should be happening. This is the right behaviour!
    ['m²', 'm^2'],
    ['m**2', 'm^2'],
    ['m-2', 'm^-2'],
    ['m.m', 'm']  # <- no product happending, and no EOL in the rule. This is the right behaviour!
])])
def test_power_spec(_, unit_str, expected):
    n = str(parse(unit_str, root='power_spec'))
    assert n == expected


@pytest.mark.parametrize("_, unit_str, expected", [[i, a, b] for i, (a, b) in enumerate([
    ['1.2', '1.2'],
    ['m', 'm'],
    ['+1e12', '+1e12'],
])])
def test_basic_spec(_, unit_str, expected):
    n = str(parse(unit_str, root='basic_spec'))
    assert n == expected

