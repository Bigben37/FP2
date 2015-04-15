#!/usr/bin/python

__author__ = "Benjamin Rottler (benjamin@dierottlers.de)"

from numpy import sqrt
from functions import setupROOT
from data import DataErrors
from op import OPData, prepareGraph, avgCloseValues
from ROOT import TCanvas, TLegend, TGaxis
from fitter import Fitter


def getFitStartX(xmin, xmax, ch2):
    ch2max = ch2.findExtrema(15, xmin, xmax, False).getX()
    return avgCloseValues(ch2max, 10 * ch2.getMinDeltaX())  # combine peaks which are closer than epsilon together


def fitEtalonPeak(g, peakx, sigma, color, part, file):
    fit = Fitter('%s-peak%d' % (file, color - 4), '[0]+[1]*x+gaus(2)')
    fit.function.SetLineColor(color)
    fit.setParam(0, 'a', -0.6)
    fit.setParam(1, 'b', 0.2)
    fit.setParam(2, 'A', 0.6)
    fit.setParam(3, 'c', peakx)
    fit.setParam(4, 's', sigma)
    fit.fit(g, peakx - sigma, peakx + sigma, '+')  # TODO instead of global sigma get x bounds with neighbor minima
    fit.saveData('../fit/part%d/%s-peak%d.txt' % (part, file, color - 4))
    return fit.params[3]['value'], fit.params[3]['error']


def fitLaserVoltage(g, xmin, xmax, part, file):
    fit = Fitter('%s-laser' % file, 'pol1(0)')
    fit.function.SetLineColor(3)
    fit.setParam(0, 'a', -0.6)
    fit.setParam(1, 'b', 200)
    fit.fit(g, xmin, xmax)
    fit.saveData('../fit/part%d/%s-laser.txt' % (part, file))
    return [(fit.params[0]['value'], fit.params[0]['error']), (fit.params[1]['value'], fit.params[1]['error'])]


def evalEtalonData(part, path, xminmax):
    dir = '../data/part%d/' % part
    ch1 = OPData.fromPath(dir + path, OPData.CH1)
    ch2 = OPData.fromPath(dir + path, OPData.CH2)

    c = TCanvas('c', '', 1280, 720)

    # make graphs
    g1 = ch1.makeGraph('ch1', 't / s', 'U / V')
    prepareGraph(g1)
    g1.SetMaximum(max(ch2.getY()) * 1.1)
    g1.SetMinimum(min((min(ch2.getY()), min(ch1.getY()))) * 1.2)
    g1.GetXaxis().SetRangeUser(0, max(ch1.getX()))
    g2 = ch2.makeGraph('ch2')
    prepareGraph(g2)
    g2.SetMarkerColor(2)  # TODO red error bars?
    g1.Draw('AP')
    g1.Draw('PX')  # redraw points without errors to set points in front of errors
    g2.Draw('P')
    g2.Draw('PX')  # redraw points without errors to set points in front of errors

    xmin2, xmax2 = xminmax
    xmin = xmin2 + OPData.OFFSET
    xmax = xmax2 + OPData.OFFSET
    peakxs = getFitStartX(xmin, xmax, ch2)
    sigmamult = 100
    if path == '23-64.1mA-34.0C.tab':
        peakxs = peakxs[:-2]
    if path == '32-61.9mA-34.0C.tab':
        peakxs = peakxs[3:]
    if path == '36-64.8mA-34.0C.tab':
        peakxs = [0.000365] + peakxs
        sigmamult = 50
    # get fits
    sigma = ch1.getMinDeltaX() * sigmamult
    peakfits = []
    for i, peakx in enumerate(peakxs):
        peakfits.append(fitEtalonPeak(g2, peakx, sigma, i % 8 + 4, part, path[:-4]))
    
    fitLaserVoltage(g1, xmin2, xmax2, part, path[:-4])

    c.Update()
    c.Print('../img/part%d/%s.pdf' % (part, path[:-4]), 'pdf')

    return peakfits


def evalEtalons():
    #files = ['23-64.1mA-34.0C.tab', '28a-62.8mA-34.0C.tab', '32-61.9mA-34.0C.tab', '36-64.8mA-34.0C.tab']
    files = ['23-64.1mA-34.0C.tab']
    xminmaxs = [(0.00084, 0.0041), (0.00076, 0.00245), (0.000065, 0.00053), (0.00014, 0.0005)]
    fitres = []
    for file, xminmax in zip(*(files, xminmaxs)):
        peakfits = evalEtalonData(2, file, xminmax)
        xlist = list(list(zip(*peakfits))[0])
        sxlist = list(list(zip(*peakfits))[1])
        ylist = list(map(lambda i: i * 9.924, range(len(peakfits))))
        sylist = list(map(lambda i: i * 0.03, range(len(peakfits))))

        etalonData = DataErrors.fromLists(xlist, ylist, sxlist, sylist)
        etalonData.multiplyX(1000)
        c = TCanvas('c' + file, '', 1280, 720)
        g = etalonData.makeGraph('g' + file, 't / ms', '#Delta#nu / GHz')
        g.SetMinimum(-5)
        g.SetMaximum(max(ylist) + 5)
        g.Draw('AP')

        fit = Fitter('fit' + file, 'pol1(0)')
        fit.setParam(0, 'a')
        fit.setParam(1, 'b')
        xmin, xmax = min(etalonData.getX()), max(etalonData.getX())
        deltax = (xmax - xmin) / 10
        fit.fit(g, xmin - deltax, xmax + deltax)
        fit.saveData('../fit/part2/%s-etalon_gauge.txt' % file)

        if fit.params[1]['value'] < 0:
            l = TLegend(0.575, 0.6, 0.85, 0.85)
        else:
            l = TLegend(0.15, 0.6, 0.425, 0.85)
        l.SetTextSize(0.03)
        l.AddEntry(g, 'Etalonpeaks', 'p')
        l.AddEntry(fit.function, 'Fit mit #Delta#nu = a + b * t', 'l')
        fit.addParamsToLegend(l, [('%.2f', '%.2f'), ('%.2f', '%.2f')], chisquareformat='%.2f', units=('GHz', 'GHz/ms'))
        l.Draw()

        c.Update()
        c.Print('../img/part2/%s-etalon_gauge.pdf' % file, 'pdf')

        fitres.append((fit.params[1]['value'], fit.params[1]['error']))
    return fitres


def getHFSFitStartParams(name):
    params = dict()
    params['09-64.1mA-34.0C'] = [[[(-0.4874, 1.85, 55e-3), (-0.0825, 2.09, 3e-3)], (1.697, 2.232)],
                                 [[(-1.4753, 2.708, 65e-3)], (2.533, 2.916)],
                                 [[(-1.86125, 3.713, 21.5e-3), (-0.79625, 3.927, 71.5e-3), (-0.567903, 4.238, 51.5e-3)], (3.5, 4.35)]]
    # params['26-62.8mA-34.0C'] = [[[(-0.25884, 0.001182, 12e-6), (-0.26071, 0.001353, 6e-6), (-1.5657, 0.001476, 23e-6)], (0.001092, 0.001582), 0.6],
    #                             [[(-1.4912, 0.001908, 13e-6)], (0.001787, 0.001997), 0.5],
    # [[(-0.21383, 0.002166, 9e-6), (-0.7897, 0.002254, 2e-6)], (0.0021, 0.002331), 0.4]] # TODO s -> ms
    return params.get(name)  # returns None if params-dict has no key 'name'


def makeHFSGraph(name, xmin, xmax):
    ch1 = OPData.fromPath('../data/part2/%s.tab' % name, 1)
    ch2 = OPData.fromPath('../data/part2/%s.tab' % name, 2)
    ch1.multiplyX(1000)
    ch2.multiplyX(1000)

    c = TCanvas('c-%s' % name, '', 1280, 720)

    g1 = ch1.makeGraph('g1-%s' % name, 't / ms', 'U / V')
    prepareGraph(g1)
    g1.SetMinimum(min(ch2.getY()) * 1.2)
    g1.SetMaximum(max(ch2.getY()) * 1.2)
    g1.GetXaxis().SetRangeUser(xmin, xmax)
    g1.Draw('APX')
    g2 = ch2.makeGraph('g2-%s' % name)
    prepareGraph(g2)
    g2.SetMarkerColor(2)
    g2.Draw('PX')

    fitStartParams = getHFSFitStartParams(name)
    fitres = []
    if fitStartParams:
        peakNum = 0
        offset = ch2.getY()[0]  # approx offset of underground
        slope = (ch2.getY()[-1] - ch2.getY()[0]) / (xmax - xmin)  # approx slope of underground
        for peakparams, xstartend in fitStartParams:
            xstart, xend = xstartend
            peakcount = len(peakparams)
            fitfunc = 'pol1(0)+gaus(2)'
            dpc = 2  # delta param count
            for i in range(1, peakcount):
                fitfunc += '+gaus(%d)' % (i * 3 + dpc)
            fit = Fitter('fitHFS%s' % name, fitfunc)
            fit.function.SetLineColor(peakNum + 3)
            fit.setParam(0, 'a', offset)
            fit.setParamLimits(0, 0, offset * 2)
            fit.setParam(1, 'b', slope)
            fit.setParamLimits(1, 0, 2 * slope)
            for i, params in enumerate(peakparams):
                fit.setParam(i * 3 + dpc, 'A%d' % i, params[0])
                fit.setParam(i * 3 + dpc + 1, 'c%d' % i, params[1])
                fit.setParam(i * 3 + dpc + 2, 's%d' % i, params[2])
                if params[0] < 0:
                    fit.setParamLimits(i * 3 + dpc, 3 * params[0], 0)
                else:
                    fit.setParamLimits(i * 3 + dpc, 0, 2 * params[0])
                fit.setParamLimits(i * 3 + dpc + 1, params[1] - 2 * params[2], params[1] + 2 * params[2])
                fit.setParamLimits(i * 3 + dpc + 2, 0, 20 * params[2])
            fit.fit(g2, xstart, xend, '+')
            fit.saveData('../fit/part2/HFS-%s-%d.txt' % (name, peakNum))
            for i in range(len(peakparams)):
                fitres.append((fit.params[i * 3 + dpc + 1]['value'], fit.params[i * 3 + dpc + 1]['error']))
            peakNum += 1

    c.Update()
    c.Print('../img/part2/HFS-%s.pdf' % name, 'pdf')
    return fitres


def evalHFSSpectrum():
    # filedata = [(64.1, 9, 1e-3, 4.6e-3), (62.8, 26, 0.8e-3, 3e-3), (61.9, 30, 0.35e-3, 0.8e-3), (64.8, 33, 0.2e-3, 0.5e-3)]  # TODO s->ms
    filedata = [(64.1, 9, 1, 4.6)]
    T = 34.0
    fitres = []
    for I, nr, xmin, xmax in filedata:
        fitres.append(makeHFSGraph('%02d-%.1fmA-%.1fC' % (nr, I, T), xmin, xmax))
    return fitres


def main():
    TGaxis.SetMaxDigits(2)
    etalongauge = evalEtalons()
    HFSPeaks = evalHFSSpectrum()

    for etalonfit, HFSfit in zip(*(etalongauge, HFSPeaks)):
        gps, sgps = etalonfit  # GHz per second, error
        toff, stoff = HFSfit[2]  # time offset, set 3rd peak as reference peak
        freqs = []
        for peak, error in HFSfit:
            t = peak - toff
            st = 0 if t == 0 else sqrt(stoff ** 2 + error ** 2)
            freq = gps * t
            sfreq = abs(freq) * sqrt((sgps / gps) ** 2 + (stoff / toff) ** 2)
            freqs.append((freq, sfreq))
        print(list(zip(*freqs))[0])

if __name__ == '__main__':
    setupROOT()
    main()
