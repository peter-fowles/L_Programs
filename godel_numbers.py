from sympy import prime
from math import sqrt

def natural_number(godel) -> int:
    """
    returns the natural number represented by a godel number

    positional arguments:
    godel -- an ordered list of numbers that represents a godel number
    """
    if len(godel) < 1:
        return 1
    num = prime(1) ** godel[0]
    for i in range(1, len(godel)):
        num *= prime(i + 1) ** godel[i]
    return num

def factor_godel(x:int, n:int=0) -> list:
    """
    factors the first n items in the godel numerical representation of some natural number x
    returns the godel number of x, up to the first n items

    positional arguments:
    x -- the natural number to factor into a godel number
    
    keyword arguments:
    n (default 0) -- the number of godel number iterations to factor (if 0, factors the number until everything else would be 0)
    """
    seq = []
    i = 1
    while natural_number(seq) != x and n == 0 or len(seq) < n:
        t = 0
        while t < x and (x % (prime(i)**(t + 1)) == 0):
            t += 1
        seq.append(t)
        i += 1
    return seq

def length_natural(x:int) -> int:
    """
    returns the length of a natural number based on its godel number

    positional arguments:
    x -- the natural number to compute the length of
    """
    return len(factor_godel(x))

def split_natural_number(z:int) -> tuple:
    """
    splits a natural number into its left and right halves such that z = <x, y>
    this function is primitive recursive - the left and right halves can be split.

    returns the left and right halves of z (x and y)

    positional arguments:
    z -- the natural number to split into its left and right halves
    """
    for x in range(int(sqrt(z)), -1, -1):
        if (z + 1) % 2**x == 0:
            break
    y = (((z + 1) // 2**x) - 1) // 2
    return x, y