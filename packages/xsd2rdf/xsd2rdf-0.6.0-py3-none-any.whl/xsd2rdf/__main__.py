import argparse
import os
import sys
import glob
from .XSDtoRDF import XSDtoRDF


def define_args():
    parser = argparse.ArgumentParser(description='Convert XSD to RDF formats (SHACL, OWL, SKOS)')

    parser.add_argument("--XSD_FILE", "-x", type=str, 
                        help="XSD file to be converted into RDF")
    parser.add_argument("--OUTPUT_DIR", "-o", type=str, 
                        help="Output directory for generated files (default: same as XSD file)")
    parser.add_argument("--ABBREVIATIONS_FILE", "-a", type=str, 
                        help="File containing custom abbreviations, one per line")
    parser.add_argument("--FOLDER", "-f", type=str, help="Folder containing non related XSD files to be converted")
    parser.add_argument("--debug", "-d", action="store_true", 
                        help="Enable debug output")
    parser.add_argument("--namespaced-concepts", "-nc", action="store_true",
                        help="Use namespaced IRIs for SKOS concepts (targetnamespace/concepts/conceptschemename/conceptname) instead of flat IRIs (targetnamespace/concepts/conceptschemename_conceptname)")
    return parser.parse_args()

def main():
    args = define_args()
    
    xsd_file = args.XSD_FILE
    OUTPUT_DIR = args.OUTPUT_DIR
    folder = args.FOLDER
    abbreviations_file = args.ABBREVIATIONS_FILE
    debug = args.debug
    namespaced_concepts = args.namespaced_concepts
    
    if args.XSD_FILE:

        if not os.path.isfile(xsd_file):
            print(f"Error: XSD file {xsd_file} not found")
            sys.exit(1)
            
        if abbreviations_file and not os.path.exists(abbreviations_file):
            print(f"Warning: Abbreviations file {abbreviations_file} not found. Using default abbreviations.")
            abbreviations_file = None
            

        # If output directory is not provided, use the directory of the XSD file
        if not output_dir:
            output_dir = os.path.dirname(os.path.abspath(xsd_file))
            # If the dirname is empty (running in same dir as file), use current directory
            if not output_dir:
                output_dir = os.getcwd()

        # Create output directory if it doesn't exist
        if output_dir and not os.path.isdir(output_dir):
            os.makedirs(output_dir)

        print(f"Converting {xsd_file} to SHACL, SKOS and OWL...")
        
        xsd2rdf = XSDtoRDF(abbreviations_file, debug=debug, namespaced_concepts=namespaced_concepts)
        xsd2rdf.evaluate_file(xsd_file, output_dir)
        
        print(f"All conversions completed successfully! Output files saved in: {output_dir}")

    if args.FOLDER:
        if not os.path.isdir(folder):
            print(f"Error: Folder {folder} not found")
            sys.exit(1)

        xsd_files = glob.glob(os.path.join(folder, "*.xsd"))
        if not xsd_files:
            print(f"No XSD files found in folder {folder}")
            sys.exit(1)

        for xsd_file in xsd_files:
            output_dir = OUTPUT_DIR or os.path.dirname(xsd_file)
            if output_dir and not os.path.isdir(output_dir):
                os.makedirs(output_dir)

            file_name = os.path.basename(xsd_file)
            shacl_file = os.path.join(output_dir, file_name + ".shape.ttl")
            print(f"Converting {xsd_file} to SHACL, SKOS and OWL...")
            xsd2rdf = XSDtoRDF(abbreviations_file, debug=debug, namespaced_concepts=namespaced_concepts)
            xsd2rdf.evaluate_file(xsd_file, output_dir)

        print(f"All conversions completed successfully! Output files saved in: {output_dir}")

    else:
        # If no command is provided, show help
        define_args()
        print("Please specify a command. Use --help for more information.")
        sys.exit(1)

if __name__ == "__main__":
    main()
