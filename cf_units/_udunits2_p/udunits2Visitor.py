# Generated from udunits2.g4 by ANTLR 4.7.2
from antlr4 import *
if __name__ is not None and "." in __name__:
    from .udunits2Parser import udunits2Parser
else:
    from udunits2Parser import udunits2Parser

# This class defines a complete generic visitor for a parse tree produced by udunits2Parser.

class udunits2Visitor(ParseTreeVisitor):

    # Visit a parse tree produced by udunits2Parser#unit_spec.
    def visitUnit_spec(self, ctx:udunits2Parser.Unit_specContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by udunits2Parser#shift_spec.
    def visitShift_spec(self, ctx:udunits2Parser.Shift_specContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by udunits2Parser#product_spec.
    def visitProduct_spec(self, ctx:udunits2Parser.Product_specContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by udunits2Parser#power_spec.
    def visitPower_spec(self, ctx:udunits2Parser.Power_specContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by udunits2Parser#basic_spec.
    def visitBasic_spec(self, ctx:udunits2Parser.Basic_specContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by udunits2Parser#id_.
    def visitId_(self, ctx:udunits2Parser.Id_Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by udunits2Parser#basic_unit.
    def visitBasic_unit(self, ctx:udunits2Parser.Basic_unitContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by udunits2Parser#base_unit.
    def visitBase_unit(self, ctx:udunits2Parser.Base_unitContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by udunits2Parser#number.
    def visitNumber(self, ctx:udunits2Parser.NumberContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by udunits2Parser#shift.
    def visitShift(self, ctx:udunits2Parser.ShiftContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by udunits2Parser#multiply.
    def visitMultiply(self, ctx:udunits2Parser.MultiplyContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by udunits2Parser#exponent_unicode.
    def visitExponent_unicode(self, ctx:udunits2Parser.Exponent_unicodeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by udunits2Parser#exponent.
    def visitExponent(self, ctx:udunits2Parser.ExponentContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by udunits2Parser#negative_exponent.
    def visitNegative_exponent(self, ctx:udunits2Parser.Negative_exponentContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by udunits2Parser#divide.
    def visitDivide(self, ctx:udunits2Parser.DivideContext):
        return self.visitChildren(ctx)



del udunits2Parser