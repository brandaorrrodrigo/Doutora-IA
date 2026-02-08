// ========== CONFIGURAÇÃO LOCAL ==========
// URL da API LOCAL
const API_URL = 'http://localhost:8000';

// ========== FUNÇÕES UTILITÁRIAS ==========

function showAlert(message, type = 'danger') {
    const alertContainer = document.getElementById('alertContainer');
    if (!alertContainer) {
        console.error('Alert container not found');
        return;
    }

    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;

    alertContainer.appendChild(alertDiv);

    setTimeout(() => {
        alertDiv.remove();
    }, 5000);
}

function setLoadingState(formId, isLoading) {
    const form = document.getElementById(formId);
    const submitBtn = form.querySelector('button[type="submit"]');
    const inputs = form.querySelectorAll('input');

    inputs.forEach(input => input.disabled = isLoading);
    submitBtn.disabled = isLoading;
    submitBtn.innerHTML = isLoading ?
        '<span class="spinner-border spinner-border-sm me-2"></span>Carregando...' :
        submitBtn.dataset.originalText || 'Enviar';

    if (!isLoading && !submitBtn.dataset.originalText) {
        submitBtn.dataset.originalText = submitBtn.innerHTML;
    }
}

// ========== LOGIN ==========

async function handleLogin(e) {
    e.preventDefault();

    const email = document.getElementById('loginEmail').value;
    const password = document.getElementById('loginPassword').value;
    const rememberMe = document.getElementById('rememberMe').checked;

    if (!email || !password) {
        showAlert('Por favor, preencha todos os campos.');
        return;
    }

    setLoadingState('loginForm', true);

    try {
        const response = await fetch(`${API_URL}/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email, password })
        });

        const data = await response.json();

        if (response.ok) {
            // Salvar tokens
            if (rememberMe) {
                localStorage.setItem('access_token', data.access_token);
                if (data.refresh_token) {
                    localStorage.setItem('refresh_token', data.refresh_token);
                }
            } else {
                sessionStorage.setItem('access_token', data.access_token);
                if (data.refresh_token) {
                    sessionStorage.setItem('refresh_token', data.refresh_token);
                }
            }

            showAlert('Login realizado com sucesso!', 'success');

            // Redirecionar baseado no tipo de usuário
            setTimeout(() => {
                if (data.user_type === 'lawyer') {
                    window.location.href = '/dashboard-advogado.html';
                } else {
                    window.location.href = '/dashboard.html';
                }
            }, 1000);
        } else {
            showAlert(data.detail || 'Erro ao fazer login. Verifique suas credenciais.');
        }
    } catch (error) {
        console.error('Login error:', error);
        showAlert('Erro ao conectar com o servidor. Verifique sua conexão.');
    } finally {
        setLoadingState('loginForm', false);
    }
}

// ========== REGISTRO ==========

async function handleRegister(e) {
    e.preventDefault();

    const name = document.getElementById('registerName').value;
    const email = document.getElementById('registerEmail').value;
    const password = document.getElementById('registerPassword').value;

    if (!name || !email || !password) {
        showAlert('Por favor, preencha todos os campos.');
        return;
    }

    if (password.length < 8) {
        showAlert('A senha deve ter pelo menos 8 caracteres.');
        return;
    }

    setLoadingState('registerForm', true);

    try {
        const response = await fetch(`${API_URL}/auth/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ name, email, password })
        });

        const data = await response.json();

        if (response.ok) {
            showAlert('Conta criada com sucesso! Verifique seu email.', 'success');

            // Limpar formulário
            document.getElementById('registerForm').reset();

            // Voltar para o login após 2 segundos
            setTimeout(() => {
                document.getElementById('registerTab').classList.remove('active');
                document.getElementById('loginTab').classList.add('active');
                document.getElementById('register').classList.remove('show', 'active');
                document.getElementById('login').classList.add('show', 'active');
            }, 2000);
        } else {
            showAlert(data.detail || 'Erro ao criar conta. Tente novamente.');
        }
    } catch (error) {
        console.error('Register error:', error);
        showAlert('Erro ao conectar com o servidor. Verifique sua conexão.');
    } finally {
        setLoadingState('registerForm', false);
    }
}

// ========== RECUPERAR SENHA ==========

async function handleForgotPassword(e) {
    e.preventDefault();

    const email = document.getElementById('forgotEmail').value;

    if (!email) {
        showAlert('Por favor, digite seu email.');
        return;
    }

    setLoadingState('forgotPasswordForm', true);

    try {
        const response = await fetch(`${API_URL}/auth/forgot-password`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email })
        });

        const data = await response.json();

        if (response.ok) {
            showAlert('Email de recuperação enviado! Verifique sua caixa de entrada.', 'success');
            document.getElementById('forgotPasswordForm').reset();
        } else {
            showAlert(data.detail || 'Erro ao enviar email de recuperação.');
        }
    } catch (error) {
        console.error('Forgot password error:', error);
        showAlert('Erro ao conectar com o servidor. Verifique sua conexão.');
    } finally {
        setLoadingState('forgotPasswordForm', false);
    }
}

// ========== VERIFICAR AUTENTICAÇÃO ==========

async function checkAuth() {
    const token = localStorage.getItem('access_token') || sessionStorage.getItem('access_token');

    if (!token) {
        return false;
    }

    try {
        const response = await fetch(`${API_URL}/auth/me`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (response.ok) {
            const data = await response.json();
            // Redirecionar se já estiver logado
            if (data.user_type === 'lawyer') {
                window.location.href = '/dashboard-advogado.html';
            } else {
                window.location.href = '/dashboard.html';
            }
            return true;
        }
    } catch (error) {
        console.error('Auth check error:', error);
    }

    return false;
}

// ========== INICIALIZAÇÃO ==========

document.addEventListener('DOMContentLoaded', function() {
    // Verificar se já está autenticado
    checkAuth();

    // Adicionar event listeners
    const loginForm = document.getElementById('loginForm');
    const registerForm = document.getElementById('registerForm');
    const forgotPasswordForm = document.getElementById('forgotPasswordForm');

    if (loginForm) {
        loginForm.addEventListener('submit', handleLogin);
    }

    if (registerForm) {
        registerForm.addEventListener('submit', handleRegister);
    }

    if (forgotPasswordForm) {
        forgotPasswordForm.addEventListener('submit', handleForgotPassword);
    }

    console.log('[LOCAL] Doutora IA - Sistema de Login inicializado');
    console.log(`[LOCAL] API: ${API_URL}`);
});
