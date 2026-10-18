#!/usr/bin/env python3
"""Convert text in traditional Chinese pages, preserving URLs and code.

Optional dependency: pip install opencc-python-reimplemented==0.1.7
"""
from html.parser import HTMLParser
from pathlib import Path


class TextConverter(HTMLParser):
    def __init__(self, convert):
        super().__init__(convert_charrefs=False)
        self.convert = convert
        self.output = []
        self.skip = 0

    def handle_starttag(self, tag, attrs):
        self.output.append(self.get_starttag_text())
        if tag in ('script', 'style'):
            self.skip += 1

    def handle_startendtag(self, tag, attrs):
        self.output.append(self.get_starttag_text())

    def handle_endtag(self, tag):
        self.output.append(f'</{tag}>')
        if tag in ('script', 'style'):
            self.skip -= 1

    def handle_data(self, data):
        self.output.append(data if self.skip else self.convert(data))

    def handle_entityref(self, name):
        self.output.append(f'&{name};')

    def handle_charref(self, name):
        self.output.append(f'&#{name};')

    def handle_comment(self, data):
        self.output.append(f'<!--{data}-->')

    def handle_decl(self, decl):
        self.output.append(f'<!{decl}>')


def convert_file(path, convert):
    path = Path(path)
    original = path.read_text(encoding='utf-8')
    parser = TextConverter(convert)
    parser.feed(original)
    parser.close()
    result = ''.join(parser.output)
    if result != original:
        path.write_text(result, encoding='utf-8')
        return True
    return False


def main():
    try:
        from opencc import OpenCC
    except ImportError:
        raise SystemExit('Install the optional tool: pip install opencc-python-reimplemented==0.1.7')
    root = Path(__file__).resolve().parent / 'tc'
    converter = OpenCC('s2twp')
    changed = sum(convert_file(path, converter.convert) for path in sorted(root.rglob('*.html')))
    print(f'Converted text in {changed} pages; URLs, attributes and scripts preserved.')


if __name__ == '__main__':
    main()
