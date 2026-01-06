import ROOT
import os
import subprocess
import sys
import time
from skimmer import AnalysisSkimmer

# --- Helper Function to find files ---
def get_files_from_das(dataset_path):
    """
    Queries DAS to get the list of ROOT files for a dataset.
    """
    print(f"Querying DAS for files in: {dataset_path} ...")
    cmd = f'dasgoclient --query="file dataset={dataset_path}"'
    
    try:
        process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        
        if process.returncode != 0:
            print(f"Error querying DAS: {stderr.decode()}")
            sys.exit(1)
            
        files = stdout.decode().strip().split('\n')
        files = [f for f in files if f] # Remove empty lines
        return files

    except Exception as e:
        print(f"Failed to run dasgoclient. Error: {e}")
        sys.exit(1)

def main():
    # --- Start Timer ---
    start_time = time.time() # <--- Record Start Time
    print(f"Process started at: {time.ctime(start_time)}")

    # --- Configuration ---
    
    # 1. Dataset & I/O
    # Instead of a single file, we define the Dataset Name and Redirector
    DATASET_NAME = "/EGamma/Run2022F-19Dec2023-v1/NANOAOD"
    #DATASET_NAME = "/MuonEG/Run2022D-22Sep2023-v1/NANOAOD"
    REDIRECTOR = "root://cmsxrootd.fnal.gov/"
    OUTPUT_FILE = "EGamma_Run2022F_Filtered.root"
    TREE_NAME = "Events"
    MAX_FILES = None 

    # 2. Define Triggers (OR Logic)
    TRIGGERS = [
        "HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL",
        "HLT_Ele32_WPTight_Gsf",
        "HLT_Ele16_Ele12_Ele8_CaloIdL_TrackIdL"
    ]

    # 3. Define MET Filters (AND Logic)
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

    # A. Setup Multi-threading (Important for large datasets!)
    ROOT.ROOT.EnableImplicitMT()

    # B. Get the File List
    # We check if we already have a text file list to save time
    file_list_txt = "input_files.txt"
    input_files = []

    if os.path.exists(file_list_txt):
        print(f"Reading file list from local {file_list_txt}...")
        with open(file_list_txt, "r") as f:
            input_files = [line.strip() for line in f]
    else:
        print(f"Going to the DAS")
        # Query DAS if we don't have the list yet
        lfns = get_files_from_das(DATASET_NAME)
        print(lfns)

        # Add the redirector to every file path so ROOT can access them
        input_files = [REDIRECTOR + lfn for lfn in lfns]
        print(input_files)
        # Save to file for next time
        with open(file_list_txt, "w") as f:
            for item in input_files:
                f.write(f"{item}\n")
        
        print(f"Found {len(input_files)} files.")

    if not input_files:
        print("No files found! Exiting.")
        sys.exit(1)

    # --- NEW: Apply File Limit ---
    if MAX_FILES is not None and MAX_FILES > 0:
        if MAX_FILES < len(input_files):
            print(f"Limit set: Processing only first {MAX_FILES} files out of {len(input_files)}.")
            input_files = input_files[:MAX_FILES]
        else:
            print(f"Limit set to {MAX_FILES}, but only {len(input_files)} available. Running all.")
    else:
        print("No limit set. Processing ALL files.")

    # C. Initialize Skimmer
    # RDataFrame accepts the LIST of files directly
    print(f"Initializing RDataFrame on {len(input_files)} files...")
    skimmer = AnalysisSkimmer(input_files, TREE_NAME)

    # D. Apply Analysis Logic
    # (Matches your previous main.py logic)
    skimmer.define_good_muons()
    skimmer.define_good_electrons()
    
    skimmer.apply_global_filters(triggers=TRIGGERS, met_filters=MET_FILTERS)

    # E. Define Output Branches
    # Be careful! Saving too many branches from a full dataset creates huge files.
    # Add any other variables you need here (e.g., Muon_pt, Electron_eta, etc.)
    branches_to_save = [
        "MET_pt", 
        "nMuon", 
        "nElectron",
    ]

    # F. Run and Save
    print("Starting processing (this may take a while)...")
    skimmer.save_snapshot(OUTPUT_FILE, branches_to_save)
    print("Done!")


    # --- End Timer ---
    end_time = time.time()
    elapsed_time = end_time - start_time
    
    # Convert seconds to nicer format (hours, minutes, seconds)
    hours = int(elapsed_time // 3600)
    minutes = int((elapsed_time % 3600) // 60)
    seconds = int(elapsed_time % 60)

    print("-" * 40)
    print("Analysis Complete!")
    print(f"Total files processed: {len(input_files)}")
    print(f"Total time elapsed: {hours}h {minutes}m {seconds}s")
    print("-" * 40)

if __name__ == "__main__":
    main()
