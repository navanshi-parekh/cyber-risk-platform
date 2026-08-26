"""
OpenVAS / Greenbone Community Edition XML Report Parser.
Extracts target host IP/hostnames, identified CVEs, CVSS base scores,
threat levels, and open service ports using Python's standard xml library.
"""

from typing import List, Dict, Any
import xml.etree.ElementTree as ET


class OpenVASParser:
    """Parses standard OpenVAS XML scan reports using standard library xml.etree."""

    @staticmethod
    def parse_xml_string(xml_content: str) -> List[Dict[str, Any]]:
        """Parses an OpenVAS XML string and extracts normalized vulnerability records."""
        try:
            root = ET.fromstring(xml_content)
        except Exception as e:
            raise ValueError(f"Invalid OpenVAS XML payload: {str(e)}")

        results: List[Dict[str, Any]] = []

        for result in root.iter("result"):
            host_elem = result.find("host")
            host_ip = host_elem.text.strip() if host_elem is not None and host_elem.text else "unknown"

            port_elem = result.find("port")
            port = port_elem.text.strip() if port_elem is not None and port_elem.text else "N/A"

            nvt = result.find("nvt")
            if nvt is None:
                continue

            name_elem = nvt.find("name")
            name = name_elem.text.strip() if name_elem is not None and name_elem.text else "Unknown Vulnerability"

            severity_elem = result.find("severity")
            try:
                cvss_score = float(severity_elem.text) if severity_elem is not None and severity_elem.text else 0.0
            except ValueError:
                cvss_score = 0.0

            threat_elem = result.find("threat")
            threat_level = threat_elem.text.strip() if threat_elem is not None and threat_elem.text else "Log"

            # Extract CVEs
            cves: List[str] = []
            cve_elem = nvt.find("cve")
            if cve_elem is not None and cve_elem.text:
                raw_cves = cve_elem.text.strip()
                if raw_cves and raw_cves.upper() != "NOCVE":
                    cves = [c.strip() for c in raw_cves.split(",") if c.strip().startswith("CVE-")]

            desc_elem = result.find("description")
            description = desc_elem.text.strip() if desc_elem is not None and desc_elem.text else ""

            solution_elem = nvt.find("solution")
            solution = solution_elem.text.strip() if solution_elem is not None and solution_elem.text else ""

            if cvss_score > 0.0:
                results.append({
                    "asset_ip": host_ip,
                    "port": port,
                    "vulnerability_name": name,
                    "cvss_score": cvss_score,
                    "threat_level": threat_level,
                    "cve_list": cves,
                    "description": description,
                    "solution": solution,
                    "scanner_source": "OpenVAS",
                })

        return results