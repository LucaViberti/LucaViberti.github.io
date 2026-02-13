// Language Switcher - Gestisce il cambio lingua e i link tra versioni
const LangSwitcher = {
  STORAGE_KEY: 'topheroes-lang',
  DEFAULT_LANG: 'en',
  LANGS: ['en', 'de', 'ko', 'vi', 'zh', 'tc', 'ja'],

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
  
  // Converte un path da una lingua all'altra
  switchPath: function(targetLang) {
    const currentPath = window.location.pathname;
    const currentLang = this.getCurrentLang();
    
    if (currentLang === targetLang) return currentPath;
    
    // Rimuovi i prefissi di lingua dal path
    let basePath = currentPath;
    if (this.hasLangPrefix(basePath, 'de')) {
      basePath = basePath.slice(3);
    } else if (this.hasLangPrefix(basePath, 'ko')) {
      basePath = basePath.slice(3);
    } else if (this.hasLangPrefix(basePath, 'vi')) {
      basePath = basePath.slice(3);
    } else if (this.hasLangPrefix(basePath, 'zh')) {
      basePath = basePath.slice(3);
    } else if (this.hasLangPrefix(basePath, 'tc')) {
      basePath = basePath.slice(3);
    } else if (this.hasLangPrefix(basePath, 'ja')) {
      basePath = basePath.slice(3);
    }
    
    // Aggiungi il prefisso della lingua target
    if (targetLang === 'de') {
      if (basePath === '' || basePath === '/index.html' || basePath === '/') {
        return '/de/index.html';
      }
      return '/de' + (basePath.startsWith('/') ? basePath : '/' + basePath);
    } else if (targetLang === 'ko') {
      if (basePath === '' || basePath === '/index.html' || basePath === '/') {
        return '/ko/index.html';
      }
      return '/ko' + (basePath.startsWith('/') ? basePath : '/' + basePath);
    } else if (targetLang === 'vi') {
      if (basePath === '' || basePath === '/index.html' || basePath === '/') {
        return '/vi/index.html';
      }
      return '/vi' + (basePath.startsWith('/') ? basePath : '/' + basePath);
    } else if (targetLang === 'zh') {
      if (basePath === '' || basePath === '/index.html' || basePath === '/') {
        return '/zh/index.html';
      }
      return '/zh' + (basePath.startsWith('/') ? basePath : '/' + basePath);
    } else if (targetLang === 'tc') {
      if (basePath === '' || basePath === '/index.html' || basePath === '/') {
        return '/tc/index.html';
      }
      return '/tc' + (basePath.startsWith('/') ? basePath : '/' + basePath);
    } else if (targetLang === 'ja') {
      if (basePath === '' || basePath === '/index.html' || basePath === '/') {
        return '/ja/index.html';
      }
      return '/ja' + (basePath.startsWith('/') ? basePath : '/' + basePath);
    } else {
      // en - ritorna il basePath senza prefisso
      if (basePath === '' || basePath === '/') return '/index.html';
      return basePath.startsWith('/') ? basePath : '/' + basePath;
    }
  },
  
  // Cambia lingua e naviga
  switchLanguage: function(targetLang) {
    this.setPreferredLang(targetLang);
    const newPath = this.switchPath(targetLang);
    window.location.href = newPath;
  },
  
  // Crea il nuovo selettore moderno per l'header
  createHeaderSelector: function() {
    const currentLang = this.getCurrentLang();
    const isEN = currentLang === 'en';
    const isDE = currentLang === 'de';
    const isKO = currentLang === 'ko';
    const isVI = currentLang === 'vi';
    const isZH = currentLang === 'zh';
    const isTC = currentLang === 'tc';
    const isJA = currentLang === 'ja';
    
    return `
      <a href="#" onclick="LangSwitcher.switchLanguage('en'); return false;" class="lang-btn ${isEN ? 'active' : ''}">
        <span class="lang-flag">🇬🇧</span>
        <span>English</span>
      </a>
      <a href="#" onclick="LangSwitcher.switchLanguage('de'); return false;" class="lang-btn ${isDE ? 'active' : ''}">
        <span class="lang-flag">🇩🇪</span>
        <span>Deutsch</span>
      </a>
      <a href="#" onclick="LangSwitcher.switchLanguage('ko'); return false;" class="lang-btn ${isKO ? 'active' : ''}">
        <span class="lang-flag">🇰🇷</span>
        <span>한국어</span>
      </a>
      <a href="#" onclick="LangSwitcher.switchLanguage('vi'); return false;" class="lang-btn ${isVI ? 'active' : ''}">
        <span class="lang-flag">🇻🇳</span>
        <span>Tiếng Việt</span>
      </a>
      <a href="#" onclick="LangSwitcher.switchLanguage('zh'); return false;" class="lang-btn ${isZH ? 'active' : ''}">
        <span class="lang-flag">🇨🇳</span>
        <span>中文 (简)</span>
      </a>
      <a href="#" onclick="LangSwitcher.switchLanguage('tc'); return false;" class="lang-btn ${isTC ? 'active' : ''}">
        <span class="lang-flag">🇭🇰</span>
        <span>中文 (繁)</span>
      </a>
      <a href="#" onclick="LangSwitcher.switchLanguage('ja'); return false;" class="lang-btn ${isJA ? 'active' : ''}">
        <span class="lang-flag">🇯🇵</span>
        <span>日本語</span>
      </a>
    `;
  },
  
  // Inizializza il nuovo selector nell'header
  initHeaderSelector: function(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
      element.innerHTML = this.createHeaderSelector();
    }
  },
  
  // Crea un selettore fisso in alto alla pagina
  createFixedSelector: function() {
    // Rimuovi selettore esistente se presente
    const existing = document.getElementById('lang-switcher-fixed');
    if (existing) existing.remove();
    
    const currentLang = this.getCurrentLang();
    const isEN = currentLang === 'en';
    const isDE = currentLang === 'de';
    const isKO = currentLang === 'ko';
    const isVI = currentLang === 'vi';
    const isZH = currentLang === 'zh';
    const isTC = currentLang === 'tc';
    const isJA = currentLang === 'ja';
    
    const container = document.createElement('div');
    container.id = 'lang-switcher-fixed';
    container.innerHTML = `
      <style>
        #lang-switcher-fixed {
          position: fixed;
          top: 10px;
          right: 10px;
          z-index: 9999;
          display: flex;
          flex-wrap: wrap;
          gap: 5px;
          max-width: 380px;
          background: rgba(30, 37, 65, 0.95);
          backdrop-filter: blur(10px);
          padding: 6px 8px;
          border-radius: 12px;
          box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
          border: 1px solid rgba(41, 171, 224, 0.3);
        }
        
        #lang-switcher-fixed .lang-btn-fixed {
          display: inline-flex;
          align-items: center;
          gap: 4px;
          padding: 5px 9px;
          border-radius: 8px;
          background: transparent;
          border: 2px solid transparent;
          color: #b0b6c7;
          font-size: 0.8rem;
          font-weight: 500;
          text-decoration: none;
          cursor: pointer;
          transition: all 0.3s ease;
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        }
        
        #lang-switcher-fixed .lang-btn-fixed:hover {
          background: rgba(41, 171, 224, 0.2);
          color: #fff;
          transform: scale(1.05);
        }
        
        #lang-switcher-fixed .lang-btn-fixed.active {
          background: linear-gradient(135deg, #29abe0, #7dd3fc);
          border-color: #29abe0;
          color: #fff;
          font-weight: 600;
          box-shadow: 0 2px 8px rgba(41, 171, 224, 0.4);
        }
        
        #lang-switcher-fixed .lang-flag {
          font-size: 1rem;
          line-height: 1;
        }
        
        @media (max-width: 640px) {
          #lang-switcher-fixed {
            top: 5px;
            right: 5px;
            padding: 5px 7px;
            gap: 4px;
            max-width: 280px;
          }
          #lang-switcher-fixed .lang-btn-fixed {
            padding: 4px 7px;
            font-size: 0.75rem;
            gap: 3px;
          }
          #lang-switcher-fixed .lang-btn-fixed span:not(.lang-flag) {
            display: none;
          }
          #lang-switcher-fixed .lang-flag {
            font-size: 0.95rem;
          }
        }
      </style>
      <a href="#" onclick="LangSwitcher.switchLanguage('en'); return false;" class="lang-btn-fixed ${isEN ? 'active' : ''}">
        <span class="lang-flag">🇬🇧</span>
        <span>EN</span>
      </a>
      <a href="#" onclick="LangSwitcher.switchLanguage('de'); return false;" class="lang-btn-fixed ${isDE ? 'active' : ''}">
        <span class="lang-flag">🇩🇪</span>
        <span>DE</span>
      </a>
      <a href="#" onclick="LangSwitcher.switchLanguage('ko'); return false;" class="lang-btn-fixed ${isKO ? 'active' : ''}">
        <span class="lang-flag">🇰🇷</span>
        <span>KO</span>
      </a>
      <a href="#" onclick="LangSwitcher.switchLanguage('vi'); return false;" class="lang-btn-fixed ${isVI ? 'active' : ''}">
        <span class="lang-flag">🇻🇳</span>
        <span>VI</span>
      </a>
      <a href="#" onclick="LangSwitcher.switchLanguage('zh'); return false;" class="lang-btn-fixed ${isZH ? 'active' : ''}">
        <span class="lang-flag">🇨🇳</span>
        <span>ZH</span>
      </a>
      <a href="#" onclick="LangSwitcher.switchLanguage('tc'); return false;" class="lang-btn-fixed ${isTC ? 'active' : ''}">
        <span class="lang-flag">🇭🇰</span>
        <span>TC</span>
      </a>
      <a href="#" onclick="LangSwitcher.switchLanguage('ja'); return false;" class="lang-btn-fixed ${isJA ? 'active' : ''}">
        <span class="lang-flag">🇯🇵</span>
        <span>JA</span>
      </a>
    `;
    
    document.body.appendChild(container);
  }
};

// Inizializzazione automatica del selettore fisso quando la pagina si carica
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', function() {
    LangSwitcher.createFixedSelector();
  });
} else {
  LangSwitcher.createFixedSelector();
}

// Forza creazione dopo 100ms se non già presente (fallback)
setTimeout(function() {
  if (!document.getElementById('lang-switcher-fixed')) {
    LangSwitcher.createFixedSelector();
  }
}, 100);
