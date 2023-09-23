from llvmlite import ir, binding

from mylang.ast.ast_objects import (
    Body,
    BoolType,
    Function,
    FunctionType,
    IntType,
    LiteralValue,
    Load,
    Module,
    MyLangType,
    NullType,
    Operator,
    Parameter,
    Term,
    VariableDeclaration,
)
from mylang.parser.code_parser import CodeParser
from symbol_table import SymbolTable, create_symbol_table

# Globals
i8 = ir.IntType(8)
i32 = ir.IntType(32)
i64 = ir.IntType(64)
char = ir.IntType(8)


def convert_types(mylang_type: MyLangType) -> ir.Type:
    match mylang_type:
        case IntType():
            return ir.IntType(mylang_type.size)
        case BoolType():
            return ir.IntType(mylang_type.size)
        case NullType():
            return ir.VoidType()
        case FunctionType():
            parameters = [
                convert_types(param.value_type) for param in mylang_type.parameters
            ]
            if mylang_type.closure_parameters:
                clojure_struct = ir.LiteralStructType(
                    [
                        convert_types(param.value_type).as_pointer()
                        for param in mylang_type.closure_parameters
                    ]
                )

                parameters.append(clojure_struct.as_pointer())
            return ir.FunctionType(
                convert_types(mylang_type.return_type),
                parameters,
            )
        case _:
            raise NotImplementedError(f"Type {mylang_type.__name__} not implemented")


def convert_literals(mylang_type: MyLangType, value: int | bool | None) -> ir.Constant:
    match mylang_type:
        case IntType():
            return ir.Constant(convert_types(mylang_type), value)
        case BoolType():
            return ir.Constant(convert_types(mylang_type), int(value))  # type: ignore
        case NullType():
            raise Exception("Cannot convert null type to literal")
        case FunctionType():
            raise Exception("Cannot convert function type to literal")
        case _:
            raise NotImplementedError(f"Type {mylang_type.__name__} not implemented")


def parse_operator(
    builder: ir.IRBuilder,
    operator: Operator,
    left_value: ir.Value,
    right_value: ir.Value,
) -> ir.instructions.Instruction:
    match operator.op:  # LiteralType["add", "sub", "mul", "div", "mod", "gt", "lt", "ge", "le", "eq"]
        case "add":
            return builder.add(left_value, right_value)  # type: ignore
        case "sub":
            return builder.sub(left_value, right_value)  # type: ignore
        case "mul":
            return builder.mul(left_value, right_value)  # type: ignore
        case "div":
            return builder.sdiv(left_value, right_value)  # type: ignore
        case "mod":
            return builder.srem(left_value, right_value)  # type: ignore
        case "gt":
            int1_result = builder.icmp_signed(">", left_value, right_value)
            return builder.zext(int1_result, i8) # type: ignore
        case "lt":
            int1_result = builder.icmp_signed("<", left_value, right_value)
            return builder.zext(int1_result, i8) # type: ignore
        case "ge":
            int1_result = builder.icmp_signed(">=", left_value, right_value)
            return builder.zext(int1_result, i8) # type: ignore
        case "le":
            int1_result = builder.icmp_signed("<=", left_value, right_value)
            return builder.zext(int1_result, i8) # type: ignore
        case "eq":
            int1_result = builder.icmp_signed("==", left_value, right_value)
            return builder.zext(int1_result, i8) # type: ignore


def create_statement(
    builder: ir.IRBuilder, statement: Term, symbol_table: SymbolTable
):
    match statement:
        case Operator() as operator:
            left_value = create_statement(builder, operator.left, symbol_table)
            right_value = create_statement(builder, operator.right, symbol_table)
            result = parse_operator(builder, operator, left_value, right_value) # type: ignore
            return result
    
        case VariableDeclaration() as variable_declaration:
            value = create_statement(builder, variable_declaration.value, symbol_table)
            value_type = convert_types(variable_declaration.value_type)
            var_ptr = builder.alloca(value_type, name=variable_declaration.name + "_ptr")
            builder.store(value, var_ptr)
            symbol = symbol_table.lookup(variable_declaration.name)
            symbol.llvm_lite_pointer = var_ptr

        case Load() as load:
            symbol = symbol_table.lookup(load.name)
            return builder.load(symbol.llvm_lite_pointer, name=load.name)
            
        case LiteralValue() as literal_value:
            return convert_literals(literal_value.value_type, literal_value.value)


def create_string(string: str) -> ir.Constant:
    string_type = ir.ArrayType(ir.IntType(8), len(string))
    string_constant = ir.Constant(string_type, bytearray(string.encode("utf8")))
    return string_constant


def create_main(module: ir.Module, module_body: Body, symbol_table: SymbolTable):
    function_type = ir.FunctionType(ir.IntType(32), [])
    function_ir = ir.Function(module, function_type, name='main')
    block = function_ir.append_basic_block(name="entry")
    builder = ir.IRBuilder(block)
    for statement in module_body.statements:
        if isinstance(statement, Function):
            continue
        create_statement(builder, statement, symbol_table)
    
    # declare printf
    printf_type = ir.FunctionType(ir.IntType(32), [ir.PointerType(ir.IntType(8))], var_arg=True)
    printf = ir.Function(module, printf_type, name="printf")

    format_str = create_string("%d\n\0A\00")
    # alloca
    format_string_ptr = builder.alloca(format_str.type, name="format_string_ptr")
    # store
    builder.store(format_str, format_string_ptr)
    # getelementptr
    format_string_ptr = builder.gep(format_string_ptr, [ir.Constant(ir.IntType(32), 0), ir.Constant(ir.IntType(32), 0)])
    # call
    builder.call(printf, [format_string_ptr, builder.load(symbol_table.lookup("high").llvm_lite_pointer)])

    builder.ret(ir.Constant(ir.IntType(32), 0))
    print(module)
    


if __name__ == "__main__":
    code_parser = CodeParser()
    code = """
    a: int = 10;
    b: int = 20;
    result: int = a * b + 10;
    high: bool = result < 300;
    """
    module = code_parser.parse(code)
    symbol_table = create_symbol_table(module)
    module_ir = ir.Module(name="my_module")
    module_ir.triple = "x86_64-pc-linux-gnu"
    create_main(module_ir, module.body, symbol_table)