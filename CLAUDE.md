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

# Generate sitemap.xml at repo root
.\tools\generate-sitemap.ps1

# Audit all root *.html for SEO issues (canonical, title, description, H1 count, img alt)
# Exit code 1 if any ERROR-level issue is found; WARNs are non-fatal
.\tools\seo-audit.ps1
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
| `assets/js/faq-accordion.js` | FAQ accordion expand/collapse |
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
- Numbers to carry consistently: 21 years operating, ages 13–73, 7 days from ¥92,000.
- Business targets: 20 participants/year (Sri Lanka 8, Nepal 12) — Nepal growth is a priority, which is why Nepal content must be strong.
- No "industry cheapest / No.1" claims.
- Do not mention meeting/consultation anywhere on the site.
- Every page must have a clear inquiry (資料請求) call-to-action.

### Mobile

- 1-column layout on mobile; left/right margin ≥ 16px; body text ≥ 16px on mobile.
- Tap targets ≥ 44px.
- Tables: horizontal scroll or card conversion where needed.

## Deployment

Files are uploaded via FTP directly to the server's document root. The deploy scope is documented in `docs/DEPLOY-FTP.ja.md`. Use `.\tools\list-deploy-files.ps1` to generate the current candidate list before each upload. `docs/`, `tools/`, `.cursor/`, `.git/`, and `README.md` are never uploaded.

## URL Migration

Old pages must not be deleted without a 301 redirect to the new URL. This is pre-planned in the redesign spec. `taiken1.html`–`taiken84.html` redirect handling depends on server configuration — do not remove them without verifying the redirect setup.

## Operational Constraints

The site is maintained by a single person (the owner). Any structural change — new CSS patterns, JS components, page types — must remain simple enough for one non-developer to update. Avoid introducing abstractions or tooling dependencies that raise the maintenance bar.
