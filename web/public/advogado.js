// Advogado Mode - Doutora IA
// Detecta automaticamente a URL da API baseado no ambiente
const API_URL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? 'http://localhost:8080'
    : window.location.origin.includes('railway.app')
        ? 'https://doutora-ia-production.up.railway.app'
        : window.location.origin;
let citationsCart = [];

// Keyboard shortcut for search (Ctrl+K)
document.addEventListener('keydown', (e) => {
    if (e.ctrlKey && e.key === 'k') {
        e.preventDefault();
        document.getElementById('searchQuery').focus();
    }
});

// Search button
document.getElementById('btnSearch').addEventListener('click', performSearch);

// Enter key in search box
document.getElementById('searchQuery').addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        performSearch();
    }
});

async function performSearch() {
    const query = document.getElementById('searchQuery').value;
    const tipo = document.getElementById('searchType').value;
    const area = document.getElementById('searchArea').value;
    const tribunal = document.getElementById('searchTribunal').value;

    if (!query || query.length < 3) {
        alert('Digite pelo menos 3 caracteres para buscar');
        return;
    }

    // Show loading
    const resultsDiv = document.getElementById('searchResults');
    resultsDiv.innerHTML = '<div class="text-center"><div class="spinner-border"></div><p>Buscando...</p></div>';

    try {
        const params = new URLSearchParams({
            query: query,
            limit: '10'
        });

        if (tipo) params.append('tipo', tipo);
        if (area) params.append('area', area);
        if (tribunal) params.append('tribunal', tribunal);

        const response = await fetch(`${API_URL}/search?${params}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                query: query,
                tipo: tipo || null,
                area: area || null,
                tribunal: tribunal || null,
                limit: 10
            })
        });

        if (!response.ok) {
            throw new Error('Erro na busca');
        }

        const data = await response.json();
        displayResults(data.results);

    } catch (error) {
        console.error('Error:', error);
        resultsDiv.innerHTML = '<div class="alert alert-danger">Erro ao buscar. Verifique se a API está rodando.</div>';
    }
}

function displayResults(results) {
    const resultsDiv = document.getElementById('searchResults');

    if (results.length === 0) {
        resultsDiv.innerHTML = '<div class="alert alert-info">Nenhum resultado encontrado.</div>';
        return;
    }

    let html = `<h5>${results.length} resultados encontrados</h5>`;

    results.forEach((citation, index) => {
        html += `
            <div class="citation-item">
                <div class="d-flex justify-content-between align-items-start">
                    <div>
                        <h6><span class="badge bg-secondary">${citation.tipo.toUpperCase()}</span> ${citation.titulo}</h6>
                        ${citation.tribunal ? `<small class="text-muted">${citation.tribunal}</small>` : ''}
                        ${citation.orgao ? `<small class="text-muted">${citation.orgao}</small>` : ''}
                        ${citation.data ? `<small class="text-muted"> | ${citation.data}</small>` : ''}
                    </div>
                </div>
                <p class="mt-2">${citation.texto.substring(0, 300)}...</p>
                <div class="citation-actions">
                    <button class="btn btn-sm btn-primary" onclick="addToCart(${index}, ${JSON.stringify(citation).replace(/"/g, '&quot;')})">
                        <i class="fas fa-plus"></i> Adicionar à Peça
                    </button>
                    ${citation.fonte_url ? `<a href="${citation.fonte_url}" target="_blank" class="btn btn-sm btn-outline-secondary"><i class="fas fa-external-link-alt"></i> Fonte</a>` : ''}
                </div>
            </div>
        `;
    });

    resultsDiv.innerHTML = html;
}

function addToCart(index, citation) {
    // Check if already in cart
    const exists = citationsCart.find(c => c.id === citation.id);
    if (exists) {
        alert('Esta citação já está no carrinho');
        return;
    }

    citationsCart.push(citation);
    updateCart();

    // Show feedback
    const btn = event.target.closest('button');
    const originalText = btn.innerHTML;
    btn.innerHTML = '<i class="fas fa-check"></i> Adicionado';
    btn.classList.remove('btn-primary');
    btn.classList.add('btn-success');

    setTimeout(() => {
        btn.innerHTML = originalText;
        btn.classList.remove('btn-success');
        btn.classList.add('btn-primary');
    }, 1500);
}

function updateCart() {
    const cartItems = document.getElementById('cartItems');
    const btnCompose = document.getElementById('btnCompose');

    if (citationsCart.length === 0) {
        cartItems.innerHTML = '<p class="text-muted text-center">Nenhuma citação adicionada</p>';
        btnCompose.disabled = true;
        return;
    }

    let html = '';
    citationsCart.forEach((citation, index) => {
        html += `
            <div class="border-bottom pb-2 mb-2">
                <small class="d-block"><strong>[${index + 1}] ${citation.titulo}</strong></small>
                <small class="text-muted">${citation.tipo}</small>
                <button class="btn btn-sm btn-outline-danger float-end" onclick="removeFromCart(${index})">
                    <i class="fas fa-trash"></i>
                </button>
            </div>
        `;
    });

    cartItems.innerHTML = html;
    btnCompose.disabled = false;
}

function removeFromCart(index) {
    citationsCart.splice(index, 1);
    updateCart();
}

// Compose document button
document.getElementById('btnCompose').addEventListener('click', () => {
    if (citationsCart.length === 0) {
        alert('Adicione citações ao carrinho primeiro');
        return;
    }

    alert(`Funcionalidade de geração de peças em desenvolvimento.\n\nVocê tem ${citationsCart.length} citações no carrinho.\n\nEm produção, aqui você abriria o formulário de composição de peça com as citações selecionadas.`);

    // In production:
    // 1. Open compose form
    // 2. Fill in case metadata (parties, court, etc)
    // 3. Call /compose endpoint
    // 4. Download generated DOCX/PDF
});
