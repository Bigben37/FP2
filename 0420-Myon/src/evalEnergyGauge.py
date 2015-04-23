#!/usr/bin/python
from functions import setupROOT
from myon import MyonData, prepareGraph
from ROOT import TCanvas
from fitter import Fitter

def makeGraph(name):
    data = MyonData.fromPath('../data/%s.TKA' % name)
    
    c = TCanvas('c', '', 1280, 720)
    g = data.makeGraph('g', 'channel c', 'counts N')
    prepareGraph(g)
    g.Draw('APX')  # don't draw error bars => fit function in front
    
    #"""
    fit = Fitter('fit', '[0]*TMath::Landau(x,  [1], [2])')
    fit.setParam(0, 'A', 400)
    fit.setParam(1, 'mpv', data.getByY(data.getMaxY())[0])
    fit.setParam(2, 'sigma', 1)
    fit.fit(g, 275, 400, 'M')
    fit.saveData('../fit/%s.txt' % name)
    #"""
    
    g.Draw('P')  # redraw points with error bars
    c.Update()
    c.Print('../img/%s.pdf' % name, 'pdf')


def main():
    makeGraph('durchflug_test')
    #makeGraph('beta_test')
    #makeGraph('lebensdauer_test')


if __name__ == "__main__":
    setupROOT()
    main()