"""
bulk_loader.py — Load CLML XML files from National Archives bulk download into legislation.db
Usage: python bulk_loader.py --dir <path> --stream <A|B|C> [--db <path>]

Scans a directory tree for *.xml files in CLML format from the bulk download at
research.legislation.gov.uk. Derives item_url from the DocumentURI attribute on
the root <Legislation> element. Reuses all XML parsing logic from downloader.py.
Skips items already present in the database.
"""

import argparse
import logging
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

from bs4 import BeautifulSoup

from downloader import (
    DB_PATH,
    already_downloaded,
    db_lock,
    init_db,
    insert_item,
    parse_xml,
)

_log = logging.getLogger('bulk_loader')
_log.setLevel(logging.INFO)
_log_fh = logging.FileHandler('bulk_load.log')
_log_fh.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
_log.addHandler(_log_fh)

_err = logging.getLogger('bulk_loader.errors')
_err.setLevel(logging.ERROR)
_err_fh = logging.FileHandler('bulk_errors.log')
_err_fh.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
_err.addHandler(_err_fh)


def extract_bulk_metadata(xml_text):
    """
    Extract item_url, leg_type, title, year, number, status from CLML bulk XML.
    Raises ValueError if DocumentURI attribute is absent.
    """
    soup = BeautifulSoup(xml_text, 'lxml-xml')

    root = soup.find('Legislation')
    if root is None:
        raise ValueError("No <Legislation> root element")

    doc_uri = root.get('DocumentURI')
    if not doc_uri:
        raise ValueError("DocumentURI attribute missing")

    # leg_type is the first path segment after the domain
    # e.g. http://www.legislation.gov.uk/ukpga/Geo3/41/52 → ukpga
    path_after_domain = doc_uri.split('legislation.gov.uk', 1)[-1]  # → /ukpga/Geo3/41/52
    uri_parts = [p for p in path_after_domain.split('/') if p]
    leg_type = uri_parts[0].lower() if uri_parts else 'unknown'

    title_tag = soup.find('dc:title')
    title = title_tag.get_text(strip=True) if title_tag else ''
    if not title:
        t2 = soup.find('Title')
        title = t2.get_text(strip=True) if t2 else ''

    year = None
    year_tag = soup.find('ukm:Year')
    if year_tag and year_tag.get('Value'):
        try:
            year = int(year_tag['Value'])
        except ValueError:
            pass

    number = ''
    number_tag = soup.find('ukm:Number')
    if number_tag and number_tag.get('Value'):
        number = number_tag['Value']

    status = ''
    status_tag = soup.find('ukm:DocumentStatus')
    if status_tag and status_tag.get('Value'):
        status = status_tag['Value']

    return {
        'item_url': doc_uri,
        'leg_type': leg_type,
        'title': title,
        'year': year,
        'number': number,
        'status': status,
    }


def load_directory(dir_path, stream, conn, progress_every=100):
    """
    Walk dir_path recursively, loading all *.xml files into conn.
    Returns (loaded, skipped, errors).
    """
    xml_files = sorted(Path(dir_path).rglob('*.xml'))
    total = len(xml_files)
    if not total:
        print(f"No .xml files found under {dir_path}")
        return 0, 0, 0

    print(f"Found {total} XML files — scanning for CLML legislation...")
    loaded = skipped = errors = 0

    for i, xml_path in enumerate(xml_files, 1):
        try:
            xml_text = xml_path.read_text(encoding='utf-8')
        except Exception as e:
            _err.error(f"Read error {xml_path}: {e}")
            errors += 1
            _maybe_progress(i, total, loaded, skipped, errors, progress_every)
            continue

        try:
            meta = extract_bulk_metadata(xml_text)
        except ValueError as e:
            _err.error(f"Metadata error {xml_path}: {e}")
            errors += 1
            _maybe_progress(i, total, loaded, skipped, errors, progress_every)
            continue

        item_url = meta['item_url']

        if already_downloaded(conn, item_url):
            skipped += 1
            _maybe_progress(i, total, loaded, skipped, errors, progress_every)
            continue

        try:
            parsed = parse_xml(xml_text, item_url, meta['leg_type'], stream)
        except Exception as e:
            _err.error(f"Parse error {item_url}: {e}")
            errors += 1
            _maybe_progress(i, total, loaded, skipped, errors, progress_every)
            continue

        parsed.update({
            'title': meta['title'],
            'year': meta['year'],
            'number': meta['number'],
            'status': meta['status'],
            'stream': stream,
            'download_timestamp': datetime.now(timezone.utc).isoformat(),
        })

        try:
            insert_item(conn, parsed)
            loaded += 1
            _log.info(f"Loaded {item_url}")
        except Exception as e:
            _err.error(f"Insert error {item_url}: {e}")
            errors += 1

        _maybe_progress(i, total, loaded, skipped, errors, progress_every)

    return loaded, skipped, errors


def _maybe_progress(done, total, loaded, skipped, errors, every=100):
    if done % every == 0 or done == total:
        print(f"  {done}/{total} ({100*done/total:.1f}%) | "
              f"loaded={loaded} skipped={skipped} errors={errors}", flush=True)


def main():
    parser = argparse.ArgumentParser(
        description='Load CLML bulk download XML files into legislation.db'
    )
    parser.add_argument('--dir', required=True,
                        help='Directory containing XML files (searched recursively)')
    parser.add_argument('--stream', required=True, choices=['A', 'B', 'C'],
                        help='Stream: A=enacted, B=in-force, C=historical')
    parser.add_argument('--db', default=DB_PATH,
                        help=f'Database path (default: {DB_PATH})')
    parser.add_argument('--progress', type=int, default=100,
                        help='Print progress line every N files (default: 100)')
    args = parser.parse_args()

    if not Path(args.dir).is_dir():
        print(f"Error: {args.dir!r} is not a directory", file=sys.stderr)
        sys.exit(1)

    conn = sqlite3.connect(args.db, check_same_thread=False)
    init_db(conn)

    print(f"Stream {args.stream} | source: {args.dir} | db: {args.db}")
    loaded, skipped, errors = load_directory(args.dir, args.stream, conn, args.progress)
    conn.close()

    print(f"\nDone. loaded={loaded} skipped={skipped} errors={errors}")
    if errors:
        print("Check bulk_errors.log for details.")
    sys.exit(1 if errors else 0)


if __name__ == '__main__':
    main()
