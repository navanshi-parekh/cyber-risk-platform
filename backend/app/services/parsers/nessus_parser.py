"""
Tenable Nessus JSON / Export Scan Parser.
Normalizes Nessus host findings, CVE lists, CVSS v3/v2 scores, and port mapping.
"""

from typing import List, Dict, Any
import json


class NessusParser:
    """Parses exported Nessus JSON scan reports."""

    @staticmethod
    def parse_json_string(json_content: str) -> List[Dict[str, Any]]:
        """Parses a Nessus JSON export and outputs normalized vulnerability dictionaries."""
        try:
            data = json.loads(json_content)
        except Exception as e:
            raise ValueError(f"Invalid Nessus JSON payload: {str(e)}")

        results: List[Dict[str, Any]] = []

        # Handle both array of host findings and root 'vulnerabilities'/'hosts' structures
        hosts_data = data.get("hosts", []) if isinstance(data, dict) else []
        if not hosts_data and isinstance(data, dict) and "vulnerabilities" in data:
            hosts_data = [{"hostname": "unknown_target", "vulnerabilities": data["vulnerabilities"]}]
        elif isinstance(data, list):
            hosts_data = data

        for host_entry in hosts_data:
            host_ip = host_entry.get("hostname") or host_entry.get("ip") or host_entry.get("host-ip", "unknown")
            vulnerabilities = host_entry.get("vulnerabilities") or host_entry.get("findings", [])

            for vuln in vulnerabilities:
                # Severity mapping (0=Info, 1=Low, 2=Medium, 3=High, 4=Critical)
                severity_num = vuln.get("severity", 0)
                severity_map = {0: "Info", 1: "Low", 2: "Medium", 3: "High", 4: "Critical"}
                threat_level = severity_map.get(severity_num, "Medium")

                # Extract CVSS
                cvss_score = float(vuln.get("cvss3_base_score") or vuln.get("cvss_base_score") or vuln.get("cvss", 0.0))
                
                # Extract CVEs
                raw_cves = vuln.get("cve", [])
                if isinstance(raw_cves, str):
                    cve_list = [raw_cves] if raw_cves.startswith("CVE-") else []
                elif isinstance(raw_cves, list):
                    cve_list = [c for c in raw_cves if isinstance(c, str) and c.startswith("CVE-")]
                else:
                    cve_list = []

                if cvss_score > 0.0 or threat_level in ["Medium", "High", "Critical"]:
                    results.append({
                        "asset_ip": host_ip,
                        "port": str(vuln.get("port", "N/A")),
                        "vulnerability_name": vuln.get("plugin_name") or vuln.get("name", "Unknown Finding"),
                        "cvss_score": cvss_score,
                        "threat_level": threat_level,
                        "cve_list": cve_list,
                        "description": vuln.get("description", ""),
                        "solution": vuln.get("solution", ""),
                        "scanner_source": "Nessus",
                    })

        return results