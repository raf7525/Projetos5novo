# Relatório de Preparação dos Dados
## Sistema Colaborativo de Monitoramento de Alagamentos - Recife

**Projeto:** Waze para Alagamentos  
**Data:** Novembro 2024  
**Versão:** 1.0

---

## 1. Fontes de Dados

### 1.1 Dados Primários (Próprios)
- **Relatórios Colaborativos:** Sistema de postagens dos usuários com informações de alagamentos
- **Formato:** CSV estruturado
- **Localização:** `data/raw/data.csv`
- **Cobertura:** 25 relatórios de junho a outubro de 2025
- **Área geográfica:** Região Metropolitana do Recife

### 1.2 Estrutura dos Dados Primários
```csv
Campos disponíveis:
- id_relato: Identificador único do relato
- latitude/longitude: Coordenadas geográficas precisas
- bairro: Localização administrativa
- timestamp: Data e hora do relato
- nivel_severidade: Escala de 1-4 (Baixo a Crítico)
- id_usuario: Identificador do usuário reportador
- confirmacoes: Número de validações da comunidade
```

### 1.3 Fontes Complementares Previstas
- **APAC (Agência Pernambucana de Águas e Clima):** Dados pluviométricos
- **Prefeitura do Recife:** Histórico de ocorrências oficiais
- **INMET:** Dados meteorológicos complementares
- **OpenStreetMap:** Informações geográficas de infraestrutura

---

## 2. Formatos de Dados Disponíveis

### 2.1 Formato Atual
- **CSV:** Dados estruturados tabulares
- **Vantagens:** Fácil processamento, compatibilidade universal
- **Limitações:** Não suporta dados complexos aninhados

### 2.2 Formatos Futuros Planejados
- **JSON:** Para dados de API em tempo real
- **PostgreSQL:** Banco de dados principal da aplicação
- **GeoJSON:** Dados geoespaciais para visualizações de mapas
- **Parquet:** Armazenamento otimizado para análises

---

## 3. Análise de Qualidade dos Dados

### 3.1 Completude dos Dados
**Status: ✅ EXCELENTE**
- **Valores nulos:** 0% (Nenhum campo possui valores faltantes)
- **Consistência geográfica:** 100% das coordenadas dentro dos limites de Recife
- **Integridade referencial:** Todos os relatos possuem bairros válidos

### 3.2 Consistência e Validação
**Status: ✅ VALIDADO**
- **Níveis de severidade:** 100% dentro da escala 1-4
- **Coordenadas geográficas:** Todas dentro dos limites da RMR
- **Timestamps:** Cronologia coerente e formatos padronizados

### 3.3 Distribuição e Representatividade
- **Cobertura temporal:** 4 meses de dados históricos
- **Cobertura geográfica:** 10 bairros diferentes
- **Diversidade de severidade:** Distribuição equilibrada entre níveis

---

## 4. Estratégias de Limpeza e Normalização

### 4.1 Tratamento de Outliers
**Critérios Geográficos:**
- Latitude válida: -8.2° a -7.9°
- Longitude válida: -35.0° a -34.8°
- **Ação:** Rejeição de coordenadas fora dos limites metropolitanos

**Critérios Temporais:**
- Timestamps futuros: Rejeição
- Relatórios duplicados no mesmo local/hora: Consolidação

### 4.2 Padronização de Dados
**Coordenadas:**
- Precisão: 6 casas decimais (±1 metro)
- Sistema: WGS84 (padrão GPS)

**Categorias:**
- Bairros: Normalização de grafias e abreviações
- Severidade: Escala numérica 1-4 consistente

### 4.3 Tratamento de Nulos (Preventivo)
```python
Estratégias definidas para dados futuros:
- Coordenadas: Geocodificação via endereço
- Severidade: Inferência via ML baseada em confirmações
- Timestamps: Timestamp do sistema como fallback
```

---

## 5. Transformações Previstas

### 5.1 Agregações Temporais
- **Dados horários:** Contagem de relatos por hora do dia
- **Dados diários:** Séries temporais para análise de tendências
- **Dados semanais:** Identificação de padrões sazonais
- **Dados mensais:** Análises de longo prazo e sazonalidade

### 5.2 Agregações Geoespaciais
- **Por bairro:** Estatísticas de severidade média e frequência
- **Por zona:** Agrupamento por regiões administrativas
- **Por grid:** Divisão em células hexagonais para heatmaps
- **Por distância:** Clusters de proximidade para alertas

### 5.3 Derivação de Variáveis
**Variáveis Temporais:**
```python
- hora_do_dia: Extração da hora (0-23)
- dia_semana: Dia da semana (Monday-Sunday)
- periodo_dia: Manhã/Tarde/Noite/Madrugada
- eh_fim_semana: Boolean para sábado/domingo
- mes: Extração do mês (1-12)
- estacao_ano: Verão/Outono/Inverno/Primavera
```

**Variáveis de Engajamento:**
```python
- taxa_confirmacao: confirmacoes / tempo_desde_relato
- credibilidade_usuario: Histórico de precisão do usuário
- urgencia_relato: severidade + proximidade_temporal
- densidade_area: Concentração de relatos na região
```

**Variáveis Geoespaciais:**
```python
- distancia_centro: Distância ao centro da cidade
- zona_risco: Classificação baseada em histórico
- proximidade_rio: Distância ao corpo d'água mais próximo
- altitude: Elevação do terreno (dados externos)
```

### 5.4 Codificação de Variáveis
**Categóricas Ordinais:**
- `nivel_severidade`: Manter escala numérica 1-4
- `periodo_dia`: Codificação ordinal 0-3

**Categóricas Nominais:**
- `bairro`: One-hot encoding para ML
- `dia_semana`: Codificação cíclica (sen/cos)

**Normalização Numérica:**
- `confirmacoes`: MinMax scaling (0-1)
- `coordenadas`: StandardScaler para clustering

---

## 6. Justificativas por Tipo de Variável

### 6.1 Variáveis Numéricas
**Tratamento:** StandardScaler + detecção de outliers via IQR
**Justificativa:** Preservar distribuições naturais enquanto permite comparabilidade entre escalas diferentes (confirmações vs. coordenadas).

**Variáveis:**
- `latitude/longitude`: Manter precisão original
- `confirmacoes`: Log-transform para reduzir skewness
- `nivel_severidade`: Manter escala original (interpretabilidade)

### 6.2 Variáveis Categóricas
**Tratamento:** Encoding adaptativo baseado na cardinalidade
**Justificativa:** Bairros (baixa cardinalidade) usam one-hot, usuários (alta cardinalidade) usam embedding.

**Estratégias:**
- `bairro` (10 valores): One-hot encoding
- `id_usuario` (15+ valores): Target encoding baseado em severidade média
- `dia_semana`: Codificação cíclica para capturar periodicidade

### 6.3 Variáveis Temporais
**Tratamento:** Decomposição em componentes cíclicos e lineares
**Justificativa:** Capturar tanto tendências de longo prazo quanto padrões cíclicos (diário/semanal/sazonal).

**Componentes extraídos:**
- Tendência linear: Para detectar mudanças climáticas
- Ciclo diário: Para alertas preditivos por horário
- Ciclo semanal: Para padrões urbanos de tráfego/ocupação
- Ciclo sazonal: Para variações pluviométricas

---

## 7. Pipeline de Processamento

### 7.1 Fluxo de Dados
```
RAW DATA → VALIDATION → CLEANING → TRANSFORMATION → AGGREGATION → ML FEATURES
```

### 7.2 Automatização
- **Validação:** Regras automáticas de qualidade
- **Limpeza:** Scripts de normalização padronizados
- **Monitoramento:** Alertas para anomalias nos dados
- **Versionamento:** Controle de versões dos datasets processados

### 7.3 Métricas de Qualidade
- **Completude:** % de campos preenchidos
- **Validade:** % de dados dentro dos ranges esperados
- **Consistência:** % de dados sem contradições
- **Atualidade:** Tempo médio desde o último update

---

## 8. Cronograma de Implementação

| Etapa | Prazo | Status |
|-------|--------|--------|
| Análise exploratória | 11/11 | ✅ Concluído |
| Pipeline de limpeza | 12/11 | 🟡 Em andamento |
| Transformações avançadas | 13/11 | ⏳ Planejado |
| Features para ML | 14/11 | ⏳ Planejado |
| Dashboard com dados | 14/11 | ⏳ Planejado |

---

**Conclusão:** Os dados apresentam excelente qualidade inicial, permitindo foco em transformações avançadas para maximizar o valor analítico do sistema colaborativo de monitoramento de alagamentos.

*Documento preparado como base técnica para o desenvolvimento do sistema tipo Waze para alagamentos em Recife.*