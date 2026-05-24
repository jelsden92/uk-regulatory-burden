"""
test_run.py — Test run on 20 UK Public General Acts from 2015.
Exercises full downloader + analyser pipeline on a small sample.
Should complete in under 2 minutes.
"""

import argparse
import csv
import hashlib
import sqlite3
import time
from io import StringIO

import requests
from bs4 import BeautifulSoup

import analyser
import downloader
from word_list import REFERENCE_SCHEDULE_KEYWORDS

TEST_DB = "test_run.db"
CSV_PATH = "InForce_results_47/result_table_aep_apgb_ukpga.csv"
STREAM = "B"
TARGET_YEAR = 2015
SAMPLE_SIZE = 20


def _extract_title(xml_text):
    """Extract dc:title from raw XML, used when title is not in the row dict."""
    try:
        soup = BeautifulSoup(xml_text, 'lxml-xml')
        tag = soup.find('dc:title')
        return tag.get_text(strip=True) if tag else ''
    except Exception:
        return ''


def build_rows_from_paths(paths):
    """
    Convert URL path strings like 'ukpga/1974/37' into row dicts compatible
    with download_one.  Title is left empty so download_one fills it from XML.
    """
    rows = []
    for path in paths:
        path = path.strip().strip('/')
        parts = path.split('/')
        if len(parts) < 3:
            print(f"  WARNING: skipping malformed path '{path}' (expected type/year/number)")
            continue
        leg_type, year, number = parts[0], parts[1], '/'.join(parts[2:])
        rows.append({
            'item': f"https://www.legislation.gov.uk/id/{leg_type}/{year}/{number}",
            'type': leg_type,
            'year': year,
            'number': number,
            'title': '',
            'status': 'InForce',
        })
    return rows


# ---------------------------------------------------------------------------
# Setup — fresh test DB
# ---------------------------------------------------------------------------
def init_test_db(conn):
    downloader.init_db(conn)
    analyser.init_db(conn)


# ---------------------------------------------------------------------------
# Load 20 Acts from 2015
# ---------------------------------------------------------------------------
def load_sample():
    items = []
    seen = set()
    with open(CSV_PATH, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            url = row.get('item', '').strip()
            year = str(row.get('year', '')).strip()
            leg_type = row.get('type', '').strip()
            if url in seen:
                continue
            if year == str(TARGET_YEAR) and leg_type == 'ukpga':
                seen.add(url)
                items.append(row)
            if len(items) >= SAMPLE_SIZE:
                break
    return items


# ---------------------------------------------------------------------------
# Download one item (single-threaded, no concurrency for test)
# ---------------------------------------------------------------------------
def download_one(row, conn, stream=STREAM):
    item_url = row.get('item', '').strip()
    base = item_url.replace('/id/', '/')
    xml_url = f"{base}/data.xml"

    xml_text = None
    for attempt in range(downloader.MAX_202_RETRIES + 1):
        try:
            resp = requests.get(xml_url, timeout=downloader.REQUEST_TIMEOUT,
                                headers={'User-Agent': 'UKRegBurden-Research/1.0'})
            if resp.status_code == 200:
                xml_text = resp.text
                break
            elif resp.status_code == 202:
                if attempt < downloader.MAX_202_RETRIES:
                    print(f"  202 {row.get('title','?')} — waiting {downloader.WAIT_202}s "
                          f"(attempt {attempt + 1}/{downloader.MAX_202_RETRIES})")
                    time.sleep(downloader.WAIT_202)
                else:
                    print(f"  SKIP {row.get('title','?')} — HTTP 202 after {downloader.MAX_202_RETRIES} retries")
                    return False
            else:
                print(f"  SKIP {row.get('title','?')} — HTTP {resp.status_code}")
                return False
        except Exception as e:
            print(f"  SKIP {row.get('title','?')} — {e}")
            return False
    if xml_text is None:
        return False

    try:
        parsed = downloader.parse_xml(xml_text, item_url, row.get('type', ''), stream)
    except Exception as e:
        print(f"  PARSE ERROR {item_url}: {e}")
        return False

    parsed.update({
        'title': row.get('title') or _extract_title(xml_text) or item_url,
        'year': int(row['year']) if str(row.get('year', '')).isdigit() else None,
        'number': row.get('number', ''),
        'status': row.get('status', ''),
        'stream': stream,
        'download_timestamp': time.strftime('%Y-%m-%dT%H:%M:%S'),
    })
    downloader.insert_item(conn, parsed)
    return True


# ---------------------------------------------------------------------------
# Report helpers
# ---------------------------------------------------------------------------
def print_divider():
    print('-' * 70)


def show_sentences(conn, leg_id, classification, label, n=3):
    rows = conn.execute("""
        SELECT sentence_text, matched_word, is_in_schedule, subject_source
        FROM sentences
        WHERE legislation_id = ? AND classification = ?
        LIMIT ?
    """, (leg_id, classification, n)).fetchall()
    if rows:
        print(f"  {label}:")
        for r in rows:
            sched = ' [SCHEDULE]' if r['is_in_schedule'] else ''
            print(f"    [{r['matched_word']}]{sched} ({r['subject_source']})")
            print(f"    \"{r['sentence_text'][:120]}...\"")
    else:
        print(f"  {label}: none found")


# ---------------------------------------------------------------------------
# Main test
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description='Test run for UK legislation analyser pipeline.'
    )
    parser.add_argument(
        '--acts',
        metavar='PATH[,PATH...]',
        help='Comma-separated URL paths to test, e.g. ukpga/1974/37,ukpga/1996/18. '
             'If omitted, loads the default sample of %(default)s ukpga Acts from %(const)s.',
        default=None,
    )
    args = parser.parse_args()

    if args.acts:
        paths = [p.strip() for p in args.acts.split(',') if p.strip()]
        sample = build_rows_from_paths(paths)
        print(f"=== TEST RUN: {len(sample)} specified Acts ===\n")
    else:
        sample = load_sample()
        print(f"=== TEST RUN: {SAMPLE_SIZE} UK Public General Acts from {TARGET_YEAR} ===\n")
        if len(sample) < SAMPLE_SIZE:
            print(f"WARNING: only found {len(sample)} ukpga Acts from {TARGET_YEAR}.")

    conn = sqlite3.connect(TEST_DB)
    conn.row_factory = sqlite3.Row
    init_test_db(conn)

    # Patch analyser and downloader to use test DB
    analyser.DB_PATH = TEST_DB
    downloader.DB_PATH = TEST_DB

    print(f"Loaded {len(sample)} Acts.\n")

    # 2. Download
    print("--- Downloading ---")
    downloaded = 0
    for row in sample:
        title = row.get('title', '?')[:60]
        ok = download_one(row, conn)
        if ok:
            downloaded += 1
            print(f"  OK  {title}")
        time.sleep(0.5)

    print(f"\nDownloaded {downloaded}/{len(sample)} items.\n")

    # 3. Verify download quality
    print("--- Download Verification ---")
    leg_rows = conn.execute(
        "SELECT id, title, territorial_extent, originating_legislature, "
        "schedule_text_prescriptive FROM legislation WHERE stream = ?",
        (STREAM,)
    ).fetchall()

    extents_found = set()
    schedules_found = 0
    for r in leg_rows:
        extents_found.add(r['territorial_extent'])
        if r['schedule_text_prescriptive']:
            schedules_found += 1

    print(f"  territorial_extent values found: {extents_found}")
    print(f"  Items with schedule content detected: {schedules_found}/{len(leg_rows)}")
    print()

    # 4. Run analyser on downloaded items
    print("--- Running Analyser ---")
    for leg_row in conn.execute("SELECT * FROM legislation WHERE stream = ?", (STREAM,)).fetchall():
        try:
            analyser.analyse_item(conn, dict(leg_row), STREAM)
        except Exception as e:
            print(f"  ANALYSER ERROR {leg_row['title']}: {e}")

    # 5. Per-Act report
    print("\n--- Per-Act Results ---")
    results = conn.execute("""
        SELECT r.*, l.territorial_extent, l.originating_legislature
        FROM results r
        JOIN legislation l ON r.legislation_id = l.id
        WHERE r.stream = ?
        ORDER BY r.private_actor_count_excl_schedules DESC
    """, (STREAM,)).fetchall()

    dedup_total = 0
    inheritance_total = 0

    for r in results:
        print_divider()
        print(f"  {r['title']} ({r['year']})")
        print(f"  Legislature: {r['originating_legislature']}  |  "
              f"Extent: {r['territorial_extent']}")
        print(f"  Words: main={r['main_body_words']} "
              f"+ sched={r['prescriptive_schedule_words']} "
              f"(ref excl={r['reference_schedule_words_excluded']})")
        print(f"  Prescriptive sentences (total): {r['total_prescriptive_sentences']}")
        print(f"  Private actor: excl schedules={r['private_actor_count_excl_schedules']} "
              f"| incl schedules={r['private_actor_count_incl_schedules']}")
        print(f"  Public body: {r['public_body_count']}  "
              f"Ambiguous: {r['ambiguous_count']}  "
              f"Conditional burden: {r['conditional_burden_count']}")
        ib = r['implied_burden_count'] if 'implied_burden_count' in r.keys() else 0
        iba = r['implied_burden_active_count'] if 'implied_burden_active_count' in r.keys() else 0
        if ib or iba:
            print(f"  Implied burden: {ib}  (active compliance sub-type: {iba})")
        hi = r['high_confidence_count'] if 'high_confidence_count' in r.keys() else 0
        md = r['medium_confidence_count'] if 'medium_confidence_count' in r.keys() else 0
        lo = r['low_confidence_count'] if 'low_confidence_count' in r.keys() else 0
        if hi or md or lo:
            print(f"  Sentence confidence: high={hi}  medium={md}  low={lo}")
        print(f"  Density (excl): {r['regulatory_density_excl_schedules']:.2f}/1000 words  "
              f"| (incl): {r['regulatory_density_incl_schedules']:.2f}/1000 words")
        print(f"  OCR corrections: {r['ocr_correction_count']}  "
              f"Lower confidence: {bool(r['lower_confidence'])}")
        print(f"  Section subject inheritance triggered: "
              f"{r['section_subject_inheritance_count']} times")

        inheritance_total += r['section_subject_inheritance_count']

        # Deduplication check
        all_sents = conn.execute(
            "SELECT COUNT(*) FROM sentences WHERE legislation_id = ?",
            (r['legislation_id'],)
        ).fetchone()[0]
        dedup_total += (r['total_prescriptive_sentences'] - all_sents) \
            if r['total_prescriptive_sentences'] > all_sents else 0

        leg_id = r['legislation_id']
        show_sentences(conn, leg_id, 'private_actor', '3 private_actor obligations', 3)
        show_sentences(conn, leg_id, 'public_body', '3 public_body exclusions', 3)
        show_sentences(conn, leg_id, 'implied_burden', 'implied_burden sentences', 5)
        show_sentences(conn, leg_id, 'implied_burden_active', 'implied_burden_active sentences', 5)

    # 6. Summary checks
    print_divider()
    print("\n--- Summary Checks ---")
    print(f"  Territorial extent values seen: {extents_found}")
    print(f"  Section subject inheritance triggered: {inheritance_total} total times")
    print(f"  Sentence deduplication occurred: {dedup_total} duplicates removed")

    rate_limit_lines = 0
    try:
        with open('rate_limit.log') as f:
            rate_limit_lines = sum(1 for _ in f)
    except FileNotFoundError:
        pass
    print(f"  rate_limit.log entries: {rate_limit_lines} (429 errors during test)")

    conn.close()
    print("\n=== TEST COMPLETE ===")
    print("Next: review the per-Act counts above against your regulatory knowledge.")
    print("If satisfied: close Claude Code and run Local Run 1 (Stream B) from PowerShell.")


if __name__ == '__main__':
    main()
