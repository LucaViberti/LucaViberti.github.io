#!/usr/bin/env python3
"""Create missing Japanese translation drafts without overwriting existing work."""
from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parent


def copy_missing(root=ROOT):
    root = Path(root)
    created = []
    sources = [(p, root / "ja/html" / p.name) for p in sorted((root / "html").glob("*.html"))]
    sources.append((root / "index.html", root / "ja/index.html"))
    for source, destination in sources:
        if destination.exists():
            continue
        destination.parent.mkdir(parents=True, exist_ok=True)
        text = source.read_text(encoding="utf-8")
        text = re.sub(r'(<html\s+lang=)["\'][^"\']+["\']', r'\1"ja"', text, count=1)
        text = re.sub(r'((?:href|action)=["\'])/html/', r'\1/ja/html/', text)
        text = re.sub(r'(href=["\'])/index\.html', r'\1/ja/index.html', text)
        text = text.replace("fetch('/html/footer.html')", "fetch('/ja/html/footer.html')")
        text = text.replace("window.location.replace('/index.html'", "window.location.replace('/ja/index.html'")
        text = text.replace('content="0;url=/index.html"', 'content="0;url=/ja/index.html"')
        text = text.replace('value="https://www.guidetopheroes.com/html/thanks.html"', 'value="https://www.guidetopheroes.com/ja/html/thanks.html"')
        canonical = 'https://www.guidetopheroes.com/ja/' + ('index.html' if destination.parent.name == 'ja' or destination.name == 'index.html' else 'html/' + destination.name)
        text = re.sub(r'(<link\s+rel="canonical"\s+href=")[^"]*', lambda match: match.group(1) + canonical, text)
        text = re.sub(r'(<meta\s+property="og:url"\s+content=")[^"]*', lambda match: match.group(1) + canonical, text)

        def localize_json(match):
            data = json.loads(match.group(2))
            if data.get('@type') == 'WebPage':
                data.update({'url': canonical, '@id': canonical + '#webpage', 'inLanguage': 'ja'})
            return match.group(1) + json.dumps(data, ensure_ascii=False) + match.group(3)

        text = re.sub(r'(<script[^>]*type="application/ld\+json"[^>]*>)(.*?)(</script>)', localize_json, text, flags=re.S)
        with destination.open("x", encoding="utf-8") as output:
            output.write(text)
        created.append(destination)
    return created


def main():
    created = copy_missing()
    for path in created:
        print(f"Created English draft to translate and review: {path.relative_to(ROOT)}")
    print(f"Created {len(created)} missing drafts; existing translations preserved.")


if __name__ == "__main__":
    main()
