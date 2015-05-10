from numpy import log, log10, sqrt
from functions import setupROOT
from fitter import Fitter
from data import DataErrors
from ROOT import TCanvas, TLegend  # @UnresolvedImport

def main():
    z, sz = 840, 40
    d = [210, 106, 75]
    sd = [10, 4, 4]
    calc = list(map(lambda x:-20 * log10(x/z), d))
    scalc = list(map(lambda x:20 * sqrt((x[1]/x[0]) ** 2 + (sz/z)**2) / log(10), zip(*[d, sd])))
    
    data = DataErrors.fromLists(calc, [12, 18, 21], scalc, [0]*3)
    c = TCanvas('c', '', 1280, 720)
    g = data.makeGraph('g', 'measured attenuation m / dB', 'nominal value n / dB')
    g.Draw('AP')
    
    fit = Fitter('fit', 'pol1(0)')
    fit.setParam(0, 'a', 0)
    fit.setParam(1, 'b', 1)
    fit.fit(g, 11, 22)
    fit.saveData('../fit/attenuator.txt')
    
    l = TLegend(0.15, 0.6, 0.5, 0.85)
    l.SetTextSize(0.03)
    l.AddEntry(g, 'measured att. vs. nominal value', 'p')
    l.AddEntry(fit.function, 'fit with n = a + b m', 'l')
    fit.addParamsToLegend(l, (('%.2f', '%.2f'), ('%.2f', '%.2f')), chisquareformat='%.2f', units=['dB', ''], lang='en')
    l.Draw()
    
    c.Update()
    c.Print('../img/attenuator.pdf', 'pdf')

if __name__ == '__main__':
    setupROOT()
    main()