#!/usr/bin/python
import datetime
from numpy import pi
from functions import setupROOT
from myon import MyonData, prepareGraph
from ROOT import TCanvas, TMath, TF1
from fitter import Fitter

def langaufun(x, par):
    """Convoluted Landau and Gaussian Fitting Function
    source: https://root.cern.ch/root/html/tutorials/fit/langaus.C.html
    translated to python by Benjamin Rottler (benjamin@dierottlers.de)
    
    parameters:
    par[0] = Width (scale) parameter of Landau density
    par[1] = Most Probable (MP, location) parameter of Landau density
    par[2] = Total area (integral -inf to inf, normalization constant)
    par[3] = Width (sigma) of convoluted Gaussian function
    
    In the Landau distribution (represented by the CERNLIB approximation), 
    the maximum is located at x=-0.22278298 with the location parameter=0.
    This shift is corrected within this function, so that the actual
    maximum is identical to the MP parameter.
    """
    # numeric constants
    invsq2pi = (2*pi)**(-1/2)
    mpshift = -0.22278298  # Landau maximum location
    
    #control constants
    np = 500  # number of convolution steps
    sc = 5    # convolution extends to +-sc Guassion sigmas
      
    # mp shift correction
    mpc = par[1] - mpshift * par[0]
    
    #range of convolution integral
    xlow, xupp = x[0] - sc * par[3], x[0] + sc * par[3]
    
    #Convolution integral of Landau and Gaussion by sum
    i = 1
    step = (xupp-xlow) / np
    s = 0
    while i <= np/2:
        xx = xlow + (i - 0.5) * step
        fland = TMath.Landau(xx, mpc, par[0]) / par[0]
        s += fland * TMath.Gaus(x[0], xx, par[3])
        
        xx = xupp - (i - 0.5) * step
        fland = TMath.Landau(xx, mpc, par[0]) / par[0]
        s += fland * TMath.Gaus(x[0], xx, par[3])
        i += 1
        
    return (par[2] * step * s * invsq2pi / par[3])
        

def evalFlythroughSpectrum(name, xmin, xmax):
    data = MyonData.fromPath('../data/%s.TKA' % name)
    # TODO make countrate
    
    c = TCanvas('c', '', 1280, 720)
    g = data.makeGraph('g', 'channel c', 'counts N')
    prepareGraph(g)
    g.Draw('APX')  # don't draw error bars => fit function in front

    maxY = data.getByY(data.getMaxY())[0]
    area = g.Integral(xmin, xmax)   
    print('maxY', maxY)
    print('area', area)
    
    c.Update() 
     
    """
    print('print function')  
    f = TF1('langaus', langaufun, xmin, xmax, 4)
    f.SetParameters(0.1, maxY, area, 30)
    f.Draw()
    """
       
    print('start fitting...')
    t1 = datetime.datetime.now()
    fit = Fitter('fit', langaufun, (xmin, xmax, 4))
    fit.setParam(0, 'scale', 1)
    fit.setParam(1, 'mpv', maxY)
    fit.setParam(2, 'A', area)
    fit.setParam(3, 'sigma', 30)
    fit.fit(g, xmin, xmax, 'RBO')
    t2 = datetime.datetime.now()
    delta = t2 - t1
    print('fitted in %d s' % int(delta.total_seconds()))
    fit.saveData('../fit/%s.txt' % name)
    
    g.Draw('P')  # redraw points with error bars
    c.Update()
    c.Print('../img/%s.pdf' % name, 'pdf')
    
    return fit.params

def evalPedestal():
    pass  # TBI


def main():
    fit100 = evalFlythroughSpectrum('energieeichung_100', 275, 600)
    #fit050 = evalFlythroughSpectrum('energieeichung_100', 0, 700)
    fit000 = evalPedestal()


if __name__ == "__main__":
    setupROOT()
    main()