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
//      | basic_spec INT    // m2
//      | negative_exponent // "s-1"
      | SCI_NUMBER basic_spec    // 2 km
      | exponent_unicode
      | exponent
;

basic_spec:
       base_unit
       | '(' shift_spec ')'
//       | LOGREF product_spec ')'
       | SCI_NUMBER
;

id_: ID;

basic_unit: base_unit;
base_unit: ID;


SCI_NUMBER:
    SCIENTIFIC_NUMBER
    | SIGNED_SCI_NUMBER
;


SIGNED_SCI_NUMBER:
//    SIGN+ number   // Allow +1, -1, --1, -+-1, etc. (UDUNITS DOES NOT SUPPORT THIS)
   SIGN SCIENTIFIC_NUMBER
;

fragment SIGN
   : (PLUS | MINUS)
   ;

fragment PLUS: '+';
fragment MINUS: '-';

SCIENTIFIC_NUMBER
   : DECIMAL (E SIGN? INTEGER)?
   ;

fragment INTEGER
   : ('0' .. '9')+
   ;

fragment DECIMAL: LEADING_DECIMAL | NO_LEADING_DECIMAL;

fragment LEADING_DECIMAL
   : ('0' .. '9')+ ('.' ('0' .. '9')*)?
   ;
fragment NO_LEADING_DECIMAL:
     ('0' .. '9')? '.' ('0' .. '9')+
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


