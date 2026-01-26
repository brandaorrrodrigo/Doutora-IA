// Login e Autenticação - Doutora IA
// Detecta automaticamente a URL da API baseado no ambiente
const API_URL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? 'http://localhost:8080'
    : window.location.origin.includes('railway.app')
        ? 'https://doutora-ia-production.up.railway.app'
        : window.location.origin;

// ==========================================
// NAVEGAÇÃO ENTRE TABS
// ==========================================

function switchTab(tabName) {
    // Esconder todas as tabs
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });

    document.querySelectorAll('.tab').forEach(tab => {
        tab.classList.remove('active');
    });

    // Mostrar tab selecionada
    if (tabName === 'login') {
        document.getElementById('loginTab').classList.add('active');
        document.querySelectorAll('.tab')[0].classList.add('active');
    } else if (tabName === 'register') {
        document.getElementById('registerTab').classList.add('active');
        document.querySelectorAll('.tab')[1].classList.add('active');
    } else if (tabName === 'forgot') {
        document.getElementById('forgotPasswordSection').classList.add('active');
    }
}

function showForgotPassword() {
    switchTab('forgot');
    return false;
}

// ==========================================
// ALERTS
// ==========================================

function showAlert(message, type = 'info') {
    const alertContainer = document.getElementById('alertContainer');

    const alert = document.createElement('div');
    alert.className = `alert alert-${type} alert-dismissible fade show`;
    alert.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;

    alertContainer.innerHTML = '';
    alertContainer.appendChild(alert);

    // Auto-remover após 5 segundos
    setTimeout(() => {
        alert.remove();
    }, 5000);
}

// ==========================================
// LOCAL STORAGE
// ==========================================

function saveTokens(accessToken, refreshToken) {
    localStorage.setItem('access_token', accessToken);
    localStorage.setItem('refresh_token', refreshToken);
}

function getAccessToken() {
    return localStorage.getItem('access_token');
}

function getRefreshToken() {
    return localStorage.getItem('refresh_token');
}

function clearTokens() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
}

// ==========================================
// LOGIN
// ==========================================

document.getElementById('loginForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    const email = document.getElementById('loginEmail').value;
    const password = document.getElementById('loginPassword').value;
    const rememberMe = document.getElementById('rememberMe').checked;

    const btn = e.target.querySelector('button[type="submit"]');
    const originalText = btn.innerHTML;
    btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Entrando...';
    btn.disabled = true;

    try {
        const response = await fetch(`${API_URL}/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ email, password })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || 'Erro ao fazer login');
        }

        // Salvar tokens
        saveTokens(data.access_token, data.refresh_token);

        // Salvar email se "lembrar de mim"
        if (rememberMe) {
            localStorage.setItem('remembered_email', email);
        }

        showAlert('Login realizado com sucesso! Redirecionando...', 'success');

        // Redirecionar para dashboard
        setTimeout(() => {
            window.location.href = '/dashboard.html';
        }, 1000);

    } catch (error) {
        showAlert(error.message, 'danger');
        btn.innerHTML = originalText;
        btn.disabled = false;
    }
});

// ==========================================
// REGISTRO
// ==========================================

document.getElementById('registerForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    const name = document.getElementById('regName').value;
    const email = document.getElementById('regEmail').value;
    const oab = document.getElementById('regOab').value;
    const phone = document.getElementById('regPhone').value;
    const password = document.getElementById('regPassword').value;
    const passwordConfirm = document.getElementById('regPasswordConfirm').value;

    // Validar senhas
    if (password !== passwordConfirm) {
        showAlert('As senhas não coincidem', 'danger');
        return;
    }

    if (password.length < 6) {
        showAlert('A senha deve ter no mínimo 6 caracteres', 'danger');
        return;
    }

    const btn = e.target.querySelector('button[type="submit"]');
    const originalText = btn.innerHTML;
    btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Criando conta...';
    btn.disabled = true;

    try {
        const response = await fetch(`${API_URL}/auth/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                name,
                email,
                oab,
                phone,
                password,
                areas: [],
                cities: [],
                states: []
            })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || 'Erro ao criar conta');
        }

        // Salvar tokens
        saveTokens(data.access_token, data.refresh_token);

        showAlert('Conta criada com sucesso! Verifique seu email para ativar sua conta. Redirecionando...', 'success');

        // Redirecionar para dashboard
        setTimeout(() => {
            window.location.href = '/dashboard.html';
        }, 2000);

    } catch (error) {
        showAlert(error.message, 'danger');
        btn.innerHTML = originalText;
        btn.disabled = false;
    }
});

// ==========================================
// ESQUECI SENHA
// ==========================================

document.getElementById('forgotPasswordForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    const email = document.getElementById('forgotEmail').value;

    const btn = e.target.querySelector('button[type="submit"]');
    const originalText = btn.innerHTML;
    btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Enviando...';
    btn.disabled = true;

    try {
        const response = await fetch(`${API_URL}/auth/forgot-password`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ email })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || 'Erro ao enviar email');
        }

        showAlert('Se o email existir, você receberá instruções para resetar sua senha', 'success');

        // Voltar para login após 3 segundos
        setTimeout(() => {
            switchTab('login');
        }, 3000);

    } catch (error) {
        showAlert(error.message, 'danger');
    } finally {
        btn.innerHTML = originalText;
        btn.disabled = false;
    }
});

// ==========================================
// VERIFICAR SE JÁ ESTÁ LOGADO
// ==========================================

async function checkIfLoggedIn() {
    const token = getAccessToken();

    if (!token) {
        return;
    }

    try {
        const response = await fetch(`${API_URL}/auth/me`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (response.ok) {
            // Já está logado, redirecionar
            window.location.href = '/dashboard.html';
        } else {
            // Token inválido, limpar
            clearTokens();
        }
    } catch (error) {
        clearTokens();
    }
}

// ==========================================
// CARREGAR EMAIL SALVO
// ==========================================

function loadRememberedEmail() {
    const rememberedEmail = localStorage.getItem('remembered_email');
    if (rememberedEmail) {
        document.getElementById('loginEmail').value = rememberedEmail;
        document.getElementById('rememberMe').checked = true;
    }
}

// ==========================================
// INICIALIZAÇÃO
// ==========================================

document.addEventListener('DOMContentLoaded', () => {
    checkIfLoggedIn();
    loadRememberedEmail();
});
