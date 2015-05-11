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
    ref = data[0][2] + offset
    sref = sqrt((data[0][2] * errorp) ** 2 + (offset * errorp) ** 2)
    newdata = []
    filters = dict()
    for d in data:
        int = (d[2] + offset) / ref
        if int == 1:
            sint = 0
        else:
            sint = int * sqrt((sqrt((d[2] * errorp) ** 2 + (offset * errorp) ** 2) / (d[2] + offset))**2 + (sref/ref)**2)
        newdata.append(d + [int*100, sint*100])
        filters[d[0]] = (int, sint)
        
    with TxtFile('../src/tab_part5_NDFilters.tex', 'w') as f:
        f.write2DArrayToLatexTable(newdata, 
                                   ["Stärke des Filters", r"$I_\text{nominell}$ / \%", r"$U_\text{ph}$ / mV", r"$I_\text{mess}$ / \%", r"$s_{I_\text{mess}}$ / \%"], 
                                   ['%.1f', '%.3f', '%d', '%.2f', '%.2f'], 
                                   r'Kalibrierung der Neutraldichtefilter: Nominelle Transmission $I_{\text{nominell}}$, gemessene Spannung an der Photodiode $U_{\text{ph}}$ und daraus berechnete Transmission $I_{\text{mess}}$. ', 
                                   'tab:deh:dnfilter')
    
    return filters

def fitTransmissionSignal(name):
    data = OPData.fromPath(DIR + name + '.tab', 2)
    c = TCanvas('c', '', 1280, 720)
    g = data.makeGraph('g_%s' % name, 'Zeit t / s', 'Spannung der Photodiode U_{ph} / V')
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
    l.AddEntry(g, 'Spannung der Photodiode', 'p')
    l.AddEntry(fit.function, 'Fit mit U_{ph}(t) = a - b e^{-t/#tau}', 'l')
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
        table.append([int*100, sint*100, tau*1000, stau*1000])
    
    table.sort(key=lambda x:x[0], reverse=True)
    # make table
    with TxtFile('../src/tab_part5_taus.tex', 'w') as f:
        f.write2DArrayToLatexTable(table, [r'$I_\text{mess}$ / \%', r'$s_{I_\text{mess}}$ / \%', r'$\tau$ / ms', r'$s_\tau$ / ms'], 
                                   ['%.2f', '%.2f', '%.3f', '%.3f'], 
                                   r'Orientierungszeiten $\tau$ des Rubidiumensembles bei verschiedenen Pumpintensitäten $I_{\text{mess}}$.', 
                                   'tab:deh:fitres')
    
    # make fit
    c = TCanvas('c_taus', '', 1280, 720)
    g = data.makeGraph('g_taus', r'relative Intensitaet I_{mess}', 'inverse Orientierungszeit #tau^{ -1} / s^{-1}')
    g.Draw('APX')
    
    fit = Fitter('fit_taus', '[0]*x + 1/[1]')
    fit.setParam(0, '#alpha', 1)
    fit.setParam(1, 'T_{R}', 1)
    fit.fit(g, 0, 1.1)
    fit.saveData('../fit/part5/taufit.txt')
    
    l = TLegend(0.55, 0.15, 0.85, 0.5)
    l.SetTextSize(0.03)
    l.AddEntry(g, 'Inverse Orientierungszeit #tau^{ -1}', 'p')
    l.AddEntry(fit.function, 'Fit mit #tau^{ -1} (I) = #alpha I + #frac{1}{T_{R}}', 'l')
    fit.addParamsToLegend(l, [('%.0f', '%.0f'), ('%.5f', '%.5f')], chisquareformat='%.2f', units=['s^{-1}', 's'])
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