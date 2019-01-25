parser grammar udunits2Parser;

options { tokenVocab=udunits2Lexer; }

unit_spec:
    shift_spec? EOF  // Zero or one "shift_spec", followed by the end of the input.
;

shift_spec:
    product
    | product shift sci_number
    | product shift timestamp
;


product:
    power
    | product power
    | product MULTIPLY power
    | product DIVIDE power
    | product WS+ power
    // NO WHITESPACE...
;

multi_product_old:
    // product_spec // (WS? product_spec)*?
    product_spec
   | 
    (product_spec (MULTIPLY power_spec)?)  // m.m, but not "m m". Space multiplication occurs in product_spec.
;

product_spec:  
    disabled
;

//      (base_unit PERIOD sci_number) // km.2 === 2*km (i.e. this trumps km * 0.2)
//       |

disabled:
      (
       (multi_power)
       | (multi_power multiply power_spec) // km*2
       | (multi_power DIVIDE power_spec)  // km/2
      )+ //(WS? product_spec)*  // "km.2 2km .2s" === "4km² 0.2s" 
;

power:
    basic_spec any_int   // Note: m2 should be matched before m for m2 vs m*2.
    | basic_spec
    | basic_spec RAISE any_int
    | basic_spec UNICODE_EXPONENT

//    (basic_spec RAISE signed_int)  //km^2, km^-1, km^+2
//    | ((base_unit | signed_int) signed_int)    // m2, m+2, s-1, 1+2, 2-3
//    | (basic_spec UNICODE_EXPONENT)  // m²
;

multi_power:
    power_spec+ // TESTING
;

power_spec:    // Examples include: m+2, m-2, m3, 2^3
    (
    exponent
    | basic_spec
      | exponent
    ) //  signed_int?   // We allow only one further power, so 2+3+4 == (2^3)*4
;

basic_spec:
       base_unit
       | '(' shift_spec ')'
//       | LOGREF product_spec ')'
       | sci_number | signed_int
;


basic_unit: base_unit;
base_unit: ID;


sci_number:
    float_t | (sign? INT) | SIGNED_INT
;

signed_int:
    SIGNED_INT | INT
;
any_int: 
    SIGNED_INT | INT
;

sign: (PLUS);  // | MINUS);

any_signed_number:
    sign? any_unsigned_number
;

any_unsigned_number:
    float_t | any_int
;

// Float is not a parser rule as the context is important (e.g. m2.3 === m^2 * 3 in udunits2)
float_t:
   FLOAT
;

timestamp: WS?
    (DATE | INT)  // TODO: Test 'since +1900'
    | WS? ((DATE | INT) WS? signed_clock (WS? signed_hour_minute)?)
    | WS? DT_T_CLOCK
//     | (date WS+ clock)
//     | (date WS+ clock WS+ signed_int)  // Timezone offset. // TODO check 0:0:0+1
//     | (date WS+ clock WS+ clock)       // Date + (Clock1 - Clock2)
// 
//     | (date WS+ signed_int)            // Date + packed_clock
//     | (date WS+ signed_int WS+ clock)  // Date + (packed_clock - )
//     | (date sign (INT|clock) WS+ hour_minute)  // Date + (packed_clock - tz offset)
// 
//     | (date WS+ signed_int ((WS+ INT) | (WS* signed_int)))  // Date + packed_clock + Timezone Offset
    | WS? TIMESTAMP

//    | (date WS+ clock WS+ ID) // UNKNOWN!
//    | (TIMESTAMP WS+ INT) // UNKNOWN!
//    | (TIMESTAMP WS+ ID) // UNKNOWN!
;

signed_clock:
    HOUR_MINUTE_SECOND | HOUR_MINUTE | any_int 
;

signed_hour_minute:
    // Second not allowed.
    (((sign?)) (HOUR_MINUTE | INT))
    | (WS* SIGNED_INT)
;

clock: HOUR_MINUTE | HOUR_MINUTE_SECOND;

shift:
    WS* SHIFT_OP WS*
;
 
multiply:
  (
    MULTIPLY    // m*2, m--1 m
  | WS+         // "m m"
  )
;

exponent:
    (basic_spec RAISE signed_int)  //km^2, km^-1, km^+2
    | ((base_unit | signed_int) signed_int)    // m2, m+2, s-1, 1+2, 2-3
    | (basic_spec UNICODE_EXPONENT)  // m²
;

