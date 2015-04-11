#!/usr/bin/python
__author__ = "Benjamin Rottler (benjamin@dierottlers.de)"

import os
from numpy import sqrt
from functions import loadCSVToList, avgerrors, setupROOT
from txtfile import TxtFile
from physconsts import h_Js, mub_JT
from op import OPData, inductorIToB, prepareGraph
from ROOT import TCanvas, TPad, TGraphErrors, TGaxis, gStyle, gROOT

def makeGraphs():
    gStyle.SetPadTickY(0)
    files = os.listdir(os.path.join(os.getcwd(), '../data/part3/'))
    files.sort()
    for file in files:
        if file.endswith('.tab'):
            ch1 = OPData.fromPath('../data/part3/' + file, 1)
            ch2 = OPData.fromPath('../data/part3/' + file, 2)

            c = TCanvas('c' + file, '', 1280, 720)
            pad = TPad('pad' + file, '', 0, 0, 1, 1)
            pad.Draw()
            pad.cd()

            frame = pad.DrawFrame(0, -0.25, 0.051, 0.25)
            frame.SetXTitle('t / s')
            frame.GetXaxis().CenterTitle()
            frame.SetYTitle('U_B / V')
            frame.GetYaxis().CenterTitle()

            g1 = ch1.makeGraph('g1' + file)
            prepareGraph(g1)
            g1.Draw('P')

            c.cd()
            overlay = TPad('overlay' + file, '', 0, 0, 1, 1)
            overlay.SetFillStyle(4000)  # transparent
            overlay.SetFillColor(0)  # white
            overlay.SetFrameFillStyle(4000)  # transparent
            overlay.Draw()
            overlay.cd()

            g2 = ch2.makeGraph('g2' + file)
            prepareGraph(g2)
            g2.SetMarkerColor(2)

            g2ymin = min(ch2.getY())
            xmin = pad.GetUxmin()
            xmax = pad.GetUxmax()
            ymin = 1.1 * g2ymin
            ymax = abs(ymin)
            oframe = overlay.DrawFrame(xmin, ymin, xmax, ymax)
            oframe.GetXaxis().SetLabelOffset(99)
            oframe.GetYaxis().SetLabelOffset(99)
            oframe.GetYaxis().SetTickLength(0)

            g2.Draw('P')

            axis = TGaxis(xmax, ymin, xmax, ymax, ymin, ymax, 510, "+L")
            axis.SetLineColor(1)
            axis.SetLabelColor(2)
            axis.SetTitle('Spannung Photodiode U_{P} / V')
            axis.SetTitleColor(2)
            axis.CenterTitle()
            axis.SetTitleOffset(1.2)
            axis.Draw()

            c.Update()
            c.Print('../img/part3/' + file[:-4] + '.pdf', 'pdf')
    
    gStyle.SetPadTickY(1)

def evalData():
    results = []
    data = loadCSVToList('../data/part3/part3.txt')
    for iL, siL, f, sf, i1, si1, i1_, si1_, i4, si4 in data:  # I-Laser, frequency, I1, I1', I4 with respective errors
        # from mA to A
        i1 *= 1e-3
        si1 *= 1e-3
        i1_ *= 1e-3
        si1_ *= 1e-3
        i4 *= 1e-3
        si4 *= 1e-3
        # from kHz to Hz
        f *= 1e3
        sf *= 1e3
        # calc B1, B1'
        B1, sB1 = inductorIToB(1, i1, si1)
        B1_, sB1_ = inductorIToB(1, i1_, si1_)
        # calc B for nuclear spin
        B, sB = (B1 + B1_) / 2, sqrt(sB1 ** 2 + sB1_ ** 2) / 2
        # calc horizontal B-Field
        Bhor, sBhor = abs(B1 - B1_), sqrt(sB1 ** 2 + sB1_ ** 2)
        # calc vertical B-Field
        Bvert, sBvert = inductorIToB(4, i4, si4)
        # calc nuclear spin
        I = mub_JT * B / (h_Js * f) - 0.5
        sI = mub_JT * B / (h_Js * f) * sqrt((sB / B) ** 2 + (sf / f) ** 2)
        results.append([["I_L/mA", (iL, siL)],
                        ["f/kHz", (f * 1e-3, sf * 1e-3)],
                        ["Bhor/µT", (Bhor * 1e6, sBhor * 1e6)],
                        ["Bver/µT", (Bvert * 1e6, sBvert * 1e6)],
                        ["I\t", (I, sI)]])
    # print out results
    with TxtFile.fromRelPath('../calc/part3.txt', 'w') as f:
        for result in results:
            for description, values in result:
                f.writeline('\t', *([description] + list(map(lambda x: '%.2f' % x , values))))
            f.writeline('')

def main():
    makeGraphs()
    evalData()


if __name__ == "__main__":
    setupROOT()
    main()
