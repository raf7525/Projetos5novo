# 🚀 COMANDOS CORRETOS PARA SEU SISTEMA

## ✅ **COMANDO CORRETO PARA RODAR:**

```bash
# Navegar para o projeto
cd /home/raf75/quinto-periodo/projetos/Projetos5novo

# Ativar ambiente virtual (DENTRO do projeto!)
source venv/bin/activate

# Rodar servidor
python manage.py runserver
```

## 📋 **COMANDOS DE UMA LINHA SÓ:**

### Para rodar o sistema:
```bash
cd /home/raf75/quinto-periodo/projetos/Projetos5novo && source venv/bin/activate && python manage.py runserver
```

### Para adicionar dados novos:
```bash
cd /home/raf75/quinto-periodo/projetos/Projetos5novo && source venv/bin/activate && python manage.py populate_db
```

### Para rodar análise ML:
```bash
cd /home/raf75/quinto-periodo/projetos/Projetos5novo && source venv/bin/activate && python utils/ml_classifier.py
```

## ⚠️ **ERRO QUE VOCÊ TEVE:**

❌ **Comando errado:**
```bash
source ../venv/bin/activate  # Procura venv na pasta pai
```

✅ **Comando correto:**
```bash
source venv/bin/activate     # venv está DENTRO do projeto
```

## 🌐 **ACESSO AO DASHBOARD:**

**URL:** http://localhost:8000
**Status:** ✅ Funcionando (servidor ativo no terminal)

## 📁 **ESTRUTURA CORRETA:**

```
/home/raf75/quinto-periodo/projetos/
└── Projetos5novo/              ← Pasta do projeto
    ├── venv/                   ← Ambiente virtual AQUI
    ├── manage.py
    ├── data/
    │   └── raw/               ← Coloque dados CSV aqui
    └── dashboard/
```

## 🎯 **RESOLUÇÃO COMPLETA:**

1. ✅ Ambiente virtual encontrado em `/Projetos5novo/venv/`
2. ✅ Migrações aplicadas corretamente  
3. ✅ Django 5.2.6 funcionando
4. ✅ Servidor rodando em http://localhost:8000
5. ✅ Dashboard acessível

**🚀 Sistema 100% funcional!**