from random import gauss
from numpy import std, matrix
from numpy.linalg import inv
import time
from functions import loadCSVToList
from txtfile import TxtFile
from z0 import LATEXE, LATEXM, LATEXQ, LATEXT

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
    
def makeTable():
    sigmas = loadCSVToList('../calc/invEfficencies_error.txt')
    thead = [r"Schnitt$\backslash$MC-Daten", LATEXE, LATEXM, LATEXT, LATEXQ]
    firstrow = [LATEXE, LATEXM, LATEXT, LATEXQ]
    with TxtFile('../src/tab_effmat_inv_err.tex', 'w') as f:
        f.write2DArrayToLatexTable(list(zip(*([firstrow] + list(zip(*sigmas))))), thead, 
                                   ['%s'] + ['%.7f']*4, 
                                   'Fehler der inversen Effizienzmatrix, berechnet mit einem toy-experiment.', 
                                   'tab:inveffmat:err')
    
if __name__ == '__main__':
    #main()
    makeTable()