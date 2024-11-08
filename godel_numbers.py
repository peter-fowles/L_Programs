from sympy import prime

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
    left = -1
    right = -1
    for x in range(z + 1):
        for y in range(z + 1):
            if 2**x * (2 * y + 1) - 1 == z:
                if left < 0:
                    left = x
    for y in range(z + 1):
        for x in range(z + 1):
            if 2**x * (2 * y + 1) - 1 == z:
                if right < 0:
                    right = y

    return left, right