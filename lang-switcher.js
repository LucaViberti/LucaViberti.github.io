// Language Switcher - Gestisce il cambio lingua e i link tra versioni
const LangSwitcher = {
  STORAGE_KEY: 'topheroes-lang',
  DEFAULT_LANG: 'en',
  LANGS: ['en', 'de', 'ko', 'vi', 'zh', 'tc', 'ja'],
  LANG_META: {
    en: { label: 'English', short: 'EN', flag: '🇬🇧' },
    de: { label: 'Deutsch', short: 'DE', flag: '🇩🇪' },
    ko: { label: '한국어', short: 'KO', flag: '🇰🇷' },
    vi: { label: 'Tiếng Việt', short: 'VI', flag: '🇻🇳' },
    zh: { label: '中文 (简)', short: 'ZH', flag: '🇨🇳' },
    tc: { label: '中文 (繁)', short: 'TC', flag: '🇭🇰' },
    ja: { label: '日本語', short: 'JA', flag: '🇯🇵' }
  },

  hasLangPrefix: function(pathname, lang) {
    const path = (pathname || '').toLowerCase();
    return path === `/${lang}` || path.startsWith(`/${lang}/`);
  },

  // Rileva la lingua corrente dal path
  getCurrentLang: function() {
    const path = window.location.pathname.toLowerCase();
    if (this.hasLangPrefix(path, 'de')) return 'de';
    if (this.hasLangPrefix(path, 'ko')) return 'ko';
    if (this.hasLangPrefix(path, 'vi')) return 'vi';
    if (this.hasLangPrefix(path, 'zh')) return 'zh';
    if (this.hasLangPrefix(path, 'tc')) return 'tc';
    if (this.hasLangPrefix(path, 'ja')) return 'ja';
    return 'en';
  },

  // Salva la lingua preferita
  setPreferredLang: function(lang) {
    if (this.LANGS.includes(lang)) {
      localStorage.setItem(this.STORAGE_KEY, lang);
    }
  },

  // Legge la lingua preferita
  getPreferredLang: function() {
    return localStorage.getItem(this.STORAGE_KEY) || this.DEFAULT_LANG;
  },

  stripLangPrefix: function(pathname) {
    let basePath = pathname || '';
    if (this.hasLangPrefix(basePath, 'de')) return basePath.slice(3);
    if (this.hasLangPrefix(basePath, 'ko')) return basePath.slice(3);
    if (this.hasLangPrefix(basePath, 'vi')) return basePath.slice(3);
    if (this.hasLangPrefix(basePath, 'zh')) return basePath.slice(3);
    if (this.hasLangPrefix(basePath, 'tc')) return basePath.slice(3);
    if (this.hasLangPrefix(basePath, 'ja')) return basePath.slice(3);
    return basePath;
  },

  // Converte un path da una lingua all'altra
  switchPath: function(targetLang) {
    const currentPath = window.location.pathname;
    const currentLang = this.getCurrentLang();

    if (currentLang === targetLang) return currentPath;

    const basePath = this.stripLangPrefix(currentPath);

    if (targetLang === 'en') {
      if (basePath === '' || basePath === '/') return '/index.html';
      return basePath.startsWith('/') ? basePath : '/' + basePath;
    }

    if (basePath === '' || basePath === '/index.html' || basePath === '/') {
      return `/${targetLang}/index.html`;
    }
    return `/${targetLang}` + (basePath.startsWith('/') ? basePath : '/' + basePath);
  },

  // Cambia lingua e naviga
  switchLanguage: function(targetLang) {
    this.setPreferredLang(targetLang);
    const newPath = this.switchPath(targetLang);
    window.location.href = newPath;
  },

  createLangOptionButtons: function(currentLang) {
    return this.LANGS.map((lang) => {
      const meta = this.LANG_META[lang];
      const active = currentLang === lang ? ' active' : '';
      return `
        <button type="button" class="th-lang-option${active}" data-lang="${lang}" role="option" aria-selected="${currentLang === lang ? 'true' : 'false'}">
          <span class="th-lang-flag" aria-hidden="true">${meta.flag}</span>
          <span class="th-lang-name">${meta.label}</span>
          <span class="th-lang-short">${meta.short}</span>
        </button>
      `;
    }).join('');
  },

  // Crea il selettore a tendina nell'header
  createHeaderSelector: function() {
    const currentLang = this.getCurrentLang();
    const currentMeta = this.LANG_META[currentLang] || this.LANG_META.en;

    return `
      <style>
        .header-lang-selector {
          position: relative;
          display: inline-flex;
          justify-content: center;
          margin-top: 10px;
          width: 100%;
          max-width: 340px;
        }

        .header-lang-selector .th-lang-toggle {
          width: 100%;
          display: inline-flex;
          align-items: center;
          justify-content: space-between;
          gap: 10px;
          padding: 10px 14px;
          border-radius: 12px;
          border: 1px solid rgba(41, 171, 224, 0.5);
          background: linear-gradient(180deg, rgba(41, 171, 224, 0.2), rgba(41, 171, 224, 0.08));
          color: #e8f6fd;
          font-weight: 600;
          font-size: 0.95rem;
          cursor: pointer;
          transition: border-color 0.2s ease, box-shadow 0.2s ease, background 0.2s ease;
        }

        .header-lang-selector .th-lang-toggle:hover,
        .header-lang-selector .th-lang-toggle:focus-visible {
          border-color: #7dd3fc;
          box-shadow: 0 0 0 3px rgba(41, 171, 224, 0.2);
          outline: none;
          background: linear-gradient(180deg, rgba(41, 171, 224, 0.28), rgba(41, 171, 224, 0.12));
        }

        .header-lang-selector .th-toggle-left {
          display: inline-flex;
          align-items: center;
          gap: 8px;
          min-width: 0;
        }

        .header-lang-selector .th-lang-flag {
          font-size: 1rem;
          line-height: 1;
          flex-shrink: 0;
        }

        .header-lang-selector .th-toggle-label {
          white-space: nowrap;
          overflow: hidden;
          text-overflow: ellipsis;
        }

        .header-lang-selector .th-caret {
          font-size: 0.8rem;
          opacity: 0.9;
          transition: transform 0.2s ease;
        }

        .header-lang-selector.open .th-caret {
          transform: rotate(180deg);
        }

        .header-lang-selector .th-lang-menu {
          position: absolute;
          top: calc(100% + 8px);
          left: 0;
          right: 0;
          background: #1c2133;
          border: 1px solid rgba(41, 171, 224, 0.35);
          border-radius: 12px;
          box-shadow: 0 10px 28px rgba(0, 0, 0, 0.35);
          padding: 6px;
          display: none;
          z-index: 1200;
          max-height: min(52vh, 320px);
          overflow-y: auto;
        }

        .header-lang-selector.open .th-lang-menu {
          display: block;
        }

        .header-lang-selector .th-lang-option {
          width: 100%;
          display: flex;
          align-items: center;
          gap: 10px;
          border: 0;
          background: transparent;
          color: #d1d7e5;
          border-radius: 9px;
          padding: 9px 10px;
          text-align: left;
          cursor: pointer;
          font-size: 0.9rem;
          font-weight: 500;
          transition: background 0.2s ease, color 0.2s ease;
        }

        .header-lang-selector .th-lang-option:hover,
        .header-lang-selector .th-lang-option:focus-visible {
          background: rgba(41, 171, 224, 0.18);
          color: #ffffff;
          outline: none;
        }

        .header-lang-selector .th-lang-option.active {
          background: linear-gradient(135deg, #29abe0, #7dd3fc);
          color: #ffffff;
          font-weight: 700;
        }

        .header-lang-selector .th-lang-option .th-lang-name {
          flex: 1;
          min-width: 0;
          white-space: nowrap;
          overflow: hidden;
          text-overflow: ellipsis;
        }

        .header-lang-selector .th-lang-option .th-lang-short {
          display: none;
          font-weight: 700;
          opacity: 0.9;
        }

        @media (max-width: 640px) {
          .header-lang-selector {
            max-width: 300px;
          }

          .header-lang-selector .th-lang-toggle {
            padding: 9px 12px;
            font-size: 0.9rem;
          }

          .header-lang-selector .th-toggle-label {
            font-size: 0.88rem;
          }

          .header-lang-selector .th-lang-option {
            padding: 10px;
            font-size: 0.88rem;
          }
        }
      </style>

      <button type="button" class="th-lang-toggle" aria-haspopup="listbox" aria-expanded="false" aria-label="Choose language">
        <span class="th-toggle-left">
          <span class="th-lang-flag" aria-hidden="true">${currentMeta.flag}</span>
          <span class="th-toggle-label">Language: ${currentMeta.label}</span>
        </span>
        <span class="th-caret" aria-hidden="true">▾</span>
      </button>

      <div class="th-lang-menu" role="listbox" aria-label="Language list">
        ${this.createLangOptionButtons(currentLang)}
      </div>
    `;
  },

  // Inizializza il selector nell'header
  initHeaderSelector: function(elementId) {
    const element = document.getElementById(elementId);
    if (!element) return;

    element.innerHTML = this.createHeaderSelector();
    const toggle = element.querySelector('.th-lang-toggle');
    const menu = element.querySelector('.th-lang-menu');
    const options = element.querySelectorAll('.th-lang-option');

    if (!toggle || !menu || !options.length) return;

    const closeMenu = () => {
      element.classList.remove('open');
      toggle.setAttribute('aria-expanded', 'false');
    };

    const openMenu = () => {
      element.classList.add('open');
      toggle.setAttribute('aria-expanded', 'true');
    };

    toggle.addEventListener('click', () => {
      const isOpen = element.classList.contains('open');
      if (isOpen) {
        closeMenu();
      } else {
        openMenu();
      }
    });

    options.forEach((btn) => {
      btn.addEventListener('click', () => {
        const lang = btn.getAttribute('data-lang');
        if (!lang) return;
        this.switchLanguage(lang);
      });
    });

    document.addEventListener('click', (event) => {
      if (!element.contains(event.target)) {
        closeMenu();
      }
    });

    document.addEventListener('keydown', (event) => {
      if (event.key === 'Escape') {
        closeMenu();
      }
    });
  },

  // Legacy: rimosso selettore fisso per evitare overlay sul contenuto
  createFixedSelector: function() {
    const existing = document.getElementById('lang-switcher-fixed');
    if (existing) existing.remove();
  }
};

// Espone il selettore in modo affidabile per i loader esterni.
window.LangSwitcher = LangSwitcher;
