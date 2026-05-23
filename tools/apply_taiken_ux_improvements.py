#!/usr/bin/env python3
"""
Apply Stage 1 UX improvements to taiken HTML files.

Stage 1 improvements:
  1. Split paragraphs >100 chars at sentence boundaries (。)
  2. Add class="taiken-short-para" to all paragraphs
  3. Report missing alt text and empty figcaptions

Usage:
  python tools/apply_taiken_ux_improvements.py taiken3.html taiken4.html ...
  python tools/apply_taiken_ux_improvements.py --all           # Process all taiken*.html
  python tools/apply_taiken_ux_improvements.py --validate      # Report issues without modifying
"""

import re
import sys
import os
from pathlib import Path
from typing import List, Tuple

class TaikenUXImprover:
    def __init__(self, dry_run=False):
        self.dry_run = dry_run
        self.repo_root = Path(__file__).parent.parent
        self.issues = []
        self.stats = {
            'files_processed': 0,
            'paragraphs_split': 0,
            'missing_alts': 0,
            'empty_figcaptions': 0,
        }

    def split_paragraph(self, text: str) -> List[str]:
        """Split paragraph at sentence boundaries (。) keeping each ~80-100 chars."""
        if len(text) <= 100:
            return [text]

        # Split at sentence boundaries
        sentences = text.split('。')
        chunks = []
        current = ""

        for i, sent in enumerate(sentences):
            sent = sent.strip()
            if not sent:
                continue

            # Add period back except for last sentence
            if i < len(sentences) - 1:
                sent += '。'

            # Check if adding this sentence would exceed limit
            test_length = len(current) + len(sent)

            if test_length > 100 and current:
                # Start new chunk
                chunks.append(current)
                current = sent
            else:
                if current:
                    current += sent
                else:
                    current = sent

        if current:
            chunks.append(current)

        return chunks if chunks else [text]

    def replace_style2_paragraphs(self, html: str) -> Tuple[str, int]:
        """Replace <p class="style2"> with split <p class="taiken-short-para">.

        Note: Only processes <p> tags, not <span> or complex nested structures.
        """
        split_count = 0

        def replace_paragraph(match):
            nonlocal split_count
            text = match.group(1)

            # Remove <br/> and normalize whitespace
            text = re.sub(r'<br\s*/?>', ' ', text)
            text = re.sub(r'\s+', ' ', text).strip()

            chunks = self.split_paragraph(text)

            if len(chunks) > 1:
                split_count += len(chunks) - 1

            # Wrap each chunk
            result = '\n'.join(
                f'<p class="taiken-short-para">{chunk}</p>'
                for chunk in chunks
            )
            return result

        # ONLY match <p class="style2">...</p> (not nested <span> tags)
        html = re.sub(
            r'<p class="style2">(.*?)</p>',
            replace_paragraph,
            html,
            flags=re.DOTALL
        )

        return html, split_count

    def find_missing_alt_and_figcaptions(self, html: str, filepath: str) -> List[str]:
        """Report missing alt text and empty figcaptions."""
        issues = []
        filename = Path(filepath).name

        # Find images with empty alt
        for match in re.finditer(r'<img[^>]*alt=["\']([^"\']*)["\'][^>]*(?:src="([^"]+)")[^>]*>', html):
            alt_text = match.group(1)
            src = match.group(2)
            if not alt_text:
                issues.append(f"{filename}: Image '{src}' has empty alt text")
                self.stats['missing_alts'] += 1

        # Find empty figcaptions
        for match in re.finditer(r'<figcaption>\s*</figcaption>', html):
            issues.append(f"{filename}: Empty <figcaption> found at position {match.start()}")
            self.stats['empty_figcaptions'] += 1

        return issues

    def process_file(self, filepath: str) -> bool:
        """Process a single taiken file. Returns True if modified."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                original = f.read()

            # Apply improvements
            improved, split_count = self.replace_style2_paragraphs(original)

            # Find issues
            issues = self.find_missing_alt_and_figcaptions(improved, filepath)
            if issues:
                self.issues.extend(issues)

            # Write if modified
            modified = improved != original
            if modified and not self.dry_run:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(improved)

            self.stats['files_processed'] += 1
            self.stats['paragraphs_split'] += split_count

            return modified
        except Exception as e:
            print(f"[ERROR] Failed to process {filepath}: {e}")
            return False

    def process_files(self, files: List[str]):
        """Process multiple files."""
        modified_files = []

        for filepath in files:
            full_path = self.repo_root / filepath
            if not full_path.exists():
                print(f"[SKIP] {filepath} not found")
                continue

            if self.process_file(str(full_path)):
                modified_files.append(filepath)

        self._print_summary(modified_files)

    def _print_summary(self, modified_files: List[str]):
        """Print processing summary."""
        print("\n" + "="*70)
        print("STAGE 1 UX IMPROVEMENT SUMMARY")
        print("="*70)
        print(f"Files processed:      {self.stats['files_processed']}")
        print(f"Files modified:       {len(modified_files)}")
        print(f"Paragraphs split:     {self.stats['paragraphs_split']}")
        print(f"Missing alt texts:    {self.stats['missing_alts']}")
        print(f"Empty figcaptions:    {self.stats['empty_figcaptions']}")
        print("="*70)

        if modified_files:
            print(f"\nModified files:")
            for f in modified_files:
                print(f"  - {f}")

        if self.issues:
            print(f"\nIssues found (manual review needed):")
            for issue in self.issues:
                print(f"  [WARN] {issue}")

        if self.dry_run:
            print("\n[DRY RUN] No files were modified. Use without --validate to apply changes.")

def get_all_taiken_files() -> List[str]:
    """Get list of all taiken*.html files."""
    repo_root = Path(__file__).parent.parent
    files = sorted([
        f.name for f in repo_root.glob('taiken[0-9]*.html')
    ])
    return files

def main():
    if '--help' in sys.argv or '-h' in sys.argv:
        print(__doc__)
        return

    dry_run = '--validate' in sys.argv

    # Determine files to process
    if '--all' in sys.argv:
        files = get_all_taiken_files()
        print(f"Processing all {len(files)} taiken files...")
    else:
        # Use command-line arguments
        files = [
            arg for arg in sys.argv[1:]
            if arg.endswith('.html') and arg.startswith('taiken')
        ]
        if not files:
            print("Usage: python tools/apply_taiken_ux_improvements.py <taiken*.html> ...")
            print("       python tools/apply_taiken_ux_improvements.py --all")
            print("       python tools/apply_taiken_ux_improvements.py --validate")
            return

    improver = TaikenUXImprover(dry_run=dry_run)
    improver.process_files(files)

if __name__ == '__main__':
    main()
