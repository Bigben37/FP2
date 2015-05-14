from numpy import sqrt
from cuts import CUTS
from functions import setupROOT
from fitter import Fitter
from z0 import Z0Data
from ROOT import gStyle, TCanvas, TLegend  # @UnresolvedImport
from txtfile import TxtFile


def makeFBAFit(energy, data, binsize):
    cutdata = data.cut(CUTS[1][1])
    c = TCanvas('c_%f' % energy, '', 1280, 720)
    hist = cutdata.makeHistogramm('hist_%f' % energy, 'cos_thet', binsize, -1, 1)
    hist.Draw()
    
    if energy in [90.22720, 91.23223, 91.97109]:
        #fit = Fitter('fit_%d' % round(energy*100), "pi * (1/128.9)^2 / (2 * %f) * ([0]*(1+x^2) + 2 * [1] * x)" % (energy ** 2))
        fit = Fitter('fit_%d' % round(energy*100), "[0]*(1+x^2) + 2 * [1] * x")
        fit.setParam(0, 'F_{1}', 1e10)
        fit.setParam(1, 'F_{2}', -4e8)
        fit.fit(hist, -0.9, 0.9, "M")
        
        l = TLegend(0.65, 0.75, 0.98, 0.98)
        l.SetTextSize(0.03)
        l.AddEntry(hist, 'daten_1 (mit mm-cut)', 'l')
        l.AddEntry(fit.function, 'Fit mit F_{1} (1 + x^{2}) + 2 F_{2} x', 'l')
        fit.addParamsToLegend(l, (('%.3f', '%.3f'), ('%.3f', '%.3f')), chisquareformat='%.2f')
        l.Draw()
        F1, sF1 = fit.params[0]["value"], fit.params[0]["error"]
        F2, sF2 = fit.params[1]["value"], fit.params[1]["error"]
        A = 3/4 * F2 / F1
        sA = abs(A) * sqrt((sF1 / F1)**2 + (sF2/F2)**2)
        sinW = 1/4 * (1 - sqrt(abs(A)/3))
        ssinW = sA / (8 * sqrt(3 * abs(A)))
        res = A, sA, sinW, ssinW
    else:
        res = None
    
    c.Update()
    s = '%.5f' % energy
    c.Print("../img/FBA_%.5f.pdf" % s.replace('.', '-'), 'pdf')
    return res
    
def main():
    datas = Z0Data.fromROOTFile('../data/daten/daten_1.root', 'h33')
    energiedatas = datas.splitEnergies()
    binsizes = {88.48021:30, 89.47158:30, 90.22720:28, 91.23223:75, 91.97109:31, 92.97091:30, 93.71841:30}
    results = dict()
    for energy, data in energiedatas.items():
        res = makeFBAFit(energy, data, binsizes[energy])
        if res:
            results[energy] = res
            
    ressort = list(results.items())
    ressort.sort(key=lambda x: x[0])
    with TxtFile('../calc/FBA.txt', 'w') as f:
        for energy, res in ressort:
            f.writeline('\t', *map(lambda x:'%.5f' % x, [energy] + list(res)))
        
        
if __name__ == '__main__':
    setupROOT()
    gStyle.SetOptStat(0)
    main()