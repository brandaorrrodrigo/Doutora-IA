// Configuracao Centralizada - Doutora IA
// Este arquivo deve ser incluido antes de qualquer outro JS

window.DoutoraIA = window.DoutoraIA || {};

// Detecta automaticamente a URL da API baseado no ambiente
window.DoutoraIA.API_URL = (function() {
    const hostname = window.location.hostname;

    // Desenvolvimento local
    if (hostname === 'localhost' || hostname === '127.0.0.1') {
        return 'http://localhost:8080';
    }

    // Railway
    if (window.location.origin.includes('railway.app')) {
        return 'https://doutora-ia-production.up.railway.app';
    }

    // Producao (mesmo dominio)
    return window.location.origin;
})();

// Versao da aplicacao
window.DoutoraIA.VERSION = '1.0.0';

// Debug mode
window.DoutoraIA.DEBUG = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';

// Funcoes utilitarias
window.DoutoraIA.utils = {
    // Formatar moeda brasileira
    formatCurrency: function(value) {
        return 'R$ ' + value.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    },

    // Formatar data brasileira
    formatDate: function(dateString) {
        return new Date(dateString).toLocaleDateString('pt-BR');
    },

    // Formatar data e hora
    formatDateTime: function(dateString) {
        return new Date(dateString).toLocaleString('pt-BR');
    },

    // Log apenas em modo debug
    log: function(...args) {
        if (window.DoutoraIA.DEBUG) {
            console.log('[DoutoraIA]', ...args);
        }
    }
};

// Autenticacao
window.DoutoraIA.auth = {
    getAccessToken: function() {
        return localStorage.getItem('access_token');
    },

    getRefreshToken: function() {
        return localStorage.getItem('refresh_token');
    },

    saveTokens: function(accessToken, refreshToken) {
        localStorage.setItem('access_token', accessToken);
        localStorage.setItem('refresh_token', refreshToken);
    },

    clearTokens: function() {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
    },

    isLoggedIn: function() {
        return !!this.getAccessToken();
    },

    logout: function() {
        this.clearTokens();
        window.location.href = '/login.html';
    }
};

// Log da configuracao em modo debug
if (window.DoutoraIA.DEBUG) {
    console.log('[DoutoraIA] Config loaded:', {
        API_URL: window.DoutoraIA.API_URL,
        VERSION: window.DoutoraIA.VERSION,
        DEBUG: window.DoutoraIA.DEBUG
    });
}
