# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a full redesign of **be-intl.com** (Beインターナショナル), a Japanese study-abroad agency offering homestay + individual English lessons in Sri Lanka and Nepal. The site is pure static HTML/CSS/JS — no build step, no framework, no CMS.

**Production files** are the repository root itself: `*.html`, `assets/`, and root-level images/GIFs. They deploy directly to the server's document root via FTP.

**Not uploaded to production:** `docs/`, `tools/`, `.cursor/`, `.git/`, `README.md`.

## Key Commands

```powershell
# Regenerate taiken.html (volunteer experience index) from the legacy backup
python tools/rebuild_taiken_index.py

# List files that belong in a production deploy (outputs tools/last-deploy-list.txt)
.\tools\list-deploy-files.ps1
```

There is no build step, test suite, or linter configured.

## Architecture

### File layout

| Location | Role |
|---|---|
| `index.html` and other root `*.html` | Production pages |
| `assets/css/home.css` | Global CSS: CSS custom properties (design tokens), layout, common components |
| `assets/css/typography.css` | Font imports (Inter + Noto Sans JP via Google Fonts) and type scale |
| `assets/css/*.css` | Per-page stylesheets (e.g. `faq.css`, `program.css`, `voices.css`) |
| `assets/js/site-header-nav.js` | Hamburger menu open/close, keyboard (Escape), aria-expanded |
| `assets/js/back-to-top.js` | Back-to-top button |
| `assets/images/` | Shared images referenced across multiple pages |
| `docs/be-intl-site-redesign-spec.md` | Full redesign specification — canonical authority for all product decisions |
| `docs/oldHP/` | Original legacy site preserved as reference (not served) |
| `tools/` | Maintenance scripts |

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
| `yakkan.html`, `privacy.html`, `others.html`, `links.html` | Footer-only pages |

Individual experience articles live at `taiken1.html`–`taiken84.html` in the root.

### CSS design system

All design tokens live in `:root` inside `assets/css/home.css`:

- `--color-primary: #183b66` (dark navy)
- `--color-accent: #e67e22` (burnt orange — CTAs and highlights only)
- `--color-bg: #fff8f1` (off-white)
- `--color-text: #222222`
- `--content-max: 1100px`
- `--header-h: 64px`
- `--font-sans: "Inter", "Noto Sans JP", sans-serif`

Every page includes `assets/css/home.css` + `assets/css/typography.css` + its own per-page stylesheet.

### Shared header/footer pattern

Every page replicates the same header and footer HTML. There is no server-side include. The header structure is:

```
.site-header > .layout-container.site-header__inner
  .site-logo
  nav.site-nav#primary-nav [data-nav]
  .site-header__end
    button.nav-toggle[data-menu-btn]
    a.btn.btn--accent.site-header__cta → postmail.html
```

`site-header-nav.js` is loaded on every page that has a hamburger menu.

## Design and Content Rules

The canonical authority is `docs/be-intl-site-redesign-spec.md` and `.cursor/rules/project-context.mdc`. When the spec conflicts with existing code, **follow the spec**.

### Hard constraints — never change

- The `postmail` form system: do not replace with another product; do not add or remove form fields; do not add `tel:` links.
- No SNS/LINE integration, no multilingual pages, no meeting-booking UI, no comparison claims against Western study abroad costs.
- Country-specific support organizations: **JASRI** for Sri Lanka, **ICEDC** for Nepal — never swap them.

### UI tone (current active rule)

The site uses an **Airbnb-style light UI**, not the earlier dark-green direction. Key points:
- White/off-white base; thin grey borders; minimal shadows.
- One accent color (`--color-accent` orange) for CTAs only.
- No gradients on UI elements; no vivid multi-color sections.
- Body text ≥ 16px; generous line-height.
- Buttons ≥ 48px tall; no "こちら" / "クリック" button labels.
- Every section ends with: testimonial excerpt → relevant FAQ → CTA bar.

### SEO requirements

- Each page must have a unique `<title>`, `<meta name="description">`, and `<link rel="canonical" href="https://be-intl.com/...">`.
- Exactly one `<h1>` per page; headings H1→H2→H3 only.
- All images need `alt`; purely decorative images use `alt=""`.
- Organization JSON-LD structured data on every page (see spec §10-5).
- BreadcrumbList on sub-pages; FAQPage on `faq.html`.

### Content rules

- Nepal is not a downgrade of Sri Lanka — lead with Himalayas, culture, volunteering.
- Primary target: women aged 30–40, solo travellers.
- Numbers to carry consistently: 21 years operating, ages 13–73, 7 days from ¥92,000.
- No "industry cheapest / No.1" claims.
- Do not mention meeting/consultation anywhere on the site.
