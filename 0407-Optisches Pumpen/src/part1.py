#!/usr/bin/python

__author__ = "Benjamin Rottler (benjamin@dierottlers.de)"

from op import OPData, prepareGraph
from functions import setupROOT
from fitter import Fitter
from ROOT import TCanvas
import os


def makeGraphs(path, ch1, ch2):   
    g1 = ch1.makeGraph('ch1')
    prepareGraph(g1)
    g1.SetMaximum(max(ch2.getY())*1.1)
    g1.SetMinimum(min((min(ch2.getY()), min(ch1.getY())))*1.2)
    g1.GetXaxis().SetRangeUser(0, max(ch1.getX()))
    g2 = ch2.makeGraph('ch2')
    prepareGraph(g2)
    g2.SetMarkerColor(2)
    g1.Draw('AP')
    g2.Draw('P')
    return g1, g2

def getFitStartX(ch1, ch2):
    ch1rebin = ch1.rebin(5)
    ch2rebin = ch2.rebin(5)
    
    ch1minima = ch1rebin.findExtrema(5, 0, 0.005)
    xmin = ch1minima.getPoint(0)[0]
    ch1maxima = ch1rebin.findExtrema(5, xmin, 0.005, False)
    xmax = ch1maxima.getPoint(0)[0]
    
    phaseoffset = 0.0002  # add phase offset for xmin, xmax in channel 2
    xmin2 = xmin + phaseoffset + (xmax - xmin) / 3  # start after deformation of signal
    xmax2 = xmax + phaseoffset
    
    ch2max = ch2rebin.findExtrema(5, xmin2, xmax2, False)
    return ch2max.getX()

def fitPeak(g, peakx, sigma, color):
    fit = Fitter('fit'+str(peakx), 'pol1(0)+gaus(2)')
    fit.function.SetLineColor(color)
    fit.setParam(0, 'a', 0.1)
    fit.setParam(1, 'b', 250)
    fit.setParam(2, 'A', 0.6)
    fit.setParam(3, 'c', peakx)
    fit.setParam(4, 's', sigma)
    fit.fit(g, peakx - sigma, peakx + sigma, '+')
    fit.saveData('../fit/'+str(color)+'.txt')
    return fit.params[3]['value'], fit.params[3]['error']

def evalData(path):
    dir = '../data/part1/'
    ch1 = OPData.fromPath(dir + path, OPData.CH1)
    ch2 = OPData.fromPath(dir + path, OPData.CH2)
    
    c = TCanvas('c', '', 1280, 720)
    g1, g2 = makeGraphs(path, ch1, ch2)

    peakxs = getFitStartX(ch1, ch2)
    fitres = []
    for i, peakx in enumerate(peakxs):
        fitres.append(fitPeak(g2, peakx, 0.0001, i % 8 + 2))
        
    for fr in fitres:
        print(fr)
        
    c.Update()
    c.Print('../img/part1/' +path[:-4] + '.pdf', 'pdf')


def main():
    evalData('01-63.6mA-33.3C.tab')
    #for file in os.listdir(os.path.join(os.getcwd(), '../data/part1/')):
    #    if file.endswith('.tab'):
    #        evalData(file)

if __name__ == '__main__':
    setupROOT()
    main()
