import time
from ROOT import TFile, TH1F  # @UnresolvedImport

LEP_ENERGIES = [88.48021, 89.47158, 90.22720, 91.23223, 91.97109, 92.97091, 93.71841]
LATEXE = r"e$^+$e$^-$"
LATEXM = r"\textmu$^+$\textmu$^-$"
LATEXT = r"\texttau$^+$\texttau$^-$"
LATEXQ = r"q$^+$q$^-$"

class Z0Data():

    def __init__(self):
        self.events = []

    @classmethod
    def fromROOTFile(cls, file, treename):
        """
        Arguments:
        file     -- name of *.root file 
        treename -- name of tree in file
        """
        t1 = time.time()
        f = TFile(file)
        tree = f.Get(treename)
        data = cls()
        events = []
        for event in tree:
            events.append({"run": event.run,
                           "event": event.event,
                           "Ncharged": event.Ncharged,
                           "Pcharged": event.Pcharged,
                           "E_ecal": event.E_ecal,
                           "E_hcal": event.E_hcal,
                           "E_lep": event.E_lep,
                           "cos_thru": event.cos_thru,
                           "cos_thet": event.cos_thet})
        data.events = events
        t2 = time.time()
        print("loaded %s_%s in %.2f seconds, %d entries" % (file, treename, t2 - t1, data.getLength()))
        return data

    def addEvent(self, event):
        self.events.append(event)

    def getEvent(self, i):
        return self.events[i]

    def getEvents(self):
        return self.events

    def getLength(self):
        return len(self.events)

    def makeHistogramm(self, name, datatype, bincount, xmin, xmax):
        hist = TH1F(name, '', bincount, xmin, xmax)
        for event in self.events:
            hist.Fill(event[datatype])
        return hist

    def cut(self, cutFunc):
        """make cut with function cutFunc

        Arguments:
        cutFunc -- cut-function, must return True/False
        """
        cutdata = Z0Data()
        for event in self.events:
            if cutFunc(event):
                cutdata.addEvent(event)
        return cutdata

    def splitEnergies(self):
        energies = [0] + LEP_ENERGIES + [1000]
        cutenergies = []
        for i in range(1, len(energies) - 1):
            cutenergies.append((energies[i], ((energies[i - 1] + energies[i]) / 2, (energies[i] + energies[i + 1]) / 2)))
        datas = dict()
        for (energie, (elow, ehigh)) in cutenergies:
            datas[energie] = self.cut(lambda e:elow <= e["E_lep"]*2 <= ehigh)
        return datas
        
