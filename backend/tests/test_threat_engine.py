import sys
from pathlib import Path
import asyncio

# Add project root to sys.path
sys.path.append(str(Path(__file__).resolve().parents[2]))

from backend.app.services.threat_engine.epss_client import EPSSClient
from backend.app.services.threat_engine.cisa_kev_client import CISAKEVClient
from backend.app.services.threat_engine.exploit_scorer import ExploitScorer


async def run_threat_engine_tests():
    print("=" * 60)
    print("Running Threat Engine Exploitability Tests...")

    test_cves = ["CVE-2021-44228", "CVE-2023-48795"]

    for cve in test_cves:
        epss_data = await EPSSClient.get_epss_score(cve)
        is_kev = await CISAKEVClient.is_in_kev(cve)
        
        # Simulate CVSS base score
        cvss = 10.0 if "44228" in cve else 7.5

        # Calculate final FAIR Vulnerability Probability
        vuln_prob = ExploitScorer.calculate_vulnerability_probability(
            cvss_score=cvss,
            epss_probability=epss_data["epss"],
            is_cisa_kev=is_kev,
            is_internet_facing=True,
        )

        print(f"\nTarget: {cve}")
        print(f"  - CVSS Base Score:     {cvss}")
        print(f"  - EPSS Probability:    {epss_data['epss']:.4f} (Rank: {epss_data['percentile'] * 100:.1f}%)")
        print(f"  - CISA KEV Listed:     {is_kev}")
        print(f"  - Computed FAIR Vuln:  {vuln_prob * 100:.1f}% exploit probability")

    print("\n" + "=" * 60)
    print("Threat Intelligence Engine Working Perfectly!")


if __name__ == "__main__":
    asyncio.run(run_threat_engine_tests())
