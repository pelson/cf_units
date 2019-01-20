grammar udunits2;


unit_spec:
//    (basic_unit (WS+ basic_unit)?)? EOF
    shift_spec? EOF
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
      basic_spec
      | juxtaposed_raise
//      | negative_exponent // "s-1"
      | juxtaposed_multiplication
      | exponent_unicode
      | exponent
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
    SIGN? (FLOAT | INT)
;


juxtaposed_multiplication:
    //SCI_NUMBER basic_spec  // 2km. TODO: "2 km"
    any_number WS* basic_spec
;

SIGN
   : (PLUS | MINUS)
   ;

PLUS: '+';
MINUS: '-';

fragment INTEGER
   : ('0' .. '9')+
   ;

any_number:
    FLOAT | INT
;

INT : '0'..'9'+ ;

FLOAT: 
     (FLOAT_LEADING_DIGIT | FLOAT_LEADING_PERIOD | INTEGER) E_POWER?  // 1.2e-5, 1e2
   ;

fragment FLOAT_LEADING_DIGIT:
     ('0' .. '9')+ '.' ('0' .. '9')*
;

fragment FLOAT_LEADING_PERIOD:
     ('0' .. '9')? '.' ('0' .. '9')+
;

fragment E_POWER:
     (E SIGN? INTEGER)?
;


fragment E
   : 'E' | 'e'
   ;


number: 
         INT
      |  REAL
;


fragment DIGIT: '0'..'9';
REAL : INT* '.' INT+ ;


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
    | ID INT   // NOTE: Not basic_spec, because that could be a number.
;

juxtaposed_raise:
    base_unit INT    // m2
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


