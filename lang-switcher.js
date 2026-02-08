// Language Switcher - Gestisce il cambio lingua e i link tra versioni
const LangSwitcher = {
  STORAGE_KEY: 'topheroes-lang',
  DEFAULT_LANG: 'en',
  LANGS: ['en', 'de', 'ko'],
  
  // Rileva la lingua corrente dal path
  getCurrentLang: function() {
    const path = window.location.pathname;
    if (path.startsWith('/de/')) return 'de';
    if (path.startsWith('/ko/')) return 'ko';
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
    
    // Primo, rimuovi i prefissi di lingua dal path
    let basePath = currentPath;
    if (basePath.startsWith('/de/')) {
      basePath = basePath.slice(3);
    } else if (basePath.startsWith('/ko/')) {
      basePath = basePath.slice(3);
    }
    
    // Aggiungi il prefisso della lingua target
    if (targetLang === 'de') {
      if (basePath === '' || basePath === '/index.html') {
        return '/de/index.html';
      }
      return '/de' + (basePath.startsWith('/') ? basePath : '/' + basePath);
    } else if (targetLang === 'ko') {
      if (basePath === '' || basePath === '/index.html') {
        return '/ko/index.html';
      }
      return '/ko' + (basePath.startsWith('/') ? basePath : '/' + basePath);
    } else {
      // en - ritorna il basePath senza prefisso
      if (basePath === '') return '/index.html';
      return basePath.startsWith('/') ? basePath : '/' + basePath;
    }
  },
  
  // Cambia lingua e naviga
  switchLanguage: function(targetLang) {
    this.setPreferredLang(targetLang);
    const newPath = this.switchPath(targetLang);
    window.location.href = newPath;
  },
  
  // Crea il markup del language selector (vecchio stile per footer)
  createSelector: function() {
    const currentLang = this.getCurrentLang();
    return `
      <div class="lang-selector" style="text-align: center; padding: 10px; border-top: 1px solid #ddd; margin-top: 10px; font-size: 14px;">
        <span style="margin-right: 15px;">
          <strong>Language:</strong>
        </span>
        <a href="#" onclick="LangSwitcher.switchLanguage('en'); return false;" style="margin: 0 8px; text-decoration: none; ${currentLang === 'en' ? 'font-weight: bold; color: #0066cc;' : 'color: #666;'}">
          🇬🇧 English
        </a>
        <span style="color: #ccc;">|</span>
        <a href="#" onclick="LangSwitcher.switchLanguage('de'); return false;" style="margin: 0 8px; text-decoration: none; ${currentLang === 'de' ? 'font-weight: bold; color: #0066cc;' : 'color: #666;'}">
          🇩🇪 Deutsch
        </a>
        <span style="color: #ccc;">|</span>
        <a href="#" onclick="LangSwitcher.switchLanguage('ko'); return false;" style="margin: 0 8px; text-decoration: none; ${currentLang === 'ko' ? 'font-weight: bold; color: #0066cc;' : 'color: #666;'}">
          🇰🇷 한국어
        </a>
      </div>
    `;
  },
  
  // Crea il nuovo selettore moderno per l'header
  createHeaderSelector: function() {
    const currentLang = this.getCurrentLang();
    const isEN = currentLang === 'en';
    const isDE = currentLang === 'de';
    const isKO = currentLang === 'ko';
    
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
    `;
  },
  
  // Inizializza il selector in un elemento (vecchio stile)
  init: function(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
      element.innerHTML += this.createSelector();
    }
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
          gap: 8px;
          background: rgba(30, 37, 65, 0.95);
          backdrop-filter: blur(10px);
          padding: 8px 12px;
          border-radius: 12px;
          box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
          border: 1px solid rgba(41, 171, 224, 0.3);
        }
        
        #lang-switcher-fixed .lang-btn-fixed {
          display: inline-flex;
          align-items: center;
          gap: 6px;
          padding: 6px 12px;
          border-radius: 8px;
          background: transparent;
          border: 2px solid transparent;
          color: #b0b6c7;
          font-size: 0.85rem;
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
          font-size: 1.1rem;
          line-height: 1;
        }
        
        @media (max-width: 640px) {
          #lang-switcher-fixed {
            top: 5px;
            right: 5px;
            padding: 6px 10px;
            gap: 6px;
          }
          #lang-switcher-fixed .lang-btn-fixed {
            padding: 5px 8px;
            font-size: 0.8rem;
          }
          #lang-switcher-fixed .lang-btn-fixed span:not(.lang-flag) {
            display: none;
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
    `;
    
    document.body.appendChild(container);
  },
  
  // Redirect automatico se esiste una preferenza e siamo sulla homepage
  autoRedirectIfNeeded: function() {
    const currentLang = this.getCurrentLang();
    const preferredLang = this.getPreferredLang();
    const isHomepage = window.location.pathname === '/' || window.location.pathname === '/index.html' || window.location.pathname === '/de/index.html' || window.location.pathname === '/ko/index.html';
    
    if (isHomepage && currentLang !== preferredLang) {
      const newPath = this.switchPath(preferredLang);
      window.location.href = newPath;
    }
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
