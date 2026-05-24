"""
missing_si_downloader.py — Fill the SI coverage gap.

For each InForce SI (uksi, ssi, nisr, wsi) that is absent from legislation.db,
fetch /data.xml via downloader.py's existing logic and insert with stream='B'.

Queue ordering (so an interrupted run still captures the most regulation-relevant
items first):
  1. Items from missing_uksi_priority.csv  (top 100 most recently made uksi)
  2. All remaining missing uksi, sorted newest first
  3. All missing ssi, newest first
  4. All missing nisr, newest first
  5. All missing wsi, newest first

Resume-safe: skips anything already in legislation.db (downloader.already_downloaded
guard fires on every item).

Progress: prints every 500 completed items with ok/error counts and a running ETA.
Logs to download.log (shared with downloader.py).

Usage:  python missing_si_downloader.py [--dry-run]
"""
import argparse
import csv
import logging
import os
import re
import sqlite3
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta, timezone

import downloader  # reuse fetch/parse/insert logic

ROOT = os.path.dirname(os.path.abspath(__file__))
CSV_DIR = os.path.join(ROOT, 'InForce_results_47')
PRIORITY_CSV = os.path.join(ROOT, 'missing_uksi_priority.csv')

# Each entry: (csv_filename, leg_type_filter)
# nisro_nisr.csv contains BOTH nisr and nisro rows — we filter by type column to
# pick up only nisr; nisro is local statutory rules of which bulk has 0/1196 anyway
# and they fall outside the SI fill scope as requested by the user.
SI_SOURCES = [
    ('result_table_uksi.csv',       'uksi'),
    ('result_table_ssi.csv',        'ssi'),
    ('result_table_nisro_nisr.csv', 'nisr'),
    ('result_table_wsi.csv',        'wsi'),
]


def norm(url: str) -> str:
    if not url:
        return ''
    u = re.sub(r'^https?://(www\.)?legislation\.gov\.uk', '', url.strip())
    u = re.sub(r'^/id/', '/', u)
    return u.rstrip('/').lower()


def load_db_norms(conn) -> set:
    return {norm(u) for (u,) in conn.execute('SELECT item_url FROM legislation')}


def parse_int(v, default=0):
    try:
        return int(v) if v else default
    except (TypeError, ValueError):
        return default


def build_queue(conn):
    """Return ordered list of dicts: item_url (no /id/), title, year, number, leg_type, status."""
    db_norms = load_db_norms(conn)
    queue = []
    seen_urls = set()

    # 1. Priority list first (top-100 most recent missing uksi)
    if os.path.exists(PRIORITY_CSV):
        with open(PRIORITY_CSV, 'r', encoding='utf-8') as fh:
            for row in csv.DictReader(fh):
                raw_url = row['item'].strip()
                clean_url = raw_url.replace('/id/', '/')
                n = norm(clean_url)
                if n in db_norms or n in seen_urls:
                    continue
                seen_urls.add(n)
                queue.append({
                    'item_url': clean_url,
                    'title': row.get('title', ''),
                    'year': parse_int(row.get('year')),
                    'number': row.get('number', ''),
                    'leg_type': 'uksi',
                    'status': 'InForce',
                    'priority': True,
                })

    # 2-5. Per-type missing lists, newest first
    for csv_name, leg_type in SI_SOURCES:
        path = os.path.join(CSV_DIR, csv_name)
        if not os.path.exists(path):
            print(f'WARN: {csv_name} not found, skipping')
            continue
        missing = []
        with open(path, 'r', encoding='utf-8') as fh:
            for row in csv.DictReader(fh):
                if (row.get('status') or '').strip() != 'InForce':
                    continue
                if (row.get('type') or '').strip() != leg_type:
                    continue  # nisro_nisr.csv has both nisr and nisro; we want nisr only
                raw_url = row['item'].strip()
                clean_url = raw_url.replace('/id/', '/')
                n = norm(clean_url)
                if n in db_norms or n in seen_urls:
                    continue
                seen_urls.add(n)
                missing.append({
                    'item_url': clean_url,
                    'title': row.get('title', ''),
                    'year': parse_int(row.get('year')),
                    'number': row.get('number', ''),
                    'leg_type': leg_type,
                    'status': 'InForce',
                    'priority': False,
                })
        missing.sort(key=lambda r: (-r['year'], -parse_int(r['number'])))
        queue.extend(missing)
        print(f'  {leg_type}: {len(missing):,} missing queued')

    return queue


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dry-run', action='store_true',
                        help='Build queue and print estimate; do not download')
    parser.add_argument('--limit', type=int, default=0,
                        help='Cap total items processed (0 = no cap)')
    args = parser.parse_args()

    conn = sqlite3.connect(downloader.DB_PATH, check_same_thread=False)
    downloader.init_db(conn)

    print(f"Building queue (excluding {sum(1 for _ in conn.execute('SELECT 1 FROM legislation'))} already-present items)...")
    queue = build_queue(conn)
    if args.limit > 0:
        queue = queue[:args.limit]

    total = len(queue)
    by_type = {}
    for q in queue:
        by_type[q['leg_type']] = by_type.get(q['leg_type'], 0) + 1

    print()
    print('=' * 60)
    print(f'Queue size: {total:,} items to download')
    for t in ('uksi', 'ssi', 'nisr', 'wsi'):
        print(f'  {t}: {by_type.get(t, 0):,}')
    print()

    # Time estimate: with THREAD_COUNT=3 and BASE_PAUSE=0.5s/thread, theoretical
    # rate ~6 req/s. In practice 2-4 items/s after parsing + occasional 202/429.
    rate_low, rate_high = 2.0, 4.0
    eta_low = total / rate_high
    eta_high = total / rate_low
    print(f'Estimated runtime: {eta_low/3600:.1f}h - {eta_high/3600:.1f}h')
    print(f'  (assumes 2-4 items/sec sustained; THREAD_COUNT={downloader.THREAD_COUNT}, '
          f'BASE_PAUSE={downloader.BASE_PAUSE}s)')
    print('=' * 60)
    print()

    if args.dry_run:
        print('Dry run — exiting without downloading.')
        return

    logging.info(f'missing_si_downloader started: {total} items')

    success = 0
    errors = 0
    start = time.time()
    last_report_t = start

    with ThreadPoolExecutor(max_workers=downloader.THREAD_COUNT) as executor:
        futures = {
            executor.submit(
                downloader.download_item,
                q['item_url'], q['title'], q['year'], q['number'],
                q['leg_type'], q['status'], 'B', conn,
            ): q
            for q in queue
        }

        done = 0
        for future in as_completed(futures):
            done += 1
            try:
                ok = future.result()
            except Exception as e:
                q = futures[future]
                logging.error(f"Exception on {q['item_url']}: {e}")
                ok = False
            if ok:
                success += 1
            else:
                errors += 1

            if done % 500 == 0 or done == total:
                now = time.time()
                elapsed = now - start
                rate = done / elapsed if elapsed > 0 else 0
                rem_s = (total - done) / rate if rate > 0 else 0
                eta = datetime.now(timezone.utc) + timedelta(seconds=rem_s)
                interval_rate = 500 / (now - last_report_t) if now > last_report_t else 0
                last_report_t = now
                pct = 100 * done / total
                line = (f'  {done:>6,}/{total:,} ({pct:5.1f}%) | '
                        f'ok={success:,} err={errors:,} | '
                        f'rate={rate:.2f}/s ({interval_rate:.2f}/s last 500) | '
                        f'ETA {eta.strftime("%Y-%m-%d %H:%M UTC")}')
                print(line)
                sys.stdout.flush()
                logging.info(line.strip())

    elapsed_total = time.time() - start
    print()
    print('=' * 60)
    print(f'Done. ok={success:,} err={errors:,} of {total:,}')
    print(f'Elapsed: {elapsed_total/3600:.2f}h ({elapsed_total:.0f}s)')
    print('=' * 60)
    logging.info(f'missing_si_downloader complete: ok={success} err={errors} '
                 f'elapsed={elapsed_total:.0f}s')
    conn.close()


if __name__ == '__main__':
    main()
