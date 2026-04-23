import os
import glob
import subprocess
import sys

def main():
    # Define input and output folders
    input_dir = "before"
    output_dir = "after"

    # Create directories if they don't exist
    if not os.path.exists(input_dir):
        os.makedirs(input_dir)
        print(f"Created input directory '{input_dir}'. Please put your PDF files there.")
        return

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Find all PDF files in the before directory
    pdf_files = glob.glob(os.path.join(input_dir, "*.pdf"))

    if not pdf_files:
        print(f"No PDF files found in '{input_dir}' directory.")
        return

    print(f"Found {len(pdf_files)} PDF files to process.")

    # Process each PDF file
    for pdf_file in pdf_files:
        print(f"\nProcessing: {pdf_file}")
        
        # Build the command based on split.bash
        command = [
            sys.executable, "pdf_splitter.py", 
            pdf_file, 
            "-o", output_dir,
            "--rows", "2", 
            "--cols", "2", 
            "--no-optimize", 
            "--no-auto-detect"
        ]
        
        try:
            # Run the command and wait for it to finish
            subprocess.run(command, check=True)
            print(f"Successfully processed {os.path.basename(pdf_file)}")
            
            # Remove the original file
            os.remove(pdf_file)
            print(f"Removed original PDF: {pdf_file}")
            
        except subprocess.CalledProcessError as e:
            print(f"Error processing {os.path.basename(pdf_file)}. Exit code: {e.returncode}")

if __name__ == "__main__":
    main()
