from numpy import sqrt
from numpy.linalg import inv  # inverse matrix
from functions import setupROOT
from z0 import Z0Data
from ROOT import gStyle, TCanvas, TLegend  # @UnresolvedImport
from txtfile import TxtFile

DEBUG = False  # TODO set False

CUTS = [("ee", lambda e: e["Ncharged"] <= 5 and e["E_ecal"] >= 70 and -0.9 <= e["cos_thet"] <= 0.9),
        ("mm", lambda e: e["Ncharged"] == 2 and e["E_ecal"] <= 50 and e["Pcharged"] >= 75),
        ("tt", lambda e: e["Ncharged"] <= 6 and 4 <= e["E_ecal"] <= 70 and 5 <= e["Pcharged"] <= 50),
        ("qq", lambda e: e["Ncharged"] >= 10)]


def plotDistribution(datas, datatype, binsize, xmin, xmax, prefix="dist_", normalize=True):
    if not DEBUG:
        c = TCanvas("c_%s" % (prefix+datatype), "", 1280, 720)
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


def calcEfficencyMatrix(cutdatas, datas):
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


def calcPurity(cutdatas, datas, cutnum):
    brs = [0.03363, 0.03366, 0.03370, 0.6991]  # branching rations Z -> (ee, mm, tt, qq)
    #sbrs = [0.00004, 0.00007, 0.00008, 0.0006]  # errors
    
    total = sum(map(lambda x: x[0].getLength() * x[1], zip(*[datas, brs]))) 
    eta = 1
    for i, cutdata in enumerate(cutdatas):
        if not i == cutnum:
            eta -= cutdata.getLength() * brs[i] / total
    return eta

def makeCut(datas, cut, cutnum, prefix=""):
    cutdatas = []
    for data in datas:
        cutdatas.append(data.cut(cut))
    plotDistributions(cutdatas, "cut_%s_" % prefix, False)
    return (calcEfficencyMatrix(cutdatas, datas), calcPurity(cutdatas, datas, cutnum))


def makeCuts(datas):
    efficencies = []
    sefficencies = []
    purities = []
    for cutnum, cutinfo in enumerate(CUTS):
        name, cut = cutinfo
        (effs, seffs), purity = makeCut(datas, cut, cutnum, name)
        efficencies.append(effs)
        sefficencies.append(seffs)
        purities.append(purity)
    with TxtFile('../calc/efficencies.txt', 'w') as f:
        f.write2DArrayToFile(efficencies, ['%.8f'] * 4)
    with TxtFile('../calc/efficencies_error.txt', 'w') as f:
        f.write2DArrayToFile(sefficencies, ['%.8f'] * 4)
    with TxtFile('../calc/invEfficencies.txt', 'w') as f:
        f.write2DArrayToFile(inv(efficencies), ['%.8f'] * 4)
    with TxtFile('../calc/purities.txt', 'w') as f:
        f.write2DArrayToFile(list(zip(*[purities])), ['%.6f'])

if __name__ == '__main__':
    setupROOT()
    gStyle.SetOptStat(0)
    # load data
    filenames = ['ee', 'mm', 'tt', 'qq']
    datas = list(map(lambda f: Z0Data.fromROOTFile('../data/mc/%s.root' % f, "h3"), filenames))

    plotDistributions(datas)
    makeCuts(datas)
