#!/bin/bash
cd /workspaces/LucaViberti.github.io
git add html/nav.html de/html/nav.html ja/html/nav.html ko/html/nav.html tc/html/nav.html vi/html/nav.html zh/html/nav.html
git commit -m "Fix Heroes flyout overlap so Pets remains visible"
git pull --rebase origin main
git push origin main
rm -- "$0"
