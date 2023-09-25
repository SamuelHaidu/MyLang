Sure, here's a simple README.md that explains the usage and features of your MyLang compiler CLI:

---

# MyLang Compiler

MyLang Compiler is a simple compiler for MyLang, a toy programming language created for studying lexers, parsers, and compilers. MyLang is designed with limited features, including basic data types, recursive functions, and closures, while excluding loops and other complex constructs.

The compiler translates MyLang source code into LLVM Intermediate Representation (IR), enabling further compilation and execution using LLVM toolchains.

## Features

- Supports two data types: integer and boolean (along with a null type for void functions).
- Enables the creation of recursive functions, providing a way to loop.
- Supports closures for capturing and utilizing external variables.
- Compiles MyLang source code into LLVM IR.

## Usage

To compile a MyLang program, use the provided CLI tool.

### Installation

1. Make sure you have Python 3.x installed.

2. Install the required packages using pip:
   
   ```bash
   pip install llvmlite
   ```

3. Run the MyLang compiler CLI:
   
   ```bash
   python mylang_compiler_cli.py input_file.my -o output.ll
   ```

   Replace `input_file.my` with the path to your MyLang source code file and `output.ll` with the desired LLVM IR output file.

## Example

Consider the following example MyLang code saved in `example.mylang`:

```mylang
function add(a: int, b: int) -> int {
    return a + b;
}
```

Compile the MyLang code to LLVM IR using the MyLang Compiler:

```bash
$ python -m mylang example.mylang -o example.ll
```

The resulting LLVM IR will be saved in `example.ll`. Compile the LLVM IR to an executable using `llc` and `clang`:

```bash
$ llc example.ll
$ clang example.s -o example
```

If have problems with target check the target triple. I hardcoded it, but you can change it on `target triple` llvm-ir statement.

To get your current target triple run:
```bash
clang -print-effective-triple
```

## Mini tutorial

