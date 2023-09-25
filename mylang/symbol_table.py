from dataclasses import dataclass
from typing import Dict, List, Literal, Optional, Tuple

from mylang.ast.ast_objects import (
    Body,
    Call,
    Function,
    FunctionType,
    If,
    MyLangType,
    Load,
    Module,
    NullType,
    Operator,
    Parameter,
    Return,
    Store,
    Term,
    VariableDeclaration,
)
from mylang.parser.code_parser import CodeParser

SymbolType = Literal["int", "bool", "function"]
LoadType = Literal["global", "argument", "local", "dereference"]


@dataclass
class Symbol:
    name: str
    type: MyLangType
    load_type: LoadType
    arg_index: Optional[int] = None
    llvm_lite_pointer: Optional[object] = None

    def copy(self) -> "Symbol":
        return Symbol(self.name, self.type, self.load_type)


class SymbolTable:
    module_context_name: str = "module"
    c_globals: list[str] = [
        'print'
    ]

    def __init__(self, context_name: str, parent: Optional["SymbolTable"] = None):
        self.symbols: Dict[str, Symbol] = {}
        if not context_name and parent:
            raise Exception("Context name is required when parent is provided")
        self.context_name = context_name or self.module_context_name
        self._contexts: Dict[str, SymbolTable] = {}
        self._parent: SymbolTable | None = parent

    @property
    def dereference_variables(self) -> List[Symbol]:
        return sorted(
            [
                symbol
                for symbol in self.symbols.values()
                if symbol.load_type == "dereference"
            ],
            key=lambda symbol: symbol.name,
        )

    @property
    def context_type(self) -> Literal["module", "function", "closure"]:
        if self.context_name == self.module_context_name:
            return "module"
        if len(self.dereference_variables) > 0:
            return "closure"

        return "function"

    def declare(
        self,
        name: str,
        type: MyLangType,
        load_type: LoadType = "local",
        arg_index: Optional[int] = None,
    ):
        if self.context_name == self.module_context_name:
            load_type = "global"

        if name in self.symbols:
            raise Exception(f"Symbol {name} already declared in {self.context_name}")

        self.symbols[name] = Symbol(name, type, load_type, arg_index)
        if isinstance(type, FunctionType):
            self._contexts[name] = SymbolTable(name, self)

    def lookup(self, name: str) -> Symbol:
        symbol = self.symbols.get(name)
        if symbol:
            return symbol

        if self._parent:
            return self._parent.lookup(name)

        raise Exception(f"Symbol {name} not found in {self.context_name}")

    def get_context(self, name: str) -> "SymbolTable":
        context = self._contexts.get(name)
        if context:
            return context
        raise Exception(f"Context {name} not found in {self.context_name}")

    def reference(self, name: str) -> Symbol:
        if name in self.c_globals:
            return Symbol(name, NullType(), "global")
        if name == self.context_name:
            return self.lookup(name)
        
        symbol = self.symbols.get(name)
        if symbol:
            return symbol

        if self._parent:
            symbol = self._parent.reference(name)
            if symbol.load_type != "global":
                clojure_symbol = symbol.copy()
                clojure_symbol.load_type = "dereference"
                function_symbol = self.lookup(self.context_name)
                function_symbol.type.closure_parameters.append( # type: ignore
                    Parameter(name, clojure_symbol.type)
                )
                self.symbols[name] = clojure_symbol
                return clojure_symbol.copy()
            return symbol

        raise Exception(f"Symbol {name} was not declared")

    def get_all_functions(self, functions: Optional[List[Tuple[str, FunctionType]]]) -> List[Tuple[str, FunctionType]]:
        functions = []
        for symbol in self.symbols.values():
            if isinstance(symbol.type, FunctionType):
                functions.append((symbol.name, symbol.type))
        for context in self._contexts.values():
            functions.extend(context.get_all_functions(functions))
        
        return functions
    
    def compute_closures_parameters(self):
        try:
            context_function = self.lookup(self.context_name).type
        except:
            context_function = None

        if isinstance(context_function, FunctionType):     
            closure_parameters: list[Parameter] = []   
            for symbol in self.symbols.values():
                if symbol.load_type == "dereference":
                    closure_parameters.append(Parameter(symbol.name, symbol.type))
            context_function.closure_parameters = closure_parameters
        
        for context in self._contexts.values():
            context.compute_closures_parameters()


def create_symbol_table(
    ast: Term, symbol_table: SymbolTable | None = None
) -> SymbolTable:
    symbol_table = symbol_table or SymbolTable("module")
    match ast:
        case Module() as module:
            symbol_table = create_symbol_table(module.body, symbol_table)
            return symbol_table

        case Body() as body:
            for statement in body.statements:
                symbol_table = create_symbol_table(statement, symbol_table)

        case Function() as function:
            symbol_table.declare(function.name, function.value_type)
            function_symbol_table = symbol_table.get_context(function.name)
            for index, argument in enumerate(function.parameters):
                function_symbol_table.declare(
                    argument.name, argument.value_type, "argument", index
                )

            create_symbol_table(function.body, function_symbol_table)

        case VariableDeclaration() as variable_declaration:
            symbol_table.declare(
                variable_declaration.name, variable_declaration.value_type
            )

        case Load() as load:
            symbol_table.reference(load.name)

        case Store() as store:
            symbol_table.reference(store.name)

        case Call() as call:
            symbol_table.reference(call.name)
            for argument in call.arguments:
                create_symbol_table(argument, symbol_table)

        case Operator() as operator:
            create_symbol_table(operator.left, symbol_table)
            create_symbol_table(operator.right, symbol_table)

        case Return() as return_statement:
            create_symbol_table(return_statement.value, symbol_table)

        case If() as if_statement:
            create_symbol_table(if_statement.condition, symbol_table)
            create_symbol_table(if_statement.then, symbol_table)
            if if_statement.otherwise:
                create_symbol_table(if_statement.otherwise, symbol_table)
        case _:
            pass

    return symbol_table


def print_symbol_table(symbol_table: SymbolTable, indent: int = 0):
    prefix = "│   " * (indent - 1) + "├─ " if indent > 0 else ""
    print(f"{prefix}{symbol_table.context_name}")
    for symbol in symbol_table.symbols.values():
        if isinstance(symbol.type, FunctionType):
            continue
        print(f"│   " * indent + f"{symbol.name} ({symbol.load_type})")
    for context in symbol_table._contexts.values():
        print_symbol_table(context, indent + 1)


if __name__ == "__main__":
    code = """
    function main_0(a: int, b: int) -> null {
        function main_1() -> null {
            function main_2() -> int {
                return a + b;
            }
        }
    }  
    """
    """ Symbol Table
    module
    ├─ main_0
    │   a (argument)
    │   ├─ main_1
    │   │   a (dereference)
    │   │   ├─ main_2
    │   │   │   a (dereference)
    """
    code_parser = CodeParser()
    module = code_parser.parse(code)
    # print(ast)
    st = create_symbol_table(module)
    print_symbol_table(st)
    print(st.get_all_functions([]))