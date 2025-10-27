const API_BASE = 'http://127.0.0.1:8000';
const API_KEY = 'troque_aqui';

async function uploadCSV() {
    const fileInput = document.getElementById('csvFile');
    const file = fileInput.files[0];
    
    if (!file) {
        alert('Selecione um arquivo CSV');
        return;
    }
    
    const formData = new FormData();
    formData.append('file', file);
    
    try {
        const response = await fetch(`${API_BASE}/upload-csv`, {
            method: 'POST',
            headers: {'x-api-key': API_KEY},
            body: formData
        });
        
        const data = await response.json();
        
        document.getElementById('uploadStatus').innerHTML = `
            <div class="success">
                <h3>✅ Upload bem-sucedido!</h3>
                <p>Estudantes: ${data.n_students}</p>
                <p>Itens: ${data.n_items}</p>
            </div>
        `;
    } catch (error) {
        document.getElementById('uploadStatus').innerHTML = `
            <div class="error">❌ Erro: ${error.message}</div>
        `;
    }
}

async function getRecommendation() {
    const strategy = document.getElementById('strategy').value;
    
    const payload = {
        student_history: [
            {item_id: 'item_1', correct: 1},
            {item_id: 'item_2', correct: 0}
        ],
        candidate_items: ['item_3', 'item_4', 'item_5'],
        strategy: strategy,
        target_p: 0.7
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
        
        const data = await response.json();
        
        document.getElementById('recommendation').innerHTML = `
            <div class="success">
                <h3>📝 Recomendação</h3>
                <p><strong>Item:</strong> ${data.item_id}</p>
                <p><strong>Probabilidade estimada:</strong> ${(data.p_estimated * 100).toFixed(1)}%</p>
                <p><strong>Justificativa:</strong> ${data.rationale}</p>
            </div>
        `;
    } catch (error) {
        document.getElementById('recommendation').innerHTML = `
            <div class="error">❌ Erro: ${error.message}</div>
        `;
    }
}

async function loadMetrics() {
    try {
        const response = await fetch(`${API_BASE}/metrics`, {
            headers: {'x-api-key': API_KEY}
        });
        
        const data = await response.json();
        
        document.getElementById('metrics').innerHTML = `
            <p><strong>AUC:</strong> ${data.auc_dkt.toFixed(3)}</p>
            <p><strong>Accuracy:</strong> ${data.accuracy_dkt.toFixed(3)}</p>
            <p><strong>Ganho médio:</strong> ${data.avg_gain_dkt.toFixed(3)}</p>
        `;
    } catch (error) {
        console.error('Erro ao carregar métricas:', error);
    }
}

window.onload = () => {
    loadMetrics();
};