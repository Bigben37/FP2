from op import OPData, prepareGraph
from fitter import Fitter
from numpy import mean
from ROOT import TCanvas
from docutils.parsers.rst.directives import path


def makeGraphs(path, ch1, ch2):
    g1 = ch1.makeGraph('ch1')
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
    return g1, g2


def getXIntervall(ch1, offset=False):
    ch1rebin = ch1.rebin(5)

    xmin, xmax = 0, ch1rebin.getPoint(-1)[0]
    ch1minima = ch1rebin.findExtrema(5, xmin, xmax).getX()
    ch1maxima = ch1rebin.findExtrema(5, xmin, xmax, False).getX()
    isAscending = ch1minima[0] < ch1maxima[0]  # check for ascending / descending flank
    phaseoffset = OPData.OFFSET if offset else 0  # add phase offset for xmin, xmax in channel 2
    xmin2, xmax2 = 0, 0
    if isAscending:
        xmin = ch1minima[0]
        xmax = list(filter(lambda x: x > xmin, ch1maxima))[0]
        xmin2 = xmin + phaseoffset + (xmax - xmin) * 0.4  # start after deformation of signal
        xmax2 = xmax + phaseoffset
    if not isAscending:
        xmin = ch1maxima[0]
        xmax = list(filter(lambda x: x > xmin, ch1minima))[0]
        xmin2 = xmin + phaseoffset
        xmax2 = xmax + phaseoffset - (xmax - xmin) * 0.5  # end before deformation of signal

    return xmin2, xmax2


def avgCloseValues(list, epsilon):
    i = 0
    avgList = []
    l = len(list)
    while i < l:
        currxs = [list[i]]
        j = i + 1
        while j < l and abs(list[j] - list[i]) <= epsilon:
            currxs.append(list[j])
            i += 1
            j += 1
        avgList.append(mean(currxs))
        i = j
    return avgList


def getFitStartX(xmin, xmax, ch2):
    ch2max = ch2.findExtrema(15, xmin, xmax, False).getX()
    return avgCloseValues(ch2max, 10 * ch2.getMinDeltaX())  # combine peaks which are closer than epsilon together


def fitPeak(g, peakx, sigma, color, part, file):
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


def evalEtalonData(part, path, xminmax=None):
    dir = '../data/part%d/' % part
    ch1 = OPData.fromPath(dir + path, OPData.CH1)
    ch2 = OPData.fromPath(dir + path, OPData.CH2)

    c = TCanvas('c', '', 1280, 720)
    g1, g2 = makeGraphs(path, ch1, ch2)

    if not xminmax:
        xmin, xmax = getXIntervall(ch1, True)
        xmin2, xmax2 = getXIntervall(ch1)
    else:
        xmin2, xmax2 = xminmax
        xmin = xmin2 + OPData.OFFSET
        xmax = xmax2 + OPData.OFFSET
    peakxs = getFitStartX(xmin, xmax, ch2)
    sigmamult = 25
    # handle special cases
    if part == 1:
        if path == '02-70.0mA-33.3C.tab' or path == '03-70.0mA-30.0C.tab' or path == '09-63.6mA-33.3C.tab':
            peakxs = peakxs[:-1]
        if path == '13-64.1mA-34.0C.tab':
            sigmamult = 50
        if path == '14-62.8mA-34.0C-modensprung.tab':
            peakxs = peakxs[1:]
    if part == 2:
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
        peakfits.append(fitPeak(g2, peakx, sigma, i % 8 + 4, part, path[:-4]))

    
    laserVoltageFit = fitLaserVoltage(g1, xmin2, xmax2, part, path[:-4])

    c.Update()
    c.Print('../img/part%d/%s.pdf' % (part, path[:-4]), 'pdf')
    
    return (laserVoltageFit, peakfits)
