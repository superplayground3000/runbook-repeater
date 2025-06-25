#!/usr/bin/env python3
import sys
import json
import argparse
import os
import stat

# Define the hardcoded template file name for simplicity.
# In a more complex system, this could also be a command-line argument.
TEMPLATE_FILENAME = "runbook_template.sh"

def generate_runbook(json_file_path, output_script_path):
    """
    Generates an executable runbook script from a template and a JSON file.

    Args:
        json_file_path (str): The path to the JSON file containing parameters.
        output_script_path (str): The path where the generated runbook will be saved.
    """
    print(f"-> Reading parameters from: {json_file_path}")
    try:
        # Open and load the JSON file. The 'with' statement ensures the file is closed.
        with open(json_file_path, 'r') as f:
            params = json.load(f)
    except FileNotFoundError:
        print(f"Error: Parameter file not found at '{json_file_path}'", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from '{json_file_path}'. Please check its format.", file=sys.stderr)
        sys.exit(1)

    print(f"-> Reading template from: {TEMPLATE_FILENAME}")
    try:
        # Read the entire content of the template file.
        with open(TEMPLATE_FILENAME, 'r') as f:
            template_content = f.read()
    except FileNotFoundError:
        print(f"Error: Template file not found at '{TEMPLATE_FILENAME}'", file=sys.stderr)
        print("Please ensure it exists in the same directory as this script.", file=sys.stderr)
        sys.exit(1)

    # This is the core replacement logic.
    # We iterate through the key-value pairs from the JSON file and replace
    # the corresponding placeholders in the template string.
    # The placeholder format is {{key}}.
    generated_script = template_content
    for key, value in params.items():
        placeholder = f"{{{{{key}}}}}"
        # We convert value to string to handle JSON numbers/booleans correctly.
        generated_script = generated_script.replace(placeholder, str(value))

    print(f"-> Writing generated runbook to: {output_script_path}")
    try:
        # Write the final, populated script to the output file.
        with open(output_script_path, 'w') as f:
            f.write(generated_script)
    except IOError as e:
        print(f"Error: Could not write to output file '{output_script_path}': {e}", file=sys.stderr)
        sys.exit(1)

    # SRE best practice: Make the generated script executable by the owner and group.
    # This saves the operator from having to run 'chmod +x' themselves.
    # The permissions set are 755 (rwxr-xr-x).
    try:
        current_stats = os.stat(output_script_path)
        # S_IRWXU: Read, write, and execute by owner.
        # S_IRGRP, S_IXGRP: Read and execute by group.
        # S_IROTH, S_IXOTH: Read and execute by others.
        os.chmod(output_script_path, current_stats.st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
        print(f"-> Made script '{output_script_path}' executable.")
    except Exception as e:
        print(f"Warning: Could not make script executable: {e}", file=sys.stderr)


def main():
    """
    Main function to parse command-line arguments and run the generator.
    """
    # Create a parser for command-line arguments.
    # This provides a helpful, auto-generated '--help' message.
    parser = argparse.ArgumentParser(
        description="Generates a production runbook script from a template and a JSON parameter file.",
        formatter_class=argparse.RawTextHelpFormatter # For better help text formatting.
    )

    # Define the command-line arguments the script expects.
    parser.add_argument("json_file", help="The path to the input JSON parameter file.")
    parser.add_argument("output_file", help="The name of the generated output runbook script.")

    # Parse the arguments provided by the user.
    args = parser.parse_args()

    # Call the main logic function with the parsed arguments.
    generate_runbook(args.json_file, args.output_file)

    print("\n✅ Success! Your runbook is ready.")
    print(f"   To review: cat {args.output_file}")
    print(f"   To run:    ./{args.output_file}")


# Standard Python entry point.
if __name__ == "__main__":
    main()