from numpy import sqrt, pi
from physconsts import hbar_eVs
from txtfile import TxtFile

def main():
    E, sE = 107.7, 1.42
    t, st = 2.237, 0.052
    tToeV = 1 / hbar_eVs * 1e-6
    nt, snt = tToeV * t, tToeV * st 
    A = 192 * pi ** 3 
    G = sqrt(A / (nt * E ** 5)) * 1e3
    sG = 1/2 * sqrt(A * (E**2 * snt**2 + 25 * sE**2 * nt**2)/(E**7 * nt**3)) * 1e3
    print(G, sG)
    with TxtFile('../calc/G.txt', 'w') as f:
        f.writeline('\t', '%.4e' % G, '%.2e' % sG)

if __name__ == '__main__':
    main()