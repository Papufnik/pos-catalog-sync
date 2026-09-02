# POS Inventory Catalog Sync

Small production utility (anonymized) from the same retail business's point-of-sale migration and inventory management work. Matches physical inventory scan counts back to the POS system's full item catalog so a bulk inventory update can be uploaded without hand-editing every column the POS requires.

## The problem

The POS system's bulk-upload format requires every one of ~70 original columns to be present and correctly filled in, or the upload silently drops or corrupts rows. A physical inventory count only produces two columns per item: a barcode and a count. Manually merging those by hand across a catalog of thousands of SKUs is slow and error-prone.

## What this does

- Loads the full item catalog once and indexes it by barcode.
- For each scanned barcode, looks up the matching catalog row, and writes back a new inventory quantity and status onto a full copy of that row — preserving every other column the POS needs untouched.
- Explicitly separates three outcomes instead of assuming success: a clean match, an unmatched barcode (item not in the catalog at all), and a duplicate barcode (more than one catalog item shares it) — the last two get flagged for manual review rather than silently guessed at.

## My role

I directed this build after running into exactly this problem migrating the business off QuickBooks onto a new POS system with no vendor support. I specified the three-way match/unmatched/duplicate split (an earlier naive version just skipped anything it couldn't match cleanly, which meant real discrepancies went unnoticed), and verified its output against real inventory counts before every upload.

## Stack

Python, `csv` (stdlib).

*Business name and file paths have been genericized. Logic and structure are unchanged from what runs in production.*
