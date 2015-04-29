from z0 import Z0Data
from txtfile import TxtFile

if __name__ == '__main__':
    files = [('mc/ee', 'h3'), ('mc/mm', 'h3'), ('mc/tt', 'h3'), ('mc/qq', 'h3'), ('daten/daten_1', 'h33')]
    for file, treename in files:
        data = Z0Data.fromROOTFile("../data/%s.root" % file, treename)
        with TxtFile('../data/%s.txt' % file, 'w') as f:
            for event in data.getEvents():
                f.writeline('\t', *list(map(str, [event["run"], event["event"], event["Ncharged"], event["Pcharged"], event["E_ecal"], event["E_hcal"], event["E_lep"], event["cos_thru"], event["cos_thet"]])))