"""Download the TUM BMW i3 dataset from Kaggle into data/raw/."""
import shutil
from pathlib import Path

import kagglehub

HANDLE = "atechnohazard/battery-and-heating-data-in-real-driving-cycles/versions/1"  # check version
TARGET = Path(__file__).resolve().parent.parent / "data" / "raw"

def main() -> None:
    cache_path = Path(kagglehub.dataset_download(HANDLE))
    TARGET.mkdir(parents=True, exist_ok=True)
    shutil.copytree(cache_path, TARGET, dirs_exist_ok=True)
    print(f"{len(list(TARGET.glob('Trip*.csv')))} trip files in {TARGET}")

if __name__ == "__main__":
    main()