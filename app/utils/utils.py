import os
from pathlib import Path
import shutil
import random

def load_prompts():
    prompts = {}

    for file in Path("app/prompts").glob("*.md"):
        if str(file).endswith(".md"):
            with open(file, "r") as f:
                prompts[str(file).split("\\")[-1].replace(".md", "")] = f.read()

    return prompts

def choose_random_contracts(source_dir="Part_I", random_contracts_dir="Contracts", total_contracts=50):

    # remove the folder if it exists
    shutil.rmtree(Path(random_contracts_dir))
    Path(random_contracts_dir).mkdir(exist_ok=True)

    # Gather all PDF files from all subfolders
    all_pdf_files = list(Path(source_dir).rglob("*.pdf"))

    if len(all_pdf_files) < total_contracts:
        raise ValueError(f"Only {len(all_pdf_files)} PDF files found, but {total_contracts} requested.")

    # Randomly sample 50 unique files
    selected_files = random.sample(all_pdf_files, total_contracts)

    for file_path in selected_files:
        print(f"Copying: {file_path}")
        shutil.copy(file_path, Path(random_contracts_dir) / file_path.name)

    print(f"\n✅ Copied {total_contracts} contracts to '{random_contracts_dir}' folder.")