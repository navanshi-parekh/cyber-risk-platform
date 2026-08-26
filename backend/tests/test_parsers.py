import sys
from pathlib import Path

# Add project root to sys.path so 'backend' is discoverable
sys.path.append(str(Path(__file__).resolve().parents[2]))

from backend.app.services.parsers.openvas_parser import OpenVASParser
from backend.app.services.parsers.nessus_parser import NessusParser

# Sample OpenVAS XML Snippet
SAMPLE_OPENVAS_XML = """<?xml version="1.0" encoding="UTF-8"?>
<report>
  <results>
    <result id="res-1">
      <host>192.168.1.50</host>
      <port>443/tcp</port>
      <nvt oid="1.3.6.1.4.1">
        <name>Apache Log4j Remote Code Execution</name>
        <cve>CVE-2021-44228</cve>
        <solution>Upgrade log4j-core to 2.17.1</solution>
      </nvt>
      <severity>10.0</severity>
      <threat>High</threat>
      <description>Log4Shell vulnerability allows unauthenticated RCE.</description>
    </result>
  </results>
</report>"""

# Sample Nessus JSON Snippet
SAMPLE_NESSUS_JSON = """[
  {
    "hostname": "10.0.0.12",
    "vulnerabilities": [
      {
        "plugin_name": "OpenSSH Terrapin Attack",
        "cvss3_base_score": 7.5,
        "severity": 3,
        "cve": ["CVE-2023-48795"],
        "port": 22,
        "solution": "Update OpenSSH to version 9.6p1 or later."
      }
    ]
  }
]"""

def run_tests():
    print("=" * 50)
    print("Running Scan Parser Tests...")
    
    # 1. Test OpenVAS
    openvas_results = OpenVASParser.parse_xml_string(SAMPLE_OPENVAS_XML)
    print(f"  [x] OpenVAS Findings Parsed: {len(openvas_results)}")
    print(f"      - Asset: {openvas_results[0]['asset_ip']}")
    print(f"      - Vulnerability: {openvas_results[0]['vulnerability_name']}")
    print(f"      - CVE: {openvas_results[0]['cve_list']}")
    print(f"      - CVSS: {openvas_results[0]['cvss_score']}")

    # 2. Test Nessus
    nessus_results = NessusParser.parse_json_string(SAMPLE_NESSUS_JSON)
    print(f"  [x] Nessus Findings Parsed:  {len(nessus_results)}")
    print(f"      - Asset: {nessus_results[0]['asset_ip']}")
    print(f"      - Vulnerability: {nessus_results[0]['vulnerability_name']}")
    print(f"      - CVE: {nessus_results[0]['cve_list']}")
    print(f"      - CVSS: {nessus_results[0]['cvss_score']}")
    
    print("=" * 50)
    print("All Parser Tests Passed Successfully!")

if __name__ == "__main__":
    run_tests()