// Language Switcher - Gestisce il cambio lingua e i link tra versioni
const LangSwitcher = {
  STORAGE_KEY: 'topheroes-lang',
  DEFAULT_LANG: 'en',
  LANGS: ['en', 'de'],
  
  // Rileva la lingua corrente dal path
  getCurrentLang: function() {
    const path = window.location.pathname;
    return path.startsWith('/de/') ? 'de' : 'en';
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
    
    if (targetLang === 'de') {
      // en → de
      if (currentPath === '/' || currentPath === '/index.html') {
        return '/de/index.html';
      }
      return '/de' + currentPath;
    } else {
      // de → en
      if (currentPath === '/de/index.html') {
        return '/index.html';
      }
      return currentPath.replace('/de/', '/');
    }
  },
  
  // Cambia lingua e naviga
  switchLanguage: function(targetLang) {
    this.setPreferredLang(targetLang);
    const newPath = this.switchPath(targetLang);
    window.location.href = newPath;
  },
  
  // Crea il markup del language selector
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
      </div>
    `;
  },
  
  // Inizializza il selector in un elemento
  init: function(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
      element.innerHTML += this.createSelector();
    }
  },
  
  // Redirect automatico se esiste una preferenza e siamo sulla homepage
  autoRedirectIfNeeded: function() {
    const currentLang = this.getCurrentLang();
    const preferredLang = this.getPreferredLang();
    const isHomepage = window.location.pathname === '/' || window.location.pathname === '/index.html' || window.location.pathname === '/de/index.html';
    
    if (isHomepage && currentLang !== preferredLang) {
      const newPath = this.switchPath(preferredLang);
      window.location.href = newPath;
    }
  }
};

// Esegui autoRedirect al caricamento se necessario
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', function() {
    // Commenta se non vuoi redirect automatico
    // LangSwitcher.autoRedirectIfNeeded();
  });
} else {
  // LangSwitcher.autoRedirectIfNeeded();
}
