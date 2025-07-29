from restful_checker.engine.analyzer import analyze_api
from urllib.parse import urlparse
import os
import sys
import requests
import tempfile
import json
import yaml
import argparse

# Import the help function from the correct module
try:
    from restful_checker.tools.help_restful_checker import show_help
except ModuleNotFoundError:
    print("❌ Error: The 'tools' module or 'help_restful_checker' file is missing in the 'restful_checker' package.")
    print("👉 Ensure the file 'restful_checker/tools/help_restful_checker.py' exists and contains the 'show_help' function.")
    sys.exit(1)

def is_valid_file(path):
    return os.path.isfile(path) and path.endswith(('.json', '.yaml', '.yml'))

def is_valid_openapi(path):
    """Check if file OpenAPI is valid."""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            if path.endswith('.json'):
                data = json.load(f)
            else:
                data = yaml.safe_load(f)

            if 'openapi' in data or 'swagger' in data:
                return True
            return False
    except Exception as e:
        print(f"❌ Error analyzing the file: {e}")
        return False

def parse_arguments():
    """Function to handle command line arguments."""
    parser = argparse.ArgumentParser(
        description="Check RESTful API compliance from OpenAPI definitions and generate reports."
    )
    parser.add_argument(
        "path",
        help="The OpenAPI definition file or URL (must end in .json, .yaml, or .yml).",
        nargs="?"
    )
    parser.add_argument(
        "--output-format",
        help="Output format: html, json, or both (default: html)",
        choices=["html", "json", "both"],
        default="html"
    )
    parser.add_argument(
        "--output-folder",
        help="Destination folder for output reports (default: ./html)",
        default="html"
    )
    return parser.parse_args()

def main():
    args = parse_arguments()

    # If no path argument is provided, show help
    if args.path is None:
        show_help()
        sys.exit(0)

    path = args.path
    parsed = urlparse(path)

    if parsed.scheme in ("http", "https"):
        try:
            response = requests.get(path, timeout=10)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"❌ Failed to fetch URL: {e}")
            sys.exit(1)

        suffix = '.yaml' if path.endswith(('.yaml', '.yml')) else '.json'
        with tempfile.NamedTemporaryFile(delete=False, mode='w+', suffix=suffix, encoding='utf-8') as tmp:
            tmp.write(response.text)
            tmp.flush()
            path = tmp.name

    elif not is_valid_file(path):
        print(f"❌ Invalid file: '{path}'")
        print("👉 Must be a local file ending in .json, .yaml, or .yml")
        sys.exit(1)

    if not is_valid_openapi(path):
        print(f"❌ The file '{path}' is not a valid OpenAPI document.")
        sys.exit(1)

    try:
        result = analyze_api(path, output_dir=args.output_folder)

        if args.output_format in ["html", "both"]:
            print(f"✅ HTML report generated: {os.path.abspath(result['html_path'])}")

        if args.output_format in ["json", "both"]:
            json_path = os.path.join(args.output_folder, "rest_report.json")
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(result["json_report"], f, indent=2, ensure_ascii=False)
            print(f"✅ JSON report generated: {os.path.abspath(json_path)}")

    except Exception as e:
        print(f"❌ Error analyzing API: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()