grammar udunits2;


unit_spec:
    shift_spec? EOF
;

shift_spec:
       product_spec
     | product_spec shift sci_number
       | product_spec shift timestamp
;

product_spec:  
      (base_unit PERIOD signed_int) // km.2 === 2*km
       |
      (power_spec
       //| power_spec PERIOD signed_int) // km.2 === 2*km
       | power_spec multiply power_spec // km*2
       | div  // km/2
      ) product_spec*  // "km.2 2km .2s" === "4km² 0.2s" 
;

div:
    power_spec divide power_spec
;

power_spec:    // Examples include: m+2, m-2, m3, 2^3, m+3**2 (=m^9)
    (basic_spec
      | juxtaposed_raise
      | juxtaposed_multiplication
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

sign: (PLUS | MINUS);
fragment SIGN
   : (PLUS | MINUS)
   ;

PLUS: '+';
MINUS: '-';
MULTIPLY: ('*' | '·');
DIVIDE: '/';
PERIOD: '.';

fragment INTEGER
   : ('0' .. '9')+
   ;

any_signed_number:
    sign? any_unsigned_number
;

any_unsigned_number:
    float_t | INT
;

INT : '0'..'9'+ ;

// Float is not a lexer token as the context is important (e.g. m2.3 === m^2 * 3 in udunits2)
float_t:
    ( (INT+ '.' INT*)
     |(INT? '.' INT+)
     | INT
    ) E_POWER?  // 1.2e-5, 1e2
;

//FLOAT: 
//     (FLOAT_LEADING_DIGIT | FLOAT_LEADING_PERIOD | INTEGER) E_POWER?  // 1.2e-5, 1e2
//   ;

fragment FLOAT_LEADING_DIGIT:
;

fragment FLOAT_LEADING_PERIOD:
     ('0' .. '9')? '.' ('0' .. '9')+
;

E_POWER:
     ('E' | 'e') (PLUS | MINUS)? INT
;


fragment E
   : 'E' | 'e'
   ;

fragment DIGIT: '0'..'9';


timestamp:
    date
    | (date signed_clock signed_hour_minute?)
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

HOUR_MINUTE_SECOND: INT ':' INT ':' INT;
HOUR_MINUTE: INT ':' INT;
clock: HOUR_MINUTE | HOUR_MINUTE_SECOND;

TIMESTAMP: INT (MONTH INT?)? 'T' INT (INT INT?)?;

fragment MONTH: 
    ('0'? ('1'..'9')) | ('1' ('0'..'2'))
;

// Timestamp: one of
//         DATE
//         DATE CLOCK
//         DATE CLOCK CLOCK
//         DATE CLOCK INT
//         DATE CLOCK ID
//         TIMESTAMP
//         TIMESTAMP INT
//         TIMESTAMP ID
// 
shift:
         WS* SHIFT_OP WS*
;
 
SHIFT_OP :
         '@'
         | 'after'
         | 'from'
         | 'since'
         | 'ref'
;

// 
// REAL:
//         the usual float_ting_point format
// 
// INT:
//         the usual integer format

multiply:
      //(SPACE+ '-')  // This is now handled in juxtaposed_multiply
//      |  (SPACE* '*' SPACE*)
      MULTIPLY
      | PERIOD
      | WS+
;

exponent_unicode:  // m²
    basic_spec UNICODE_EXPONENT
;

exponent:  // TODO: m2
    basic_spec RAISE signed_int  //km^2, km^-1, km^+2
    | ID INT   // NOTE: Not basic_spec, because that could be a number.
;

juxtaposed_raise:
    (base_unit | signed_int) signed_int    // m2, m+2, s-1, 1+2, 2-3
;

negative_exponent:
   basic_spec '-' INT
;
    

WS : [ ] ;
// SPACE      : (WS | [\t\r\n]);

divide:
        WS* '/' WS*
;

UNICODE_EXPONENT:
    // One or more ISO-8859-9 encoded exponent characters
    ('⁻' | '⁺' | '¹' | '²' | '³' | '⁴' | '⁵' | '⁶' | '⁷' | '⁸' | '⁹' | '⁰')+
; 

RAISE :
         '^'
       | '**'
;

//ID: one of
//        <id>
//        '%'
//        "'"
//        "\""
//        degree sign
//        greek mu character
//

ID:  [A-Za-z_]+ ;


// handle characters which failed to match any other token
ErrorCharacter : . ;
