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


T = {
    'en': dict(
        locale='en_US', locale_alt='ru_RU', other='ru', other_label='RU', other_name='Русская версия',
        other_title='Эта страница по-русски', skip='Skip to content', nav_label='Main', footer_nav='Site',
        crumbs_label='Breadcrumb', nav_home='Home', nav_features='Features', nav_manual='Manual',
        nav_support='Support', nav_privacy='Privacy Policy', nav_terms='Terms of Use', nav_credits='Photo Credits',
        home='/', manual='/manual/', support='/support', privacy='/privacy', terms='/terms', credits='/credits',
        footer_tagline='Quick meal ideas from what’s in your fridge. Works offline, no account needed.',
        footer_contact='Questions or ideas?',
        og_alt='Fridge Pick: What can I cook right now? 28 quick dishes from what’s in your fridge',
        badge_apple_small='Download on the', badge_google_small='Get it on',
        soon_both='Coming soon to the App Store and Google Play.', soon_play='Coming soon to Google Play.',
        soon_apple='Coming soon to the App Store.',
    ),
    'ru': dict(
        locale='ru_RU', locale_alt='en_US', other='en', other_label='EN', other_name='English version',
        other_title='This page in English', skip='Перейти к содержанию', nav_label='Основное меню', footer_nav='Разделы сайта',
        crumbs_label='Навигационная цепочка', nav_home='Главная', nav_features='Возможности', nav_manual='Руководство',
        nav_support='Поддержка', nav_privacy='Политика конфиденциальности', nav_terms='Условия использования',
        nav_credits='Авторы фотографий',
        home='/ru/', manual='/ru/manual/', support='/ru/support', privacy='/ru/privacy', terms='/ru/terms', credits='/ru/credits',
        footer_tagline='Быстрые блюда из того, что есть в холодильнике. Работает без интернета, регистрация не нужна.',
        footer_contact='Вопросы или идеи?',
        og_alt='Fridge Pick: что приготовить прямо сейчас? 28 быстрых блюд из того, что есть в холодильнике',
        badge_apple_small='Загрузите в', badge_google_small='Доступно в',
        soon_both='Скоро в App Store и Google Play.', soon_play='Скоро в Google Play.', soon_apple='Скоро в App Store.',
    ),
}

# key -> (en url, ru url)
URLS = {
    'home': ('/', '/ru/'), 'manual': ('/manual/', '/ru/manual/'), 'support': ('/support', '/ru/support'),
    'privacy': ('/privacy', '/ru/privacy'), 'terms': ('/terms', '/ru/terms'), 'credits': ('/credits', '/ru/credits'),
}

PAGES = {
    'en': {
        'home': dict(title='Fridge Pick: Quick Meal Ideas from What’s in Your Fridge (iPhone & Android)',
                     og_title='Fridge Pick: Quick Meal Ideas',
                     description='Tick what’s in your fridge and see what you can cook right now. 28 quick recipes (15 min or less), I’m hungry suggestions, a week plan and a shopping list. Offline, no account.'),
        'manual': dict(title='Fridge Pick User Manual: How to Use Every Feature', crumb='User manual',
                       description='Step-by-step guide to Fridge Pick: My fridge, filters, dish pages, sharing recipe cards, I’m hungry, week plan, shopping list, allergies, excluded ingredients, kitchen settings and FAQ.'),
        'support': dict(title='Support – Fridge Pick', crumb='Support',
                        description='Get help with Fridge Pick: contact the developer, report a bug, and read answers about your data, offline use, allergen labels and dish photos.'),
        'privacy': dict(title='Privacy Policy – Fridge Pick', crumb='Privacy Policy',
                        description='Fridge Pick collects no personal data. It works fully offline, has no accounts, analytics or ads, and keeps everything you enter on your device.'),
        'terms': dict(title='Terms of Use – Fridge Pick', crumb='Terms of Use',
                      description='Terms of use for the Fridge Pick app for iPhone and Android: license, reference-only recipe and nutrition content, allergen disclaimer and photo licenses.'),
        'credits': dict(title='Photo Credits – Fridge Pick', crumb='Photo Credits',
                        description='Authors and licenses of the dish photos used in Fridge Pick, from Wikimedia Commons (Creative Commons) and Unsplash.'),
    },
    'ru': {
        'home': dict(title='Fridge Pick — что приготовить из того, что есть в холодильнике (iPhone и Android)',
                     og_title='Fridge Pick — быстрые блюда из холодильника',
                     description='Отметьте продукты в холодильнике и узнайте, что приготовить прямо сейчас. 28 быстрых рецептов до 15 минут, подсказки, меню на неделю и список покупок. Без интернета и регистрации.'),
        'manual': dict(title='Руководство Fridge Pick: как пользоваться приложением', crumb='Руководство',
                       description='Пошаговое руководство по Fridge Pick: холодильник, фильтры, страница блюда, карточки рецептов, I’m hungry, меню на неделю, список покупок, аллергии, исключённые продукты, техника и FAQ.'),
        'support': dict(title='Поддержка – Fridge Pick', crumb='Поддержка',
                        description='Помощь по приложению Fridge Pick: связь с разработчиком, сообщения об ошибках, ответы о данных, работе без интернета, аллергенах и фотографиях блюд.'),
        'privacy': dict(title='Политика конфиденциальности – Fridge Pick', crumb='Политика конфиденциальности',
                        description='Fridge Pick не собирает персональные данные. Приложение работает без интернета, без учётных записей, аналитики и рекламы; всё хранится на вашем устройстве.'),
        'terms': dict(title='Условия использования – Fridge Pick', crumb='Условия использования',
                      description='Условия использования приложения Fridge Pick для iPhone и Android: лицензия, справочный характер рецептов и пищевой ценности, аллергены и лицензии фотографий.'),
        'credits': dict(title='Авторы фотографий – Fridge Pick', crumb='Авторы фотографий',
                        description='Авторы и лицензии фотографий блюд в Fridge Pick: Wikimedia Commons (Creative Commons) и Unsplash.'),
    },
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


def md_page(lang, key):
    src = open(os.path.join(HERE, 'content', lang, key + '.md'), encoding='utf-8').read()
    src = re.sub(r'^---\n.*?\n---\n', '', src, flags=re.S)
    src = re.sub(r"\{\{\s*'([^']+)'\s*\|\s*relative_url\s*\}\}", lambda m: rel(m.group(1)), src)
    body = markdown.markdown(src, extensions=['tables', 'sane_lists'])
    body = body.replace('<table>', '<div class="table-wrap"><table>').replace('</table>', '</table></div>')
    body = body.replace('<a href="http', '<a rel="noopener" href="http')
    return f'<article class="wrap narrow doc">\n{body}\n</article>'


def main():
    env = Environment(loader=FileSystemLoader([os.path.join(HERE, 'templates'), os.path.join(HERE, 'content')]),
                      autoescape=select_autoescape(['html']), trim_blocks=False, lstrip_blocks=False)
    css = open(os.path.join(HERE, 'assets', 'site.css'), 'rb').read()
    g = dict(rel=rel, abs=abs_, stores=STORES, css_version=hashlib.md5(css).hexdigest()[:8])
    env.globals.update(g)

    # fresh output (keep nothing stale)
    if os.path.exists(OUT):
        shutil.rmtree(OUT)
    shutil.copytree(os.path.join(HERE, 'assets'), os.path.join(OUT, 'assets'))
    for f in ('favicon.ico', 'favicon.png', 'apple-touch-icon.png'):
        shutil.copy(os.path.join(HERE, f), OUT)
    open(os.path.join(OUT, '.nojekyll'), 'w').close()

    sitemap = []
    for lang in ('en', 'ru'):
        t = T[lang]
        faq = json.load(open(os.path.join(HERE, 'content', lang, 'faq.json'), encoding='utf-8'))
        for key, meta in PAGES[lang].items():
            url = URLS[key][0 if lang == 'en' else 1]
            page = dict(meta, url=url, kind=key, alternates={'en': URLS[key][0], 'ru': URLS[key][1]}, jsonld=[])
            home_name = t['nav_home']
            if key != 'home':
                page['crumbs'] = [(home_name, t['home']), (meta['crumb'], url)]
                page['jsonld'].append(ld({
                    '@context': 'https://schema.org', '@type': 'BreadcrumbList',
                    'itemListElement': [{'@type': 'ListItem', 'position': i + 1, 'name': n, 'item': abs_(u)}
                                        for i, (n, u) in enumerate(page['crumbs'])]}))
            ctx = dict(lang=lang, t=t, page=page, faq=faq)
            if key == 'home':
                page['jsonld'].insert(0, ld(home_ld(lang, t, page)))
                body = env.get_template(f'{lang}/home.html').render(**ctx)
            elif key in ('manual', 'support'):
                if key == 'manual':
                    page['jsonld'].append(ld({
                        '@context': 'https://schema.org', '@type': 'FAQPage', 'inLanguage': lang,
                        'mainEntity': [{'@type': 'Question', 'name': strip_tags(q['q']),
                                        'acceptedAnswer': {'@type': 'Answer', 'text': strip_tags(q['a'])}} for q in faq]}))
                    page['jsonld'].append(ld({
                        '@context': 'https://schema.org', '@type': 'TechArticle', 'headline': meta['title'],
                        'description': meta['description'], 'inLanguage': lang, 'url': abs_(url),
                        'dateModified': CFG['lastmod'], 'image': abs_('/assets/img/og-' + lang + '.jpg'),
                        'author': {'@type': 'Person', 'name': 'Pavel Yakimenko'},
                        'about': {'@id': abs_(t['home'] + '#app')}}))
                body = env.get_template(f'{lang}/{key}.html').render(**ctx)
            else:
                body = md_page(lang, key)
            html_out = env.get_template('base.html').render(body=Markup(body), **ctx)
            p = out_path(url)
            os.makedirs(os.path.dirname(p), exist_ok=True)
            open(p, 'w', encoding='utf-8').write(html_out)
            if lang == 'en':
                sitemap.append(key)

    # 404 (bilingual, noindex)
    page = dict(title='Page not found – Fridge Pick', description='This page does not exist. Go to the Fridge Pick home page, manual or support.',
                url='/404', kind='404', alternates={'en': '/', 'ru': '/ru/'}, jsonld=[], robots='noindex')
    body = env.get_template('404.html').render(lang='en', t=T['en'], page=page)
    open(os.path.join(OUT, '404.html'), 'w', encoding='utf-8').write(
        env.get_template('base.html').render(body=Markup(body), lang='en', t=T['en'], page=page))

    # sitemap with hreflang alternates
    prio = {'home': '1.0', 'manual': '0.9', 'support': '0.8', 'privacy': '0.4', 'terms': '0.3', 'credits': '0.3'}
    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">']
    for key in sitemap:
        en, ru = URLS[key]
        for u in (en, ru):
            lines += ['  <url>', f'    <loc>{abs_(u)}</loc>', f'    <lastmod>{CFG["lastmod"]}</lastmod>',
                      f'    <priority>{prio[key]}</priority>',
                      f'    <xhtml:link rel="alternate" hreflang="en" href="{abs_(en)}"/>',
                      f'    <xhtml:link rel="alternate" hreflang="ru" href="{abs_(ru)}"/>',
                      f'    <xhtml:link rel="alternate" hreflang="x-default" href="{abs_(en)}"/>', '  </url>']
    lines.append('</urlset>')
    open(os.path.join(OUT, 'sitemap.xml'), 'w').write('\n'.join(lines) + '\n')
    open(os.path.join(OUT, 'robots.txt'), 'w').write(
        f'User-agent: *\nAllow: /\n\nSitemap: {abs_("/sitemap.xml")}\n')
    print('built', len(sitemap) * 2, 'pages + 404 into', OUT)


def home_ld(lang, t, page):
    en = lang == 'en'
    feats_en = ['My fridge: tick the products you have and see dishes you can make now',
                '28 quick dishes, 15 minutes or less, with photos, recipes and nutrition per serving',
                "I'm hungry: answer a few quick questions and get 3–5 dish suggestions",
                'Week plan for the next 7 days with Fill week and replacement suggestions',
                'Shopping list built from your week plan, shareable as text',
                'Share any recipe as an image card',
                'Allergy filters (11 common allergens) and excluded ingredients',
                'Recipes adapt to your kitchen appliances',
                'Favorites, your own dishes, works fully offline with no account']
    feats_ru = ['Мой холодильник: отметьте продукты и посмотрите, что можно приготовить сейчас',
                '28 быстрых блюд до 15 минут с фото, рецептами и пищевой ценностью порции',
                'I’m hungry: несколько быстрых вопросов и 3–5 подходящих блюд',
                'Меню на 7 дней с автозаполнением и подсказками замен',
                'Список покупок из меню на неделю, можно отправить текстом',
                'Отправка рецепта красивой карточкой-картинкой',
                'Фильтры по аллергенам (11 распространённых) и исключённые продукты',
                'Рецепты подстраиваются под вашу кухонную технику',
                'Избранное, свои блюда, полностью офлайн и без регистрации']
    app = {
        '@type': 'MobileApplication', '@id': abs_(page['url'] + '#app'),
        'name': 'Fridge Pick: Quick Meal Ideas', 'alternateName': 'Fridge Pick',
        'description': page['description'], 'url': abs_(page['url']),
        'operatingSystem': 'iOS, Android', 'applicationCategory': 'LifestyleApplication',
        'applicationSubCategory': 'Food & Drink', 'softwareVersion': '1.0.0',
        'image': abs_('/assets/img/icon-512.jpg'),
        'screenshot': [abs_(f'/assets/img/{n}-720.webp') for n in ('01_home', '02_recipe', '03_im_hungry', '05_week_plan', '06_shopping_list', '07_my_fridge')],
        'featureList': feats_en if en else feats_ru,
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
            'inLanguage': ['en', 'ru'], 'publisher': {'@type': 'Person', 'name': 'Pavel Yakimenko'}}
    return {'@context': 'https://schema.org', '@graph': [site, app]}


if __name__ == '__main__':
    main()
