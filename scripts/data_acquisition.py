"""Download India's annual HS 8542 trade records from UN Comtrade.

The script uses the public preview API, which requires no API key. Queries are
split by year because the preview service accepts one period and one product per
request and returns at most 500 records. It saves both heading-level trade flows
and six-digit import detail for diagnostic analysis.
"""

from __future__ import annotations

import argparse
import csv
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


API_URL = "https://comtradeapi.un.org/public/v1/preview/C/A/HS"
PARTNER_REFERENCE_URL = (
    "https://comtradeapi.un.org/files/v1/app/reference/partnerAreas.json"
)
REPORTER_CODE = 699
REPORTER_NAME = "India"
REPORTER_ISO3 = "IND"
COMMODITY_CODE = "8542"
COMMODITY_NAME = "Electronic integrated circuits"
HS6_PRODUCTS = {
    "854231": "Processors and controllers",
    "854232": "Memories",
    "854233": "Amplifiers",
    "854239": "Other electronic integrated circuits",
    "854290": "Parts of electronic integrated circuits",
}
FLOW_NAMES = {"M": "Import", "X": "Export"}
MAX_RECORDS = 500


def fetch_json(url: str, attempts: int = 3) -> dict[str, Any]:
    """Fetch JSON with a small retry policy for transient API errors."""
    request = Request(url, headers={"User-Agent": "DSC3132-trade-project/1.0"})
    for attempt in range(1, attempts + 1):
        try:
            with urlopen(request, timeout=60) as response:
                return json.load(response)
        except (HTTPError, URLError, TimeoutError, json.JSONDecodeError):
            if attempt == attempts:
                raise
            time.sleep(2**attempt)
    raise RuntimeError("UN Comtrade request failed")


def partner_lookup() -> dict[int, dict[str, Any]]:
    payload = fetch_json(PARTNER_REFERENCE_URL)
    entries = payload.get("results", payload)
    return {int(item["id"]): item for item in entries}


def build_query_url(
    year: int, cmd_code: str = COMMODITY_CODE, flow_codes: str = "M,X"
) -> str:
    parameters = {
        "period": year,
        "reporterCode": REPORTER_CODE,
        "flowCode": flow_codes,
        "cmdCode": cmd_code,
        "partner2Code": 0,
        "customsCode": "C00",
        "motCode": 0,
        "maxRecords": MAX_RECORDS,
    }
    return f"{API_URL}?{urlencode(parameters)}"


def download_query(
    year: int, cmd_code: str = COMMODITY_CODE, flow_codes: str = "M,X"
) -> tuple[list[dict[str, Any]], str]:
    url = build_query_url(year, cmd_code, flow_codes)
    payload = fetch_json(url)
    records = payload.get("data", [])

    if payload.get("error"):
        raise RuntimeError(
            f"UN Comtrade returned an error for {year}, HS {cmd_code}: "
            f"{payload['error']}"
        )
    if not records:
        raise RuntimeError(f"No UN Comtrade records returned for {year}, HS {cmd_code}")
    if len(records) >= MAX_RECORDS:
        raise RuntimeError(
            f"The {year} query reached the {MAX_RECORDS}-record preview limit; "
            "narrow the query or use an authenticated API request."
        )
    return records, url


def format_record(
    record: dict[str, Any],
    partners: dict[int, dict[str, Any]],
    cmd_code: str,
    commodity_name: str,
) -> dict[str, Any]:
    partner_code = int(record["partnerCode"])
    partner = partners.get(partner_code, {})
    return {
        "year": int(record["period"]),
        "reporter_code": REPORTER_CODE,
        "reporter_iso3": REPORTER_ISO3,
        "reporter_name": REPORTER_NAME,
        "flow_code": record["flowCode"],
        "flow_name": FLOW_NAMES.get(record["flowCode"], record["flowCode"]),
        "partner_code": partner_code,
        "partner_iso3": partner.get("PartnerCodeIsoAlpha3", ""),
        "partner_name": partner.get("text", f"Partner {partner_code}"),
        "partner_is_group": bool(partner.get("isGroup", False)),
        "hs_code": cmd_code,
        "commodity": commodity_name,
        "classification": record.get("classificationCode", "HS"),
        "trade_value_usd": record.get("primaryValue"),
        "net_weight_kg": record.get("netWgt"),
        "net_weight_estimated": record.get("isNetWgtEstimated"),
        "comtrade_is_aggregate": record.get("isAggregate"),
        "comtrade_is_reported": record.get("isReported"),
    }


def acquire_trade_data(
    start_year: int,
    end_year: int,
    output_dir: Path,
    partners: dict[int, dict[str, Any]] | None = None,
) -> Path:
    if start_year > end_year:
        raise ValueError("start_year must not be greater than end_year")

    partners = partners or partner_lookup()
    all_records: list[dict[str, Any]] = []
    query_log: list[dict[str, Any]] = []

    for index, year in enumerate(range(start_year, end_year + 1)):
        records, url = download_query(year)
        query_log.append({"year": year, "record_count": len(records), "url": url})

        all_records.extend(
            format_record(record, partners, COMMODITY_CODE, COMMODITY_NAME)
            for record in records
        )

        if index < end_year - start_year:
            time.sleep(1.1)

    all_records.sort(key=lambda row: (row["year"], row["flow_code"], row["partner_code"]))
    output_dir.mkdir(parents=True, exist_ok=True)
    csv_path = output_dir / f"india_hs8542_trade_{start_year}_{end_year}.csv"

    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(all_records[0]))
        writer.writeheader()
        writer.writerows(all_records)

    metadata = {
        "source": "United Nations Comtrade Database",
        "source_documentation": "https://uncomtrade.org/docs/un-comtrade-api/",
        "api_endpoint": API_URL,
        "partner_reference_endpoint": PARTNER_REFERENCE_URL,
        "retrieved_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "scope": {
            "reporter": REPORTER_NAME,
            "reporter_code": REPORTER_CODE,
            "commodity": COMMODITY_NAME,
            "hs_code": COMMODITY_CODE,
            "years": [start_year, end_year],
            "flows": list(FLOW_NAMES.values()),
        },
        "record_count": len(all_records),
        "queries": query_log,
        "notes": [
            "The public preview API requires no subscription key.",
            "Each request contains one year and one HS product and is checked against the 500-record limit.",
            "Partner code 0 is the World aggregate and is retained for national totals.",
        ],
    }
    metadata_path = output_dir / "un_comtrade_metadata.json"
    metadata_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")

    print(f"Downloaded {len(all_records):,} records from UN Comtrade")
    print(f"Trade data: {csv_path}")
    print(f"Metadata: {metadata_path}")
    return csv_path


def acquire_hs6_import_data(
    start_year: int,
    end_year: int,
    output_dir: Path,
    partners: dict[int, dict[str, Any]] | None = None,
) -> Path:
    """Download supplier detail for the five HS 8542 six-digit products."""
    partners = partners or partner_lookup()
    output_dir.mkdir(parents=True, exist_ok=True)
    records_out: list[dict[str, Any]] = []
    query_log: list[dict[str, Any]] = []
    queries = [
        (year, code, description)
        for year in range(start_year, end_year + 1)
        for code, description in HS6_PRODUCTS.items()
    ]

    for index, (year, code, description) in enumerate(queries):
        records, url = download_query(year, cmd_code=code, flow_codes="M")
        query_log.append(
            {"year": year, "hs_code": code, "record_count": len(records), "url": url}
        )
        records_out.extend(
            format_record(record, partners, code, description) for record in records
        )
        if index < len(queries) - 1:
            time.sleep(1.1)

    records_out.sort(key=lambda row: (row["year"], row["hs_code"], row["partner_code"]))
    csv_path = output_dir / f"india_hs8542_hs6_imports_{start_year}_{end_year}.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(records_out[0]))
        writer.writeheader()
        writer.writerows(records_out)

    metadata = {
        "source": "United Nations Comtrade Database",
        "source_documentation": "https://uncomtrade.org/docs/un-comtrade-api/",
        "retrieved_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "scope": {
            "reporter": REPORTER_NAME,
            "reporter_code": REPORTER_CODE,
            "parent_hs_code": COMMODITY_CODE,
            "hs6_products": HS6_PRODUCTS,
            "years": [start_year, end_year],
            "flow": "Import",
        },
        "record_count": len(records_out),
        "queries": query_log,
        "notes": [
            "The five six-digit codes exhaust HS heading 8542 in the classifications used.",
            "World totals are retained so the six-digit sum can be reconciled to HS 8542.",
            "Partner code 0 and group partners are excluded from supplier calculations.",
        ],
    }
    metadata_path = output_dir / "un_comtrade_hs6_metadata.json"
    metadata_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")

    print(f"Downloaded {len(records_out):,} HS6 import records from UN Comtrade")
    print(f"HS6 data: {csv_path}")
    print(f"HS6 metadata: {metadata_path}")
    return csv_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--start-year", type=int, default=2019)
    parser.add_argument("--end-year", type=int, default=2025)
    parser.add_argument("--output-dir", type=Path, default=Path("data/raw"))
    return parser.parse_args()


if __name__ == "__main__":
    arguments = parse_args()
    partner_reference = partner_lookup()
    acquire_trade_data(
        arguments.start_year,
        arguments.end_year,
        arguments.output_dir,
        partner_reference,
    )
    time.sleep(1.1)
    acquire_hs6_import_data(
        arguments.start_year,
        arguments.end_year,
        arguments.output_dir,
        partner_reference,
    )
