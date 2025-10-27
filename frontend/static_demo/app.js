const API_BASE = 'http://127.0.0.1:8000';
const API_KEY = 'troque_aqui';

// Theme management
function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
}

// Load theme from localStorage
function loadTheme() {
    const savedTheme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-theme', savedTheme);
}

// Button loading state
function setButtonLoading(buttonId, loading) {
    const btn = document.getElementById(buttonId);
    if (loading) {
        btn.disabled = true;
        btn.innerHTML = '<span class="loading"></span> Processando...';
    } else {
        btn.disabled = false;
        btn.textContent = btn.dataset.originalText || 'Executar';
    }
}

async function uploadCSV() {
    const fileInput = document.getElementById('csvFile');
    const file = fileInput.files[0];
    
    if (!file) {
        showMessage('uploadStatus', 'Selecione um arquivo CSV', 'error');
        return;
    }
    
    const btn = document.getElementById('uploadBtn');
    btn.dataset.originalText = 'Carregar CSV';
    setButtonLoading('uploadBtn', true);
    
    const formData = new FormData();
    formData.append('file', file);
    
    try {
        const response = await fetch(`${API_BASE}/upload-csv`, {
            method: 'POST',
            headers: {'x-api-key': API_KEY},
            body: formData
        });
        
        if (!response.ok) {
            throw new Error(`Erro ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        
        document.getElementById('uploadStatus').innerHTML = `
            <div class="success">
                <h3>✅ Upload bem-sucedido!</h3>
                <div class="stats-grid" style="margin-top: 1rem;">
                    <div class="stat-card">
                        <div class="stat-value">${data.n_students}</div>
                        <div class="stat-label">Estudantes</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">${data.n_items}</div>
                        <div class="stat-label">Itens</div>
                    </div>
                </div>
            </div>
        `;
    } catch (error) {
        showMessage('uploadStatus', `❌ Erro: ${error.message}`, 'error');
    } finally {
        setButtonLoading('uploadBtn', false);
    }
}

async function getRecommendation() {
    const strategy = document.getElementById('strategy').value;
    const targetP = parseFloat(document.getElementById('targetP').value);
    
    const btn = document.getElementById('recommendBtn');
    btn.dataset.originalText = 'Obter Recomendação';
    setButtonLoading('recommendBtn', true);
    
    const payload = {
        student_history: [
            {item_id: 'item_1', correct: 1, timestamp: new Date().toISOString()},
            {item_id: 'item_2', correct: 0, timestamp: new Date().toISOString()}
        ],
        candidate_items: ['item_3', 'item_4', 'item_5'],
        strategy: strategy,
        target_p: targetP
    };
    
    try {
        const response = await fetch(`${API_BASE}/infer`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'x-api-key': API_KEY
            },
            body: JSON.stringify(payload)
        });
        
        if (!response.ok) {
            throw new Error(`Erro ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        
        document.getElementById('recommendation').innerHTML = `
            <div class="success">
                <h3>📝 Recomendação</h3>
                <div class="stats-grid" style="margin-top: 1rem;">
                    <div class="stat-card">
                        <div class="stat-value">${data.item_id}</div>
                        <div class="stat-label">Item Recomendado</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">${(data.p_estimated * 100).toFixed(1)}%</div>
                        <div class="stat-label">Probabilidade Estimada</div>
                    </div>
                </div>
                <p style="margin-top: 1rem;"><strong>Justificativa:</strong> ${data.rationale}</p>
                <p style="margin-top: 0.5rem;"><span class="badge badge-info">Estratégia: ${data.strategy}</span></p>
            </div>
        `;
    } catch (error) {
        showMessage('recommendation', `❌ Erro: ${error.message}`, 'error');
    } finally {
        setButtonLoading('recommendBtn', false);
    }
}

async function loadMetrics() {
    try {
        const response = await fetch(`${API_BASE}/metrics`, {
            headers: {'x-api-key': API_KEY}
        });
        
        if (!response.ok) return;
        
        const data = await response.json();
        
        document.getElementById('metrics').innerHTML = `
            <div class="info">
                <h3>📊 Métricas do Modelo</h3>
            </div>
        `;
        
        const statsHtml = `
            <div class="stat-card">
                <div class="stat-value">${data.auc_dkt.toFixed(3)}</div>
                <div class="stat-label">AUC</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">${data.accuracy_dkt.toFixed(3)}</div>
                <div class="stat-label">Accuracy</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">${data.avg_gain_dkt.toFixed(3)}</div>
                <div class="stat-label">Ganho Médio DKT</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">${data.time_to_master_mean_dkt.toFixed(1)}</div>
                <div class="stat-label">Tempo até Maestria</div>
            </div>
        `;
        
        document.getElementById('statsGrid').innerHTML = statsHtml;
        
        // Create chart
        const ctx = document.getElementById('metricsChart').getContext('2d');
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['DKT', 'Random', 'Heuristic'],
                datasets: [{
                    label: 'Ganho Médio de Habilidade',
                    data: [data.avg_gain_dkt, data.avg_gain_random, data.avg_gain_heuristic],
                    backgroundColor: [
                        'rgba(59, 130, 246, 0.8)',
                        'rgba(239, 68, 68, 0.8)',
                        'rgba(16, 185, 129, 0.8)'
                    ]
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    title: {
                        display: true,
                        text: 'Comparação de Estratégias'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    } catch (error) {
        console.error('Erro ao carregar métricas:', error);
    }
}

async function checkDrift() {
    showMessage('advancedResults', '🔍 Verificando drift...', 'info');
    
    try {
        const response = await fetch(`${API_BASE}/check-drift`, {
            headers: {'x-api-key': API_KEY}
        });
        
        if (!response.ok) {
            throw new Error('Endpoint não disponível');
        }
        
        const data = await response.json();
        
        const driftStatus = data.has_drift ? 
            '<span class="badge badge-error">⚠️ Drift Detectado</span>' :
            '<span class="badge badge-success">✅ Sem Drift</span>';
        
        showMessage('advancedResults', `
            <h3>Detecção de Drift</h3>
            ${driftStatus}
            <p style="margin-top: 1rem;">Última verificação: ${new Date().toLocaleString('pt-BR')}</p>
        `, 'info');
    } catch (error) {
        showMessage('advancedResults', '⚠️ Feature de drift detection ainda não disponível na API', 'error');
    }
}

async function getCacheStats() {
    showMessage('advancedResults', '📊 Carregando estatísticas de cache...', 'info');
    
    try {
        const response = await fetch(`${API_BASE}/cache-stats`, {
            headers: {'x-api-key': API_KEY}
        });
        
        if (!response.ok) {
            throw new Error('Endpoint não disponível');
        }
        
        const data = await response.json();
        
        showMessage('advancedResults', `
            <h3>Estatísticas de Cache</h3>
            <div class="stats-grid" style="margin-top: 1rem;">
                <div class="stat-card">
                    <div class="stat-value">${data.n_entries || 0}</div>
                    <div class="stat-label">Entradas</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">${(data.total_size_mb || 0).toFixed(2)} MB</div>
                    <div class="stat-label">Tamanho Total</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">${((data.utilization || 0) * 100).toFixed(1)}%</div>
                    <div class="stat-label">Utilização</div>
                </div>
            </div>
        `, 'success');
    } catch (error) {
        showMessage('advancedResults', '⚠️ Feature de cache ainda não disponível na API', 'error');
    }
}

async function getUncertainty() {
    showMessage('advancedResults', '🎲 Calculando incerteza com MC Dropout...', 'info');
    
    try {
        const response = await fetch(`${API_BASE}/uncertainty`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'x-api-key': API_KEY
            },
            body: JSON.stringify({
                student_history: [{item_id: 'item_1', correct: 1}],
                candidate_item: 'item_3',
                n_samples: 10
            })
        });
        
        if (!response.ok) {
            throw new Error('Endpoint não disponível');
        }
        
        const data = await response.json();
        
        showMessage('advancedResults', `
            <h3>Estimativa de Incerteza (MC Dropout)</h3>
            <div class="stats-grid" style="margin-top: 1rem;">
                <div class="stat-card">
                    <div class="stat-value">${(data.mean * 100).toFixed(1)}%</div>
                    <div class="stat-label">Probabilidade Média</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">±${(data.std * 100).toFixed(1)}%</div>
                    <div class="stat-label">Desvio Padrão</div>
                </div>
            </div>
        `, 'success');
    } catch (error) {
        showMessage('advancedResults', '⚠️ Feature de MC Dropout ainda não disponível na API', 'error');
    }
}

function showMessage(elementId, message, type) {
    document.getElementById(elementId).innerHTML = `
        <div class="${type}">
            ${message}
        </div>
    `;
}

// Initialize
window.onload = () => {
    loadTheme();
    loadMetrics();
};
