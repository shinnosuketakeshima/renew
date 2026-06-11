#!/usr/bin/env python3
"""
Crawl taiken*.html pages, extract metadata, vectorize, and upload to Supabase.

Usage:
  python tools/vectorize_taiken.py --initial
  python tools/vectorize_taiken.py --taiken-number 32
"""

import os
import re
import argparse
from pathlib import Path
from typing import Dict, List, Optional
from html.parser import HTMLParser
import json

from supabase import create_client, Client
import google.generativeai as genai
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()


def _is_valid_credential(val: Optional[str]) -> bool:
    """Check if credential looks like a real value (not placeholder)."""
    if not val:
        return False
    val_lower = val.lower()
    # Reject obvious placeholders
    return not any([
        "your-" in val_lower,
        "placeholder" in val_lower,
        val_lower.startswith("https://your"),
        "example" in val_lower
    ])


# Initialize Supabase client only if credentials are valid
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if _is_valid_credential(SUPABASE_URL) and _is_valid_credential(SUPABASE_KEY):
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
else:
    supabase: Client = None  # Will be set later if credentials are valid

# Initialize Google Generative AI for embeddings
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)


class TaikenMetadataParser(HTMLParser):
    """Parse meta tags and structured data from taiken HTML."""

    def __init__(self):
        super().__init__()
        self.metadata = {
            "title": None,
            "description": None,
            "country": None,
            "age": None,
            "year": None
        }
        self.in_title = False
        self.title_text = ""
        self.in_script = False
        self.json_ld_data = None

    def handle_starttag(self, tag: str, attrs: List[tuple]):
        attrs_dict = dict(attrs)

        if tag == "title":
            self.in_title = True
        elif tag == "script":
            # Check if this is JSON-LD
            script_type = attrs_dict.get("type", "")
            if "application/ld+json" in script_type:
                self.in_script = True
        elif tag == "meta":
            name = attrs_dict.get("name", "")
            property_ = attrs_dict.get("property", "")
            content = attrs_dict.get("content", "")

            # Extract description
            if name == "description" or property_ == "og:description":
                self.metadata["description"] = content

            # Extract custom data attributes if present
            for attr_name, attr_value in attrs_dict.items():
                if attr_name == "data-country":
                    self.metadata["country"] = attr_value
                elif attr_name == "data-age":
                    try:
                        self.metadata["age"] = int(attr_value)
                    except ValueError:
                        pass
                elif attr_name == "data-year":
                    try:
                        self.metadata["year"] = int(attr_value)
                    except ValueError:
                        pass

    def handle_data(self, data: str):
        if self.in_title:
            self.title_text += data
        elif self.in_script:
            # Parse JSON-LD data
            try:
                json_data = json.loads(data)
                # Look for Article type with datePublished
                if isinstance(json_data, dict):
                    if json_data.get("@type") == "Article":
                        self.metadata["title"] = json_data.get("headline")
                        if "datePublished" in json_data:
                            # Extract year from ISO date string
                            date_str = json_data.get("datePublished", "")
                            if date_str:
                                year_match = re.match(r"(\d{4})", date_str)
                                if year_match:
                                    self.metadata["year"] = int(year_match.group(1))
            except json.JSONDecodeError:
                pass

    def handle_endtag(self, tag: str):
        if tag == "title":
            self.in_title = False
            self.metadata["title"] = self.title_text.strip()
        elif tag == "script":
            self.in_script = False


def extract_taiken_metadata(html: str, taiken_number: int) -> Dict:
    """
    Extract metadata and body text from taiken HTML.

    Extracts:
    - Title from <title> tag and JSON-LD
    - Description from <meta name="description">
    - Country from taiken-meta list
    - Age from taiken-meta (if available)
    - Year from taiken-meta or JSON-LD datePublished
    - Body text from <main> element

    Args:
        html: Full HTML content
        taiken_number: Taiken page number (1-84)

    Returns:
        Dict with taiken_number, title, body, country, age, year, url
    """
    parser = TaikenMetadataParser()
    parser.feed(html)

    # Parse body text from main content
    soup = BeautifulSoup(html, "html.parser")
    main = soup.find("main")
    body_text = ""

    if main:
        # Remove script and style elements
        for script in main(["script", "style"]):
            script.decompose()
        body_text = main.get_text(separator="\n", strip=True)

    # Clean up body text: collapse whitespace and normalize
    body_text = re.sub(r"\s+", " ", body_text).strip()

    # Extract country from taiken-meta list if not already set
    country = parser.metadata.get("country")
    if not country and soup:
        taiken_meta = soup.find("ul", class_="taiken-meta")
        if taiken_meta:
            for li in taiken_meta.find_all("li"):
                text = li.get_text()
                if "スリランカ" in text:
                    country = "スリランカ"
                    break
                elif "ネパール" in text:
                    country = "ネパール"
                    break

    # Try to extract age from title (e.g., "30代男性")
    age = parser.metadata.get("age")
    if not age and parser.metadata.get("title"):
        title = parser.metadata.get("title")
        age_match = re.search(r"(\d+)代", title)
        if age_match:
            age = int(age_match.group(1))

    return {
        "taiken_number": taiken_number,
        "title": parser.metadata.get("title") or f"Experience #{taiken_number}",
        "body": body_text[:5000],  # Cap at 5000 chars to keep embeddings efficient
        "country": country or "Unknown",
        "age": age,
        "year": parser.metadata.get("year"),
        "url": f"/taiken{taiken_number}.html"
    }


def embed_text(text: str) -> List[float]:
    """
    Generate embedding using Google Generative AI.

    Uses the embedding-001 model which returns 1536-dimensional vectors.

    Args:
        text: Text to embed (title + body combined)

    Returns:
        List of floats representing the embedding vector

    Raises:
        Exception: If API call fails or API key is not configured
    """
    if not GOOGLE_API_KEY:
        raise RuntimeError("GOOGLE_API_KEY not set. Cannot generate embeddings.")

    try:
        result = genai.embed_content(
            model="models/embedding-001",
            content=text,
            task_type="RETRIEVAL_DOCUMENT"
        )
        return result["embedding"]
    except Exception as e:
        print(f"[ERROR] Error embedding text: {e}")
        raise


def crawl_taiken_pages(taiken_number: Optional[int] = None) -> List[Dict]:
    """
    Crawl taiken HTML files and extract metadata.

    Reads HTML files from the repository root (taiken1.html through taiken84.html).
    Gracefully handles missing files by skipping them with a warning.

    Args:
        taiken_number: If set, crawl only this specific page (1-84).
                      If None, crawl all pages 1-84.

    Returns:
        List of dicts containing extracted metadata for each taiken page.
    """
    results = []
    numbers = [taiken_number] if taiken_number else range(1, 85)

    for num in numbers:
        # Construct path relative to current working directory
        path = Path(f"taiken{num}.html")

        if not path.exists():
            print(f"[WARN] taiken{num} not found, skipping")
            continue

        try:
            with open(path, "r", encoding="utf-8") as f:
                html = f.read()

            metadata = extract_taiken_metadata(html, num)
            results.append(metadata)
            print(f"[OK] Extracted taiken{num}")

        except Exception as e:
            print(f"[ERROR] Error processing taiken{num}: {e}")
            continue

    return results


def vectorize_and_upload(experiences: List[Dict]):
    """
    Vectorize experiences and upload to Supabase.

    For each experience:
    1. Combines title and body text
    2. Generates 1536-dim embedding via Google API
    3. Upserts record to taiken_experiences table (on conflict, replaces)

    Shows progress for each record. Errors in a single record do not stop processing.

    Args:
        experiences: List of experience dicts from extract_taiken_metadata

    Raises:
        RuntimeError: If Supabase client not initialized (missing env vars)
    """
    if not supabase:
        raise RuntimeError("Supabase client not initialized. Check SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY.")

    for exp in experiences:
        try:
            # Create text to embed (title + body)
            text_to_embed = f"{exp['title']}\n\n{exp['body']}"

            print(f"Vectorizing taiken{exp['taiken_number']}...", end=" ", flush=True)
            embedding = embed_text(text_to_embed)

            # Upsert to Supabase
            # Use upsert to handle existing records by replacing them
            response = supabase.table("taiken_experiences").upsert({
                "taiken_number": exp["taiken_number"],
                "title": exp["title"],
                "body": exp["body"],
                "country": exp["country"],
                "age": exp["age"],
                "year": exp["year"],
                "url": exp["url"],
                "embedding": embedding
            }).execute()

            print("[OK]")

        except Exception as e:
            print(f"[ERROR] Error: {e}")
            continue


def main():
    parser = argparse.ArgumentParser(
        description="Crawl taiken pages, vectorize, and upload to Supabase"
    )
    parser.add_argument(
        "--initial",
        action="store_true",
        help="Full crawl of all 84 pages (initial setup)"
    )
    parser.add_argument(
        "--taiken-number",
        type=int,
        help="Update specific taiken page (1-84)"
    )

    args = parser.parse_args()

    # Validate environment variables
    url_valid = _is_valid_credential(SUPABASE_URL)
    key_valid = _is_valid_credential(SUPABASE_KEY)
    google_valid = _is_valid_credential(GOOGLE_API_KEY)

    if not url_valid or not key_valid or not google_valid:
        print("Error: Missing or invalid environment variables")
        print("  SUPABASE_URL: " + ("OK" if url_valid else "MISSING/INVALID"))
        print("  SUPABASE_SERVICE_ROLE_KEY: " + ("OK" if key_valid else "MISSING/INVALID"))
        print("  GOOGLE_API_KEY: " + ("OK" if google_valid else "MISSING/INVALID"))
        exit(1)

    # Determine which pages to crawl
    taiken_num = args.taiken_number if args.taiken_number else None

    print(f"\n🔄 Crawling taiken pages...")
    experiences = crawl_taiken_pages(taiken_num)

    if not experiences:
        print("No pages found to process.")
        exit(1)

    print(f"\nFound {len(experiences)} page(s) to vectorize")
    print(f"\nVectorizing and uploading to Supabase...")
    vectorize_and_upload(experiences)

    print(f"\nDone! {len(experiences)} page(s) processed.")


if __name__ == "__main__":
    main()
