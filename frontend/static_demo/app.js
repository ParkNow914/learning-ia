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
        showMessage('uploadStatus', '⚠️ Por favor, selecione um arquivo CSV primeiro!', 'error');
        return;
    }
    
    const btn = document.getElementById('uploadBtn');
    btn.dataset.originalText = '📤 Carregar Arquivo';
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
                <h3>✅ Arquivo carregado com sucesso!</h3>
                <p style="margin-top: 0.5rem;">🎉 Seus dados foram processados e estão prontos para usar!</p>
                <div class="stats-grid" style="margin-top: 1rem;">
                    <div class="stat-card">
                        <div class="stat-value">${data.n_students}</div>
                        <div class="stat-label">👥 Estudantes</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">${data.n_items}</div>
                        <div class="stat-label">📝 Exercícios</div>
                    </div>
                </div>
                <p style="margin-top: 1rem; font-size: 0.9em;">
                    💡 Agora você pode pedir recomendações na seção 2 abaixo!
                </p>
            </div>
        `;
    } catch (error) {
        showMessage('uploadStatus', `❌ Erro ao processar arquivo: ${error.message}<br><br>💡 Dica: Verifique se o arquivo está no formato correto (veja o exemplo acima)`, 'error');
    } finally {
        setButtonLoading('uploadBtn', false);
    }
}

async function getRecommendation() {
    const strategy = document.getElementById('strategy').value;
    const targetP = parseFloat(document.getElementById('targetP').value);
    
    const btn = document.getElementById('recommendBtn');
    btn.dataset.originalText = '🎯 Obter Recomendação';
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
        
        const strategyNames = {
            'target': '🎯 Target (Dificuldade Ideal)',
            'info_gain': '📊 Ganho de Informação',
            'exploration': '🔍 Exploração',
            'heuristic': '🧮 Heurística',
            'random': '🎲 Aleatória'
        };
        
        document.getElementById('recommendation').innerHTML = `
            <div class="success">
                <h3>🎯 Recomendação Gerada pela IA</h3>
                <p style="margin-top: 0.5rem; font-size: 0.95em;">
                    A Inteligência Artificial analisou o histórico e recomenda:
                </p>
                <div class="stats-grid" style="margin-top: 1rem;">
                    <div class="stat-card">
                        <div class="stat-value">${data.item_id}</div>
                        <div class="stat-label">📝 Exercício Recomendado</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">${(data.p_estimated * 100).toFixed(1)}%</div>
                        <div class="stat-label">📊 Chance de Acerto</div>
                    </div>
                </div>
                <div style="margin-top: 1.5rem; padding: 1rem; background: var(--section-bg); border-radius: 8px;">
                    <p><strong>💡 Por que este exercício?</strong></p>
                    <p style="margin-top: 0.5rem;">${data.rationale}</p>
                </div>
                <p style="margin-top: 1rem;">
                    <span class="badge badge-info">${strategyNames[data.strategy] || data.strategy}</span>
                </p>
                <p style="margin-top: 1rem; font-size: 0.85em; color: var(--text-secondary);">
                    ℹ️ Esta recomendação foi calculada usando Inteligência Artificial (Deep Learning)
                </p>
            </div>
        `;
    } catch (error) {
        showMessage('recommendation', `❌ Erro ao obter recomendação: ${error.message}<br><br>💡 Dica: Certifique-se de que enviou os dados primeiro (seção 1) e que a API está rodando.`, 'error');
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
    showMessage('advancedResults', '🔍 Verificando se o modelo precisa ser retreinado...<br><br>💡 Esta análise compara dados atuais com os dados de treino.', 'info');
    
    try {
        const response = await fetch(`${API_BASE}/check-drift`, {
            headers: {'x-api-key': API_KEY}
        });
        
        if (!response.ok) {
            throw new Error('Endpoint não disponível');
        }
        
        const data = await response.json();
        
        const driftStatus = data.has_drift ? 
            '<span class="badge badge-error">⚠️ Drift Detectado - Modelo Pode Estar Desatualizado</span>' :
            '<span class="badge badge-success">✅ Modelo Está Funcionando Bem</span>';
        
        const recommendation = data.has_drift ?
            '<p style="margin-top: 1rem; padding: 1rem; background: rgba(239, 68, 68, 0.1); border-radius: 8px;"><strong>⚠️ Recomendação:</strong><br>O modelo está desatualizado. Retreine com dados mais recentes para manter a precisão!</p>' :
            '<p style="margin-top: 1rem; padding: 1rem; background: rgba(16, 185, 129, 0.1); border-radius: 8px;"><strong>✅ Tudo Certo:</strong><br>O modelo está funcionando bem. Não é necessário retreinar agora.</p>';
        
        showMessage('advancedResults', `
            <h3>🔍 Análise de Drift do Modelo</h3>
            ${driftStatus}
            <p style="margin-top: 1rem; font-size: 0.9em; color: var(--text-secondary);">
                📅 Última verificação: ${new Date().toLocaleString('pt-BR')}
            </p>
            ${recommendation}
            <details style="margin-top: 1rem;">
                <summary style="cursor: pointer; color: var(--primary-color);">❓ O que é "drift"?</summary>
                <p style="margin-top: 0.5rem; font-size: 0.9em;">
                    Drift acontece quando os padrões dos dados mudam com o tempo. Por exemplo, se os alunos mudarem de nível, o modelo precisa aprender de novo com os dados atualizados.
                </p>
            </details>
        `, 'info');
    } catch (error) {
        showMessage('advancedResults', '⚠️ Recurso de detecção de drift ainda não está conectado à API.<br><br>💡 Esta feature está implementada no código mas precisa ser integrada ao servidor.', 'error');
    }
}

async function getCacheStats() {
    showMessage('advancedResults', '📊 Carregando estatísticas do cache...<br><br>💡 O cache é uma memória rápida que acelera as respostas.', 'info');
    
    try {
        const response = await fetch(`${API_BASE}/cache-stats`, {
            headers: {'x-api-key': API_KEY}
        });
        
        if (!response.ok) {
            throw new Error('Endpoint não disponível');
        }
        
        const data = await response.json();
        
        const utilizationPercent = ((data.utilization || 0) * 100).toFixed(1);
        const utilizationColor = data.utilization > 0.8 ? 'error' : data.utilization > 0.5 ? 'info' : 'success';
        
        showMessage('advancedResults', `
            <h3>💾 Estatísticas do Cache</h3>
            <p style="margin-top: 0.5rem; font-size: 0.95em;">
                O cache armazena resultados para responder mais rápido nas próximas vezes!
            </p>
            <div class="stats-grid" style="margin-top: 1rem;">
                <div class="stat-card">
                    <div class="stat-value">${data.n_entries || 0}</div>
                    <div class="stat-label">📦 Itens Armazenados</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">${(data.total_size_mb || 0).toFixed(2)} MB</div>
                    <div class="stat-label">💾 Espaço Usado</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">${utilizationPercent}%</div>
                    <div class="stat-label">📊 Utilização</div>
                </div>
            </div>
            <p style="margin-top: 1rem; padding: 1rem; background: var(--section-bg); border-radius: 8px; font-size: 0.9em;">
                <strong>⚡ Benefício:</strong> Predições no cache são até 90% mais rápidas!
            </p>
            <details style="margin-top: 1rem;">
                <summary style="cursor: pointer; color: var(--primary-color);">❓ Como funciona o cache?</summary>
                <p style="margin-top: 0.5rem; font-size: 0.9em;">
                    Quando você pede uma recomendação, o sistema guarda o resultado. Se pedir a mesma coisa de novo, ele já tem a resposta pronta e não precisa calcular tudo outra vez!
                </p>
            </details>
        `, 'success');
    } catch (error) {
        showMessage('advancedResults', '⚠️ Recurso de cache ainda não está conectado à API.<br><br>💡 Esta feature está implementada no código mas precisa ser integrada ao servidor.', 'error');
    }
}

async function getUncertainty() {
    showMessage('advancedResults', '🎲 Calculando nível de confiança da IA usando MC Dropout...<br><br>💡 Vamos executar a IA 10 vezes para medir a certeza.', 'info');
    
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
        const stdPercent = (data.std * 100).toFixed(1);
        const confidence = data.std < 0.05 ? 'Alta' : data.std < 0.10 ? 'Média' : 'Baixa';
        const confidenceBadge = data.std < 0.05 ? 'success' : data.std < 0.10 ? 'info' : 'error';
        const confidenceEmoji = data.std < 0.05 ? '✅' : data.std < 0.10 ? '⚠️' : '❌';
        
        showMessage('advancedResults', `
            <h3>🎲 Análise de Incerteza (MC Dropout)</h3>
            <p style="margin-top: 0.5rem; font-size: 0.95em;">
                Medimos quantas vezes a IA dá a mesma resposta para avaliar sua confiança
            </p>
            <div class="stats-grid" style="margin-top: 1rem;">
                <div class="stat-card">
                    <div class="stat-value">${(data.mean * 100).toFixed(1)}%</div>
                    <div class="stat-label">📊 Probabilidade Média</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">±${stdPercent}%</div>
                    <div class="stat-label">📉 Variação (Incerteza)</div>
                </div>
            </div>
            <p style="margin-top: 1rem;">
                <span class="badge badge-${confidenceBadge}">${confidenceEmoji} Confiança: ${confidence}</span>
            </p>
            <p style="margin-top: 1rem; padding: 1rem; background: var(--section-bg); border-radius: 8px; font-size: 0.9em;">
                <strong>💡 Interpretação:</strong><br>
                ${confidence === 'Alta' ? 'A IA está muito confiante nesta predição. Você pode confiar nela!' : 
                  confidence === 'Média' ? 'A IA tem confiança razoável, mas há alguma incerteza. Use com cuidado.' :
                  'A IA não está confiante nesta predição. Considere usar estratégia heurística ou coletar mais dados.'}
            </p>
            <details style="margin-top: 1rem;">
                <summary style="cursor: pointer; color: var(--primary-color);">❓ O que significa incerteza?</summary>
                <p style="margin-top: 0.5rem; font-size: 0.9em;">
                    Incerteza mostra se a IA "tem certeza" ou está "em dúvida". Baixa incerteza = alta confiança. Alta incerteza = pode ser que a IA precise de mais dados sobre este aluno.
                </p>
            </details>
        `, 'success');
    } catch (error) {
        showMessage('advancedResults', '⚠️ Recurso de MC Dropout ainda não está conectado à API.<br><br>💡 Esta feature está implementada no código mas precisa ser integrada ao servidor.', 'error');
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
