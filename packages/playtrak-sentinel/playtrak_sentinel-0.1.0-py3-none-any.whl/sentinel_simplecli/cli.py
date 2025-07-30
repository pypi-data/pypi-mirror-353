import pyfiglet
import requests
import re
import sys
import json
import argparse
from datetime import datetime

def load_trakignore():
    try:
        with open(".trakignore", "r") as f:
            return set(line.strip() for line in f if line.strip())
    except FileNotFoundError:
        return set()

def parse_requirements(file_path):
    with open(file_path, "r") as f:
        lines = f.readlines()
    packages = []
    for line in lines:
        line = line.strip()
        if not line or line.startswith("#") or line.startswith("--"):
            continue
        match = re.match(r"^([a-zA-Z0-9_\-]+)==([a-zA-Z0-9\.\+\-]+)", line)
        if match:
            packages.append((match.group(1), match.group(2)))
    return packages

def parse_freeze():
    import subprocess
    output = subprocess.check_output(["pip", "freeze"]).decode()
    return parse_requirements_from_text(output)

def parse_requirements_from_text(text):
    lines = text.splitlines()
    packages = []
    for line in lines:
        line = line.strip()
        if not line or line.startswith("#") or line.startswith("--"):
            continue
        match = re.match(r"^([a-zA-Z0-9_\-]+)==([a-zA-Z0-9\.\+\-]+)", line)
        if match:
            packages.append((match.group(1), match.group(2)))
    return packages

def check_version_vulnerabilities(name, version):
    res = requests.post("https://api.osv.dev/v1/query", json={
        "version": version,
        "package": {
            "name": name,
            "ecosystem": "PyPI"
        }
    })
    res.raise_for_status()
    return res.json().get("vulns", [])

def generate_reports(vulnerable, args):
    if args.json:
        with open(args.json, "w") as jf:
            json.dump(vulnerable, jf, indent=2)

    if args.csv:
        with open(args.csv, "w") as cf:
            cf.write("package,version,vuln_id,summary,url\n")
            for name, version, vulns in vulnerable:
                for vuln in vulns:
                    summary = vuln.get("summary", "").replace(",", " ")
                    url = next((r.get("url") for r in vuln.get("references", []) if r.get("url")), "")
                    cf.write(f"{name},{version},{vuln['id']},{summary},{url}\n")

def cli():
    ascii_banner = pyfiglet.figlet_format("Sentinel")
    print(ascii_banner)
    print("🛡️  by PLAYTRAK Security Team\n")
    parser = argparse.ArgumentParser(description="Sentinel - OSV Vulnerability Scanner")
    parser.add_argument("-r", "--requirements", action="append", help="Path to requirements.txt file(s)")
    parser.add_argument("--json", help="Export report to JSON")
    parser.add_argument("--csv", help="Export report to CSV")
    args = parser.parse_args()

    if args.requirements:
        packages = []
        for file in args.requirements:
            packages.extend(parse_requirements(file))
    else:
        packages = parse_freeze()

    ignore_list = load_trakignore()
    vulnerable_packages = []

    for name, version in packages:
        vulns = check_version_vulnerabilities(name, version)
        filtered = [v for v in vulns if v["id"] not in ignore_list]
        if filtered:
            vulnerable_packages.append((name, version, filtered))

    generate_reports(vulnerable_packages, args)

    print("+==============================================================================+")
    print("Sentinel - Vulnerability Report")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Scanned {len(packages)} packages")
    print(f"Found {len(vulnerable_packages)} vulnerable package(s) (excluding ignored)")
    print("+==============================================================================+")

    if vulnerable_packages:
        print("\nDetailed Vulnerabilities:\n")
        for name, version, vulns in vulnerable_packages:
            print(f"• {name}=={version}")
            for vuln in vulns:
                vuln_id = vuln.get("id", "UNKNOWN")
                summary = vuln.get("summary", "No summary available.")
                url = next((r.get("url") for r in vuln.get("references", []) if r.get("url")), "No URL")
                print(f"   - [{vuln_id}] {summary}")
                print(f"     Link: {url}")
            print()
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    cli()
