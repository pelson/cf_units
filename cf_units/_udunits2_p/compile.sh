# Generates the python code based on the udunits2.g4 specification.

# You might be interested in running this script whenever you change
# the grammar file, in which case try "echo udunits2.g4 | entr -c ./compile.sh" ;)

# Requires the antlr jar.
java -jar antlr-4.7.2-complete.jar -Dlanguage=Python3 -visitor -no-listener udunits2.g4
