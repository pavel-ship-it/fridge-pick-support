#!/usr/bin/env python3
"""Builds the Fridge Pick website into ../docs (served by GitHub Pages from main:/docs).

Edit the sources in site/ (templates/, content/, assets/, config.json) and run:
    python3 site/build.py
Needs: jinja2, markdown  (pip install jinja2 markdown)
"""
import json, os, re, shutil, hashlib, html
from jinja2 import Environment, FileSystemLoader, select_autoescape
from markupsafe import Markup
import markdown

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, 'docs')
CFG = json.load(open(os.path.join(HERE, 'config.json')))
BASE_URL, BASE_PATH = CFG['base_url'], CFG['base_path']
STORES = CFG['stores']


def rel(u):
    return BASE_PATH + u


def abs_(u):
    return BASE_URL + BASE_PATH + u


T = dict(
    locale='en_US',
    skip='Skip to content', nav_label='Main', footer_nav='Site',
    crumbs_label='Breadcrumb', nav_home='Home', nav_features='Features', nav_manual='Manual',
    nav_support='Support', nav_privacy='Privacy Policy', nav_terms='Terms of Use', nav_credits='Photo Credits',
    home='/', manual='/manual/', support='/support', privacy='/privacy', terms='/terms', credits='/credits',
    footer_tagline='Quick meal ideas from what’s in your fridge. Works offline, no account needed.',
    footer_contact='Questions or ideas?',
    og_alt='Fridge Pick: What can I cook right now? quick dishes from what’s in your fridge',
    badge_apple_small='Download on the', badge_google_small='Get it on',
    soon_both='Coming soon to the App Store and Google Play.', soon_play='Coming soon to Google Play.',
    soon_apple='Coming soon to the App Store.',
    dev_url='https://pavel-ship-it.github.io/', dev_link='More apps by Pavel Yakimenko', dev_support='https://pavel-ship-it.github.io/support',
)

URLS = {
    'home': '/', 'manual': '/manual/', 'support': '/support',
    'privacy': '/privacy', 'terms': '/terms', 'credits': '/credits',
}

PAGES = {
    'home': dict(title='Fridge Pick: Quick Meal Ideas from What’s in Your Fridge (iPhone & Android)',
                 og_title='Fridge Pick: Quick Meal Ideas',
                 description='Tick what’s in your fridge and Home shows what you can cook right now. Quick recipes (15 min or less), a cookbook, I’m hungry suggestions, a week plan and a shopping list. Metric or imperial units. Offline, no account.'),
    'manual': dict(title='Fridge Pick User Manual: How to Use Every Feature', crumb='User manual',
                   description='Step-by-step guide to Fridge Pick: Home, the Cookbook, My fridge and individual fruits, Seasonal, units, dish pages, sharing recipe cards, I’m hungry, week plan, shopping list and FAQ.'),
    'support': dict(title='Support – Fridge Pick', crumb='Support',
                    description='Get help with Fridge Pick: contact the developer, report a bug, and read answers about your data, offline use, allergen labels and dish photos.'),
    'privacy': dict(title='Privacy Policy – Fridge Pick', crumb='Privacy Policy',
                    description='Fridge Pick collects no personal data. It works fully offline, has no accounts, analytics or ads, and keeps everything you enter on your device.'),
    'terms': dict(title='Terms of Use – Fridge Pick', crumb='Terms of Use',
                  description='Terms of use for the Fridge Pick app for iPhone and Android: license, reference-only recipe and nutrition content, allergen disclaimer and photo licenses.'),
    'credits': dict(title='Photo Credits – Fridge Pick', crumb='Photo Credits',
                    description='Authors and licenses of the dish photos used in Fridge Pick, from Wikimedia Commons (Creative Commons) and Unsplash.'),
}


def strip_tags(s):
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', '', s))).strip()


def ld(obj):
    s = json.dumps(obj, ensure_ascii=False, separators=(',', ':'))
    return Markup(s.replace('</', '<\\/'))


def out_path(url):
    p = url.lstrip('/')
    if p == '' or p.endswith('/'):
        return os.path.join(OUT, p, 'index.html')
    return os.path.join(OUT, p + '.html')


def md_page(key):
    src = open(os.path.join(HERE, 'content', 'en', key + '.md'), encoding='utf-8').read()
    src = re.sub(r'^---\n.*?\n---\n', '', src, flags=re.S)
    src = re.sub(r"\{\{\s*'([^']+)'\s*\|\s*relative_url\s*\}\}", lambda m: rel(m.group(1)), src)
    body = markdown.markdown(src, extensions=['tables', 'sane_lists'])
    body = body.replace('<table>', '<div class="table-wrap"><table>').replace('</table>', '</table></div>')
    body = body.replace('<a href="http', '<a rel="noopener" href="http')
    return f'<article class="wrap narrow doc">\n{body}\n</article>'


def check_en(path, text):
    """English site. Pages may quote Russian app labels. No /ru/ pages."""
    if '/ru/' in text or re.search(r'hreflang="ru"', text):
        raise SystemExit(f'/ru/ or Russian hreflang leftover on {path}')


def main():
    env = Environment(loader=FileSystemLoader([os.path.join(HERE, 'templates'), os.path.join(HERE, 'content')]),
                      autoescape=select_autoescape(['html']), trim_blocks=False, lstrip_blocks=False)
    css = open(os.path.join(HERE, 'assets', 'site.css'), 'rb').read()
    env.globals.update(rel=rel, abs=abs_, stores=STORES, css_version=hashlib.md5(css).hexdigest()[:8])

    # fresh output (keep nothing stale)
    if os.path.exists(OUT):
        shutil.rmtree(OUT)
    shutil.copytree(os.path.join(HERE, 'assets'), os.path.join(OUT, 'assets'))
    for f in ('favicon.ico', 'favicon.png', 'apple-touch-icon.png'):
        shutil.copy(os.path.join(HERE, f), OUT)
    open(os.path.join(OUT, '.nojekyll'), 'w').close()

    sitemap = []
    faq = json.load(open(os.path.join(HERE, 'content', 'en', 'faq.json'), encoding='utf-8'))
    for key, meta in PAGES.items():
        url = URLS[key]
        page = dict(meta, url=url, kind=key, jsonld=[])
        if key != 'home':
            page['crumbs'] = [(T['nav_home'], T['home']), (meta['crumb'], url)]
            page['jsonld'].append(ld({
                '@context': 'https://schema.org', '@type': 'BreadcrumbList',
                'itemListElement': [{'@type': 'ListItem', 'position': i + 1, 'name': n, 'item': abs_(u)}
                                    for i, (n, u) in enumerate(page['crumbs'])]}))
        ctx = dict(lang='en', t=T, page=page, faq=faq)
        if key == 'home':
            page['jsonld'].insert(0, ld(home_ld(page)))
            body = env.get_template('en/home.html').render(**ctx)
        elif key in ('manual', 'support'):
            if key == 'manual':
                page['jsonld'].append(ld({
                    '@context': 'https://schema.org', '@type': 'FAQPage', 'inLanguage': 'en',
                    'mainEntity': [{'@type': 'Question', 'name': strip_tags(q['q']),
                                    'acceptedAnswer': {'@type': 'Answer', 'text': strip_tags(q['a'])}} for q in faq]}))
                page['jsonld'].append(ld({
                    '@context': 'https://schema.org', '@type': 'TechArticle', 'headline': meta['title'],
                    'description': meta['description'], 'inLanguage': 'en', 'url': abs_(url),
                    'dateModified': CFG['lastmod'], 'image': abs_('/assets/img/og-en.jpg'),
                    'author': {'@type': 'Person', 'name': 'Pavel Yakimenko'},
                    'about': {'@id': abs_(T['home'] + '#app')}}))
            body = env.get_template(f'en/{key}.html').render(**ctx)
        else:
            body = md_page(key)
        html_out = env.get_template('base.html').render(body=Markup(body), **ctx)
        check_en(url, html_out)
        p = out_path(url)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        open(p, 'w', encoding='utf-8').write(html_out)
        sitemap.append(key)

    # 404 (noindex)
    page = dict(title='Page not found – Fridge Pick', description='This page does not exist. Go to the Fridge Pick home page, manual or support.',
                url='/404', kind='404', jsonld=[], robots='noindex')
    body = env.get_template('404.html').render(lang='en', t=T, page=page)
    html404 = env.get_template('base.html').render(body=Markup(body), lang='en', t=T, page=page)
    check_en('404.html', html404)
    open(os.path.join(OUT, '404.html'), 'w', encoding='utf-8').write(html404)

    prio = {'home': '1.0', 'manual': '0.9', 'support': '0.8', 'privacy': '0.4', 'terms': '0.3', 'credits': '0.3'}
    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for key in sitemap:
        u = URLS[key]
        lines += ['  <url>', f'    <loc>{abs_(u)}</loc>', f'    <lastmod>{CFG["lastmod"]}</lastmod>',
                  f'    <priority>{prio[key]}</priority>', '  </url>']
    lines.append('</urlset>')
    open(os.path.join(OUT, 'sitemap.xml'), 'w').write('\n'.join(lines) + '\n')
    open(os.path.join(OUT, 'robots.txt'), 'w').write(
        f'User-agent: *\nAllow: /\n\nSitemap: {abs_("/sitemap.xml")}\n')
    print('built', len(sitemap), 'pages + 404 into', OUT)


def home_ld(page):
    feats = [
        'Home: what you can cook from what’s at home, with a glass tab bar (Home, Cookbook, Fridge, Plan)',
        'My fridge: tick the products you have, including individual fruits, and see dishes you can make now',
        'Seasonal dishes: an In season line on Home and a Seasonal filter, using the hemisphere of your region',
        'Units: Auto (from the phone), Metric or Imperial',
        'Quick dishes, 15 minutes or less, with photos, recipes and nutrition per serving',
        "I'm hungry: answer a few quick questions and get 3–5 dish suggestions",
        'Week plan for the next 7 days with Fill week and replacement suggestions',
        'Shopping list built from your week plan, shareable as text',
        'Share any recipe as an image card',
        'Allergy filters (11 common allergens) and excluded ingredients',
        'Recipes adapt to your kitchen appliances',
        'Favorites, your own dishes, works fully offline with no account',
    ]
    app = {
        '@type': 'MobileApplication', '@id': abs_(page['url'] + '#app'),
        'name': 'Fridge Pick: Quick Meal Ideas', 'alternateName': 'Fridge Pick',
        'description': page['description'], 'url': abs_(page['url']),
        'operatingSystem': 'iOS, Android', 'applicationCategory': 'LifestyleApplication',
        'applicationSubCategory': 'Food & Drink', 'softwareVersion': '1.0.0',
        'image': abs_('/assets/img/icon-512.jpg'),
        'screenshot': [abs_(f'/assets/img/{n}-720.webp') for n in ('01_home', '08_cookbook', '02_recipe', '03_im_hungry', '05_week_plan', '06_shopping_list', '07_my_fridge', '09_settings_units')],
        'featureList': feats,
        'author': {'@type': 'Person', 'name': 'Pavel Yakimenko', 'email': 'mailto:dreamcomenull@gmail.com'},
        'publisher': {'@type': 'Person', 'name': 'Pavel Yakimenko'},
        'inLanguage': 'en',
    }
    same = [u for u in (STORES.get('app_store'), STORES.get('google_play')) if u]
    if same:
        app['sameAs'] = same
        if STORES.get('google_play'):
            app['installUrl'] = STORES['google_play']
    site = {'@type': 'WebSite', '@id': abs_(page['url'] + '#website'), 'name': 'Fridge Pick', 'url': abs_('/'),
            'inLanguage': 'en', 'publisher': {'@type': 'Person', 'name': 'Pavel Yakimenko'}}
    return {'@context': 'https://schema.org', '@graph': [site, app]}


# --- Security: per-page meta CSP (GitHub Pages cannot set headers). Inline <script> blocks are allowed by
# their sha256 hash, so editing a script just needs a rebuild. JSON-LD data blocks are not executed and need no hash.
# frame-ancestors is not supported in <meta> CSP, so it is intentionally absent.
def add_csp(out_dir):
    import base64, glob as _glob, hashlib, re as _re
    for path in _glob.glob(os.path.join(out_dir, '**', '*.html'), recursive=True):
        s = open(path, encoding='utf-8').read()
        if 'http-equiv="Content-Security-Policy"' in s:
            continue
        hashes = sorted({"'sha256-" + base64.b64encode(hashlib.sha256(m.group(1).encode('utf-8')).digest()).decode() + "'"
                         for m in _re.finditer(r'<script>(.*?)</script>', s, _re.S)})
        csp = ("default-src 'none'; script-src 'self' " + ' '.join(hashes) + "; style-src 'self'; img-src 'self'; "
               "font-src 'self'; connect-src 'self'; manifest-src 'self'; base-uri 'none'; form-action 'none'; "
               "upgrade-insecure-requests")
        meta = ('\n<meta http-equiv="Content-Security-Policy" content="' + csp + '">'
                '\n<meta name="referrer" content="no-referrer">')
        assert '<meta charset="utf-8">' in s, path
        s = s.replace('<meta charset="utf-8">', '<meta charset="utf-8">' + meta, 1)
        open(path, 'w', encoding='utf-8').write(s)


if __name__ == '__main__':
    main()
    add_csp(OUT)
