(function () {
  function ensureLangSwitcher() {
    return new Promise((resolve) => {
      if (window.LangSwitcher) return resolve(true);

      // Evita doppio load
      const existing = document.querySelector('script[src="/lang-switcher.js"]');
      if (existing) {
        existing.addEventListener('load', () => resolve(true));
        existing.addEventListener('error', () => resolve(false));
        return;
      }

      const script = document.createElement('script');
      script.src = '/lang-switcher.js';
      script.onload = () => resolve(true);
      script.onerror = () => resolve(false);
      document.head.appendChild(script);
    });
  }

  function getLangFromPath() {
    const p = (window.location.pathname || '').toLowerCase();
    if (p.startsWith('/ko/')) return 'ko';
    if (p.startsWith('/de/')) return 'de';
    if (p.startsWith('/vi/')) return 'vi';
    return 'en';
  }

  function getNavPath(lang) {
    if (lang === 'ko') return '/ko/html/nav.html';
    if (lang === 'de') return '/de/html/nav.html';
    if (lang === 'vi') return '/vi/html/nav.html';
    return '/html/nav.html';
  }

  function normalizePath(pathname) {
    let p = (pathname || '').toLowerCase();

    // se finisce con / -> index.html (opzionale, ma utile se hai root)
    if (p.endsWith('/')) p += 'index.html';

    return p;
  }

  function highlightCurrent(navRoot) {
    const currentPath = normalizePath(window.location.pathname);

    navRoot.querySelectorAll('nav a[href]').forEach((a) => {
      const raw = a.getAttribute('href') || '';
      // ignora anchor e link esterni
      if (!raw || raw.startsWith('#') || raw.startsWith('http')) return;

      // risolve href relativo -> pathname assoluto
      let linkPath;
      try {
        linkPath = normalizePath(new URL(raw, window.location.origin).pathname);
      } catch {
        return;
      }

      if (linkPath === currentPath) {
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

  document.addEventListener('DOMContentLoaded', async () => {
    const navContainer = document.getElementById('navbar');
    if (!navContainer) return;

    const lang = getLangFromPath();
    const navPath = getNavPath(lang);

    try {
      const res = await fetch(navPath);
      const html = await res.text();
      navContainer.innerHTML = html;

      highlightCurrent(navContainer);
      initNavInteractions(navContainer);

      // opzionale ma sensato: init del language selector appena il nav è montato
      const ok = await ensureLangSwitcher();
      if (ok && window.LangSwitcher?.initHeaderSelector) {
        window.LangSwitcher.initHeaderSelector('header-lang-selector');
      }
    } catch (err) {
      console.error('Navbar load failed:', err);
    }
  });
})();
