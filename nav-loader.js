(function () {
  function getLanguageFromPath(pathname = location.pathname) {
    return pathname.startsWith('/it/') ? 'it' : 'en';
  }

  function normalizePath(pathname = location.pathname) {
    let normalized = pathname || '/index.html';
    if (normalized === '/') normalized = '/index.html';
    return normalized.replace(/\/+$/, '');
  }

  function getEquivalentPath(targetLanguage, pathname = location.pathname) {
    const normalized = normalizePath(pathname);
    const isItalianPath = normalized.startsWith('/it/');

    if (targetLanguage === 'it') {
      return isItalianPath ? normalized : `/it${normalized}`;
    }

    if (targetLanguage === 'en') {
      return isItalianPath ? normalized.replace(/^\/it/, '') : normalized;
    }

    return normalized;
  }

  function highlightCurrent(navRoot) {
    const currentPath = normalizePath();

    navRoot.querySelectorAll('nav a[href]').forEach((a) => {
      const rawHref = a.getAttribute('href') || '';
      if (!rawHref.startsWith('/')) return;

      const hrefPath = normalizePath(rawHref);
      if (hrefPath === currentPath) {
        a.style.color = '#fff';
        a.style.borderBottomColor = '#29abe0';
      }
    });
  }

  function initLanguageSelector(navRoot) {
    const selector = navRoot.querySelector('[data-language-selector]');
    if (!selector) return;

    selector.value = getLanguageFromPath();
    selector.addEventListener('change', (event) => {
      const targetLanguage = event.target.value;
      const destination = getEquivalentPath(targetLanguage);
      location.assign(destination);
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

    const language = getLanguageFromPath();
    const navUrl = language === 'it' ? '/it/html/nav.html' : '/html/nav.html';

    fetch(navUrl)
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
