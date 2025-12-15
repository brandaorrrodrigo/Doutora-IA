// Dashboard - Doutora IA
const API_URL = 'http://localhost:8080';

let leadsChart, areasChart, funnelChart;

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

        const lawyer = await response.json();
        document.getElementById('lawyerName').textContent = lawyer.name;

        return true;
    } catch (error) {
        logout();
        return false;
    }
}

// ==========================================
// API CALLS
// ==========================================

async function apiCall(endpoint) {
    const token = getAccessToken();

    const response = await fetch(`${API_URL}${endpoint}`, {
        headers: {
            'Authorization': `Bearer ${token}`
        }
    });

    if (!response.ok) {
        if (response.status === 401) {
            logout();
            throw new Error('Sessão expirada');
        }
        throw new Error('Erro ao carregar dados');
    }

    return await response.json();
}

// ==========================================
// CARREGAR DASHBOARD
// ==========================================

async function loadDashboard() {
    try {
        // Carregar dados completos
        const data = await apiCall('/dashboard/full');

        // Renderizar cada seção
        renderStats(data.overview);
        renderAlerts(await apiCall('/dashboard/alerts'));
        renderLeadsChart(data.charts.leads_by_day);
        renderAreasChart(data.charts.leads_by_area);
        renderFunnelChart(data.charts.conversion_funnel);
        renderPrazos(data.prazos_urgentes);
        renderLeadsHistory(data.leads_history);

        // Carregar novas funcionalidades
        await loadReceitaChart(6);
        await loadTimeline(7);
        await loadRanking();

        // Atualizar badge de notificações
        document.getElementById('notificationBadge').textContent = data.overview.notificacoes_nao_lidas;

    } catch (error) {
        console.error('Erro ao carregar dashboard:', error);
        alert('Erro ao carregar dashboard. Tente novamente.');
    }
}

// ==========================================
// RENDERIZAR ESTATÍSTICAS
// ==========================================

function renderStats(overview) {
    const statsGrid = document.getElementById('statsGrid');

    statsGrid.innerHTML = `
        <div class="stat-card primary">
            <div class="icon">
                <i class="fas fa-inbox"></i>
            </div>
            <div class="value">${overview.leads_pendentes}</div>
            <div class="label">Leads Pendentes</div>
        </div>

        <div class="stat-card success">
            <div class="icon">
                <i class="fas fa-check-circle"></i>
            </div>
            <div class="value">${overview.leads_aceitos_mes}</div>
            <div class="label">Aceitos este Mês</div>
        </div>

        <div class="stat-card warning">
            <div class="icon">
                <i class="fas fa-percentage"></i>
            </div>
            <div class="value">${overview.taxa_conversao}%</div>
            <div class="label">Taxa de Conversão</div>
        </div>

        <div class="stat-card success">
            <div class="icon">
                <i class="fas fa-dollar-sign"></i>
            </div>
            <div class="value">R$ ${(overview.valor_estimado_mes / 1000).toFixed(0)}k</div>
            <div class="label">Valor Estimado (Mês)</div>
        </div>

        <div class="stat-card danger">
            <div class="icon">
                <i class="fas fa-clock"></i>
            </div>
            <div class="value">${overview.prazos_proximos}</div>
            <div class="label">Prazos Próximos</div>
        </div>

        <div class="stat-card primary">
            <div class="icon">
                <i class="fas fa-calendar"></i>
            </div>
            <div class="value">${overview.agendamentos_hoje}</div>
            <div class="label">Agendamentos Hoje</div>
        </div>

        <div class="stat-card warning">
            <div class="icon">
                <i class="fas fa-star"></i>
            </div>
            <div class="value">${overview.avaliacao_media}/5</div>
            <div class="label">Avaliação Média (${overview.total_avaliacoes} avaliações)</div>
        </div>

        <div class="stat-card danger">
            <div class="icon">
                <i class="fas fa-bell"></i>
            </div>
            <div class="value">${overview.notificacoes_nao_lidas}</div>
            <div class="label">Notificações</div>
        </div>
    `;
}

// ==========================================
// RENDERIZAR ALERTAS
// ==========================================

function renderAlerts(alerts) {
    const alertsSection = document.getElementById('alertsSection');
    const alertsList = document.getElementById('alertsList');

    if (alerts.length === 0) {
        alertsSection.style.display = 'none';
        return;
    }

    alertsSection.style.display = 'block';

    alertsList.innerHTML = alerts.map(alert => `
        <div class="alert-item ${alert.prioridade}">
            <div class="d-flex justify-content-between align-items-start">
                <div>
                    <strong>${alert.titulo}</strong>
                    <p class="mb-0 mt-1">${alert.mensagem}</p>
                </div>
                ${alert.link ? `<a href="${alert.link}" class="btn btn-sm btn-primary">Ver</a>` : ''}
            </div>
        </div>
    `).join('');
}

// ==========================================
// GRÁFICO DE LEADS POR DIA
// ==========================================

function renderLeadsChart(data) {
    const ctx = document.getElementById('leadsChart').getContext('2d');

    // Destruir gráfico anterior se existir
    if (leadsChart) {
        leadsChart.destroy();
    }

    leadsChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.map(d => {
                const date = new Date(d.data);
                return date.toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit' });
            }),
            datasets: [
                {
                    label: 'Total',
                    data: data.map(d => d.total),
                    borderColor: '#1a5490',
                    backgroundColor: 'rgba(26, 84, 144, 0.1)',
                    tension: 0.4,
                    fill: true
                },
                {
                    label: 'Aceitos',
                    data: data.map(d => d.aceitos),
                    borderColor: '#28a745',
                    backgroundColor: 'rgba(40, 167, 69, 0.1)',
                    tension: 0.4,
                    fill: true
                },
                {
                    label: 'Rejeitados',
                    data: data.map(d => d.rejeitados),
                    borderColor: '#dc3545',
                    backgroundColor: 'rgba(220, 53, 69, 0.1)',
                    tension: 0.4,
                    fill: true
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    position: 'top',
                },
                tooltip: {
                    mode: 'index',
                    intersect: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 1
                    }
                }
            }
        }
    });
}

// ==========================================
// GRÁFICO DE ÁREAS
// ==========================================

function renderAreasChart(data) {
    const ctx = document.getElementById('areasChart').getContext('2d');

    if (areasChart) {
        areasChart.destroy();
    }

    const areaLabels = {
        'familia': 'Família',
        'consumidor': 'Consumidor',
        'bancario': 'Bancário',
        'saude': 'Saúde',
        'trabalhista': 'Trabalhista'
    };

    areasChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: data.map(d => areaLabels[d.area] || d.area),
            datasets: [{
                data: data.map(d => d.total),
                backgroundColor: [
                    '#1a5490',
                    '#28a745',
                    '#ffc107',
                    '#dc3545',
                    '#17a2b8'
                ]
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    position: 'bottom'
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const label = context.label || '';
                            const value = context.parsed || 0;
                            const percentage = data[context.dataIndex].percentual;
                            return `${label}: ${value} (${percentage}%)`;
                        }
                    }
                }
            }
        }
    });
}

// ==========================================
// GRÁFICO DE FUNIL
// ==========================================

function renderFunnelChart(data) {
    const ctx = document.getElementById('funnelChart').getContext('2d');

    if (funnelChart) {
        funnelChart.destroy();
    }

    funnelChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['Recebidos', 'Visualizados', 'Aceitos', 'Convertidos'],
            datasets: [{
                label: 'Leads',
                data: [data.recebidos, data.visualizados, data.aceitos, data.convertidos],
                backgroundColor: [
                    'rgba(26, 84, 144, 0.8)',
                    'rgba(26, 84, 144, 0.6)',
                    'rgba(40, 167, 69, 0.8)',
                    'rgba(40, 167, 69, 1)'
                ]
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            indexAxis: 'y',
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                x: {
                    beginAtZero: true
                }
            }
        }
    });
}

// ==========================================
// RENDERIZAR PRAZOS
// ==========================================

function renderPrazos(prazos) {
    const prazosList = document.getElementById('prazosList');

    if (prazos.length === 0) {
        prazosList.innerHTML = '<p class="text-muted">Nenhum prazo urgente nos próximos 5 dias</p>';
        return;
    }

    prazosList.innerHTML = `
        <div class="table-responsive">
            <table class="table table-sm">
                <thead>
                    <tr>
                        <th>Processo</th>
                        <th>Tipo</th>
                        <th>Data Limite</th>
                        <th>Dias</th>
                        <th>Prioridade</th>
                    </tr>
                </thead>
                <tbody>
                    ${prazos.map(prazo => {
                        const badge = prazo.prioridade === 'critica' ? 'danger' :
                                     prazo.prioridade === 'alta' ? 'warning' : 'info';
                        return `
                            <tr>
                                <td><small>${prazo.processo_numero}</small></td>
                                <td>${prazo.tipo}</td>
                                <td>${new Date(prazo.data_limite).toLocaleDateString('pt-BR')}</td>
                                <td><strong>${prazo.dias_restantes} dia(s)</strong></td>
                                <td><span class="badge bg-${badge}">${prazo.prioridade}</span></td>
                            </tr>
                        `;
                    }).join('')}
                </tbody>
            </table>
        </div>
    `;
}

// ==========================================
// RENDERIZAR HISTÓRICO DE LEADS
// ==========================================

function renderLeadsHistory(leads) {
    const tbody = document.getElementById('leadsHistoryBody');

    if (leads.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" class="text-center text-muted">Nenhum lead recente</td></tr>';
        return;
    }

    tbody.innerHTML = leads.slice(0, 10).map(lead => {
        const statusBadge = {
            'pending': '<span class="badge bg-warning">Pendente</span>',
            'accepted': '<span class="badge bg-success">Aceito</span>',
            'rejected': '<span class="badge bg-danger">Rejeitado</span>',
            'expired': '<span class="badge bg-secondary">Expirado</span>'
        };

        const probabilidadeBadge = {
            'alta': '<span class="badge bg-success">Alta</span>',
            'media': '<span class="badge bg-warning">Média</span>',
            'baixa': '<span class="badge bg-danger">Baixa</span>'
        };

        return `
            <tr>
                <td>${new Date(lead.sent_at).toLocaleDateString('pt-BR')}</td>
                <td><span class="badge bg-primary">${lead.area.toUpperCase()}</span></td>
                <td><small>${lead.description}</small></td>
                <td>${probabilidadeBadge[lead.probability] || lead.probability}</td>
                <td>R$ ${lead.estimated_fees.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}</td>
                <td>${statusBadge[lead.status] || lead.status}</td>
            </tr>
        `;
    }).join('');
}

// ==========================================
// GRÁFICO DE RECEITA MENSAL
// ==========================================

let receitaChart;

async function loadReceitaChart(meses = 6) {
    try {
        const data = await apiCall(`/dashboard/charts/receita-mensal?meses=${meses}`);
        renderReceitaChart(data);
    } catch (error) {
        console.error('Erro ao carregar gráfico de receita:', error);
    }
}

function renderReceitaChart(data) {
    const ctx = document.getElementById('receitaChart').getContext('2d');

    if (receitaChart) {
        receitaChart.destroy();
    }

    receitaChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.map(d => d.mes_nome),
            datasets: [
                {
                    label: 'Receita Estimada',
                    data: data.map(d => d.receita_estimada),
                    backgroundColor: 'rgba(26, 84, 144, 0.8)',
                    borderColor: '#1a5490',
                    borderWidth: 1
                },
                {
                    label: 'Receita Real',
                    data: data.map(d => d.receita_real),
                    backgroundColor: 'rgba(40, 167, 69, 0.8)',
                    borderColor: '#28a745',
                    borderWidth: 1
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    position: 'top',
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const label = context.dataset.label || '';
                            const value = context.parsed.y || 0;
                            return `${label}: R$ ${value.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}`;
                        },
                        afterLabel: function(context) {
                            const index = context.dataIndex;
                            const item = data[index];
                            return [
                                `Leads Convertidos: ${item.leads_convertidos}`,
                                `Ticket Médio: R$ ${item.ticket_medio.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}`
                            ];
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return 'R$ ' + (value / 1000).toFixed(0) + 'k';
                        }
                    }
                }
            }
        }
    });
}

// ==========================================
// TIMELINE DE ATIVIDADES
// ==========================================

async function loadTimeline(dias = 7) {
    try {
        const data = await apiCall(`/dashboard/timeline?dias=${dias}&limit=50`);
        renderTimeline(data);
    } catch (error) {
        console.error('Erro ao carregar timeline:', error);
    }
}

function renderTimeline(activities) {
    const container = document.getElementById('timelineContainer');

    if (activities.length === 0) {
        container.innerHTML = '<p class="text-muted text-center py-4">Nenhuma atividade recente</p>';
        return;
    }

    const iconMap = {
        'check-circle': 'fa-check-circle',
        'times-circle': 'fa-times-circle',
        'calendar-check': 'fa-calendar-check',
        'bell': 'fa-bell',
        'file-alt': 'fa-file-alt'
    };

    container.innerHTML = `
        <div class="timeline-container">
            ${activities.map(activity => {
                const icon = iconMap[activity.icone] || 'fa-circle';
                const timeAgo = formatTimeAgo(activity.timestamp);

                return `
                    <div class="timeline-item">
                        <div class="timeline-icon ${activity.cor}">
                            <i class="fas ${icon}"></i>
                        </div>
                        <div class="timeline-content">
                            <div class="d-flex justify-content-between align-items-start">
                                <div>
                                    <strong>${activity.titulo}</strong>
                                    <p class="mb-1 mt-1">${activity.descricao}</p>
                                    <small class="timeline-time">
                                        <i class="far fa-clock"></i> ${timeAgo}
                                    </small>
                                </div>
                                ${activity.link ? `
                                    <a href="${activity.link}" class="btn btn-sm btn-outline-primary">
                                        Ver <i class="fas fa-arrow-right"></i>
                                    </a>
                                ` : ''}
                            </div>
                        </div>
                    </div>
                `;
            }).join('')}
        </div>
    `;
}

function formatTimeAgo(timestamp) {
    if (!timestamp) return 'Data desconhecida';

    const now = new Date();
    const date = new Date(timestamp);
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'Agora mesmo';
    if (diffMins < 60) return `${diffMins} minuto${diffMins > 1 ? 's' : ''} atrás`;
    if (diffHours < 24) return `${diffHours} hora${diffHours > 1 ? 's' : ''} atrás`;
    if (diffDays < 7) return `${diffDays} dia${diffDays > 1 ? 's' : ''} atrás`;

    return date.toLocaleDateString('pt-BR', { day: '2-digit', month: 'short', year: 'numeric' });
}

// ==========================================
// RANKING DE PERFORMANCE
// ==========================================

async function loadRanking() {
    try {
        const data = await apiCall('/dashboard/ranking/performance?limit=10');
        renderRanking(data);
    } catch (error) {
        console.error('Erro ao carregar ranking:', error);
    }
}

function renderRanking(data) {
    const container = document.getElementById('rankingCard');

    const medalEmojis = ['🥇', '🥈', '🥉'];

    container.innerHTML = `
        <div class="ranking-card">
            <div class="ranking-position">#${data.sua_posicao}</div>
            <p class="mb-1"><strong>Sua Posição</strong></p>
            <p class="text-muted small">de ${data.total_advogados} advogados</p>

            <div class="ranking-percentile">
                <i class="fas fa-chart-line"></i> Top ${(100 - data.percentil).toFixed(0)}%
            </div>

            <hr>

            <p class="mb-2"><strong>Seu Score</strong></p>
            <div class="progress mb-3" style="height: 25px;">
                <div class="progress-bar bg-success" role="progressbar"
                     style="width: ${data.seu_score}%">
                    ${data.seu_score.toFixed(0)}
                </div>
            </div>

            <p class="mb-2 mt-4"><strong>Top 10</strong></p>
            <div class="ranking-list">
                ${data.top_10.map(item => `
                    <div class="ranking-item ${item.posicao === data.sua_posicao ? 'bg-light' : ''}">
                        <div class="ranking-medal">
                            ${item.posicao <= 3 ? medalEmojis[item.posicao - 1] : `#${item.posicao}`}
                        </div>
                        <div class="flex-grow-1 text-start">
                            <div><strong>${item.nome}</strong></div>
                            <small class="text-muted">
                                Score: ${item.score.toFixed(0)} |
                                ${item.total_leads} leads |
                                ⭐ ${item.rating.toFixed(1)}
                            </small>
                        </div>
                    </div>
                `).join('')}
            </div>
        </div>
    `;
}

// ==========================================
// EXPORTAÇÃO DE DADOS
// ==========================================

async function exportCSV() {
    try {
        const token = getAccessToken();
        const response = await fetch(`${API_URL}/dashboard/export/csv?meses=1`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (!response.ok) throw new Error('Erro ao exportar CSV');

        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `leads_${new Date().toISOString().split('T')[0]}.csv`;
        document.body.appendChild(a);
        a.click();
        a.remove();
        window.URL.revokeObjectURL(url);

        alert('✅ CSV exportado com sucesso!');
    } catch (error) {
        console.error('Erro ao exportar CSV:', error);
        alert('❌ Erro ao exportar CSV. Tente novamente.');
    }
}

async function exportJSON() {
    try {
        const token = getAccessToken();
        const response = await fetch(`${API_URL}/dashboard/export/json`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (!response.ok) throw new Error('Erro ao exportar JSON');

        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `dashboard_${new Date().toISOString().split('T')[0]}.json`;
        document.body.appendChild(a);
        a.click();
        a.remove();
        window.URL.revokeObjectURL(url);

        alert('✅ JSON exportado com sucesso!');
    } catch (error) {
        console.error('Erro ao exportar JSON:', error);
        alert('❌ Erro ao exportar JSON. Tente novamente.');
    }
}

// ==========================================
// NAVEGAÇÃO
// ==========================================

function showSection(section) {
    // TODO: Implementar navegação entre seções
    alert(`Navegando para: ${section}`);
}

function refreshDashboard() {
    location.reload();
}

// ==========================================
// UTILITÁRIOS
// ==========================================

function updateCurrentDate() {
    const now = new Date();
    const formatted = now.toLocaleDateString('pt-BR', {
        weekday: 'long',
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
    document.getElementById('currentDate').textContent = formatted;
}

// ==========================================
// INICIALIZAÇÃO
// ==========================================

document.addEventListener('DOMContentLoaded', async () => {
    updateCurrentDate();

    // Verificar autenticação
    const isAuth = await checkAuth();

    if (isAuth) {
        // Carregar dashboard
        await loadDashboard();

        // Atualizar a cada 5 minutos
        setInterval(loadDashboard, 5 * 60 * 1000);
    }
});
