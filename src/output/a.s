.data

form:
                .string "%d\n"

.text

.globl main

main:

                pushq %rbx
                pushq %r12
                pushq %r13
                pushq %r14
                pushq %r15

                pushq %rbp
                movq %rsp, %rbp

                subq $0, %rsp
                pushq $1

                pushq %rcx
                pushq %rdx
                pushq %rsi
                pushq %rdi
                pushq %r8
                pushq %r9
                pushq %r10
                pushq %r11

                movq %rbp, %rdx
                pushq %rdx
                subq $8, %rsp

                pushq %rbx
                pushq %r12
                pushq %r13
                pushq %r14
                pushq %r15

                pushq %rbp
                movq %rsp, %rbp

                subq $0, %rsp
for_0:
                movq %rbp, %rdx
                pushq 128(%rdx)
                pushq $5
                popq %rbx
                popq %rcx
                cmpq %rbx, %rcx
                jl cmp_true_2
                pushq $0
                jmp cmp_end_3
cmp_true_2:
                pushq $1
cmp_end_3:
                popq %rbx
                movq $0, %rcx
                cmpq %rbx, %rcx
                je rof_1
                movq %rbp, %rdx
                pushq 128(%rdx)

                pushq %rcx
                pushq %rdx
                pushq %rsi
                pushq %rdi
                pushq %r8
                pushq %r9
                pushq %r10
                pushq %r11

                leaq form(%rip), %rdi
                movq 64(%rsp), %rsi
                movq $0, %rax
                movq %rsp, %rcx
                andq $-16, %rsp
                movq $0, %rbx
                cmpq %rsp, %rcx
                je aligned_4
                incq %rbx
aligned_4:
                pushq %rbx
                subq $8, %rsp
                callq printf@plt
                addq $8, %rsp
                popq %rbx
                cmpq $0, %rbx
                je aligned_5
                addq $8, %rsp
aligned_5:
                addq $8, %rsp


                popq %r11
                popq %r10
                popq %r9
                popq %r8
                popq %rdi
                popq %rsi
                popq %rdx
                popq %rcx

                movq %rbp, %rdx
                pushq 128(%rdx)
                pushq $1
                popq %rbx
                popq %rcx
                addq %rbx, %rcx
                pushq %rcx
                movq %rbp, %rdx
                popq 128(%rdx)
                jmp for_0
rof_1:
                addq $0, %rsp
                movq %rbp, %rsp
                popq %rbp

                popq %r15
                popq %r14
                popq %r13
                popq %r12
                popq %rbx


                addq $8, %rsp

                popq %r11
                popq %r10
                popq %r9
                popq %r8
                popq %rdi
                popq %rsi
                popq %rdx
                popq %rcx

                addq $8, %rsp
end_main:
                addq $0, %rsp
                movq %rbp, %rsp
                popq %rbp

                popq %r15
                popq %r14
                popq %r13
                popq %r12
                popq %rbx


                ret

