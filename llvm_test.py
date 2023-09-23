from llvmlite import ir, binding

# Create a new LLVM module and its main function
module = ir.Module(name="my_module")
main_function = ir.Function(module, ir.FunctionType(ir.VoidType(), []), name="main")
block = main_function.append_basic_block(name="entry")
builder = ir.IRBuilder(block)
add_1 = builder.add(ir.Constant(ir.IntType(32), 1), ir.Constant(ir.IntType(32), 2))
add_2 = builder.add(add_1, ir.Constant(ir.IntType(32), 3))
type(add_2)
builder.ret(ir.Constant(ir.IntType(32), 0))
print(type(add_2))
