import ROOT
from typing import List, Union

# Enable multi-threading for speed
ROOT.ROOT.EnableImplicitMT()

class AnalysisSkimmer:
    def __init__(self, input_files: Union[str, List[str]], tree_name: str):
        self.df = ROOT.RDataFrame(tree_name, input_files)
        self.output_branches = []
        self.my_histograms = []
        print(f"Initialized RDataFrame with tree '{tree_name}'")


    def book_monitor_histos(self, df, step_name):
        """
        Books nMuon and nElectron histograms for the current state of the dataframe.
        """
        # Histogram arguments: (Name, Title, nBins, min, max)
        
        # Monitor nMuon
        h_mu = df.Histo1D(
            (f"nMuon_{step_name}", f"nMuon after {step_name};Multiplicity;Events", 10, 0, 10), 
            "nMuon"
        )
        
        # Monitor nElectron
        h_el = df.Histo1D(
            (f"nElectron_{step_name}", f"nElectron after {step_name};Multiplicity;Events", 10, 0, 10), 
            "nElectron"
        )

        # Add to our list so we keep track of them
        self.my_histograms.append(h_mu)
        self.my_histograms.append(h_el)

    def apply_global_filters(self, triggers: List[str] = [], met_filters: List[str] = []):
        """
        Applies Triggers (OR logic) and MET Filters (AND logic) if provided.
        """
        self.book_monitor_histos(self.df, "Step0_NoCuts")

        # 1. Apply Triggers (OR)
        if triggers:
            self.df = self.df.Filter(" || ".join(triggers), "Combined Trigger Cut")
            print(f"Applied {len(triggers)} Triggers")
        
        self.book_monitor_histos(self.df, "Step1_triggers")

        # 2. Apply MET Filters (AND)
        if met_filters:
            self.df = self.df.Filter(" && ".join(met_filters), "Combined MET Cut")
            print(f"Applied {len(met_filters)} MET Filters")
        
        self.book_monitor_histos(self.df, "Step2_MetFilters")

        #3. Apply additional cuts
        self.df = self.df.Filter("PV_npvsGood > 0 && nJet>0", "Has Good PV")
        self.book_monitor_histos(self.df, "Step3_GoodPV")
        self.df = self.df.Filter("nJet>0", "Atleast one Jet is required")
        #self.book_monitor_histos(self.df, "Step4_nJet>0")
        self.df = self.df.Filter("nMuon + nElectron >= 3" , "Only allowed 3 Leptons")
        #self.book_monitor_histos(self.df, "Step5_More_than_3Lepton")
        print("3 Lepton >1 jet and the GOOD_PV cut is applied")

        return self.df

    def define_good_electrons(self):
        print(f"Defining Good Electrons")
        
        # Define mask and new branches
        self.df = self.df.Define("good_ele_mask","Electron_pt >15 && abs(Electron_eta) < 2.4 && Electron_cutBased == 4")
        self.df = self.df.Define("tight_ele_mask","Electron_pt >15 && abs(Electron_eta) < 2.4 && Electron_cutBased == 4 && Electron_mvaTTH > 0.90")
        
        # Create the new filtered branches
        self.df = self.df.Define("GoodElectron_pt", "Electron_pt[good_ele_mask]")
        self.df = self.df.Define("GoodElectron_eta", "Electron_eta[good_ele_mask]")
        self.df = self.df.Define("nGoodElectron", "Sum(good_ele_mask)")

        self.df = self.df.Define("TightElectron_pt", "Electron_pt[tight_ele_mask]")
        self.df = self.df.Define("TightElectron_eta", "Electron_eta[tight_ele_mask]")
        self.df = self.df.Define("nTightElectron", "Sum(tight_ele_mask)")

        
        # Add to save list
        self.output_branches.extend(["GoodElectron_pt", "GoodElectron_eta","nGoodElectron","TightElectron_pt","TightElectron_eta","nTightElectron" ])
        return self

    def define_good_muons(self):
        print(f"Defining Good Muons)")
        
        self.df = self.df.Define("good_mu_mask", 
                                 "Muon_pt > 15 && abs(Muon_eta) < 2.4")
        
        self.df = self.df.Define("GoodMuon_pt", "Muon_pt[good_mu_mask]")
        self.df = self.df.Define("GoodMuon_eta", "Muon_eta[good_mu_mask]")
        self.df = self.df.Define("nGoodMuon", "Sum(good_mu_mask)")
        
        self.output_branches.extend(["GoodMuon_pt", "GoodMuon_eta", "nGoodMuon"])
        return self

    def _save_cutflow(self, report, output_filename):
        # Convert the C++ RCutFlowReport object to a standard Python list
        cuts = list(report)
        n_cuts = len(cuts)
        
        # Create the histogram with the correct number of bins
        h_cutflow = ROOT.TH1D("cutflow", "Cut Flow", n_cuts, 0, n_cuts)
        
        # Loop over the list we just created
        for i, cut in enumerate(cuts):
            cut_name = cut.GetName()
            cut_pass = cut.GetPass()
            
            # Fill the histogram
            h_cutflow.GetXaxis().SetBinLabel(i+1, cut_name)
            h_cutflow.SetBinContent(i+1, cut_pass)
            
            # Optional: Print to console for debugging
            print(f"Cut: {cut_name}, Pass: {cut_pass}")

        # Save to file
        f_out = ROOT.TFile(output_filename, "UPDATE")

        # Create a folder for plots (optional, but keeps things organized)
        f_out.mkdir("ControlPlots")
        f_out.cd("ControlPlots")

        # Loop through the list and write each histogram
        for h in self.my_histograms:
            h.Write()
        h_cutflow.Write()
        f_out.Close()

    def save_snapshot(self, output_filename: str, extra_branches: List[str] = None):
        if extra_branches:
            self.output_branches.extend(extra_branches)
            
        print(f"Saving {len(self.output_branches)} branches to {output_filename}...")
        
        branch_vector = ROOT.std.vector('string')()
        for branch in self.output_branches:
            branch_vector.push_back(branch)
        try:
            ROOT.RDF.Experimental.AddProgressBar(self.df)
        except:
            print("The progress bar is not supporting !! ")
            pass # Older ROOT versions might not have this

        report = self.df.Report()

        # Run Snapshot (Event Loop happens here)
        opts = ROOT.RDF.RSnapshotOptions()
        opts.fMode = "RECREATE"
        self.df.Snapshot("Events", output_filename, branch_vector, opts)

        # Call the helper function to add the histogram
        self._save_cutflow(report, output_filename)

        print("\n--- Cut Flow Report ---")
        report.Print()


