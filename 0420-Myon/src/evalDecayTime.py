from functions import setupROOT
from myon import MyonData, prepareGraph
from fitter import Fitter
from ROOT import TCanvas, TLegend  # @UnresolvedImport


def main():
    xmin, xmax = 0.55, 8

    data = MyonData.fromPath('../data/zerfallszeit.TKA')
    data.convertToCountrate()
    data.convertChannelToTime()
    data.filterY(None, 0.2e-3)
    data.filterX(xmin, xmax)
    data = data.rebin(3)

    c = TCanvas('c', '', 1280, 720)
    g = data.makeGraph('g', 't / #mus', 'countrate n / (1/s)')
    prepareGraph(g)
    g.GetXaxis().SetRangeUser(0, 8.2)
    g.Draw('APX')

    fit = Fitter('fit', '[0]*1e-3*exp(-x/[1])')
    fit.setParam(0, 'A', 0.2)
    fit.setParam(1, '#tau', 2.2)
    fit.fit(g, xmin, xmax)
    fit.saveData('../fit/decayTime.txt')

    l = TLegend(0.6, 0.6, 0.85, 0.85)
    l.SetTextSize(0.03)
    l.AddEntry(g, 'measurement', 'p')
    l.AddEntry(fit.function, 'fit with n(t) = 10^{-3} A e^{- #frac{t}{#tau}}', 'l')
    fit.addParamsToLegend(l, (('%.3f', '%.3f'), ('%.2f', '%.2f')), chisquareformat='%.2f', units=['s', '#mus'], lang='de')
    l.Draw()

    g.Draw('P')
    c.Update()
    c.Print('../img/decayTime.pdf', 'pdf')

    c.SetLogy()
    c.Update()
    c.Print('../img/decayTime_log.pdf', 'pdf')

if __name__ == '__main__':
    setupROOT()
    main()
