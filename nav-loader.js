(function () {
  function highlightCurrent(navRoot) {
    const current = (location.pathname.split("/").pop() || "index.html").toLowerCase();
    navRoot.querySelectorAll('nav a[href]').forEach((a) => {
      const href = (a.getAttribute('href') || '').toLowerCase();
      if (href === current) {
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

  function loadTranslateWidget() {
    if (window.__googleTranslateLoaded) return;
    window.__googleTranslateLoaded = true;

    window.googleTranslateElementInit = function () {
      if (!document.getElementById('google_translate_element')) return;
      new window.google.translate.TranslateElement(
        { pageLanguage: 'en', autoDisplay: false },
        'google_translate_element'
      );
      const status = document.querySelector('.lang-status');
      if (status) status.style.display = 'none';
    };

    const showFallback = (message) => {
      const status = document.querySelector('.lang-status');
      if (status) status.textContent = message;
    const script = document.createElement('script');
    script.src = 'https://translate.google.com/translate_a/element.js?cb=googleTranslateElementInit';
    script.async = true;
    script.onerror = () => {
      const status = document.querySelector('.lang-status');
      if (status) status.textContent = 'Unavailable';
      const fallback = document.querySelector('.lang-fallback');
      if (fallback) {
        fallback.style.display = 'inline';
        fallback.href = `https://translate.google.com/translate?hl=en&sl=en&tl=it&u=${encodeURIComponent(location.href)}`;
      }
    };

    //const script = document.createElement('script');
    //script.src = 'https://translate.google.com/translate_a/element.js?cb=googleTranslateElementInit';
    //script.async = true;
    //script.onerror = () => {
      //showFallback('Unavailable');
    //};
    //document.head.appendChild(script);

    //window.setTimeout(() => {
      //const hasWidget = document.querySelector('#google_translate_element select');
      //if (!hasWidget) {
        //showFallback('Translate (blocked)');
      //}
    //}, 3000);
    ////document.head.appendChild(script);
  }

  document.addEventListener('DOMContentLoaded', () => {
    const navContainer = document.getElementById('navbar');
    if (!navContainer) return;

    fetch('nav.html')
      .then((res) => res.text())
      .then((html) => {
        navContainer.innerHTML = html;
        highlightCurrent(navContainer);
        initNavInteractions(navContainer);
       l
      })
      .catch((err) => console.error('Navbar load failed:', err));
  });
})();
