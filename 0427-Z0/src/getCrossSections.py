from numpy import dot, matrix
from numpy.linalg import inv  # inverse matrix
from cuts import CUTS
from functions import setupROOT, loadCSVToList
from z0 import Z0Data
from ROOT import gStyle, TCanvas, TLegend  # @UnresolvedImport
from txtfile import TxtFile

DEBUG = True

def loadInvEffMatrix():
    m = loadCSVToList('../calc/efficencies.txt')
    print(matrix(inv(m)))
    return inv(m)

def loadSTRatios():
    datas = loadCSVToList('../calc/s-t-integrals.txt')
    d = dict()
    for data in datas:
        d[data[0]] = (data[5], data[6])
    print(d)
    return d

def plotDataDistribution(data, datatype, binsize, xmin, xmax, suffix="_dist"):
    if not DEBUG:
        c = TCanvas("c_%s" % (suffix+datatype), "", 1280, 720)
        hist = data.makeHistogramm("hist_%s" % (suffix+datatype), datatype, binsize, xmin, xmax)
        hist.GetXaxis().SetTitle(datatype)
        hist.GetXaxis().CenterTitle()
        hist.GetYaxis().SetTitle('Anzahl der Ereignisse')
        hist.GetYaxis().CenterTitle()
        hist.Draw()
        c.Update()
        c.Print('../img/data%s_%s.pdf' % (suffix, datatype), 'pdf')
    
def plotDataDistributions(data, suffix="_dist"):
    types = ["Ncharged", "Pcharged", "E_ecal", "E_hcal", "cos_thru", "cos_thet", "E_lep"]
    rangeparams = [(40, 0, 40), (120, 0, 120), (120, 0, 120), (45, 0, 45), (200, -1, 1), (200, -1, 1), (1000, 44, 47)]
    for datatype, rangepars in zip(*[types, rangeparams]):
        plotDataDistribution(data, datatype, rangepars[0], rangepars[1], rangepars[2], suffix)
    

def makeDataCut(data):
    cutcounts = []
    for name, cut in CUTS:
        cutdata = data.cut(cut)
        cutcounts.append(cutdata.getLength())
    return cutcounts

def main():
    # load data
    data = Z0Data.fromROOTFile('../data/daten/daten_1.root', 'h33')
    energiedatas = data.splitEnergies()
    # load inverse efficency matrix
    inveffmatrix = loadInvEffMatrix()
    # load s-t rations
    stRatios = loadSTRatios()
    
    plotDataDistributions(data)
    trueVectors = dict()
    for energie, data in energiedatas.items():
        print("E_lep: ", energie)
        
        MeasVector = makeDataCut(data)
        print("MeasVector: ")
        print(MeasVector)
        
        print("TrueVector:")
        trueVector = list(dot(inveffmatrix, MeasVector))
        print(trueVector)
        trueVector[0] = trueVector[0] * stRatios[energie][0]
        print(trueVector)
        print("")
        
        trueVectors[energie] = trueVector
        
    NDatas = [[]]*4
    for energie in trueVectors.keys():
        for i in range(4):
            NDatas[i] = NDatas[i] + [(energie, trueVectors[energie][i], 0, 0)]
    print(NDatas)
    
    filenames = ['ee', 'mm', 'tt', 'qq']
    for filename, NData in zip(*[filenames, NDatas]):
        with TxtFile('../calc/N_%s.txt' % filename, 'w') as f:
            f.write2DArrayToFile(NData, ['%.2f']*4)
    

if __name__ == '__main__':
    setupROOT()
    gStyle.SetOptStat(0)
    main()