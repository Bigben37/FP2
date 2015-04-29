from functions import setupROOT, loadCSVToList
from data import DataErrors
from ROOT import gStyle, TCanvas, TLegend  # @UnresolvedImport
from fitter import Fitter

def loadCrossSection(ctype):
    datalist = loadCSVToList('../calc/crosssections_%s.txt' % ctype)
    xlist = list(zip(*datalist))[0]
    sxlist = [0] * len(xlist)
    ylist = list(zip(*datalist))[1]
    sylist = list(zip(*datalist))[2]
    return DataErrors.fromLists(xlist, ylist, sxlist, sylist)
    
def makeCSGraphUnderground(ctype, startGammaEE=None):
    data = loadCrossSection(ctype)
    c = TCanvas('c_%s' % ctype, '', 1280, 720)
    g = data.makeGraph('g_%s' % ctype, '#sqrt{s} / GeV', '#sigma / nb')
    g.Draw('AP')
    
    if not startGammaEE:
        fit = Fitter('fit_%s' % ctype, '[0] + [1] * x + 12*pi / [2]^2 * x * [3]^2 / ((x-[2])^2 + x^2 * [4]^2 / [2]^2)')
    else:
        fit = Fitter('fit_%s' % ctype, '[0] + [1] * x + 12*pi / [2]^2 * x * [3] * [5] / ((x-[2])^2 + x^2 * [4]^2 / [2]^2)')
    fit.setParam(0, 'a', 0)
    fit.setParam(1, 'b', 0)
    fit.setParam(2, 'M_{Z}', 91.2)
    fit.setParam(4, '#Gamma_{Z}', 2.5)
    if not startGammaEE:
        fit.setParam(3, '#Gamma_{%s}' % ctype[0], 0.08)
    else:
        fit.setParam(3, '#Gamma_{e}', startGammaEE, True)
        fit.setParam(5, '#Gamma_{%s}' % ctype[0], 2)
    fit.fit(g, 88, 94)
    fit.saveData('../fit/crosssections_%s' % ctype)
    
    l = TLegend(0.625, 0.6, 0.95, 0.975)
    l.SetTextSize(0.03)
    l.AddEntry(g, "%s Wirkungsquerschnitte" % ctype, 'p')
    l.AddEntry(fit.function, "fit", 'l')
    if not startGammaEE:
        fit.addParamsToLegend(l, [('%.3f', '%.3f'), ('%.3f', '%.3f'), ('%.3f', '%.3f'), ('%.3f', '%.3f'), ('%.3f', '%.3f')], chisquareformat='%f', units=['nb', 'nb/GeV', 'GeV / c^{2}', 'GeV', 'GeV'])
    else:
        fit.addParamsToLegend(l, [('%.3f', '%.3f'), ('%.3f', '%.3f'), ('%.3f', '%.3f'), '%.3f', ('%.3f', '%.3f'), ('%.3f', '%.3f')], chisquareformat='%f', units=['nb', 'nb/GeV', 'GeV/c^{2}', 'GeV', 'GeV', 'GeV'])
    l.Draw()

    c.Update()
    c.Print('../img/crosssections_%s.pdf' % ctype, 'pdf')
    
    return fit.params[3]['value']

def makeCSGraph(ctype, startGammaEE=None):
    data = loadCrossSection(ctype)
    c = TCanvas('c_%s' % ctype, '', 1280, 720)
    g = data.makeGraph('g_%s' % ctype, 's / GeV', '#sigma / nb')
    g.Draw('AP')
    
    if not startGammaEE:
        fit = Fitter('fit_%s' % ctype, '(12*pi / [0]^2) * (x * [1]^2) / ((x-[0])^2 + x^2 * [2]^2 / [0]^2) * 0.3894e-6')  #  GeV^-2 = 0.3894 mb 
    else:
        fit = Fitter('fit_%s' % ctype, '(12*pi / [0]^2) * (x * [1] * [3]) / ((x-[0])^2 + x^2 * [2]^2 / [0]^2) * 0.3894e-6')
    fit.setParam(0, 'M_{Z}', 91.2)
    fit.setParam(2, '#Gamma_{Z}', 2.5)
    if not startGammaEE:
        fit.setParam(1, '#Gamma_{%s}' % ctype[0], 0.08)
    else:
        fit.setParam(1, '#Gamma_{e}', startGammaEE, True)
        fit.setParam(3, '#Gamma_{%s}' % ctype[0], 2)
    fit.fit(g, 88, 94, 'M')
    fit.saveData('../fit/crosssections_%s.txt' % ctype)
    
    l = TLegend(0.625, 0.6, 0.95, 0.975)
    l.SetTextSize(0.03)
    l.AddEntry(g, "%s Wirkungsquerschnitte" % ctype, 'p')
    l.AddEntry(fit.function, "fit", 'l')
    if not startGammaEE:
        fit.addParamsToLegend(l, [('%.3f', '%.3f'), ('%.3f', '%.3f'), ('%.3f', '%.3f')], chisquareformat='%f', units=['GeV / c^{2}', 'GeV', 'GeV'])
    else:
        fit.addParamsToLegend(l, [('%.3f', '%.3f'), '%.3f', ('%.3f', '%.3f'), ('%.3f', '%.3f')], chisquareformat='%f', units=['GeV/c^{2}', 'GeV', 'GeV', 'GeV'])
    l.Draw()

    c.Update()
    c.Print('../img/crosssections_%s.pdf' % ctype, 'pdf')
    
    return fit.params[1]['value']
    
def main():
    ctypes = ['ee', 'mm', 'tt', 'qq']
    startGammaEE = 0.084
    for ctype in ctypes:
        if not ctype == 'qq':
            gamma = makeCSGraph(ctype)
        else:
            gamma = makeCSGraph(ctype, startGammaEE)
        #if ctype == 'ee':
        #    startGammaEE = gamma

if __name__ == '__main__':
    setupROOT()
    gStyle.SetOptStat(0)
    main()