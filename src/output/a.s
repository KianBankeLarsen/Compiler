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

                subq $24, %rsp
                pushq $5
                movq %rbp, %rdx
                popq -8(%rdx)
                pushq $10
                movq %rbp, %rdx
                popq -16(%rdx)
                pushq $34534
                movq %rbp, %rdx
                popq -24(%rdx)
end_main:
                movq %rbp, %rsp
                popq %rbp

                popq %r15
                popq %r14
                popq %r13
                popq %r12
                popq %rbx


                ret

