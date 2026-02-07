(function () {
  const SUPPORTED_LANGS = ['en', 'it', 'es'];

  function normalizePath(path) {
    if (!path) return '/';
    return path.endsWith('/') ? `${path}index.html` : path;
  }

  function getCurrentLanguage() {
    const parts = location.pathname.split('/').filter(Boolean);
    const maybeLang = parts[0];
    return SUPPORTED_LANGS.includes(maybeLang) ? maybeLang : 'en';
  }

  function removeLangPrefix(pathname) {
    const langPrefix = pathname.match(/^\/(en|it|es)(\/|$)/);
    if (!langPrefix) return pathname;
    const stripped = pathname.replace(/^\/(en|it|es)/, '');
    return stripped || '/';
  }

  function buildPathForLanguage(basePath, targetLang) {
    if (targetLang === 'en') return basePath;
    return `/${targetLang}${basePath === '/' ? '/index.html' : basePath}`;
  }

  function highlightCurrent(navRoot) {
    const current = normalizePath(location.pathname.toLowerCase());

    navRoot.querySelectorAll('nav a[href]').forEach((a) => {
      const href = a.getAttribute('href') || '';
      if (href.startsWith('#') || href.startsWith('http')) return;

      const resolved = new URL(href, location.origin);
      const linkPath = normalizePath(resolved.pathname.toLowerCase());

      if (linkPath === current) {
        a.style.color = '#fff';
        a.style.borderBottomColor = '#29abe0';
      }
    });
  }

  function initLanguageSelector(navRoot) {
    const select = navRoot.querySelector('#language-select');
    if (!select) return;

    const currentLang = getCurrentLanguage();
    select.value = currentLang;

    select.addEventListener('change', (e) => {
      const targetLang = e.target.value;
      const basePath = removeLangPrefix(location.pathname);
      const nextPath = buildPathForLanguage(basePath, targetLang);
      location.assign(`${nextPath}${location.search}${location.hash}`);
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
      a.addEventListener('click', (e) => {
        e.stopPropagation();
      });
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

    document.addEventListener('click', (e) => {
      const nav = navRoot.querySelector('nav');
      if (!nav || nav.contains(e.target)) return;
      navRoot.querySelectorAll('nav li.has-sub').forEach((li) => li.classList.remove('open'));
      navRoot.querySelectorAll('.has-flyout .flyout-toggle').forEach((btn) => btn.setAttribute('aria-expanded', 'false'));
      navRoot.querySelectorAll('.has-flyout').forEach((li) => li.classList.remove('open'));
    });

    document.addEventListener('keydown', (e) => {
      if (e.key !== 'Escape') return;
      navRoot.querySelectorAll('nav li.has-sub').forEach((li) => li.classList.remove('open'));
      navRoot.querySelectorAll('.has-flyout .flyout-toggle').forEach((btn) => btn.setAttribute('aria-expanded', 'false'));
      navRoot.querySelectorAll('.has-flyout').forEach((li) => li.classList.remove('open'));
    });
  }

  document.addEventListener('DOMContentLoaded', () => {
    const navContainer = document.getElementById('navbar');
    if (!navContainer) return;

    const currentLang = getCurrentLanguage();
    const navPath = currentLang === 'en' ? '/html/nav.html' : `/${currentLang}/html/nav.html`;

    fetch(navPath)
      .then((res) => res.text())
      .then((html) => {
        navContainer.innerHTML = html;
        highlightCurrent(navContainer);
        initLanguageSelector(navContainer);
        initNavInteractions(navContainer);
      })
      .catch((err) => console.error('Navbar load failed:', err));
  });
})();
