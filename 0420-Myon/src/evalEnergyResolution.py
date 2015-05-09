#!/usr/bin/python
import os
from functions import setupROOT, loadCSVToList
from myon import MyonData, prepareGraph
from ROOT import TCanvas, TLegend  # @UnresolvedImport
from fitter import Fitter
from data import DataErrors


def makeGraph(channel):
    data = MyonData.fromPath('../data/energieaufloesung_%s.TKA' % channel)
    data.convertToCountrate()

    c = TCanvas('c_%s' % channel, ', 1280, 720')
    g = data.makeGraph('g%s' % channel, 'channel c', 'countrate n / (1/s)')
    prepareGraph(g)
    g.GetXaxis().SetRangeUser(0, 700)
    g.Draw('APX')

    ch = int(channel)
    if ch < 100:
        xmin, xmax = ch - 25, ch + 25
    elif ch < 120:
        xmin, xmax = ch - 50, ch + 40
    elif ch < 200:
        xmin, xmax = ch - 50, ch + 50
    elif ch < 600:
        xmin, xmax = 0, 700
    else:
        xmin, xmax = 0, ch + 45

    fit = Fitter('fit_%s' % channel, '[0] + gaus(1)')
    fit.function.SetNpx(1000)
    fit.setParam(0, 'b', 0)  # offset
    fit.setParam(1, 'A', data.getMaxY())  # amplitude
    fit.setParam(2, 'x', ch)  # channel
    fit.setParam(3, '#sigma', 50)  # sigma
    #fit.setParamLimits(0, 0, 1000)
    fit.fit(g, xmin, xmax)
    fit.saveData('../fit/energieaufloesung_%s.txt' % channel)

    if ch > 350:
        l = TLegend(0.15, 0.5, 0.45, 0.85)
    else:
        l = TLegend(0.55, 0.5, 0.85, 0.85)
    l.SetTextSize(0.03)
    l.AddEntry(g, "measurement", 'p')
    l.AddEntry(fit.function, "fit with n(c) =", 'l')
    l.AddEntry(None, "b + A gaus(c; x, #sigma)", '')
    fit.addParamsToLegend(l, (('%.4f', '%.4f'), ('%.2f', '%.2f'), ('%.2f', '%.2f'), ('%.2f', '%.2f'),),
                          chisquareformat='%.2f', units=['1/s', '1/s', '', ''], lang='en')
    l.Draw()

    g.Draw('P')
    c.Update()
    c.Print('../img/energieaufloesung_%s.pdf' % channel, 'pdf')
    return (fit.params[2]['value'], fit.params[2]['error'], abs(fit.params[3]['value']), fit.params[3]['error'])  # abs(sigma)


def evalSigmaChannelDatas(datas):
    x = list(zip(*datas))[0]
    sx = list(zip(*datas))[1]
    y = list(zip(*datas))[2]
    sy = list(zip(*datas))[3]
    data = DataErrors.fromLists(x, y, sx, sy)

    c = TCanvas('c_sc', '', 1280, 720)
    g = data.makeGraph('g_sc', 'channel c', '#sigma(channels)')
    g.Draw('AP')
    c.Update()
    c.Print('../img/energieaufloesung_channels.pdf', 'pdf')

    ecallist = loadCSVToList('../calc/ecal_sigmas.txt')
    x, sx, y, sy = list(zip(*ecallist))
    ecaldata = DataErrors.fromLists(x, y, sx, sy)
    
    g.SetMaximum(50)
    g.Draw('AP')
    gecal = ecaldata.makeGraph('g_ecal', 'channel c', '#sigma(channels)')
    gecal.SetMarkerColor(2)
    gecal.SetLineColor(2)
    gecal.Draw('P')

    l = TLegend(0.15, 0.7, 0.5, 0.85)
    l.SetTextSize(0.03)
    l.AddEntry(g, 'fitted #sigma of LED-Peaks', 'p')
    l.AddEntry(gecal, 'fitted #sigma of energy calibration peaks', 'p')
    l.Draw()

    c.Update()
    c.Print('../img/energieaufloesung_channels+ecal.pdf', 'pdf')


def makeMultiGraph(files):
    c = TCanvas('c_m', '', 1280, 720)

    graphs = []
    for file in files:
        if file.startswith('energieaufloesung'):
            data = MyonData.fromPath('../data/%s' % file)
            data.convertToCountrate()
            graphs.append(data.makeGraph('g_%s' % file, 'channel c', 'countrate n / (1/s)'))

    first = True
    for i, g in enumerate(graphs):
        g.SetMarkerStyle(1)
        g.SetMarkerColor(int(round(51 + (100. - 51) / 11 * i)))
        g.GetXaxis().SetRangeUser(0, 700)
        g.SetMaximum(100)
        if first:
            g.Draw('APX')
            first = False
        else:
            g.Draw('PX')
    c.Update()
    c.Print('../img/energieaufloesung_multi.pdf', 'pdf')


def main():
    files = os.listdir(os.path.join(os.getcwd(), '../data/'))
    files.sort()
    sigmaChannelDatas = []
    for file in files:
        if file.startswith('energieaufloesung'):
            sigmaChannelDatas.append(makeGraph(file[-7:-4]))
    evalSigmaChannelDatas(sigmaChannelDatas)
    makeMultiGraph(files)


if __name__ == "__main__":
    setupROOT()
    main()
