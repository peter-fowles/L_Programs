from sympy import prime
from l_program import L_Program

def natural_number(godel:list) -> int:
    if len(godel) < 1:
        return 1
    num = prime(1) ** godel[0]
    for i in range(1, len(godel)):
        num *= prime(i + 1) ** godel[i]
    return num

def factor_godel(x:int) -> list:
    seq = []
    i = 1
    while natural_number(seq) != x:
        t = 0
        while t < x and (x % (prime(i)**(t + 1)) == 0):
            t += 1
        seq.append(t)
        i += 1
    return seq

def length_natural(x:int) -> int:
    return len(factor_godel(x))

def encode_program(variables:list, labels:list, instructions:list) -> int:
    num_p = []
    for ins in instructions:
        num_p.append(encode_instruction(variables, labels, ins))
    return natural_number(num_p) - 1

def encode_instruction(variables:list, labels:list, instruction:str) -> int:
    labelled = instruction[0] == '['
    instruction = instruction.split(' ')
    a = 0
    b = 0
    c = 0
    var = ''
    if labelled:
        a = labels.index(instruction[0][1:-1]) + 1
        instruction = instruction[1:]
    if instruction[0] == 'IF':
        b = labels.index(instruction[-1]) + 3
        var = instruction[1]
    elif '+' in instruction:
        b = 1
        var = instruction[0]
    elif '-' in instruction:
        b = 2
        var = instruction[0]
    else:
        b = 0
        var = instruction[0]
    c = variables.index(var) + 1
    return compute_instruction(a, b, c)

def compute_instruction(a, b, c):
    right = 2**b * (2 * c + 1) - 1
    return 2**a * (2 * right + 1) - 1

def program_from_number(n:int) -> 

if __name__ == '__main__':
    print(factor_godel(2**21))