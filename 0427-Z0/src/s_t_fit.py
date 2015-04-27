from z0 import Z0Data
from functions import setupROOT
from fitter import Fitter
from ROOT import gStyle, TCanvas, TLegend # @UnresolvedImport

def main():
    data = Z0Data.fromROOTFile('../data/mc/ee.root', 'h3')
    datacut = data.cut(lambda e: e["Ncharged"] <= 5 and e["E_ecal"] >= 70)
    
    c = TCanvas('c', '', 1280, 720)
    hist = datacut.makeHistogramm('hist', 'cos_thet', 200, -1, 1)  # TODO params for hist title (defualt = '')
    hist.Draw()
    
    fit = Fitter('f', '[0] * (1 + x^{2}) + [1] * (1 - x)^(-2)')
    fit.setParam(0, 's', 100)
    fit.setParam(1, 't', 10)
    fit.fit(hist, -0.9, 0.9)
    fit.saveData('../fit/s_t_fit.txt')
    
    l = TLegend(0.15, 0.6, 0.5, 0.85)
    l.AddEntry(hist, "ee (mit cut)", 'l')
    l.AddEntry(fit.function, 'Fit mit N = s (1 + x^2) + t (1 - x)^{-2}', 'l')
    fit.addParamsToLegend(l, [('%.2f', '%.2f'), ('%.2f', '%.2f')], chisquareformat='%.2f')
    l.Draw()
    
    #g.Draw('P')
    c.Update()
    c.Print('../img/s_t_fit.pdf', 'pdf')

if __name__ == '__main__':
    setupROOT()
    gStyle.SetOptStat(0)
    main()