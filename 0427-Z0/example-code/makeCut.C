#include "TFile.h"
#include "TTree.h"
#include "TH1F.h"
#include "TString.h"
#include <iostream>

void makeCut(){
  TFile* files[5];
  files[0] = new TFile("../data/mc/ee.root");
  files[1] = new TFile("../data/mc/mm.root");
  files[2] = new TFile("../data/mc/tt.root");
  files[3] = new TFile("../data/mc/qq.root");
  files[4] = new TFile("../data/daten/daten_1.root");

  //Make cuts and get the number of events

  files[0]->cd(); //ee ntuple
  //without cuts
  TTree *hee = (TTree*)files[0]->Get("h3");
  float nEvents_ee_all = hee->Draw("E_ecal>>heEcal_ee_all(200,0,200)","");
  TH1F* heEcal_ee_all = (TH1F*) gDirectory->Get("heEcal_ee_all");
  cout << ("n_ee_all=") << nEvents_ee_all << endl;


  files[1]->cd(); //mm ntuple
  //with cuts
  TString mmcuts="Ncharged<2 && Pcharged>0";
  TTree *hmm = (TTree*)files[1]->Get("h3");
  float nEvents_mm_all = hmm->Draw("E_ecal>>heEcal_mm_all(200,0,200)",mmcuts);
  TH1F* heEcal_mm_all = (TH1F*) gDirectory->Get("heEcal_mm_all");
  cout << ("n_mm_all=") << nEvents_mm_all << endl;

}
