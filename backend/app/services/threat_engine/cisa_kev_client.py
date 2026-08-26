"""
CISA Known Exploited Vulnerabilities (KEV) Catalog Client.
Identifies active weaponization flags in wild cyberattacks.
"""

from typing import Set, Dict, Any
import httpx


class CISAKEVClient:
    API_URL = "https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json"

    # Pre-seeded offline known exploited set
    OFFLINE_KEV_SET: Set[str] = {
        "CVE-2021-44228",  # Log4Shell
        "CVE-2017-0144",   # EternalBlue
        "CVE-2023-38606",
        "CVE-2020-1472",   # Zerologon
        "CVE-2019-19781",  # Citrix ADC
        "CVE-2024-3094",   # XZ Backdoor
    }

    @classmethod
    async def is_in_kev(cls, cve_id: str) -> bool:
        """Checks if a CVE is flagged as an active threat in CISA KEV."""
        cve_clean = cve_id.strip().upper()

        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                resp = await client.get(cls.API_URL)
                if resp.status_code == 200:
                    catalog = resp.json()
                    vulnerabilities = catalog.get("vulnerabilities", [])
                    cisa_cves = {v.get("cveID") for v in vulnerabilities if "cveID" in v}
                    return cve_clean in cisa_cves
        except Exception:
            pass  # Fall back to offline catalog

        return cve_clean in cls.OFFLINE_KEV_SET