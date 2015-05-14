from numpy import dot, sqrt
from cuts import CUTS
from functions import setupROOT, loadCSVToList
from z0 import Z0Data
from ROOT import gStyle, TCanvas # @UnresolvedImport
from txtfile import TxtFile

DEBUG = True


def loadInvEffMatrix():
    m = loadCSVToList('../calc/invEfficencies.txt')
    sm = loadCSVToList('../calc/invEfficencies_error.txt')
    return m, sm


def loadSTRatios():
    datas = loadCSVToList('../calc/s-t-integrals.txt')
    d = dict()
    for data in datas:
        d[data[0]] = data[-2:]  # last to elems, value and error
    return d


def loadLums():
    datas = loadCSVToList('../data/daten/lum.txt')
    d = dict()
    for data in datas:
        d[data[0]] = data[1:]
    return d


def loadCorrections():
    datas = loadCSVToList('../data/daten/corr.txt')
    d = dict()
    for data in datas:
        d[data[0]] = {'qq': data[1], 'll': data[2]}
    return d


def plotDataDistribution(data, datatype, binsize, xmin, xmax, suffix="_dist"):
    if not DEBUG:
        c = TCanvas("c_%s" % (suffix + datatype), "", 1280, 720)
        hist = data.makeHistogramm("hist_%s" % (suffix + datatype), datatype, binsize, xmin, xmax)
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


def calcCrossSection(ctype, NData, lums, corrs):
    if ctype == 'ee' or ctype == 'mm' or ctype == 'tt':
        corrtype = 'll'
    else:
        corrtype = 'qq'
    sigmas = []
    for energy, N, sN in NData:
        sigma = N / lums[energy][0] + corrs[energy][corrtype]   # sigma = N / L + corr
        ssimga = N / lums[energy][0] * sqrt((sN / N)**2 + (lums[energy][1] / lums[energy][0])**2)
        sigmas.append((energy, sigma, ssimga))
    return sigmas


def main():
    # load data
    data = Z0Data.fromROOTFile('../data/daten/daten_1.root', 'h33')
    energiedatas = data.splitEnergies()
    inveffmatrix, sinveffmatrix = loadInvEffMatrix()
    stRatios = loadSTRatios()
    lums = loadLums()
    corrs = loadCorrections()

    plotDataDistributions(data)
    trueVectors = dict()
    sTrueVectors = dict()
    for energie, data in energiedatas.items():
        # print("E_lep: ", energie)
        # energies = []
        #  for event in data.getEvents():
        #     energies.append(event["E_lep"])
        # print("E_lep_data: ", average(energies) * 2)

        MeasVector = makeDataCut(data)
        # print("MeasVector: ")
        # print(MeasVector)

        # print("TrueVector:")
        trueVector = list(dot(inveffmatrix, MeasVector))
        sTrueVector = [sqrt(sum((inveffmatrix[i][j]*MeasVector[j])**2 * ((sinveffmatrix[i][j] / inveffmatrix[i][j])**2 + (sqrt(MeasVector[j]) / MeasVector[j])**2) for j in range(4))) for i in range(4)]
        old = trueVector[0]
        trueVector[0] = old * stRatios[energie][0]
        sTrueVector[0] = trueVector[0] * sqrt((sTrueVector[0] / old)**2 + (stRatios[energie][1] / stRatios[energie][0])**2)
        # print(trueVector)
        # print("")

        trueVectors[energie] = trueVector
        sTrueVectors[energie] = sTrueVector

    NDatas = [[] for i in range(4)]
    names = ['ee', 'mm', 'tt', 'qq']
    for energie in trueVectors.keys():
        for i in range(4):
            NDatas[i].append((energie, trueVectors[energie][i], sTrueVectors[energie][i]))

    crosssections = dict()
    for ctype, NData in zip(*[names, NDatas]):
        sigmas = calcCrossSection(ctype, NData, lums, corrs)
        crosssections[ctype] = sigmas
        with TxtFile('../calc/crosssections_%s.txt' % ctype, 'w') as f:
            for sigma in sigmas:
                f.writeline('\t', *list(map(str, sigma)))

if __name__ == '__main__':
    setupROOT()
    gStyle.SetOptStat(0)
    main()
