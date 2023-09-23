; ModuleID = "my_module"
target triple = "x86_64-pc-linux-gnu"
target datalayout = ""

define i32 @"main"()
{
entry:
  %"a_ptr" = alloca i64
  store i64 10, i64* %"a_ptr"
  %"b_ptr" = alloca i64
  store i64 20, i64* %"b_ptr"
  %"a" = load i64, i64* %"a_ptr"
  %"b" = load i64, i64* %"b_ptr"
  %".4" = mul i64 %"a", %"b"
  %".5" = add i64 %".4", 10
  %"result_ptr" = alloca i64
  store i64 %".5", i64* %"result_ptr"
  %"result" = load i64, i64* %"result_ptr"
  %".7" = icmp slt i64 %"result", 300
  %".8" = zext i1 %".7" to i8
  %"high_ptr" = alloca i8
  store i8 %".8", i8* %"high_ptr"
  %"format_string_ptr" = alloca [6 x i8]
  store [6 x i8] c"%d\0a\00A\00", [6 x i8]* %"format_string_ptr"
  %".11" = getelementptr [6 x i8], [6 x i8]* %"format_string_ptr", i32 0, i32 0
  %".12" = load i8, i8* %"high_ptr"
  %".13" = call i32 (i8*, ...) @"printf"(i8* %".11", i8 %".12")
  ret i32 0
}

declare i32 @"printf"(i8* %".1", ...)

