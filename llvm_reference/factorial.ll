; ModuleID = "module"
target triple = "x86_64-pc-linux-gnu"
target datalayout = ""

define i32 @"main"()
{
entry:
  %".2" = call i64 @"factorial"(i64 10)
  store i64 %".2", i64* @"print_on_screen"
  %"format_string_ptr" = alloca [6 x i8]
  store [6 x i8] c"%d\0a\00A\00", [6 x i8]* %"format_string_ptr"
  %".5" = getelementptr [6 x i8], [6 x i8]* %"format_string_ptr", i32 0, i32 0
  %".6" = load i64, i64* @"print_on_screen"
  %".7" = call i32 (i8*, ...) @"printf"(i8* %".5", i64 %".6")
  ret i32 0
}

define i64 @"factorial"(i64 %".1")
{
entry:
  %".3" = icmp eq i64 %".1", 1
  %".4" = zext i1 %".3" to i8
  %"is_1_ptr" = alloca i8
  store i8 %".4", i8* %"is_1_ptr"
  %".6" = icmp eq i64 %".1", 0
  %".7" = zext i1 %".6" to i8
  %"is_0_ptr" = alloca i8
  store i8 %".7", i8* %"is_0_ptr"
  %"is_1" = load i8, i8* %"is_1_ptr"
  %"is_0" = load i8, i8* %"is_0_ptr"
  %".9" = or i8 %"is_1", %"is_0"
  %".10" = trunc i8 %".9" to i1
  br i1 %".10", label %"entry.if", label %"entry.endif"
entry.if:
  ret i64 %".1"
entry.endif:
  %".13" = sub i64 %".1", 1
  %".14" = call i64 @"factorial"(i64 %".13")
  %".15" = mul i64 %".1", %".14"
  ret i64 %".15"
}

@"print_on_screen" = internal global i64 0
declare i32 @"printf"(i8* %".1", ...)

