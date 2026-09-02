import csv
import sys
import os

"""
POS Inventory Catalog Sync
===========================
(Anonymized portfolio version of a script running in production for a real
retail business's point-of-sale migration and inventory workflow.)

Merges a physical inventory scan file (barcode, count) against the POS
system's full item catalog export, producing a ready-to-upload file with
every required column intact -- while explicitly separating matches,
unmatched barcodes, and duplicate barcodes instead of silently dropping
anything that doesn't match cleanly.
"""

CATALOG = "sample_data/catalog_export.csv"


def load_catalog(catalog_path=CATALOG):
    with open(catalog_path, newline='', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames
        rows = list(reader)
    by_barcode = {}
    for row in rows:
        bc = (row.get('barcode') or "").strip()
        if bc:
            by_barcode.setdefault(bc, []).append(row)
    return headers, by_barcode


def build(scan_path, catalog_path=CATALOG):
    headers, by_barcode = load_catalog(catalog_path)
    with open(scan_path, newline='', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        scans = list(reader)

    matched_rows = []
    unmatched = []
    duplicates = []

    for scan in scans:
        barcode = scan['barcode'].strip()
        count = scan['count']
        catalog_rows = by_barcode.get(barcode)

        if not catalog_rows:
            unmatched.append((barcode, count))
        elif len(catalog_rows) > 1:
            duplicates.append((barcode, count, [r['name'] for r in catalog_rows]))
        else:
            row = dict(catalog_rows[0])
            row['inventory quantity'] = count
            row['inventory status'] = f"{count} in stock"
            matched_rows.append(row)

    base = os.path.splitext(os.path.basename(scan_path))[0]
    out_path = f"POS_UPLOAD_{base}.csv"
    with open(out_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        for row in matched_rows:
            writer.writerow(row)

    print(f"Matched: {len(matched_rows)} -> {out_path}")
    if unmatched:
        print(f"Unmatched barcodes (not in catalog, needs review): {len(unmatched)}")
        for bc, count in unmatched:
            print(f"  {bc} (count={count})")
    if duplicates:
        print(f"Duplicate barcodes (ambiguous, needs review): {len(duplicates)}")
        for bc, count, names in duplicates:
            print(f"  {bc} (count={count}) matches: {names}")

    return matched_rows, unmatched, duplicates


if __name__ == "__main__":
    build(sys.argv[1] if len(sys.argv) > 1 else "sample_data/inventory_scan.csv")
