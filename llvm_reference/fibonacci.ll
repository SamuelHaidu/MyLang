; ModuleID = "module"
target triple = "x86_64-pc-linux-gnu"
target datalayout = ""

define i32 @"main"()
{
entry:
  %".2" = call i64 @"fib"(i64 35)
  store i64 %".2", i64* @"print_on_screen"
  %"format_string_ptr" = alloca [6 x i8]
  store [6 x i8] c"%d\0a\00A\00", [6 x i8]* %"format_string_ptr"
  %".5" = getelementptr [6 x i8], [6 x i8]* %"format_string_ptr", i32 0, i32 0
  %".6" = load i64, i64* @"print_on_screen"
  %".7" = call i32 (i8*, ...) @"printf"(i8* %".5", i64 %".6")
  ret i32 0
}

define i64 @"fib"(i64 %".1")
{
entry:
  %".3" = icmp sle i64 %".1", 1
  %".4" = zext i1 %".3" to i8
  %".5" = trunc i8 %".4" to i1
  br i1 %".5", label %"entry.if", label %"entry.endif"
entry.if:
  ret i64 %".1"
entry.endif:
  %".8" = sub i64 %".1", 1
  %".9" = call i64 @"fib"(i64 %".8")
  %".10" = sub i64 %".1", 2
  %".11" = call i64 @"fib"(i64 %".10")
  %".12" = add i64 %".9", %".11"
  ret i64 %".12"
}

@"print_on_screen" = internal global i64 0
declare i32 @"printf"(i8* %".1", ...)

