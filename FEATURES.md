# Features — Fridge Pick support site

Public GitHub Pages site for **Fridge Pick: Quick Meal Ideas**, live at [https://pavel-ship-it.github.io/fridge-pick-support/](https://pavel-ship-it.github.io/fridge-pick-support/). Sources live in `site/` and are built into `docs/`, which GitHub Pages serves from `main`. The site is English only, like the app.

## Implemented features

- **English-only site.** There is no `/ru/` section, no automatic locale redirect, and no language switcher. A request to `/ru/` is served as a 404. Verified by `check_en()` in `site/build.py`, which fails the build if Russian text or leftover `/ru/` / `hreflang="ru"` appears, and by a manual check of the live `/ru/` URL.
- **Home page (`/`).** Describes what Fridge Pick is, how it works in three steps, ten feature cards with links into the manual, a screenshot gallery, a privacy/offline summary, a note that the app interface is in English, an allergen and nutrition disclaimer, and support contact details. Verified by a manual check of the live home page.
- **User manual (`/manual/`).** Step-by-step guide with a table of contents and 17 sections covering getting started, the home screen, filters, My fridge, dish pages, sharing, favorites, I’m hungry, the week plan, the shopping list, menu and custom dishes, kitchen settings, allergies, excluded ingredients, data/offline use, FAQ, and further help. Verified by a manual check of the live manual.
- **Support page (`/support`).** Explains how to get help, gives the developer email, and includes answers about bugs, on-device data and deletion, offline use, allergen labels, and photo credits. Verified by a manual check of the live support page.
- **Link to the shared developer support page.** The support page points visitors to the common support page for all of Pavel’s apps at [https://pavel-ship-it.github.io/support](https://pavel-ship-it.github.io/support), as well as the Fridge Pick email. The footer also links to [https://pavel-ship-it.github.io/](https://pavel-ship-it.github.io/) (“More apps by Pavel Yakimenko”). Verified by a manual check of those links on the live pages.
- **Privacy policy (`/privacy`).** States that the app collects no personal data, works fully offline, has no accounts, analytics or ads, and keeps user data only on the device; notes that the device’s own backups (for example iCloud or Google) may include app data; covers OS-level crash reports, children, and GDPR-style rights. Verified by a manual check of the live privacy page.
- **Terms of use (`/terms`).** Personal non-commercial licence, reference-only recipes and nutrition, allergen and health disclaimer, no warranty, limitation of liability, third-party photo licences, and the Apple EULA for App Store users. Verified by a manual check of the live terms page.
- **Photo credits (`/credits`).** Lists authors and licences for dish photos from Wikimedia Commons (Creative Commons) and Unsplash, with a contact address for corrections. Verified by a manual check of the live credits page.
- **Custom 404.** `docs/404.html` is marked `noindex` and offers links to Home, the user manual, Support, and the developer email. Verified by a manual check of a missing path such as `/fridge-pick-support/ru/`.
- **App Store badge and Google Play placeholder.** The home page shows a “Download on the App Store” badge from `site/config.json` (`https://apps.apple.com/app/id6828103127`). `stores.google_play` is currently `null`, so the page shows “Coming soon to Google Play” and no Play badge. Verified by a manual check of the live home page and `site/config.json`.
- **Developer contact.** The address `dreamcomenull@gmail.com` appears in the footer, the home help bar, and on the support, manual, privacy, terms, credits and 404 pages. Verified by a manual check of those pages.
- **Shared site chrome.** Every page has a skip-to-content link, a header with the Fridge Pick brand and Features / Manual / Support navigation, breadcrumbs on inner pages, and a footer with Home, Manual, Support, Privacy Policy, Terms of Use, Photo Credits and the developer site. Verified by a manual check of the live pages.
- **SEO and social metadata.** Each page has its own title, description, canonical URL, Open Graph and Twitter Card tags, theme colour, favicons, apple-touch-icon, and the `og-en.jpg` preview image. Verified by a manual check of the HTML source.
- **Structured data.** The home page emits schema.org `WebSite` and `MobileApplication` JSON-LD (feature list, screenshots, and store `sameAs` / `installUrl` when configured). Inner pages emit `BreadcrumbList`. The manual also emits `FAQPage` (from `site/content/en/faq.json`) and `TechArticle`. Verified by a manual check of the HTML source.
- **Sitemap and robots.txt.** `docs/sitemap.xml` lists the six public pages (home, manual, support, privacy, terms, credits) with `lastmod` and priorities, and does not include `/ru/` URLs. `docs/robots.txt` allows all crawlers and points to the sitemap. Verified by a manual check of the live files.
- **Google Search Console verification.** Pages include the site-verification meta tag in the shared template. Verified by a manual check of the HTML source.
- **HTML content security policy.** After the pages are written, `site/build.py` adds a per-page `Content-Security-Policy` meta tag (restrictive `default-src`, hashed inline scripts, `form-action 'none'`, `upgrade-insecure-requests`) and `referrer: no-referrer`. Verified by a manual check of the built HTML.
- **Static site build.** `python3 site/build.py` rebuilds `docs/` from `site/` (Jinja templates, English Markdown/HTML content, assets, and `site/config.json`). The same run copies assets and writes `.nojekyll`. Verified by running the build; there is no CI workflow in this repository.

## Planned changes

None recorded.

No open issues or pull requests in this repository list unfinished work. Earlier requests that are already done are not listed here (including Pavel’s request to remove the Russian site, language switcher and automatic locale redirect). Suggestions that were discussed but not approved — for example making the App Store badge the primary home-page call to action, or reshooting screenshots after the Favorites filter was added — are not recorded as planned work.

## Features without tests

This repository has no test suite and no GitHub Actions (or other CI) workflow. The only automated check is `check_en()` in `site/build.py`, which runs at build time and only looks for leftover Russian text or `/ru/` links.

Everything else above is verified only by manual inspection of the live site, the built HTML, or a local build: page content and links, store badges, the shared developer support link, legal pages, the 404 page, SEO/JSON-LD, the sitemap, robots.txt, Search Console verification, and the content security policy.
