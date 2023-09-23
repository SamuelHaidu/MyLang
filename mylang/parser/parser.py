from typing import Dict
from sly import Parser
from mylang.ast.ast_objects import (
    BinOpName,
    BoolType,
    FunctionType,
    IntType,
    LiteralValue,
    NullType,
    Parameter,
    VariableDeclaration,
    Store,
    Load,
    Operator,
    Body,
    Function,
    Return,
    Call,
    If,
)
from mylang.parser.lexer import CalcLexer

class CalcParser(Parser):
    tokens = CalcLexer.tokens
    op_map: Dict[str, BinOpName] = {
        "+": "add",
        "-": "sub",
        "*": "mul",
        "/": "div",
        "%": "mod",
        ">": "gt",
        "<": "lt",
        ">=": "ge",
        "<=": "le",
        "==": "eq",
    }

    type_map = {
        "int": IntType(),
        "bool": BoolType(),
        "null": NullType(),
    }

    # debugfile = "parser.out"

    @_("body statement")  # type: ignore
    def body(self, p):  # type: ignore
        p.body.statements.append(p.statement)
        return p.body

    @_("statement")  # type: ignore
    def body(self, p):  # type: ignore
        return Body([p.statement])
    
    # If statement
    @_("IF L_PARENTHESIS expr R_PARENTHESIS L_BRACE body R_BRACE")  # type: ignore
    def statement(self, p):  # type: ignore
        return If(p.expr, p.body, None)
    
    @_("IF L_PARENTHESIS expr R_PARENTHESIS L_BRACE body R_BRACE ELSE L_BRACE body R_BRACE")  # type: ignore
    def statement(self, p):  # type: ignore
        return If(p.expr, p.body0, p.body1)

    # Function definition
    @_("FUNCTION SYMBOL function_type L_BRACE body R_BRACE")  # type: ignore
    def statement(self, p):  # type: ignore
        return Function(
            p.SYMBOL, p.function_type.parameters, p.body, p.function_type.return_type
        )

    @_("L_PARENTHESIS R_PARENTHESIS return_definition")  # type: ignore
    def function_type(self, p):  # type: ignore
        return FunctionType([], p.return_definition)

    @_("L_PARENTHESIS parameters R_PARENTHESIS return_definition")  # type: ignore
    def function_type(self, p):  # type: ignore
        return FunctionType(p.parameters, p.return_definition)

    @_("SYMBOL SYMBOL_TYPE_ASSIGN SYMBOL")  # type: ignore
    def parameter(self, p):  # type: ignore
        return Parameter(p.SYMBOL0, self.type_map[p.SYMBOL1])

    @_("SYMBOL SYMBOL_TYPE_ASSIGN function_type")  # type: ignore
    def parameter(self, p):  # type: ignore
        return Parameter(p.SYMBOL, p.function_type)

    @_("parameters COMMA parameter")  # type: ignore
    def parameters(self, p):  # type: ignore
        return p.parameters + [p.parameter]

    @_("parameter")  # type: ignore
    def parameters(self, p):  # type: ignore
        return [p.parameter]

    @_("ARROW SYMBOL")  # type: ignore
    def return_definition(self, p):  # type: ignore
        return self.type_map[p.SYMBOL]

    @_("ARROW function_type")  # type: ignore
    def return_definition(self, p):  # type: ignore
        return p.function_type
    
    @_("RETURN expr END_STATEMENT")  # type: ignore
    def statement(self, p):  # type: ignore
        return Return(p.expr)

    # Assignments
    @_("SYMBOL SYMBOL_TYPE_ASSIGN SYMBOL ASSIGN expr END_STATEMENT")  # type: ignore
    def statement(self, p):  # type: ignore
        return VariableDeclaration(p.SYMBOL0, self.type_map[p.SYMBOL1], p.expr)

    @_("SYMBOL ASSIGN expr END_STATEMENT")  # type: ignore
    def statement(self, p):  # type: ignore
        return Store(p.SYMBOL, p.expr)

    # Call Functions
    @_("SYMBOL L_PARENTHESIS R_PARENTHESIS")  # type: ignore
    def expr(self, p):  # type: ignore
        return Call(p.SYMBOL, [])

    @_("SYMBOL L_PARENTHESIS expr R_PARENTHESIS")  # type: ignore
    def expr(self, p):  # type: ignore
        return Call(p.SYMBOL, p.expr)

    @_("SYMBOL L_PARENTHESIS arguments R_PARENTHESIS")  # type: ignore
    def expr(self, p):  # type: ignore
        return Call(p.SYMBOL, p.arguments)

    @_("arguments expr")  # type: ignore
    def arguments(self, p):  # type: ignore
        p.arguments.append(p.expr)
        return p.arguments

    @_("arguments COMMA")  # type: ignore
    def arguments(self, p):  # type: ignore
        return p.arguments

    @_("expr COMMA")  # type: ignore
    def arguments(self, p):  # type: ignore
        return [p.expr]
    
    # Basic Statements
    @_("expr END_STATEMENT")  # type: ignore
    def statement(self, p):  # type: ignore
        return p.expr

    @_("expr OPERATOR term")  # type: ignore
    def expr(self, p):  # type: ignore
        return Operator(self.op_map[p.OPERATOR], p.expr, p.term)

    @_("term")  # type: ignore
    def expr(self, p):  # type: ignore
        return p.term

    @_("factor")  # type: ignore
    def term(self, p):  # type: ignore
        return p.factor

    @_("NUMBER")  # type: ignore
    def factor(self, p):  # type: ignore
        return LiteralValue(IntType(), int(p.NUMBER))

    @_("BOOL")  # type: ignore
    def factor(self, p):  # type: ignore
        return LiteralValue(BoolType(), p.BOOL == "True")

    @_("NULL")  # type: ignore
    def factor(self, p):  # type: ignore
        return LiteralValue(NullType(), None)

    @_("SYMBOL")  # type: ignore
    def factor(self, p):  # type: ignore
        return Load(p.SYMBOL)