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
    if (p.startsWith('/tc/')) return 'tc';
    if (p.startsWith('/zh/')) return 'zh';
    if (p.startsWith('/ja/')) return 'ja';
    return 'en';
  }

  function stripLangPrefix(pathname) {
    let p = pathname || '';
    if (p.startsWith('/de/')) return p.slice(3);
    if (p.startsWith('/ko/')) return p.slice(3);
    if (p.startsWith('/vi/')) return p.slice(3);
    if (p.startsWith('/tc/')) return p.slice(3);
    if (p.startsWith('/zh/')) return p.slice(3);
    if (p.startsWith('/ja/')) return p.slice(3);
    return p;
  }

  function normalizeBasePath(pathname) {
    let p = pathname || '';
    if (!p.startsWith('/')) p = '/' + p;
    if (p === '/' || p === '') return '/index.html';
    if (p.endsWith('/')) return p + 'index.html';
    return p;
  }

  function buildLangPath(lang, basePath) {
    const normalized = normalizeBasePath(basePath);
    if (lang === 'en') return normalized;
    return '/' + lang + normalized;
  }

  function ensureMetaTag(selector, attrs) {
    let tag = document.head.querySelector(selector);
    if (!tag) {
      tag = document.createElement('meta');
      Object.keys(attrs).forEach((key) => tag.setAttribute(key, attrs[key]));
      document.head.appendChild(tag);
      return tag;
    }
    Object.keys(attrs).forEach((key) => tag.setAttribute(key, attrs[key]));
    return tag;
  }

  function ensureLinkTag(selector, attrs) {
    let tag = document.head.querySelector(selector);
    if (!tag) {
      tag = document.createElement('link');
      Object.keys(attrs).forEach((key) => tag.setAttribute(key, attrs[key]));
      document.head.appendChild(tag);
      return tag;
    }
    Object.keys(attrs).forEach((key) => tag.setAttribute(key, attrs[key]));
    return tag;
  }

  function ensureJsonLd(id, payload) {
    const existing = document.getElementById(id);
    if (existing) {
      existing.textContent = JSON.stringify(payload);
      return;
    }
    const script = document.createElement('script');
    script.type = 'application/ld+json';
    script.id = id;
    script.textContent = JSON.stringify(payload);
    document.head.appendChild(script);
  }

  function ensureSeoTags() {
    const siteUrl = 'https://www.guidetopheroes.com';
    const siteName = 'TopHeroes Guide';
    const ogImagePath = '/images/og-image.svg';
    const currentLang = getLangFromPath();
    let currentPath = normalizeBasePath(stripLangPrefix(window.location.pathname || '/'));
    if (currentPath === '/html/index.html') currentPath = '/index.html';
    const canonicalPath = buildLangPath(currentLang, currentPath);
    const canonicalUrl = siteUrl + canonicalPath;
    const ogImageUrl = siteUrl + ogImagePath;
    const homeUrl = siteUrl + buildLangPath(currentLang, '/index.html');

    const descriptionTag = document.head.querySelector('meta[name="description"]');
    const description = descriptionTag?.getAttribute('content') || (document.title + ' - ' + siteName + '.');
    if (!descriptionTag) {
      ensureMetaTag('meta[name="description"]', { name: 'description', content: description });
    }

    if (!document.head.querySelector('meta[name="robots"]')) {
      ensureMetaTag('meta[name="robots"]', {
        name: 'robots',
        content: 'index, follow, max-snippet:-1, max-image-preview:large, max-video-preview:-1'
      });
    }
    if (!document.head.querySelector('meta[name="googlebot"]')) {
      ensureMetaTag('meta[name="googlebot"]', {
        name: 'googlebot',
        content: 'index, follow, max-snippet:-1, max-image-preview:large, max-video-preview:-1'
      });
    }

    ensureMetaTag('meta[name="referrer"]', { name: 'referrer', content: 'strict-origin-when-cross-origin' });
    ensureMetaTag('meta[name="theme-color"]', { name: 'theme-color', content: '#141720' });

    ensureLinkTag('link[rel="preconnect"][href="https://pagead2.googlesyndication.com"]', {
      rel: 'preconnect',
      href: 'https://pagead2.googlesyndication.com'
    });
    ensureLinkTag('link[rel="preconnect"][href="https://www.googletagservices.com"]', {
      rel: 'preconnect',
      href: 'https://www.googletagservices.com'
    });
    ensureLinkTag('link[rel="preconnect"][href="https://googleads.g.doubleclick.net"]', {
      rel: 'preconnect',
      href: 'https://googleads.g.doubleclick.net'
    });
    ensureLinkTag('link[rel="preconnect"][href="https://tpc.googlesyndication.com"]', {
      rel: 'preconnect',
      href: 'https://tpc.googlesyndication.com'
    });
    ensureLinkTag('link[rel="preconnect"][href="https://js.stripe.com"]', {
      rel: 'preconnect',
      href: 'https://js.stripe.com'
    });
    ensureLinkTag('link[rel="dns-prefetch"][href="https://pagead2.googlesyndication.com"]', {
      rel: 'dns-prefetch',
      href: 'https://pagead2.googlesyndication.com'
    });
    ensureLinkTag('link[rel="dns-prefetch"][href="https://www.googletagservices.com"]', {
      rel: 'dns-prefetch',
      href: 'https://www.googletagservices.com'
    });
    ensureLinkTag('link[rel="dns-prefetch"][href="https://googleads.g.doubleclick.net"]', {
      rel: 'dns-prefetch',
      href: 'https://googleads.g.doubleclick.net'
    });
    ensureLinkTag('link[rel="dns-prefetch"][href="https://tpc.googlesyndication.com"]', {
      rel: 'dns-prefetch',
      href: 'https://tpc.googlesyndication.com'
    });
    ensureLinkTag('link[rel="dns-prefetch"][href="https://js.stripe.com"]', {
      rel: 'dns-prefetch',
      href: 'https://js.stripe.com'
    });
    ensureLinkTag('link[rel="preload"][as="image"][href="' + ogImageUrl + '"]', {
      rel: 'preload',
      as: 'image',
      href: ogImageUrl
    });

    ensureLinkTag('link[rel="canonical"]', { rel: 'canonical', href: canonicalUrl });

    const hreflangList = {
      en: 'en',
      de: 'de',
      ko: 'ko',
      vi: 'vi',
      zh: 'zh',
      ja: 'ja'
    };

    Object.keys(hreflangList).forEach((lang) => {
      const href = siteUrl + buildLangPath(lang, currentPath);
      ensureLinkTag(`link[rel="alternate"][hreflang="${hreflangList[lang]}"]`, {
        rel: 'alternate',
        hreflang: hreflangList[lang],
        href
      });
    });

    ensureLinkTag('link[rel="alternate"][hreflang="x-default"]', {
      rel: 'alternate',
      hreflang: 'x-default',
      href: siteUrl + buildLangPath('en', currentPath)
    });

    ensureMetaTag('meta[property="og:title"]', { property: 'og:title', content: document.title });
    ensureMetaTag('meta[property="og:description"]', { property: 'og:description', content: description });
    ensureMetaTag('meta[property="og:url"]', { property: 'og:url', content: canonicalUrl });
    ensureMetaTag('meta[property="og:type"]', { property: 'og:type', content: 'website' });
    ensureMetaTag('meta[property="og:site_name"]', { property: 'og:site_name', content: siteName });
    ensureMetaTag('meta[property="og:image"]', { property: 'og:image', content: ogImageUrl });
    ensureMetaTag('meta[property="og:image:type"]', { property: 'og:image:type', content: 'image/svg+xml' });
    ensureMetaTag('meta[property="og:image:alt"]', { property: 'og:image:alt', content: 'TopHeroes Guide cover image' });

    const localeMap = {
      en: 'en_US',
      de: 'de_DE',
      ko: 'ko_KR',
      vi: 'vi_VN',
      zh: 'zh_CN',
      ja: 'ja_JP'
    };

    ensureMetaTag('meta[property="og:locale"]', { property: 'og:locale', content: localeMap[currentLang] || 'en_US' });
    Object.keys(localeMap).forEach((lang) => {
      if (lang === currentLang) return;
      ensureMetaTag(`meta[property="og:locale:alternate"][content="${localeMap[lang]}"]`, {
        property: 'og:locale:alternate',
        content: localeMap[lang]
      });
    });

    ensureMetaTag('meta[name="twitter:card"]', { name: 'twitter:card', content: 'summary_large_image' });
    ensureMetaTag('meta[name="twitter:title"]', { name: 'twitter:title', content: document.title });
    ensureMetaTag('meta[name="twitter:description"]', { name: 'twitter:description', content: description });
    ensureMetaTag('meta[name="twitter:image"]', { name: 'twitter:image', content: ogImageUrl });
    ensureMetaTag('meta[name="twitter:image:alt"]', { name: 'twitter:image:alt', content: 'TopHeroes Guide cover image' });

    ensureJsonLd('seo-jsonld', {
      '@context': 'https://schema.org',
      '@type': 'WebPage',
      '@id': canonicalUrl + '#webpage',
      name: document.title,
      url: canonicalUrl,
      inLanguage: currentLang,
      description: description,
      image: ogImageUrl,
      isPartOf: {
        '@type': 'WebSite',
        name: siteName,
        url: siteUrl
      }
    });

    ensureJsonLd('seo-breadcrumb', {
      '@context': 'https://schema.org',
      '@type': 'BreadcrumbList',
      itemListElement: [
        {
          '@type': 'ListItem',
          position: 1,
          name: 'Home',
          item: homeUrl
        },
        {
          '@type': 'ListItem',
          position: 2,
          name: document.title,
          item: canonicalUrl
        }
      ]
    });
  }

  function getNavPath(lang) {
    if (lang === 'ko') return '/ko/html/nav.html';
    if (lang === 'de') return '/de/html/nav.html';
    if (lang === 'vi') return '/vi/html/nav.html';
    if (lang === 'tc') return '/tc/html/nav.html';
    if (lang === 'zh') return '/zh/html/nav.html';
    if (lang === 'ja') return '/ja/html/nav.html';
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
    ensureSeoTags();

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
