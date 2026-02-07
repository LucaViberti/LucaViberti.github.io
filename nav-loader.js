(function () {
  function normalizePath(pathname) {
    if (!pathname || pathname === '/') return '/index.html';
    if (pathname.endsWith('/')) return pathname + 'index.html';
    return pathname;
  }

  function isItalian(pathname) {
    return normalizePath(pathname).startsWith('/it/');
  }

  function getPairPaths(pathname) {
    const normalized = normalizePath(pathname);
    if (isItalian(normalized)) {
      const enPath = normalized.replace(/^\/it/, '') || '/index.html';
      return { enPath, itPath: normalized };
    }
    return { enPath: normalized, itPath: `/it${normalized}` };
  }

  function createLanguageSelector() {
    const { enPath, itPath } = getPairPaths(location.pathname);
    const query = location.search || '';
    const hash = location.hash || '';
    const isIt = isItalian(location.pathname);

    const wrap = document.createElement('div');
    wrap.className = 'language-switcher-wrap';
    wrap.innerHTML = `
      <div class="language-switcher" aria-label="Language selector">
        <button class="language-switcher__btn" type="button" aria-expanded="false">${isIt ? 'Lingua' : 'Language'} ▾</button>
        <ul class="language-switcher__menu" hidden>
          <li><a href="${enPath}${query}${hash}">English</a></li>
          <li><a href="${itPath}${query}${hash}">Italiano</a></li>
        </ul>
      </div>
    `;

    if (!document.getElementById('language-switcher-style')) {
      const style = document.createElement('style');
      style.id = 'language-switcher-style';
      style.textContent = `
        .language-switcher-wrap{display:flex;justify-content:flex-end;max-width:1200px;margin:10px auto 0;padding:0 20px}
        .language-switcher{position:relative;z-index:30}
        .language-switcher__btn{background:#1e2541;color:#fff;border:1px solid #2b2f3a;border-radius:8px;padding:8px 12px;cursor:pointer;font:inherit}
        .language-switcher__menu{position:absolute;top:calc(100% + 6px);right:0;background:#1c2133;border:1px solid #2b2f3a;border-radius:8px;list-style:none;margin:0;padding:6px 0;min-width:130px}
        .language-switcher__menu a{display:block;padding:8px 12px;color:#d1d1d6;text-decoration:none}
        .language-switcher__menu a:hover{background:#25314d;color:#fff}
      `;
      document.head.appendChild(style);
    }

    const btn = wrap.querySelector('.language-switcher__btn');
    const menu = wrap.querySelector('.language-switcher__menu');
    btn.addEventListener('click', function (e) {
      e.stopPropagation();
      const open = btn.getAttribute('aria-expanded') === 'true';
      btn.setAttribute('aria-expanded', String(!open));
      menu.hidden = open;
    });
    document.addEventListener('click', function (e) {
      if (wrap.contains(e.target)) return;
      btn.setAttribute('aria-expanded', 'false');
      menu.hidden = true;
    });

    return wrap;
  }

  function highlightCurrent(navRoot) {
    const current = (location.pathname.split('/').pop() || 'index.html').toLowerCase();
    navRoot.querySelectorAll('nav a[href]').forEach((a) => {
      const href = (a.getAttribute('href') || '').toLowerCase();
      if (href.endsWith('/' + current) || href === current) {
        a.style.color = '#fff';
        a.style.borderBottomColor = '#29abe0';
      }
    });
  }

  function initNavInteractions(navRoot) {
    const isTouch = window.matchMedia('(hover: none)').matches;

    navRoot.querySelectorAll('nav li.has-sub > a').forEach((link) => {
      link.addEventListener('click', function (e) {
        const li = this.parentElement;
        if (!isTouch) return;
        if (!li.classList.contains('open')) {
          e.preventDefault();
          li.classList.add('open');
          navRoot.querySelectorAll('nav li.has-sub').forEach((other) => {
            if (other !== li) other.classList.remove('open');
          });
        }
      });
    });

    navRoot.querySelectorAll('nav li .dropdown a').forEach((a) => {
      a.addEventListener('click', (e) => e.stopPropagation());
    });

    navRoot.querySelectorAll('.has-flyout .flyout-toggle').forEach((btn) => {
      btn.addEventListener('click', function (e) {
        e.stopPropagation();
        const li = this.closest('.has-flyout');
        const expanded = this.getAttribute('aria-expanded') === 'true';
        this.setAttribute('aria-expanded', expanded ? 'false' : 'true');
        li.classList.toggle('open', !expanded);
      });
    });
  }

  document.addEventListener('DOMContentLoaded', () => {
    const navContainer = document.getElementById('navbar');
    if (!navContainer) return;

    navContainer.insertAdjacentElement('beforebegin', createLanguageSelector());

    const navPath = isItalian(location.pathname) ? '/it/html/nav.html' : '/html/nav.html';
    fetch(navPath)
      .then((res) => res.text())
      .then((html) => {
        navContainer.innerHTML = html;
        highlightCurrent(navContainer);
        initNavInteractions(navContainer);
      })
      .catch((err) => console.error('Navbar load failed:', err));
  });
})();
