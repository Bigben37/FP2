from numpy import exp, sqrt
# ========================================================================
# make sure to add ../../lib to your project path or copy files from there
from functions import setupROOT, loadCSVToList
from op import OPData, prepareGraph, getRootColor
from fitter import Fitter
from data import DataErrors
# ========================================================================
from ROOT import TCanvas, TLegend, TF1

DIR = '../data/part6/'


def franzenFunc(xx, params):
    x = xx[0]
    A, u, m, s, B, l = params
    m *= 1e-3
    s *= 1e-6
    l *= 1e3
    piece = 0
    if x >= m:
        piece = B * (1 - exp(-l * (x - m)))
    return A / (1 + exp((m - x) / s)) + u + piece


def fermiFunc(xx, params):
    x = xx[0]
    A, u, m, s, B = params
    m *= 1e-3
    s *= 1e-6
    piece = 0
    if x >= m:
        piece = B
    return A / (1 + exp((m - x) / s)) + u + piece


def makeFranzenFit(n, plotParams):
    data = OPData.fromPath(DIR + '%02d.tab' % n, 1)
    xmin, xmax = plotParams[:2]
    fitparams = plotParams[2:]

    c = TCanvas('c_%d' % n, '', 1280, 720)
    g = data.makeGraph('g_%d' % n, 'Zeit t / s', 'U_{ph} / V')
    prepareGraph(g, 2)
    g.GetXaxis().SetRangeUser(xmin, xmax)
    g.Draw('APX')

    fit = Fitter('fit%d' % n, franzenFunc, (xmin, xmax, 6))
    fit.function.SetNpx(1000)
    paramnames = ["A", "u", "#mu", "#sigma", "B", "#lambda"]
    for i in range(6):
        fit.setParam(i, paramnames[i], fitparams[3 * i])
        fit.setParamLimits(i, fitparams[3 * i + 1], fitparams[3 * i + 2])
        print(fitparams[3 * i], fitparams[3 * i + 1], fitparams[3 * i + 2])
    fit.fit(g, xmin, xmax)
    fit.saveData('../fit/part6/%02d.txt' % n)

    fermi = TF1('func', fermiFunc, xmin, xmax, 5)
    fermi.SetNpx(1000)
    fermi.SetLineColor(getRootColor(0))
    fermi.SetLineWidth(1)
    for i in range(5):
        fermi.SetParameter(i, fit.params[i]['value'])
    fermi.Draw('SAME')

    g.Draw('P')

    l = TLegend(0.4, 0.15, 0.85, 0.65)
    l.SetTextSize(0.03)
    l.AddEntry(g, "Spannung Photodiode U_{ph}", 'l')
    l.AddEntry(fit.function, 'Fit mit U_{ph}(t) = U_{F}(t; A, u, #mu, #sigma) + U_{E}(t; #mu, B, #lambda)', 'l')
    l.AddEntry(fermi, 'Fermi-Verteilung', 'l')
    fit.addParamsToLegend(l, [('%.4f', '%.4f'), ('%.4f', '%.4f'), ('%.5f', '%.5f'), ('%.2f', '%.2f'), ('%.4f', '%.4f'), ('%.3f', '%.3f')],
                          chisquareformat='%.2f', units=["V", "V", "ms", "#mus", "V", "1/ms"])
    l.Draw()

    c.Update()
    c.Print('../img/part6/%02d.pdf' % n, 'pdf')

    result = []
    exportvals = [2, 3, 4]  # mu, sigma, B
    for e in exportvals:
        result.append((fit.params[e]['value'], fit.params[e]['error']))
    return result


def makeSigmaFit(darkTimes, sigmas):
    dt, sdt = list(zip(*darkTimes))
    s, ss = list(zip(*sigmas))
    data = DataErrors.fromLists(dt, s, sdt, ss)

    c = TCanvas('c_sigma', '', 1280, 720)
    g = data.makeGraph('g_sigma', 'Dunkelzeit t_{D} / ms', 'Verschmierung #sigma / #mus')
    g.Draw('APX')

    fit = Fitter('fit_sigma', 'pol1(0)')
    fit.setParam(0, 'a', 0)
    fit.setParam(1, 'b', 1)
    fit.fit(g, 0, 25)
    fit.saveData('../fit/sigma.txt')

    l = TLegend(0.6, 0.15, 0.85, 0.5)
    l.SetTextSize(0.03)
    l.AddEntry(g, 'Verschmierung #sigma', 'p')
    l.AddEntry(None, 'der Fermi-Verteilung', '')
    l.AddEntry(fit.function, 'Fit mit #sigma(t_{D}) = a + b t_{D}', 'l')
    fit.addParamsToLegend(l, (('%.2f', '%.2f'), ('%.2f', '%.2f')), chisquareformat='%.2f', units=['#mus', '10^{-3}'])
    l.Draw()

    g.Draw('P')
    c.Print('../img/part6/sigmaFit.pdf', 'pdf')


def makeBFit(darkTimes, Bs):
    dt, sdt = list(zip(*darkTimes))
    b, sb = list(zip(*Bs))
    data = DataErrors.fromLists(dt, b, sdt, sb)

    c = TCanvas('c_B', '', 1280, 720)
    g = data.makeGraph('g_B', 'Dunkelzeit t_{D} / ms', 'Fitparameter B / V')
    g.Draw('APX')

    fit = Fitter('fit_B', '[0] + [1] * (1 - exp(-x/[2]))')
    fit.function.SetNpx(1000)
    fit.setParam(0, 'a', 0.1)
    fit.setParam(1, 'b', 0.1)
    fit.setParam(2, 'T_{R_{F}}', 6)
    fit.fit(g, 0, 25)
    fit.saveData('../fit/B.txt')

    l = TLegend(0.55, 0.15, 0.85, 0.6)
    l.SetTextSize(0.03)
    l.AddEntry(g, 'Fitparameter B', 'p')
    l.AddEntry(fit.function, 'Fit mit B(t_{D}) = a + b (1 - e^{-x/T_{R_{F}}})', 'l')
    fit.addParamsToLegend(l, (('%.3f', '%.3f'), ('%.3f', '%.3f'), ('%.1f', '%.1f')), chisquareformat='%.2f', units=['V', 'V', 'ms'])
    l.Draw()

    g.Draw('P')
    c.Print('../img/part6/BFit.pdf', 'pdf')


def makeFranzenFits():
    MAXFILE = 12
    plotParams = loadCSVToList(DIR + 'FitdataRoot.txt')
    results = []
    for i in range(1, MAXFILE + 1):
        results.append(makeFranzenFit(i, plotParams[i - 1]))
    mus, sigmas, Bs = list(zip(*results))

    # calculate delta T
    endtimes = loadCSVToList(DIR + 'endtimes.txt')[0]
    darkTimes = []
    for (mu, smu), e in zip(*[mus, endtimes]):
        dt = e - mu
        se = e * 0.01 + 0.1
        sdt = sqrt(smu ** 2 + se ** 2)
        darkTimes.append((dt, sdt))

    makeSigmaFit(darkTimes, sigmas)
    makeBFit(darkTimes, Bs)


def main():
    makeFranzenFits()

if __name__ == '__main__':
    setupROOT()
    main()
