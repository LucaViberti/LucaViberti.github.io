(function () {
  const NAV_FILE = '/nav.html'; // <-- fondamentale: assoluto, non relativo

  function normalizePath(pathname) {
    // /foo/ -> /foo/index.html
    if (!pathname) return 'index.html';
    if (pathname.endsWith('/')) return (pathname + 'index.html').toLowerCase();
    return pathname.toLowerCase();
  }

  function highlightCurrent(navRoot) {
    const currentPath = normalizePath(location.pathname);

    navRoot.querySelectorAll('nav a[href]').forEach((a) => {
      const rawHref = (a.getAttribute('href') || '').trim();
      if (!rawHref) return;

      // ignora hash / mailto / tel / link esterni
      if (rawHref.startsWith('#')) return;
      if (/^(mailto:|tel:|javascript:)/i.test(rawHref)) return;

      let linkPath = '';
      try {
        const u = new URL(rawHref, location.origin); // risolve anche href relativi
        linkPath = normalizePath(u.pathname);
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

    // Dropdown touch: primo tap apre, secondo segue il link
    navRoot.querySelectorAll('nav li.has-sub > a').forEach((link) => {
      link.addEventListener('click', function (e) {
        if (!isTouch) return;

        const li = this.parentElement;
        if (!li.classList.contains('open')) {
          e.preventDefault();
          li.classList.add('open');

          navRoot.querySelectorAll('nav li.has-sub.open').forEach((other) => {
            if (other !== li) other.classList.remove('open');
          });
        }
      });
    });

    // Evita che click dentro dropdown chiuda tutto
    navRoot.querySelectorAll('nav li .dropdown a').forEach((a) => {
      a.addEventListener('click', (e) => e.stopPropagation());
    });

    // Flyout Gear
    navRoot.querySelectorAll('.has-flyout .flyout-toggle').forEach((btn) => {
      btn.addEventListener('click', function (e) {
        e.stopPropagation();
        const li = this.closest('.has-flyout');
        const expanded = this.getAttribute('aria-expanded') === 'true';
        this.setAttribute('aria-expanded', expanded ? 'false' : 'true');
        li.classList.toggle('open', !expanded);
      });
    });

    // Chiudi cliccando fuori
    document.addEventListener('click', (e) => {
      const nav = navRoot.querySelector('nav');
      if (!nav || nav.contains(e.target)) return;

      navRoot.querySelectorAll('nav li.has-sub.open').forEach((li) => li.classList.remove('open'));
      navRoot.querySelectorAll('.has-flyout.open').forEach((li) => li.classList.remove('open'));
      navRoot.querySelectorAll('.has-flyout .flyout-toggle').forEach((btn) =>
        btn.setAttribute('aria-expanded', 'false')
      );
    });

    // ESC chiude
    document.addEventListener('keydown', (e) => {
      if (e.key !== 'Escape') return;

      navRoot.querySelectorAll('nav li.has-sub.open').forEach((li) => li.classList.remove('open'));
      navRoot.querySelectorAll('.has-flyout.open').forEach((li) => li.classList.remove('open'));
      navRoot.querySelectorAll('.has-flyout .flyout-toggle').forEach((btn) =>
        btn.setAttribute('aria-expanded', 'false')
      );
    });
  }

  document.addEventListener('DOMContentLoaded', async () => {
    const navContainer = document.getElementById('navbar');
    if (!navContainer) return;

    try {
      const res = await fetch(NAV_FILE, { cache: 'no-cache' });
      if (!res.ok) throw new Error(`HTTP ${res.status} for ${NAV_FILE}`);

      const html = await res.text();
      navContainer.innerHTML = html;

      highlightCurrent(navContainer);
      initNavInteractions(navContainer);
    } catch (err) {
      console.error('Navbar load failed:', err);
    }
  });
})();
