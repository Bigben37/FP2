import os
from numpy import sqrt
# ========================================================================
# make sure to add ../../lib to your project path or copy files from there
from functions import setupROOT, loadCSVToList
from op import OPData, prepareGraph, inductorIToB
from data import DataErrors
from fitter import Fitter
# ========================================================================
from ROOT import TCanvas, TLegend

DIR = '../data/part4/'


def makeGraph(name):
    file = DIR + name + '.tab'
    ch1 = OPData.fromPath(file, 1)
    ch2 = OPData.fromPath(file, 2)

    c = TCanvas('c_%s' % name, '', 1280, 720)
    g1 = ch1.makeGraph('g1_%s' % name, 'Zeit t/s', 'Spannung U/V')
    g2 = ch2.makeGraph('g1_%s' % name, 'Zeit t/s', 'Spannung U/V')
    if int(name[:2]) < 4:
        prepareGraph(g1, 2)
        prepareGraph(g2, 1)
    else:
        prepareGraph(g1, 1)
        prepareGraph(g2, 2)

    g1.GetXaxis().SetRangeUser(0, ch1.getMaxX())
    ymin = min(ch1.getMinY(), ch2.getMinY())
    ymax = max(ch1.getMaxY(), ch2.getMaxY())
    deltaY = abs(ymax - ymin) * 0.05
    g1.SetMinimum(ymin - deltaY)
    g1.SetMaximum(ymax + deltaY)

    g1.Draw('APX')
    g1.Draw('P')
    g2.Draw('PX')
    g2.Draw('P')

    l = TLegend(0.55, 0.7, 0.85, 0.85)
    l.SetTextSize(0.03)
    if int(name[:2]) < 4:
        l.AddEntry(g1, 'Photodiodenspannung U_{ph}', 'l')
        l.AddEntry(g2, 'Spannung U_{5} an Spule 5', 'l')
    else:
        l.AddEntry(g2, 'Photodiodenspannung U_{ph}', 'l')
        l.AddEntry(g1, 'Spannung U_{5} an Spule 5', 'l')
    l.Draw()

    c.Update()
    c.Print('../img/part4/%s.pdf' % name.replace('.', '-'), 'pdf')


def makeGraphs():
    files = os.listdir(os.path.join(os.getcwd(), DIR))
    files.sort()
    for file in files:
        if file.endswith('.tab'):
            makeGraph(file[:-4])


def calcPrecissionFreq(t2, t1, n):
    strel = 0.01
    f = n / (t2 - t1)
    sf = n * sqrt(2) * sqrt((t1 * strel) ** 2 + (t2 * strel) ** 2) / ((t2 - t1) ** 2)
    return f, sf


def evalSpinPrecission(name):
    datalist = loadCSVToList(DIR + name + '.txt')
    data = DataErrors()
    sI = 1
    for t2, t1, n, I in datalist:
        f, sf = calcPrecissionFreq(t2, t1, n)
        B, sB = inductorIToB(4, I * 1e-3, sI * 1e-3)
        data.addPoint(B * 1e6, f, sB * 1e6, sf)

    if len(name) == 4:
        xmin, xmax = 0, 50
    else:
        xmin, xmax = 0, 80

    c = TCanvas('c_%s' % name, '', 1280, 720)
    g = data.makeGraph('g_%s' % name, 'Zusaetzliches Vertikalfeld B_{S, v} / #muT', 'Praezessionsfrequenz f / kHz')
    g.GetXaxis().SetRangeUser(xmin, xmax)
    g.Draw('APX')

    fit1 = Fitter('fit1_%s' % name, '[0] * abs([1]-x)')
    fit1.function.SetNpx(1000)
    fit1.setParam(0, '#alpha', 1)
    fit1.setParam(1, 'B_{E, v}', 40)
    fit1.fit(g, xmin, xmax)
    fit1.saveData('../fit/part4/fit1_%s' % name)

    fit2 = Fitter('fit1_%s' % name, '[0] * (abs([1]-x) + [2])')
    fit2.function.SetNpx(1000)
    fit2.function.SetLineColor(3)
    fit2.setParam(0, '#alpha', 1)
    fit2.setParam(1, 'B_{E, v}', 40)
    fit2.setParam(2, 'B_{E,h,s}', 20)
    fit2.setParamLimits(2, 0, 100)
    fit2.fit(g, xmin, xmax, '+')
    fit2.saveData('../fit/part4/fit2_%s' % name)

    g.Draw('P')

    if len(name) == 4:
        l = TLegend(0.6, 0.4, 0.975, 0.95)
    else:
        l = TLegend(0.325, 0.475, 0.725, 0.99)
    l.SetTextSize(0.03)
    l.AddEntry(g, 'Praezessionsfrequenzen', 'p')
    l.AddEntry(fit1.function, 'Fit mit f_{1}(B_{S, v}) = #alpha |B_{E, v} - B_{S, v}|', 'l')
    fit1.addParamsToLegend(l, (('%.2f', '%.2f'), ('%.2f', '%.2f')), chisquareformat='%.2f', units=['kHz/#muT', '#muT'])
    l.AddEntry(fit2.function, 'Fit mit f_{2}(B_{S, v}) = #alpha (|B_{E, v} - B_{S, v}| + B_{E,h,s})', 'l')
    fit2.addParamsToLegend(l, (('%.2f', '%.2f'), ('%.2f', '%.2f'), ('%.2f', '%.2f')),
                           chisquareformat='%.2f', units=['kHz/#muT', '#muT', '#muT'])
    l.Draw()

    c.Update()
    c.Print('../img/part4/%s.pdf' % name, 'pdf')


def evalAngleDependency():
    datalist = loadCSVToList(DIR + 'Winkelabh.txt')
    data = DataErrors()
    strel = 0.01
    sI = 1
    for t2, t1, n, phi in datalist:
        f, sf = calcPrecissionFreq(t2, t1, n)
        data.addPoint(phi, f, 0.5, sf)

    c = TCanvas('c_phi', '', 1280, 720)
    g = data.makeGraph('g_phi', 'Rotation des Strahlengangs #varphi / #circ', 'Praezessionsfrequenz f / kHz')
    g.GetXaxis().SetRangeUser(-15, 15)
    g.SetMinimum(0)
    g.Draw('APX')

    fit = Fitter('fit_phi', '[0] * abs(sin((x-[1])*pi/180))')
    fit.function.SetNpx(1000)
    fit.setParam(0, '#beta', 1)
    fit.setParam(1, '#phi_{0}', 0)
    fit.fit(g, -15, 15)
    fit.saveData('../fit/part4/winkel.txt')

    g.Draw('P')

    l = TLegend(0.7, 0.15, 0.95, 0.5)
    l.SetTextSize(0.03)
    l.AddEntry(g, 'Praezessionsfrequenz', 'p')
    l.AddEntry(fit.function, 'Fit mit f = #beta |sin(#varphi + #varphi_{0})|', 'l')
    fit.addParamsToLegend(l, (('%.1f', '%.1f'), ('%.2f', '%.2f')), chisquareformat='%.2f', units=['kHz/#muT', '#circ'])
    l.Draw()

    c.Update()
    c.Print('../img/part4/winkel.pdf', 'pdf')


def main():
    makeGraphs()
    spinprecs = ['Rb85', 'Rb85_gedreht', 'Rb87']  # TODO gedreht größerer Bereich
    for spinprec in spinprecs:
        evalSpinPrecission(spinprec)
    evalAngleDependency()

if __name__ == '__main__':
    setupROOT()
    main()
