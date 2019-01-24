parser grammar udunits2Parser;

options { tokenVocab=udunits2Lexer; }

unit_spec:
    shift_spec? EOF
;

shift_spec:
       product_spec
     | product_spec shift sci_number
     | product_spec shift timestamp
;


product_spec:  
      (base_unit PERIOD sci_number) // km.2 === 2*km (i.e. this trumps km * 0.2)
       |
      (power_spec
       //| power_spec PERIOD signed_int) // km.2 === 2*km
       | power_spec multiply power_spec // km*2
       | div  // km/2
      ) (WS? product_spec)*  // "km.2 2km .2s" === "4km² 0.2s" 
;

div:
    power_spec divide power_spec
;

power_spec:    // Examples include: m+2, m-2, m3, 2^3, m+3**2 (=m^9)
    (basic_spec
      | exponent_unicode
      | exponent
      | negative_exponent
    )  signed_int?   // We allow only one further power, so 2+3+4 == (2^3)*4
;

basic_spec:
       base_unit
       | '(' shift_spec ')'
//       | LOGREF product_spec ')'
       | sci_number
;


basic_unit: base_unit;
base_unit: ID;


sci_number:
    sign? (float_t | INT)
;

signed_int:
    sign? INT
;

juxtaposed_multiplication:
    (sci_number WS* basic_spec)    // "2km", "2  km"
    | (basic_spec WS+ any_signed_number)  // "km 2", "km -2"
    | (any_signed_number WS+ any_signed_number)  // "2 3"
;

divide:
    WS* DIVIDE WS*
;

sign: (PLUS | MINUS);


any_signed_number:
    sign? any_unsigned_number
;

any_unsigned_number:
    float_t | INT
;


// Float is not a lexer token as the context is important (e.g. m2.3 === m^2 * 3 in udunits2)
float_t:
    (((INT PERIOD INT?)
     |(INT? PERIOD INT)
    ) E_POWER?)  // 1.2e-5, 1e2
    | (INT E_POWER)
;


timestamp:
    DATE
    | (DATE WS? signed_clock signed_hour_minute?)
//     | (date WS+ clock)
//     | (date WS+ clock WS+ signed_int)  // Timezone offset. // TODO check 0:0:0+1
//     | (date WS+ clock WS+ clock)       // Date + (Clock1 - Clock2)
// 
//     | (date WS+ signed_int)            // Date + packed_clock
//     | (date WS+ signed_int WS+ clock)  // Date + (packed_clock - )
//     | (date sign (INT|clock) WS+ hour_minute)  // Date + (packed_clock - tz offset)
// 
//     | (date WS+ signed_int ((WS+ INT) | (WS* signed_int)))  // Date + packed_clock + Timezone Offset
    | TIMESTAMP

//    | (date WS+ clock WS+ ID) // UNKNOWN!
//    | (TIMESTAMP WS+ INT) // UNKNOWN!
//    | (TIMESTAMP WS+ ID) // UNKNOWN!
;

date: INT MINUS INT (MINUS INT)?;

signed_clock:
    (WS+ | (WS* sign)) (clock | INT)    
;

signed_hour_minute:
    (WS+ | (WS* sign)) (HOUR_MINUTE | INT) 
;
hour_minute: INT ':' INT;

clock: HOUR_MINUTE | HOUR_MINUTE_SECOND;


shift:
         WS* SHIFT_OP WS*
;
 
multiply:
      '-'  // m--1 === m * -1
      | MULTIPLY
      | PERIOD
      | WS+
;

exponent_unicode:  // m²
    basic_spec UNICODE_EXPONENT
;

exponent:  // TODO: m2
    (basic_spec RAISE signed_int)  //km^2, km^-1, km^+2
    | ((base_unit | signed_int) signed_int)    // m2, m+2, s-1, 1+2, 2-3
;


negative_exponent:
   basic_spec '-' INT
;
