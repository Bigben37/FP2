from ROOT import TFile # @UnresolvedImport
import timeit

def testDict():
    f = TFile('../data/mc/ee.root')
    tree = f.Get('h3')
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
        
def testList():
    f = TFile('../data/mc/ee.root')
    tree = f.Get('h3')
    events = []
    #for event in tree:
        #events.append([event.run, event.event, event.Ncharged, event.Pcharged, event.E_ecal, event.E_hcal, event.E_lep, event.cos_thru, event.cos_thet])
    for i in range(tree.GetEntries()):
        print(tree.GetEvent(0).GetLeaf("Pcharged").GetValue(i))

if __name__ == '__main__':
    #print(timeit.timeit("testDict()", setup="from __main__ import testDict", number=1))
    print(timeit.timeit("testList()", setup="from __main__ import testList", number=1))