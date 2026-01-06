from skimmer import AnalysisSkimmer

def main():
    # --- Configuration ---
    #INPUT_FILE = "/uscms/home/msahoo/nobackup/Project_tzq/merged.root" # Change this to your file path
    INPUT_FILE = "root://cmsxrootd.fnal.gov//store/data/Run2022D/MuonEG/NANOAOD/22Sep2023-v1/40000/a74255fa-4b70-4ef0-9d47-1ee2651ac525.root"
    OUTPUT_FILE = "output_filtered.root"
    TREE_NAME = "Events"

    # Define Triggers (OR Logic)
    # Events passing ANY of these will be kept
    TRIGGERS = [
        "HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL",
        "HLT_Ele32_WPTight_Gsf",
        "HLT_Ele16_Ele12_Ele8_CaloIdL_TrackIdL"
    ]

    # Define MET Filters (AND Logic)
    # Events must pass ALL of these to be kept
    MET_FILTERS = [
        "Flag_goodVertices",
        "Flag_HBHENoiseFilter",
        "Flag_HBHENoiseIsoFilter",
        "Flag_EcalDeadCellTriggerPrimitiveFilter",
        "Flag_BadPFMuonFilter",
        "Flag_BadPFMuonDzFilter",
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
