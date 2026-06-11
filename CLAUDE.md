# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a full redesign of **be-intl.com** (Beインターナショナル), a Japanese study-abroad agency offering homestay + individual English lessons in Sri Lanka and Nepal. The site is pure static HTML/CSS/JS — no build step, no framework, no CMS.

**Production files** are the repository root itself: `*.html`, `assets/`, and root-level images/GIFs. They deploy directly to the server's document root via FTP.

**Not uploaded to production:** `docs/`, `tools/`, `.cursor/`, `.git/`, `README.md`.

## Business Context

**Annual targets:** 20 participants/year total (8 Sri Lanka, 12 Nepal). Nepal growth is a strategic priority.  
**Monthly inquiry target:** ~11 inquiries/month (measured by 資料請求 submissions).  
**Key insight:** Increasing inquiry volume is the priority before optimizing conversion rate.

## Target Audience

**Primary (main site axis):** Women aged 30–40, solo travelers. Often at life transitions (career change, sabbatical, divorce, etc.). Primary concerns: safety, total cost, homestay environment, anxiety about solo travel.

**Secondary:** University students/20s, seniors, high-schoolers + parents, volunteer-motivated travelers. Site structure must favor primary audience, but secondary targets are welcome.

**Photos & voice:** Prioritize imagery where a solo woman aged 30–40 can picture herself. Avoid exclusively young/group/couple scenarios.

## Reference Hierarchy & Decision-Making

When in doubt, follow this priority order:

1. **`docs/be-intl-site-redesign-spec.md`** — canonical authority for all product decisions, design specifications, and feature scope.
2. **`.cursor/rules/project-context.mdc`** — secondary reference for business context, operational rules, and implementation guidance.
3. **Existing code** — follow the spec; only preserve existing code if it serves live-site stability (postmail system, course data, testimonials, pricing).
4. **Never change** (see below).

When spec conflicts with existing code, follow the spec — **except** for the non-negotiable constraints listed below.

## Key Commands

```powershell
# Regenerate taiken.html (volunteer experience index) from the legacy backup
python tools/rebuild_taiken_index.py

# Convert images (JPEG/PNG) to WebP in-place; outputs alongside originals
python tools/convert_to_webp.py

# List files that belong in a production deploy (outputs tools/last-deploy-list.txt)
.\tools\list-deploy-files.ps1

# Generate sitemap.xml at repo root
.\tools\generate-sitemap.ps1

# Audit all root *.html for SEO issues (canonical, title, description, H1 count, img alt)
# Exit code 1 if any ERROR-level issue is found; WARNs are non-fatal
.\tools\seo-audit.ps1
```

### Pre-Deploy Checklist

Before uploading to production:

```powershell
# 1. Audit SEO — must return exit code 0 for ERROR-level issues
.\tools\seo-audit.ps1

# 2. List files to deploy — review tools/last-deploy-list.txt for unintended files
.\tools\list-deploy-files.ps1

# 3. Verify in browser (mobile + desktop):
#    - All CTAs link to postmail.html or postmail form works if embedded
#    - No broken links, images, or resource loads
#    - Header, footer, nav work on small/large screens
#    - Testimonials, pricing, forms render correctly
```

There is no build step, test suite, or linter configured.

## Architecture

### File layout

| Location | Role |
|---|---|
| `index.html` and other root `*.html` | Production pages |
| `assets/css/home.css` | Global CSS: CSS custom properties (design tokens), layout, common components |
| `assets/css/typography.css` | Font imports (Inter + Noto Sans JP via Google Fonts) and type scale |
| `assets/css/srilanka.css` / `nepal.css` | Country-page styles |
| `assets/css/program.css` | Pricing / course page |
| `assets/css/voices.css` | Testimonials index |
| `assets/css/faq.css` | FAQ accordion page |
| `assets/css/volunteer.css` | Volunteer page |
| `assets/css/flow.css` | `process1.html` — departure flow |
| `assets/css/postmail.css` | Contact form page |
| `assets/css/legal.css` | `yakkan.html`, `privacy.html`, `others.html` |
| `assets/css/report.css` | Participant report list (`voices.html` sub-list); also used by `columns.html` and `column-*.html` |
| `assets/css/site-guide.css` | Internal site guide / about pages |
| `assets/css/taiken-article.css` | Individual experience articles (`taiken1.html`–`taiken84.html`) |
| `assets/js/site-header-nav.js` | Hamburger menu open/close, keyboard (Escape), aria-expanded |
| `assets/js/back-to-top.js` | Back-to-top button |
| `assets/js/faq-accordion.js` | FAQ accordion expand/collapse |
| `assets/js/card-visited.js` | Marks `.voice-card`, `.home-voices-teaser__card`, `.report-index__card` as visited via localStorage |
| `assets/images/` | Shared images referenced across multiple pages |
| `docs/be-intl-site-redesign-spec.md` | Full redesign specification — canonical authority for all product decisions |
| `docs/oldHP/` | Original legacy site preserved as reference (not served) |
| `tools/taiken_seo_preview.tsv` | SEO improvement data for all 84 taiken articles (proposed title, description, participant attributes) |
| `tools/` | Maintenance scripts (see below) |

The `tools/` directory contains two kinds of scripts:
- **Routine tools** (documented above): `rebuild_taiken_index.py`, `list-deploy-files.ps1`, `generate-sitemap.ps1`, `seo-audit.ps1`
- **One-time migration scripts** (do not re-run without reviewing): `migrate_taiken_batch1.py`, `convert_taiken_*.py`, `fix_taiken*.py`, `patch_legacy_*.py`, `seo_inject_*.py`, `normalize_footer_block.py`, `restore_taiken_blocks_from_oldhp.py`, etc. These were used during the taiken page migration and should not be run routinely.

### Page-to-URL mapping (new site structure)

| File | Intended URL |
|---|---|
| `index.html` | `/` |
| `srilanka.html` | `/srilanka/` |
| `nepal.html` | `/nepal/` |
| `program.html` | `/program/` |
| `voices.html` | `/voices/` |
| `volunteer.html` | `/volunteer/` |
| `faq.html` | `/faq/` |
| `postmail.html` | `/contact/` |
| `about.html` | `/about/` |
| `process1.html` | `/flow/` |
| `taiken.html` | `/taiken/` — index of all 84 experience articles (generated by `rebuild_taiken_index.py`) |
| `columns.html` | `/columns.html` — 留学コラム一覧 |
| `column-srilanka-english.html` | スリランカ英語教育コラム記事 |
| `column-nepal-english.html` | ネパール英語コラム記事 |
| `living-basics.html` | 現地生活の基礎知識（ナビに掲載中） |
| `yakkan.html`, `privacy.html`, `others.html`, `links.html` | Footer-only pages |

Individual experience articles live at `taiken1.html`–`taiken84.html` in the root.

### Legacy pages still in root (not part of new structure)

Many old-site pages remain in the root and deploy with the site. They are **not** part of the redesigned nav but must not be deleted without a 301 redirect in place. Examples: `indonesia.html`, `cost.html`, `scost.html`, `ncost.html`, `homestay.html`, `nhomestay.html`, `lesson.html`, `slesson.html`, `nlesson.html`, `security.html`, `nsecurity.html`, `free.html`, `jasri.html`, `nepallg.html`, `support.html`, `village.html`, `volunteers.html`, `report1.html`–`report5.html`, and various others listed in `tools/last-deploy-list.txt`. Do not edit these as if they follow the new design system — they are legacy pages preserved for URL continuity.

### CSS design system

All design tokens live in `:root` inside `assets/css/home.css`:

| Token | Value | Role |
|-------|-------|------|
| `--color-bg` | `#f7f5f0` | warm ivory — main background |
| `--color-bg-elevated` | `#f0ebe3` | muted beige — alternating section background |
| `--color-text` | `#2a2724` | charcoal — body copy |
| `--color-text-muted` | `#7a746c` | warm grey — sub-text, labels |
| `--color-primary` | `#1c1c28` | deep navy — CTAs, links, primary UI |
| `--color-border` | `#e0d8ce` | warm border |
| `--radius-md` | `2px` | near-square corners (editorial) |
| `--section-space` | `clamp(4rem, 7vw, 6rem)` | generous whitespace between sections |
| `--content-max` | `1100px` | max content width |
| `--header-h` | `60px` | fixed header height |
| `--font-sans` | `"Inter", "Noto Sans JP", sans-serif` | |

Every page includes `assets/css/home.css` + `assets/css/typography.css` + its own per-page stylesheet.

Filter buttons (used on `voices.html`): unselected `#EDEAE6`, selected `#D4B483`, hover `#C8A97E`. No box-shadow; smooth color transition only.

### CSS cache-busting

All `<link rel="stylesheet">` tags use a version querystring: `assets/css/home.css?v=YYYYMMDD{letter}`. When editing a CSS file, bump its querystring version on every page that includes it (e.g. `?v=20260611a`).

### Images

All production images are **WebP** (converted from JPEG/PNG via `tools/convert_to_webp.py`). When adding new images, convert to WebP first. Always include explicit `width` and `height` attributes on `<img>` elements to prevent CLS. Use `filter: saturate(0.88)` for subtle tonal matching if needed.

### Google Analytics 4

GA4 property `G-40ZZ28MV66` is loaded on every page via `<script async src="https://www.googletagmanager.com/gtag/js?id=G-40ZZ28MV66">`. Copy the exact snippet from any existing page — do not omit it from new pages.

### Async font loading

Non-critical fonts (Noto Serif JP) use the print-media swap pattern for non-blocking load:
```html
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Serif+JP:wght@400;500;600&display=swap" media="print" onload="this.media='all'">
<noscript><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Serif+JP:wght@400;500;600&display=swap"></noscript>
```

### Participant attribute typography

In `taiken*.html` and `voices.html`, participant attribute text (年代・性別など) uses dedicated classes with Noto Serif JP:

| Class | Context |
|-------|---------|
| `.taiken-head__attr` | H1 area of individual taiken articles |
| `.taiken-index__attr` | `voices.html` participant listing table |

These render in serif (`Noto Serif JP, Yu Mincho, MS Mincho, serif`) at a smaller size, distinct from the name (gothic body font).

### Shared header/footer pattern

Every page replicates the same header and footer HTML. There is no server-side include. The header structure is:

```
.site-header > .layout-container.site-header__inner
  .site-logo
  nav.site-nav#primary-nav [data-nav]
    スリランカ / ネパール / ボランティア / 料金 / 参加者の声
    現地生活の基礎知識 / よくある質問 / 留学コラム
  .site-header__end
    button.nav-toggle[data-menu-btn]
    a.btn.btn--accent.site-header__cta → postmail.html（資料請求）
```

`site-header-nav.js` is loaded on every page that has a hamburger menu.

### postmail system (CGI contact form)

The contact form runs on Perl CGI. The `postmail/` directory must be uploaded in its entirety:

| Location | Role |
|---|---|
| `postmail/postmail.cgi` | Main form handler |
| `postmail/init.cgi` | Configuration |
| `postmail/check.cgi` | CGI self-diagnostic (access `/check.cgi` to verify execution) |
| `postmail/lib/` | Perl module dependencies (CGI/, Jcode/, Unicode/) |
| `postmail/tmpl/conf.html` | Confirmation page |
| `postmail/tmpl/thanks.html` | Thank-you page |
| `postmail/tmpl/error.html` | Error page |
| `postmail/tmpl/mail.txt` | Admin notification email template |
| `postmail/tmpl/reply.txt` | Auto-reply email template |
| `postmail/data/` | Auto-generated log/session files (server-side, do not overwrite) |

The form action in `postmail.html` is `action="./postmail.cgi"` (root-relative). Do not change this path.

## Design and Content Rules

### Hard constraints — never change

These are non-negotiable for business, legal, or operational reasons:

- **Form system**: Continue using `postmail`. Do not replace with another product. Do not add, remove, or rename form fields. Do not add `tel:` links (phone numbers only in footer text if present). Form labels must go above their input fields.
- **Organization references**: **JASRI** for Sri Lanka only; **ICEDC** for Nepal only. Never swap them. This is tied to actual partnerships and cannot change. Service-level statements (e.g., "24-hour Japanese support") may be used for both countries, but organization names and location facts must be country-specific.
- **Prohibited features**: No SNS/LINE integration, no multilingual pages, no meeting-booking or consultation UI, no cost comparisons against Western study-abroad agencies, no "industry cheapest / No.1" claims.
- **Live-site data**: Do not remove or significantly thin out testimonials, pricing tables, course options, or participant reports (taiken pages) — these are core trust assets.

### Hero overlay gradient (left-side readability)

The hero uses a full-bleed photo with a left-side ivory gradient overlay for text legibility:

```css
background: linear-gradient(108deg,
  rgba(247,245,240,0.97) 0%,
  rgba(247,245,240,0.62) 36%,
  rgba(28,28,40,0.08) 100%
);
```

### Hero panel (confirmed implementation values)

```css
background: rgba(240, 235, 227, 0.25);  /* beige 25% opacity */
padding: 2rem 2.25rem 2.25rem 1.75rem;
border-radius: 1.5rem;
backdrop-filter: none;                   /* interior photo shows through unblurred */
mask-image: radial-gradient(
  ellipse 90% 88% at 46% 50%,
  black 52%,        /* solid readable zone */
  transparent 100%  /* soft edge fade */
);
```

- `backdrop-filter` is intentionally absent — the photo shows through the beige at full clarity inside the panel.
- Edge softness comes from `mask-image` only.
- `white-space: nowrap` on `.hero__kicker` and `.page-srilanka__kicker` prevents single trailing characters from wrapping.

### UI tone (current active rule)

The site uses a **boutique travel magazine / editorial / quiet luxury** aesthetic. The goal is to convey not "travel" but *"entering someone else's everyday life"*. **When in doubt, choose the quieter, more trustworthy option.** Show with whitespace and photos, not with busy UI.

Key rules:
- **Hero**: full-bleed photo, text overlays directly on an ivory gradient — no white floating panel box.
- **Section headings**: clean typography only. No navy box + orange left-border badge style. Do not use `display: table` to capsulize headings. Do not add decorative backgrounds or shadows to headings.
- **Two heading types**: label/kicker (`0.75rem / uppercase / letter-spacing: 0.12em / color: --color-text-muted`) and large heading (`clamp(1.4rem, 2.8vw, 1.75rem) / font-weight: 600 / letter-spacing: -0.01em`).
- **Buttons**: flat deep navy (`#1c1c28`), no gradients, no box-shadow. On dark backgrounds use ivory-reversed button (bg `#f7f5f0` / text `#1c1c28`). Height ≥ 48px; label must contain an action verb — no "こちら" or "クリック". One strong CTA per section.
- **Cards**: `1px solid var(--color-border)` only, no box-shadow. Hover = opacity or image scale (no `translateY`).
- **Border-radius**: 2–3px (near-square, editorial).
- **Sections**: full-width backgrounds alternating ivory / muted beige. No card-style side-margin containers. Content width controlled by inner `.layout-container` (max-width 1100px).
- **Header**: fixed, `background: rgba(247, 245, 240, 0.97)` + thin bottom border. Nav hover = underline only (no background chip). "資料請求" always visible. No phone number.
- Body text ≥ 16px; generous line-height (≥ 1.75); generous whitespace between sections.
- No orange (`#e67e22`), no Zoom-blue (`#183b66`), no gradients, no glassmorphism.
- Every section ends with: testimonial excerpt → relevant FAQ → CTA bar.

### Typography letter-spacing

| Element | letter-spacing |
|---------|---------------|
| h1 | `-0.02em` |
| h2 | `-0.01em` |
| kicker / label / uppercase | `0.08em–0.12em` |

### Photos

- Preferred: lesson scenes, homestay interiors, local nature, life-as-lived authenticity.
- Prioritize images where a solo woman aged 30–40 can picture herself.
- Do not mix Sri Lanka and Nepal photos on the same page.
- Subtle saturation reduction is acceptable: `filter: saturate(0.88)`. No heavy filters or staged stock-photo feel.

### SEO requirements

- Each page must have a unique `<title>`, `<meta name="description">`, and `<link rel="canonical" href="https://be-intl.com/...">`.
- Exactly one `<h1>` per page; headings H1→H2→H3 only.
- All images need `alt`; purely decorative images use `alt=""`.
- Organization JSON-LD structured data on every page (see spec §10-5).
- BreadcrumbList on sub-pages; FAQPage on `faq.html`.

### Content rules

- Nepal is not a downgrade of Sri Lanka — lead with Himalayas, culture, volunteering. **Do not mention comparative weaknesses** (e.g., "no ocean").
- Primary target: women aged 30–40, solo travellers (life transitions — career change, etc.). Address: safety, total cost, homestay environment, anxiety about solo travel.
- Secondary targets: university students/20s, seniors, high-schoolers with parents, volunteer-motivated travellers. The site's main axis stays aligned to the primary target.
- Numbers to carry consistently: 21 years operating, ages 13–73, 7 days from ¥92,000.
- Business targets: 20 participants/year (Sri Lanka 8, Nepal 12) — Nepal growth is a priority, which is why Nepal content must be strong.
- No "industry cheapest / No.1" claims.
- Do not mention meeting/consultation anywhere on the site.
- Every page must have a clear inquiry (資料請求) call-to-action.

### Core strengths — never diminish

- **Testimonials** (体験者の声): the primary trust asset — never cut or thin out.
- **Price transparency**: fee table and cost breakdown must remain complete.
- **Course duration flexibility**: the wide range of duration options is a differentiator — preserve it.
- **Volunteer component**: unique differentiator for Nepal — keep it prominent.
- **Participant reports** (taiken pages): real-life evidence of the program — treat as valuable content, not legacy clutter.

### Accessibility

- Contrast must meet WCAG AA (deep navy on ivory satisfies this).
- All interactive elements must be keyboard-operable.
- Heading hierarchy H1→H2→H3 — never skip levels or use headings for decoration.

### Mobile

- 1-column layout on mobile; left/right margin ≥ 16px; body text ≥ 16px on mobile.
- Tap targets ≥ 44px.
- Tables: horizontal scroll or card conversion where needed.

## Implementation Priority Order

When planning work on multiple pages, prioritize in this order (later items depend on earlier ones):

1. **Top page** (`index.html`) + **shared header/footer** (`site-header-nav.js`, common footer)
2. **Country pages**: `srilanka.html`, then `nepal.html` (Nepal content strength is a priority)
3. **Program/pricing page** (`program.html`)
4. **Testimonials/voices** (`voices.html` + voice cards across all pages)
5. **FAQ** (`faq.html`), flow (`process1.html`), volunteer (`volunteer.html`), about (`about.html`)
6. **Footer-only pages** (privacy, links, etc.) + SEO tuning

### Completion Criteria

- Site is readable and fully functional on mobile (tested in browser, not just responsive view).
- Main nav is clear and simple; 資料請求 is always accessible.
- Every page has a clear inquiry call-to-action (resources request link/button).
- Testimonials and pricing are visible and compelling.
- Nepal content is not positioned as a downgrade — unique strengths are clear.
- Single-person maintenance is viable (no complex tooling, no CMS, no abstraction layers required for content updates).

## Deployment

Files are uploaded via FTP directly to the server's document root. The deploy scope is documented in `docs/DEPLOY-FTP.ja.md`. Use `.\tools\list-deploy-files.ps1` to generate the current candidate list before each upload. `docs/`, `tools/`, `.cursor/`, `.git/`, and `README.md` are never uploaded.

**CGI-specific requirements:** Upload `*.cgi` files in **binary mode** (not text mode). After upload, set permissions to **755** via FTP client (e.g., FileZilla → right-click → File permissions). Verify CGI is executing by visiting `https://be-intl.com/check.cgi` — a diagnostic page should appear (not raw Perl source). A 500 error usually means a wrong Perl shebang path (`#!/usr/local/bin/perl`); a text display means permissions are not set to 755.

## URL Migration

Old pages must not be deleted without a 301 redirect to the new URL. This is pre-planned in the redesign spec. `taiken1.html`–`taiken84.html` redirect handling depends on server configuration — do not remove them without verifying the redirect setup.

## Operational Constraints

The site is maintained by a single person (the owner). Any structural change — new CSS patterns, JS components, page types — must remain simple enough for one non-developer to update. Avoid introducing abstractions or tooling dependencies that raise the maintenance bar.

## Working Style

- Before updating a page, confirm: purpose, target user, primary CTA, required sections.
- Change one page or one component at a time — not multiple pages in one pass.
- Before any large change, list what will be modified as a short bullet summary.
- If you want to add something not in the spec, propose it separately rather than implementing it unilaterally.
- When creating new UI patterns, first check whether an existing pattern in `home.css` / `index.html` can be reused or extended.
