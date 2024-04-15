#! /usr/bin/env python3
# Author: Alexei Raspereza (December 2022)
# High pT tau ID efficiency measurement
# Datacard producer (W*->mu+v control region)
import ROOT
import math
import HighPT.Tau.utilsHighPT as utils
import HighPT.Tau.stylesHighPT as styles
import HighPT.Tau.analysisHighPT as analysis
from array import array

import os

#################################
#     definition of cuts        #
#################################
basecut = 'pt_1>100&&fabs(eta_1)<2.1&&metfilter>0.5&&njets==0&&extraelec_veto<0.5&&extramuon_veto<0.5&&extratau_veto<0.5&&idMedium_1>0.5&&njets==0&&iso_1<0.15'

metCut = "130"
mtCut  = "200"
dphiCut = "2.8"

#################################
#     definition of samples     #
#################################
RunBkgSampleNames = {
    'Run2' : ['DYJetsToLL_M-50','TTTo2L2Nu','TTToSemiLeptonic','TTToHadronic','ST_t-channel_antitop_4f_InclusiveDecays','ST_t-channel_top_4f_InclusiveDecays','ST_tW_antitop_5f_NoFullyHadronicDecays','ST_tW_top_5f_NoFullyHadronicDecays','WW','WZ','ZZ'],
    '2022' : ['DYto2L-4Jets_MLL-50','TTTo2L2Nu','TTtoLNu2Q','TTto4Q','TBbarQ_t-channel','TbarBQ_t-channel','TWminustoLNu2Q','TWminusto2L2Nu','TbarWplustoLNu2Q','TbarWplusto2L2Nu','WW','WZ','ZZ'],
    '2023' : ['DYto2L-4Jets_MLL-50','TTto2L2Nu','TTtoLNu2Q','TTto4Q','TWminustoLNu2Q','TWminusto2L2Nu','TbarWplustoLNu2Q','TbarWplusto2L2Nu','WW','WZ','ZZ'],
}

RunSigSampleNames = { 
    "Run2" : ['WToMuNu_M-200'],
    "2022" : ['WtoMuNu'],
    "2023" : ['WtoMuNu']
}

XTitle = {
    'mt_1'  : "m_{T} (GeV)",
    'pt_1'  : "muon p_{T} (GeV)",
    'eta_1' : "muon #eta",
    'metphi': "MET #phi",
    'phi_1' : "muon #phi",
    'met'   : "E_{T}^{mis} (GeV)"
}

def PlotWToMuNu(h_data_input,h_bkg_input,h_sig_input,**kwargs):

    era = kwargs.get('era','2023')
    var = kwargs.get('var','mt_1')
    plotLegend = kwargs.get('plotLegend',True)

    h_data = h_data_input.Clone("data")
    h_sig = h_sig_input.Clone("signal")
    h_bkg = h_bkg_input.Clone("background")
    styles.InitData(h_data)
    styles.InitHist(h_bkg,"","",ROOT.TColor.GetColor("#6F2D35"),1001)
    styles.InitHist(h_sig,"","",ROOT.TColor.GetColor("#FFCC66"),1001)

    print('')
    print('Yields ->')
    nbins = h_data.GetNbinsX()
    # log-normal systematic uncertainties (5% signal, 10% background)
    e_sig_sys = 0.05
    e_bkg_sys = 0.20
    for i in range(1,nbins+1):
        x_sig = h_sig.GetBinContent(i)
        x_bkg = h_bkg.GetBinContent(i)
        e_sig_stat = h_sig.GetBinError(i)
        e_sig = math.sqrt(e_sig_stat*e_sig_stat+e_sig_sys*e_sig_sys*x_sig*x_sig)
        h_sig.SetBinError(i,e_sig)
        e_bkg_stat = h_bkg.GetBinError(i)
        e_bkg = math.sqrt(e_bkg_stat*e_bkg_stat+e_bkg_sys*e_bkg_sys*x_bkg*x_bkg)
        h_bkg.SetBinError(i,e_bkg)
        xlower = int(h_data.GetBinLowEdge(i))
        xupper = int(h_data.GetBinLowEdge(i+1))
        x_data = h_data.GetBinContent(i)
        print('[%4i,%4i] ->  data = %5.0f   W = %5.0f   bkg = %4.0f'%(xlower,xupper,x_data,x_sig,x_bkg))
        

    print('')
    h_sig.Add(h_sig,h_bkg,1.,1.)
    h_tot = h_sig.Clone("total")
    styles.InitTotalHist(h_tot)

    h_ratio = utils.histoRatio(h_data,h_tot,'ratio')
    h_tot_ratio = utils.createUnitHisto(h_tot,'tot_ratio')

    styles.InitRatioHist(h_ratio)
    h_ratio.GetYaxis().SetRangeUser(0.001,1.999)
    
    utils.zeroBinErrors(h_sig)
    utils.zeroBinErrors(h_bkg)

    ymax = h_data.GetMaximum()
    if h_tot.GetMaximum()>ymax: ymax = h_tot.GetMaximum()

    h_data.GetYaxis().SetRangeUser(0.,1.2*ymax)
    h_data.GetXaxis().SetLabelSize(0)
    h_data.GetYaxis().SetTitle("events / bin")
    h_ratio.GetYaxis().SetTitle("obs/exp")
    h_ratio.GetXaxis().SetTitle(XTitle[var])

    # canvas and pads
    canvas = styles.MakeCanvas("canv","",600,700)
    # upper pad
    upper = ROOT.TPad("upper", "pad",0,0.31,1,1)
    upper.Draw()
    upper.cd()
    styles.InitUpperPad(upper)    
    
    h_data.Draw('e1')
    h_sig.Draw('hsame')
    h_bkg.Draw('hsame')
    h_data.Draw('e1same')
    h_tot.Draw('e2same')

    leg = ROOT.TLegend(0.55,0.45,0.8,0.7)
    styles.SetLegendStyle(leg)
    leg.SetTextSize(0.045)
    leg.AddEntry(h_data,'data','lp')
    leg.AddEntry(h_sig,'W#rightarrow #mu#nu','f')
    leg.AddEntry(h_bkg,'bkg','f')
    if plotLegend: leg.Draw()

    styles.CMS_label(upper,era=era)

    upper.Draw("SAME")
    upper.RedrawAxis()
    upper.Modified()
    upper.Update()
    canvas.cd()

    # lower pad
    lower = ROOT.TPad("lower", "pad",0,0,1,0.30)
    lower.Draw()
    lower.cd()
    styles.InitLowerPad(lower)

    h_ratio.Draw('e1')
    h_tot_ratio.Draw('e2same')
    h_ratio.Draw('e1same')
    nbins = h_ratio.GetNbinsX()
    xmin = h_ratio.GetXaxis().GetBinLowEdge(1)    
    xmax = h_ratio.GetXaxis().GetBinLowEdge(nbins+1)
    line = ROOT.TLine(xmin,1.,xmax,1.)
    line.SetLineStyle(1)
    line.SetLineWidth(2)
    line.SetLineColor(4)
    line.Draw()
    lower.Modified()
    lower.RedrawAxis()

    canvas.cd()
    canvas.Modified()
    canvas.cd()
    canvas.SetSelected(canvas)
    canvas.Update()
    print('')
    print('Creating control plot')
    canvas.Print(utils.baseFolder+"/"+era+"/figures/WMuNu/wmunu_"+var+"_"+era+".png")

def CreateCardsWToMuNu(fileName,h_data,h_bkg,h_sig,uncs,era):

    x_data = h_data.GetSumOfWeights()
    x_bkg  = h_bkg.GetSumOfWeights()
    x_sig  = h_sig.GetSumOfWeights() 

    cardsFileName = fileName + ".txt"
    rootFileName = fileName + ".root"
    f = open(cardsFileName,"w")
    f.write("imax 1    number of channels\n")
    f.write("jmax *    number of backgrounds\n")
    f.write("kmax *    number of nuisance parameters\n")
    f.write("---------------------------\n")
    f.write("observation   %3.1f\n"%(x_data))
    f.write("---------------------------\n")
    f.write("shapes * *  "+rootFileName+"  munu/$PROCESS munu/$PROCESS_$SYSTEMATIC \n")
    f.write("---------------------------\n")
    f.write("bin                 WtoMuNu     WtoMuNu\n")
    f.write("process             wmunu       bkg_munu\n")
    f.write("process             1           2\n")
    f.write("rate                %4.3f   %4.3f\n"%(x_sig,x_bkg))
    f.write("-----------------------------------\n")
    f.write("muEff         lnN   1.04        -\n")
    f.write("bkgNorm_munu  lnN   -           1.2\n")
    for unc in uncs:
        f.write(unc+"_"+era+"    shape  1.0          -\n")
    f.write("normW  rateParam  WtoMuNu wmunu  1.0  [0.5,1.5]\n")
    f.write("* autoMCStats 0\n")
    groups = "sysUnc group = normW muEff bkgNorm_munu"
    for unc in uncs:
        groups = groups + " " + unc + "_" + era
    f.write(groups+"\n")
    f.close()


if __name__ == "__main__":

    styles.InitROOT()
    styles.SetStyle()

    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument('-e','--era', dest='era', default='2023',choices=['UL2016','UL2017','UL2018','2022','2023'])
    parser.add_argument('-var','--variable',dest='variable',default='mt_1',choices=['mt_1','pt_1','met','phi_1','eta_1','metphi'])

    args = parser.parse_args() 
    period = args.era

    xbins_phi = utils.createBins(20,-3.14,3.14)
    xbins_eta = utils.createBins(20,-2.4,2.4)
    xbins_var = {
        'mt_1' : [200,300,400,500,600,700,800,1000,1200,1400],
        'pt_1' : [100,150,200,250,300,350,400,500,600,700],
        'met' : [100,150,200,250,300,350,400,500,600,700],
        'metphi' : xbins_phi,
        'phi_1' : xbins_phi,
        'eta_1' : xbins_eta
    }


    basefolder = utils.picoFolder+'/'+args.era
    var = args.variable    
    xbins = xbins_var[var]
    
    eras = utils.periods[args.era]

    print('')
    print('initializing SingleMuon samples >>>')
    singlemuSamples = {} # data samples dictionary
    for era in eras:
        singlemuNames = utils.singlemu[era]
        for singlemuName in singlemuNames:
            name = singlemuName + "_" + era
            singlemuSamples[name] = analysis.sampleHighPt(basefolder,era,
                                                       "munu",singlemuName,True)

    print('')
    print('initializing background samples >>>')
    bkgSamples = {} # MC bkg samples dictionary 
    for era in eras:
        run = utils.eraRun[era]
        bkgSampleNames = RunBkgSampleNames[run]
        for bkgSampleName in bkgSampleNames:
            name = bkgSampleName + "_" + era
            bkgSamples[name] = analysis.sampleHighPt(basefolder,era,
                                                  "munu",bkgSampleName,False)

    print('')
    print('initializing signal samples >>>')
    sigSamples = {} # MC signal samples dictionary 
    for era in eras:
        run = utils.eraRun[era]
        sigSampleNames = RunSigSampleNames[run]
        for sigSampleName in sigSampleNames:
            name = sigSampleName + "_" + era
            sigSamples[name] = analysis.sampleHighPt(basefolder,era,
                                                  "munu",sigSampleName,False)


    # apply hot jet veto in 2023 dataset
    if args.era=='2023':
        basecut += "&&hotjet_veto<0.5"

    jmetcut = 'met>'+metCut+'&&metdphi_1>'+dphiCut+'&&mt_1>'+mtCut # additional cuts (MET related variables)

    cut_data = basecut + "&&" + jmetcut
    cut = basecut + "&&" + jmetcut
    hist_data = analysis.RunSamples(singlemuSamples,var,cut_data,xbins,"data_obs")
    hist_bkg  = analysis.RunSamples(bkgSamples,var,cut,xbins,"bkgd")
    hist_sig  = analysis.RunSamples(sigSamples,var,cut,xbins,"wmunu")

    # making control plot
    plotlLegend = True
    if var=='phi_1' or var=='eta_1':
        plotlLegend = False


    PlotWToMuNu(hist_data,hist_bkg,hist_sig,
                era=args.era,var=var,plotLegend=plotlLegend)

    if var not in ['mt_1']:
        exit()

    hists_unc = {} # uncertainty histograms  
    for unc in utils.unc_jme:
        for variation in ["Up"]:
            name_unc = unc + variation
            var_unc = var + "_" + name_unc            
            met_cut = "met_" + name_unc + ">" + metCut 
            mt_1_cut = "mt_1_" + name_unc + ">" + mtCut
            metdphi_1_cut = "metdphi_1_" + name_unc + ">" + dphiCut
            jmetcut_unc = met_cut + "&&" + mt_1_cut + "&&" + metdphi_1_cut
            cut_unc = basecut + "&&" + jmetcut_unc
            name = "wmunu_" + name_unc
            hist_sys = analysis.RunSamples(sigSamples,var_unc,cut_unc,xbins,name)
            name_hist = "wmunu_" + unc
            hist_up,hist_down = utils.ComputeSystematics(hist_sig,hist_sys,name_hist)
            hists_unc[name_hist+"_"+args.era+"Up"] = hist_up
            hists_unc[name_hist+"_"+args.era+"Down"] = hist_down


    # saving histograms to file
    outputFileName = utils.baseFolder + "/" + args.era + "/datacards/munu_" + args.era
    print('')
    print("Saving shapes to file %s.root"%(outputFileName))
    fileOutput = ROOT.TFile(outputFileName+".root","recreate")
    fileOutput.mkdir("munu")
    fileOutput.cd("munu")
    hist_data.Write("data_obs")
    hist_sig.Write("wmunu")
    hist_bkg.Write("bkg_munu")
    for uncName in hists_unc:
        hists_unc[uncName].Write(uncName)
        
    fileOutput.Close()
    
    CreateCardsWToMuNu(outputFileName,hist_data,hist_bkg,hist_sig,utils.unc_jme,args.era)
    print("Saving cards to file %s.txt"%(outputFileName))
