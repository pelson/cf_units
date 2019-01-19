# Generates the python code based on the udunits2.g4 specification.

# Requires the antlr jar.
java -jar antlr-4.7.2-complete.jar -Dlanguage=Python3 -visitor -no-listener udunits2.g4
