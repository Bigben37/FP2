from numpy import sqrt
from functions import setupROOT
from myon import MyonData, prepareGraph
from ROOT import TCanvas, TLegend  # @UnresolvedImport
from fitter import Fitter
from txtfile import TxtFile


def evalUnderground():
    data1 = MyonData.fromPath('../data/untergrund.TKA')
    data2 = MyonData.fromPath('../data/untergrund_2.TKA')
    data = MyonData.fromDataErrors(data1 + data2, data1.time + data2.time, data1.timed + data2.timed)
    data.convertToCountrate()
    data = data.rebin(20)
    
    c = TCanvas('cu', '', 1280, 720)
    g = data.makeGraph('gu', 'channel c', 'countrate n / (1/s)')
    prepareGraph(g)
    g.GetXaxis().SetRangeUser(0, 700)
    g.Draw('AP')
    c.Update()
    c.Print('../img/underground.pdf', 'pdf')

def makeEnergyPlot():
    data = MyonData.fromPath('../data/betaspektrum.TKA')
    data.convertToCountrate()
    
    c = TCanvas('c', '', 1280, 720)
    g = data.makeGraph('g', 'channel c', 'countrate n / (1/s)')
    prepareGraph(g)
    g.GetXaxis().SetRangeUser(0, 250)
    g.GetYaxis().SetTitleOffset(1.2)
    g.Draw('AP')
    c.Update()
    c.Print('../img/betaspectrum.pdf', 'pdf')
    
def calcFermiKuriePlot(data):
    new = MyonData()
    for (x, y, sx, sy) in data.getPoints():
        ny = sqrt(y/x**2)  # sqrt(N/E^2)
        if not y == 0:
            nsy = sqrt(sy**2/(4 * x**2 * y) + (sx**2 * y)/x**4)  # sy / y^2
        else:
            nsy = 0
        new.addPoint(x, ny, sx, nsy)
    return new
    
def makeFermiKuriePlot():
    data = MyonData.fromPath('../data/betaspektrum.TKA')
    data.convertToCountrate()
    data.convertChannelToEnergy()
    data = calcFermiKuriePlot(data)
    
    c = TCanvas('c', '', 1280, 720)
    g = data.makeGraph('g', 'energy E / MeV', '#sqrt{n/E^{2}}')
    prepareGraph(g)
    g.GetXaxis().SetRangeUser(0, 150)
    g.SetMaximum(0.004)
    g.GetYaxis().SetTitleOffset(1.3)
    g.Draw('APX')
    g.Draw('P')
    c.Update()
    c.Print('../img/betaspectrum_FermiKurie.pdf', 'pdf') 
    
    g.GetXaxis().SetRangeUser(0, 80)
    g.SetMaximum(3e-3)
    
    fit = Fitter('fit', '[0]*(x-[1])*1e-6')
    fit.setParam(0, 'a', -0.3)
    fit.setParam(1, 'b', 55)
    fit.fit(g, 23, 45)
    fit.saveData('../fit/FermiKurie.txt')
    
    l = TLegend(0.65, 0.6, 0.85, 0.85)
    l.SetTextSize(0.03)
    l.AddEntry(g, 'Fermi-Kurie plot', 'p')
    l.AddEntry(fit.function, 'fit with a(E-b)', 'l')
    fit.addParamsToLegend(l, (('%.2f', '%.2f'), ('%.2f', '%.2f')), chisquareformat='%.2f', units=["10^{-6}", ""], lang='en')
    l.Draw()
    
    c.Update()
    c.Print('../img/betaspectrum_FermiKurie_fit.pdf', 'pdf') 
    
    return fit.params[1]["value"], fit.params[1]["error"]

def main():
    evalUnderground()
    makeEnergyPlot()
    e, se = makeFermiKuriePlot()
    E = e*2
    sE = se * 2
    print(E, sE)
    with TxtFile('../calc/energy.txt', 'w') as f:
        f.writeline('\t', *map(lambda x:'%.2f' % x, (e, se)))
        f.writeline('\t', *map(lambda x:'%.2f' % x, (E, sE)))

if __name__ == '__main__':
    setupROOT()
    main()