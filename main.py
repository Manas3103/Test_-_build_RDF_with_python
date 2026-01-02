from skimmer import AnalysisSkimmer

def main():
    # --- Configuration ---
    INPUT_FILE = "/uscms/home/msahoo/nobackup/Project_tzq/2022Data_Muon.root"  # Change this to your file path
    OUTPUT_FILE = "output_filtered.root"
    TREE_NAME = "Events"

    # Define Triggers (OR Logic)
    # Events passing ANY of these will be kept
    TRIGGERS = [
        "HLT_IsoMu24",
        "HLT_Ele32_WPTight_Gsf",
        "HLT_Mu50"
    ]

    # Define MET Filters (AND Logic)
    # Events must pass ALL of these to be kept
    MET_FILTERS = [
        "Flag_goodVertices",
        "Flag_globalSuperTightHalo2016Filter",
        "Flag_HBHENoiseFilter",
        "Flag_HBHENoiseIsoFilter",
        "Flag_EcalDeadCellTriggerPrimitiveFilter",
        "Flag_BadPFMuonFilter",
        "Flag_eeBadScFilter"
    ]

    # --- Execution ---
    
    # 1. Initialize
    skimmer = AnalysisSkimmer(INPUT_FILE, TREE_NAME)

    # 2. Apply cuts
    skimmer.define_good_muons()
    skimmer.define_good_electrons()

    # 3. Apply Global Filters
    skimmer.apply_global_filters(triggers=TRIGGERS, met_filters=MET_FILTERS)
    
    extra_branches=["MET_pt","nMuon","nElectron"]

    # 4. Run and Save
    skimmer.save_snapshot(OUTPUT_FILE, extra_branches)

if __name__ == "__main__":
    main()
