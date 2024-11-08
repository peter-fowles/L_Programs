from sympy import prime
from math import sqrt

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

def split_natural_number(z):
    for x in range(int(sqrt(z)), -1, -1):
        if (z + 1) % 2**x == 0:
            break
    y = (((z + 1) // 2**x) - 1) // 2
    return x, y