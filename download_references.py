"""
Download PDFs for all references in references.bib.

Pipeline per reference:
  1. Search Crossref by title to obtain DOI
  2. Query Unpaywall (free, legal OA) for a PDF link
  3. Fall back to Semantic Scholar open-access PDF
  4. Download to reference_pdfs/<BibKey>.pdf

Usage:
    python download_references.py

Requires: bibtexparser, requests
Supply your email for Unpaywall (polite-pool) via UNPAYWALL_EMAIL env var
or it defaults to the one below.
"""

import os
import re
import time
import requests
import bibtexparser

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
BIB_FILE = os.path.join(os.path.dirname(__file__), "references.bib")
OUT_DIR = os.path.join(os.path.dirname(__file__), "reference_pdfs")
EMAIL = os.environ.get("UNPAYWALL_EMAIL", "oisin.ofriel@ucdconnect.ie")
HEADERS = {"User-Agent": f"ThesisRefDownloader/1.0 (mailto:{EMAIL})"}
TIMEOUT = 30

os.makedirs(OUT_DIR, exist_ok=True)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def clean_title(title: str) -> str:
    """Strip LaTeX braces and commands from a title."""
    title = re.sub(r"[{}]", "", title)
    title = re.sub(r"\\[a-zA-Z]+", "", title)
    title = re.sub(r"\s+", " ", title).strip()
    return title


def search_crossref_doi(title: str) -> str | None:
    """Search Crossref for a DOI by title. Returns DOI string or None."""
    url = "https://api.crossref.org/works"
    params = {"query.title": title, "rows": 3, "select": "DOI,title"}
    try:
        r = requests.get(url, params=params, headers=HEADERS, timeout=TIMEOUT)
        r.raise_for_status()
        items = r.json().get("message", {}).get("items", [])
        # Pick the best title match
        title_lower = title.lower()
        for item in items:
            for t in item.get("title", []):
                if t.lower().strip() == title_lower:
                    return item["DOI"]
        # Fallback: return first result if reasonably close
        if items:
            return items[0]["DOI"]
    except Exception:
        pass
    return None


def unpaywall_pdf_url(doi: str) -> str | None:
    """Query Unpaywall for an open-access PDF URL."""
    url = f"https://api.unpaywall.org/v2/{doi}"
    params = {"email": EMAIL}
    try:
        r = requests.get(url, params=params, headers=HEADERS, timeout=TIMEOUT)
        r.raise_for_status()
        data = r.json()
        # Best OA location
        best = data.get("best_oa_location")
        if best:
            pdf = best.get("url_for_pdf") or best.get("url")
            if pdf:
                return pdf
        # Try all locations
        for loc in data.get("oa_locations", []):
            pdf = loc.get("url_for_pdf") or loc.get("url")
            if pdf:
                return pdf
    except Exception:
        pass
    return None


def semantic_scholar_pdf_url(title: str) -> str | None:
    """Search Semantic Scholar for an open-access PDF."""
    url = "https://api.semanticscholar.org/graph/v1/paper/search"
    params = {"query": title, "limit": 3, "fields": "title,isOpenAccess,openAccessPdf"}
    try:
        r = requests.get(url, params=params, headers=HEADERS, timeout=TIMEOUT)
        r.raise_for_status()
        papers = r.json().get("data", [])
        title_lower = title.lower()
        for p in papers:
            if p.get("isOpenAccess") and p.get("openAccessPdf"):
                pdf_url = p["openAccessPdf"].get("url")
                if pdf_url:
                    return pdf_url
    except Exception:
        pass
    return None


def download_pdf(url: str, dest: str) -> bool:
    """Download a PDF from url to dest. Returns True on success."""
    try:
        r = requests.get(url, headers=HEADERS, timeout=60, stream=True)
        r.raise_for_status()
        content_type = r.headers.get("Content-Type", "")
        # Check we actually got a PDF (not an HTML login page)
        first_chunk = b""
        chunks = []
        for chunk in r.iter_content(chunk_size=8192):
            chunks.append(chunk)
            if not first_chunk:
                first_chunk = chunk
            if len(b"".join(chunks)) > 1024:
                break
        # Read rest
        for chunk in r.iter_content(chunk_size=8192):
            chunks.append(chunk)

        data = b"".join(chunks)
        # Verify it looks like a PDF
        if not data[:5] == b"%PDF-" and "pdf" not in content_type.lower():
            return False
        with open(dest, "wb") as f:
            f.write(data)
        return True
    except Exception:
        return False


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    with open(BIB_FILE, encoding="utf-8") as f:
        bib_db = bibtexparser.load(f)

    entries = bib_db.entries
    print(f"Found {len(entries)} references in {BIB_FILE}\n")

    results = {"downloaded": [], "not_found": [], "skipped": []}

    for i, entry in enumerate(entries, 1):
        key = entry.get("ID", "unknown")
        title = clean_title(entry.get("title", ""))
        entry_type = entry.get("ENTRYTYPE", "")

        # Skip non-article types (misc/web, books without likely PDFs)
        if entry_type in ("misc",):
            print(f"[{i}/{len(entries)}] {key}: skipping ({entry_type})")
            results["skipped"].append(key)
            continue

        dest = os.path.join(OUT_DIR, f"{key}.pdf")
        if os.path.exists(dest):
            print(f"[{i}/{len(entries)}] {key}: already downloaded")
            results["downloaded"].append(key)
            continue

        print(f"[{i}/{len(entries)}] {key}: \"{title[:60]}...\"")

        # Step 1: Get DOI via Crossref
        doi = entry.get("doi")
        if not doi:
            doi = search_crossref_doi(title)
            if doi:
                print(f"  DOI: {doi}")
            else:
                print(f"  No DOI found via Crossref")

        pdf_url = None

        # Step 2: Try Unpaywall
        if doi:
            pdf_url = unpaywall_pdf_url(doi)
            if pdf_url:
                print(f"  Unpaywall: {pdf_url[:80]}...")

        # Step 3: Fall back to Semantic Scholar
        if not pdf_url:
            pdf_url = semantic_scholar_pdf_url(title)
            if pdf_url:
                print(f"  Semantic Scholar: {pdf_url[:80]}...")

        # Step 4: Download
        if pdf_url:
            ok = download_pdf(pdf_url, dest)
            if ok:
                size_kb = os.path.getsize(dest) / 1024
                print(f"  -> Downloaded ({size_kb:.0f} KB)")
                results["downloaded"].append(key)
            else:
                print(f"  -> Download failed (not a valid PDF)")
                results["not_found"].append(key)
                if os.path.exists(dest):
                    os.remove(dest)
        else:
            print(f"  -> No open-access PDF found")
            results["not_found"].append(key)

        # Be polite to APIs
        time.sleep(1.0)

    # Summary
    print("\n" + "=" * 60)
    print(f"SUMMARY")
    print(f"  Downloaded:  {len(results['downloaded'])}")
    print(f"  Not found:   {len(results['not_found'])}")
    print(f"  Skipped:     {len(results['skipped'])}")
    if results["not_found"]:
        print(f"\nMissing (download manually via UCD library):")
        for k in results["not_found"]:
            print(f"  - {k}")


if __name__ == "__main__":
    main()
