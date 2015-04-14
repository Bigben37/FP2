#!/usr/bin/python

__author__ = "Benjamin Rottler (benjamin@dierottlers.de)"

from numpy import sqrt
from functions import setupROOT
from evalEtalon import evalEtalonData
from data import DataErrors
import os
from ROOT import TCanvas, TLegend
from fitter import Fitter


def evalEtalons():
    files = ['23-64.1mA-34.0C.tab', '28a-62.8mA-34.0C.tab', '32-61.9mA-34.0C.tab', '36-64.8mA-34.0C.tab']
    xminmaxs = [(0.00084, 0.0041), (0.00076, 0.00245), (0.000065, 0.00053), (0.00014, 0.0005)]
    for file, xminmax in zip(*(files, xminmaxs)):
        laserVoltageFit, peakfits = evalEtalonData(2, file, xminmax)
        m, sm = laserVoltageFit[1]  # V/s
        m *= 40  # mA/s
        sm *= 40  # mA/s
        xoffset, sxoffset = peakfits[0]
        xlist = list(map(lambda peak: peak[0] * m - xoffset, peakfits))
        sxlist = list(map(lambda peak: sqrt((peak[0] * m * sqrt((peak[1] / peak[0]) ** 2 + (sm / m) ** 2)) ** 2 + sxoffset ** 2), peakfits))
        ylist = list(map(lambda i: i * 9.924, range(len(peakfits))))
        sylist = list(map(lambda i: i * 0.03, range(len(peakfits))))

        etalonData = DataErrors.fromLists(xlist, ylist, sxlist, sylist)
        c = TCanvas('c' + file, '', 1280, 720)
        g = etalonData.makeGraph('g' + file, '#Delta I / mA', '#Delta#nu / GHz')
        g.SetMinimum(-5)
        g.SetMaximum(max(ylist) + 5)
        g.Draw('AP')

        fit = Fitter('fit' + file, 'pol1(0)')
        fit.setParam(0, 'a')
        fit.setParam(1, 'b')
        fit.fit(g, min(xlist) - 2, max(xlist) + 2)
        fit.saveData('../fit/part2/%s-etalon_gauge.txt' % file)

        if fit.params[1]['value'] < 0:
            l = TLegend(0.575, 0.6, 0.85, 0.85)
        else:
            l = TLegend(0.15, 0.6, 0.425, 0.85) 
        l.SetTextSize(0.03)
        l.AddEntry(g, 'Messwerte', 'p')
        l.AddEntry(fit.function, 'Fit mit #Delta#nu = a + b * #Delta I', 'l')
        fit.addParamsToLegend(l, [('%.2f', '%.2f'), ('%.3f', '%.3f')], chisquareformat='%.2f', units=('GHz', 'GHz/mA'))
        l.Draw()

        c.Update()
        c.Print('../img/part2/%s-etalon_gauge.pdf' % file, 'pdf')


def main():
    evalEtalons()

if __name__ == '__main__':
    setupROOT()
    main()
