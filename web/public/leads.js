// Marketplace de Leads - Doutora IA
// URL da API - usar producao enquanto desenvolve localmente
const API_URL = 'https://doutora-ia-production.up.railway.app';

let leadsData = [];
let currentLawyer = null;

// ==========================================
// AUTENTICAÇÃO
// ==========================================

function getAccessToken() {
    return localStorage.getItem('access_token');
}

function logout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    window.location.href = '/login.html';
}

async function checkAuth() {
    const token = getAccessToken();

    if (!token) {
        window.location.href = '/login.html';
        return false;
    }

    try {
        const response = await fetch(`${API_URL}/auth/me`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (!response.ok) {
            throw new Error('Token inválido');
        }

        currentLawyer = await response.json();
        return true;
    } catch (error) {
        logout();
        return false;
    }
}

// Carregar leads ao iniciar
document.addEventListener('DOMContentLoaded', async () => {
    // Verificar autenticação
    const isAuth = await checkAuth();

    if (isAuth) {
        carregarLeads();
        carregarEstatisticas();

        // Atualizar a cada 30 segundos
        setInterval(carregarLeads, 30000);
    }
});

async function carregarLeads(area = null) {
    try {
        const params = new URLSearchParams({
            limit: 20
        });

        if (area) params.append('area', area);

        const token = getAccessToken();
        const response = await fetch(`${API_URL}/marketplace/leads?${params}`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (!response.ok) {
            throw new Error('Erro ao carregar leads');
        }

        leadsData = await response.json();
        renderizarLeads(leadsData);

    } catch (error) {
        console.error('Erro:', error);
        document.getElementById('leadsList').innerHTML = `
            <div class="alert alert-warning">
                <i class="fas fa-exclamation-triangle"></i>
                Erro ao carregar leads. Verifique se a API está rodando.
            </div>
        `;
    }
}

async function carregarEstatisticas() {
    try {
        const token = getAccessToken();
        const response = await fetch(`${API_URL}/marketplace/estatisticas`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        const stats = await response.json();

        document.getElementById('statPendentes').textContent = stats.pendentes || 0;
        document.getElementById('statAceitos').textContent = stats.aceitos || 0;
        document.getElementById('statTaxa').textContent = stats.taxa_conversao + '%' || '0%';
        document.getElementById('statValor').textContent = `R$ ${(stats.valor_medio_honorarios || 0).toLocaleString('pt-BR')}`;

    } catch (error) {
        console.error('Erro ao carregar estatísticas:', error);
    }
}

function renderizarLeads(leads) {
    const container = document.getElementById('leadsList');

    if (leads.length === 0) {
        container.innerHTML = `
            <div class="alert alert-info text-center">
                <i class="fas fa-inbox"></i>
                <h4>Nenhum lead disponível no momento</h4>
                <p>Novos clientes qualificados aparecerão aqui automaticamente.</p>
            </div>
        `;
        return;
    }

    let html = '';

    leads.forEach(lead => {
        const scoreClass = lead.score_qualidade >= 80 ? 'score-alta' :
                          lead.score_qualidade >= 50 ? 'score-media' : 'score-baixa';

        const probClass = lead.probabilidade === 'alta' ? 'text-success' :
                         lead.probabilidade === 'media' ? 'text-warning' : 'text-danger';

        // Calcular tempo restante (mockup - em produção viria do backend)
        const horasRestantes = 47; // TODO: calcular real

        html += `
            <div class="lead-card quente">
                <span class="badge ${scoreClass} badge-score">
                    ${lead.score_qualidade}/100
                </span>

                <div class="row">
                    <div class="col-md-8">
                        <h4>
                            <i class="fas fa-user"></i> ${lead.cliente.nome}
                            ${lead.cliente.tem_email ? '<i class="fas fa-envelope text-success ms-2"></i>' : ''}
                            ${lead.cliente.tem_telefone ? '<i class="fas fa-phone text-success"></i>' : ''}
                        </h4>

                        <p class="mb-2">
                            <span class="badge bg-primary">${lead.area.toUpperCase()}</span>
                            ${lead.sub_area ? `<span class="badge bg-secondary">${lead.sub_area}</span>` : ''}
                            <span class="badge bg-${probClass.replace('text-', '')}">${lead.probabilidade.toUpperCase()}</span>
                        </p>

                        <p class="mb-2">
                            <strong>Descrição:</strong><br>
                            ${lead.descricao_resumida}
                        </p>

                        <p class="mb-1">
                            <i class="fas fa-map-marker-alt"></i> ${lead.cliente.cidade}
                        </p>

                        <p class="timer mb-0">
                            <i class="fas fa-clock"></i> Expira em ${horasRestantes}h
                        </p>
                    </div>

                    <div class="col-md-4 text-end">
                        <div class="valor-estimado mb-3">
                            R$ ${lead.valor_estimado.toLocaleString('pt-BR', {minimumFractionDigits: 2})}
                        </div>
                        <small class="text-muted">Honorários estimados</small>

                        <div class="mt-4">
                            <button class="btn btn-aceitar w-100 mb-2" onclick="aceitarLead(${lead.id})">
                                <i class="fas fa-check"></i> ACEITAR LEAD
                            </button>

                            <button class="btn btn-rejeitar w-100" onclick="rejeitarLead(${lead.id})">
                                <i class="fas fa-times"></i> Rejeitar
                            </button>
                        </div>

                        ${lead.relatorio_pago ? '<span class="badge bg-success mt-2"><i class="fas fa-check-circle"></i> Cliente Pagou R$ 7</span>' : ''}
                    </div>
                </div>
            </div>
        `;
    });

    container.innerHTML = html;
}

async function aceitarLead(caseId) {
    if (!confirm('Aceitar este lead? Você receberá os dados de contato do cliente e terá 24h para entrar em contato.')) {
        return;
    }

    try {
        const token = getAccessToken();
        const response = await fetch(`${API_URL}/marketplace/leads/acao`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({
                case_id: caseId,
                acao: 'aceitar'
            })
        });

        if (!response.ok) {
            throw new Error('Erro ao aceitar lead');
        }

        const resultado = await response.json();

        if (resultado.erro) {
            alert(resultado.erro);
            return;
        }

        // Mostrar dados do cliente
        mostrarDadosCliente(resultado);

        // Remover lead da lista
        carregarLeads();
        carregarEstatisticas();

    } catch (error) {
        console.error('Erro:', error);
        alert('Erro ao aceitar lead. Tente novamente.');
    }
}

async function rejeitarLead(caseId) {
    const motivo = prompt('Por que está rejeitando este lead? (opcional)');

    if (motivo === null) return; // Cancelou

    try {
        const token = getAccessToken();
        const response = await fetch(`${API_URL}/marketplace/leads/acao`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({
                case_id: caseId,
                acao: 'rejeitar',
                motivo: motivo
            })
        });

        if (!response.ok) {
            throw new Error('Erro ao rejeitar lead');
        }

        alert('Lead rejeitado. Ele será oferecido a outro advogado.');

        // Atualizar lista
        carregarLeads();
        carregarEstatisticas();

    } catch (error) {
        console.error('Erro:', error);
        alert('Erro ao rejeitar lead. Tente novamente.');
    }
}

function mostrarDadosCliente(resultado) {
    const { cliente, caso } = resultado;

    const html = `
        <div class="alert alert-success">
            <h4><i class="fas fa-check-circle"></i> Lead Aceito com Sucesso!</h4>
            <p>Entre em contato com o cliente nas próximas 24 horas.</p>
        </div>

        <h5>Dados do Cliente</h5>
        <table class="table table-bordered">
            <tr>
                <th>Nome:</th>
                <td>${cliente.nome}</td>
            </tr>
            <tr>
                <th>Email:</th>
                <td>
                    <a href="mailto:${cliente.email}">${cliente.email}</a>
                    <button class="btn btn-sm btn-outline-primary" onclick="copiarTexto('${cliente.email}')">
                        <i class="fas fa-copy"></i> Copiar
                    </button>
                </td>
            </tr>
            <tr>
                <th>Telefone/WhatsApp:</th>
                <td>
                    ${cliente.telefone}
                    <a href="https://wa.me/${cliente.telefone.replace(/\D/g, '')}" target="_blank" class="btn btn-sm btn-success">
                        <i class="fab fa-whatsapp"></i> Abrir WhatsApp
                    </a>
                </td>
            </tr>
            ${cliente.cpf ? `<tr><th>CPF:</th><td>${cliente.cpf}</td></tr>` : ''}
        </table>

        <h5>Detalhes do Caso</h5>
        <p><strong>Descrição:</strong></p>
        <p>${caso.descricao}</p>

        <p><strong>Probabilidade:</strong> <span class="badge bg-success">${caso.probabilidade.toUpperCase()}</span></p>

        ${caso.relatorio_url ? `
            <a href="${caso.relatorio_url}" target="_blank" class="btn btn-primary">
                <i class="fas fa-file-pdf"></i> Baixar Relatório Completo
            </a>
        ` : ''}

        <hr>

        <div class="alert alert-warning">
            <strong>Próximos Passos:</strong>
            <ol>
                <li>Entre em contato com o cliente por WhatsApp ou email</li>
                <li>Ofereça uma consulta inicial gratuita de 15 minutos</li>
                <li>Baixe e leia o relatório completo</li>
                <li>Apresente proposta de honorários</li>
                <li>Formalize o contrato</li>
            </ol>
        </div>
    `;

    document.getElementById('modalLeadBody').innerHTML = html;

    const modal = new bootstrap.Modal(document.getElementById('modalLeadDetalhes'));
    modal.show();
}

function copiarTexto(texto) {
    navigator.clipboard.writeText(texto);
    alert('Copiado para área de transferência!');
}

function filtrarLeads() {
    const area = document.getElementById('filterArea').value;
    const prob = document.getElementById('filterProb').value;

    let leadsFiltrados = leadsData;

    if (area) {
        leadsFiltrados = leadsFiltrados.filter(l => l.area === area);
    }

    if (prob) {
        leadsFiltrados = leadsFiltrados.filter(l => l.probabilidade === prob);
    }

    renderizarLeads(leadsFiltrados);
}
