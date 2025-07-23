import logging
import os
import json
from document_pipeline.pipeline import process_document
from document_pipeline.utils import save_processed_output

logging.basicConfig(level=logging.INFO)

if __name__ == "__main__":
    input_dir = "data"  # Directory containing files to process
    save_individual = False  # Set to True to also save individual outputs
    combined_results = []

    if not os.path.exists(input_dir):
        logging.error(f"Input directory '{input_dir}' does not exist.")
        exit(1)

    files = [os.path.join(input_dir, f) for f in os.listdir(input_dir)
             if os.path.isfile(os.path.join(input_dir, f))]

    if not files:
        logging.warning(f"No files found in '{input_dir}'.")
        exit(0)

    for file_path in files:
        logging.info(f"Processing file: {file_path}")
        result = process_document(file_path)
        output = result.to_dict()
        combined_results.append({
            "file": os.path.basename(file_path),
            **output
        })
        if save_individual:
            save_processed_output(result, file_path)

    # Save combined results
    processed_dir = "processed"
    if not os.path.exists(processed_dir):
        os.makedirs(processed_dir)
    combined_path = os.path.join(processed_dir, "all_processed.json")
    with open(combined_path, "w", encoding="utf-8") as f:
        json.dump(combined_results, f, ensure_ascii=False, indent=2)
    print(f"\nAll processed output saved to: {combined_path}") 