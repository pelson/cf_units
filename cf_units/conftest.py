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

"""
Configure pytest to ignore python 3 files in python 2.

"""
import os.path
import glob
import six


if six.PY2:
    here = os.path.dirname(__file__)

    # Files under cf_units/_udunits2_parser/parser/ are all autogenerated
    # (and are py3 only).
    all_parse_py = glob.glob(
        os.path.join(here, '_udunits2_parser', 'parser', '*.py'))

    # Files under cf_units/_udunits2_parser are python3 *only*.
    all_compiled_parse_py = glob.glob(
        os.path.join(here, '_udunits2_parser', '*.py'))

    # Files under cf_units/tests/integration/parse are python3 *only*.
    parse_test_files = glob.glob(
        os.path.join(here, 'tests', 'integration', 'parse', '*.py'))

    # collect_ignore is the special variable that pytest reads to
    # indicate which files should be ignored (and not even imported).
    # See also https://docs.pytest.org/en/latest/example/pythoncollection.html
    collect_ignore = (list(all_parse_py) +
                      list(all_compiled_parse_py) +
                      list(parse_test_files))
