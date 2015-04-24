#!/usr/bin/python
from functions import setupROOT
from data import DataErrors
from ROOT import TCanvas, TLegend
from fitter import Fitter

def main():
    times = [2.4, 4.5, 6.25, 8.6]
    times_error = [0.02] * len(times)
    channels = [113, 223, 315.5, 441]
    channels_error = [0.5] * len(times)
    
    data = DataErrors.fromLists(channels, times, channels_error, times_error)
    c = TCanvas('c', '', 1280, 720)
    g = data.makeGraph('g', 'channel c', 'time t / #mus')
    g.Draw('APX')
    
    fit = Fitter('fit', 'pol1(0)')
    fit.setParam(0, 'a', 0)
    fit.setParam(1, 'b', 50)
    fit.fit(g, 100, 450)
    fit.saveData('../fit/timeGauge.txt')
    
    l = TLegend(0.15, 0.6, 0.5, 0.85)
    l.SetTextSize(0.03)
    l.AddEntry(g, 'TODO Beschriftung', 'p')
    l.AddEntry(fit.function, 'fit with t(c) = a + b * c', 'l')
    fit.addParamsToLegend(l, (('%.2f', '%.2f'), ('%.5f', '%.5f')), chisquareformat='%.2f', units=('#mus', '#mus/channel'), lang='en')
    l.Draw()
    
    g.Draw('P')
    c.Update()
    c.Print('../img/timeGauge.pdf', 'pdf')

if __name__ == "__main__":
    setupROOT()
    main()