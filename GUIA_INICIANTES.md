# 🎯 Guia Rápido Para Iniciantes

**Nunca usou programação? Sem problema! Siga este guia passo a passo.**

---

## ✅ Passo 1: Instale o Python

### Windows
1. Vá em https://www.python.org/downloads/
2. Baixe a última versão (3.8 ou mais nova)
3. **IMPORTANTE:** Marque a caixa "Add Python to PATH"
4. Clique em "Install Now"
5. Espere terminar

### Mac
1. Abra o Terminal (Aplicativos > Utilitários > Terminal)
2. Digite: `brew install python3`
3. Aperte Enter
4. Espere terminar

### Linux (Ubuntu/Debian)
1. Abra o Terminal
2. Digite: `sudo apt update && sudo apt install python3 python3-pip`
3. Digite sua senha
4. Espere terminar

---

## ✅ Passo 2: Baixe o Projeto

### Opção A: Usando Git (Recomendado)

**Windows:**
1. Baixe Git: https://git-scm.com/download/win
2. Instale clicando em "Next" em tudo
3. Abra "Git Bash" (procure no menu iniciar)
4. Digite:
```bash
cd Desktop
git clone https://github.com/ParkNow914/learning-ia.git
cd learning-ia
```

**Mac/Linux:**
1. Abra o Terminal
2. Digite:
```bash
cd ~/Desktop
git clone https://github.com/ParkNow914/learning-ia.git
cd learning-ia
```

### Opção B: Download Direto (Mais Fácil)

1. Vá em https://github.com/ParkNow914/learning-ia
2. Clique no botão verde "Code"
3. Clique em "Download ZIP"
4. Extraia o ZIP na sua Área de Trabalho
5. Abra o Terminal/Prompt nesta pasta

---

## ✅ Passo 3: Execute o Instalador Automático

**No terminal/prompt, digite:**

```bash
# Windows (Prompt de Comando)
demo_run.sh

# Mac/Linux (Terminal)
chmod +x demo_run.sh
./demo_run.sh
```

**O que vai acontecer:**

```
┌─────────────────────────────────────┐
│ 1. Criando ambiente virtual...      │  ⏱️ 30 segundos
│ 2. Instalando bibliotecas...        │  ⏱️ 2 minutos
│ 3. Baixando dados educacionais...   │  ⏱️ 1 minuto
│ 4. Treinando Inteligência Artificial│  ⏱️ 2 minutos
│ 5. Gerando relatórios...            │  ⏱️ 30 segundos
└─────────────────────────────────────┘
         TOTAL: ~6 minutos
```

**Relaxe e espere! ☕**

---

## ✅ Passo 4: Veja os Resultados

Quando terminar, você verá:

```
✅ SUCESSO! Sistema pronto para uso.

📁 Arquivos criados:
   - data/real_combined_dataset.csv (dados processados)
   - models/dkt.pt (Inteligência Artificial treinada)
   - results/summary.json (métricas)
   - results/figures/*.png (gráficos)
   - results/demo_summary.txt (relatório legível)

📊 Métricas:
   - AUC: 0.850 (Excelente!)
   - Accuracy: 78.0% (Bom!)
   - Ganho de Aprendizado: 0.150 (Ótimo!)

🎉 Pronto para usar!
```

---

## ✅ Passo 5: Abra a Interface Visual

### Terminal 1: Inicie o Sistema

```bash
# Ative o ambiente virtual primeiro
source .venv/bin/activate  # Mac/Linux
.venv\Scripts\activate     # Windows

# Inicie a API
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Vai aparecer:
```
INFO: Started server process
INFO: Waiting for application startup.
INFO: Application startup complete.
INFO: Uvicorn running on http://127.0.0.1:8000
```

**Deixe este terminal aberto!**

### Terminal 2: Inicie a Interface

**Abra um NOVO terminal** e digite:

```bash
cd frontend/static_demo
python -m http.server 8001
```

Vai aparecer:
```
Serving HTTP on 0.0.0.0 port 8001 (http://0.0.0.0:8001/) ...
```

**Deixe este terminal aberto também!**

### Abra no Navegador

1. Abra seu navegador (Chrome, Firefox, Edge, Safari)
2. Digite na barra de endereço: `http://localhost:8001`
3. Aperte Enter

**🎉 Pronto! Você verá a interface visual!**

---

## ✅ Passo 6: Use o Sistema

### 6.1 Veja as Métricas

Na primeira seção você vê:
- **AUC**: Qualidade das previsões
- **Accuracy**: Taxa de acerto
- **Ganho Médio DKT**: Quanto os alunos melhoram
- **Tempo até Maestria**: Rapidez do aprendizado

### 6.2 Peça uma Recomendação

1. Escolha uma estratégia (recomendamos "Target")
2. Clique em "Obter Recomendação"
3. Sistema mostra:
   - Qual exercício recomendar
   - Probabilidade de acerto
   - Justificativa da escolha

### 6.3 Recursos Avançados

Clique nos botões:
- **Verificar Drift**: Vê se modelo precisa retreinar
- **Estatísticas de Cache**: Performance do sistema
- **Estimativa de Incerteza**: Confiança nas previsões

---

## 🎨 Personalize a Aparência

### Modo Escuro/Claro

Clique no botão **🌓** no canto superior direito!

- 🌞 **Modo Claro**: Cores claras e suaves
- 🌙 **Modo Escuro**: Confortável para os olhos

Sua preferência é salva automaticamente!

---

## 📊 Envie Seus Próprios Dados

### Formato do CSV

Crie um arquivo `meus_dados.csv` com estas colunas:

```csv
student_id,timestamp,item_id,skill_id,correct
aluno_001,2024-01-15T10:30:00,ex_mat_01,matematica,1
aluno_001,2024-01-15T10:35:00,ex_mat_02,matematica,0
aluno_002,2024-01-15T11:00:00,ex_mat_01,matematica,1
```

**Explicação das colunas:**
- `student_id`: ID do aluno (pode ser nome ou código)
- `timestamp`: Data e hora (formato: AAAA-MM-DDTHH:MM:SS)
- `item_id`: ID do exercício
- `skill_id`: Habilidade/conceito do exercício
- `correct`: 1 se acertou, 0 se errou

### Faça Upload

1. Na interface, clique em "Escolher arquivo"
2. Selecione seu `meus_dados.csv`
3. Clique em "Carregar CSV"
4. Sistema processa e mostra estatísticas

### Treine com Seus Dados

No terminal onde a API está rodando, pressione Ctrl+C e digite:

```bash
# Treinar com seus dados
python train_dkt.py --data-path meus_dados.csv --epochs 5
```

Aguarde o treinamento terminar (~5-10 minutos).

---

## 🔧 Comandos Úteis

### Ver Ajuda de um Comando

```bash
python train_dkt.py --help
```

### Treinar Rápido (Teste)

```bash
python train_dkt.py --epochs 2 --batch-size 32
```

### Treinar com Qualidade (Produção)

```bash
python train_dkt.py --epochs 10 --batch-size 64 --hidden-size 256
```

### Verificar Instalação

```bash
python check_installation.py
```

### Ver Logs

```bash
# Logs da API
tail -f results/logs/api.log

# Logs do treinamento
tail -f results/logs/train.log
```

---

## 🐛 Problemas? Soluções Rápidas

### "Comando não encontrado"

**Problema:** Terminal não reconhece comandos
**Solução:** Certifique-se de estar na pasta do projeto
```bash
cd ~/Desktop/learning-ia  # Ajuste para sua pasta
```

### "Permissão negada"

**Problema:** Windows bloqueia scripts
**Solução:** Execute como administrador ou use:
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### "Porta já em uso"

**Problema:** Já tem algo rodando na porta
**Solução:** Use outra porta
```bash
uvicorn app.main:app --port 8002
```

### "Sem memória"

**Problema:** Computador não tem RAM suficiente
**Solução:** Use menos dados
```bash
python train_dkt.py --batch-size 16 --limit-samples 1000
```

### "Baixando devagar"

**Problema:** Internet lenta
**Solução:** Use só um dataset por vez
```bash
python data/data_fetch_and_prepare.py --datasets assistments
```

---

## 📱 Acesso Remoto (Opcional)

Quer acessar de outro dispositivo na mesma rede?

### Descubra seu IP

**Windows:**
```bash
ipconfig
# Procure por "IPv4 Address"
```

**Mac/Linux:**
```bash
ifconfig
# Procure por "inet" (não 127.0.0.1)
```

Exemplo: `192.168.1.100`

### Inicie com IP Público

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Acesse de Outro Dispositivo

No outro computador/celular, abra:
```
http://192.168.1.100:8000
```

**⚠️ Só funciona na mesma rede WiFi!**

---

## 🎓 Aprenda Mais

### Tutoriais Incluídos

1. **notebook_demo.ipynb**: Tutorial interativo (requer Jupyter)
2. **presentation_slides.md**: Apresentação completa
3. **IMPROVEMENTS.md**: Features avançadas explicadas

### Abrindo o Notebook

```bash
jupyter notebook notebook_demo.ipynb
```

Abre automaticamente no navegador!

---

## 💡 Dicas de Uso

### Para Professores

✅ **Comece com dados pequenos**
   - Teste com 20-50 alunos primeiro
   - Depois expanda para turma inteira

✅ **Use estratégia Target**
   - Melhor para aprendizado real
   - Mantém aluno na "zona ideal"

✅ **Monitore o drift**
   - Retreine a cada 2-3 meses
   - Ou quando accuracy cair 10%

### Para Desenvolvedores

✅ **Ative o cache**
   - Torna inferência 90% mais rápida
   - Essencial para produção

✅ **Use batch inference**
   - 3-5x mais rápido que sequencial
   - Ideal para muitos alunos

✅ **MC Dropout para incerteza**
   - Identifica predições duvidosas
   - Crucial para decisões importantes

---

## 🎯 Checklist Final

Antes de usar em produção, verifique:

- [ ] Python 3.8+ instalado
- [ ] Todos os testes passando (`pytest`)
- [ ] Modelo treinado (arquivo `models/dkt.pt` existe)
- [ ] API_KEY alterada no `.env`
- [ ] SALT_ANON alterado no `.env`
- [ ] Dados anonimizados
- [ ] Backup dos dados original
- [ ] Documentação lida
- [ ] Sistema testado com dados reais
- [ ] Professores treinados no uso

---

## 🎉 Parabéns!

Você configurou com sucesso um sistema de IA educacional!

**Próximos passos sugeridos:**

1. Experimente com seus próprios dados
2. Explore os notebooks tutoriais
3. Personalize as estratégias de recomendação
4. Compartilhe com outros educadores

**Dúvidas?** Abra uma Issue no GitHub!

---

**Feito com ❤️ para democratizar IA na educação**

*Versão 2.0 - Outubro 2025*
