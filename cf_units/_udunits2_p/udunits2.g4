grammar udunits2;


unit_spec:
       basic_unit EOF
;


shift_spec:
       product_spec
//       | product_spec shift number
//       | product_spec SHIFT Timestamp
;

product_spec:
       power_spec
       | product_spec multiply power_spec  // km*2
       | product_spec divide power_spec  // km/2
;

power_spec:
      basic_spec INT    // m2
      | negative_exponent // "s-1"
//      | SIGNED_NUMBER SPACE+ basic_spec    // 2 km
      | exponent_unicode
      | exponent
      | basic_spec
;

basic_spec:
       id_
       | '(' shift_spec ')'
//       | LOGREF product_spec ')'
       | number
;

id_: ID;

basic_unit: ID;

number: 
         INT
      |  REAL
;

SIGNED_NUMBER : [+-]+ (REAL | INT) ;
REAL : INT* '.' INT+ ;
UINT: INT;
INT : '0'..'9'+ ;

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
         SPACE* SHIFT_OP SPACE*   // TODO: Test "afromb" - it should be a unit string, not "a from b", right?
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
//         the usual floating_point format
// 
// INT:
//         the usual integer format

multiply:
      // '-'  // This is a complete lie, and what about m+2?
//      |  (SPACE* '.' SPACE*)
//      |  (SPACE* '*' SPACE*)
       '*'
      | SPACE+
;

exponent_unicode:  // m²
    basic_spec EXPONENT
;

exponent:  // TODO: m2
    basic_spec RAISE INT  //km^2
    | id_ INT   // NOTE: Not basic_spec, because that could be a number.
;

negative_exponent:
   basic_spec '-' INT
;
    

WS : [ ] ;
SPACE      : (WS | [\t\r\n]);

divide:
        WS* '/' WS*
;

EXPONENT:
//         ISO-8859-9 or UTF-8 encoded exponent characters
    '\u00B2'  // ²
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


