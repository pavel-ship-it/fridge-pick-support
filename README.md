# Fridge Pick support site

Static site for **Fridge Pick: Quick Meal Ideas**, served by GitHub Pages from `docs/`
(https://pavel-ship-it.github.io/fridge-pick-support/). The site is in English.
The app is mostly English; Home, the tab bar, fruit names, units and the seasonal
line also have Russian wording when the phone language is Russian. The manual uses the English screen names.

`docs/` is generated — edit the sources in `site/` and rebuild:

```sh
python3 -m venv .venv && .venv/bin/pip install jinja2 markdown
.venv/bin/python site/build.py
```

- `site/content/en/` — home, manual, support (Jinja HTML), FAQ (`faq.json`, also emitted as FAQPage JSON-LD), legal pages (Markdown).
- `site/templates/` — layout, macros, 404.
- `site/assets/` — CSS and optimized images (`site/make_images.py` regenerates them from the app's store assets).
- `site/config.json` — base URL, `lastmod`, and **store links**: set `stores.app_store` / `stores.google_play`
  to the public URLs and rebuild; the badges appear on the home page (inside the `STORE-BADGES` markers)
  and as `sameAs` / `installUrl` in the MobileApplication JSON-LD.
