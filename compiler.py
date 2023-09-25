from llvmlite import ir, binding

from mylang.ast.ast_objects import (
    Body,
    BoolType,
    Call,
    Function,
    FunctionType,
    If,
    IntType,
    LiteralValue,
    Load,
    Module,
    MyLangType,
    NullType,
    Operator,
    Parameter,
    Return,
    Store,
    Term,
    VariableDeclaration,
)
from mylang.parser.code_parser import CodeParser
from symbol_table import SymbolTable, create_symbol_table, print_symbol_table

# Globals
i1 = ir.IntType(1)
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


def generate_global_initializer(my_lang_type: MyLangType) -> ir.Constant:
    match my_lang_type:
        case IntType():
            return ir.Constant(convert_types(my_lang_type), 0)
        case BoolType():
            return ir.Constant(convert_types(my_lang_type), 0)
        case NullType():
            return i8(0)
        case _:
            raise NotImplementedError(f"Type {my_lang_type.__name__} not implemented")


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
) -> ir.NamedValue:
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
            return to_mylang_bool(builder, int1_result)  # type: ignore
        case "lt":
            int1_result = builder.icmp_signed("<", left_value, right_value)
            return to_mylang_bool(builder, int1_result)  # type: ignore
        case "ge":
            int1_result = builder.icmp_signed(">=", left_value, right_value)
            return to_mylang_bool(builder, int1_result)  # type: ignore
        case "le":
            int1_result = builder.icmp_signed("<=", left_value, right_value)
            return to_mylang_bool(builder, int1_result)  # type: ignore
        case "eq":
            int1_result = builder.icmp_signed("==", left_value, right_value)
            return to_mylang_bool(builder, int1_result)  # type: ignore
        case "ne":
            return builder.icmp_signed("!=", left_value, right_value)  # type: ignore
        case "or":
            return builder.or_(left_value, right_value)  # type: ignore
        case "and":
            return builder.and_(left_value, right_value)  # type: ignore
        case "xor":
            return builder.xor(left_value, right_value)  # type: ignore
        case _:
            raise NotImplementedError(f"Operator {operator.op} not implemented")


def to_mylang_bool(builder: ir.IRBuilder, llvm_named_value):
    return builder.zext(llvm_named_value, i8)


def to_llvm_bool(builder: ir.IRBuilder, llvm_named_value):
    return builder.trunc(llvm_named_value, i1)


def create_statement(
    builder: ir.IRBuilder, module: ir.Module, statement: Term, symbol_table: SymbolTable
):
    match statement:
        case Operator() as operator:
            left_value = create_statement(builder, module, operator.left, symbol_table)
            right_value = create_statement(
                builder, module, operator.right, symbol_table
            )
            result = parse_operator(builder, operator, left_value, right_value)  # type: ignore
            return result

        case VariableDeclaration() as variable_declaration:
            if symbol_table.context_name != "module":
                value = create_statement(
                    builder, module, variable_declaration.value, symbol_table
                )
                value_type = convert_types(variable_declaration.value_type)
                var_ptr = builder.alloca(
                    value_type, name=variable_declaration.name + "_ptr"
                )
                builder.store(value, var_ptr)
                symbol = symbol_table.lookup(variable_declaration.name)
                symbol.llvm_lite_pointer = var_ptr
            elif symbol_table.context_name == "module":
                value = create_statement(
                    builder, module, variable_declaration.value, symbol_table
                )
                value_type = convert_types(variable_declaration.value_type)
                var_ptr = ir.GlobalVariable(
                    module, value_type, name=variable_declaration.name
                )
                var_ptr.linkage = "internal"
                var_ptr.initializer = generate_global_initializer(variable_declaration.value_type)  # type: ignore
                symbol = symbol_table.lookup(variable_declaration.name)
                symbol.llvm_lite_pointer = var_ptr
                builder.store(value, var_ptr)

        case Load() as load:
            symbol = symbol_table.lookup(load.name)
            if symbol.load_type == "argument":
                arg_index = symbol_table.lookup(symbol_table.context_name).type.get_argument_index(load.name)  # type: ignore
                return builder.function.args[arg_index]
            
            return builder.load(symbol.llvm_lite_pointer, name=load.name)

        case Store() as store:
            value = create_statement(builder, module, store.value, symbol_table)
            symbol = symbol_table.lookup(store.name)
            builder.store(value, symbol.llvm_lite_pointer)

        case LiteralValue() as literal_value:
            return convert_literals(literal_value.value_type, literal_value.value)

        case Function() as function:
            function_symbol = symbol_table.lookup(function.name)
            function_type_llvm = convert_types(function_symbol.type)
            function_llvm = ir.Function(module, function_type_llvm, name=function.name)
            function_symbol.llvm_lite_pointer = function_llvm
            function_block = function_llvm.append_basic_block(name="entry")
            function_builder = ir.IRBuilder(function_block)
            function_symbol_table = symbol_table.get_context(function.name)
            
            # load closure environment
            if function_symbol_table.context_type == "closure":
                env_struct_type = function_builder.function.args[-1]
                for env_var in function_symbol.type.closure_parameters: # type: ignore
                    env_index = function_symbol.type.get_environment_index(env_var.name) # type: ignore
                    env_ptr_ptr = function_builder.gep(env_struct_type, [ i32(0), i32(env_index) ])
                    env_ptr = function_builder.load(env_ptr_ptr)
                    env_symbol = function_symbol_table.lookup(env_var.name)
                    env_symbol.llvm_lite_pointer = env_ptr
            
            # create closure environment
            if function.value_type.is_clojure:
                # create closure struct = { function, env }
                env_struct_type = function_type_llvm.args[-1] # type: ignore
                closure_struct_type = ir.LiteralStructType(
                    function_type_llvm, 
                    env_struct_type
                )
                closure_struct_ptr = function_builder.alloca(closure_struct_type)
                function_ptr_ptr = function_builder.gep(closure_struct_ptr, [ i32(0), i32(0) ])
                builder.store(function_llvm, function_ptr_ptr)

                # store env variables in env_struct_ptr
                env_struct_ptr = function_builder.gep(closure_struct_ptr, [ i32(0), i32(1) ])
                for closure_parameter in function.value_type.closure_parameters: # type: ignore
                    to_load_symbol = function_symbol_table.lookup(closure_parameter.name)
                    env_var_ptr = function_builder.alloca(convert_types(to_load_symbol.type))
                    
                    if to_load_symbol.load_type == "argument":
                        arg_index = function_symbol.type.get_argument_index(to_load_symbol.name) # type: ignore
                        builder.store(builder.function.args[arg_index], env_var_ptr)
                    else:
                        builder.store(to_load_symbol.llvm_lite_pointer, env_var_ptr)

                    closure_parameter_index = function.value_type.get_environment_index(closure_parameter.name) # type: ignore
                    # get the pointer inside of env_struct_ptr for the current closure parameter
                    env_var_ptr_ptr = function_builder.gep(env_struct_ptr, [ i32(0), i32(closure_parameter_index) ])
                    builder.store(env_var_ptr, env_var_ptr_ptr)

            
            for statement in function.body.statements:
                create_statement(
                    function_builder, module, statement, function_symbol_table
                )

        case Return() as return_statement:
            value = create_statement(
                builder, module, return_statement.value, symbol_table
            )
            builder.ret(value)
            pass

        case Call() as call:
            function_symbol = symbol_table.lookup(call.name)
            function_return_value = builder.call(
                function_symbol.llvm_lite_pointer,
                [
                    create_statement(builder, module, argument, symbol_table)
                    for argument in call.arguments
                ],
            )
            return function_return_value

        case If() as if_statement:
            condition_result = create_statement(
                builder, module, if_statement.condition, symbol_table
            )
            condition_result = to_llvm_bool(builder, condition_result)  # type: ignore
            if if_statement.otherwise:
                with builder.if_else(condition_result) as (then, otherwise):
                    with then:
                        for statement in if_statement.then.statements:
                            create_statement(builder, module, statement, symbol_table)

                    with otherwise:
                        for statement in if_statement.otherwise.statements:
                            create_statement(
                                builder, module, statement, symbol_table
                            )
            else:
                with builder.if_then(condition_result):
                    for statement in if_statement.then.statements:
                        create_statement(builder, module, statement, symbol_table)


def create_string(string: str) -> ir.Constant:
    string_type = ir.ArrayType(ir.IntType(8), len(string) + 2)
    string_constant = ir.Constant(string_type, bytearray(string.encode("utf8") + b'\x0A\x00'))
    return string_constant


def create_main(module: ir.Module, module_body: Body, symbol_table: SymbolTable):
    function_type = ir.FunctionType(ir.IntType(32), [])
    function_ir = ir.Function(module, function_type, name="main")
    block = function_ir.append_basic_block(name="entry")
    builder = ir.IRBuilder(block)
    for statement in module_body.statements:
        create_statement(builder, module, statement, symbol_table)

    # declare printf
    printf_type = ir.FunctionType(
        ir.IntType(32), [ir.PointerType(ir.IntType(8))], var_arg=True
    )
    printf = ir.Function(module, printf_type, name="printf")

    format_str = create_string("%d\n")
    format_string_ptr = builder.alloca(format_str.type, name="format_string_ptr")
    builder.store(format_str, format_string_ptr)
    format_string_ptr = builder.gep(
        format_string_ptr,
        [ir.Constant(ir.IntType(32), 0), ir.Constant(ir.IntType(32), 0)],
    )
    builder.call(
        printf,
        [
            format_string_ptr,
            builder.load(symbol_table.lookup("print_on_screen").llvm_lite_pointer),
        ],
    )

    builder.ret(ir.Constant(ir.IntType(32), 0))
    print(module)


if __name__ == "__main__":
    code_parser = CodeParser()
    code = """
    function outer(a: int) -> null {
        function inner() -> int {
            return a + 10;
        }
    }
    print_on_screen: int = 20;
    """
    module = code_parser.parse(code)
    symbol_table = create_symbol_table(module)
    module_ir = ir.Module(name="module")
    module_ir.triple = "x86_64-pc-linux-gnu"
    create_main(module_ir, module.body, symbol_table)