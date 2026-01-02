import ROOT
from typing import List, Union

# Enable multi-threading for speed
ROOT.ROOT.EnableImplicitMT()

class AnalysisSkimmer:
    def __init__(self, input_files: Union[str, List[str]], tree_name: str):
        self.df = ROOT.RDataFrame(tree_name, input_files)
        self.output_branches = []
        print(f"Initialized RDataFrame with tree '{tree_name}'")

    def apply_multiple_triggers(self, trigger_list: List[str] = None, MET_Filter: List[str] = None):
        """
        Filters events if ANY of the triggers in the list fired.
        """
        if not trigger_list:
            print("NO Triggers are applied")
            return self

        if not MET_Filter:
            print("NO MET Filters are applied")
            return self


        # Join all triggers with "||" (OR operator)
        trigger_logic = " || ".join(trigger_list)
        print(f"Applying Trigger Logic: {trigger_logic}")

        # Join all MET Filters with "&&" (AND operator)
        MET_logic = " && ".join(MET_Filter)
        print(f"Applying MET Filters: {MET_logic}")

        
        self.df = self.df.Filter(trigger_logic, "Combined Trigger Cut")
        self.df = self.df.Filter(MET_logic, "Combined MET Cut")
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

# --- MAIN ---
if __name__ == "__main__":
    # Create Skimmer
    skimmer = AnalysisSkimmer("/uscms/home/msahoo/nobackup/Project_tzq/2022Data_Muon.root", "Events")

    # 1. Apply Multiple Triggers
    triggers = ["HLT_IsoMu24", "HLT_Ele32_WPTight_Gsf"]
    #MET = [
    skimmer.apply_multiple_triggers(triggers)

    # 2. Select Objects
    skimmer.define_good_electrons()
    skimmer.define_good_muons()

    # 3. Save
    skimmer.save_snapshot("output_multi_trigger.root", extra_branches=["MET_pt"])
