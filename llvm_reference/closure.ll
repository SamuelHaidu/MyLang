%vars = type { i64* }
%closure = type { i64 (i64, %vars*)*, %vars }
@.str = private unnamed_addr constant [4 x i8] c"%d\0A\00", align 1
declare i32 @printf(i8*, ...)

define i64 @local_add(i64 %b, %vars* %closure_vars) {
entry:
    ; load pointer to pointer to a
    %vars.a = getelementptr %vars, %vars* %closure_vars, i32 0, i32 0
    ; load pointer to a
    %a.ptr = load i64*, i64** %vars.a
    ; load a
    %a = load i64, i64* %a.ptr
    ; add a and b
    %add = add i64 %a, %b
    ; return the result
    ret i64 %add
}

define %closure* @add(i64 %a) {
entry:
    ; Make a closure
    ; allocate a closure
    %closure_local_add = alloca %closure
      ; store values in the dereferences
      ; create "a" dereference
      %a.ptr = alloca i64
      store i64 %a, i64* %a.ptr
    
      ; get pointer to vars
      %vars.ptr = getelementptr %closure, %closure* %closure_local_add, i32 0, i32 1
      
      ; store dereference in the closure vars
      ; store a.ptr in vars.a
      %vars.a.ptr = getelementptr %vars, %vars* %vars.ptr, i32 0, i32 0
      store i64* %a.ptr, i64** %vars.a.ptr

      ; store the function in the closure
      %closure_local_add.func.ptr = getelementptr %closure, %closure* %closure_local_add, i32 0, i32 0
      store i64 (i64, %vars*)* @local_add, i64 (i64, %vars*)** %closure_local_add.func.ptr
    
    ; return the closure
    ret %closure* %closure_local_add
}


define i32 @main() {
entry:
  ; call add(1)
  %add_closure = call %closure* @add(i64 20)
  ; load the function pointer
  %add_closure.func.ptr = getelementptr %closure, %closure* %add_closure, i32 0, i32 0
  ; load function pointer
  %add_closure.func = load i64 (i64, %vars*)*, i64 (i64, %vars*)** %add_closure.func.ptr
  ; load the vars pointer
  %add_closure.vars.ptr = getelementptr %closure, %closure* %add_closure, i32 0, i32 1

  ; call the function
  %add_result = call i64 %add_closure.func(i64 50, %vars* %add_closure.vars.ptr)

  ; print the result
  %str = getelementptr [4 x i8], [4 x i8]* @.str, i32 0, i32 0
  %call = call i32 (i8*, ...) @printf(i8* %str, i64 %add_result)
  ret i32 1
}
