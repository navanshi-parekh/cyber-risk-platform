"""
Vulnerability Scan Ingestion & Telemetry Enrichment REST Endpoint.
Ingests OpenVAS XML and Tenable Nessus JSON scan reports, parses findings,
and enriches CVEs with live/cached EPSS and CISA KEV exploitability scores.
"""

from typing import List, Dict, Any, Optional
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status
from pydantic import BaseModel, Field

from backend.app.services.parsers.openvas_parser import OpenVASParser
from backend.app.services.parsers.nessus_parser import NessusParser
from backend.app.services.threat_engine.epss_client import EPSSClient
from backend.app.services.threat_engine.cisa_kev_client import CISAKEVClient
from backend.app.services.threat_engine.exploit_scorer import ExploitScorer

router = APIRouter()


# ---------------------------------------------------------------------------
# Pydantic Response Schemas
# ---------------------------------------------------------------------------

class EnrichedVulnerabilityRecord(BaseModel):
    asset_ip: str
    port: str
    vulnerability_name: str
    cvss_score: float
    threat_level: str
    cve_list: List[str]
    epss_probability: float
    epss_percentile: float
    is_cisa_kev: bool
    fair_vulnerability_probability: float
    description: str
    solution: str
    scanner_source: str


class IngestionSummary(BaseModel):
    filename: str
    detected_scanner: str
    total_findings_parsed: int
    critical_findings_count: int
    kev_weaponized_count: int
    mean_fair_vuln_prob: float
    findings: List[EnrichedVulnerabilityRecord]


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.post(
    "/upload-scan",
    response_model=IngestionSummary,
    status_code=status.HTTP_200_OK,
    summary="Upload & Parse Vulnerability Scan Report",
)
async def upload_and_process_scan(
    file: UploadFile = File(..., description="OpenVAS XML or Nessus JSON vulnerability report file"),
    scanner_type: Optional[str] = Form(
        default="auto",
        description="Explicit scanner type ('openvas', 'nessus', or 'auto')",
    ),
    is_internet_facing: Optional[bool] = Form(
        default=False,
        description="Whether the target asset subnet is exposed to the public internet",
    ),
):
    """
    Ingests an OpenVAS XML or Nessus JSON report, normalizes technical findings,
    enriches them with EPSS and CISA KEV threat feeds, and computes composite FAIR
    vulnerability likelihoods for downstream Monte Carlo loss quantification.
    """
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file must have a valid filename.",
        )

    # 1. Read raw stream
    try:
        raw_bytes = await file.read()
        text_content = raw_bytes.decode("utf-8", errors="ignore").strip()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to read upload payload stream: {str(e)}",
        )

    if not text_content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The uploaded scan report is empty.",
        )

    # 2. Scanner Format Detection & Parsing
    raw_findings: List[Dict[str, Any]] = []
    detected_type: str = "Unknown"
    norm_scanner = (scanner_type or "auto").lower()

    try:
        if (
            norm_scanner == "openvas"
            or file.filename.endswith(".xml")
            or "<report" in text_content[:500]
            or "<results>" in text_content[:1000]
        ):
            raw_findings = OpenVASParser.parse_xml_string(text_content)
            detected_type = "OpenVAS XML"
        elif (
            norm_scanner == "nessus"
            or file.filename.endswith((".json", ".nessus"))
            or text_content.startswith("[")
            or text_content.startswith("{")
        ):
            raw_findings = NessusParser.parse_json_string(text_content)
            detected_type = "Nessus JSON"
        else:
            # Fallback attempt
            try:
                raw_findings = OpenVASParser.parse_xml_string(text_content)
                detected_type = "OpenVAS XML (Auto-detected)"
            except Exception:
                raw_findings = NessusParser.parse_json_string(text_content)
                detected_type = "Nessus JSON (Auto-detected)"
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Report parsing failed: {str(e)}",
        )

    # 3. Threat Intelligence Enrichment & FAIR Vulnerability Calculation
    enriched_records: List[EnrichedVulnerabilityRecord] = []
    kev_count = 0
    critical_count = 0
    accumulated_vuln_prob = 0.0

    for item in raw_findings:
        cve_list = item.get("cve_list", [])
        primary_cve = cve_list[0] if cve_list else None

        # Fetch EPSS and CISA KEV status
        epss_prob = 0.05
        epss_perc = 0.50
        is_kev = False

        if primary_cve:
            epss_data = await EPSSClient.get_epss_score(primary_cve)
            epss_prob = epss_data.get("epss", 0.05)
            epss_perc = epss_data.get("percentile", 0.50)
            is_kev = await CISAKEVClient.is_in_kev(primary_cve)

        if is_kev:
            kev_count += 1

        cvss = float(item.get("cvss_score", 0.0))
        if cvss >= 9.0 or item.get("threat_level") == "Critical":
            critical_count += 1

        # Calculate dynamic FAIR Vulnerability probability (0.0 to 1.0)
        fair_vuln = ExploitScorer.calculate_vulnerability_probability(
            cvss_score=cvss,
            epss_probability=epss_prob,
            is_cisa_kev=is_kev,
            is_internet_facing=is_internet_facing or False,
        )
        accumulated_vuln_prob += fair_vuln

        enriched_records.append(
            EnrichedVulnerabilityRecord(
                asset_ip=item.get("asset_ip", "unknown"),
                port=str(item.get("port", "N/A")),
                vulnerability_name=item.get("vulnerability_name", "Unknown Vulnerability"),
                cvss_score=cvss,
                threat_level=item.get("threat_level", "Medium"),
                cve_list=cve_list,
                epss_probability=round(epss_prob, 4),
                epss_percentile=round(epss_perc, 4),
                is_cisa_kev=is_kev,
                fair_vulnerability_probability=round(fair_vuln, 4),
                description=item.get("description", ""),
                solution=item.get("solution", ""),
                scanner_source=item.get("scanner_source", detected_type),
            )
        )

    total = len(enriched_records)
    mean_vuln = round(accumulated_vuln_prob / total, 4) if total > 0 else 0.0

    return IngestionSummary(
        filename=file.filename,
        detected_scanner=detected_type,
        total_findings_parsed=total,
        critical_findings_count=critical_count,
        kev_weaponized_count=kev_count,
        mean_fair_vuln_prob=mean_vuln,
        findings=enriched_records,
    )