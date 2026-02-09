(function () {
  function loadScriptOnce(src) {
    return new Promise((resolve, reject) => {
      // già caricato?
      const existing = document.querySelector(`script[src="${src}"]`);
      if (existing) {
        // se era già in pagina ma non ancora pronto, aspetta un tick
        if (window.LangSwitcher) return resolve();
        existing.addEventListener('load', () => resolve(), { once: true });
        existing.addEventListener('error', () => reject(new Error(`Failed to load ${src}`)), { once: true });
        return;
      }

      const script = document.createElement('script');
      script.src = src;
      script.onload = () => resolve();
      script.onerror = () => reject(new Error(`Failed to load ${src}`));
      document.head.appendChild(script);
    });
  }

  function highlightCurrent(navRoot) {
    const current = (location.pathname.split("/").pop() || "index.html").toLowerCase();
    navRoot.querySelectorAll('nav a[href]').forEach((a) => {
      const href = (a.getAttribute('href') || '').toLowerCase();

      // match robusto: supporta sia "page.html" sia "/ko/html/page.html"
      if (href === current || href.endsWith('/' + current)) {
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

  function detectLangFromPath() {
    const p = window.location.pathname;
    if (p.startsWith('/de/')) return 'de';
    if (p.startsWith('/ko/')) return 'ko';
    return 'en';
  }

  document.addEventListener('DOMContentLoaded', async () => {
    const navContainer = document.getElementById('navbar');
    if (!navContainer) return;

    const lang = detectLangFromPath();
    const navPath =
      lang === 'de' ? '/de/html/nav.html'
      : lang === 'ko' ? '/ko/html/nav.html'
      : '/html/nav.html';

    try {
      // 1) carica nav
      const html = await fetch(navPath).then(r => r.text());
      navContainer.innerHTML = html;

      // 2) init interazioni + highlight
      highlightCurrent(navContainer);
      initNavInteractions(navContainer);

      // 3) carica switcher e init header selector
      await loadScriptOnce('/lang-switcher.js');

      // IMPORTANT: init SOLO quello dell'header (quello fisso già lo fai da solo nel file)
      if (window.LangSwitcher?.initHeaderSelector) {
        window.LangSwitcher.initHeaderSelector('header-lang-selector');
      }
    } catch (err) {
      console.error('Navbar load failed:', err);
    }
  });
})();
