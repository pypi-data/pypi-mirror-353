import os
import argparse
from spc_export import spcexport

def main():
    parser = argparse.ArgumentParser(
        description="Utility for parsing spc files.")
    parser.add_argument("input_file", help="Path to the input file.")
    parser.add_argument("output_file",nargs="?", default=None, help="Path to the output file.")

    args = parser.parse_args()

    # Validate input file
    if not os.path.isfile(args.input_file):
        print(f"Error: Input file '{args.input_file}' does not exist.")
        return

    record = spcexport.SPC_Record(args.input_file)
    record.write_zip_file()

if __name__ == "__main__":
    main()
    
