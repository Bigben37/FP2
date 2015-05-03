from numpy import sqrt
from cuts import CUTS
from functions import setupROOT
from fitter import Fitter
from z0 import Z0Data
from ROOT import gStyle, TCanvas, TLegend  # @UnresolvedImport


def makeFBAFit(energy, data):
    cutdata = data.cut(CUTS[1][1])
    c = TCanvas('c_%f' % energy, '', 1280, 720)
    hist = cutdata.makeHistogramm('hist_%f' % energy, 'cos_thet', 100, -1, 1)
    hist.Draw()
    
    if energy == 91.23223:
        fit = Fitter('fit_%d' % round(energy*100), "pi * (1/128.9)^2 / (2 * %f) * ([0]*(1+x^2) + 2 * [1] * x)" % (energy ** 2))
        fit.setParam(0, 'F_{1}', 1e10)
        fit.setParam(1, 'F_{2}', -4e8)
        fit.fit(hist, -0.9, 0.9, "M")
        
        l = TLegend(0.7, 0.7, 0.975, 0.95)
        l.SetTextSize(0.03)
        l.AddEntry(hist, 'daten_1 (mit mm-cut)', 'l')
        l.AddEntry(fit.function, 'Fit mit C(s) (F_{1} (1 + x^2) + 2 F_{2} x)', 'l')
        fit.addParamsToLegend(l, (('%.3e', '%.3e'), ('%.3e', '%.3e')), chisquareformat='%.2f')
        l.Draw()
        F1, sF1 = fit.params[0]["value"], fit.params[0]["error"]
        F2, sF2 = fit.params[1]["value"], fit.params[1]["error"]
        A = 3/4 * F2 / F1
        print(A)
        sA = A * sqrt((sF1 / F1)**2 + (sF2/F2)**2)
        sinW = 1/4 * (1 - sqrt(abs(A)/3))
        ssinW = sA / (8 * sqrt(3 * abs(A)))
    else:
        sinW, ssinW = None, None
    
    c.Update()
    c.Print("../img/FBA_%.5f.pdf" % energy, 'pdf')
    return sinW, ssinW
    
def main():
    datas = Z0Data.fromROOTFile('../data/daten/daten_1.root', 'h33')
    energiedatas = datas.splitEnergies()
    for energy, data in energiedatas.items():
        sinW, ssinW = makeFBAFit(energy, data)
        if sinW:
            print(sinW, ssinW)
        
        
if __name__ == '__main__':
    setupROOT()
    gStyle.SetOptStat(0)
    main()