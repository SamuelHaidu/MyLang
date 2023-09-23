from sly import Lexer


class CalcLexer(Lexer):
    tokens = {
        "ARROW",
        "SYMBOL_TYPE_ASSIGN",
        "OPERATOR",
        "ASSIGN",
        "FUNCTION",
        "L_PARENTHESIS",
        "R_PARENTHESIS",
        "L_BRACE",
        "R_BRACE",
        "COMMA",
        "RETURN",
        "IF",
        "ELSE",
        "END_STATEMENT",
        "SYMBOL",
        "NUMBER",
        "BOOL",
        "NULL",
    }

    ARROW = r"->"
    SYMBOL_TYPE_ASSIGN = r":"
    OPERATOR = r"[-+*/%]|==|>=|<=|>|<"
    ASSIGN = r"="
    FUNCTION = r"function "
    L_PARENTHESIS = r"\("
    R_PARENTHESIS = r"\)"
    L_BRACE = r"\{"
    R_BRACE = r"\}"
    COMMA = r","
    RETURN = r"return"
    IF = r"if"
    ELSE = r"else"
    END_STATEMENT = r";"
    SYMBOL = r"[a-zA-Z_][a-zA-Z0-9_]*"
    NUMBER = r"\d+"
    BOOL = r"True|False"
    NULL = r"null"
    ignore = " \t"

    @_(r"\n+")  # type: ignore
    def ignore_newline(self, t):
        self.lineno += len(t.value)
