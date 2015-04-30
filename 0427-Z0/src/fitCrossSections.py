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
        fit = Fitter('fit_%s' % ctype, '[0] + [1] * x + 12*pi / [2]^2 * x^2 * [3]^2 / ((x^2-[2]^2)^2 + x^4 * [4]^2 / [2]^2) * 0.3894e6')
        fitfuncstring = "a + b#sqrt{s} + #frac{12#pi}{M_{Z}^{2}} #frac{s #Gamma_{%s}^{2}}{(s-M_{Z}^{2})^{2} + s^{2} #Gamma_{Z}^{2} / M_{Z}^{2}}" % ctype[0]
    else:
        fit = Fitter('fit_%s' % ctype, '[0] + [1] * x + 12*pi / [2]^2 * x^2 * [3] * [5] / ((x^2-[2]^2)^2 + x^4 * [4]^2 / [2]^2) * 0.3894e6')
        fitfuncstring = "a + b#sqrt{s} + #frac{12#pi}{M_{Z}^{2}} #frac{s #Gamma_{e} #Gamma_{%s}}{(s-M_{Z}^{2})^{2} + s^{2} #Gamma_{Z}^{2} / M_{Z}^{2}}" % ctype[0]
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
    fit.saveData('../fit/crosssections_%s.txt' % ctype)
    
    l = TLegend(0.625, 0.575, 0.98, 0.98)
    l.SetTextSize(0.03)
    l.AddEntry(g, "%s Wirkungsquerschnitte" % ctype, 'p')
    l.AddEntry(fit.function, "Fit mit #sigma(s) = ", 'l')
    l.AddEntry(None, "", '')
    l.AddEntry(None, fitfuncstring, '')
    l.AddEntry(None, "", '')
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
    g = data.makeGraph('g_%s' % ctype, '#sqrt{s} / GeV', '#sigma / nb')
    g.Draw('AP')
    
    if not startGammaEE:
        fit = Fitter('fit_%s' % ctype, '(12*pi / [0]^2) * (x^2 * [1]^2) / ((x^2-[0]^2)^2 + x^4 * [2]^2 / [0]^2) * 0.3894*10^6')  #  GeV^-2 = 0.3894 mb 
        fitfuncstring = "#frac{12#pi}{M_{Z}^{2}} #frac{s #Gamma_{%s}^{2}}{(s-M_{Z}^{2})^{2} + s^{2} #Gamma_{Z}^{2} / M_{Z}^{2}}" % ctype[0]
    else:
        fit = Fitter('fit_%s' % ctype, '(12*pi / [0]^2) * (x^2 * [1] * [2]) / ((x^2-[0]^2)^2 + x^4 * [3]^2 / [0]^2) * 0.3894*10^6')
        fitfuncstring = "#frac{12#pi}{M_{Z}^{2}} #frac{s #Gamma_{e} #Gamma_{%s}}{(s-M_{Z}^{2})^{2} + s^{2} #Gamma_{Z}^{2} / M_{Z}^{2}}" % ctype[0]
    fit.setParam(0, 'M_{Z}', 91.2)
    fit.setParamLimits(0, 0, 1000)
    if not startGammaEE:
        fit.setParam(1, '#Gamma_{%s}' % ctype[0], 0.08)
        fit.setParamLimits(1, 0, 1000)
        fit.setParam(2, '#Gamma_{Z}', 2.5)
        fit.setParamLimits(2, 0, 1000)
    else:
        fit.setParam(1, '#Gamma_{e}', startGammaEE, True)
        fit.setParam(2, '#Gamma_{%s}' % ctype[0], 1.5)
        fit.setParam(3, '#Gamma_{Z}', 2.5)
        fit.setParamLimits(2, 0, 1000)
    fit.fit(g, 88, 94, '')
    fit.saveData('../fit/crosssections_%s.txt' % ctype)
    
    l = TLegend(0.625, 0.6, 0.98, 0.975)
    l.SetTextSize(0.03)
    l.AddEntry(g, "%s Wirkungsquerschnitte" % ctype, 'p')
    l.AddEntry(fit.function, "Fit mit #sigma(s) = %s" % fitfuncstring, 'l')
    l.AddEntry(None, "", '')
    if not startGammaEE:
        fit.addParamsToLegend(l, [('%.3f', '%.3f'), ('%.4f', '%.4f'), ('%.3f', '%.3f')], chisquareformat='%f', units=['GeV / c^{2}', 'GeV', 'GeV'])
    else:
        fit.addParamsToLegend(l, [('%.3f', '%.3f'), '%.3f', ('%.3f', '%.3f'), ('%.3f', '%.3f')], chisquareformat='%f', units=['GeV/c^{2}', 'GeV', 'GeV', 'GeV'])
    l.Draw()

    c.Update()
    c.Print('../img/crosssections_%s.pdf' % ctype, 'pdf')
    
    return fit.params[1]['value']
    
def main():
    startGammaEE = 0.084
    makeCSGraph('ee')
    makeCSGraph('mm')
    makeCSGraph('tt')
    #makeCSGraphUnderground('tt')
    makeCSGraph('qq', startGammaEE)

if __name__ == '__main__':
    setupROOT()
    gStyle.SetOptStat(0)
    main()