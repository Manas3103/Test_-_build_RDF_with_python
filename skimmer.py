import ROOT
from typing import List, Union

# Enable multi-threading for speed
ROOT.ROOT.EnableImplicitMT()

class AnalysisSkimmer:
    def __init__(self, input_files: Union[str, List[str]], tree_name: str):
        self.df = ROOT.RDataFrame(tree_name, input_files)
        self.output_branches = []
        print(f"Initialized RDataFrame with tree '{tree_name}'")

    def apply_global_filters(self, triggers: List[str] = [], met_filters: List[str] = []):
        """
        Applies Triggers (OR logic) and MET Filters (AND logic) if provided.
        """
        # 1. Apply Triggers (OR)
        if triggers:
            self.df = self.df.Filter(" || ".join(triggers), "Combined Trigger Cut")
            print(f"Applied {len(triggers)} Triggers")

        # 2. Apply MET Filters (AND)
        if met_filters:
            self.df = self.df.Filter(" && ".join(met_filters), "Combined MET Cut")
            print(f"Applied {len(met_filters)} MET Filters")

        return self

    def define_good_electrons(self):
        print(f"Defining Good Electrons")
        
        # Define mask and new branches
        self.df = self.df.Define("good_ele_mask", 
                                 f"Electron_pt >15 && abs(Electron_eta) < 2.4")
        
        # Create the new filtered branches
        self.df = self.df.Define("GoodElectron_pt", "Electron_pt[good_ele_mask]")
        self.df = self.df.Define("GoodElectron_eta", "Electron_eta[good_ele_mask]")
        
        # Add to save list
        self.output_branches.extend(["GoodElectron_pt", "GoodElectron_eta"])
        return self

    def define_good_muons(self):
        print(f"Defining Good Muons)")
        
        self.df = self.df.Define("good_mu_mask", 
                                 f"Muon_pt > 15 && abs(Muon_eta) < 2.4")
        
        self.df = self.df.Define("GoodMuon_pt", "Muon_pt[good_mu_mask]")
        self.df = self.df.Define("GoodMuon_eta", "Muon_eta[good_mu_mask]")
        
        self.output_branches.extend(["GoodMuon_pt", "GoodMuon_eta"])
        return self

    def save_snapshot(self, output_filename: str, extra_branches: List[str] = None):
        if extra_branches:
            self.output_branches.extend(extra_branches)
            
        print(f"Saving {len(self.output_branches)} branches to {output_filename}...")
        
        branch_vector = ROOT.std.vector('string')()
        for branch in self.output_branches:
            branch_vector.push_back(branch)

        report = self.df.Report()
        self.df.Snapshot("Events", output_filename, branch_vector)
        print("\n--- Cut Flow Report ---")
        report.Print()


