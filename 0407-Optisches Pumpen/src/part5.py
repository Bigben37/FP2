import os
from numpy import sqrt
from functions import setupROOT, loadCSVToList
from txtfile import TxtFile
from op import OPData, prepareGraph
from fitter import Fitter
from data import DataErrors
from ROOT import TCanvas, TLegend

DIR = '../data/part5/04.10/'

def calibrateNDFilters():
    errorp = 0.01  # percentage error
    offset = 70
    data = loadCSVToList('../data/part5/04.10/filters.txt')
    ref = data[0][2] + offset  # error = sqrt(2) * errorp
    newdata = []
    filters = dict()
    for d in data:
        int = (d[2] + offset) / ref
        if int == 1:
            sint = 0
        else:
            sint = int * 2 * errorp
        newdata.append(d + [int, sint])
        filters[d[0]] = (int, sint)
        
    with TxtFile('../src/tab_part5_NDFilters.tex', 'w') as f:
        f.write2DArrayToLatexTable(newdata, 
                                   ["Stärke des Filters", r"$I_\text{nominell}$ / \%", r"$U_\text{ph}$ / mV", r"$I_\text{mess}$ / \%", r"$s_{I_\text{mess}}$ / \%"], 
                                   ['%.1f', '%.3f', '%d', '%.5f', '%.5f'], 
                                   r'Kalibrierung der Neutraldichtefilter: Nominelle Transmission $I_{\text{nominell}}$, gemessene Spannung an der Photodiode $U_{\text{ph}}$ und daraus berechnete Transmission $I_{\text{mess}}$. ', 
                                   'tab:deh:dnfilter')
    
    return filters

def fitTransmissionSignal(name):
    data = OPData.fromPath(DIR + name + '.tab', 2)
    c = TCanvas('c', '', 1280, 720)
    g = data.makeGraph('g_%s' % name, 't / s', 'U / V')
    prepareGraph(g, 2)
    g.GetXaxis().SetRangeUser(0.004, 0.019)
    g.Draw('APX')
    
    xmin, xmax = 0.0054, 0.015
    
    fit = Fitter('fit_%s' % name[-2:], '[0] - [1] * exp(-x/[2])')
    fit.setParam(0, 'a', 0.01)
    fit.setParam(1, 'b', 100)
    fit.setParam(2, '#tau', 0.001)
    fit.fit(g, xmin, xmax, 'M')
    fit.saveData('../fit/part5/%s.txt' % name)
    
    g.Draw('P')
    
    l = TLegend(0.35, 0.2, 0.65, 0.525)
    l.SetTextSize(0.03)
    l.AddEntry(g, 'Dehmelt Spektrum', 'p')
    l.AddEntry(fit.function, 'Fit mit a - b e^{-t/#tau}', 'l')
    fit.addParamsToLegend(l, [('%.6f', '%.6f'), ('%.2f', '%.2f'), ('%.6f', '%.6f')], chisquareformat='%.2f', units=['V', 'V', 's'])
    l.Draw()
    
    c.Update()
    c.Print('../img/part5/%s.pdf' % name.replace('.', '-'), 'pdf')
    
    return fit.params[2]['value'], fit.params[2]['error']
    

def evalTransmissionSignals():
    files = os.listdir(os.path.join(os.getcwd(), DIR))
    files.sort()
    taus = dict()
    for file in files:
        if file.startswith('65.5') and '-' in file:
            name = file[:-4]
            filter = int(name.split('-')[1]) / 10
            taus[filter] = fitTransmissionSignal(name)
    return taus

def evalTaus(taus, filters):
    data = DataErrors()
    table = []
    for key, (tau, stau) in taus.items():
        invtau = 1 / tau
        sinvtau = stau / (tau ** 2)
        int, sint = filters[key]
        data.addPoint(int, invtau, sint, sinvtau)
        table.append([int, sint, tau*1000, stau*1000])
    
    table.sort(key=lambda x:x[0], reverse=True)
    # make table
    with TxtFile('../src/tab_part5_taus.tex', 'w') as f:
        f.write2DArrayToLatexTable(table, ['$I$', '$s_I$', r'$\tau$ / ms', r'$s_\tau$ / ms'], 
                                   ['%.4f', '%.4f', '%.3f', '%.3f'], 'xxx', 'tab:deh:fitres')
    
    # make fit
    c = TCanvas('c_taus', '', 1280, 720)
    g = data.makeGraph('g_taus', r'Intensitaet in %', '#frac{1}{#tau} / #frac{1}{s} ')
    g.Draw('APX')
    
    fit = Fitter('fit_taus', '[0]*x + 1/[1]')
    fit.setParam(0, 'a', 1)
    fit.setParam(1, 'T', 1)
    fit.fit(g, 0, 1.1)
    fit.saveData('../fit/part5/taufit.txt')
    
    l = TLegend(0.55, 0.15, 0.85, 0.5)
    l.SetTextSize(0.03)
    l.AddEntry(g, '#frac{1}{#tau} gegen Intensitaet', 'p')
    l.AddEntry(fit.function, 'Fit mit #frac{1}{#tau} = a*I + #frac{1}{T}', 'l')
    fit.addParamsToLegend(l, [('%.0f', '%.0f'), ('%.5f', '%.5f')], chisquareformat='%.2f', units=['1/s', 's'])
    l.Draw()
    
    g.Draw('P')
    c.Print('../img/part5/taufit.pdf', 'pdf')

def main():
    filters = calibrateNDFilters()
    taus = evalTransmissionSignals()
    evalTaus(taus, filters)

if __name__ == '__main__':
    setupROOT()
    main()