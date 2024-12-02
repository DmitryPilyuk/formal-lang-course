grammar GraphQueryLang;

// Parser
prog: stmt*;

stmt: declare | bind | add | remove;

declare: LET VAR IS GRAPH;

bind: LET VAR EQ expr;

remove: REMOVE (VERTEX | EDGE | VERTICES) expr FROM VAR;

add: ADD (VERTEX | EDGE) expr TO VAR;

expr: NUM | CHAR | VAR | edge_expr | set_expr | regexp | select;

set_expr: L_BR expr (COMMA expr)* R_BR;

edge_expr: L_PAR expr COMMA expr COMMA expr R_PAR;

regexp:
	regexp PIPE regexp
	| regexp AND regexp
	| regexp DOT regexp
	| regexp CARET range
	| L_PAR regexp R_PAR
	| CHAR
	| VAR;

range: L_BR NUM DDOT NUM? R_BR;

select:
	v_filter? v_filter? RETURN VAR (COMMA VAR)? WHERE VAR REACHABLE FROM VAR IN VAR BY expr;

v_filter: FOR VAR IN expr;

// Lexer
LET: 'let';
IS: 'is';
GRAPH: 'graph';
REMOVE: 'remove';
VERTEX: 'vertex';
EDGE: 'edge';
VERTICES: 'vertices';
ADD: 'add';
TO: 'to';
FROM: 'from';
FOR: 'for';
IN: 'in';
RETURN: 'return';
WHERE: 'where';
REACHABLE: 'reachable';
BY: 'by';

EQ: '=';
L_BR: '[';
R_BR: ']';
L_PAR: '(';
R_PAR: ')';
COMMA: ',';
DOT: '.';
DDOT: '..';
PIPE: '|';
AND: '&';
CARET: '^';

VAR: [a-z] [a-z0-9]*;
NUM: '0' | [1-9][0-9]*;
CHAR: '"' [a-z] '"';

WS: [ \t\r\n]+ -> skip;
