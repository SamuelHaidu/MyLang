from mylang.ast.ast_objects import Module
from mylang.parser.lexer import CalcLexer
from mylang.parser.parser import CalcParser


class CodeParser:
    def __init__(self):
        self.lexer = CalcLexer()
        self.parser = CalcParser()

    def parse(self, code: str) -> Module:
        tokens = self.lexer.tokenize(code)
        ast = self.parser.parse(tokens)
        return Module(body=ast)
