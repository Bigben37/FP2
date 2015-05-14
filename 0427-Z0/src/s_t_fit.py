from numpy import sqrt
from cuts import CUTS
from z0 import Z0Data
from functions import setupROOT
from fitter import Fitter
from ROOT import gStyle, TCanvas, TLegend, TF1  # @UnresolvedImport
from txtfile import TxtFile


def stFit(data, energie, xmin, xmax, binsize):
    datacut = data.cut(CUTS[0][1])  # ee-cut

    c = TCanvas('c', '', 1280, 720)
    hist = datacut.makeHistogramm('hist_%f' % energie, 'cos_thet', binsize, -1, 1)
    hist.Draw()

    fit = Fitter('f', '[0] * (1 + x^2) + [1] * (1 - x)^(-2)')
    fit.setParam(0, 's', 100)
    fit.setParam(1, 't', 10)
    fit.fit(hist, xmin, xmax)
    fit.saveData('../fit/s_t_fit_%.2f.txt' % energie)

    sfunc = TF1('sfunc', '[0]*(1+x^2)', xmin, xmax)
    sfunc.SetParameter(0, fit.params[0]['value'])
    sfunc.SetLineWidth(1)
    sfunc.SetLineColor(3)
    sfunc.Draw('same')

    tfunc = TF1('tfunc', '[0]*(1-x)^(-2)', xmin, xmax)
    tfunc.SetParameter(0, fit.params[1]['value'])
    tfunc.SetLineWidth(1)
    tfunc.SetLineColor(4)
    tfunc.Draw('same')

    l = TLegend(0.15, 0.6, 0.45, 0.85)
    l.SetTextSize(0.03)
    l.AddEntry(hist, "daten_1 (mit ee-cut)", 'l')
    l.AddEntry(fit.function, 'Fit mit N = s (1 + x^{2}) + t (1 - x)^{-2}', 'l')
    fit.addParamsToLegend(l, [('%.2f', '%.2f'), ('%.2f', '%.2f')], chisquareformat='%.2f')
    l.AddEntry(sfunc, 's (1 + x^{2})', 'l')
    l.AddEntry(tfunc, 't (1 - x)^{-2}', 'l')
    l.Draw()

    c.Update()
    s = '%.2f' % energie
    c.Print('../img/s_t_fit_%s.pdf' % s.replace('.', '-'), 'pdf')

    return ((fit.params[0]["value"], fit.params[0]["error"]), (fit.params[1]["value"], fit.params[1]["error"]))


def main():
    data = Z0Data.fromROOTFile('../data/daten/daten_1.root', 'h33')
    energiedatas = data.splitEnergies()
    xmin, xmax = -0.9, 0.9
    binsizes = {88.48021:80, 89.47158:80, 90.22720:80, 91.23223:50, 91.97109:25, 92.97091:59, 93.71841:80}
    integrals = []
    eds = list(energiedatas.items())  # energy datas sorted after energy
    eds.sort(key=lambda x: x[0])
    for energie, data in eds:
        (s, ss), (t, st) = stFit(data, energie, xmin, xmax, binsizes[energie])
        # s intergral:
        Is = s * (xmax - xmin + (xmax ** 3 - xmin ** 3) / 3)
        sIs = Is * ss / s
        # t integral
        It = t * (1 / (1 - xmax) - 1 / (1 - xmin))
        sIt = It * st / t
        r = Is / (Is + It)  # s-ratio
        sr = r * sqrt((sIs / Is) ** 2 + (sIs ** 2 + sIt ** 2) / ((Is + It) ** 2))
        integrals.append((energie, Is, sIs, It, sIt, r, sr))
    with TxtFile('../calc/s-t-integrals.txt', 'w') as f:
        f.write2DArrayToFile(integrals, ['%.5f'] + ['%.3f'] * 6)

if __name__ == '__main__':
    setupROOT()
    gStyle.SetOptStat(0)
    main()
