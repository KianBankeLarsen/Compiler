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

                subq $8, %rsp
                pushq $4
                movq %rbp, %rdx
                popq -8(%rdx)
                movq %rbp, %rdx
                pushq -8(%rdx)
                pushq $5
                popq %rbx
                popq %rcx
                imulq %rbx, %rcx
                pushq %rcx

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
                je aligned_0
                incq %rbx
aligned_0:
                pushq %rbx
                subq $8, %rsp
                callq printf@plt
                addq $8, %rsp
                popq %rbx
                cmpq $0, %rbx
                je aligned_1
                addq $8, %rsp
aligned_1:
                addq $8, %rsp


                popq %r11
                popq %r10
                popq %r9
                popq %r8
                popq %rdi
                popq %rsi
                popq %rdx
                popq %rcx

end_main:
                addq $8, %rsp
                movq %rbp, %rsp
                popq %rbp

                popq %r15
                popq %r14
                popq %r13
                popq %r12
                popq %rbx


                ret

