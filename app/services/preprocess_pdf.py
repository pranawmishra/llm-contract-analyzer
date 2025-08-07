from pathlib import Path
import random
import shutil
import os
import fitz  # PyMuPDF
import re
import json

from pathlib import Path
import shutil
import random

class PDFPreProcessorPipeline:
    """
    This class is used to preprocess the contracts.
    It will extract the text from the contracts and save it to a json file.
    It will also clean the text and remove the headers and footers and page numbers and dates and monetary amounts.

    Example usage:
    ```python
    processed_contracts = PDFPreProcessorPipeline().process_contracts()
    ```
    """
    def __init__(self):
        self.contracts_dir = "app/dataContracts"

    def _clean_text(self, text):
        """Advanced text cleaning and normalization."""
        # Remove common PDF artifacts
        text = re.sub(r'[^\x00-\x7F]+', ' ', text)  # Remove non-ASCII characters
        text = re.sub(r'\x0c', ' ', text)  # Remove form feed characters
        
        # Fix common OCR errors and spacing issues
        text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)  # Add space between lowercase-uppercase
        text = re.sub(r'(\d)([A-Za-z])', r'\1 \2', text)  # Space between numbers and letters
        text = re.sub(r'([A-Za-z])(\d)', r'\1 \2', text)  # Space between letters and numbers
        
        # Normalize whitespace
        text = re.sub(r'\n+', '\n', text)  # Collapse multiple newlines
        text = re.sub(r'[ \t]+', ' ', text)  # Collapse tabs and multiple spaces
        text = re.sub(r'[\r\f\v]', ' ', text)  # Replace other whitespace chars
        
        # Remove excessive punctuation
        text = re.sub(r'[.]{3,}', '...', text)  # Replace multiple dots with ellipsis
        text = re.sub(r'[-]{2,}', '--', text)  # Replace multiple dashes
        text = re.sub(r'[_]{2,}', '__', text)  # Replace multiple underscores
        
        # Clean up common contract artifacts
        text = re.sub(r'\bPage\s+\d+\b', '', text)  # Remove page numbers
        text = re.sub(r'\b\d{1,2}\/\d{1,2}\/\d{2,4}\b', '[DATE]', text)  # Normalize dates
        text = re.sub(r'\$[\d,]+\.?\d*', '[AMOUNT]', text)  # Normalize monetary amounts
        
        return text.strip()

    def _remove_headers_footers(self, text, threshold=0.3):
        """Remove likely headers/footers by detecting repeated content."""
        lines = text.split('\n')
        if len(lines) < 10:  # Skip if too few lines
            return text
        
        line_counts = {}
        for line in lines:
            clean_line = line.strip()
            if clean_line and len(clean_line) > 5:  # Ignore very short lines
                line_counts[clean_line] = line_counts.get(clean_line, 0) + 1
        
        # Find lines that appear frequently (likely headers/footers)
        total_lines = len(lines)
        repeated_lines = {
            line for line, count in line_counts.items() 
            if count / total_lines > threshold and count > 2
        }
        
        # Remove repeated lines
        filtered_lines = [
            line for line in lines 
            if line.strip() not in repeated_lines
        ]
        
        return '\n'.join(filtered_lines)

    def _extract_text_from_pdf(self, pdf_path):
        """Extract and normalize text from a single PDF."""
        try:
            doc = fitz.open(pdf_path)
            full_text = ""
            
            for page_num, page in enumerate(doc):
                page_text = page.get_text()
                
                # Skip pages that are mostly empty
                if len(page_text.strip()) < 50:
                    continue
                    
                full_text += f"\n--- Page {page_num + 1} ---\n"
                full_text += page_text
            
            doc.close()
            
            # Apply cleaning and preprocessing
            cleaned_text = self._clean_text(full_text)
            cleaned_text = self._remove_headers_footers(cleaned_text)
            
            return cleaned_text
        
        except Exception as e:
            print(f"Error extracting text from {pdf_path}: {e}")
            return ""

    def process_contracts(self):
        """Walk through the folders and preprocess contracts with enhanced features."""
        # process contracts
        contract_texts = []
        
        pdf_files = list(Path(self.contracts_dir).glob("*.pdf"))
        print(f"Found {len(pdf_files)} PDF files to process...")
        
        for i, filename in enumerate(pdf_files, 1):
            try:
                print(f"Processing {i}/{len(pdf_files)}: {filename.name}")
                
                text = self._extract_text_from_pdf(filename)
                
                contract_data = {
                    "contract_id": filename.stem,  # filename without extension
                    "filename": filename.name,
                    "text": text,
                    "char_count": len(text),
                    "word_count": len(text.split())
                }
                
                contract_texts.append(contract_data)
                
            except Exception as e:
                print(f"Error processing {filename}: {e}")
                continue
        
        print(f"Successfully processed {len(contract_texts)} contracts")
        # Save as JSON (optional)
        with open("app/data/processed_contracts.json", "w", encoding="utf-8") as f:
            json.dump(contract_texts, f, indent=2, ensure_ascii=False)

# Example usage
if __name__ == "__main__":
    # choose_random_contracts()
    processed_contracts = PDFPreProcessorPipeline().process_contracts()

    # Save as JSON (optional)
    with open("processed_contracts.json", "w", encoding="utf-8") as f:
        json.dump(processed_contracts, f, indent=2, ensure_ascii=False)

    print(f"Processed {len(processed_contracts)} contracts.")
    
