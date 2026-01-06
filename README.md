
# CMS NanoAOD Analysis Framework

This is a Python-based analysis framework using **ROOT RDataFrame** to skim and process CMS NanoAOD datasets. It features automatic file discovery via DAS, smart caching, multi-threading, and detailed event logging.

## 📂 Project Structure

| File | Description |
| --- | --- |
| **`config.py`** | **Control Center.** Edit this file to change datasets, triggers, cuts, and output branches. |
| **`skimmer.py`** | **Logic.** Contains the `AnalysisSkimmer` class with the RDataFrame physics logic (definitions & filters). |
| **`runner.py`** | **Standard Execution.** The main script to run the analysis efficiently. |
| **`runner_with_validation.py`** | **Validation Mode.** Same as `runner.py` but calculates and prints detailed event counts to prove data integrity. |

---

## 🚀 Quick Start

### 1. Prerequisites

Ensure you have a valid VOMS proxy to access CMS files via XRootD:

```bash
voms-proxy-init --voms cms --valid 192:00

```

### 2. Configure Your Run

Open `config.py` and set your parameters:

```python
# config.py
DATASET_NAME = "/MuonEG/Run2022D-22Sep2023-v1/NANOAOD"
MAX_FILES = 5  # Set to None to run on the full dataset
OUTPUT_FILE = "MyAnalysisOutput.root"

```

### 3. Run the Analysis

You have two options depending on your needs:

#### Option A: Standard Run (Recommended)

Use this for production runs or when you just want the output file.

```bash
python3 runner.py

```

#### Option B: Validation Run

Use this when you need to **confirm** that every single file was processed correctly. This script adds a "Total Input Events" counter and prints a cut-flow report at the end.

```bash
python3 runner_with_validation.py

```

**Example Validation Output:**

```text
==================================================
       PROCESSING VERIFICATION REPORT
==================================================
Total Input Events             | Events: 540230
Combined Trigger Cut           | Events: 250100
...
--------------------------------------------------
[SUCCESS] RDataFrame successfully ran over the event loop.

```

---

## ⚙️ Configuration (`config.py`)

You do not need to touch the logic code (`skimmer.py`) to change the analysis parameters. Everything is controlled via `config.py`:

* **`DATASET_NAME`**: The official CMS dataset path.
* **`REDIRECTOR`**: Use `root://cmsxrootd.fnal.gov/` for official data.
* **`MAX_FILES`**:
* `Integer` (e.g., `10`): Runs on the first 10 files (good for testing).
* `None`: Runs on the entire dataset.


* **`TRIGGERS`**: A list of HLT paths (OR logic).
* **`MET_FILTERS`**: A list of Flag paths (AND logic).
* **`BRANCHES_TO_SAVE`**: The list of variables to keep in the final output ROOT file.

---

## 🛠 Features

### Smart Caching

The script avoids querying DAS every time you run.

1. When you run a dataset (e.g., `MuonEG_Run2022D`), it creates a cache file: `filelist_MuonEG_Run2022D.txt`.
2. On the next run, it reads from this text file instantly.
3. If you change the dataset in `config.py`, the script automatically detects the change, queries DAS again, and creates a new cache file for the new dataset.

### Multi-Threading

The framework automatically enables `ROOT.ROOT.EnableImplicitMT()` to utilize all available CPU cores for faster processing.

---

Troubleshooting

**Q: I get `[3011] Unable to open file` errors.**

* **Solution:** Check your VOMS proxy (`voms-proxy-info`). If it is expired, run `voms-proxy-init`.
* **Solution:** Check `config.py`. Ensure `REDIRECTOR` is set to `root://cmsxrootd.fnal.gov/`.

**Q: I want to refresh the file list.**

* **Solution:** Just delete the text file starting with `filelist_...` in your directory. The script will fetch a fresh list from DAS on the next run.
