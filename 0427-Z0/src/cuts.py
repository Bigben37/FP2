from numpy import sqrt, matrix
from functions import setupROOT
from z0 import Z0Data
from ROOT import gStyle, TCanvas, TLegend


def plotDistribution(datas, type, binsize, xmin, xmax, prefix="dist_"):
    c = TCanvas("c_%s" % type, "", 1280, 720)
    hists = []
    maxs = []
    for i, data in enumerate(datas):
        hists.append(data.makeHistogramm('hist_%s_%d' % (type, i), type, binsize, xmin, xmax))
        hists[i].SetLineColor(i + 1)
        n = hists[i].GetEntries()
        if n > 0:
            hists[i].Scale(1 / n)
        maxs.append(hists[i].GetMaximum())

    hists[0].SetMaximum(max(maxs) * 1.1)
    hists[0].GetXaxis().SetTitle(type)
    hists[0].GetXaxis().CenterTitle()
    hists[0].GetYaxis().SetTitle('rel. Counts')
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
    c.Print("../img/%s%s.pdf" % (prefix, type), "pdf")


def plotDistributions(datas, prefix="dist_"):
    types = ["Ncharged", "Pcharged", "E_ecal", "E_hcal", "cos_thru", "cos_thet"]
    rangeparams = [(40, 0, 40), (120, 0, 120), (120, 0, 120), (45, 0, 45), (200, -1, 1), (200, -1, 1)]
    for type, rangepars in zip(*[types, rangeparams]):
        plotDistribution(datas, type, rangepars[0], rangepars[1], rangepars[2], prefix)


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


def makeCut(datas, cut):  # TODO prefix for different cuts
    cutdatas = []
    for data in datas:
        cutdatas.append(data.cut(cut))
    plotDistributions(cutdatas, "cut_")
    return calcEfficencyVector(cutdatas, datas)


def makeCuts(datas):  # TODO DEBUG switch => dont print graphs to file
    cuts = [lambda e: e["Ncharged"] <= 5 and e["E_ecal"] >= 70,
            lambda e: e["Ncharged"] == 2 and e["E_ecal"] <= 50 and e["Pcharged"] >= 75,
            lambda e: e["Ncharged"] <= 4 and 4 <= e["E_ecal"] <= 70 and e["Pcharged"] <= 70,
            lambda e: e["Ncharged"] >= 10]
    efficencies = []
    sefficencies = []
    for cut in cuts:
        effs, seffs = makeCut(datas, cut)
        efficencies.append(effs)
        sefficencies.append(seffs)
    m = matrix(efficencies)
    sm = matrix(sefficencies)
    print(m)
    print(sm)

if __name__ == '__main__':
    setupROOT
    gStyle.SetOptStat(0)
    # load data
    filenames = ['ee', 'mm', 'tt', 'qq']
    datas = list(map(lambda f: Z0Data.fromROOTFile('../data/mc/%s.root' % f, "h3"), filenames))

    # plotDistributions(datas)
    makeCuts(datas)
