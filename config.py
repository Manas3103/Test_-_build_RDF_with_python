# config.py

# --- Dataset & I/O ---
DATASET_NAME = "/MuonEG/Run2022D-22Sep2023-v1/NANOAOD"
REDIRECTOR = "root://cmsxrootd.fnal.gov/"
OUTPUT_FILE = "MuonEG_Run2022D_Filtered.root"
TREE_NAME = "Events"

# --- Run Settings ---
# Set to an integer (e.g., 5) or None to run on all files
MAX_FILES = 2

# --- Analysis Cuts ---
# Triggers (OR Logic)
TRIGGERS = [
    "HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL",
    "HLT_Ele32_WPTight_Gsf",
    "HLT_Ele16_Ele12_Ele8_CaloIdL_TrackIdL"
]

# MET Filters (AND Logic)
MET_FILTERS = [
    "Flag_goodVertices",
    "Flag_HBHENoiseFilter",
    "Flag_HBHENoiseIsoFilter",
    "Flag_EcalDeadCellTriggerPrimitiveFilter",
    "Flag_BadPFMuonFilter",
    "Flag_BadPFMuonDzFilter",
    "Flag_eeBadScFilter"
]

# --- Output Content ---
BRANCHES_TO_SAVE = [
    "MET_pt",
    "nMuon",
    "nElectron",
    "Muon_pt", "Muon_eta",
    "Electron_pt", "Electron_eta"
]
