from functions import loadCSVToList
from txtfile import TxtFile

def main():
    # luminosity
    lums = loadCSVToList('../data/daten/lum.txt')
    with TxtFile('../src/tab_lums.tex', 'w') as f:
        f.write2DArrayToLatexTable(lums, 
                                   [r"$\sqrt{s}$ / GeV", r"$L$ / (1/nb)", r"$s_L^\text{stat}$ / (1/nb)", 
                                    r"$s_L^\text{sys}$ / (1/nb)", r"$s_L^\text{tot}$ / (1/nb)"], 
                                   ["%.2f"] + ["%.0f"]*4, 
                                   "Zeitlich integrierte Luminosität mit statistischem, systematischem und totalem " + 
                                   "Fehler für verschiedene Schwerpunktsenergieen.", 
                                   "tab:lums")
    
    # beam correction
    corr = loadCSVToList('../data/daten/corr.txt')
    with TxtFile('../src/tab_beamcorr.tex', 'w') as f:
        f.write2DArrayToLatexTable(corr, 
                                   [r"$\sqrt{s}$ / GeV", r"$c_\text{beam, \qq}$ / nb", r"$c_\text{beam, \leplep}$ / nb"], 
                                   ["%.2f", "%.1f", "%.2f"], 
                                   r"Strahlungskorrekturen für hadronische und leptonische Zerfälle bei verschiedenen Schwerpunktsenergieen.", 
                                   "tab:beamcorrs")

if __name__ == '__main__':
    main()