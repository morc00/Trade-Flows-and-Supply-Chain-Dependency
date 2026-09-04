"""Download India's annual HS 8542 trade records from UN Comtrade.

The script uses the public preview API, which requires no API key. Queries are
split by year because the preview service accepts one period and one product per
request and returns at most 500 records.
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


def build_query_url(year: int) -> str:
    parameters = {
        "period": year,
        "reporterCode": REPORTER_CODE,
        "flowCode": "M,X",
        "cmdCode": COMMODITY_CODE,
        "partner2Code": 0,
        "customsCode": "C00",
        "motCode": 0,
        "maxRecords": MAX_RECORDS,
    }
    return f"{API_URL}?{urlencode(parameters)}"


def download_year(year: int) -> tuple[list[dict[str, Any]], str]:
    url = build_query_url(year)
    payload = fetch_json(url)
    records = payload.get("data", [])

    if payload.get("error"):
        raise RuntimeError(f"UN Comtrade returned an error for {year}: {payload['error']}")
    if not records:
        raise RuntimeError(f"No UN Comtrade records returned for {year}")
    if len(records) >= MAX_RECORDS:
        raise RuntimeError(
            f"The {year} query reached the {MAX_RECORDS}-record preview limit; "
            "narrow the query or use an authenticated API request."
        )
    return records, url


def acquire_trade_data(start_year: int, end_year: int, output_dir: Path) -> Path:
    if start_year > end_year:
        raise ValueError("start_year must not be greater than end_year")

    partners = partner_lookup()
    all_records: list[dict[str, Any]] = []
    query_log: list[dict[str, Any]] = []

    for index, year in enumerate(range(start_year, end_year + 1)):
        records, url = download_year(year)
        query_log.append({"year": year, "record_count": len(records), "url": url})

        for record in records:
            partner_code = int(record["partnerCode"])
            partner = partners.get(partner_code, {})
            all_records.append(
                {
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
                    "hs_code": COMMODITY_CODE,
                    "commodity": COMMODITY_NAME,
                    "classification": record.get("classificationCode", "HS"),
                    "trade_value_usd": record.get("primaryValue"),
                    "net_weight_kg": record.get("netWgt"),
                    "net_weight_estimated": record.get("isNetWgtEstimated"),
                    "comtrade_is_aggregate": record.get("isAggregate"),
                    "comtrade_is_reported": record.get("isReported"),
                }
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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--start-year", type=int, default=2019)
    parser.add_argument("--end-year", type=int, default=2025)
    parser.add_argument("--output-dir", type=Path, default=Path("data/raw"))
    return parser.parse_args()


if __name__ == "__main__":
    arguments = parse_args()
    acquire_trade_data(arguments.start_year, arguments.end_year, arguments.output_dir)
