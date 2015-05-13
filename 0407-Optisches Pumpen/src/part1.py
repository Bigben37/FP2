#!/usr/bin/python

__author__ = "Benjamin Rottler (benjamin@dierottlers.de)"

from numpy import sqrt
# ========================================================================
# make sure to add ../../lib to your project path or copy files from there
from fitter import Fitter
from op import OPData
from functions import setupROOT, loadCSVToList
from data import DataErrors
# ========================================================================
from ROOT import TCanvas, TLegend, TLine


def evalDiode():
    datalist = loadCSVToList('../data/part1/Kennlinie.txt')
    data = DataErrors()
    U0 = datalist[0][1]
    sU0 = 0.05 + 0.01 * U0
    for I, u in datalist:
        U = u - U0
        su = 5 + 0.01 * u
        sU = sqrt(su ** 2 + sU0 ** 2)
        data.addPoint(I, U, 0.1, sU)
    xmin, xmax = 53, 71.5

    c = TCanvas('c_diode', '', 1280, 720)
    g = data.makeGraph('g_diode', "Laserstrom I_{L} / mA", "Photodiodenspannung U_{ph} / mV")
    g.GetXaxis().SetRangeUser(-5, 90)
    g.SetMinimum(-50)
    g.SetMaximum(1400)
    g.Draw('APX')

    # y=0 line
    line = TLine(-5, 0, 90, 0)
    line.SetLineColor(OPData.CH2ECOLOR)
    line.Draw()

    data.filterX(xmin, xmax)
    g2 = data.makeGraph('g_diode_2', "Laserstrom I_{L} / mA", "Photodiodenspannung U_{ph} / mV")
    g2.SetMarkerColor(OPData.CH1COLOR)
    g2.SetLineColor(OPData.CH1COLOR)

    fit = Fitter('fit_diode', '[0] * (x-[1])')
    fit.function.SetNpx(1000)
    fit.setParam(0, 'a', 1)
    fit.setParam(1, 'I_{th}', 50)
    fit.fit(g2, 40, 77)
    fit.saveData('../fit/part1/kennlinie.txt')

    l = TLegend(0.15, 0.55, 0.4, 0.85)
    l.SetTextSize(0.03)
    l.AddEntry(g, 'Laserdiodenkennlinie', 'p')
    l.AddEntry(g2, 'Ausschnitt zum Fitten', 'p')
    l.AddEntry(fit.function, 'Fit mit U_{ph} = a (I_{ L} - I_{ th} )', 'l')
    fit.addParamsToLegend(l, (('%.1f', '%.1f'), ('%.2f', '%.2f')), chisquareformat='%.2f', units=['mV/mA', 'mA'])
    l.Draw()

    g.Draw('P')
    g2.Draw('P')

    c.Update()
    c.Print('../img/part1/diodenkennlinie.pdf', 'pdf')


def main():
    evalDiode()

if __name__ == '__main__':
    setupROOT()
    main()
