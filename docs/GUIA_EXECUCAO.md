# 🚀 **GUIA COMPLETO DE EXECUÇÃO**
*Sistema Waze Alagamentos - Como Rodar e Adicionar Dados*

---

## ⚡ **COMANDO PRINCIPAL PARA RODAR**

### **Passo a Passo:**

```bash
# 1️⃣ NAVEGAR PARA O PROJETO
cd /home/raf75/quinto-periodo/projetos/Projetos5novo

# 2️⃣ ATIVAR AMBIENTE VIRTUAL
source ../venv/bin/activate

# 3️⃣ INICIAR SERVIDOR DJANGO
python manage.py runserver

# 4️⃣ ACESSAR NO NAVEGADOR
# http://localhost:8000
```

### **🔍 Verificar se está funcionando:**
Você deve ver no terminal:
```
Starting development server at http://0.0.0.0:8000/
Quit the server with CONTROL-C.
```

---

## 📂 **ONDE COLOCAR NOVOS DADOS**

### **📍 Local principal dos dados:**
```
/home/raf75/quinto-periodo/projetos/Projetos5novo/data/raw/
```

### **📁 Estrutura de pastas:**
```
data/
├── raw/                    ← 🎯 SEUS DADOS VÃO AQUI
│   ├── data.csv           ← Arquivo atual (pode substituir)
│   ├── novos_dados.csv    ← Adicione novos arquivos aqui
│   └── alagamentos_*.csv  ← Qualquer nome CSV
├── processed/             ← Dados processados (automático)
├── exports/               ← Gráficos e análises (automático)
└── temp/                  ← Arquivos temporários
```

---

## 📥 **COMO ADICIONAR NOVOS DADOS**

### **Método 1: Substituir arquivo principal**
```bash
# Backup do arquivo atual
cp data/raw/data.csv data/raw/data_backup.csv

# Copiar seus novos dados
cp /caminho/para/seus/dados.csv data/raw/data.csv
```

### **Método 2: Adicionar arquivo novo**
```bash
# Copiar arquivo adicional
cp /caminho/para/novos_dados.csv data/raw/novos_dados.csv
```

### **📋 Formato CSV esperado:**
Seus dados devem ter colunas similares a:
```csv
data,bairro,latitude,longitude,severidade,confirmacoes,usuario,descricao
2025-10-15 08:30:00,Boa Viagem,-8.1234,-34.5678,3,5,user123,Alagamento na rua principal
```

**Colunas necessárias:**
- `data` - Data/hora do relato
- `bairro` - Nome do bairro
- `latitude, longitude` - Coordenadas GPS
- `severidade` - Nível 1-4 (1=baixo, 4=crítico)
- `confirmacoes` - Número de confirmações
- `usuario` - ID do usuário
- `descricao` - Descrição do problema

---

## 🔄 **COMO PROCESSAR DADOS NOVOS**

### **Comando para recarregar dados:**
```bash
# Limpar banco atual e recarregar
python manage.py flush --noinput
python manage.py migrate
python manage.py populate_db
```

### **Comando para análise ML dos novos dados:**
```bash
# Rodar análise de Machine Learning
python utils/ml_classifier.py
```

---

## 🛠️ **COMANDOS ÚTEIS**

### **Verificar status do projeto:**
```bash
# Verificar se Django está OK
python manage.py check

# Ver migrações
python manage.py showmigrations

# Criar superusuário (admin)
python manage.py createsuperuser
```

### **Acessar admin Django:**
```bash
# URL: http://localhost:8000/admin/
# Use as credenciais do superusuário criado
```

### **Ver logs em tempo real:**
```bash
# Terminal 1: Servidor
python manage.py runserver

# Terminal 2: Monitorar logs
tail -f logs/*.log
```

---

## 📊 **EXEMPLO PRÁTICO: ADICIONANDO DADOS**

### **Cenário: Você baixou `alagamentos_recife_2024.csv`**

```bash
# 1. Navegar para o projeto
cd /home/raf75/quinto-periodo/projetos/Projetos5novo

# 2. Ativar ambiente
source ../venv/bin/activate

# 3. Copiar seus dados
cp ~/Downloads/alagamentos_recife_2024.csv data/raw/

# 4. Editar o populate_db.py para usar o novo arquivo
# (se necessário)

# 5. Reprocessar dados
python manage.py flush --noinput
python manage.py migrate  
python manage.py populate_db

# 6. Rodar análise ML
python utils/ml_classifier.py

# 7. Iniciar dashboard
python manage.py runserver

# 8. Acessar http://localhost:8000
```

---

## 🎯 **ESTRUTURA DE COMANDOS POR TAREFA**

### **🚀 Primeira execução:**
```bash
cd /home/raf75/quinto-periodo/projetos/Projetos5novo
source ../venv/bin/activate
python manage.py runserver
```

### **📥 Adicionar dados novos:**
```bash
# Colocar CSV em data/raw/
cp novo_arquivo.csv data/raw/
python manage.py populate_db
python manage.py runserver
```

### **🔧 Reset completo:**
```bash
python manage.py flush --noinput
python manage.py migrate
python manage.py populate_db
python utils/ml_classifier.py
python manage.py runserver
```

### **📊 Só análise ML:**
```bash
python utils/ml_classifier.py
# Gráficos salvos em data/exports/
```

---

## ⚠️ **TROUBLESHOOTING**

### **Problema: Porta ocupada**
```bash
# Matar processo na porta 8000
sudo lsof -t -i:8000 | xargs kill -9

# Ou usar porta diferente
python manage.py runserver 8001
```

### **Problema: Ambiente virtual não ativo**
```bash
# Verificar se está ativo
which python
# Deve mostrar: .../venv/bin/python

# Ativar se necessário
source ../venv/bin/activate
```

### **Problema: CSV com formato diferente**
Edite o arquivo `dashboard/management/commands/populate_db.py` na função `migrar_relatorios()` para ajustar as colunas do seu CSV.

---

## 📱 **URLS IMPORTANTES**

- **Dashboard Principal:** http://localhost:8000/
- **Admin Django:** http://localhost:8000/admin/
- **API (futura):** http://localhost:8000/api/

---

## 🎉 **RESUMO RÁPIDO**

**Para rodar pela primeira vez:**
```bash
cd Projetos5novo && source ../venv/bin/activate && python manage.py runserver
```

**Para adicionar dados:**
1. Coloque CSV em `data/raw/`
2. Rode `python manage.py populate_db`
3. Acesse http://localhost:8000

**✅ Sistema pronto para uso!** 🚀