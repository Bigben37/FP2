#!/usr/bin/python
__author__ = "Benjamin Rottler (benjamin@dierottlers.de)"

import os
from numpy import sqrt
from functions import loadCSVToList, setupROOT
from txtfile import TxtFile
from physconsts import h_Js, mub_JT
from op import OPData, inductorIToB, prepareGraph
from ROOT import TCanvas, TPad, TGaxis, gStyle


def makeTwoScalesGraph(file):
    print(file)
    ch1 = OPData.fromPath('../data/part3/%s' % file, 1)
    ch2 = OPData.fromPath('../data/part3/%s' % file, 2)

    print('make canvas + pad')
    c = TCanvas('c-%s' % file, '', 1280, 720)
    pad = TPad('pad-%s' % file, '', 0, 0, 1, 1)
    pad.Draw()
    pad.cd()

    print('frame')
    frame = pad.DrawFrame(0, min(ch1.getY())*1.1, 0.051, max(ch1.getY())*1.1)
    frame.SetXTitle('t / s')
    frame.GetXaxis().CenterTitle()
    frame.SetYTitle('Spannung Spule 2: U_{2} / V')
    frame.GetYaxis().CenterTitle()
    frame.GetYaxis().SetLabelColor(4)
    frame.GetYaxis().SetTitleColor(4)

    print('g1')
    g1 = ch1.makeGraph('g1-%s' % file)
    prepareGraph(g1)
    g1.Draw('PX')

    print('overlay')
    c.cd()
    overlay = TPad('overlay-%s' % file, '', 0, 0, 1, 1)
    overlay.SetFillStyle(4000)  # transparent
    overlay.SetFillColor(0)  # white
    overlay.SetFrameFillStyle(4000)  # transparent
    overlay.Draw()
    overlay.cd()

    print('g2')
    g2 = ch2.makeGraph('g2-%s' % file)
    prepareGraph(g2, 2)
    g2ymin = min(ch2.getY())
    xmin = pad.GetUxmin()
    xmax = pad.GetUxmax()
    ymin = 1.1 * g2ymin
    ymax = abs(ymin)
    if file == '07.tab':  # same scale like 06.tab
        ymin, ymax = -0.07128, 0.07128
    oframe = overlay.DrawFrame(xmin, ymin, xmax, ymax)
    oframe.GetXaxis().SetLabelOffset(99)
    oframe.GetYaxis().SetLabelOffset(99)
    oframe.GetYaxis().SetTickLength(0)
    g2.Draw('PX')

    print('axis')
    axis = TGaxis(xmax, ymin, xmax, ymax, ymin, ymax, 510, "+L")
    axis.SetTitle('Spannung Photodiode: U_{ph} / V')
    axis.CenterTitle()
    axis.SetTitleOffset(1.2)
    axis.Draw()

    print('print')
    c.Update()
    c.Print('../img/part3/%s.pdf' % file[:-4], 'pdf')


def makeGraphs():
    gStyle.SetPadTickY(0)
    files = os.listdir(os.path.join(os.getcwd(), '../data/part3/'))
    files.sort()
    files = files[0:]
    for file in files:
        if file.endswith('.tab'):
            makeTwoScalesGraph(file)
    gStyle.SetPadTickY(1)


def evalNuclearSpin():
    results = []
    data = loadCSVToList('../data/part3/part3.txt')
    
    tabledata = []
    for d in data[-4:]:
        tabledata.append([d[0], d[2]] + d[4:-2])
    
    with TxtFile('../src/tab_part3_data.tex', 'w') as f:
        f.write2DArrayToLatexTable(tabledata, 
                                   [r"$I_\text{L}$ / mA", r"$\nu$ / kHz", 
                                    "$I_1$ / mA", "$s_{I_1}$ / mA", "$I_1'$ / mA", "$s_{I_1'}$ / mA"],
                                   ['%.1f', '%.2f', '%d', '%d', '%d', '%d'], 
                                   'Messdaten des Doppelresonanzexperiments.', 'tab:part3:data')
    
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
        Bhor, sBhor = abs(B1 - B1_) / 2, sqrt(sB1 ** 2 + sB1_ ** 2) / 2
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
    with TxtFile('../calc/part3.txt', 'w') as f:
        for result in results:
            for description, values in result:
                f.writeline('\t', *([description] + list(map(lambda x: '%.2f' % x, values))))
            f.writeline('')
            
    tableresults = []
    for result in results:
        flattend = [item for sublist in result for item in sublist[1]]
        flattend.pop(7)
        flattend.pop(6)
        flattend.pop(3)
        flattend.pop(1)
        tableresults.append(flattend)
            
    with TxtFile('../src/tab_part3_results.tex', 'w') as f:
        f.write2DArrayToLatexTable(tableresults[-4:], 
                                   [r"$I_\text{L}$ / mA", r"$\nu$ / kHz", r"$B_\text{hor}$ / \textmu T", r"$s_{B_\text{hor}}$ / \textmu T", 
                                    "$I$", "$s_I$"], 
                                   ['%.1f', '%.2f', '%.1f', '%.1f', '%.2f', '%.2f'], 
                                   r"Berechnete horizontale Komponenten des Erdmagnetfeldes und Kernspin von Rubidium für das Doppelresonanzexperiment bei verschiedenen Lasterströmen $I_\text{L}$ und RF-Sender Frequenzen $\nu$.", 
                                   "tab:part3:results")


def main():
    makeGraphs()
    evalNuclearSpin()


if __name__ == "__main__":
    setupROOT()
    main()
