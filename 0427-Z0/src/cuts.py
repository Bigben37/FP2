from numpy import sqrt, matrix
from functions import setupROOT
from z0 import Z0Data
from ROOT import gStyle, TCanvas, TLegend  # @UnresolvedImport
from txtfile import TxtFile

DEBUG = False


def plotDistribution(datas, datatype, binsize, xmin, xmax, prefix="dist_", normalize=True):
    if not DEBUG:
        c = TCanvas("c_%s" % datatype, "", 1280, 720)
        hists = []
        maxs = []
        for i, data in enumerate(datas):
            hists.append(data.makeHistogramm('hist_%s_%d' % (datatype, i), datatype, binsize, xmin, xmax))
            hists[i].SetLineColor(i + 1)
            n = hists[i].GetEntries()
            if normalize and n > 0:
                hists[i].Scale(1 / n)
            maxs.append(hists[i].GetMaximum())

        hists[0].SetMaximum(max(maxs) * 1.1)
        hists[0].GetXaxis().SetTitle(datatype)
        hists[0].GetXaxis().CenterTitle()
        if normalize:
            hists[0].GetYaxis().SetTitle('rel. Anzahl der Ereignisse')
        else:
            hists[0].GetYaxis().SetTitle('Anzahl der Ereignisse')
        hists[0].GetYaxis().CenterTitle()

        for i, hist in enumerate(hists):
            if i == 0:
                hist.Draw()
            else:
                hist.Draw("same")

        lentries = ["ee", "mm", "tt", "qq"]
        l = TLegend(0.65, 0.65, 0.85, 0.85)
        for name, hist in zip(*[lentries, hists]):
            l.AddEntry(hist, name, 'l')
        l.Draw()

        c.Update()
        c.Print("../img/%s%s.pdf" % (prefix, datatype), "pdf")


def plotDistributions(datas, prefix="dist_", normalize=True):
    types = ["Ncharged", "Pcharged", "E_ecal", "E_hcal", "cos_thru", "cos_thet"]
    rangeparams = [(40, 0, 40), (120, 0, 120), (120, 0, 120), (45, 0, 45), (200, -1, 1), (200, -1, 1)]
    for datatype, rangepars in zip(*[types, rangeparams]):
        plotDistribution(datas, datatype, rangepars[0], rangepars[1], rangepars[2], prefix, normalize)


def calcEfficencyVector(cutdatas, datas):
    effs = []
    seffs = []
    for cutdata, data in zip(*[cutdatas, datas]):
        c = cutdata.getLength()
        n = data.getLength()
        eff = c / n
        seff = sqrt(eff * (1 - eff) / n)
        effs.append(eff)
        seffs.append(seff)
    return effs, seffs


def makeCut(datas, cut, prefix=""):  # TODO prefix for different cuts
    cutdatas = []
    for data in datas:
        cutdatas.append(data.cut(cut))
    plotDistributions(cutdatas, "cut_%s_" % prefix, False)
    return calcEfficencyVector(cutdatas, datas)


def makeCuts(datas):
    cuts = [("ee", lambda e: e["Ncharged"] <= 5 and e["E_ecal"] >= 70),
            ("mm", lambda e: e["Ncharged"] == 2 and e["E_ecal"] <= 50 and e["Pcharged"] >= 75),
            ("tt", lambda e: e["Ncharged"] <= 4 and 4 <= e["E_ecal"] <= 70 and e["Pcharged"] <= 70),
            ("qq", lambda e: e["Ncharged"] >= 10)]
    efficencies = []
    sefficencies = []
    for name, cut in cuts:
        effs, seffs = makeCut(datas, cut, name)
        efficencies.append(effs)
        sefficencies.append(seffs)
    m = matrix(efficencies)
    sm = matrix(sefficencies)
    print(m)
    print(sm)
    with TxtFile('../calc/efficencies.txt', 'w') as f:
        f.write2DArrayToFile(efficencies, ['%.6f'] * 4)
    with TxtFile('../calc/efficencies_error.txt', 'w') as f:
        f.write2DArrayToFile(sefficencies, ['%.6f'] * 4)

if __name__ == '__main__':
    setupROOT()
    gStyle.SetOptStat(0)
    # load data
    filenames = ['ee', 'mm', 'tt', 'qq']
    datas = list(map(lambda f: Z0Data.fromROOTFile('../data/mc/%s.root' % f, "h3"), filenames))

    plotDistributions(datas)
    makeCuts(datas)
