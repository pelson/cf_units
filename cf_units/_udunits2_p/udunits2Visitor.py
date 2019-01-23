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


    # Visit a parse tree produced by udunits2Parser#div.
    def visitDiv(self, ctx:udunits2Parser.DivContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by udunits2Parser#power_spec.
    def visitPower_spec(self, ctx:udunits2Parser.Power_specContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by udunits2Parser#basic_spec.
    def visitBasic_spec(self, ctx:udunits2Parser.Basic_specContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by udunits2Parser#basic_unit.
    def visitBasic_unit(self, ctx:udunits2Parser.Basic_unitContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by udunits2Parser#base_unit.
    def visitBase_unit(self, ctx:udunits2Parser.Base_unitContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by udunits2Parser#sci_number.
    def visitSci_number(self, ctx:udunits2Parser.Sci_numberContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by udunits2Parser#signed_int.
    def visitSigned_int(self, ctx:udunits2Parser.Signed_intContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by udunits2Parser#juxtaposed_multiplication.
    def visitJuxtaposed_multiplication(self, ctx:udunits2Parser.Juxtaposed_multiplicationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by udunits2Parser#divide.
    def visitDivide(self, ctx:udunits2Parser.DivideContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by udunits2Parser#sign.
    def visitSign(self, ctx:udunits2Parser.SignContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by udunits2Parser#any_signed_number.
    def visitAny_signed_number(self, ctx:udunits2Parser.Any_signed_numberContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by udunits2Parser#any_unsigned_number.
    def visitAny_unsigned_number(self, ctx:udunits2Parser.Any_unsigned_numberContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by udunits2Parser#float_t.
    def visitFloat_t(self, ctx:udunits2Parser.Float_tContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by udunits2Parser#timestamp.
    def visitTimestamp(self, ctx:udunits2Parser.TimestampContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by udunits2Parser#date.
    def visitDate(self, ctx:udunits2Parser.DateContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by udunits2Parser#signed_clock.
    def visitSigned_clock(self, ctx:udunits2Parser.Signed_clockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by udunits2Parser#signed_hour_minute.
    def visitSigned_hour_minute(self, ctx:udunits2Parser.Signed_hour_minuteContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by udunits2Parser#hour_minute.
    def visitHour_minute(self, ctx:udunits2Parser.Hour_minuteContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by udunits2Parser#clock.
    def visitClock(self, ctx:udunits2Parser.ClockContext):
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


    # Visit a parse tree produced by udunits2Parser#juxtaposed_raise.
    def visitJuxtaposed_raise(self, ctx:udunits2Parser.Juxtaposed_raiseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by udunits2Parser#negative_exponent.
    def visitNegative_exponent(self, ctx:udunits2Parser.Negative_exponentContext):
        return self.visitChildren(ctx)



del udunits2Parser