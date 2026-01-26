// Doutora IA Web App
// Detecta automaticamente a URL da API baseado no ambiente
const API_URL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? 'http://localhost:8080'
    : window.location.origin.includes('railway.app')
        ? 'https://doutora-ia-production.up.railway.app'
        : window.location.origin;
let currentCaseId = null;

// Handle form submission
document.getElementById('analysisForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    const description = document.getElementById('description').value;
    const email = document.getElementById('email').value;

    if (description.length < 50) {
        alert('Por favor, descreva sua situação com mais detalhes (mínimo 50 caracteres)');
        return;
    }

    // Show loading
    document.querySelector('.loading').style.display = 'block';
    document.getElementById('resultBox').style.display = 'none';

    try {
        const response = await fetch(`${API_URL}/analyze_case`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                descricao: description,
                detalhado: false,
                user_email: email || null
            })
        });

        if (!response.ok) {
            throw new Error('Erro ao analisar caso');
        }

        const data = await response.json();

        // Store case ID
        currentCaseId = data.case_id;

        // Display results
        displayResults(data);

    } catch (error) {
        console.error('Error:', error);
        alert('Erro ao analisar seu caso. Por favor, tente novamente.');
    } finally {
        document.querySelector('.loading').style.display = 'none';
    }
});

// Display results
function displayResults(data) {
    document.getElementById('resultTipificacao').textContent = data.tipificacao || 'Análise em andamento...';
    document.getElementById('resultEstrategias').textContent = data.estrategias || '';

    // Probability badge
    const probBadge = document.getElementById('resultProbabilidade');
    probBadge.textContent = `Probabilidade ${data.probabilidade.toUpperCase()}`;
    probBadge.className = `prob-badge prob-${data.probabilidade}`;

    // Show result box
    document.getElementById('resultBox').style.display = 'block';

    // Scroll to results
    document.getElementById('resultBox').scrollIntoView({ behavior: 'smooth' });
}

// Buy report button
document.getElementById('btnBuyReport').addEventListener('click', async () => {
    if (!currentCaseId) {
        alert('Por favor, analise seu caso primeiro.');
        return;
    }

    alert(`Funcionalidade de pagamento em desenvolvimento.\n\nSeu caso ID: ${currentCaseId}\n\nEm produção, aqui você seria redirecionado para pagamento via PIX ou cartão (R$ 7,00).`);

    // In production:
    // 1. Create payment
    // 2. Show QR code or redirect to payment page
    // 3. Poll for payment confirmation
    // 4. Download report when paid
});

// Find lawyer button
document.getElementById('btnFindLawyer').addEventListener('click', async () => {
    if (!currentCaseId) {
        alert('Por favor, analise seu caso primeiro.');
        return;
    }

    alert(`Funcionalidade de conexão com advogados em desenvolvimento.\n\nSeu caso ID: ${currentCaseId}\n\nEm produção, aqui você seria conectado com advogados especializados na sua área.`);

    // In production:
    // 1. Call /leads/assign endpoint
    // 2. Show lawyer profile
    // 3. Enable contact
});
