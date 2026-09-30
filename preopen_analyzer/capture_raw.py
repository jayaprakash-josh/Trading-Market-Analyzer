"""
NSE Pre-Open Market Analyzer — Phase 0 Data Capture

Run this script during the live pre-open session (9:00-9:08 AM IST)
to capture raw API responses and verify available fields.

Usage:
    python -m preopen_analyzer.capture_raw
"""
import json
import os
import time
import logging
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


def capture_preopen_data():
    """Capture raw NSE pre-open API responses every 30 seconds."""
    from jugaad_data.nse import NSELive

    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "raw_captures")
    os.makedirs(output_dir, exist_ok=True)

    today = datetime.now().strftime("%Y-%m-%d")
    capture_count = 0

    logger.info("=" * 60)
    logger.info("  PHASE 0: RAW DATA CAPTURE")
    logger.info(f"  Date: {today}")
    logger.info(f"  Output: {output_dir}")
    logger.info("=" * 60)

    while True:
        now = datetime.now()

        if not _is_within_capture_window(now):
            if now.hour == 9 and now.minute >= 8:
                logger.info("Pre-open window closed. Stopping capture.")
                break
            logger.info(f"Waiting for 09:00 AM... Current: {now.strftime('%H:%M:%S')}")
            time.sleep(10)
            continue

        capture_count += 1
        timestamp_str = now.strftime("%H%M%S")

        logger.info(f"--- Capture #{capture_count} at {now.strftime('%H:%M:%S')} ---")

        nse = NSELive()
        _capture_and_save(nse, "FO", output_dir, today, timestamp_str, capture_count)
        _capture_and_save(nse, "NIFTY", output_dir, today, timestamp_str, capture_count)

        logger.info(f"Sleeping 30 seconds...")
        time.sleep(30)

    _print_capture_summary(output_dir, today, capture_count)


def _is_within_capture_window(now: datetime) -> bool:
    """Check if current time is within the pre-open capture window."""
    return now.hour == 9 and 0 <= now.minute <= 7


def _capture_and_save(nse, category: str, output_dir: str, today: str, timestamp_str: str, count: int):
    """Fetch data from one category and save to file."""
    try:
        data = nse.pre_open_market(category)
        filename = f"{today}_{timestamp_str}_{category}_capture_{count:03d}.json"
        filepath = os.path.join(output_dir, filename)

        with open(filepath, "w") as f:
            json.dump(data, f, indent=2, default=str)

        record_count = len(data.get("data", []))
        logger.info(f"  [{category}] Saved {record_count} records -> {filename}")

        if record_count > 0:
            _print_field_analysis(data["data"][0], category)

    except Exception as e:
        logger.error(f"  [{category}] Error: {e}")


def _print_field_analysis(sample_record: dict, category: str):
    """Analyze and print the fields available in a sample record."""
    logger.info(f"  [{category}] --- FIELD ANALYSIS ---")

    metadata = sample_record.get("metadata", {})
    detail = sample_record.get("detail", {})

    logger.info(f"  [{category}] metadata keys: {list(metadata.keys())}")
    logger.info(f"  [{category}] detail keys: {list(detail.keys())}")

    # Check critical fields
    critical_fields = {
        "iep": metadata.get("iep"),
        "previousClose": metadata.get("previousClose"),
        "finalQuantity (IEQ)": metadata.get("finalQuantity"),
        "totalBuyQuantity": metadata.get("totalBuyQuantity"),
        "totalSellQuantity": metadata.get("totalSellQuantity"),
        "yearHigh": metadata.get("yearHigh"),
        "yearLow": metadata.get("yearLow"),
        "pChange": metadata.get("pChange"),
    }

    for field_name, value in critical_fields.items():
        status = "✓ PRESENT" if value is not None else "✗ MISSING"
        logger.info(f"  [{category}]   {field_name}: {status} (value={value})")

    # Check detail sub-structure for imbalance data
    pre_open_detail = detail.get("preOpen", detail.get("preopen", []))
    if pre_open_detail:
        logger.info(f"  [{category}]   detail.preOpen: {len(pre_open_detail)} rows")
        iep_row = next((r for r in pre_open_detail if r.get("iep")), None)
        if iep_row:
            logger.info(f"  [{category}]   IEP row keys: {list(iep_row.keys())}")
            logger.info(f"  [{category}]   IEP row: {iep_row}")
    else:
        logger.info(f"  [{category}]   detail.preOpen: EMPTY/MISSING")


def _print_capture_summary(output_dir: str, today: str, count: int):
    """Print summary after capture completes."""
    files = [f for f in os.listdir(output_dir) if f.startswith(today)]
    logger.info("")
    logger.info("=" * 60)
    logger.info("  CAPTURE COMPLETE")
    logger.info(f"  Total captures: {count}")
    logger.info(f"  Files saved: {len(files)}")
    logger.info(f"  Location: {output_dir}")
    logger.info("=" * 60)
    logger.info("")
    logger.info("Next step: Review the JSON files to verify field availability.")
    logger.info("Then proceed with Phase 1 (core engine build).")


if __name__ == "__main__":
    capture_preopen_data()
