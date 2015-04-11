#!/usr/bin/python

__author__ = "Benjamin Rottler (benjamin@dierottlers.de)"

from op import OPData, prepareGraph
from functions import setupROOT
from ROOT import TCanvas
import os

def plotData(path):
    dir = '../data/part1/'
    ch1 = OPData.fromPath(dir + path, OPData.CH1)
    ch2 = OPData.fromPath(dir + path, OPData.CH2)

    c = TCanvas('c', '', 1280, 720)
    
    g1 = ch1.makeGraph('ch1')
    prepareGraph(g1)
    g2 = ch2.makeGraph('ch2')
    prepareGraph(g2)
    g2.SetMarkerColor(2)
    
    g2.Draw('AP')
    g1.Draw('P')
    
    
    c.Update()
    c.Print('../img/part1/' +path[:-4] + '.pdf', 'pdf')



def main():
    for file in os.listdir(os.path.join(os.getcwd(), '../data/part1/')):
        if file.endswith('.tab'):
            plotData(file)

if __name__ == '__main__':
    setupROOT()
    main()
