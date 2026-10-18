"""Repository-wide regression checks: python3 -m unittest discover -s tests -v."""
from collections import Counter
from hashlib import sha256
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urljoin, urlsplit
import importlib.util
import json
import re
import subprocess
import tempfile
import unittest
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
LANGS = ('en', 'de', 'ko', 'vi', 'zh', 'tc', 'ja')
SITE = 'https://www.guidetopheroes.com'


class Page(HTMLParser):
    def __init__(self, path):
        super().__init__(convert_charrefs=True)
        self.path = path
        self.raw = path.read_text(encoding='utf-8')
        self.tags = Counter()
        self.ends = Counter()
        self.ids = []
        self.refs = []
        self.links = []
        self.images = []
        self.scripts = []
        self.tables = {}
        self.table = None
        self.cell = None
        self.script = None
        self.language = None
        self.feed(self.raw)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        self.tags[tag] += 1
        if attrs.get('id'):
            self.ids.append(attrs['id'])
        if tag == 'html':
            self.language = attrs.get('lang')
        if tag == 'link':
            self.links.append(attrs)
        if tag == 'img':
            self.images.append(attrs.get('src'))
        for key in ('src', 'href', 'action', 'aria-controls'):
            if attrs.get(key):
                self.refs.append((key, attrs[key]))
        if tag == 'script':
            self.script = (attrs, [])
        if tag == 'table':
            self.table = attrs.get('id', 'anonymous')
            self.tables[self.table] = []
        if tag in ('td', 'th'):
            self.cell = []

    def handle_endtag(self, tag):
        self.ends[tag] += 1
        if tag == 'script' and self.script is not None:
            attrs, content = self.script
            self.scripts.append((attrs, ''.join(content)))
            self.script = None
        if tag in ('td', 'th') and self.cell is not None:
            self.tables[self.table].append(''.join(self.cell).strip())
            self.cell = None
        if tag == 'table':
            self.table = None

    def handle_data(self, data):
        if self.script is not None:
            self.script[1].append(data)
        if self.cell is not None:
            self.cell.append(data)


def language(path):
    first = path.relative_to(ROOT).parts[0]
    return first if first in LANGS else 'en'


def prefix(lang):
    return '' if lang == 'en' else '/' + lang


def load_module(filename):
    spec = importlib.util.spec_from_file_location(Path(filename).stem, ROOT / filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class SiteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pages = {p: Page(p) for p in ROOT.rglob('*.html')}

    def test_document_structure_and_languages(self):
        for path, page in self.pages.items():
            with self.subTest(path=str(path.relative_to(ROOT))):
                self.assertEqual(len(page.ids), len(set(page.ids)), 'Duplicate IDs')
                self.assertNotRegex(page.raw, r'(?m)^(?:<<<<<<<|=======|>>>>>>>)')
                self.assertEqual(len(re.findall(r'<script\b', page.raw)), len(re.findall(r'</script\s*>', page.raw)))
                if path.name in ('nav.html', 'footer.html'):
                    continue
                for tag in ('html', 'head', 'body'):
                    self.assertEqual(page.tags[tag], 1, tag)
                    self.assertEqual(page.ends[tag], 1, tag)
                self.assertEqual(page.tags['main'], page.ends['main'])
                self.assertEqual(page.language, 'zh-Hant' if language(path) == 'tc' else language(path))

    def test_official_english_content_is_preserved(self):
        class Content(HTMLParser):
            def __init__(self):
                super().__init__()
                self.skip = 0
                self.parts = []

            def handle_starttag(self, tag, attrs):
                if tag in ('head', 'script', 'style'):
                    self.skip += 1

            def handle_endtag(self, tag):
                if tag in ('head', 'script', 'style'):
                    self.skip -= 1

            def handle_data(self, data):
                if not self.skip and data.strip():
                    self.parts.append(' '.join(data.split()))

        # Captured from the original English files, excluding only the removed
        # Spring banner and obsolete duplicate home. Update intentionally when
        # the official editorial content changes.
        snapshot = json.loads((ROOT / 'tests/english-content.json').read_text())
        for name, expected in snapshot.items():
            with self.subTest(page=name):
                parser = Content()
                parser.feed((ROOT / name).read_text())
                self.assertEqual(sha256('\n'.join(parser.parts).encode()).hexdigest(), expected)

    def test_local_links_assets_fetches_and_anchors(self):
        for path, page in self.pages.items():
            with self.subTest(path=str(path.relative_to(ROOT))):
                base = SITE + '/' + path.relative_to(ROOT).as_posix()
                for attr, value in page.refs:
                    if attr == 'aria-controls':
                        self.assertIn(value, page.ids)
                        continue
                    url = urlsplit(urljoin(base, value))
                    if url.scheme not in ('http', 'https') or url.hostname not in ('www.guidetopheroes.com', 'guidetopheroes.com'):
                        continue
                    target = ROOT / unquote(url.path).lstrip('/')
                    if target.is_dir():
                        target /= 'index.html'
                    self.assertTrue(target.is_file(), f'{value} -> {target}')
                    if url.fragment and target in self.pages:
                        self.assertIn(unquote(url.fragment), self.pages[target].ids, value)
                for value in re.findall(r'fetch\(["\x27]([^"\x27]+)["\x27]\)', page.raw):
                    target = ROOT / urlsplit(urljoin(base, value)).path.lstrip('/')
                    self.assertTrue(target.is_file(), value)
                    if target.name == 'footer.html':
                        self.assertEqual(language(target), language(path))

    def test_metadata(self):
        for path, page in self.pages.items():
            if path.name in ('nav.html', 'footer.html') or '/html/index.html' in '/' + path.relative_to(ROOT).as_posix():
                continue
            with self.subTest(path=str(path.relative_to(ROOT))):
                canonical = [x['href'] for x in page.links if x.get('rel') == 'canonical']
                self.assertEqual(canonical, [SITE + '/' + path.relative_to(ROOT).as_posix()])
                alternatives = {x['hreflang']: x['href'] for x in page.links if x.get('rel') == 'alternate'}
                self.assertEqual(set(alternatives), {'en', 'de', 'ko', 'vi', 'zh', 'zh-Hant', 'ja', 'x-default'})
                for attrs, code in page.scripts:
                    if attrs.get('type') == 'application/ld+json':
                        data = json.loads(code)
                        if data.get('@type') == 'WebPage':
                            self.assertEqual(data['url'], canonical[0])
                            self.assertEqual(data['inLanguage'], page.language)

    def test_removed_pages_and_complete_language_sets(self):
        expected = {p.name for p in (ROOT / 'html').glob('*.html')}
        self.assertNotIn('spring.html', expected)
        self.assertNotIn('calculator.html', expected)
        for lang in LANGS[1:]:
            self.assertEqual({p.name for p in (ROOT / lang / 'html').glob('*.html')}, expected)
        for page in self.pages.values():
            self.assertNotRegex(page.raw, r'(?:spring|calculator)\.html')

    def test_translations_keep_official_images_and_table_values(self):
        for original in (ROOT / 'html').glob('*.html'):
            if original.name in ('index.html', 'nav.html', 'footer.html'):
                continue
            english = self.pages[original]
            for lang in LANGS[1:]:
                other = self.pages[ROOT / lang / 'html' / original.name]
                with self.subTest(page=original.name, lang=lang):
                    self.assertEqual(other.images, english.images)
                    self.assertEqual(set(other.tables), set(english.tables))
                    for name, cells in english.tables.items():
                        translated = other.tables[name]
                        self.assertEqual(len(translated), len(cells), name)
                        for a, b in zip(cells, translated):
                            # Numbers and units are editorial data from the English source.
                            if re.fullmatch(r'[\d.,\s%+$/*★☆-]+', a):
                                self.assertEqual(a, b, name)

    def test_sitemaps(self):
        namespace = {'s': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
        index = ET.parse(ROOT / 'sitemap-index.xml')
        actual = {x.text for x in index.findall('s:sitemap/s:loc', namespace)}
        self.assertEqual(actual, {SITE + f'/sitemap-{lang}.xml' for lang in LANGS})
        seen = set()
        for lang in LANGS:
            tree = ET.parse(ROOT / f'sitemap-{lang}.xml')
            urls = [x.text for x in tree.findall('s:url/s:loc', namespace)]
            self.assertEqual(len(urls), len(set(urls)))
            expected = {SITE + prefix(lang) + '/index.html'}
            directory = ROOT / (lang if lang != 'en' else '') / 'html'
            expected.update(SITE + prefix(lang) + '/html/' + p.name for p in directory.glob('*.html') if p.name not in ('nav.html', 'footer.html', 'thanks.html', 'index.html'))
            self.assertEqual(set(urls), expected)
            self.assertFalse(seen.intersection(urls))
            seen.update(urls)

    def test_javascript_syntax(self):
        for filename in ('nav-loader.js', 'lang-switcher.js'):
            result = subprocess.run(['node', '--check', str(ROOT / filename)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
        for path, page in self.pages.items():
            for attrs, code in page.scripts:
                if not code.strip() or attrs.get('type', '') not in ('', 'text/javascript', 'module'):
                    continue
                result = subprocess.run(['node', '--check', '--input-type=' + ('module' if attrs.get('type') == 'module' else 'commonjs')], input=code, capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, f'{path}: {result.stderr}')


class MaintenanceTests(unittest.TestCase):
    def test_copy_drafts_preserves_existing_translations_and_is_repeatable(self):
        module = load_module('copy_to_ja.py')
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / 'html').mkdir()
            (root / 'ja/html').mkdir(parents=True)
            (root / 'index.html').write_text('<html lang="en"></html>')
            (root / 'html/gear.html').write_text('official')
            (root / 'ja/html/gear.html').write_text('existing translation')
            self.assertEqual(len(module.copy_missing(root)), 1)
            self.assertEqual((root / 'ja/html/gear.html').read_text(), 'existing translation')
            self.assertEqual(module.copy_missing(root), [])

    def test_chinese_converter_preserves_urls_attributes_and_scripts(self):
        module = load_module('convert_tc_to_traditional.py')
        parser = module.TextConverter(lambda s: s.replace('汉', '漢'))
        parser.feed('<p title="汉"><a href="/汉/">汉字</a></p><script>const label="汉";</script><style>/* 汉 */</style>')
        self.assertEqual(''.join(parser.output), '<p title="汉"><a href="/汉/">漢字</a></p><script>const label="汉";</script><style>/* 汉 */</style>')


if __name__ == '__main__':
    unittest.main()
