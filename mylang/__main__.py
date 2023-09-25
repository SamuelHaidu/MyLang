import argparse
from llvmlite import ir
from mylang.parser.code_parser import CodeParser
from mylang.symbol_table import create_symbol_table
from mylang.compiler import create_main


def create_arg_parser():
    parser = argparse.ArgumentParser(description='MyLang Compiler CLI')
    parser.add_argument('input_file', help='Input file containing MyLang code')
    parser.add_argument('-o', '--output', help='Output LLVM IR file (default: out.ll)', default='out.ll')
    return parser


def main():
    parser = create_arg_parser()
    args = parser.parse_args()

    with open(args.input_file, 'r') as f:
        mylang_code = f.read()

    code_parser = CodeParser()
    module = code_parser.parse(mylang_code)
    symbol_table = create_symbol_table(module)

    module_ir = ir.Module(name='module')
    module_ir.triple = 'x86_64-pc-linux-gnu'

    create_main(module_ir, module.body, symbol_table)

    with open(args.output, 'w') as f:
        f.write(str(module_ir))

    print(f'LLVM IR saved to {args.output}')

if __name__ == '__main__':
    main()
