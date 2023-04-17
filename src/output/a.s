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
                pushq $3
                pushq $7
                popq %rbx
                popq %rcx
                addq %rbx, %rcx
                pushq %rcx
                pushq $7
                pushq $9
                popq %rbx
                popq %rcx
                movq %rcx, %rax
                cqo
                idivq %rbx
                movq %rax, %rcx
                pushq %rcx
                pushq $8
                popq %rbx
                popq %rcx
                imulq %rbx, %rcx
                pushq %rcx
                popq %rbx
                popq %rcx
                addq %rbx, %rcx
                pushq %rcx
                pushq $6
                popq %rbx
                popq %rcx
                subq %rbx, %rcx
                pushq %rcx
                movq %rbp, %rdx
                popq -8(%rdx)
end_main:
                movq %rbp, %rsp
                popq %rbp

                popq %r15
                popq %r14
                popq %r13
                popq %r12
                popq %rbx


                ret

