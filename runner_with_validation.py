import ROOT
import os
import subprocess
import sys
import time

# Import your existing class and config
from skimmer import AnalysisSkimmer
import config 

class AnalysisRunner:
    def __init__(self, config_module):
        self.cfg = config_module
        self.files = []
        self.start_time = 0
        
        # Enable multi-threading
        ROOT.ROOT.EnableImplicitMT()

    def _query_das(self):
        print(f"Querying DAS for: {self.cfg.DATASET_NAME} ...")
        cmd = f'dasgoclient --query="file dataset={self.cfg.DATASET_NAME}"'
        try:
            process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = process.communicate()
            if process.returncode != 0:
                raise RuntimeError(f"DAS Error: {stderr.decode()}")
            files = stdout.decode().strip().split('\n')
            return [f for f in files if f]
        except Exception as e:
            print(f"FATAL: {e}")
            sys.exit(1)

    def get_file_list(self):
        safe_name = self.cfg.DATASET_NAME.replace("/", "_")[1:]
        cache_filename = f"filelist_{safe_name}.txt"

        if os.path.exists(cache_filename):
            print(f"Loading cached file list: {cache_filename}")
            with open(cache_filename, "r") as f:
                self.files = [line.strip() for line in f]
        else:
            print(f"Cache not found. Fetching from DAS...")
            lfns = self._query_das()
            self.files = [self.cfg.REDIRECTOR + lfn for lfn in lfns]
            with open(cache_filename, "w") as f:
                for item in self.files:
                    f.write(f"{item}\n")
        
        # Apply Limit
        if self.cfg.MAX_FILES and self.cfg.MAX_FILES < len(self.files):
            print(f"Limiting processing to {self.cfg.MAX_FILES} / {len(self.files)} files.")
            self.files = self.files[:self.cfg.MAX_FILES]
        else:
            print(f"Processing all {len(self.files)} files.")

    def run(self):
        self.start_time = time.time()
        print(f"--- Process Started: {time.ctime(self.start_time)} ---")
        
        # 1. Get Files
        self.get_file_list()
        if not self.files: return

        # 2. Initialize Skimmer
        print(f"Initializing RDataFrame...")
        skimmer = AnalysisSkimmer(self.files, self.cfg.TREE_NAME)

        # --- VERIFICATION STEP ---
        # We add a filter that passes EVERYTHING ("true") right at the start.
        # This forces RDataFrame to count every single event in every file.
        skimmer.df = skimmer.df.Filter("true", "Total Input Events")

        # 3. Apply Cuts
        print("Applying filters...")
        skimmer.define_good_muons()
        skimmer.define_good_electrons()
        skimmer.apply_global_filters(
            triggers=self.cfg.TRIGGERS, 
            met_filters=self.cfg.MET_FILTERS
        )

        # 4. Request Report (Bookkeeping)
        report = skimmer.df.Report()

        # 5. Save Output
        print(f"Starting Event Loop (writing to {self.cfg.OUTPUT_FILE})...")
        try:
            skimmer.save_snapshot(self.cfg.OUTPUT_FILE, self.cfg.BRANCHES_TO_SAVE)
            print("Snapshot saved successfully.")
        except Exception as e:
            print(f"\n!!! CRITICAL FAILURE !!!")
            print(f"The process crashed. This usually means a file could not be opened.")
            print(f"Error Details: {e}")
            sys.exit(1)

        # 6. Final Validation & Stats
        self.print_validation(report)

    def print_validation(self, report):
        end_time = time.time()
        elapsed = end_time - self.start_time
        
        print("\n" + "="*50)
        print("       PROCESSING VERIFICATION REPORT")
        print("="*50)
        
        # Iterate over the report to find our "Total Input Events" counter
        # report contains C++ objects, so we iterate like this:
        input_events = 0
        for cut in report:
            name = cut.GetName()
            count = cut.GetPass()
            if name == "Total Input Events":
                input_events = count
            
            # Print flow for the user
            print(f"{name:30} | Events: {count}")

        print("-" * 50)
        print(f"Files Requested : {len(self.files)}")
        print(f"Events Processed: {input_events}")
        print(f"Time Elapsed    : {elapsed/60:.2f} minutes")
        
        # LOGIC CHECK
        if input_events == 0:
            print("\n[WARNING] Total events is 0. Something is wrong (empty files?)")
        else:
            print("\n[SUCCESS] RDataFrame successfully ran over the event loop.")
            print("          If any file was missing/corrupt, the script would have crashed above.")
        print("="*50)

if __name__ == "__main__":
    runner = AnalysisRunner(config)
    runner.run()
