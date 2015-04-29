from random import gauss
from numpy import std, matrix
from numpy.linalg import inv
import time
from functions import loadCSVToList
from txtfile import TxtFile

def generateErrorMatrix(effmatrix, seffmatrix):
    m = []
    for i in range(len(effmatrix)):
        l = []
        for j in range(len(effmatrix[i])):
            l.append(effmatrix[i][j] + gauss(0, 1) * seffmatrix[i][j])
        m.append(l)
    return m

def main():
    effmatrix = loadCSVToList('../calc/efficencies.txt')
    seffmatrix = loadCSVToList('../calc/efficencies_error.txt')
    
    t1 = time.time()
    
    #generate matrices
    ms = []
    for i in range(100000):
        m = generateErrorMatrix(effmatrix, seffmatrix)
        ms.append(inv(m))
        
    #group values
    sigmas = [[[] for i in range(4)] for j in range(4)]  # empty 4x4 matrix
    for i in range(4):
        for j in range(4):
            entries = []
            for m in ms:
                entries.append(m[i][j])
            sigmas[i][j] = std(entries, ddof=1)
            
    t2 = time.time()
    print('%.3f' % (t2 - t1))
    print(matrix(sigmas))
    
    with TxtFile('../calc/invEfficencies_error.txt', 'w') as f:
        f.write2DArrayToFile(sigmas, ['%.7f'] * 4)
    
if __name__ == '__main__':
    main()