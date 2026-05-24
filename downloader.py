"""
downloader.py — Legislation.gov.uk XML downloader
Usage: python downloader.py --csv <path_to_csv> --stream <A|B|C>

CONFIRMED API FACTS (do not deviate):
  - Always /data.xml, never /data.json (404 for pre-1988)
  - Stream B/C: <item_url>/data.xml  (current consolidated)
  - Stream A:   <item_url>/enacted/data.xml  (original as-enacted)
  - No API key required
"""

import argparse
import csv
import hashlib
import logging
import re
import sqlite3
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta, timezone
from threading import Lock

import requests
from bs4 import BeautifulSoup

from word_list import REFERENCE_SCHEDULE_KEYWORDS

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
DB_PATH = "legislation.db"
THREAD_COUNT = 3
BASE_PAUSE = 0.5          # seconds between requests per thread
RATE_LIMIT_PAUSE = 30     # seconds to wait after 429
REDUCED_PAUSE = 1.0       # pause after rate-limit event (for 500 requests)
MAX_RETRIES = 3
MAX_202_RETRIES = 5       # retries for HTTP 202 (server still generating)
WAIT_202 = 30             # seconds to wait between 202 retries
REQUEST_TIMEOUT = 120     # seconds per HTTP request (15MB files need >30s)

LEGISLATURE_MAP = {
    'ukpga': 'Westminster', 'uksi': 'Westminster',
    'aep': 'Westminster', 'apgb': 'Westminster',
    'asp': 'Scottish Parliament', 'ssi': 'Scottish Parliament',
    'asc': 'Senedd', 'anaw': 'Senedd', 'mwa': 'Senedd', 'wsi': 'Senedd',
    'nia': 'NI Assembly', 'nisi': 'NI Assembly', 'nisr': 'NI Assembly',
    'nisro': 'NI Assembly', 'mnia': 'NI Assembly', 'apni': 'NI Assembly',
    'eur': 'EU Retained', 'eudn': 'EU Retained',
}

BILINGUAL_TYPES = {'asc', 'anaw', 'mwa', 'wsi'}

# RestrictExtent attribute uses shortcodes like "E+W+S+N.I."
RESTRICT_EXTENT_MAP = {
    frozenset(['E', 'W', 'S', 'N.I.']): 'United Kingdom',
    frozenset(['E', 'W', 'S']):         'Great Britain',
    frozenset(['E', 'W']):              'England and Wales',
    frozenset(['E']):                   'England',
    frozenset(['W']):                   'Wales',
    frozenset(['S']):                   'Scotland',
    frozenset(['N.I.']):                'Northern Ireland',
}

# ---------------------------------------------------------------------------
# Logging setup
# ---------------------------------------------------------------------------
logging.basicConfig(
    filename='download.log',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
)

rate_limit_logger = logging.getLogger('rate_limit')
rate_limit_handler = logging.FileHandler('rate_limit.log')
rate_limit_logger.addHandler(rate_limit_handler)
rate_limit_logger.setLevel(logging.WARNING)

error_logger = logging.getLogger('errors')
error_handler = logging.FileHandler('errors.log')
error_logger.addHandler(error_handler)
error_logger.setLevel(logging.ERROR)

# ---------------------------------------------------------------------------
# Database
# ---------------------------------------------------------------------------
db_lock = Lock()

def init_db(conn):
    conn.execute("""
        CREATE TABLE IF NOT EXISTS legislation (
            id                          INTEGER PRIMARY KEY AUTOINCREMENT,
            item_url                    TEXT UNIQUE,
            title                       TEXT,
            year                        INTEGER,
            number                      TEXT,
            legislation_type            TEXT,
            originating_legislature     TEXT,
            territorial_extent          TEXT,
            full_text                   TEXT,
            schedule_text_prescriptive  TEXT,
            schedule_text_reference     TEXT,
            date_enacted                TEXT,
            date_repealed               TEXT,
            status                      TEXT,
            stream                      TEXT,
            extracted_language          TEXT,
            download_timestamp          TEXT,
            amendment_insertion_text    TEXT
        )
    """)
    try:
        conn.execute("ALTER TABLE legislation ADD COLUMN amendment_insertion_text TEXT")
    except sqlite3.OperationalError:
        pass  # column already exists in existing databases
    conn.commit()


def already_downloaded(conn, item_url):
    row = conn.execute(
        "SELECT 1 FROM legislation WHERE item_url = ?", (item_url,)
    ).fetchone()
    return row is not None


def insert_item(conn, row):
    with db_lock:
        conn.execute("""
            INSERT OR IGNORE INTO legislation (
                item_url, title, year, number, legislation_type,
                originating_legislature, territorial_extent,
                full_text, schedule_text_prescriptive, schedule_text_reference,
                date_enacted, date_repealed, status, stream,
                extracted_language, download_timestamp, amendment_insertion_text
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, (
            row['item_url'], row['title'], row['year'], row['number'],
            row['legislation_type'], row['originating_legislature'],
            row['territorial_extent'], row['full_text'],
            row['schedule_text_prescriptive'], row['schedule_text_reference'],
            row['date_enacted'], row['date_repealed'], row['status'],
            row['stream'], row['extracted_language'], row['download_timestamp'],
            row.get('amendment_insertion_text', ''),
        ))
        conn.commit()

# ---------------------------------------------------------------------------
# Pause state (shared across threads)
# ---------------------------------------------------------------------------
pause_lock = Lock()
_pause_seconds = BASE_PAUSE
_reduced_pause_count = 0

def get_pause():
    global _pause_seconds, _reduced_pause_count
    with pause_lock:
        if _reduced_pause_count > 0:
            _reduced_pause_count -= 1
            return REDUCED_PAUSE
        return _pause_seconds

def trigger_rate_limit_backoff():
    global _pause_seconds, _reduced_pause_count
    with pause_lock:
        _reduced_pause_count = 500

# ---------------------------------------------------------------------------
# HTTP fetch with retry
# ---------------------------------------------------------------------------
session = requests.Session()
session.headers.update({'User-Agent': 'UKRegBurden-Research/1.0 (Academic regulatory burden measurement project by Jethro Elsden; contact: jelsden1000@gmail.com)'})

def fetch_xml(url):
    """Fetch URL with retry logic. Returns (text, status_code) or (None, final_status)."""
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            resp = session.get(url, timeout=REQUEST_TIMEOUT)
            if resp.status_code == 200:
                return resp.text, 200
            elif resp.status_code == 429:
                rate_limit_logger.warning(f"429 {url} attempt={attempt}")
                time.sleep(RATE_LIMIT_PAUSE)
                trigger_rate_limit_backoff()
            elif resp.status_code in (500, 503):
                logging.warning(f"HTTP {resp.status_code} {url} attempt={attempt}")
                time.sleep(10)
            else:
                return None, resp.status_code
        except requests.Timeout:
            logging.warning(f"Timeout {url} attempt={attempt}")
            time.sleep(5)
        except requests.RequestException as e:
            logging.warning(f"RequestException {url} attempt={attempt}: {e}")
            time.sleep(5)
    error_logger.error(f"FAILED after {MAX_RETRIES} retries: {url}")
    return None, None

# ---------------------------------------------------------------------------
# XML parsing helpers
# ---------------------------------------------------------------------------
NS = {
    'leg': 'http://www.legislation.gov.uk/namespaces/legislation',
    'dct': 'http://purl.org/dc/terms/',
    'dc':  'http://purl.org/dc/elements/1.1/',
    'xml': 'http://www.w3.org/XML/1998/namespace',
}

TYPE_EXTENT_FALLBACK = {
    'wsi': 'Wales', 'anaw': 'Wales', 'asc': 'Wales', 'mwa': 'Wales',
    'asp': 'Scotland', 'ssi': 'Scotland',
    'nia': 'Northern Ireland', 'nisr': 'Northern Ireland', 'nisro': 'Northern Ireland',
    'nisi': 'Northern Ireland', 'mnia': 'Northern Ireland', 'apni': 'Northern Ireland',
    'eur': 'United Kingdom', 'eudn': 'United Kingdom',
}


def extract_extent(soup, leg_type=None):
    """
    Extract territorial extent from RestrictExtent attribute on root element,
    or fall back to dct:extent tags, or infer from legislation type code.
    """
    root = soup.find('Legislation')
    if root and root.get('RestrictExtent'):
        raw = root['RestrictExtent']            # e.g. "E+W+S+N.I."
        parts = frozenset(p.strip() for p in raw.split('+') if p.strip())
        mapped = RESTRICT_EXTENT_MAP.get(parts)
        if mapped:
            return mapped
        # Unknown combination — describe it
        if len(parts) > 1:
            return 'Mixed'
        return raw  # return raw value rather than Unknown

    # Fall back: dct:extent tags
    extents = [t.get_text(strip=True) for t in soup.find_all('dct:extent')]
    if len(extents) == 1:
        raw = extents[0].lower()
        for key, val in {
            'united kingdom': 'United Kingdom',
            'great britain': 'Great Britain',
            'england, wales and scotland': 'Great Britain',
            'england and wales': 'England and Wales',
            'england': 'England', 'scotland': 'Scotland',
            'wales': 'Wales', 'northern ireland': 'Northern Ireland',
        }.items():
            if key in raw:
                return val
    elif len(extents) > 1:
        return 'Mixed'

    # Infer from type code for jurisdictions whose instruments never carry dct:extent
    if leg_type and leg_type in TYPE_EXTENT_FALLBACK:
        return TYPE_EXTENT_FALLBACK[leg_type]

    return 'Unknown'


def extract_english_text(soup, leg_type):
    """
    For bilingual documents (Welsh), extract English text only.
    Tries xml:lang='en' attribute; falls back to second copy heuristic.
    """
    if leg_type not in BILINGUAL_TYPES:
        return None  # not bilingual

    # Try explicit lang attribute
    en_tags = soup.find_all(attrs={'xml:lang': 'en'})
    if en_tags:
        return ' '.join(t.get_text(' ', strip=True) for t in en_tags)

    # Heuristic: split all text paragraphs, take even-indexed ones (English = second copy)
    paras = soup.find_all(['p', 'para', 'P'])
    if len(paras) > 4:
        even = paras[1::2]
        return ' '.join(p.get_text(' ', strip=True) for p in even)

    return soup.get_text(' ', strip=True)


def is_reference_schedule(text_lower):
    return any(kw in text_lower for kw in REFERENCE_SCHEDULE_KEYWORDS)


def strip_metadata(soup):
    """Remove metadata and explanatory note blocks so their content doesn't leak into extracted text."""
    for tag in soup.find_all(['ukm:Metadata', 'Metadata', 'ExplanatoryNotes', 'ExplanatoryNote']):
        tag.decompose()


# CLML Status values denoting provisions with no current legal force. Applied
# at the wrapping element (typically <P1group>) so descendants inherit; decompose()
# removes the subtree, so a single pass handles every nesting level.
_NO_FORCE_STATUSES = {'Prospective', 'Repealed', 'Dead', 'Prospective Repealed', 'Discarded'}


def strip_no_force_provisions(soup):
    """Remove provisions whose CLML Status indicates no current legal force.
    Prospective = not yet commenced; Repealed = withdrawn; Dead = never came into
    force; Prospective Repealed = repealed before commencement; Discarded = abandoned.
    None impose a current regulatory obligation, so they must not be counted."""
    for tag in soup.find_all(lambda t: t.get('Status') in _NO_FORCE_STATUSES):
        tag.decompose()


def extract_amendment_insertions(soup):
    """
    Extract text within amendment insertion markup.
    CLML uses <Addition> for inserted text; some versions also use <ins> or <InF>.
    Called after strip_metadata so metadata strings are excluded.
    """
    tags = soup.find_all(['Addition', 'ins', 'InF'])
    if not tags:
        return ''
    return '\n'.join(t.get_text(' ', strip=True) for t in tags if t.get_text(strip=True))


def extract_schedules(soup):
    """
    Strip metadata, split schedule text into prescriptive and reference buckets.
    Returns (main_text, prescriptive_schedule_text, reference_schedule_text).
    Real schedule tag names confirmed from API: Schedule, Schedules, ScheduleBody.
    """
    strip_metadata(soup)

    schedule_tags = soup.find_all(['Schedule', 'ScheduleBody'])

    prescriptive_parts = []
    reference_parts = []

    for sched in schedule_tags:
        text = sched.get_text(' ', strip=True)
        if is_reference_schedule(text.lower()):
            reference_parts.append(text)
        else:
            prescriptive_parts.append(text)

    # Remove schedule nodes so main body text is clean
    for sched in soup.find_all(['Schedule', 'ScheduleBody', 'Schedules']):
        sched.decompose()

    main_text = soup.get_text(' ', strip=True)
    return (
        main_text,
        ' '.join(prescriptive_parts),
        ' '.join(reference_parts),
    )


def parse_xml(xml_text, item_url, leg_type, stream):
    """Parse downloaded XML. Returns dict of fields."""
    soup = BeautifulSoup(xml_text, 'lxml-xml')

    # Territorial extent
    territorial_extent = extract_extent(soup, leg_type)

    # Legislature
    originating_legislature = LEGISLATURE_MAP.get(leg_type, 'Unknown')

    # Dates
    date_enacted = None
    date_enacted_tag = soup.find('dct:valid') or soup.find('dct:created')
    if date_enacted_tag:
        date_enacted = date_enacted_tag.text.strip()

    date_repealed = None

    # Strip metadata and no-force (Prospective/Repealed/etc.) provisions before
    # any text extraction so they contribute nothing to amendments, schedules, or main text.
    strip_metadata(soup)
    strip_no_force_provisions(soup)

    # Extract amendment insertion text before schedule decomposition alters the tree
    amendment_insertion_text = extract_amendment_insertions(soup)

    # Language handling
    if leg_type in BILINGUAL_TYPES:
        full_text = extract_english_text(soup, leg_type)
        extracted_language = 'en'
        main_text, prescriptive_sched, reference_sched = extract_schedules(
            BeautifulSoup(full_text or '', 'lxml-xml') if full_text else soup
        )
    else:
        main_text, prescriptive_sched, reference_sched = extract_schedules(soup)
        full_text = main_text
        extracted_language = 'en'

    return {
        'item_url': item_url,
        'legislation_type': leg_type,
        'originating_legislature': originating_legislature,
        'territorial_extent': territorial_extent,
        'full_text': full_text or main_text,
        'schedule_text_prescriptive': prescriptive_sched,
        'schedule_text_reference': reference_sched,
        'date_enacted': date_enacted,
        'date_repealed': date_repealed,
        'extracted_language': extracted_language,
        'amendment_insertion_text': amendment_insertion_text,
    }

# ---------------------------------------------------------------------------
# Per-item download task
# ---------------------------------------------------------------------------
def download_item(item_url, title, year, number, leg_type, status, stream, conn):
    """Download one legislation item. Returns True on success, False on failure."""
    # Resume: skip if already in DB
    with db_lock:
        if already_downloaded(conn, item_url):
            return True

    # Build XML URL
    base = item_url.replace('/id/', '/')
    if stream == 'A':
        xml_url = f"{base}/enacted/data.xml"
    else:
        xml_url = f"{base}/data.xml"

    time.sleep(get_pause())
    xml_text, status_code = None, None
    for attempt_202 in range(MAX_202_RETRIES + 1):
        xml_text, status_code = fetch_xml(xml_url)
        if xml_text is not None:
            break
        if status_code == 202:
            if attempt_202 < MAX_202_RETRIES:
                logging.info(
                    f"HTTP 202 {xml_url}, waiting {WAIT_202}s "
                    f"(attempt {attempt_202 + 1}/{MAX_202_RETRIES})"
                )
                time.sleep(WAIT_202)
            else:
                logging.warning(f"Giving up after {MAX_202_RETRIES} 202 retries: {xml_url}")
        else:
            break  # non-202 failure, don't retry

    if xml_text is None:
        return False

    try:
        parsed = parse_xml(xml_text, item_url, leg_type, stream)
    except Exception as e:
        error_logger.error(f"Parse error {item_url}: {e}")
        return False

    parsed.update({
        'title': title,
        'year': int(year) if str(year).isdigit() else None,
        'number': number,
        'status': status,
        'stream': stream,
        'download_timestamp': datetime.now(timezone.utc).isoformat(),
    })

    insert_item(conn, parsed)
    return True

# ---------------------------------------------------------------------------
# CSV loading
# ---------------------------------------------------------------------------

# Stream B only downloads items with these statuses; A and C take everything.
_STREAM_B_STATUSES = frozenset(['inforce', 'coreonly', 'limitedapplication'])


def load_csv(csv_path, stream='B'):
    """
    Load CSV and deduplicate by item_url.
    Stream B: exclude rows whose status is not InForce, CoreOnly, or LimitedApplication.
    Streams A/C: include all rows regardless of status.
    When duplicates exist, prefer the InForce row.
    Returns (rows, excluded_count).
    """
    items = {}
    excluded = 0
    with open(csv_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            url = row.get('item', '').strip()
            if not url:
                continue
            status_raw = row.get('status', '').strip()
            status_key = status_raw.lower().replace(' ', '')
            if stream == 'B' and status_key not in _STREAM_B_STATUSES:
                excluded += 1
                continue
            if url not in items:
                items[url] = row
            elif status_key == 'inforce':
                items[url] = row
    if excluded:
        logging.info(f"load_csv: excluded {excluded} non-qualifying rows for stream {stream}")
    return list(items.values()), excluded

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--csv', required=True, help='Path to InForce CSV')
    parser.add_argument('--stream', required=True, choices=['A', 'B', 'C'])
    args = parser.parse_args()

    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    init_db(conn)

    rows, skipped = load_csv(args.csv, stream=args.stream)
    total = len(rows)
    print(f"Loaded {total} qualifying items from {args.csv} "
          f"(stream {args.stream}; {skipped} excluded by status)")

    success = 0
    errors = 0
    start_time = time.time()

    with ThreadPoolExecutor(max_workers=THREAD_COUNT) as executor:
        futures = {
            executor.submit(
                download_item,
                r.get('item', '').strip().replace('/id/', '/'),
                r.get('title', ''),
                r.get('year', ''),
                r.get('number', ''),
                r.get('type', ''),
                r.get('status', ''),
                args.stream,
                conn,
            ): r
            for r in rows
        }

        done = 0
        for future in as_completed(futures):
            done += 1
            ok = future.result()
            if ok:
                success += 1
            else:
                errors += 1

            if done % 100 == 0 or done == total:
                elapsed = time.time() - start_time
                rate = done / elapsed if elapsed > 0 else 0
                remaining = (total - done) / rate if rate > 0 else 0
                eta = datetime.now(timezone.utc) + timedelta(seconds=remaining)
                pct = 100 * done / total
                print(
                    f"  {done}/{total} ({pct:.1f}%) | "
                    f"ok={success} skipped={skipped} errors={errors} | "
                    f"ETA {eta.strftime('%H:%M UTC')}"
                )
                logging.info(f"Progress {done}/{total} ok={success} skipped={skipped} errors={errors}")

    conn.close()
    print(f"\nDone. ok={success} skipped={skipped} errors={errors}")


if __name__ == '__main__':
    main()
